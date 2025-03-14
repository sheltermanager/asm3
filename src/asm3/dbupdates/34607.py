# add 2FA columns to users table
add_column(dbo, "users", "EnableTOTP", dbo.type_integer)
add_column(dbo, "users", "OTPSecret", dbo.type_shorttext)
execute(dbo,"UPDATE users SET EnableTOTP=0, OTPSecret=''")