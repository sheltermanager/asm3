# Remove last published fields added since ASM3 - we're only retaining
# the ASM2 ones for compatibility and everything else is going to
# the animalpublished table
drop_column(dbo, "media", "LastPublishedHLP")
drop_column(dbo, "media", "LastPublishedMP")
drop_column(dbo, "animal", "PetLinkSentDate")