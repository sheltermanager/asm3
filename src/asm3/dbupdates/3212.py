# Many of our lookup fields are too short for foreign languages
fields = [ "animaltype.AnimalType", "animaltype.AnimalDescription", "basecolour.BaseColour", "basecolour.BaseColourDescription",
    "breed.BreedName", "breed.BreedDescription", "lkcoattype.CoatType", "costtype.CostTypeName", "costtype.CostTypeDescription",
    "deathreason.ReasonName", "deathreason.ReasonDescription", "diet.DietName", "diet.DietDescription", 
    "donationtype.DonationName", "donationtype.DonationDescription", "entryreason.ReasonName", "entryreason.ReasonDescription",
    "internallocation.LocationName", "internallocation.LocationDescription", "logtype.LogTypeName", "logtype.LogTypeDescription",
    "lksmovementtype.MovementType",  "lkownerflags.Flag", "lksex.Sex", "lksize.Size", "lksyesno.Name", "lksynun.Name", 
    "lksposneg.Name", "species.SpeciesName", "species.SpeciesDescription", "lkurgency.Urgency", 
    "vaccinationtype.VaccinationType", "vaccinationtype.VaccinationDescription", "voucher.VoucherName", "voucher.VoucherDescription",
    "accounts.Code", "accounts.Description", "accountstrx.Description",
    "animal.TimeOnShelter", "animal.AnimalAge", "animalfigures.Heading", "animalfiguresannual.Heading", 
    "animalfiguresannual.GroupHeading", "animalwaitinglist.AnimalDescription",
    "animalmedical.TreatmentName", "animalmedical.Dosage", "diary.Subject", "diary.LinkInfo",
    "medicalprofile.TreatmentName", "medicalprofile.Dosage", "medicalprofile.ProfileName" ]
for f in fields:
    table, field = f.split(".")
    try:
        modify_column(dbo, table, field, dbo.type_shorttext)
    except Exception as err:
        asm3.al.error("failed extending %s: %s" % (f, str(err)), "dbupdate.update_3212", dbo)