# Install new incident information template
path = dbo.installpath
asm2_dbfs_put_file(dbo, "incident_information.html", "/templates", path + "media/templates/incident_information.html")