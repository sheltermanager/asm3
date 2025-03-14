# Add ownerlookingfor table
sql = "CREATE TABLE ownerlookingfor ( " \
    "OwnerID INTEGER NOT NULL, " \
    "AnimalID INTEGER NOT NULL, " \
    "MatchSummary %s NOT NULL)" % dbo.type_longtext
execute(dbo,sql)
add_index(dbo, "ownerlookingfor_OwnerID", "ownerlookingfor", "OwnerID")
add_index(dbo, "ownerlookingfor_AnimalID", "ownerlookingfor", "AnimalID")
# Add animallostfoundmatch table
sql = "CREATE TABLE animallostfoundmatch ( " \
    "AnimalLostID INTEGER NOT NULL, " \
    "AnimalFoundID INTEGER, " \
    "AnimalID INTEGER, " \
    "LostContactName %(short)s, " \
    "LostContactNumber %(short)s, " \
    "LostArea %(short)s, " \
    "LostPostcode %(short)s, " \
    "LostAgeGroup %(short)s, " \
    "LostSex INTEGER, " \
    "LostSpeciesID INTEGER, " \
    "LostBreedID INTEGER, " \
    "LostFeatures %(long)s, " \
    "LostBaseColourID INTEGER, " \
    "LostDate %(date)s, " \
    "FoundContactName %(short)s, " \
    "FoundContactNumber %(short)s, " \
    "FoundArea %(short)s, " \
    "FoundPostcode %(short)s, " \
    "FoundAgeGroup %(short)s, " \
    "FoundSex INTEGER, " \
    "FoundSpeciesID INTEGER, " \
    "FoundBreedID INTEGER, " \
    "FoundFeatures %(long)s, " \
    "FoundBaseColourID INTEGER, " \
    "FoundDate %(date)s, " \
    "MatchPoints INTEGER NOT NULL)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
execute(dbo,sql)
add_index(dbo, "animallostfoundmatch_AnimalLostID", "animallostfoundmatch", "AnimalLostID")
add_index(dbo, "animallostfoundmatch_AnimalFoundID", "animallostfoundmatch", "AnimalFoundID")
add_index(dbo, "animallostfoundmatch_AnimalID", "animallostfoundmatch", "AnimalID")
