l = dbo.locale
# Add entry type for owner requested euth and set it from the old field
execute(dbo,"INSERT INTO lksentrytype VALUES (10, ?)", [ _("Owner requested euthanasia", l) ])
execute(dbo,"UPDATE animal SET EntryTypeID=10 WHERE AsilomarOwnerRequestedEuthanasia=1")