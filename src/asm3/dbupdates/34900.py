# ClinicTypeDescription was mispelled in the create code above (but not the update for existing databases) 
# as ClinicTypeDescripton - fix this.
if column_exists(dbo, "lkclinictype", "ClinicTypeDescripton"):
    add_column(dbo, "lkclinictype", "ClinicTypeDescription", dbo.type_longtext)
    drop_column(dbo, "lkclinictype", "ClinicTypeDescripton")
