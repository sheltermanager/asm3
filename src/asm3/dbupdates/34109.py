# Remove recordversion and created/lastchanged columns from ownerlookingfor - should never have been there
# and has been erroneously added to these tables for new databases (nullable change is the serious cause)
tables = [ "ownerlookingfor" ]
cols = [ "CreatedBy", "CreatedDate", "LastChangedBy", "LastChangedDate", "RecordVersion" ]
for t in tables:
    for c in cols:
        if column_exists(dbo, t, c): drop_column(dbo, t, c)
