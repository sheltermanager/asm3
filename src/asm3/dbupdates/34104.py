l = dbo.locale
# Add owner.GDPRContactOptIn
add_column(dbo, "owner", "GDPRContactOptIn", dbo.type_shorttext)
add_index(dbo, "owner_GDPRContactOptIn", "owner", "GDPRContactOptIn")
execute(dbo,"UPDATE owner SET GDPRContactOptIn = ''")
# Add a new GDPR contact opt-in log type
ltid = dbo.get_id_max("logtype")
dbo.insert("logtype", { "ID": ltid, "LogTypeName": _("GDPR Contact Opt-In", l), "IsRetired": 0 }, setOverrideDBLock=True)
asm3.configuration.cset(dbo, "GDPRContactChangeLogType", str(ltid), ignoreDBLock=True)