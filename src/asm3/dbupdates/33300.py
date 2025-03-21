# Add animalcontrol table
sql = "CREATE TABLE animalcontrol (" \
    "ID INTEGER NOT NULL PRIMARY KEY, " \
    "IncidentDateTime %(date)s NOT NULL, " \
    "IncidentTypeID INTEGER NOT NULL, " \
    "CallDateTime %(date)s, " \
    "CallNotes %(long)s, " \
    "CallTaker %(short)s, " \
    "CallerID INTEGER, " \
    "VictimID INTEGER, " \
    "DispatchAddress %(short)s, " \
    "DispatchTown %(short)s, " \
    "DispatchCounty %(short)s, " \
    "DispatchPostcode %(short)s, " \
    "DispatchLatLong %(short)s, " \
    "DispatchedACO %(short)s, " \
    "DispatchDateTime %(date)s, " \
    "RespondedDateTime %(date)s, " \
    "FollowupDateTime %(date)s, " \
    "CompletedDate %(date)s, " \
    "IncidentCompletedID INTEGER, " \
    "OwnerID INTEGER, " \
    "AnimalDescription %(long)s, " \
    "SpeciesID INTEGER, " \
    "Sex INTEGER, " \
    "AgeGroup %(short)s, " \
    "RecordVersion INTEGER, " \
    "CreatedBy %(short)s, " \
    "CreatedDate %(date)s, " \
    "LastChangedBy %(short)s, " \
    "LastChangedDate %(date)s)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
execute(dbo,sql)
add_index(dbo, "animalcontrol_IncidentDateTime", "animalcontrol", "IncidentDateTime")
add_index(dbo, "animalcontrol_IncidentTypeID", "animalcontrol", "IncidentTypeID")
add_index(dbo, "animalcontrol_CallDateTime", "animalcontrol", "CallDateTime")
add_index(dbo, "animalcontrol_CallerID", "animalcontrol", "CallerID")
add_index(dbo, "animalcontrol_DispatchAddress", "animalcontrol", "DispatchAddress")
add_index(dbo, "animalcontrol_DispatchPostcode", "animalcontrol", "DispatchPostcode")
add_index(dbo, "animalcontrol_DispatchedACO", "animalcontrol", "DispatchedACO")
add_index(dbo, "animalcontrol_DispatchDateTime", "animalcontrol", "DispatchDateTime")
add_index(dbo, "animalcontrol_CompletedDate", "animalcontrol", "CompletedDate")
add_index(dbo, "animalcontrol_IncidentCompletedID", "animalcontrol", "IncidentCompletedID")
add_index(dbo, "animalcontrol_OwnerID", "animalcontrol", "OwnerID")
add_index(dbo, "animalcontrol_VictimID", "animalcontrol", "VictimID")