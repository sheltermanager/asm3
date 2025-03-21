# Add online form tables
sql = "CREATE TABLE onlineform (ID INTEGER NOT NULL PRIMARY KEY, " \
    "Name %(short)s NOT NULL, " \
    "RedirectUrlAfterPOST %(short)s, " \
    "SetOwnerFlags %(short)s, " \
    "Description %(long)s )" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
execute(dbo,sql)
add_index(dbo, "onlineform_Name", "onlineform", "Name")
sql = "CREATE TABLE onlineformfield(ID INTEGER NOT NULL PRIMARY KEY, " \
    "OnlineFormID INTEGER NOT NULL, " \
    "FieldName %(short)s NOT NULL, " \
    "FieldType INTEGER NOT NULL, " \
    "Label %(short)s NOT NULL, " \
    "Lookups %(long)s, " \
    "Tooltip %(long)s )" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
execute(dbo,sql)
add_index(dbo, "onlineformfield_OnlineFormID", "onlineformfield", "OnlineFormID")
sql = "CREATE TABLE onlineformincoming(CollationID INTEGER NOT NULL, " \
    "FormName %(short)s NOT NULL, " \
    "PostedDate %(date)s NOT NULL, " \
    "Flags %(short)s, " \
    "FieldName %(short)s NOT NULL, " \
    "Value %(long)s )" % { "date": dbo.type_datetime, "short": dbo.type_shorttext, "long": dbo.type_longtext }
execute(dbo,sql)
add_index(dbo, "onlineformincoming_CollationID", "onlineformincoming", "CollationID")