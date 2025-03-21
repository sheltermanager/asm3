# Add ownerlicence.Token and ownerlicence.Renewed
add_column(dbo, "ownerlicence", "Token", dbo.type_shorttext)
add_column(dbo, "ownerlicence", "Renewed", dbo.type_integer)
add_index(dbo, "ownerlicence_Token", "ownerlicence", "Token") 
add_index(dbo, "ownerlicence_Renewed", "ownerlicence", "Renewed")
add_column(dbo, "licencetype", "RescheduleDays", dbo.type_integer)
execute(dbo,"UPDATE licencetype SET RescheduleDays=365")
execute(dbo,"UPDATE ownerlicence SET Renewed = 0")
execute(dbo,"UPDATE ownerlicence SET Renewed = 1 " \
    "WHERE EXISTS(SELECT oli.ID FROM ownerlicence oli WHERE oli.LicenceTypeID = ownerlicence.LicenceTypeID "
    "AND oli.OwnerID = ownerlicence.OwnerID AND oli.AnimalID = ownerlicence.AnimalID AND oli.IssueDate > ownerlicence.IssueDate)")
# Use MD5 hashes of the ID for old tokens for speed (we use UUIDs for new ones)
execute(dbo,"UPDATE ownerlicence SET Token = %s" % (dbo.sql_md5("ID")))