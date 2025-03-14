# Add ownercitation.CitationNumber
add_column(dbo, "ownercitation", "CitationNumber", dbo.type_shorttext)
add_index(dbo, "ownercitation_CitationNumber", "ownercitation", "CitationNumber")
execute(dbo, "UPDATE ownercitation SET CitationNumber=%s" % dbo.sql_zero_pad_left("ID", 6))