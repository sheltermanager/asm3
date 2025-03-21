# Switch ui-lightness and smoothness to the new asm replacement theme
execute(dbo,"UPDATE configuration SET itemvalue='asm' WHERE itemvalue = 'smoothness' OR itemvalue = 'ui-lightness'")