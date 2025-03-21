# Switch shelter animals quicklink for shelter view
# This will fail on locked databases, but shouldn't be an issue.
links = asm3.configuration.quicklinks_id(dbo)
links = links.replace("35", "40")
asm3.configuration.quicklinks_id(dbo, links)