
import asm3.configuration
import asm3.i18n
import asm3.medical
import asm3.utils

from .base import AbstractPublisher
from asm3.sitedefs import PETSZEL_URL
from asm3.typehints import Database, Dict, List, PublishCriteria, ResultRow

import sys

class PetszelPublisher(AbstractPublisher):
    """
    Handles publishing to petszel.com

    Note: Requires json files of breeds that are stored in static/publishers/petrescue
    """
    breeds = None
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("petrescue", "PetRescue Publisher")

    def run(self) -> None:
        
        self.log("Petszel Publisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        animals = self.getMatchingAnimals(includeAdditionalFields=True)
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
                "animalId": "A123456",
                "animalName": an.ANIMALNAME.title(),
                "animalType": an.SPECIESNAME,
                "sourceReference": {
                    "sourceId": "A123456",
                    "dateUpdated": "2026-09-17T12:00:00Z"
                }
            },
            "event": {
                "type": "Adoption",
                "date": "2026-09-17T12:00:00Z"
            }
        }
        return p


