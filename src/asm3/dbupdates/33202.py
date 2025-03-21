# Add the animalpublished table to track what was sent to which
# publisher and when
sql = "CREATE TABLE animalpublished (" \
    "AnimalID INTEGER NOT NULL, " \
    "PublishedTo %s NOT NULL, " \
    "SentDate %s NOT NULL, " \
    "Extra %s)" % (dbo.type_shorttext, dbo.type_datetime, dbo.type_shorttext)
execute(dbo,sql)
add_index(dbo, "animalpublished_AnimalIDPublishedTo", "animalpublished", "AnimalID, PublishedTo", True)
add_index(dbo, "animalpublished_SentDate", "animalpublished", "SentDate")
# Copy existing values into the new table
execute(dbo,"INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
    "SELECT a.ID, 'smarttag', a.SmartTagSentDate FROM animal a WHERE a.SmartTagSentDate Is Not Null")
execute(dbo,"INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
    "SELECT a.ID, 'petlink', a.PetLinkSentDate FROM animal a WHERE a.PetLinkSentDate Is Not Null")
execute(dbo,"INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
    "SELECT DISTINCT m.LinkID, 'html', m.LastPublished FROM media m WHERE m.LastPublished Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
execute(dbo,"INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
    "SELECT DISTINCT m.LinkID, 'petfinder', m.LastPublishedPF FROM media m WHERE m.LastPublishedPF Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
execute(dbo,"INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
    "SELECT DISTINCT m.LinkID, 'adoptapet', m.LastPublishedAP FROM media m WHERE m.LastPublishedAP Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
execute(dbo,"INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
    "SELECT DISTINCT m.LinkID, 'pets911', m.LastPublishedP911 FROM media m WHERE m.LastPublishedP911 Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
execute(dbo,"INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
    "SELECT DISTINCT m.LinkID, 'rescuegroups', m.LastPublishedRG FROM media m WHERE m.LastPublishedRG Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
execute(dbo,"INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
    "SELECT DISTINCT m.LinkID, 'meetapet', m.LastPublishedMP FROM media m WHERE m.LastPublishedMP Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
execute(dbo,"INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
    "SELECT DISTINCT m.LinkID, 'helpinglostpets', m.LastPublishedHLP FROM media m WHERE m.LastPublishedHLP Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
