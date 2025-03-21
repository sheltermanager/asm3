# Install new clinic_invoice template
dbo.insert("templatedocument", {
    "ID":       dbo.get_id_max("templatedocument"), 
    "Name":     "clinic_invoice.html",
    "Path":     "/templates",
    "Content":  asm3.utils.base64encode( asm3.utils.read_text_file( dbo.installpath + "media/templates/clinic_invoice.html" ) )
}, generateID=False)