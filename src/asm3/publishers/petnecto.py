
import asm3.configuration
import asm3.i18n
import asm3.utils

from .base import AbstractPublisher, get_animal_data
from asm3.sitedefs import PETNECTO_URL
from asm3.typehints import Any, Database, Dict, List, PublishCriteria, ResultRow, Tuple

import re
import requests
import sys
import time
import urllib.parse

# Only these fields are ever sent to Petnecto. None of them is personal data: no owner, adopter,
# person, vet, address, telephone, email, surrender reason, microchip number or internal note.
# processAnimal() builds the dictionary from exactly this list and refuses to return anything else.
PETNECTO_FIELDS = (
    "shelter_code", "name", "species", "breed", "mix", "sex", "date_of_birth", "age_text", "size", "colour",
    "neutered", "good_with_dogs", "good_with_cats", "good_with_children", "description", "photo_urls",
    "date_brought_in", "status"
)

SHELTER_ID_RE = re.compile(r"^sh_[A-Za-z0-9_-]{1,80}$")
TOKEN_RE = re.compile(r"^pnp_[A-Za-z0-9_-]{43}$")
EMAIL_RE = re.compile(r"[^\s@<>()]{1,64}@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
CODE_BAD_RE = re.compile(r"[^A-Za-z0-9._-]")

MAX_PHOTOS = 8
MAX_DESCRIPTION = 4000
TIMEOUT = (5, 30) # connect, read: seconds. A stuck server must not hold the publisher forever
MAX_CONSECUTIVE_FAILURES = 3 # network failures in a row before we give up for this run
MAX_RETRY_WAIT = 60 # seconds: the longest we wait when Petnecto says 429 slow down, once per request
CANCEL_AFTER_DAYS = 182 # same window petrescue.py uses for listings we may have to take down

def redact(msg: Any, token: str) -> str:
    """ Returns msg as a string with the token removed. Everything that reaches a log goes through this. """
    s = str(msg)
    if token: s = s.replace(token, "[token]")
    return re.sub(r"pnp_[A-Za-z0-9_-]{8,}", "[token]", s)

def base_url_problem(url: str) -> str:
    """
    Returns a problem description if url cannot be used as the Petnecto base URL, or "" if it is fine.
    https is required. Plain http is only accepted for a host on a private network (a local test setup),
    because the bearer token travels in the request.
    """
    try:
        u = urllib.parse.urlsplit(url)
    except Exception:
        return "The Petnecto URL is not valid"
    if u.scheme not in ("http", "https") or not u.hostname: return "The Petnecto URL must start with https://"
    if u.username or u.password or u.query or u.fragment: return "The Petnecto URL must not contain a login, query or fragment"
    if u.scheme == "http":
        h = u.hostname.lower()
        private = "." not in h or h == "localhost" or h.endswith((".local", ".internal", ".lan", ".home", ".test")) or \
            re.match(r"^(10\.|127\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)", h) is not None
        if not private: return "The Petnecto URL must use https:// (plain http is only accepted for hosts on a private network)"
    return ""

def yes_no_unknown(v: Any) -> str:
    """ ASM stores good-with as 0 = yes, 1 = no, anything else unknown/selective """
    if v == 0: return "yes"
    if v == 1: return "no"
    return "unknown"

def clean_text(s: Any) -> Tuple[str, bool]:
    """ Normalises line endings and removes email addresses. Returns the text and whether an address was removed. """
    s = asm3.utils.nulltostr(s).replace("\r\n", "\n").replace("\r", "\n").strip()
    removed = EMAIL_RE.search(s) is not None
    if removed: s = EMAIL_RE.sub("", s).strip()
    return s, removed

class PetnectoPublisher(AbstractPublisher):
    """
    Handles publishing to Petnecto (petnecto.com), which lists adoptable shelter animals for people and AI assistants.

    Sends one JSON document per adoptable animal (POST, an upsert keyed by the shelter code) and, for animals
    that were sent before and are no longer adoptable, a status change (PATCH) so they come off the listing.
    Authentication is a bearer token issued by Petnecto for this one shelter. It is not an ASM key or login.
    Only the fields in PETNECTO_FIELDS are sent: no owner or other personal data.
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("petnecto", "Petnecto Publisher")
        self.token = ""
        self.rawcodes = {}

    # -- logging that can never contain the token ---------------------------------------------------

    def log(self, msg: str) -> None:
        AbstractPublisher.log(self, redact(msg, self.token))

    def logError(self, msg: str, ie: Any = None) -> None:
        # the traceback is dropped: an exception raised from the HTTP layer can carry request details
        AbstractPublisher.logError(self, redact(msg, self.token), None)

    def logSuccess(self, msg: str) -> None:
        AbstractPublisher.logSuccess(self, redact(msg, self.token))

    def setLastError(self, msg: str, log_error: bool = True) -> None:
        AbstractPublisher.setLastError(self, redact(msg, self.token), log_error)

    # -- building what is sent -------------------------------------------------------------------------

    def shelterCode(self, an: ResultRow) -> str:
        """
        The stable id Petnecto keys an animal by. It comes from the animal table as stored, because get_animal_data rewrites codes
        (slashes and spaces) for ALL rows only when the FIRST row has a slash, so the same animal could be sent under two codes.
        Characters that are awkward in a URL path are replaced, the same way for the upload and for the take-down.
        """
        return self.cleanCode(self.rawcodes.get(an.ID, an.SHELTERCODE))

    def cleanCode(self, code: Any) -> str:
        return CODE_BAD_RE.sub("-", asm3.utils.nulltostr(code).strip())

    def getAnimals(self) -> List[ResultRow]:
        """ The animals to publish. Personal data is stripped from the rows before we ever look at them. """
        a = get_animal_data(self.dbo, self.pc, include_additional_fields = False, strip_personal_data = True, publisher_key = self.publisherKey)
        self.log("Got %d matching animals for publishing." % len(a))
        self.rawcodes = {}
        if len(a) > 0:
            for r in self.dbo.query("SELECT ID, ShelterCode FROM animal WHERE ID IN (%s)" % ",".join([ str(int(x.ID)) for x in a ])):
                self.rawcodes[r.ID] = r.SHELTERCODE
        return a

    def processAnimal(self, an: ResultRow, status: str = "adoptable") -> Dict:
        """ Processes an animal record and returns the dictionary to upload as JSON. """
        description, removed = clean_text(an.WEBSITEMEDIANOTES)
        if removed: self.log("%s: an email address was removed from the description before sending" % an.SHELTERCODE)
        sex = asm3.utils.nulltostr(an.SEXNAME).lower()
        if sex not in ("male", "female"): sex = "unknown"
        dob = asm3.i18n.format_date(an.DATEOFBIRTH, "%Y-%m-%d") if an.DATEOFBIRTH is not None else None
        brought = asm3.i18n.format_date(an.DATEBROUGHTIN, "%Y-%m-%d") if an.DATEBROUGHTIN is not None else None
        data = {
            "shelter_code":         self.shelterCode(an),
            "name":                 asm3.utils.nulltostr(an.ANIMALNAME).strip(),
            "species":              asm3.utils.nulltostr(an.SPECIESNAME),
            "breed":                asm3.utils.nulltostr(an.BREEDNAME),
            "mix":                  self.isCrossBreed(an),
            "sex":                  sex,
            "date_of_birth":        dob,
            "age_text":             asm3.utils.nulltostr(an.ANIMALAGE)[:60],
            "size":                 asm3.utils.nulltostr(an.SIZENAME),
            "colour":               asm3.utils.nulltostr(an.BASECOLOURNAME),
            "neutered":             an.NEUTERED == 1,
            "good_with_dogs":       yes_no_unknown(an.ISGOODWITHDOGS),
            "good_with_cats":       yes_no_unknown(an.ISGOODWITHCATS),
            "good_with_children":   yes_no_unknown(an.ISGOODWITHCHILDREN),
            "description":          description[:MAX_DESCRIPTION],
            "photo_urls":           self.getPhotoUrls(an.ID)[:MAX_PHOTOS], # ASM's own photo URLs: Petnecto fetches nothing from us until it chooses to
            "date_brought_in":      brought,
            "status":               status
        }
        assert tuple(data.keys()) == PETNECTO_FIELDS # nothing else may ever be added without changing the list above
        return data

    # -- talking to Petnecto ---------------------------------------------------------------------------

    def send(self, method: str, url: str, data: Dict) -> Tuple[int, Dict, str]:
        """
        Sends data as JSON. Returns (status, parsed json or {}, retry-after). Never follows a redirect (the token must
        not go anywhere but where the shelter set it up), always has a timeout, and returns 599 for a network failure.
        """
        try:
            r = requests.request(method, url, data = asm3.utils.json(data).encode("utf-8"), timeout = TIMEOUT, allow_redirects = False,
                headers = { "Authorization": "Bearer %s" % self.token, "Content-Type": "application/json", "Accept": "application/json" })
        except Exception as err:
            return 599, {}, redact(err.__class__.__name__, self.token)
        try:
            j = r.json()
            if not isinstance(j, dict): j = {}
        except Exception:
            j = {}
        return r.status_code, j, r.headers.get("retry-after", "")

    def sendPatiently(self, method: str, url: str, data: Dict) -> Tuple[int, Dict, str]:
        """
        send(), but when Petnecto answers 429 with a short Retry-After we wait that long (checking for a cancel every second) and send once more.
        A longer wait, or a second 429, is returned to the caller, which stops the run: the rest is sent next time.
        """
        status, j, retryafter = self.send(method, url, data)
        if status == 429 and retryafter.strip().isdigit() and 0 < int(retryafter) <= MAX_RETRY_WAIT:
            self.log("Petnecto asked us to wait %s seconds, waiting" % retryafter)
            for _ in range(int(retryafter)):
                if self.shouldStopPublishing(): break
                time.sleep(1)
            status, j, retryafter = self.send(method, url, data)
        return status, j, retryafter

    def describeFailure(self, status: int, j: Dict) -> str:
        """ A short message for the log and the animal's publishing history, from the status and Petnecto's error code. """
        err = redact(j.get("error", ""), self.token)[:60]
        field = redact(j.get("field", ""), self.token)[:40]
        return "HTTP %d %s%s" % (status, err, " (%s)" % field if field else "")

    def wasChanged(self, animals: List[ResultRow]) -> bool:
        """
        True if there is something to do: a change since the last publish, or an animal we have never sent, or one
        whose last send failed. (A failed send must not be hidden by the "nothing has changed" shortcut.)
        """
        if self.isChangedSinceLastPublish(): return True
        sent = self.dbo.query("SELECT AnimalID, Extra FROM animalpublished WHERE PublishedTo = ?", [self.publisherKey])
        ok = set([ x.ANIMALID for x in sent if asm3.utils.nulltostr(x.EXTRA) in ("", "None") ]) # sent fine: no error and no take-down status in Extra
        return any(an.ID not in ok for an in animals)

    def run(self) -> None:

        self.log("PetnectoPublisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        self.token = asm3.configuration.petnecto_token(self.dbo).strip()
        shelterid = asm3.configuration.petnecto_shelter_id(self.dbo).strip()
        baseurl = PETNECTO_URL.strip().rstrip("/")

        if baseurl == "":
            self.setLastError("The Petnecto service address has not been set up on this server (petnecto_url).")
            self.cleanup()
            return

        problem = base_url_problem(baseurl)
        if problem != "":
            self.setLastError(problem)
            self.cleanup()
            return

        if self.token == "" or shelterid == "":
            self.setLastError("No Petnecto shelter ID or token has been set.")
            self.cleanup()
            return

        if not SHELTER_ID_RE.match(shelterid):
            self.setLastError("The Petnecto shelter ID looks wrong. It starts with sh_")
            self.cleanup()
            return

        if not TOKEN_RE.match(self.token):
            self.setLastError("The Petnecto token looks wrong. It starts with pnp_")
            self.cleanup()
            return

        animals = self.getAnimals()

        if not self.wasChanged(animals):
            self.logSuccess("No animal/movement changes have been made since last publish")
            self.setLastError("No animal/movement changes have been made since last publish", log_error = False)
            self.cleanup()
            return

        if len(animals) == 0:
            self.log("No animals found to publish.") # we still need to take down previously sent listings

        url = "%s/api/v1/shelters/%s/animals" % (baseurl, shelterid)
        processed = []
        failures = 0
        fatal = False

        anCount = 0
        for an in animals:
            try:
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing():
                    self.stopPublishing()
                    return

                data = self.processAnimal(an)
                self.log("Sending POST to %s to create/update %s" % (url, data["shelter_code"]))
                status, j, retryafter = self.sendPatiently("POST", url, data)

                if status in (200, 201):
                    self.log("HTTP %d: %s" % (status, redact(j.get("result", ""), self.token)))
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                    processed.append(an)
                    failures = 0
                elif status in (401, 403):
                    # The token was revoked, is wrong, or the shelter is not accepting animals. The same answer would come for
                    # every other animal, so stop here instead of sending the whole list again.
                    self.setLastError("Petnecto refused the token (%s). Check the shelter ID and token, or ask Petnecto for a new one." % self.describeFailure(status, j))
                    fatal = True
                    break
                elif status == 429:
                    self.setLastError("Petnecto asked us to slow down (HTTP 429, retry after %ss). The rest will be sent next time." % (redact(retryafter, self.token)[:6] or "?"))
                    fatal = True
                    break
                elif status == 599:
                    failures += 1
                    self.logError("Could not reach Petnecto for %s (%s)" % (an["SHELTERCODE"], retryafter))
                    self.markAnimalPublished(an.ID, extra = "error: could not reach Petnecto")
                    if failures >= MAX_CONSECUTIVE_FAILURES:
                        self.setLastError("Petnecto could not be reached %d times in a row. Stopping; the rest will be sent next time." % failures)
                        fatal = True
                        break
                else:
                    msg = self.describeFailure(status, j)
                    self.logError("%s: %s" % (an["SHELTERCODE"], msg))
                    # Update animalpublished for this animal with the error so that it is visible in the UI that we tried and what the error was.
                    self.markAnimalPublished(an.ID, extra = "error: " + msg)
                    if status >= 500:
                        failures += 1
                        if failures >= MAX_CONSECUTIVE_FAILURES:
                            self.setLastError("Petnecto answered with errors %d times in a row. Stopping; the rest will be sent next time." % failures)
                            fatal = True
                            break

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark sent animals published
        self.markAnimalsPublished(processed, first=True)

        if fatal:
            self.cleanup()
            return

        self.takeDown(url, animals)

        self.cleanup()

    def takeDown(self, url: str, sentanimals: List[ResultRow]) -> None:
        """
        Tells Petnecto about animals we sent before that are no longer in the set we just sent: adopted, transferred or
        deceased animals are removed; animals that are simply not adoptable at the moment (hold, reserved) are put on hold.
        """
        try:
            # Everything we sent in the last six months. This can include animals whose send failed with an error.
            prevsent = self.dbo.query("SELECT AnimalID FROM animalpublished WHERE SentDate>=? AND PublishedTo=?", [self.dbo.today(offset=-CANCEL_AFTER_DAYS), self.publisherKey])
            sentids = set([ x.ID for x in sentanimals ])
            tocancel = set([ str(x.ANIMALID) for x in prevsent if x.ANIMALID not in sentids ])
            if len(tocancel) == 0: return
            animals = self.dbo.query("SELECT ID, ShelterCode, AnimalName, ActiveMovementDate, ActiveMovementType, DeceasedDate, " \
                "(SELECT Extra FROM animalpublished WHERE AnimalID=a.ID AND PublishedTo=?) AS LastStatus " \
                "FROM animal a WHERE ID IN (%s)" % ",".join(tocancel), [self.publisherKey])
        except Exception as err:
            self.logError("Failed finding listings to take down: %s" % err, sys.exc_info())
            return

        failures = 0
        for an in animals:
            try:
                if self.shouldStopPublishing():
                    self.stopPublishing()
                    return
                status = "hold"
                if an.DECEASEDDATE is not None or an.ACTIVEMOVEMENTDATE is not None: status = "removed"
                # Don't send the same update again: the last status we sent is kept in animalpublished.Extra
                if an.LASTSTATUS == status: continue
                code = self.cleanCode(an.SHELTERCODE)
                purl = "%s/%s" % (url, urllib.parse.quote(code, safe=""))
                self.log("Sending PATCH to %s to set status %s" % (purl, status))
                st, j, retryafter = self.sendPatiently("PATCH", purl, { "status": status })
                self.log("HTTP %d: %s" % (st, redact(j.get("result", j.get("error", "")), self.token)))
                if st == 200 or st == 404: # 404: Petnecto never received it (an earlier send failed), so there is nothing to take down
                    self.logSuccess("%s - %s: Marked with new status %s" % (an.SHELTERCODE, an.ANIMALNAME, status))
                    # Keep the status we sent in Extra so that it is not sent again next time.
                    self.markAnimalPublished(an.ID, extra = status)
                    failures = 0
                elif st in (401, 403, 429):
                    self.setLastError("Petnecto refused the status changes (%s)." % self.describeFailure(st, j))
                    return
                else:
                    self.logError("%s - %s: Error updating status to %s (%s)" % (an.SHELTERCODE, an.ANIMALNAME, status, self.describeFailure(st, j)))
                    failures += 1
                    if failures >= MAX_CONSECUTIVE_FAILURES:
                        self.setLastError("Petnecto could not be reached %d times in a row while taking animals down. Stopping." % failures)
                        return
            except Exception as err:
                self.logError("Failed taking down %s - %s: %s" % (an.SHELTERCODE, an.ANIMALNAME, err), sys.exc_info())
