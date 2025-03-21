# change column eventownerid to nullable
execute(dbo,dbo.ddl_drop_notnull("event", "EventOwnerID", dbo.type_integer))