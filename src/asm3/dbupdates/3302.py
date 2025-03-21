# Add default cost fields to costtype and voucher
add_column(dbo, "costtype", "DefaultCost", "INTEGER")
add_column(dbo, "voucher", "DefaultCost", "INTEGER")