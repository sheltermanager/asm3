add_column(dbo, "templatedocument", "ShowAt", dbo.type_shorttext)
execute(dbo,"UPDATE templatedocument SET ShowAt='everywhere'")