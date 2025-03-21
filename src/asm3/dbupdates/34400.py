# Add new lksdonationfreq for fortnightly with ID 2
# This requires renumbering the existing frequencies up one as there was no spare slot
if dbo.query_int("SELECT MAX(ID) FROM lksdonationfreq") != 6:
    l = dbo.locale
    execute(dbo,"UPDATE lksdonationfreq SET ID=6 WHERE ID=5")
    execute(dbo,"UPDATE lksdonationfreq SET ID=5 WHERE ID=4")
    execute(dbo,"UPDATE lksdonationfreq SET ID=4 WHERE ID=3")
    execute(dbo,"UPDATE lksdonationfreq SET ID=3 WHERE ID=2")
    execute(dbo,"UPDATE ownerdonation SET Frequency=Frequency+1 WHERE Frequency IN (2,3,4,5)")
    execute(dbo,"INSERT INTO lksdonationfreq (ID, Frequency) VALUES (2, ?)", [ _("Fortnightly", l) ])