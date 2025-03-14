# If the user has no online forms, install the default set
if 0 == dbo.query_int("SELECT COUNT(*) FROM onlineform"):
    install_default_onlineforms(dbo)