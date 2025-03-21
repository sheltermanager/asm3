# Correct payment amounts to gross where sales tax exists.
# This query only updates the amount if the tax value matches
# an exclusive of tax calculation.
# Eg: amount = 100, vat = 6, rate = 6 - will update amount to 106 because 100 * 0.06 == 6.0
#     amount = 106, vat = 6, rate = 6 - will not update as 106 * 0.06 == 6.35
execute(dbo,"UPDATE ownerdonation SET donation = donation + vatamount, " \
    "LastChangedBy = %s " \
    "WHERE isvat = 1 and vatamount > 0 and vatrate > 0 and vatamount = ((donation / 100.0) * vatrate)" % 
    dbo.sql_concat(["LastChangedBy", "'+dbupdate34405'"]))
