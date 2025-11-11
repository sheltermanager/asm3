from asm3.dbupdate import execute, add_index

fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("StartDatetime", dbo.type_datetime, False),
    dbo.ddl_add_table_column("EndDatetime", dbo.type_integer, True),
    dbo.ddl_add_table_column("AnimalID", dbo.type_integer, False),
    dbo.ddl_add_table_column("ConditionID", dbo.type_integer, False),
    dbo.ddl_add_table_column("Comments", dbo.type_longtext, False)
]) + dbo.ddl_audit_table_columns()
execute(dbo, dbo.ddl_add_table("animalcondition", fields) )

add_index(dbo, "animalcondition_ConditionID", "animalcondition", "ConditionID")

fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("ConditionTypeID", dbo.type_integer, False),
    dbo.ddl_add_table_column("IsZoonotic", dbo.type_integer, True),
    dbo.ddl_add_table_column("ConditionName", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("Description", dbo.type_longtext, False),
    dbo.ddl_add_table_column("IsRetired", dbo.type_integer, True)
])
execute(dbo, dbo.ddl_add_table("lkcondition", fields) )

add_index(dbo, "lkcondition_ConditionTypeID", "lkcondition", "ConditionTypeID")

fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("ConditionTypeName", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("Description", dbo.type_longtext, False),
    dbo.ddl_add_table_column("IsRetired", dbo.type_integer, True)
])
execute(dbo, dbo.ddl_add_table("lksconditiontype", fields) )

for conditiontype in (
    _("GI"),
    _("Respiratory"),
    _("Miscellaneous"),
    _("Reproductive"),
    _("Symptom")
):
    dbo.execute("INSERT INTO lksconditiontype (ConditionTypeName, Description, IsRetired) VALUES (?, ?, ?)", [conditiontype, "", 0] )
