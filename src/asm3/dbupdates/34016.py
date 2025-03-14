l = dbo.locale
# Add JurisdictionID
add_column(dbo, "owner", "JurisdictionID", dbo.type_integer)
add_column(dbo, "animalcontrol", "JurisdictionID", dbo.type_integer)
add_index(dbo, "owner_JurisdictionID", "owner", "JurisdictionID")
add_index(dbo, "animalcontrol_JurisdictionID", "animalcontrol", "JurisdictionID")
sql = "CREATE TABLE jurisdiction ( ID INTEGER NOT NULL, " \
    "JurisdictionName %(short)s NOT NULL, " \
    "JurisdictionDescription %(long)s, " \
    "IsRetired INTEGER)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
execute(dbo,sql)
execute(dbo,"UPDATE owner SET JurisdictionID = 0")
execute(dbo,"UPDATE animalcontrol SET JurisdictionID = 0")
execute(dbo,"INSERT INTO jurisdiction VALUES (1, '%s', '', 0)" % _("Local", l))