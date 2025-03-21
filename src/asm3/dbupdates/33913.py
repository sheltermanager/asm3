# Add owner.OwnerCode
add_column(dbo, "owner", "OwnerCode", dbo.type_shorttext)
add_index(dbo, "owner_OwnerCode", "owner", "OwnerCode")
execute(dbo,"UPDATE owner SET OwnerCode = %s" % dbo.sql_concat([ dbo.sql_substring("UPPER(OwnerSurname)", 1, 2), dbo.sql_zero_pad_left("ID", 6) ]))