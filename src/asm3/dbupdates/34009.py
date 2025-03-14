# Set includewithoutdescription in the publishing presets
s = asm3.configuration.publisher_presets(dbo)
s += " includewithoutdescription"
execute(dbo,"UPDATE configuration SET ItemValue = ? WHERE ItemName = 'PublisherPresets'", [ s ])