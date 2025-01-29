
import asm3.configuration
import asm3.i18n
import asm3.medical
import asm3.utils

from .base import AbstractPublisher
from asm3.sitedefs import SAC_METRICS_URL, SAC_METRICS_API_KEY
from asm3.typehints import Database, Dict, List, PublishCriteria, Tuple

import sys

class SACMetricsPublisher(AbstractPublisher):
    """
    Handles publishing stats/metrics to shelteranimalscount.org

    Unlike other publishers, has no processAnimal function and does not markAnimalPublished
    since the data we are sending is aggregate stats rather than individual line level data.
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("shelteranimalscount", "ShelterAnimalsCount Publisher")

    def analyseMonths(self) -> List[Tuple[int, int]]:
        """
        Construct and return the list of months that we are going to run for.
        months are a list of tuples of month, year as integers. 
        """
        def d2m(d):
            return "%s%02d" % (d.year, d.month)
        def m2t(m):
            return (asm3.utils.cint(m[4:]), asm3.utils.cint(m[0:4]))
        dbo = self.dbo

        # Construct the list of months that we are going to run for.
        # months are a list of tuples of month, year as integers. 
        monthset = set()
        self.log("Analysing months to send to SAC ...")

        # If today is the 1st of the month, run for last month
        if dbo.today().day == 1:
            monthset.add( d2m(dbo.today(offset=-2)) )
            self.log("Add month %s (last month), triggered by today being the 1st of the month" % d2m(dbo.today(offset=-2)))

        # Find animals and movements where lastchangeddate is in the last 24 hours,
        # return a list of MostRecentEntryDate, DeceasedDate, MovementDate and ReturnDate fields, 
        # which we parse into a set of months/years that will require an update sending.
        # (these are the 4 fields that determine intake and outcome)
        animals = dbo.query("SELECT ID, ShelterCode, MostRecentEntryDate, DeceasedDate FROM animal WHERE LastChangedDate >= ?", [ dbo.now(offset=-1) ])
        movements = dbo.query("SELECT AnimalID, MovementDate, ReturnDate FROM adoption WHERE LastChangedDate >= ?", [ dbo.now(offset=-1) ])
        for a in animals:
            if a.MOSTRECENTENTRYDATE and a.MOSTRECENTENTRYDATE < dbo.today(): 
                monthset.add( d2m(a.MOSTRECENTENTRYDATE) )
                self.log("Add month %s (intake), triggered by changes to animal %s (%s)" % (d2m(a.MOSTRECENTENTRYDATE), a.ID, a.SHELTERCODE))
            if a.DECEASEDDATE and a.DECEASEDDATE < dbo.today(): 
                monthset.add( d2m(a.DECEASEDDATE) )
                self.log("Add month %s (deceased), triggered by changes to animal %s (%s)" % (d2m(a.DECEASEDDATE), a.ID, a.SHELTERCODE))
        for m in movements:
            if m.MOVEMENTDATE and m.MOVEMENTDATE < dbo.today(): 
                monthset.add( d2m(m.MOVEMENTDATE) )
                self.log("Add month %s (movement), triggered by changes to animal %s" % (d2m(m.MOVEMENTDATE), a.ID))
            if m.RETURNDATE and m.RETURNDATE < dbo.today(): 
                monthset.add( d2m(m.RETURNDATE) )
                self.log("Add month %s (return), triggered by changes to animal %s" % (d2m(m.RETURNDATE), a.ID))

        # Remove this month from the set as we would be premature doing this month now.
        thismonth = d2m(dbo.today())
        self.log("remove this month: %s" % thismonth)
        if thismonth in monthset: monthset.remove(thismonth)

        self.log("Running SAC Metrics for months: %s" % monthset)

        # months are a list of tuples in the form ( month (int), year (int) )
        months = []
        for mo in monthset:
            months.append(m2t(mo))
        return months

    def run(self) -> None:
        
        self.log("SACMetricsPublisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        months = self.analyseMonths()

        if len(months) == 0:
            self.setLastError("Found no changes in previous months to send to SAC.")
            return

        # Now run each section for the appropriate species for each period and construct our JSON document. 
        mCount = 0
        for month, year in months:
            try:
                mCount += 1
                self.log("Processing: year=%s, month=%s" % (year, month))
                self.updatePublisherProgress(self.getProgress(mCount, len(months)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return

                # Run our query for every species set, and post the JSON to SAC
                for specieslist in [ "canine", "feline", "rabbit", "equine", "small_mammal", "bird", "farm_animal", "reptile_or_amphibian" ]:
                    data = self.processStats(month, year, specieslist)
                    self.putData(data)
              
            except Exception as err:
                self.logError("Failed processing period: year=%s, month=%s '%s'" % (year, month, err), sys.exc_info())

        self.cleanup()

    def putData(self, data: Dict) -> None:
        """ Sends the data (obj tree) to SAC """
        try:
            url = SAC_METRICS_URL 
            year = data["recordYear"]
            month = data["recordMonth"]
            speciesname = data["species"]
            jsondata = asm3.utils.json(data)
            headers = { "apikey": SAC_METRICS_API_KEY }
            self.log("Sending PUT to %s to upsert metrics: \n\n%s\n" % (url, jsondata))
            r = asm3.utils.put_json(url, jsondata, headers=headers)
            if r["status"] != 200:
                self.logError("HTTP %d, headers: %s\nresponse: %s" % (r["status"], r["headers"], r["response"]))
            else:
                self.log("HTTP %d, headers: %s\nresponse: %s" % (r["status"], r["headers"], r["response"]))
                self.logSuccess("Processed: year=%s, month=%s, species=%s" % ( year, month, speciesname ))
        except Exception as err:
            self.logError("Failed processing period: year=%s, month=%s, species=%s '%s'" % (year, month, speciesname, err), sys.exc_info())

    def processStats(self, month: int, year: int, speciesname: str, externalId: str = "") -> Dict:
        """ Given a month, year and a key from SAC_SPECIES, produces the list of 
            SAC Metrics for that combination and returns an object representation
            of the JSON document that will fulfil SAC metricsDataDto
            month: (int)
            year: (int)
            speciesname: (str) from SAC_SPECIES
            externalId: The externalId value to use, defaults to dbo.name() (sm account number) if not set
        """
        dbo = self.dbo
        fromdate = asm3.i18n.parse_date("%Y-%m-%d", "%s-%02d-01" % (year, month))
        todate = asm3.i18n.last_of_month(fromdate)
        todate = todate.replace(hour=23, minute=59, second=59)

        tokens = {
            "from": dbo.sql_date(fromdate),
            "to": dbo.sql_date(todate),
            "specieslist": SAC_SPECIES[speciesname],
            "broughtinm5": dbo.sql_interval("DateBroughtIn", sign="-", number=5, units="months"),
            "deceasedm5": dbo.sql_interval("DeceasedDate", sign="-", number=5, units="months"),
            "returnedm5": dbo.sql_interval("ReturnDate", sign="-", number=5, units="months"),
            "movementm5": dbo.sql_interval("MovementDate", sign="-", number=5, units="months")
        }
        sql = SAC_SPECIES_QUERY.format(**tokens)
        r = self.dbo.first_row(self.dbo.query(sql))

        # Construct the JSON response as a big static object
        return {
            "animalCounts": {
                "beginingCount": {
                    "count": r.BEGINNINGINSHELTER,
                    "date": asm3.i18n.format_date(fromdate, "%Y-%m-%d"),
                    "fosterAnimalCount": r.BEGINNINGONFOSTER
                },
                "endiningCount": {
                    "count": r.ENDINGINSHELTER,
                    "date": asm3.i18n.format_date(todate, "%Y-%m-%d"),
                    "fosterAnimalCount": r.ENDINGONFOSTER
                }
            },
            "liveIntake": {
                "adult": {
                    "otherIntakes": r.ADULTOTHERINTAKE + r.ADULTOTHERRETURN,
                    "ownerIntendedEuthanasia": r.ADULTREQUESTEDEUTH,
                    "relinquishedbyOwner": r.ADULTSURRENDER + r.ADULTADOPTIONRETURN,
                    "seizedOrImpounded": r.ADULTIMPOUND,
                    "strayAtLarge": r.ADULTSTRAY,
                    "transferredinFromAgency": {
                        "inState": r.ADULTTRANSFERINSTATE,
                        "international": 0,
                        "outOfState": r.ADULTTRANSFEROUTSTATE
                    }
                },
                "ageUnknown": {
                    "otherIntakes": 0,
                    "ownerIntendedEuthanasia": 0,
                    "relinquishedbyOwner": 0,
                    "seizedOrImpounded": 0,
                    "strayAtLarge": 0,
                    "transferredinFromAgency": {
                        "inState": 0,
                        "international": 0,
                        "outOfState": 0
                    }
                },
                "upToFiveMonths": {
                    "otherIntakes": r.JUNIOROTHERINTAKE + r.JUNIOROTHERRETURN,
                    "ownerIntendedEuthanasia": r.JUNIORREQUESTEDEUTH,
                    "relinquishedbyOwner": r.JUNIORSURRENDER + r.JUNIORADOPTIONRETURN,
                    "seizedOrImpounded": r.JUNIORIMPOUND,
                    "strayAtLarge": r.JUNIORSTRAY,
                    "transferredinFromAgency": {
                        "inState": r.JUNIORTRANSFERINSTATE,
                        "international": 0,
                        "outOfState": r.JUNIORTRANSFEROUTSTATE
                    }
                }
            },
            "organization": {
                "externalId": asm3.utils.iif(externalId != "", externalId, dbo.name()),
                "name": asm3.configuration.organisation(dbo),
                "vendorName": "Shelter_Manager"
            },
            "outComes": {
                "liveOutcomes": {
                    "adult": {
                        "adoption": r.ADULTADOPTION,
                        "otherLiveOutcome": r.ADULTOTHERLIVE,
                        "returnedToField": r.ADULTRETURNTOFIELD,
                        "returnedToOwner": r.ADULTRECLAIM,
                        "transferredToAgency": {
                            "inState": r.ADULTTRANSFEROUTINSTATE,
                            "international": 0,
                            "outOfState": r.ADULTTRANSFEROUTOUTSTATE
                        }
                    },
                    "ageUnknown": {
                        "adoption": 0,
                        "otherLiveOutcome": 0,
                        "returnedToField": 0,
                        "returnedToOwner": 0,
                        "transferredToAgency": {
                            "inState": 0,
                            "international": 0,
                            "outOfState": 0
                        }
                    },
                    "upToFiveMonths": {
                        "adoption": r.JUNIORADOPTION,
                        "otherLiveOutcome": r.JUNIOROTHERLIVE,
                        "returnedToField": r.JUNIORRETURNTOFIELD,
                        "returnedToOwner": r.JUNIORRECLAIM,
                        "transferredToAgency": {
                            "inState": r.JUNIORTRANSFEROUTINSTATE,
                            "international": 0,
                            "outOfState": r.JUNIORTRANSFEROUTOUTSTATE
                        }
                    }
                },
                "otherOutcomes": {
                    "adult": {
                        "diedInCare": r.ADULTDIEDCARE,
                        "lostInCare": r.ADULTLOSTINCARE,
                        "ownerIntendedEuthanasia": r.ADULTOUTREQEUTH,
                        "shelterEuthanasia": r.ADULTEUTHANASIA
                    },
                    "ageUnknown": {
                        "diedInCare": 0,
                        "lostInCare": 0,
                        "ownerIntendedEuthanasia": 0,
                        "shelterEuthanasia": 0
                    },
                    "upToFiveMonths": {
                        "diedInCare": r.JUNIORDIEDCARE,
                        "lostInCare": r.JUNIORLOSTINCARE,
                        "ownerIntendedEuthanasia": r.JUNIOROUTREQEUTH,
                        "shelterEuthanasia": r.JUNIOREUTHANASIA
                    }
                }
            },
            "recordMonth": str(month),
            "recordYear": str(year),
            "species": speciesname
        }

# ==============================================
SAC_SP_CANINES = "1"
SAC_SP_FELINES = "2"
SAC_SP_RABBITS = "7"
SAC_SP_EQUINES = "24,25,26"
SAC_SP_SMALLMAMMALS = "4,5,9,10,18,20,22"
SAC_SP_FARMANIMALS = "16,27,28"
SAC_SP_BIRDS = "3,14,15,17"
SAC_SP_REPTILES = "11,12,13"

SAC_SPECIES = {
    "canine": SAC_SP_CANINES,
    "feline": SAC_SP_FELINES,
    "rabbit": SAC_SP_RABBITS,
    "equine": SAC_SP_EQUINES,
    "small_mammal": SAC_SP_SMALLMAMMALS,
    "farm_animal": SAC_SP_FARMANIMALS,
    "bird": SAC_SP_BIRDS,
    "reptile_or_amphibian": SAC_SP_REPTILES
}

SAC_SPECIES_QUERY = """SELECT 

