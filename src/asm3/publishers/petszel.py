import asm3.configuration
import asm3.i18n
import asm3.medical
import asm3.utils

from .base import AbstractPublisher
from asm3.sitedefs import PETSZEL_URL
from asm3.typehints import Database, Dict, List, PublishCriteria, Results, ResultRow

import sys

class PetszelPublisher(AbstractPublisher):
    """
    Handles publishing to petszel.com
    """
    def __init__(self, dbo: Database) -> None:
        AbstractPublisher.__init__(self, dbo, False)
        self.initLog("petszel", "Petszel Publisher")
        self.dbo = dbo

    def getData(self) -> Results:
        a = self.dbo.query(
            "SELECT m.ID, a.ShelterCode, a.AnimalName, s.SpeciesName, a.ExtraID, a.LastChangedDate FROM adoption m INNER JOIN animal a ON m.AnimalID = a.ID INNER JOIN species s ON a.SpeciesID = s.ID LEFT JOIN animalpublished p ON a.ID = p.AnimalID WHERE a.ExtraID" % ()
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
        animals = self.dbo.query(
            "SELECT " \
            "a.ShelterCode, " \
            "a.AnimalName, " \
            "s.SpeciesName, " \
            "a.LastChangedDate, " \
            "FROM adoption m " \
            "INNER JOIN animal a ON m.AnimalID = a.ID " \
            "INNER JOIN owner o ON m.OwnerID = o.ID " \
            "INNER JOIN species s ON a.SpeciesID = s.ID " \
            "WHERE m.MovementType = 1 AND m.ReturnDate IS NULL " \
        )
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
      
                # data = self.processAnimal(an)

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

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark sent animals published
        self.markAnimalsPublished(processed, first=True)

        self.cleanup()

    def processAnimal(self, an: ResultRow) -> Dict:
        """ Processes an animal record and returns a data dictionary to upload as JSON """
        p = {
            "animal": {
                "animalId": an.SHELTERCODE,
                "animalName": an.ANIMALNAME.title(),
                "animalType": an.SPECIESNAME,
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
                        "personId": "P100",
                        "firstName": "Taylor",
                        "middleName": "A",
                        "lastName": "Lee",
                        "emails": [
                            {
                                "emailAdress": "taylor@example.com",
                                "type": "Personal",
                                "doNotEmail": False,
                                "sourceReference": {
                                    "sourceId": "EMAIL-1",
                                    "sourceDisplayId": "Personal email",
                                    "dateCreated": "2026-09-17T12:00:00Z",
                                    "dateUpdated": "2026-09-17T12:00:00Z"
                                }
                            }
                        ],
                        "addresses": [
                            {
                                "streetLine1": "123 Main St",
                                "streetLine2": "Apt 4",
                                "city": "Springfield",
                                "stateProvince": "NY",
                                "postalCode": "10001",
                                "country": "US",
                                "doNotMail": False,
                                "sourceReference": {
                                    "sourceId": "ADDR-1",
                                    "sourceDisplayId": "Home address",
                                    "dateCreated": "2026-09-17T12:00:00Z",
                                    "dateUpdated": "2026-09-17T12:00:00Z"
                                }
                            }
                        ],
                        "phoneNumbers": [
                            {
                                "number": "+15555550123",
                                "type": "Mobile",
                                "doNotCall": False,
                                "doNotText": False,
                                "sourceReference": {
                                    "sourceId": "PHONE-1",
                                    "sourceDisplayId": "Mobile phone",
                                    "dateCreated": "2026-09-17T12:00:00Z",
                                    "dateUpdated": "2026-09-17T12:00:00Z"
                                }
                            }
                        ],
                        "sourceReference": {
                            "sourceId": "P100",
                            "sourceDisplayId": "Taylor Lee",
                            "dateCreated": "2026-09-17T12:00:00Z",
                            "dateUpdated": "2026-09-17T12:00:00Z"
                        }
                    }
                ],
            }
        }
        
        return p


