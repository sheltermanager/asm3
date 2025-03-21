# Add animal.JurisdictionID
add_column(dbo, "animal", "JurisdictionID", dbo.type_integer)
add_index(dbo, "animal_JurisdictionID", "animal", "JurisdictionID")
# Set it on existing animals based on original owner, then brought in by jurisdiction
execute(dbo,"UPDATE animal SET JurisdictionID = " \
    "(SELECT JurisdictionID FROM owner WHERE ID = animal.OriginalOwnerID) WHERE JurisdictionID Is Null")
execute(dbo,"UPDATE animal SET JurisdictionID = " \
    "(SELECT JurisdictionID FROM owner WHERE ID = animal.BroughtInByOwnerID) WHERE JurisdictionID Is Null")
execute(dbo,"UPDATE animal SET JurisdictionID = 0 WHERE JurisdictionID Is Null")
