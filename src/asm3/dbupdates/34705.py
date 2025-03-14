# add movement type to additional fields
l = dbo.locale
execute(dbo,"INSERT INTO lksfieldlink VALUES (22, '%s')" % _("Movement - Adoption", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (23, '%s')" % _("Movement - Foster", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (24, '%s')" % _("Movement - Transfer", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (25, '%s')" % _("Movement - Escaped", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (26, '%s')" % _("Movement - Reclaimed", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (27, '%s')" % _("Movement - Stolen", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (28, '%s')" % _("Movement - Released", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (29, '%s')" % _("Movement - Retailer", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (30, '%s')" % _("Movement - Reservation", l))