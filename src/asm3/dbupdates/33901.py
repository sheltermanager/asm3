# Add audittrail.LinkID field
add_column(dbo, "audittrail", "LinkID", "INTEGER")
add_index(dbo, "audittrail_LinkID", "audittrail", "LinkID")
execute(dbo,"UPDATE audittrail SET LinkID = 0")