(SELECT COUNT(*) FROM animal WHERE 
NOT EXISTS (SELECT MovementDate FROM adoption WHERE MovementDate < {from} AND (ReturnDate Is Null OR ReturnDate >= {from}) AND MovementType NOT IN (2,8) AND AnimalID = animal.ID)
AND DateBroughtIn < {from}
AND NonShelterAnimal = 0 AND IsDOA = 0
AND SpeciesID IN ({specieslist})
AND (DeceasedDate Is Null OR DeceasedDate >= {from})) AS BeginningInShelter,

(SELECT COUNT(*) FROM animal WHERE 
EXISTS (SELECT MovementDate FROM adoption WHERE MovementDate < {from} AND (ReturnDate Is Null OR ReturnDate >= {from}) AND MovementType = 2 AND AnimalID = animal.ID)
AND DateBroughtIn < {from}
AND NonShelterAnimal = 0
AND SpeciesID IN ({specieslist})
AND (DeceasedDate Is Null OR DeceasedDate >= {from})) AS BeginningOnFoster,

(SELECT COUNT(*) FROM animal WHERE 
NOT EXISTS (SELECT MovementDate FROM adoption WHERE MovementDate <= {to} AND (ReturnDate Is Null OR ReturnDate > {to}) AND MovementType NOT IN (2,8) AND AnimalID = animal.ID)
AND DateBroughtIn <= {to}
AND NonShelterAnimal = 0 AND IsDOA = 0
AND SpeciesID IN ({specieslist})
AND (DeceasedDate Is Null OR DeceasedDate > {to})) AS EndingInShelter,

