# Add animalboarding.BoardingTypeID and table
l = dbo.locale
add_column(dbo, "animalboarding", "BoardingTypeID", dbo.type_integer)
add_index(dbo, "animalboarding_BoardingTypeID", "animalboarding", "BoardingTypeID")
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("BoardingName", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("BoardingDescription", dbo.type_shorttext, True),
    dbo.ddl_add_table_column("DefaultCost", dbo.type_integer, True),
    dbo.ddl_add_table_column("IsRetired", dbo.type_integer, True)
])
execute(dbo, dbo.ddl_add_table("lkboardingtype", fields) )
execute(dbo, "INSERT INTO lkboardingtype VALUES (1, ?, '', 0, 0)", [ _("Boarding", l) ])