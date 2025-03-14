# add lkworktype.IsRetired
add_column(dbo, "lkworktype", "IsRetired", dbo.type_integer)
execute(dbo,"UPDATE lkworktype SET IsRetired = 0")