(SELECT COUNT(*) FROM animal WHERE 
EXISTS (SELECT MovementDate FROM adoption WHERE MovementDate <= {to} AND (ReturnDate Is Null OR ReturnDate > {to}) AND MovementType = 2 AND AnimalID = animal.ID)
AND DateBroughtIn <= {to}
AND NonShelterAnimal = 0
AND SpeciesID IN ({specieslist})
AND (DeceasedDate Is Null OR DeceasedDate > {to})) AS EndingOnFoster,

(SELECT COUNT(*) FROM animal
INNER JOIN entryreason ON entryreason.ID = animal.EntryReasonID
WHERE EntryTypeID = 2 
AND DateBroughtIn >= {from} AND DateBroughtIn <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth < {broughtinm5}
AND NonShelterAnimal = 0) AS AdultStray,

(SELECT COUNT(*) FROM animal 
INNER JOIN entryreason ON entryreason.ID = animal.EntryReasonID
WHERE EntryTypeID = 2
AND DateBroughtIn >= {from} AND DateBroughtIn <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth >= {broughtinm5}
AND NonShelterAnimal = 0) AS JuniorStray,

(SELECT COUNT(*) FROM animal
WHERE EntryTypeID = 1
AND AsilomarOwnerRequestedEuthanasia = 0
AND DateBroughtIn >= {from} AND DateBroughtIn <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth < {broughtinm5} 
AND NonShelterAnimal = 0) AS AdultSurrender,

