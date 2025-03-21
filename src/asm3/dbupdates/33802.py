# Remove the Incident - Citation link from additional fields as it's no longer valid
execute(dbo,"DELETE FROM lksfieldlink WHERE ID = 19")