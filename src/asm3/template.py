
import asm3.audit
import asm3.configuration
import asm3.utils
from asm3.typehints import Database, List, Results, Tuple

def get_html_template(dbo: Database, name: str) -> Tuple[str, str, str]:
    """ Returns a tuple of the header, body and footer values for template name """
    rows = dbo.query("SELECT * FROM templatehtml WHERE Name = ?", [name])
    if len(rows) == 0:
        return ("", "", "")
    else:
        return (rows[0].header, rows[0].body, rows[0].footer)
    
def get_html_template_from_file(dbo: Database, name: str) -> Tuple[str, str, str]:
    """ Reads one of our default html publishing templates from the file system """
    head = asm3.utils.read_text_file(dbo.installpath + "media/internet/%s/head.html" % name)
    foot = asm3.utils.read_text_file(dbo.installpath + "media/internet/%s/foot.html" % name)
    body = asm3.utils.read_text_file(dbo.installpath + "media/internet/%s/body.html" % name)
    return ( head, body, foot)

def get_html_templates(dbo: Database) -> Results:
    """ Returns all available HTML publishing templates (excluding built ins) """
    return dbo.query("SELECT * FROM templatehtml WHERE IsBuiltIn = 0 ORDER BY Name")

def get_html_template_names(dbo: Database) -> List[str]:
    l = []
    for r in dbo.query("SELECT Name FROM templatehtml WHERE IsBuiltIn = 0 ORDER BY Name"):
        l.append(r.name)
    return l

def update_html_template(dbo: Database, username: str, name: str, head: str, body: str, foot: str, builtin: bool = False) -> None:
    """ Creates/updates an HTML publishing template """
    dbo.execute("DELETE FROM templatehtml WHERE Name = ?", [name])
    htid = dbo.insert("templatehtml", {
        "Name":     name,
        "*Header":  head,
        "*Body":    body,
        "*Footer":  foot,
        "IsBuiltIn": builtin and 1 or 0
    })
    asm3.audit.create(dbo, username, "templatehtml", htid, "", "id: %d, name: %s" % (htid, name))

def delete_html_template(dbo: Database, username: str, name: str) -> None:
    """ Get an html template by name """
    dbo.execute("DELETE FROM templatehtml WHERE Name = ?", [name])
    asm3.audit.delete(dbo, username, "templatehtml", 0, "", "delete template %s" % name)

def get_document_templates(dbo: Database, show: str = "") -> Results:
    """ Returns document template info. """
    allowodt = asm3.configuration.allow_odt_document_templates(dbo)
    rows = dbo.query(f"SELECT ID, Name, Path, ShowAt, {dbo.sql_char_length('Content')} AS Size FROM templatedocument ORDER BY Path, Name")
    out = []
    for r in rows:
        if not allowodt and r.NAME.endswith(".odt"): continue
        if show != "" and asm3.utils.nulltostr(r.SHOWAT).find(show) == -1 and r.SHOWAT != "everywhere": continue
        out.append(r)
    return out

def get_document_templates_defaults(dbo: Database, hide_installed: bool = True) -> List[str]:
    """ Returns a list of default document templates for installation """
    installed = [ x.NAME for x in get_document_templates(dbo) ]
    t = []
    for name in asm3.utils.listdir(f"{dbo.installpath}media/templates"):
        if not name.endswith(".html"): continue
        if name in installed and hide_installed: continue
        t.append(name)
    return sorted(t)

def get_document_template_content(dbo: Database, dtid: int) -> bytes:
    """ Returns the document template content for a given ID as bytes """
    return asm3.utils.base64decode( dbo.query_string("SELECT Content FROM templatedocument WHERE ID = ?", [dtid]) )

def get_document_template_name(dbo: Database, dtid: int) -> str:
    """ Returns the name for a document template with an ID """
    return dbo.query_string("SELECT Name FROM templatedocument WHERE ID = ?", [dtid])

def get_document_template_show(dbo: Database, dtid: int) -> str:
    """ Returns the type for a document template with an ID """
    return dbo.query_string("SELECT ShowAt FROM templatedocument WHERE ID = ?", [dtid])

