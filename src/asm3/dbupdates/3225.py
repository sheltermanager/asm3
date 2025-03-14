# Make sure the ADOPTIONFEE mistake is really gone
if column_exists(dbo, "species", "AdoptionFee"):
    execute(dbo,"ALTER TABLE species DROP COLUMN AdoptionFee")