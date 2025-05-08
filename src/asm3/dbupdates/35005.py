from asm3.dbupdate import execute, add_column

# Restore citation linktype if it has been removed
if dbo.query_int("SELECT COUNT(*) FROM lksfieldlink WHERE ID=19") == 0:
    execute(dbo, "INSERT INTO lksfieldlink (ID, LinkType) VALUES (?, ?)", [ 19, _("Incident - Citation", dbo.locale) ])

