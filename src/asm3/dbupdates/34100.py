# Add templatehtml table
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("Name", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("Header", dbo.type_longtext, False),
    dbo.ddl_add_table_column("Body", dbo.type_longtext, True),
    dbo.ddl_add_table_column("Footer", dbo.type_longtext, True),
    dbo.ddl_add_table_column("IsBuiltIn", dbo.type_integer, False) ])
execute(dbo, dbo.ddl_add_table("templatehtml", fields) )
execute(dbo, dbo.ddl_add_index("templatehtml_Name", "templatehtml", "Name", True) )
# Copy HTML templates from DBFS - we track ID manually as the sequence won't be created yet
nextid = 1
for row in dbo.query("SELECT Name, Path FROM dbfs WHERE Path Like '/internet' AND Name NOT LIKE '%.%' ORDER BY Name"):
    head = asm3.dbfs.get_string(dbo, "head.html", "/internet/%s" % row.name)
    foot = asm3.dbfs.get_string(dbo, "foot.html", "/internet/%s" % row.name)
    body = asm3.dbfs.get_string(dbo, "body.html", "/internet/%s" % row.name)
    dbo.insert("templatehtml", {
        "ID":       nextid,
        "Name":     row.name,
        "*Header":  asm3.utils.bytes2str(head),
        "*Body":    asm3.utils.bytes2str(body),
        "*Footer":  asm3.utils.bytes2str(foot),
        "IsBuiltIn":  0
    }, generateID=False, setOverrideDBLock=True)
    nextid += 1
# Copy fixed templates for report header/footer and online form header/footer
if asm3.dbfs.file_exists(dbo, "head.html", "/reports") and asm3.dbfs.file_exists(dbo, "foot.html"):
    reporthead = asm3.dbfs.get_string(dbo, "head.html", "/reports")
    reportfoot = asm3.dbfs.get_string(dbo, "foot.html", "/reports")
    if reporthead != "":
        dbo.insert("templatehtml", {
            "ID":       nextid,
            "Name":     "report",
            "*Header":  asm3.utils.bytes2str(reporthead),
            "*Body":    "",
            "*Footer":  asm3.utils.bytes2str(reportfoot),
            "IsBuiltIn":  1
        }, generateID=False, setOverrideDBLock=True)
        nextid += 1
if asm3.dbfs.file_exists(dbo, "head.html", "/onlineform") and asm3.dbfs.file_exists(dbo, "foot.html", "/onlineform"):
    ofhead = asm3.dbfs.get_string(dbo, "head.html", "/onlineform")
    offoot = asm3.dbfs.get_string(dbo, "foot.html", "/onlineform")
    if ofhead != "":
        dbo.insert("templatehtml", {
            "ID":       nextid,
            "Name":     "onlineform",
            "*Header":  asm3.utils.bytes2str(ofhead),
            "*Body":    "",
            "*Footer":  asm3.utils.bytes2str(offoot),
            "IsBuiltIn":  1
        }, generateID=False, setOverrideDBLock=True)
