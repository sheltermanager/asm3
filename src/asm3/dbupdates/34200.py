# Add audittrail.ParentLinks
add_column(dbo, "audittrail", "ParentLinks", dbo.type_shorttext)
add_index(dbo, "audittrail_ParentLinks", "audittrail", "ParentLinks")