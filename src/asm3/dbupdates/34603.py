l = dbo.locale
# create event tables
execute(dbo,"CREATE TABLE event (ID %(int)s NOT NULL PRIMARY KEY, StartDateTime %(date)s, EndDateTime %(date)s, " \
                    "EventName %(short)s NOT NULL, EventDescription %(long)s NOT NULL," \
                    "RecordVersion %(int)s, CreatedBy %(short)s, CreatedDate %(date)s, LastChangedBy %(short)s, LastChangedDate %(date)s)" \
                    % { "int": dbo.type_integer, "date": dbo.type_datetime, "short": dbo.type_shorttext, "long": dbo.type_longtext })
execute(dbo,"CREATE TABLE eventanimal (ID %(int)s NOT NULL PRIMARY KEY, EventID %(int)s NOT NULL, AnimalID %(int)s NOT NULL, "\
                    "ArrivalDate %(date)s, " \
                    "RecordVersion %(int)s, CreatedBy %(short)s, CreatedDate %(date)s, LastChangedBy %(short)s, LastChangedDate %(date)s)" \
                    % { "int": dbo.type_integer, "date": dbo.type_datetime, "short": dbo.type_shorttext })
add_index(dbo, "event_StartDateTime", "event", "StartDateTime")
add_index(dbo, "event_EndDateTime", "event", "EndDateTime")
add_index(dbo, "event_EventName", "event", "EventName")
add_index(dbo, "eventanimal_EventAnimalID", "eventanimal", "EventID,AnimalID", True)
add_index(dbo, "eventanimal_ArrivalDate", "eventanimal", "ArrivalDate")
# add events to the additional field links
execute(dbo,"INSERT INTO lksfieldlink VALUES (21, '%s')" % _("Event - Details", l))