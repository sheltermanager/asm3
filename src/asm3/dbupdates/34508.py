# Replace old JQUI themes with light or dark
execute(dbo,"UPDATE users SET ThemeOverride='asm' WHERE ThemeOverride IN ('base','cupertino'," \
    "'dot-luv','excite-bike','flick','hot-sneaks','humanity','le-frog','overcast','pepper-grinder','redmond'," \
    "'smoothness','south-street','start','sunny','swanky-purse','ui-lightness')")
execute(dbo,"UPDATE users SET ThemeOverride='asm-dark' WHERE ThemeOverride IN ('black-tie','blitzer'," \
    "'dark-hive','eggplant','mint-choc','trontastic','ui-darkness','vader')")