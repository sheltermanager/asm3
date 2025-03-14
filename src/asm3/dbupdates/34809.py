# Add ownerlicence.PaymentReference
add_column(dbo, "ownerlicence", "PaymentReference", dbo.type_shorttext)
add_index(dbo, "ownerlicence_PaymentReference", "ownerlicence", "PaymentReference") 
execute(dbo,"UPDATE ownerlicence SET PaymentReference = ''")