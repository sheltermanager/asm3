# Add a display index field to onlineformfield
add_column(dbo, "onlineformfield", "DisplayIndex", "INTEGER")
# Add a label field to onlineformincoming
add_column(dbo, "onlineformincoming", "Label", dbo.type_shorttext)