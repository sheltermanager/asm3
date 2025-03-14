l = dbo.locale
# Add clinictype table and field to clinicappointment
add_column(dbo, "clinicappointment", "ClinicTypeID", dbo.type_integer)
add_index(dbo, "clinicappointment_ClinicTypeID", "clinicappointment", "ClinicTypeID")
dbo.execute_dbupdate("UPDATE clinicappointment SET ClinicTypeID=1")
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("ClinicTypeName", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("ClinicTypeDescription", dbo.type_shorttext, True),
    dbo.ddl_add_table_column("IsRetired", dbo.type_integer, True)
])
execute(dbo, dbo.ddl_add_table("lkclinictype", fields) )
execute(dbo,"INSERT INTO lkclinictype VALUES (1, ?, '', 0)", [ _("Consultation", l) ])
execute(dbo,"INSERT INTO lkclinictype VALUES (2, ?, '', 0)", [ _("Followup", l) ])
execute(dbo,"INSERT INTO lkclinictype VALUES (3, ?, '', 0)", [ _("Prescription", l) ])
execute(dbo,"INSERT INTO lkclinictype VALUES (4, ?, '', 0)", [ _("Surgery", l) ])