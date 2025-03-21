# Create initial data for testtype and testresult tables
if dbo.query_int("SELECT COUNT(*) FROM testtype") == 0: 
    l = dbo.locale
    execute(dbo,"INSERT INTO testresult (ID, ResultName) VALUES (1, '" + _("Unknown", l) + "')")
    execute(dbo,"INSERT INTO testresult (ID, ResultName) VALUES (2, '" + _("Negative", l) + "')")
    execute(dbo,"INSERT INTO testresult (ID, ResultName) VALUES (3, '" + _("Positive", l) + "')")
    execute(dbo,"INSERT INTO testtype (ID, TestName, DefaultCost) VALUES (1, '" + _("FIV", l) + "', 0)")
    execute(dbo,"INSERT INTO testtype (ID, TestName, DefaultCost) VALUES (2, '" + _("FLV", l) + "', 0)")
    execute(dbo,"INSERT INTO testtype (ID, TestName, DefaultCost) VALUES (3, '" + _("Heartworm", l) + "', 0)")