def create_document_template(dbo: Database, username: str, name: str, ext: str = ".html", content: bytes = b"<p></p>", show: str = "") -> int:
    """
    Creates a document template from the name given.
    If there's no extension, adds it
    If it's a relative path (doesn't start with /) adds /templates/ to the front
    If it's an absolute path that doesn't start with /templates/, add /templates
    Changes spaces and unwanted punctuation to underscores
    """
    filepath = name
    if not filepath.endswith(ext): filepath += ext
    if not filepath.startswith("/"): filepath = "/templates/" + filepath
    if not filepath.startswith("/templates"): filepath = "/templates" + filepath
    filepath = sanitise_path(filepath)
    name = filepath[filepath.rfind("/")+1:]
    path = filepath[:filepath.rfind("/")]

    if 0 != dbo.query_int("SELECT COUNT(*) FROM templatedocument WHERE Name = ? AND Path = ?", (name, path)):
        raise asm3.utils.ASMValidationError("%s already exists" % filepath)

    dtid = dbo.insert("templatedocument", {
        "Name":     name,
        "Path":     path,
        "ShowAt":   show,
        "Content":  asm3.utils.bytes2str(asm3.utils.base64encode(content))
    })
    asm3.audit.create(dbo, username, "templatedocument", dtid, "", "id: %d, name: %s" % (dtid, name))
    return dtid

def clone_document_template(dbo: Database, username: str, dtid: int, newname: str) -> int:
    """
    Creates a new document template with the content from the id given.
    """
    # Get the extension/type from newname, defaulting to html
    ext = ".html"
    if newname.rfind(".") != -1:
        ext = newname[newname.rfind("."):]
    content = get_document_template_content(dbo, dtid)
    show = get_document_template_show(dbo, dtid)
    ndtid = create_document_template(dbo, username, newname, ext, content, show)
    return ndtid

def delete_document_template(dbo: Database, username: str, dtid: int) -> None:
    """
    Deletes a document template
    """
    name = get_document_template_name(dbo, dtid)
    dbo.delete("templatedocument", dtid, username, writeAudit=False)
    asm3.audit.delete(dbo, username, "templatedocument", dtid, "", "delete template %d (%s)" % (dtid, name))

def rename_document_template(dbo: Database, username: str, dtid: int, newname: str) -> None:
    """
    Renames a document template.
    If there is a path component (starts with forward slash)
    then the path is extracted and updated first.
    """
    path = ""
    name = newname
    if name.startswith("/"):
        path = name[0:newname.rfind("/")+1]
        name = name[newname.rfind("/")+1:]
    if not name.endswith(".html") and not name.endswith(".odt"): name += ".html"
    d = { "Name": name }
    if path != "": d["Path"] = path
    oldname = get_document_template_name(dbo, dtid)
    dbo.update("templatedocument", dtid, d)
    asm3.audit.edit(dbo, username, "templatedocument", dtid, "", "rename %d, %s ==> %s" % (dtid, oldname, newname))

def update_document_template_content(dbo: Database, username: str, dtid: int, content: bytes) -> None:
    """ Changes the content of a template """
    row = dbo.first_row(dbo.query("SELECT * FROM templatedocument WHERE ID = ?", (dtid,)))
    sql = dbo.row_to_update_sql("templatedocument", row)

    dbo.update("templatedocument", dtid, {
        "Content":  asm3.utils.bytes2str(asm3.utils.base64encode(content))
    })
    name = get_document_template_name(dbo, dtid)

    asm3.audit.insert_deletion(dbo, username, "templatedocument", dtid, "", sql)
    asm3.audit.edit(dbo, username, "templatedocument", dtid, "", "changed content of template %s (%s)" % (dtid, name))

def update_document_template_show(dbo: Database, username: str, dtid: int, newshow: str) -> None:
    """
    Updates the show value for a document template for where it appears
    """
    dbo.update("templatedocument", dtid, {
        "ShowAt": newshow
    })
    name = get_document_template_name(dbo, dtid)
    asm3.audit.edit(dbo, username, "templatedocument", dtid, "", "update show value of %d (%s) to %s" % (dtid, name, newshow))

def sanitise_path(path: str) -> str:
    """ Strips disallowed chars from new paths """
    disallowed = (" ", "|", ",", "!", "\"", "'", "$", "%", "^", "*",
        "(", ")", "[", "]", "{", "}", "\\", ":", "@", "?", "+")
    for d in disallowed:
        path = path.replace(d, "_")
    return path

