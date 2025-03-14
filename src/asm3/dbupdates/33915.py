# Add the animalcontrolrole table
execute(dbo,"CREATE TABLE animalcontrolrole (AnimalControlID INTEGER NOT NULL, " \
    "RoleID INTEGER NOT NULL, CanView INTEGER NOT NULL, CanEdit INTEGER NOT NULL)")
execute(dbo,"CREATE UNIQUE INDEX animalcontrolrole_AnimalControlIDRoleID ON animalcontrolrole(AnimalControlID, RoleID)")