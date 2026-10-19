import asm3.configuration
import asm3.dbfs
import asm3.i18n
import asm3.log

from .base import AbstractPublisher
from asm3.sitedefs import PETSZEL_URL
from asm3.typehints import Database, Dict, List, PublishCriteria, Results, ResultRow

import sys

# ID type keys used in the ExtraIDs column
IDTYPE_PETSZEL = "petszel"

class PetszelPublisher(AbstractPublisher):
    """
    Handles publishing to petszel.com
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("petszel", "Petszel Publisher")
        self.dbo = dbo

    def getAnimalMedia(self, animalid) -> Results:
        m = self.dbo.query(
            "SELECT m.ID, m.MediaName, m.MediaMimeType, m.DBFSID FROM media m WHERE m.LinkTypeID = ? AND m.LinkID = ? AND m.ExcludeFromPublish = 0 AND m.MediaType = ?",
            [asm3.media.ANIMAL, animalid, asm3.media.MEDIATYPE_FILE]
        )
        return m

    def getData(self, lastpublished) -> Results:

        weightlogtype = asm3.configuration.weight_change_log_type(self.dbo)

        a = self.dbo.query(
            "SELECT " \
            "a.ID, " \
            "a.ActiveMovementType, " \
            "a.ActiveMovementDate, " \
            "a.ShelterCode, " \
            "a.AnimalName, " \
            "a.DateOfBirth, " \
            "g.Sex, " \
            "z.Size, " \
            "a.Neutered, " \
            "a.ExtraIDs, " \
            "s.SpeciesName, " \
            "a.LastChangedDate, " \
            "o.OwnerCode, " \
            "o.OwnerName, " \
            "o.OwnerForeNames, " \
            "o.OwnerSurname, " \
            "o.OwnerAddress, " \
            "o.OwnerTown, " \
            "o.OwnerCounty, " \
            "o.OwnerPostcode, " \
            "o.EmailAddress, " \
            "o.MobileTelephone, " \
            "o.CreatedDate AS OwnerCreatedDate, " \
            "o.LastChangedDate AS OwnerLastChangedDate, " \
            "(SELECT Comments FROM log WHERE LogTypeID = ? AND LinkType = ? AND LinkID = a.ID AND Date < ? ORDER BY Date desc ) AS AdoptionWeight, " \
            "(SELECT Date FROM log WHERE LogTypeID = ? AND LinkType = ? AND LinkID = a.ID AND Date < ? ORDER BY Date desc ) AS AdoptionWeightDate " \
            "FROM adoption m " \
            "INNER JOIN animal a ON m.AnimalID = a.ID " \
            "INNER JOIN lksex g ON a.Sex = g.ID " \
            "INNER JOIN lksize z ON a.Size = z.ID " \
            "INNER JOIN owner o ON m.OwnerID = o.ID " \
            "INNER JOIN species s ON a.SpeciesID = s.ID " \
            "WHERE a.DeceasedDate IS NULL AND m.MovementType = 1 AND m.ReturnDate IS NULL AND m.MovementDate > ?",
            [weightlogtype, asm3.log.ANIMAL, self.dbo.sql_interval("m.MovementDate", 1, "+", "days"), weightlogtype, asm3.log.ANIMAL, self.dbo.sql_interval("m.MovementDate", 1, "+", "days"), lastpublished]
        )
        self.log("Got %d matching animals for publishing." % len(a))
        return a

    def run(self) -> None:
        
        self.log("Petszel Publisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        # animals = self.getMatchingAnimals(includeAdditionalFields=True)
        lastpublished = asm3.publish.get_last_published(self.dbo, "petszel")
        animals = self.getData(asm3.i18n.format_date(lastpublished))
        processed = []

        # Log that there were no animals, we still need to check
        # previously sent listings
        if len(animals) == 0:
            self.log("No animals found to publish.")

        # headers = { "Authorization": "Token token=%s" % token, "Accept": "*/*" }

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

                r = {
                    "status": 200,
                    "headers": "Headers Placeholder",
                    "response": "Success"
                }

                if r["status"] != 200:
                    self.logError("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                    # Update animalpublished for this animal with the error code so that it's visible in the UI
                    # that we tried and what the error was.
                    errormsg = str(r["response"])
                    self.markAnimalPublished(an.ID, extra = errormsg)
                else:
                    self.log("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                    processed.append(an)
                    asm3.animal.set_extra_id(self.dbo, "pub::petszel", an, IDTYPE_PETSZEL, str(self.dbo.today()))

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark sent animals published
        self.markAnimalsPublished(processed, first=True)

        self.cleanup()

    def processAnimal(self, an: ResultRow) -> Dict:
        """ Processes an animal record and returns a data dictionary to upload as JSON """

        ofirstname = an.OWNERFORENAMES.split(" ")[0]
        omiddlenames = " ".join(an.OWNERFORENAMES.split(" ")[0][1:])
        address = self.splitAddress(an.OWNERADDRESS)

        p = {
            "animal": {
                "animalId": an.SHELTERCODE,
                "animalName": an.ANIMALNAME.title(),
                "dateOfBirth": asm3.i18n.python2iso(an.DATEOFBIRTH, self.dbo.timezone),
                "adoptionDate": asm3.i18n.python2iso(an.ACTIVEMOVEMENTDATE, self.dbo.timezone),
                "animalType": an.SPECIESNAME,
                "sex": an.SEX,
                "sizeGroup": an.SIZE,
                "sourceReference": {
                    "sourceId": an.SHELTERCODE,
                    "dateUpdated": asm3.i18n.python2iso(an.LASTCHANGEDDATE, self.dbo.timezone)
                }
            },
            "event": {
                "type": "Adoption",
                "date": asm3.i18n.python2iso(an.ACTIVEMOVEMENTDATE, self.dbo.timezone),
                "participants": [
                    {
                        "personId": an.OWNERCODE,
                        "firstName": ofirstname,
                        "middleName": omiddlenames,
                        "lastName": an.OWNERSURNAME,
                        "emails": [
                            {
                                "emailAdress": an.EMAILADDRESS,
                                "type": "Personal",
                                "doNotEmail": False,
                                "sourceReference": {
                                    "sourceId": an.OWNERCODE,
                                    "sourceDisplayId": "Personal email",
                                    "dateCreated": asm3.i18n.python2iso(an.OWNERCREATEDDATE, self.dbo.timezone),
                                    "dateUpdated": asm3.i18n.python2iso(an.OWNERLASTCHANGEDDATE, self.dbo.timezone)
                                }
                            }
                        ],
                        "addresses": [
                            {
                                "streetLine1": address["line1"],
                                "streetLine2": address["line2"],
                                "city": an.OWNERTOWN,
                                "stateProvince": an.OWNERCOUNTY,
                                "postalCode": an.OWNERPOSTCODE,
                                "country": "US",
                                "doNotMail": False,
                                "sourceReference": {
                                    "sourceId": an.OWNERCODE,
                                    "sourceDisplayId": "Home address",
                                    "dateCreated": asm3.i18n.python2iso(an.OWNERCREATEDDATE, self.dbo.timezone),
                                    "dateUpdated": asm3.i18n.python2iso(an.OWNERLASTCHANGEDDATE, self.dbo.timezone)
                                }
                            }
                        ],
                        "phoneNumbers": [
                            {
                                "number": an.MOBILETELEPHONE,
                                "type": "Mobile",
                                "doNotCall": False,
                                "doNotText": False,
                                "sourceReference": {
                                    "sourceId": an.OWNERCODE,
                                    "sourceDisplayId": "Mobile phone",
                                    "dateCreated": asm3.i18n.python2iso(an.OWNERCREATEDDATE, self.dbo.timezone),
                                    "dateUpdated": asm3.i18n.python2iso(an.OWNERLASTCHANGEDDATE, self.dbo.timezone)
                                }
                            }
                        ],
                        "sourceReference": {
                            "sourceId": an.OWNERCODE,
                            "sourceDisplayId": an.OWNERNAME,
                            "dateCreated": asm3.i18n.python2iso(an.OWNERCREATEDDATE, self.dbo.timezone),
                            "dateUpdated": asm3.i18n.python2iso(an.OWNERLASTCHANGEDDATE, self.dbo.timezone)
                        }
                    }
                ],
            }
        }
        if an.ADOPTIONWEIGHT:
            p["animal"]["adoptedWeight"] = an.ADOPTIONWEIGHT,
            p["animal"]["adoptedWeightDate"] = asm3.i18n.python2iso(an.ADOPTIONWEIGHTDATE, self.dbo.timezone),
        if an.NEUTERED:
            if an.SEX == "Male":
                p["animal"]["altered"] = "Neutered"
            elif an.SEX == "Female":
                p["animal"]["altered"] = "Spayed"
        animalmedia = self.getAnimalMedia(an.ID)
        print("Animal Media")
        for m in animalmedia:
            print(m.MEDIANAME + " " + m.MEDIAMIMETYPE)
            mediabytes = asm3.dbfs.get_string_id(self.dbo, m.DBFSID)
            # mediabytes = mediabytestring.encode("utf-8")
            imagedimensions = asm3.media.image_dimensions(mediabytes)
            print(str(imagedimensions))

        return p