(SELECT COUNT(*) FROM animal 
WHERE EntryTypeID = 1
AND AsilomarOwnerRequestedEuthanasia = 0
AND DateBroughtIn >= {from} AND DateBroughtIn <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth >= {broughtinm5} 
AND NonShelterAnimal = 0) AS JuniorSurrender,

(SELECT COUNT(*) FROM animal
WHERE EntryTypeID = 3
AND (animal.BroughtInByOwnerID = 0 OR (SELECT OwnerCounty FROM owner WHERE ID = animal.BroughtInByOwnerID) = 
(SELECT ItemValue FROM configuration WHERE ItemName = 'OrganisationCounty'))
AND DateBroughtIn >= {from} AND DateBroughtIn <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth < {broughtinm5}
AND NonShelterAnimal = 0) AS AdultTransferInState,

(SELECT COUNT(*) FROM animal 
WHERE EntryTypeID = 3
AND (animal.BroughtInByOwnerID = 0 OR (SELECT OwnerCounty FROM owner WHERE ID = animal.BroughtInByOwnerID) = 
(SELECT ItemValue FROM configuration WHERE ItemName = 'OrganisationCounty'))
AND DateBroughtIn >= {from} AND DateBroughtIn <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth >= {broughtinm5} 
AND NonShelterAnimal = 0) AS JuniorTransferInState,

