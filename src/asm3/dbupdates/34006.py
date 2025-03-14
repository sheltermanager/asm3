# Set includenonneutered in the publishing presets
s = asm3.configuration.publisher_presets(dbo)
s += " includenonneutered"
execute(dbo,"UPDATE configuration SET ItemValue = ? WHERE ItemName = 'PublisherPresets'", [ s ])