# Remove recordversion and created/lastchanged columns from role tables - should never have been there
# and has been erroneously added to these tables for new databases (nullable change is the serious cause)
for t in ( "accountsrole", "animalcontrolrole", "customreportrole" ):
    try:
        execute(dbo, dbo.ddl_drop_column(t, "CreatedBy") )
        execute(dbo, dbo.ddl_drop_column(t, "CreatedDate") )
        execute(dbo, dbo.ddl_drop_column(t, "LastChangedDate") )
        execute(dbo, dbo.ddl_drop_column(t, "LastChangedBy") )
        execute(dbo, dbo.ddl_drop_column(t, "RecordVersion") )
    except:
        pass