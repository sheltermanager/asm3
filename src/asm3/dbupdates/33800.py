# Add IsRetired field to lookups
retirablelookups = [ "animaltype", "basecolour", "breed", "citationtype", "costtype", 
    "deathreason", "diet", "donationpayment", "donationtype", "entryreason", "incidentcompleted", 
    "incidenttype", "internallocation", "licencetype", "logtype", "pickuplocation", 
    "reservationstatus", "species", "stocklocation", "stockusagetype", "testtype", 
    "testresult", "traptype", "vaccinationtype", "voucher" ]
for t in retirablelookups:
    add_column(dbo, t, "IsRetired", "INTEGER")
    execute(dbo,"UPDATE %s SET IsRetired = 0" % t)