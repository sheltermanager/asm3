# Add clinic tables
l = dbo.locale
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("AnimalID", dbo.type_integer, False),
    dbo.ddl_add_table_column("OwnerID", dbo.type_integer, False),
    dbo.ddl_add_table_column("ApptFor", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("DateTime", dbo.type_datetime, False),
    dbo.ddl_add_table_column("Status", dbo.type_integer, False),
    dbo.ddl_add_table_column("ArrivedDateTime", dbo.type_datetime, True),
    dbo.ddl_add_table_column("WithVetDateTime", dbo.type_datetime, True),
    dbo.ddl_add_table_column("CompletedDateTime", dbo.type_datetime, True),
    dbo.ddl_add_table_column("ReasonForAppointment", dbo.type_longtext, True),
    dbo.ddl_add_table_column("Comments", dbo.type_longtext, True),
    dbo.ddl_add_table_column("Amount", dbo.type_integer, False),
    dbo.ddl_add_table_column("IsVAT", dbo.type_integer, False),
    dbo.ddl_add_table_column("VATRate", dbo.type_float, False),
    dbo.ddl_add_table_column("VATAmount", dbo.type_integer, False),
    dbo.ddl_add_table_column("RecordVersion", dbo.type_integer, True),
    dbo.ddl_add_table_column("CreatedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("CreatedDate", dbo.type_datetime, False),
    dbo.ddl_add_table_column("LastChangedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("LastChangedDate", dbo.type_datetime, False)
])
execute(dbo, dbo.ddl_add_table("clinicappointment", fields) )
execute(dbo, dbo.ddl_add_index("clinicappointment_AnimalID", "clinicappointment", "AnimalID") )
execute(dbo, dbo.ddl_add_index("clinicappointment_OwnerID", "clinicappointment", "OwnerID") )
execute(dbo, dbo.ddl_add_index("clinicappointment_ApptFor", "clinicappointment", "ApptFor") )
execute(dbo, dbo.ddl_add_index("clinicappointment_Status", "clinicappointment", "Status") )
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("ClinicAppointmentID", dbo.type_integer, False),
    dbo.ddl_add_table_column("Description", dbo.type_longtext, False),
    dbo.ddl_add_table_column("Amount", dbo.type_integer, False),
    dbo.ddl_add_table_column("RecordVersion", dbo.type_integer, True),
    dbo.ddl_add_table_column("CreatedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("CreatedDate", dbo.type_datetime, False),
    dbo.ddl_add_table_column("LastChangedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("LastChangedDate", dbo.type_datetime, False)
])
execute(dbo, dbo.ddl_add_table("clinicinvoiceitem", fields) )
execute(dbo, dbo.ddl_add_index("clinicinvoiceitem_ClinicAppointmentID", "clinicinvoiceitem", "ClinicAppointmentID") )
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("Status", dbo.type_shorttext, False)
])
execute(dbo, dbo.ddl_add_table("lksclinicstatus", fields) )
dbo.insert("lksclinicstatus", { "ID": 0, "Status": _("Scheduled", l) }, setOverrideDBLock=True, generateID=False)
dbo.insert("lksclinicstatus", { "ID": 1, "Status": _("Invoice Only", l) }, setOverrideDBLock=True, generateID=False)
dbo.insert("lksclinicstatus", { "ID": 2, "Status": _("Not Arrived", l) }, setOverrideDBLock=True, generateID=False)
dbo.insert("lksclinicstatus", { "ID": 3, "Status": _("Waiting", l) }, setOverrideDBLock=True, generateID=False)
dbo.insert("lksclinicstatus", { "ID": 4, "Status": _("With Vet", l) }, setOverrideDBLock=True, generateID=False)
dbo.insert("lksclinicstatus", { "ID": 5, "Status": _("Complete", l) }, setOverrideDBLock=True, generateID=False)
dbo.insert("lksclinicstatus", { "ID": 6, "Status": _("Cancelled", l) }, setOverrideDBLock=True, generateID=False)