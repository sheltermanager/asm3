from asm3.dbupdate import add_column, execute

add_column(dbo, "owner", "MatchDeclawed", dbo.type_integer)
execute(dbo, "UPDATE owner SET MatchDeclawed = -1")