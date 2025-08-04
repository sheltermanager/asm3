# Create initial data for testtype and testresult tables
if dbo.query_int("SELECT COUNT(*) FROM testtype") == 0: 
    l = dbo.locale
    execute(dbo,"INSERT INTO testresult (ID, ResultName) VALUES (1, ?)", [ _("Unknown", l) ])
    execute(dbo,"INSERT INTO testresult (ID, ResultName) VALUES (2, ?)", [ _("Negative", l) ])
    execute(dbo,"INSERT INTO testresult (ID, ResultName) VALUES (3, ?)", [ _("Positive", l) ])
    execute(dbo,"INSERT INTO testtype (ID, TestName, DefaultCost) VALUES (1, ?, 0)", [ _("FIV", l) ])
    execute(dbo,"INSERT INTO testtype (ID, TestName, DefaultCost) VALUES (2, ?, 0)", [ _("FLV", l) ])
    execute(dbo,"INSERT INTO testtype (ID, TestName, DefaultCost) VALUES (3, ?, 0)", [ _("Heartworm", l) ])
