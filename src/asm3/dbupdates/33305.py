# Add traptype lookup
l = dbo.locale
sql = "CREATE TABLE traptype (ID INTEGER NOT NULL PRIMARY KEY, " \
    "TrapTypeName %s NOT NULL, TrapTypeDescription %s, DefaultCost INTEGER)" % (dbo.type_shorttext, dbo.type_longtext)
execute(dbo,sql)
execute(dbo,"INSERT INTO traptype VALUES (1, '%s', '', 0)" % _("Cat", l))