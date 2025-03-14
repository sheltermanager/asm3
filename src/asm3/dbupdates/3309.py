if dbo.query_int("SELECT COUNT(*) FROM animaltest") == 0:
    fiv = dbo.query("SELECT ID, CombiTestDate, CombiTestResult FROM animal WHERE CombiTested = 1 AND CombiTestDate Is Not Null")
    asm3.al.debug("found %d fiv results to convert" % len(fiv), "update_3309", dbo)
    for f in fiv:
        try:
            dbo.insert("animaltest", {
                "ID": dbo.get_id_max("animaltest"),
                "AnimalID": f["ID"],
                "TestTypeID": 1,
                "TestResultID": f["COMBITESTRESULT"] + 1,
                "DateOfTest": f["COMBITESTDATE"],
                "DateRequired": f["COMBITESTDATE"],
                "Cost": 0,
                "Comments": ""
            }, user="dbupdate", generateID=False, writeAudit=False)
        except Exception as err:
            asm3.al.error("fiv: " + str(err), "dbupdate.update_3309", dbo)
    flv = dbo.query("SELECT ID, CombiTestDate, FLVResult FROM animal WHERE CombiTested = 1 AND CombiTestDate Is Not Null")
    asm3.al.debug("found %d flv results to convert" % len(flv), "update_3309", dbo)
    for f in flv:
        try:
            dbo.insert("animaltest", {
                "ID": dbo.get_id_max("animaltest"),
                "AnimalID": f["ID"],
                "TestTypeID": 2,
                "TestResultID": f["FLVRESULT"] + 1,
                "DateOfTest": f["COMBITESTDATE"],
                "DateRequired": f["COMBITESTDATE"],
                "Cost": 0,
                "Comments": ""
            }, user="dbupdate", generateID=False, writeAudit=False)
        except Exception as err:
            asm3.al.error("flv: " + str(err), "dbupdate.update_3309", dbo)
    hw = dbo.query("SELECT ID, HeartwormTestDate, HeartwormTestResult FROM animal WHERE HeartwormTested = 1 AND HeartwormTestDate Is Not Null")
    asm3.al.debug("found %d heartworm results to convert" % len(hw), "update_3309", dbo)
    for f in hw:
        try:
            dbo.insert("animaltest", {
                "ID": dbo.get_id_max("animaltest"),
                "AnimalID": f["ID"],
                "TestTypeID": 3,
                "TestResultID": f["HEARTWORMTESTRESULT"] + 1,
                "DateOfTest": f["HEARTWORMTESTDATE"],
                "DateRequired": f["HEARTWORMTESTDATE"],
                "Cost": 0,
                "Comments": ""
            }, user="dbupdate", generateID=False, writeAudit=False)
        except Exception as err:
            asm3.al.error("hw: " + str(err), "dbupdate.update_3309", dbo)