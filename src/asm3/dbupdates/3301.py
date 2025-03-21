# Add the accountsrole table
execute(dbo,"CREATE TABLE accountsrole (AccountID INTEGER NOT NULL, " \
    "RoleID INTEGER NOT NULL, CanView INTEGER NOT NULL, CanEdit INTEGER NOT NULL)")
execute(dbo,"CREATE UNIQUE INDEX accountsrole_AccountIDRoleID ON accountsrole(AccountID, RoleID)")
