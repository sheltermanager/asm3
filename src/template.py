#!/usr/bin/python

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
    dbo.execute("DELETE FROM templatehtml WHERE Name = ?", [name])