(SELECT COUNT(*) FROM animal
WHERE EntryTypeID = 3
AND (animal.BroughtInByOwnerID <> 0 AND (SELECT OwnerCounty FROM owner WHERE ID = animal.BroughtInByOwnerID) <> 
(SELECT ItemValue FROM configuration WHERE ItemName = 'OrganisationCounty'))
AND DateBroughtIn >= {from} AND DateBroughtIn <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth < {broughtinm5}
AND NonShelterAnimal = 0) AS AdultTransferOutState,

(SELECT COUNT(*) FROM animal 
WHERE EntryTypeID = 3
AND (animal.BroughtInByOwnerID <> 0 AND (SELECT OwnerCounty FROM owner WHERE ID = animal.BroughtInByOwnerID) <> 
(SELECT ItemValue FROM configuration WHERE ItemName = 'OrganisationCounty'))
AND DateBroughtIn >= {from} AND DateBroughtIn <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth >= {broughtinm5} 
AND NonShelterAnimal = 0) AS JuniorTransferOutState,

(SELECT COUNT(*) FROM animal
WHERE EntryTypeID = 10
AND DateBroughtIn >= {from} AND DateBroughtIn <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth < {broughtinm5} 
AND NonShelterAnimal = 0) AS AdultRequestedEuth,

(SELECT COUNT(*) FROM animal 
WHERE EntryTypeID = 10
AND DateBroughtIn >= {from} AND DateBroughtIn <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth >= {broughtinm5} 
AND NonShelterAnimal = 0) AS JuniorRequestedEuth,

(SELECT COUNT(*) FROM animal
WHERE EntryTypeID = 7
AND DateBroughtIn >= {from} AND DateBroughtIn <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth < {broughtinm5} 
AND NonShelterAnimal = 0) AS AdultImpound,

(SELECT COUNT(*) FROM animal 
WHERE EntryTypeID = 7
AND DateBroughtIn >= {from} AND DateBroughtIn <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth >= {broughtinm5} 
AND NonShelterAnimal = 0) AS JuniorImpound,

(SELECT COUNT(*) FROM animal
WHERE EntryTypeID NOT IN (1,2,3,7)
AND AsilomarOwnerRequestedEuthanasia = 0
AND DateBroughtIn >= {from} AND DateBroughtIn <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth < {broughtinm5} 
AND NonShelterAnimal = 0) AS AdultOtherIntake,

