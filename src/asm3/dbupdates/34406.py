# Remove bloated items from the config table that now live in the disk cache
execute(dbo,"DELETE FROM configuration WHERE ItemName IN " \
    "('ASMNews', 'LookingForReport', 'LookingForLastMatchCount', 'LostFoundReport', 'LostFoundLastMatchCount')")