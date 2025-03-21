# PostgreSQL databases have been using VARCHAR(16384) as longtext when
# they really shouldn't. Let's switch those fields to be TEXT instead.
if dbo.dbtype == "POSTGRESQL": 
    fields = [ "activeuser.Messages", "additionalfield.LookupValues", "additional.Value", "adoption.ReasonForReturn", 
        "adoption.Comments", "animal.Markings", "animal.HiddenAnimalDetails", "animal.AnimalComments", "animal.ReasonForEntry", 
        "animal.ReasonNO", "animal.HealthProblems", "animal.PTSReason", "animalcost.Description", "animal.AnimalComments", 
        "animalfound.DistFeat", "animalfound.Comments", "animallitter.Comments", "animallost.DistFeat", "animallost.Comments", 
        "animalmedical.Comments", "animalmedicaltreatment.Comments", "animalvaccination.Comments", "animalwaitinglist.ReasonForWantingToPart", 
        "animalwaitinglist.ReasonForRemoval", "animalwaitinglist.Comments", "audittrail.Description", "customreport.Description", 
        "diary.Subject", "diary.Note", "diarytaskdetail.Subject", "diarytaskdetail.Note", "log.Comments", "media.MediaNotes", 
        "medicalprofile.Comments", "messages.Message", "owner.Comments", "owner.AdditionalFlags", "owner.HomeCheckAreas", 
        "ownerdonation.Comments", "ownerinvestigation.Notes", "ownervoucher.Comments", "role.SecurityMap", "users.SecurityMap", 
        "users.IPRestriction", "configuration.ItemValue", "customreport.SQLCommand", "customreport.HTMLBody" ]
    for f in fields:
        table, field = f.split(".")
        try:
            execute(dbo,"ALTER TABLE %s ALTER %s TYPE %s" % (table, field, dbo.type_longtext))
        except Exception as err:
            asm3.al.error("failed switching to TEXT %s: %s" % (f, str(err)), "dbupdate.update_3223", dbo)