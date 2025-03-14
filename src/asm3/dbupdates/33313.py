# onlineformincoming.DisplayIndex should have been an integer,
# but the new db created it accidentally as a str in some
# databases - switch it to integer
modify_column(dbo, "onlineformincoming", "DisplayIndex", "INTEGER", "(DisplayIndex::integer)")