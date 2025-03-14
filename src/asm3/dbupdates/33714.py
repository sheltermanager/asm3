# ASM3 requires a nonzero value for RecordSearchLimit where ASM2 does not
execute(dbo,"UPDATE configuration SET ItemValue = '1000' WHERE ItemName LIKE 'RecordSearchLimit'")