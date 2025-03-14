# AVG is a reserved keyword in some SQL dialects, change that field
try:
    if dbo.dbtype == "MYSQL":
        execute(dbo,"ALTER TABLE animalfigures CHANGE AVG AVERAGE %s NOT NULL" % dbo.type_float)
    elif dbo.dbtype == "POSTGRESQL":
        execute(dbo,"ALTER TABLE animalfigures RENAME COLUMN AVG TO AVERAGE")
    elif dbo.dbtype == "SQLITE":
        execute(dbo,"ALTER TABLE animalfigures ADD AVERAGE %s" % dbo.type_float)
except Exception as err:
    asm3.al.error("failed renaming AVG to AVERAGE: %s" % str(err), "dbupdate.update_3224", dbo)