(SELECT COUNT(*) FROM animal 
WHERE EntryTypeID NOT IN (1,2,3,7)
AND AsilomarOwnerRequestedEuthanasia = 0
AND DateBroughtIn >= {from} AND DateBroughtIn <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth >= {broughtinm5} 
AND NonShelterAnimal = 0) AS JuniorOtherIntake,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
WHERE MovementType = 1
AND ReturnDate >= {from} AND ReturnDate <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth < {returnedm5} 
AND NonShelterAnimal = 0) AS AdultAdoptionReturn,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
WHERE MovementType = 1
AND ReturnDate >= {from} AND ReturnDate <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth >= {returnedm5} 
AND NonShelterAnimal = 0) AS JuniorAdoptionReturn,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
WHERE MovementType NOT IN (1,2,8)
AND ReturnDate >= {from} AND ReturnDate <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth < {returnedm5} 
AND NonShelterAnimal = 0) AS AdultOtherReturn,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
WHERE MovementType NOT IN (1,2,8)
AND ReturnDate >= {from} AND ReturnDate <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth >= {returnedm5} 
AND NonShelterAnimal = 0) AS JuniorOtherReturn,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
WHERE MovementType = 1
AND MovementDate >= {from} AND MovementDate <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth < {movementm5} 
AND NonShelterAnimal = 0) AS AdultAdoption,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
WHERE MovementType = 1
AND MovementDate >= {from} AND MovementDate <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth >= {movementm5} 
AND NonShelterAnimal = 0) AS JuniorAdoption,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
WHERE MovementType = 5
AND MovementDate >= {from} AND MovementDate <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth < {movementm5} 
AND NonShelterAnimal = 0) AS AdultReclaim,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
WHERE MovementType = 5
AND MovementDate >= {from} AND MovementDate <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth >= {movementm5} 
AND NonShelterAnimal = 0) AS JuniorReclaim,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
INNER JOIN owner ON owner.ID = adoption.OwnerID
WHERE MovementType = 3
AND owner.OwnerCounty = (SELECT ItemValue FROM configuration WHERE ItemName = 'OrganisationCounty')
AND MovementDate >= {from} AND MovementDate <= {to} 
AND SpeciesID IN ({specieslist})
AND animal.DateOfBirth < {movementm5} 
AND NonShelterAnimal = 0) AS AdultTransferOutInState,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
INNER JOIN owner ON owner.ID = adoption.OwnerID
WHERE MovementType = 3
AND owner.OwnerCounty = (SELECT ItemValue FROM configuration WHERE ItemName = 'OrganisationCounty')
AND MovementDate >= {from} AND MovementDate <= {to} 
AND SpeciesID IN ({specieslist})
AND animal.DateOfBirth >= {movementm5} 
AND NonShelterAnimal = 0) AS JuniorTransferOutInState,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
INNER JOIN owner ON owner.ID = adoption.OwnerID
WHERE MovementType = 3
AND owner.OwnerCounty <> (SELECT ItemValue FROM configuration WHERE ItemName = 'OrganisationCounty')
AND MovementDate >= {from} AND MovementDate <= {to} 
AND SpeciesID IN ({specieslist})
AND animal.DateOfBirth < {movementm5} 
AND NonShelterAnimal = 0) AS AdultTransferOutOutState,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
INNER JOIN owner ON owner.ID = adoption.OwnerID
WHERE MovementType = 3
AND owner.OwnerCounty <> (SELECT ItemValue FROM configuration WHERE ItemName = 'OrganisationCounty')
AND MovementDate >= {from} AND MovementDate <= {to} 
AND SpeciesID IN ({specieslist})
AND animal.DateOfBirth >= {movementm5} 
AND NonShelterAnimal = 0) AS JuniorTransferOutOutState,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
WHERE MovementType = 7 AND EntryTypeID <> 4
AND MovementDate >= {from} AND MovementDate <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth < {movementm5} 
AND NonShelterAnimal = 0) AS AdultReturnToField,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
WHERE MovementType = 7 AND EntryTypeID <> 4
AND MovementDate >= {from} AND MovementDate <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth >= {movementm5} 
AND NonShelterAnimal = 0) AS JuniorReturnToField,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
WHERE MovementType IN (4, 6)
AND MovementDate >= {from} AND MovementDate <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth < {movementm5} 
AND NonShelterAnimal = 0) AS AdultLostInCare,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
WHERE MovementType IN (4, 6)
AND MovementDate >= {from} AND MovementDate <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth >= {movementm5} 
AND NonShelterAnimal = 0) AS JuniorLostInCare,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
WHERE MovementType = 7 AND EntryTypeID = 4
AND MovementDate >= {from} AND MovementDate <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth < {movementm5} 
AND NonShelterAnimal = 0) AS AdultOtherLive,

