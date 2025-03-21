# Copy addresses from any existing transport records to the new fields
# (only acts on transport records with blank addresses)
tr = dbo.query("SELECT animaltransport.ID, " \
    "dro.OwnerAddress AS DRA, dro.OwnerTown AS DRT, dro.OwnerCounty AS DRC, dro.OwnerPostcode AS DRP, " \
    "po.OwnerAddress AS POA, po.OwnerTown AS POT, po.OwnerCounty AS POC, po.OwnerPostcode AS POD " \
    "FROM animaltransport " \
    "INNER JOIN owner dro ON animaltransport.DropoffOwnerID = dro.ID " \
    "INNER JOIN owner po ON animaltransport.PickupOwnerID = po.ID "\
    "WHERE PickupAddress Is Null OR DropoffAddress Is Null")
for t in tr:
    execute(dbo,"UPDATE animaltransport SET " \
        "PickupAddress = ?, PickupTown = ?, PickupCounty = ?, PickupPostcode = ?,  " \
        "DropoffAddress = ?, DropoffTown = ?, DropoffCounty = ?, DropoffPostcode = ? " \
        "WHERE ID = ?", ( \
        t["POA"], t["POT"], t["POC"], t["POD"], 
        t["DRA"], t["DRT"], t["DRC"], t["DRP"],
        t["ID"] ))