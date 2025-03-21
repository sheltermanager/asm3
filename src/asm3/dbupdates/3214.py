# More short fields
fields = [ "diarytaskhead.Name", "diarytaskdetail.Subject", "diarytaskdetail.WhoFor", "lksdonationfreq.Frequency",
    "lksloglink.LinkType", "lksdiarylink.LinkType", "lksfieldlink.LinkType", "lksfieldtype.FieldType",
    "lksmedialink.LinkType", "lksdiarylink.LinkType" ]
for f in fields:
    table, field = f.split(".")
    modify_column(dbo, table, field, dbo.type_shorttext)