from asm3.dbupdate import add_column, add_index, execute
add_column(dbo, "ownerdonation", "FundedByOwnerDonationID", dbo.type_integer)
add_column(dbo, "ownerdonation", "IsFundingSource", dbo.type_integer)

add_index(dbo, "ownerdonation_FundedByOwnerDonationID", "ownerdonation", "FundedByOwnerDonationID")
add_index(dbo, "ownerdonation_IsFundingSource", "ownerdonation", "IsFundingSource")

execute(dbo, "UPDATE ownerdonation SET FundedByOwnerDonationID = 0")
execute(dbo, "UPDATE ownerdonation SET IsFundingSource = 0")