# Add the default animalview template
path = dbo.installpath
asm2_dbfs_put_file(dbo, "body.html", "/internet/animalview", path + "media/internet/animalview/body.html")
asm2_dbfs_put_file(dbo, "foot.html", "/internet/animalview", path + "media/internet/animalview/foot.html")
asm2_dbfs_put_file(dbo, "head.html", "/internet/animalview", path + "media/internet/animalview/head.html")
