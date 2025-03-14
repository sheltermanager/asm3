# Add the customreportrole table
execute(dbo,"CREATE TABLE customreportrole (ReportID INTEGER NOT NULL, " \
    "RoleID INTEGER NOT NULL, CanView INTEGER NOT NULL)")
execute(dbo,"CREATE UNIQUE INDEX customreportrole_ReportIDRoleID ON customreportrole(ReportID, RoleID)")