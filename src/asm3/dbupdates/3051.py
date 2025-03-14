# Fix incorrect field name from ASM3 initial install (it was listed
# as TimingRuleNoFrequency instead of TimingRuleFrequency)
if column_exists(dbo, "medicalprofile", "TimingRuleNoFrequency"):
    add_column(dbo, "medicalprofile", "TimingRuleFrequency", "INTEGER")
    drop_column(dbo, "medicalprofile", "TimingRuleNoFrequency")