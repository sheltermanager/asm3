# Assume all already adopted animals with PETtrac UK chips have been sent to them
execute(dbo,"INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
    "SELECT a.ID, 'pettracuk', a.ActiveMovementDate FROM animal a " \
    "WHERE ActiveMovementDate Is Not Null " \
    "AND ActiveMovementType = 1 AND IdentichipNumber LIKE '977%'")