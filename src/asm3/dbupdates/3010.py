# Create person flags table
sql = "CREATE TABLE lkownerflags ( ID INTEGER NOT NULL, " \
    "Flag %s NOT NULL)" % dbo.type_shorttext
execute(dbo,sql)
# Add additionalflags field to person
add_column(dbo, "owner", "AdditionalFlags", dbo.type_longtext)
# Populate it with existing flags
execute(dbo,"UPDATE owner SET AdditionalFlags = ''")
flags = ( 
    ("IDCheck", "homechecked"), 
    ("IsBanned", "banned"),
    ("IsVolunteer", "volunteer"),
    ("IsMember", "member"),
    ("IsHomeChecker", "homechecker"),
    ("IsDonor", "donor"),
    ("IsShelter", "shelter"),
    ("IsACO", "aco"), 
    ("IsStaff", "staff"), 
    ("IsFosterer", "fosterer"), 
    ("IsRetailer", "retailer"), 
    ("IsVet", "vet"), 
    ("IsGiftAid", "giftaid")
)
for field, flag in flags:
    concat = dbo.sql_concat(["AdditionalFlags", "'%s|'" % flag])
    execute(dbo,"UPDATE owner SET AdditionalFlags=%s WHERE %s=1" % (concat, field) )