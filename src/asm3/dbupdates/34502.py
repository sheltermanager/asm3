# Replace HTML entities in the database with unicode code points now
# that they are no longer needed.
if dbo.locale not in ( "en", "en_GB", "en_AU" ):
    replace_html_entities(dbo)