l = dbo.locale
# Lookup tables
sql = "CREATE TABLE citationtype (ID INTEGER NOT NULL PRIMARY KEY, " \
    "CitationName %s NOT NULL, CitationDescription %s, DefaultCost INTEGER)" % (dbo.type_shorttext, dbo.type_longtext)
execute(dbo,sql)
sql = "CREATE TABLE incidenttype (ID INTEGER NOT NULL PRIMARY KEY, " \
    "IncidentName %s NOT NULL, IncidentDescription %s)" % (dbo.type_shorttext, dbo.type_longtext)
execute(dbo,sql)
sql = "CREATE TABLE incidentcompleted (ID INTEGER NOT NULL PRIMARY KEY, " \
    "CompletedName %s NOT NULL, CompletedDescription %s)" % (dbo.type_shorttext, dbo.type_longtext)
execute(dbo,sql)
# Default lookup data
execute(dbo,"INSERT INTO citationtype VALUES (1, '%s', '', 0)" % _("First offence", l))
execute(dbo,"INSERT INTO citationtype VALUES (2, '%s', '', 0)" % _("Second offence", l))
execute(dbo,"INSERT INTO citationtype VALUES (3, '%s', '', 0)" % _("Third offence", l))
execute(dbo,"INSERT INTO incidenttype VALUES (1, '%s', '')" % _("Aggression", l))
execute(dbo,"INSERT INTO incidenttype VALUES (2, '%s', '')" % _("Animal defecation", l))
execute(dbo,"INSERT INTO incidenttype VALUES (3, '%s', '')" % _("Animals at large", l))
execute(dbo,"INSERT INTO incidenttype VALUES (4, '%s', '')" % _("Animals left in vehicle", l))
execute(dbo,"INSERT INTO incidenttype VALUES (5, '%s', '')" % _("Bite", l))
execute(dbo,"INSERT INTO incidenttype VALUES (6, '%s', '')" % _("Dead animal", l))
execute(dbo,"INSERT INTO incidenttype VALUES (7, '%s', '')" % _("Neglect", l))
execute(dbo,"INSERT INTO incidenttype VALUES (8, '%s', '')" % _("Noise", l))
execute(dbo,"INSERT INTO incidenttype VALUES (9, '%s', '')" % _("Number of pets", l))
execute(dbo,"INSERT INTO incidenttype VALUES (10, '%s', '')" % _("Sick/injured animal", l))
execute(dbo,"INSERT INTO incidentcompleted VALUES (1, '%s', '')" % _("Animal destroyed", l))
execute(dbo,"INSERT INTO incidentcompleted VALUES (2, '%s', '')" % _("Animal picked up", l))
execute(dbo,"INSERT INTO incidentcompleted VALUES (3, '%s', '')" % _("Owner given citation", l))