(SELECT COUNT(*) FROM animal
INNER JOIN adoption ON animal.ID = adoption.AnimalID 
WHERE MovementType = 7 AND EntryTypeID = 4
AND MovementDate >= {from} AND MovementDate <= {to} 
AND SpeciesID IN ({specieslist})
AND DateOfBirth >= {movementm5} 
AND NonShelterAnimal = 0) AS JuniorOtherLive,

(SELECT COUNT(*) FROM animal 
WHERE DeceasedDate >= {from} AND DeceasedDate <= {to}
AND NonShelterAnimal = 0 AND DiedOffShelter = 0 AND IsDOA = 0 
AND PutToSleep = 0 AND AsilomarOwnerRequestedEuthanasia = 0
AND SpeciesID IN ({specieslist})
AND DateOfBirth < {deceasedm5}) AS AdultDiedCare,

(SELECT COUNT(*) FROM animal 
WHERE DeceasedDate >= {from} AND DeceasedDate <= {to}
AND NonShelterAnimal = 0 AND DiedOffShelter = 0 AND IsDOA = 0 
AND PutToSleep = 0 AND AsilomarOwnerRequestedEuthanasia = 0
AND SpeciesID IN ({specieslist})
AND DateOfBirth >= {deceasedm5}) AS JuniorDiedCare,

(SELECT COUNT(*) FROM animal 
WHERE DeceasedDate >= {from} AND DeceasedDate <= {to}
AND NonShelterAnimal = 0 AND DiedOffShelter = 0
AND PutToSleep = 1 AND AsilomarOwnerRequestedEuthanasia = 0
AND SpeciesID IN ({specieslist})
AND DateOfBirth < {deceasedm5}) AS AdultEuthanasia,

(SELECT COUNT(*) FROM animal 
WHERE DeceasedDate >= {from} AND DeceasedDate <= {to}
AND NonShelterAnimal = 0 AND DiedOffShelter = 0
AND PutToSleep = 1 AND AsilomarOwnerRequestedEuthanasia = 0
AND SpeciesID IN ({specieslist})
AND DateOfBirth >= {deceasedm5}) AS JuniorEuthanasia,

(SELECT COUNT(*) FROM animal 
WHERE DeceasedDate >= {from} AND DeceasedDate <= {to}
AND NonShelterAnimal = 0 AND DiedOffShelter = 0
AND PutToSleep = 1 AND AsilomarOwnerRequestedEuthanasia = 1
AND SpeciesID IN ({specieslist})
AND DateOfBirth < {deceasedm5}) AS AdultOutReqEuth,

(SELECT COUNT(*) FROM animal 
WHERE DeceasedDate >= {from} AND DeceasedDate <= {to}
AND NonShelterAnimal = 0 AND DiedOffShelter = 0
AND PutToSleep = 1 AND AsilomarOwnerRequestedEuthanasia = 1
AND SpeciesID IN ({specieslist})
AND DateOfBirth >= {deceasedm5}) AS JuniorOutReqEuth
"""

