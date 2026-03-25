from asm3.dbupdate import add_column, add_index
add_column(dbo, "ownerdonation", "FundedByOwnerDonationID", dbo.type_integer)
add_column(dbo, "ownerdonation", "AvailableForFunding", dbo.type_integer)

add_index(dbo, "ownerdonation_FundedByOwnerDonationID", "ownerdonation", "FundedByOwnerDonationID")
add_index(dbo, "ownerdonation_AvailableForFunding", "ownerdonation", "AvailableForFunding")
