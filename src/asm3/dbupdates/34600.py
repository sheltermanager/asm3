# Remove the old ASM2 report definitions as they break versioning on them if present
execute(dbo,"DELETE FROM customreport WHERE SQLCommand LIKE '0%'")