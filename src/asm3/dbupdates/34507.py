# add costtype.AccountID, donationtype.AccountID
add_column(dbo, "costtype", "AccountID", dbo.type_integer)
add_column(dbo, "donationtype", "AccountID", dbo.type_integer)
# Copy the values from the redundant columns in accounts
for a in dbo.query("SELECT ID, CostTypeID, DonationTypeID FROM accounts"):
    if a.COSTTYPEID is not None and a.COSTTYPEID > 0:
        execute(dbo,"UPDATE costtype SET AccountID=? WHERE ID=?", (a.ID, a.COSTTYPEID))
    if a.DONATIONTYPEID is not None and a.DONATIONTYPEID > 0:
        execute(dbo,"UPDATE donationtype SET AccountID=? WHERE ID=?", (a.ID, a.DONATIONTYPEID))