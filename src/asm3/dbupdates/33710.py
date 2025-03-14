# Turn off forcereupload as it should no longer be needed
p = dbo.query_string("SELECT ItemValue FROM configuration WHERE ItemName LIKE 'PublisherPresets'")
s = []
for x in p.split(" "):
    if x != "forcereupload": s.append(x)
execute(dbo,"UPDATE configuration SET ItemValue = '%s' WHERE ItemName LIKE 'PublisherPresets'" % " ".join(s))
