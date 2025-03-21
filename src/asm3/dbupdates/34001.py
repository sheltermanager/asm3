# Remove the unique index on LicenceNumber and make it non-unique (optionally enforced by backend code)
drop_index(dbo, "ownerlicence_LicenceNumber", "ownerlicence")
add_index(dbo, "ownerlicence_LicenceNumber", "ownerlicence", "LicenceNumber")