import asm3.configuration
import asm3.dbfs
import asm3.i18n
import asm3.log
import asm3.lookups

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
            "SELECT " \
            "m.ID, " \
            "m.MediaName, " \
            "m.MediaNotes, " \
            "m.MediaMimeType, " \
            "m.DBFSID, " \
            "m.CreatedDate, " \
            "m.LastChangedDate " \
            "FROM media m " \
            "WHERE " \
            "m.LinkTypeID = ? " \
            "AND m.LinkID = ? " \
            "AND m.ExcludeFromPublish = 0 " \
            "AND m.MediaType = ? " \
            "AND m.MediaMimeType = 'image/jpeg'",
            [asm3.media.ANIMAL, animalid, asm3.media.MEDIATYPE_FILE]
        )
        return m

    def getAnimalConditions(self, animalid) -> Results:
            m = self.dbo.query(
                "SELECT " \
                "c.ID, " \
                "l.ConditionName, " \
                "t.ConditionTypeName, " \
                "c.StartDatetime, " \
                "c.EndDatetime, " \
                "c.CreatedDate, " \
                "c.LastChangedDate " \
                "FROM animalcondition c " \
                "INNER JOIN lkcondition l ON c.ConditionID = l.ID " \
                "INNER JOIN lksconditiontype t ON l.ConditionTypeID = t.ID " \
                "WHERE " \
                "c.AnimalID = ?",
                [animalid,]
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
            "c.BaseColour, " \
            "a.BreedName, " \
            "a.DateOfBirth, " \
            "a.IdentichipNumber, " \
            "a.Identichip2Number, " \
            "a.IdentichipDate, " \
            "g.Sex, " \
            "z.Size, " \
            "a.Neutered, " \
            "a.ExtraIDs, " \
            "s.SpeciesName, " \
            "a.LastChangedDate, " \
            "o.OwnerType, " \
            "o.OwnerCode, " \
            "o.OwnerName, " \
            "o.OwnerForeNames, " \
            "o.OwnerForeNames2, " \
            "o.OwnerSurname, " \
            "o.OwnerSurname2, " \
            "o.OwnerAddress, " \
            "o.OwnerTown, " \
            "o.OwnerCounty, " \
            "o.OwnerPostcode, " \
            "o.EmailAddress, " \
            "o.EmailAddress2, " \
            "o.MobileTelephone, " \
            "o.MobileTelephone2, " \
            "o.CreatedDate AS OwnerCreatedDate, " \
            "o.LastChangedDate AS OwnerLastChangedDate, " \
            "(SELECT Comments FROM log WHERE LogTypeID = ? AND LinkType = ? AND LinkID = a.ID AND Date < ? ORDER BY Date desc ) AS AdoptionWeight, " \
            "(SELECT Date FROM log WHERE LogTypeID = ? AND LinkType = ? AND LinkID = a.ID AND Date < ? ORDER BY Date desc ) AS AdoptionWeightDate " \
            "FROM adoption m " \
            "INNER JOIN animal a ON m.AnimalID = a.ID " \
            "INNER JOIN basecolour c ON a.BaseColourID = c.ID " \
            "INNER JOIN lksex g ON a.Sex = g.ID " \
            "INNER JOIN lksize z ON a.Size = z.ID " \
            "INNER JOIN owner o ON m.OwnerID = o.ID " \
            "INNER JOIN species s ON a.SpeciesID = s.ID " \
            "WHERE a.DeceasedDate IS NULL AND m.MovementType = 1 AND m.ReturnDate IS NULL AND m.MovementDate > ?",
            [weightlogtype, asm3.log.ANIMAL, self.dbo.sql_interval("m.MovementDate", 1, "+", "days"), weightlogtype, asm3.log.ANIMAL, self.dbo.sql_interval("m.MovementDate", 1, "+", "days"), lastpublished]
        )
        self.log("Got %d matching animals for publishing." % len(a))
        return a

    def getVaccinations(self, animalid):
        v = self.dbo.query(
            "SELECT " \
            "v.ID, " \
            "t.VaccinationType, " \
            "v.DateOfVaccination, " \
            "v.DateExpires, " \
            "v.BatchExpiryDate, " \
            "v.BatchNumber, " \
            "v.Comments, " \
            "o.OwnerName AS VetName, " \
            "v.Manufacturer, " \
            "v.CreatedDate, " \
            "v.LastChangedDate " \
            "FROM animalvaccination v " \
            "INNER JOIN vaccinationtype t ON v.VaccinationID = t.ID " \
            "LEFT JOIN owner o ON v.AdministeringVetID = o.ID " \
            "WHERE " \
            "v.AnimalID = ? ",
            [animalid,]
        )
        return v

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

                payload = {
                    "userName": asm3.configuration.petszel_client_id(self.dbo),
                    "password": asm3.configuration.petszel_client_secret(self.dbo)
                }
                headers = {
                    'Content-Type': 'application/json'
                }
                r = asm3.utils.post_json(f"{PETSZEL_URL}/Authorize", asm3.utils.json(payload), headers)
                if r["status"] == 200:
                    token = asm3.utils.json_parse(r["response"])["token"]
                else:
                    return

                payload = self.processAnimal(an)
                headers = {
                    'Authorization': 'Bearer ' + token,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }

                r = asm3.utils.post_json(f"{PETSZEL_URL}/api/v1/ingestion/animal-lifecycle", asm3.utils.json(payload), headers)

                if r["status"] != 202:
                    self.logError("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                    # Update animalpublished for this animal with the error code so that it's visible in the UI
                    # that we tried and what the error was.
                    errormsg = str(r["response"])
                    self.markAnimalPublished(an.ID, extra = errormsg)
                else:
                    self.log("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                    processed.append(an)
                    correlationid = asm3.utils.json_parse(r["response"])["correlationId"]
                    asm3.animal.set_extra_id(self.dbo, "pub::petszel", an, IDTYPE_PETSZEL, correlationid)

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark sent animals published
        self.markAnimalsPublished(processed, first=True)

        self.cleanup()

    def processAnimal(self, an: ResultRow) -> Dict:
        """ Processes an animal record and returns a data dictionary to upload as JSON """

        ofirstname = an.OWNERFORENAMES.split(" ")[0]
        omiddlenames = ""
        if " " in an.OWNERFORENAMES:
            omiddlenames = " ".join(an.OWNERFORENAMES.split(" ")[0][1:])
        
        address = self.splitAddress(an.OWNERADDRESS)
        emails = []
        if an.EMAILADDRESS:
            emails.append(
                {
                    "emailAddress": an.EMAILADDRESS,
                    "type": "Personal",
                    "doNotEmail": False,
                    "sourceReference": {
                        "sourceSystem": "ASM",
                        "sourceId": an.OWNERCODE,
                        "sourceDisplayId": "Personal email",
                        "dateCreated": asm3.i18n.python2iso(an.OWNERCREATEDDATE, self.dbo.timezone),
                        "dateUpdated": asm3.i18n.python2iso(an.OWNERLASTCHANGEDDATE, self.dbo.timezone)
                    }
                }
            )
        phonenumbers = []
        if an.MOBILETELEPHONE:
            phonenumbers.append(
                {
                    "number": an.MOBILETELEPHONE,
                    "type": "Mobile",
                    "doNotCall": False,
                    "doNotText": False,
                    "sourceReference": {
                        "sourceSystem": "ASM",
                        "sourceId": an.OWNERCODE,
                        "sourceDisplayId": "Mobile phone",
                        "dateCreated": asm3.i18n.python2iso(an.OWNERCREATEDDATE, self.dbo.timezone),
                        "dateUpdated": asm3.i18n.python2iso(an.OWNERLASTCHANGEDDATE, self.dbo.timezone)
                    }
                }
            )
        
        participants = [
            {
                "personId": an.OWNERCODE,
                "firstName": ofirstname,
                "middleName": omiddlenames,
                "lastName": an.OWNERSURNAME,
                "emails": emails,
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
                            "sourceSystem": "ASM",
                            "sourceId": an.OWNERCODE,
                            "sourceDisplayId": "Home address",
                            "dateCreated": asm3.i18n.python2iso(an.OWNERCREATEDDATE, self.dbo.timezone),
                            "dateUpdated": asm3.i18n.python2iso(an.OWNERLASTCHANGEDDATE, self.dbo.timezone)
                        }
                    }
                ],
                "phoneNumbers": phonenumbers,
                "sourceReference": {
                    "sourceSystem": "ASM",
                    "sourceId": an.OWNERCODE,
                    "sourceDisplayId": an.OWNERNAME,
                    "dateCreated": asm3.i18n.python2iso(an.OWNERCREATEDDATE, self.dbo.timezone),
                    "dateUpdated": asm3.i18n.python2iso(an.OWNERLASTCHANGEDDATE, self.dbo.timezone)
                }
            }
        ]

        if an.OWNERTYPE == 3: # Owner is a couple
            ofirstname = an.OWNERFORENAMES2.split(" ")[0]
            omiddlenames = ""
            if " " in an.OWNERFORENAMES2:
                omiddlenames = " ".join(an.OWNERFORENAMES2.split(" ")[0][1:])
            emails = []
            if an.EMAILADDRESS2:
                emails.append(
                    {
                        "emailAddress": an.EMAILADDRESS2,
                        "type": "Personal",
                        "doNotEmail": False,
                        "sourceReference": {
                            "sourceSystem": "ASM",
                            "sourceId": an.OWNERCODE,
                            "sourceDisplayId": "Personal email",
                            "dateCreated": asm3.i18n.python2iso(an.OWNERCREATEDDATE, self.dbo.timezone),
                            "dateUpdated": asm3.i18n.python2iso(an.OWNERLASTCHANGEDDATE, self.dbo.timezone)
                        }
                    }
                )
            phonenumbers = []
            if an.MOBILETELEPHONE2:
                phonenumbers.append(
                    {
                        "number": an.MOBILETELEPHONE2,
                        "type": "Mobile",
                        "doNotCall": False,
                        "doNotText": False,
                        "sourceReference": {
                            "sourceSystem": "ASM",
                            "sourceId": an.OWNERCODE,
                            "sourceDisplayId": "Mobile phone",
                            "dateCreated": asm3.i18n.python2iso(an.OWNERCREATEDDATE, self.dbo.timezone),
                            "dateUpdated": asm3.i18n.python2iso(an.OWNERLASTCHANGEDDATE, self.dbo.timezone)
                        }
                    }
                )

            participants.append(
                {
                    "personId": an.OWNERCODE,
                    "firstName": ofirstname,
                    "middleName": omiddlenames,
                    "lastName": an.OWNERSURNAME2,
                    "emails": emails,
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
                                "sourceSystem": "ASM",
                                "sourceId": an.OWNERCODE,
                                "sourceDisplayId": "Home address",
                                "dateCreated": asm3.i18n.python2iso(an.OWNERCREATEDDATE, self.dbo.timezone),
                                "dateUpdated": asm3.i18n.python2iso(an.OWNERLASTCHANGEDDATE, self.dbo.timezone)
                            }
                        }
                    ],
                    "phoneNumbers": phonenumbers,
                    "sourceReference": {
                        "sourceSystem": "ASM",
                        "sourceId": an.OWNERCODE,
                        "sourceDisplayId": an.OWNERNAME,
                        "dateCreated": asm3.i18n.python2iso(an.OWNERCREATEDDATE, self.dbo.timezone),
                        "dateUpdated": asm3.i18n.python2iso(an.OWNERLASTCHANGEDDATE, self.dbo.timezone)
                    }
                }
            )

        p = {
            "animal": 
                { "animal": {
                    "animalId": an.SHELTERCODE,
                    "name": an.ANIMALNAME.title(),
                    "dateOfBirth": asm3.i18n.python2iso(an.DATEOFBIRTH, self.dbo.timezone),
                    "adoptionDate": asm3.i18n.python2iso(an.ACTIVEMOVEMENTDATE, self.dbo.timezone),
                    "animalType": an.SPECIESNAME,
                    "sex": an.SEX,
                    "sizeGroup": an.SIZE,
                    "breeds": [an.BREEDNAME],
                    "colors": [an.BASECOLOUR],
                    "sourceReference": {
                        "sourceSystem": "ASM",
                        "sourceId": an.SHELTERCODE,
                        "dateUpdated": asm3.i18n.python2iso(an.LASTCHANGEDDATE, self.dbo.timezone)
                    }
                }
            },
            "lifecycleEvent": {
                "eventType": "Adoption",
                "eventDirection": "Outcome",
                "occurredAt": asm3.i18n.python2iso(an.ACTIVEMOVEMENTDATE, self.dbo.timezone)
            },
            "participants": participants
            
        }
        if an.ADOPTIONWEIGHT:
            p["animal"]["adoptedWeight"] = an.ADOPTIONWEIGHT
            p["animal"]["adoptedWeightDate"] = asm3.i18n.python2iso(an.ADOPTIONWEIGHTDATE, self.dbo.timezone)
        if an.NEUTERED:
            if an.SEX == "Male":
                p["animal"]["altered"] = "Neutered"
            elif an.SEX == "Female":
                p["animal"]["altered"] = "Spayed"
        if an.IDENTICHIPNUMBER:
            chipno = an.IDENTICHIPNUMBER
            if an.IDENTICHIP2NUMBER:
                chipno += " " + an.IDENTICHIP2NUMBER
            chipco = asm3.lookups.get_microchip_manufacturer(self.dbo.locale, an.IDENTICHIPNUMBER)
            p["animal"]["microchip"] = {
                "microchipNumber": chipno,
                "issuer": chipco,
                "implantedDate": asm3.i18n.python2iso(an.IDENTICHIPDATE, self.dbo.timezone),
                "sourceReference": {
                    "sourceSystem": "ASM",
                    "sourceId": an.SHELTERCODE,
                    "sourceDisplayId": "Microchip"
                }
            }
        animalconditions = self.getAnimalConditions(an.ID)
        if len(animalconditions):
            conditions = []
            for c in animalconditions:
                conditions.append(
                    {
                        "conditionName": c.CONDITIONNAME,
                        "conditionType": c.CONDITIONTYPENAME,
                        "onsetDate": asm3.i18n.python2iso(c.STARTDATETIME, self.dbo.timezone),
                        "resolutionDate": asm3.i18n.python2iso(c.ENDDATETIME, self.dbo.timezone),
                        "sourceReference": {
                            "sourceSystem": "ASM",
                            "sourceId": str(c.ID),
                            "dateCreated": asm3.i18n.python2iso(c.CREATEDDATE, self.dbo.timezone),
                            "dateUpdated": asm3.i18n.python2iso(c.LASTCHANGEDDATE, self.dbo.timezone)
                        }
                    }
                )
            p["conditions"] = conditions

        animalmedia = self.getAnimalMedia(an.ID)
        if len(animalmedia):
            photos = []
            for m in animalmedia:
                mediabytes = asm3.dbfs.get_string_id(self.dbo, m.DBFSID)
                imagewidth, imageheight = asm3.media.image_dimensions(mediabytes)
                photos.append(
                    {
                        "photoId": str(m.ID),
                        "contentBase64": asm3.utils.base64encode(mediabytes),
                        "photoName": m.MEDIANAME,
                        "photoType": "image/jpeg",
                        "isPublic": True,
                        "description": m.MEDIANOTES,
                        "height": imageheight,
                        "width": imagewidth,
                        "sourceReference": {
                            "sourceSystem": "ASM",
                            "sourceId": str(m.ID),
                            "sourceDisplayId": m.MEDIANAME,
                            "dateCreated": asm3.i18n.python2iso(m.CREATEDDATE, self.dbo.timezone),
                            "dateUpdated": asm3.i18n.python2iso(m.LASTCHANGEDDATE, self.dbo.timezone)
                        }
                    }
                )
            p["photos"] = photos

            animalvaccinations = self.getVaccinations(an.ID)
            if len(animalvaccinations):
                vaccinations = []
                for v in animalvaccinations:
                    vaccineduration = 0
                    if v.DATEOFVACCINATION and v.DATEEXPIRES:
                        vaccineduration = (v.DATEEXPIRES - v.DATEOFVACCINATION).days
                    vaccination = {
                            "vaccineName": v.VACCINATIONTYPE,
                            "status": "Administered",
                            # "type": "Core",
                            # "subType": "One year",
                            "vaccinationDate": asm3.i18n.python2iso(v.DATEOFVACCINATION, self.dbo.timezone),
                            "reVaccinationDate": asm3.i18n.python2iso(v.DATEEXPIRES, self.dbo.timezone),
                            "expirationDate": asm3.i18n.python2iso(v.BATCHEXPIRYDATE, self.dbo.timezone),
                            # "providerLicenseNumber": "VET-123",
                            "manufacturerName": v.MANUFACTURER,
                            # "brandName": "Example Vaccine",
                            "lotNumber": v.BATCHNUMBER,
                            "lotExpiration": asm3.i18n.python2iso(v.BATCHEXPIRYDATE, self.dbo.timezone),
                            # "administeredBodyPart": "Right hind leg",
                            # "administeredRoute": "Subcutaneous",
                            # "tagNumber": "TAG-123",
                            # "tagExpiration": "2027-08-01T12:00:00Z",
                            "description": v.COMMENTS,
                            "sourceReference": {
                                "sourceSystem": "ASM",
                                "sourceId": str(v.ID),
                                "sourceDisplayId": v.VACCINATIONTYPE,
                                "dateCreated": asm3.i18n.python2iso(v.CREATEDDATE, self.dbo.timezone),
                                "dateUpdated": asm3.i18n.python2iso(v.LASTCHANGEDDATE, self.dbo.timezone)
                            }
                    }
                    if vaccineduration:
                        vaccination["duration"] = vaccineduration
                    if v.VETNAME:
                        vaccination["providerName"] = v.VETNAME
                    vaccinations.append(vaccination)
                p["vaccines"] = vaccinations

        # return asm3.utils.json(p, True)
        return p


