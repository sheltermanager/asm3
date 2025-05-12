from asm3.dbupdate import execute, add_column, add_index

dbo = dbo
l = dbo.locale

add_column(dbo, "animalmedical", "MedicalTypeID", dbo.type_integer)
add_index(dbo, "animalmedical_MedicalTypeID", "animalmedical", "MedicalTypeID")

add_column(dbo, "medicalprofile", "MedicalTypeID", dbo.type_integer)
add_index(dbo, "medicalprofile_MedicalTypeID", "medicalprofile", "MedicalTypeID")

add_column(dbo, "animalmedical", "CustomTimingRule", dbo.type_shorttext)
add_column(dbo, "medicalprofile", "CustomTimingRule", dbo.type_shorttext)
add_column(dbo, "animalmedicaltreatment", "CustomTreatmentName", dbo.type_shorttext)


# Add the lksmedicaltype table
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("MedicalTypeName", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("Description", dbo.type_longtext, True),
    dbo.ddl_add_table_column("ForceSingleUse", dbo.type_integer, False),
    dbo.ddl_add_table_column("IsRetired", dbo.type_integer, False)
])
execute(dbo, dbo.ddl_add_table("lksmedicaltype", fields) )

data = (
    (1, "Parasite: Worm treatment", 0),
    (2, "Parasite: Flea treatment", 0),
    (3, "Parasite: Other", 0),
    (4, "Allergy treatment", 0),
    (5, "Anti-inflammatory", 0),
    (6, "Antibiotic", 0),
    (7, "Antiviral", 0),
    (8, "Pain relief", 0),
    (9, "Euthanasia", 1),
    (10, "Anesthesia", 1),
    (11, "Medicated bath", 0),
    (12, "Examination", 1),
    (13, "Surgery: Sterilization", 1),
    (14, "Surgery: C-Section", 1),
    (15, "X-Ray / Scan", 1),
    (16, "Surgery: Amputation", 1),
    (17, "Other", 0),
    (18, "Microchip", 1),
    (19, "Tattoo", 1),
    (20, "Parasite: Antifungal", 0),
    (21, "Parasite: Heartworm", 0),
    (22, "Dietary supplement", 0),
    (23, "Appetite stimulant", 0),
    (24, "Anti-nausea", 0),
    (25, "Anti-diarrhea", 0),
    (26, "Surgery: Dental procedure", 1),
    (27, "Surgery: Other", 1),
    (28, "Topical treatment", 0)
)

for d in data:
    execute(dbo, "INSERT INTO lksmedicaltype (ID, MedicalTypeName, Description, ForceSingleUse, IsRetired) VALUES (?, ?, ?, ?, ?)", [ d[0], _(d[1], l), "", d[2], 0 ])