# Add extra fields to animal notes
add_column(dbo, "animal", "IsCrateTrained", dbo.type_integer)
add_column(dbo, "animal", "IsGoodWithElderly", dbo.type_integer)
add_column(dbo, "animal", "IsGoodTraveller", dbo.type_integer)
add_column(dbo, "animal", "IsGoodOnLead", dbo.type_integer)
add_column(dbo, "animal", "EnergyLevel", dbo.type_integer)
execute(dbo, "UPDATE animal SET IsCrateTrained=2, IsGoodWithElderly=2, IsGoodTraveller=2, IsGoodOnLead=2, EnergyLevel=0")