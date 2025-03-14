# Add owner.IsAdopter flag
add_column(dbo, "owner", "IsAdopter", dbo.type_integer)
add_index(dbo, "owner_IsAdopter", "owner", "IsAdopter")
execute(dbo,"UPDATE owner SET IsAdopter = (SELECT COUNT(*) FROM adoption WHERE OwnerID = owner.ID AND MovementType=1 AND MovementDate Is Not Null AND ReturnDate Is Null)")
execute(dbo,"UPDATE owner SET IsAdopter = 1 WHERE IsAdopter > 0")
