# Add facility for users to override the system locale
add_column(dbo, "users", "LocaleOverride", dbo.type_shorttext)