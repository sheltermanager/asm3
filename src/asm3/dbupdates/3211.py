# People who upgraded from ASM2 will find that some of their address fields
# are a bit short - particularly if they are using unicode chars
fields = [ "OwnerTitle", "OwnerInitials", "OwnerForeNames", "OwnerSurname", 
    "OwnerName", "OwnerAddress", "OwnerTown", "OwnerCounty", "OwnerPostcode", 
    "HomeTelephone", "WorkTelephone", "MobileTelephone", "EmailAddress" ]
for f in fields:
    modify_column(dbo, "owner", f, dbo.type_shorttext)