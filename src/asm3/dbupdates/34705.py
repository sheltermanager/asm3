# add movement type to additional fields
l = dbo.locale
execute(dbo,"INSERT INTO lksfieldlink VALUES (22, ?)", [ _("Movement - Adoption", l)])
execute(dbo,"INSERT INTO lksfieldlink VALUES (23, ?)", [ _("Movement - Foster", l)])
execute(dbo,"INSERT INTO lksfieldlink VALUES (24, ?)", [ _("Movement - Transfer", l)])
execute(dbo,"INSERT INTO lksfieldlink VALUES (25, ?)", [ _("Movement - Escaped", l)])
execute(dbo,"INSERT INTO lksfieldlink VALUES (26, ?)", [ _("Movement - Reclaimed", l)])
execute(dbo,"INSERT INTO lksfieldlink VALUES (27, ?)", [ _("Movement - Stolen", l)])
execute(dbo,"INSERT INTO lksfieldlink VALUES (28, ?)", [ _("Movement - Released", l)])
execute(dbo,"INSERT INTO lksfieldlink VALUES (29, ?)", [ _("Movement - Retailer", l)])
execute(dbo,"INSERT INTO lksfieldlink VALUES (30, ?)", [ _("Movement - Reservation", l)])
