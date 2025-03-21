# Add templatedocument table and copy templates from DBFS
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("Name", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("Path", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("Content", dbo.type_longtext, False) ])
execute(dbo, dbo.ddl_add_table("templatedocument", fields) )
execute(dbo, dbo.ddl_add_index("templatedocument_NamePath", "templatedocument", "Name,Path", True) )
# Copy document templates from DBFS - we track ID manually as the sequence won't be created yet
nextid = 1
for row in dbo.query("SELECT ID, Name, Path FROM dbfs WHERE Path Like '/templates%' AND (Name LIKE '%.html' OR Name LIKE '%.odt') ORDER BY Name"):
    content = asm3.dbfs.get_string_id(dbo, row.id)
    dbo.insert("templatedocument", {
        "ID":       nextid,
        "Name":     row.name,
        "Path":     row.path,
        "Content":  asm3.utils.base64encode(content)
    }, generateID=False, setOverrideDBLock=True)
    nextid += 1