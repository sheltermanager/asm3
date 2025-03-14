l = dbo.locale
# Move all rota types above shift up 2 places
execute(dbo,"UPDATE lksrotatype SET ID = ID + 10 WHERE ID > 1")
execute(dbo,"UPDATE ownerrota SET RotaTypeID = RotaTypeID + 10 WHERE RotaTypeID > 1")
# Insert two new types
execute(dbo,"INSERT INTO lksrotatype (ID, RotaType) VALUES (2, ?)",  [ _("Overtime", l) ])
execute(dbo,"INSERT INTO lksrotatype (ID, RotaType) VALUES (11, ?)", [ _("Public Holiday", l) ])