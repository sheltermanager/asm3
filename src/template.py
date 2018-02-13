#!/usr/bin/python

import audit
import base64
import configuration

def get_html_template(dbo, name):
    """ Returns a tuple of the header, body and footer values for template name """
    rows = dbo.query("SELECT * FROM templatehtml WHERE Name = ?", [name])
    if len(rows) == 0:
        return ("", "", "")
    else:
        return (rows[0].header, rows[0].body, rows[0].footer)

def get_html_templates(dbo):
    """ Returns all available HTML publishing templates (excluding built ins) """
    return dbo.query("SELECT * FROM templatehtml WHERE IsBuiltIn = 0 ORDER BY Name")

def get_html_template_names(dbo):
    l = []
    for r in dbo.query("SELECT Name FROM templatehtml WHERE IsBuiltIn = 0 ORDER BY Name"):
        l.append(r.name)
    return l

def update_html_template(dbo, username, name, head, body, foot, builtin = False):
    """ Creates/updates an HTML publishing template """
    dbo.execute("DELETE FROM templatehtml WHERE Name = ?", [name])
    dbo.insert("templatehtml", {
        "Name":     name,
        "*Header":  head,
        "*Body":    body,
        "*Footer":  foot,
        "IsBuiltIn": builtin and 1 or 0
    })

def delete_html_template(dbo, username, name):
    """ Get an html template by name """
    dbo.execute("DELETE FROM templatehtml WHERE Name = ?", [name])

def get_document_templates(dbo):
    """ Returns all document template info """
    where = ""
    if not configuration.allow_odt_document_templates(dbo):
        where = " WHERE Name LIKE '%.html' "
    return dbo.query("SELECT ID, Name, Path FROM templatedocument %s ORDER BY Path, Name" % where)

def get_document_template_content(dbo, dtid):
    """ Returns the document template content for a given ID """
    return base64.b64decode( dbo.query_string("SELECT Content FROM templatedocument WHERE ID = ?", [dtid]) )

def get_document_template_name(dbo, dtid):
    """ Returns the name for a document template with an ID """
    return dbo.query_string("SELECT Name FROM templatedocument WHERE ID = ?", [dtid])

def create_document_template(dbo, username, name, ext = ".html", content = "<p></p>"):
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
    dtid = dbo.insert("templatedocument", {
        "Name":     name,
        "Path":     path,
        "Content":  base64.b64encode(content)
    })
    audit.create(dbo, username, "templatedocument", dtid, "id: %d, name: %s" % (dtid, name))
    return dtid

def clone_document_template(dbo, username, dtid, newname):
    """
    Creates a new document template with the content from the id given.
    """
    # Get the extension/type from newname, defaulting to html
    ext = ".html"
    if newname.rfind(".") != -1:
        ext = newname[newname.rfind("."):]
    content = get_document_template_content(dbo, dtid)
    ndtid = create_document_template(dbo, username, newname, ext, content)
    return ndtid

def delete_document_template(dbo, username, dtid):
    """
    Deletes a document template
    """
    name = get_document_template_name(dbo, dtid)
    dbo.delete("templatedocument", dtid, username, writeAudit=False)
    audit.delete(dbo, username, "templatedocument", dtid, "delete template %d (%s)" % (dtid, name))

def rename_document_template(dbo, username, dtid, newname):
    """
    Renames a document template.
    """
    if not newname.endswith(".html") and not newname.endswith(".odt"): newname += ".html"
    dbo.update("templatedocument", dtid, {
        "Name":     newname
    })
    audit.edit(dbo, username, "templatedocument", dtid, "rename %d to %s" % (dtid, newname))

def update_document_template_content(dbo, dtid, content):
    """ Changes the content of a template """
    dbo.update("templatedocument", dtid, {
        "Content":  base64.b64encode(content)
    })

def sanitise_path(path):
    """ Strips disallowed chars from new paths """
    disallowed = (" ", "|", ",", "!", "\"", "'", "$", "%", "^", "*",
        "(", ")", "[", "]", "{", "}", "\\", ":", "@", "?", "+")
    for d in disallowed:
        path = path.replace(d, "_")
    return path

