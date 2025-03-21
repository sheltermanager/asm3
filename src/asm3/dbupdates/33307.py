# Add licencetype lookup
l = dbo.locale
sql = "CREATE TABLE licencetype (ID INTEGER NOT NULL PRIMARY KEY, " \
    "LicenceTypeName %s NOT NULL, LicenceTypeDescription %s, DefaultCost INTEGER)" % (dbo.type_shorttext, dbo.type_longtext)
execute(dbo,sql)
execute(dbo,"INSERT INTO licencetype VALUES (1, '%s', '', 0)" % _("Altered Dog - 1 year", l))
execute(dbo,"INSERT INTO licencetype VALUES (2, '%s', '', 0)" % _("Unaltered Dog - 1 year", l))
execute(dbo,"INSERT INTO licencetype VALUES (3, '%s', '', 0)" % _("Altered Dog - 3 year", l))
execute(dbo,"INSERT INTO licencetype VALUES (4, '%s', '', 0)" % _("Unaltered Dog - 3 year", l))