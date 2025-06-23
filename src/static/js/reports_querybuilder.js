/*global $, jQuery, _, asm, common, config, format, html, tableform */

$(function() {

    "use strict";

    const ADDITIONAL_ANIMAL = [0,2,3,4,5,6];
    const ADDITIONAL_PERSON = [1,7,8];
    const ADDITIONAL_INCIDENT = [16,17,18,19,20];
    const ADDITIONAL_WAITINGLIST = [13,14,15];

    const QB_ANIMAL_CRITERIA = [
            [ _("Adoptable"), "adoptable", "Archived=0 AND IsNotAvailableForAdoption=0" ],
            [ _("Adopted"), "adopted", "ActiveMovementDate Is Not Null AND ActiveMovementType=1" ],
            [ _("Aged under 6 months"), "under6months", "DateOfBirth >= '$CURRENT_DATE-182$'" ],
            [ _("Aged over 6 months"), "over6months", "DateOfBirth < '$CURRENT_DATE-182$'" ],
            [ _("Altered"), "altered", "Neutered=1" ],
            [ _("Altered between two dates"), "alteredtwodates", 
                "NeuteredDate>='$ASK DATE {0}$' AND NeuteredDate<='$ASK DATE {1}$'"
                .replace("{0}", _("Altered between"))
                .replace("{1}", _("and")) ],
            [ _("Ask the user for a color"), "askcolor", "BaseColourName LIKE '%$ASK STRING Color$%'" ],
            [ _("Ask the user for an entry category"), "askentry", "EntryReasonID=$ASK ENTRYCATEGORY$" ],
            [ _("Ask the user for a flag"), "askflag", "AdditionalFlags LIKE '%$ASK ANIMALFLAG$%'" ],
            [ _("Ask the user for a location"), "asklocation", "ShelterLocation=$ASK LOCATION$" ],
            [ _("Ask the user for a species"), "askspecies", "SpeciesID=$ASK SPECIES$" ],
            [ _("Ask the user for a type"), "asktype", "AnimalTypeID=$ASK ANIMALTYPE$" ],
            [ _("Cruelty Case"), "cruelty", "CrueltyCase=1" ],
            [ _("Date brought in between two dates"), "dbintwodates", 
                "DateBroughtIn>='$ASK DATE {0}$' AND DateBroughtIn<='$ASK DATE {1}$'"
                .replace("{0}", _("Entered the shelter between"))
                .replace("{1}", _("and")) ],
            [ _("Date of birth after"), "dobafter", "DateOfBirth > '$ASK DATE Date of birth after$'"],
            [ _("Date of birth between two dates"), "dobtwodates", 
                "DateOfBirth>='$ASK DATE {0}$' AND DateOfBirth<='$ASK DATE {1}$'"
                .replace("{0}", _("Date of birth between"))
                .replace("{1}", _("and")) ],
            [ _("Deceased"), "deceased", "DeceasedDate Is Not Null" ],
            [ _("Died between two dates"), "diedtwodates", 
                "DeceasedDate>='$ASK DATE {0}$' AND DeceasedDate<='$ASK DATE {1}$'"
                .replace("{0}", _("Died between"))
                .replace("{1}", _("and")) ],
            [ _("Died in care"), "diedincare", "DeceasedDate Is Not Null AND PutToSleep=0" ],
            [ _("Died today"), "diedtoday", "DeceasedDate = '$CURRENT_DATE$'" ],
            [ _("Entered the shelter today"), "entertoday", "Archived=0 AND MostRecentEntryDate>='$CURRENT_DATE$'" ],
            [ _("Entered the shelter between two dates"), "entertwodates", 
                "MostRecentEntryDate>='$ASK DATE {0}$' AND MostRecentEntryDate<='$ASK DATE {1}$'"
                .replace("{0}", _("Entered the shelter between"))
                .replace("{1}", _("and")) ],
            [ _("Escaped"), "escaped", "ActiveMovementDate Is Not Null AND ActiveMovementType=4" ],
            [ _("Euthanized"), "euthanised", "DeceasedDate Is Not Null AND PutToSleep=1" ],
            [ _("FIV+"), "fivplus", "CombiTested=1 AND CombiTestResult=2" ],
            [ _("FIV-"), "fivneg", "CombiTested=1 AND CombiTestResult=1" ],
            [ _("FIV Tested"), "fivtest", "CombiTested=1" ],
            [ _("FLV+"), "flvplus", "CombiTested=1 AND FLVResult=2" ],
            [ _("FLV-"), "flvneg", "CombiTested=1 AND FLVResult=1" ],
            [ _("Fostered between two dates"), "fostertwodates", 
                "ActiveMovementType = 2 AND ActiveMovementDate Is Not Null AND " +
                "ActiveMovementDate>='$ASK DATE {0}$' AND ActiveMovementDate<='$ASK DATE {1}$'"
                .replace("{0}", _("Fostered between"))
                .replace("{1}", _("and")) ],
            [ _("Good with cats"), "goodwithcats", "IsGoodWithCats=0" ],
            [ _("Good with children"), "goodwithkids", "IsGoodWithChildren=0" ],
            [ _("Good with dogs"), "goodwithdogs", "IsGoodWithDogs=0" ],
            [ _("Heartworm+"), "heartwormplus", "HeartwormTested=1 AND HeartwormTestResult=2" ],
            [ _("Heartworm-"), "heartwormneg", "HeartwormTested=1 AND HeartwormTestResult=1" ],
            [ _("Heartworm Tested"), "heartwormtest", "HeartwormTested=1" ],
            [ _("Held"), "held", "IsHold=1" ],
            [ _("Housetrained"), "housetrained", "IsHouseTrained=0" ],
            [ _("Left shelter"), "leftshelter", "Archived=1" ],
            [ _("Left the shelter today"), "lefttoday", "Archived=1 AND ActiveMovementDate = '$CURRENT_DATE$'" ],
            [ _("Left the shelter between two dates"), "lefttwodates", 
                "ActiveMovementType NOT IN (2,8) AND ActiveMovementDate Is Not Null AND " +
                "ActiveMovementDate>='$ASK DATE {0}$' AND ActiveMovementDate<='$ASK DATE {1}$'"
                .replace("{0}", _("Left the shelter between"))
                .replace("{1}", _("and")) ],
            [ _("Licensed"), "activelicense", "EXISTS(SELECT ID FROM ownerlicense WHERE AnimalID=v_animal.ID " +
                "AND IssueDate<='$CURRENT_DATE$' AND (ExpiryDate Is Null OR ExpiryDate>'$CURRENT_DATE$'))" ],
            [ _("No license"), "nolicense", "NOT EXISTS(SELECT ID FROM ownerlicense WHERE AnimalID=v_animal.ID " +
                "AND IssueDate<='$CURRENT_DATE$' AND (ExpiryDate Is Null OR ExpiryDate>'$CURRENT_DATE$'))" ],
            [ _("Non-shelter"), "nonshelter", "NonShelterAnimal=1" ],
            [ _("Not adoptable"), "notadoptable", "IsNotAvailableForAdoption=1" ],
            [ _("Not altered"), "notaltered", "Neutered=0" ],
            [ _("Not deceased"), "notdeceased", "DeceasedDate Is Null" ],
            [ _("Not microchipped"), "notmicrochip", "IdentichipNumber=0" ],
            [ _("Not non-shelter"), "notnonshelter", "NonShelterAnimal=0" ],
            [ _("No tattoo"), "nottattoo", "Tattoo=0" ],
            [ _("Reclaimed"), "reclaimed", "ActiveMovementDate Is Not Null AND ActiveMovementType=5" ],
            [ _("Reserved"), "reserved", "HasActiveReserve=1" ],
            [ _("On foster"), "onfoster", "ActiveMovementType=2 AND HasPermanentFoster=0" ],
            [ _("On permanent foster"), "onpfoster", "ActiveMovementType=2 AND HasPermanentFoster=1" ],
            [ _("On shelter"), "onshelter", "Archived=0" ],
            [ _("On shelter (no fosters)"), "onshelternf", "Archived=0 AND (ActiveMovementType Is Null OR ActiveMovementType=0)" ],
            [ _("On shelter (at date)"), "osatdate", 
                "NOT EXISTS (SELECT MovementDate FROM adoption WHERE MovementDate <= '$@osatdate$ 23:59:59' AND (ReturnDate Is Null OR ReturnDate > '$@osatdate$') AND MovementType NOT IN (2,8) AND AnimalID = v_animal.ID) " +
                "AND DateBroughtIn <= '$@osatdate$ 23:59:59' " +
                "AND NonShelterAnimal = 0 " + 
                "AND (DeceasedDate Is Null OR DeceasedDate > '$@osatdate$ 23:59:59') " ],
            [ _("On shelter (between two dates)"), "ostwodates", 
                "NOT EXISTS (SELECT MovementDate FROM adoption WHERE MovementDate <= '$@osfrom$ 23:59:59' AND (ReturnDate Is Null OR ReturnDate > '$@osfrom$') AND MovementType NOT IN (2,8) AND AnimalID = v_animal.ID) " +
                "AND DateBroughtIn <= '$@osto$ 23:59:59' " +
                "AND NonShelterAnimal = 0 " + 
                "AND (DeceasedDate Is Null OR DeceasedDate > '$@osfrom$ 23:59:59') " ],
            [ _("On trial adoption"), "trialadoption", "ActiveMovementType=1 AND HasTrialAdoption=1" ],
            [ _("Pickup"), "pickup", "IsPickup=1" ],
            [ _("Quarantine"), "quarantine", "IsQuarantine=1" ],
            [ _("Released to Wild"), "released", "ActiveMovementDate Is Not Null AND ActiveMovementType=7" ],
            [ _("Sex is male"), "male", "Sex=1" ],
            [ _("Sex is female"), "female", "Sex=0" ],
            [ _("Site matches current user"), "site", "SiteID=$SITE$" ],
            [ _("Stolen"), "stolen", "ActiveMovementDate Is Not Null AND ActiveMovementType=6" ],
            [ _("TNR"), "tnr", "ActiveMovementDate Is Not Null AND ActiveMovementType=7" ],
            [ _("Transfer In"), "transferin", "IsTransfer=1" ],
            [ _("Transferred Out"), "transferout", "ActiveMovementDate Is Not Null AND ActiveMovementType=3" ]
        ];

        const QB_INCIDENT_CRITERIA = [
            [ _("Active"), "active", "CompletedDate Is Null" ],
            [ _("Ask the user for a city"), "askcity", "DispatchTown LIKE '%$ASK STRING {0}$%'"
                .replace("{0}", _("Enter a city")) ],
            [ _("Call between two dates"), "calltwo", 
                "CallDateTime>='$ASK DATE {0}$' AND CallDateTime<='$ASK DATE {1}$'"
                .replace("{0}", _("Call between"))
                .replace("{1}", _("and")) ],
            [ _("Completed"), "completed", "CompletedDate Is Not Null" ],
            [ _("Completed between two dates"), "completedtwo", 
                "CompletedDate Is Not Null AND CompletedDate>='$ASK DATE {0}$' AND CompletedDate<='$ASK DATE {1}$'"
                .replace("{0}", _("Completed between"))
                .replace("{1}", _("and")) ],
            [ _("Incident between two dates"), "incidenttwo", 
                "IncidentDateTime>='$ASK DATE {0}$' AND IncidentDateTime<='$ASK DATE {1}$'"
                .replace("{0}", _("Incident between"))
                .replace("{1}", _("and")) ],
            [ _("Followup between two dates"), "followuptwo", 
                "FollowupDateTime>='$ASK DATE {0}$' AND FollowupDateTime<='$ASK DATE {1}$'"
                .replace("{0}", _("Followup between"))
                .replace("{1}", _("and")) ],
            [ _("Site matches current user"), "site", "SiteID=$SITE$" ]
        ];

        const QB_MEDICAL_CRITERIA = [ 
            [ _("Ask the user for a treatment"), "asktreatment", "TreatmentName LIKE '%$ASK STRING {0}$%'"
                .replace("{0}", _("Enter a treatment name")) ],
            [ _("Ask the user for a medical type"), "askmedicaltype", "MedicalTypeName LIKE '%$ASK STRING {0}$%'"
                .replace("{0}", _("Enter a medical type name")) ],
            [ _("Due"), "duenow", "DateGiven Is Null" ],
            [ _("Due between two dates"), "duetwo", 
                "DateRequired>='$ASK DATE {0}$' AND DateRequired<='$ASK DATE {1}$'"
                .replace("{0}", _("Due between"))
                .replace("{1}", _("and")) ],
            [ _("Given"), "givennow", "DateGiven Is Not Null" ],
            [ _("Given between two dates"), "giventwo", 
                "DateGiven>='$ASK DATE {0}$' AND DateGiven<='$ASK DATE {1}$'"
                .replace("{0}", _("Given between"))
                .replace("{1}", _("and")) ]
        ];

        const QB_PAYMENT_CRITERIA = [
            [ _("Ask the user for a check number"), "askcheck", "ChequeNumber LIKE '%$ASK NUMBER {0}$%'"
                .replace("{0}", _("Check")) ],
            [ _("Ask the user for a payment type"), "askpaymenttype", "DonationTypeID=$ASK PAYMENTTYPE$'" ],
            [ _("Ask the user for a payment method"), "askpaymentmethod", "DonationPaymentID=$ASK PAYMENTMETHOD$'" ],
            [ _("Ask the user for a receipt number"), "askreceipt", "ReceiptNumber LIKE '%$ASK NUMBER {0}$%'"
                .replace("{0}", _("Receipt")) ],
            [ _("Due"), "duenow", "DateDue Is Null" ],
            [ _("Due between two dates"), "duetwo", 
                "DateDue>='$ASK DATE {0}$' AND DateDue<='$ASK DATE {1}$'"
                .replace("{0}", _("Due between"))
                .replace("{1}", _("and")) ],
            [ _("Received"), "receivednow", "Date Is Not Null" ],
            [ _("Received between two dates"), "receivedtwo", 
                "Date>='$ASK DATE {0}$' AND Date<='$ASK DATE {1}$'"
                .replace("{0}", _("Received between"))
                .replace("{1}", _("and")) ]
        ];

        const QB_PERSON_CRITERIA = [
            [ _("ACO"), "aco", "IsACO=1" ],
            [ _("Active license held"), "haslicense", "EXISTS(SELECT ID FROM ownerlicence WHERE OwnerID=v_owner.ID " +
                "AND IssueDate<='$CURRENT_DATE$' AND (ExpiryDate Is Null OR ExpiryDate>'$CURRENT_DATE$'))" ],
            [ _("Adopter"), "adopter", "IsAdopter=1" ],
            [ _("Adoption Coordinator"), "coordinator", "IsAdoptionCoordinator=1" ],
            [ _("Ask the user for a flag"), "askflag", "AdditionalFlags LIKE '%$ASK PERSONFLAG$%'" ],
            [ _("Ask the user for a city"), "askcity", "OwnerTown LIKE '%$ASK STRING {0}$%'"
                .replace("{0}", _("Enter a city")) ],
            [ _("Banned"), "banned", "IsBanned=1" ],
            [ _("Created since"), "createdsince", "CreatedDate>='$ASK DATE {0}$'".replace("{0}", _("Created since")) ],
            [ _("Deceased"), "deceased", "IsDeceased=1" ],
            [ _("Donor"), "donor", "IsDonor=1" ],
            [ _("Driver"), "driver", "IsDriver=1" ],
            [ _("Fosterer"), "fosterer", "IsFosterer=1" ],
            [ _("GiftAid"), "giftaid", "IsGiftAid=1" ],
            [ _("Homechecked"), "homechecked", "IDCheck=1" ],
            [ _("Homechecked between two dates"), "homechecktwo", 
                "DateLastHomeChecked>='$ASK DATE {0}$' AND DateLastHomeChecked<='$ASK DATE {1}$'"
                .replace("{0}", _("Homechecked between"))
                .replace("{1}", _("and")) ],
            [ _("Homechecked by"), "homecheckedby", "IDCheck=1 AND HomeCheckedBy=$ASK PERSON$" ],
            [ _("Member"), "member", "IsMember=1" ],
            [ _("No active license held"), "nolicense", "NOT EXISTS(SELECT ID FROM ownerlicence WHERE OwnerID=v_owner.ID " +
                "AND IssueDate<='$CURRENT_DATE$' AND (ExpiryDate Is Null OR ExpiryDate>'$CURRENT_DATE$'))" ],
            [ _("Retailer"), "retailer", "IsRetailer=1" ],
            [ _("Site matches current user"), "site", "SiteID=$SITE$" ],
            [ _("Staff"), "staff", "IsStaff=1" ],
            [ _("Vet"), "vet", "IsVet=1" ],
            [ _("Volunteer"), "volunteer", "IsVolunteer=1" ]
        ];

        const QB_WAITINGLIST_CRITERIA = [
            [ _("Put on the list between two dates"), "onlisttwodates", 
                "DatePutOnList >='$ASK DATE {0}$' AND DatePutOnList <= '$ASK DATE {1}$'"
                .replace("{0}", _("Put on the list between"))
                .replace("{1}", _("and")) ],
            [ _("Removed from the list between two dates"), "removedlisttwodates", 
                "DateRemovedFromList >='$ASK DATE {0}$' AND DateRemovedFromList <= '$ASK DATE {1}$'"
                .replace("{0}", _("Removed from the list between"))
                .replace("{1}", _("and")) ]
        ];

    const reports_querybuilder = {

        qb_active_criteria: null, 
        qb_animal_criteria: null,
        qb_incident_criteria: null,
        qb_medical_criteria: null,
        qb_payment_criteria: null,
        qb_person_criteria: null,
        qb_waitinglist_criteria: null,

        render: function() {
            return [
                '<div id="dialog-qb" style="display: none" title="' + html.title(_("Query Builder")) + '">',
                '<table width="100%">',
                '<tr>',
                '<td class="bottomborder">',
                '<label for="qbtype">' + _("Type") + '</label>',
                '</td>',
                '<td class="bottomborder">',
                '<select id="qbtype" data="qbtype" class="qb asm-selectbox">',
                '<option value="animal">' + _("Animal") + '</option>',
                '<option value="animalcontrol">' + _("Incident") + '</option>',
                '<option value="animalmedicalcombined">' + _("Medical") + '</option>',
                '<option value="ownerdonation">' + _("Payment") + '</option>',
                '<option value="owner">' + _("Person") + '</option>',
                '<option value="animalwaitinglist">' + _("Waiting List") + '</option>',
                '</select>',
                '</td>',
                '</tr><tr>',
                '<td class="bottomborder">',
                '<label for="qbfields">' + _("Fields") + '</label>',
                '</td>',
                '<td class="bottomborder">',
                '<select id="qbfields" data="qbfields" multiple="multiple" class="qb asm-bsmselect">',
                '</select>',
                '</td>',
                '</tr><tr>',
                '<td class="bottomborder">',
                '<label for="qbcriteria">' + _("Criteria") + '</label>',
                '<span id="callout-criteria" class="asm-callout">',
                _("Records must match all of the selected criteria in order to appear on the report"),
                '</span>',
                '</td>',
                '<td class="bottomborder">',
                '<select id="qbcriteria" data="qbcriteria" multiple="multiple" class="qb asm-bsmselect">',
                '</select>',
                '</td>',
                '</tr><tr>',
                '<td class="bottomborder">',
                '<label for="qbsort">' + _("Sort") + '</label>',
                '</td>',
                '<td class="bottomborder">',
                '<select id="qbsort" data="qbsort" multiple="multiple" class="qb asm-bsmselect">',
                '</select>',
                '</td>',
                '</tr><tr>',
                '<td>',
                '<label for="qbgrp">' + _("Group (optional)") + '</label>',
                '</td>',
                '<td>',
                '<select id="qbgrp" data="qbgrp" class="qb asm-selectbox">',
                '</select>',
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        bind: function() {
            const expand_additional = function(l) {
                // Expands our fake fields that require subqueries (additional fields, some animal medical info, etc)
                let o = [];
                $.each(l, function(i, v) {
                    if (v.indexOf("afc_") == 0) {
                        // Yes/No additional fields
                        o.push("CASE WHEN EXISTS(SELECT Value FROM additional WHERE LinkID=v_" + $("#qbtype").val() + 
                            ".ID AND AdditionalFieldID=" + v.substring(4) + " AND Value='1') THEN '" +
                            _("Yes") + "' ELSE '" + _("No") + "' END AS " + v);
                    }
                    else if (v.indexOf("afa_") == 0) {
                        // Animal link additional fields
                        o.push("(SELECT animal.AnimalName FROM additional " + 
                            "INNER JOIN animal ON animal.ID = CAST(additional.Value AS INTEGER) " +
                            "WHERE LinkID=v_" + $("#qbtype").val() + ".ID AND " +
                            "AdditionalFieldID=" + v.substring(4) + ") AS " + v);
                    }
                    else if (v.indexOf("afp_") == 0) {
                        // Person link additional fields
                        o.push("(SELECT owner.OwnerName FROM additional " + 
                            "INNER JOIN owner ON owner.ID = CAST(additional.Value AS INTEGER) " +
                            "WHERE LinkID=v_" + $("#qbtype").val() + ".ID AND " +
                            "AdditionalFieldID=" + v.substring(4) + ") AS " + v);
                    }
                    else if (v.indexOf("moneyaf_") == 0) {
                        // Money additional fields
                        o.push("(SELECT Value FROM additional WHERE LinkID=v_" + $("#qbtype").val() + 
                            ".ID AND AdditionalFieldID=" + v.substring(8) + ") AS " + v);
                    }
                    else if (v.indexOf("af_") == 0) {
                        // Any other additional fields
                        o.push("(SELECT Value FROM additional WHERE LinkID=v_" + $("#qbtype").val() + 
                            ".ID AND AdditionalFieldID=" + v.substring(3) + ") AS " + v);
                    }
                    else if (v.indexOf("meddate_") == 0) {
                        // Date medical profile given
                        o.push("(SELECT DateGiven FROM animalmedicaltreatment WHERE animalmedicaltreatment.ID = " +
                        "(SELECT MAX(animalmedicaltreatment.ID) FROM animalmedicaltreatment " +
                        "INNER JOIN animalmedical ON animalmedical.ID = animalmedicaltreatment.AnimalMedicalID " +
                        "WHERE DateGiven Is Not Null AND animalmedical.AnimalID=v_animal.ID " + 
                        "AND MedicalProfileID=" + v.substring(8) + ")) AS " + v);
                    }
                    else if (v.indexOf("testdate_") == 0) {
                        // Date test given
                        o.push("(SELECT DateOfTest FROM animaltest WHERE animaltest.ID = " +
                        "(SELECT MAX(ID) FROM animaltest WHERE DateOfTest Is Not Null AND AnimalID=v_animal.ID " + 
                        "AND TestTypeID=" + v.substring(9) + ")) AS " + v);
                    }
                    else if (v.indexOf("testresult_") == 0) {
                        // Test result
                        o.push("(SELECT ResultName FROM animaltest INNER JOIN testresult ON testresult.ID=animaltest.TestResultID " + 
                        "WHERE animaltest.ID = " +
                        "(SELECT MAX(ID) FROM animaltest WHERE DateOfTest Is Not Null AND AnimalID=v_animal.ID " + 
                        "AND TestTypeID=" + v.substring(11) + ")) AS " + v);
                    }
                    else if (v.indexOf("vaccdate_") == 0) {
                        // Date vacc given
                        o.push("(SELECT DateOfVaccination FROM animalvaccination WHERE animalvaccination.ID = " +
                        "(SELECT MAX(ID) FROM animalvaccination WHERE DateOfVaccination Is Not Null AND AnimalID=v_animal.ID " + 
                        "AND VaccinationID=" + v.substring(9) + ")) AS " + v);
                    }
                    else if (v.indexOf("vaccexp") == 0) {
                        // Date vacc expires
                        o.push("(SELECT DateExpires FROM animalvaccination WHERE animalvaccination.ID = " +
                        "(SELECT MAX(ID) FROM animalvaccination WHERE DateOfVaccination Is Not Null AND AnimalID=v_animal.ID " + 
                        "AND VaccinationID=" + v.substring(9) + ")) AS " + v);
                    }
                    else { o.push(v); }
                });
                return o;
            };
            const expand_var_tokens = function(s) {
                // If any tokens are found for special criteria that require VAR tokens, add them
                let tokens = [];
                if (s.indexOf("$@osatdate$") != -1) {
                    tokens.push("$VAR osatdate DATE " + _("On shelter at date") + "$");
                }
                if (s.indexOf("$@osfrom$") != -1) {
                    tokens.push("$VAR osfrom DATE " + _("On shelter between") + "$");
                }
                if (s.indexOf("$@osto$") != -1) {
                    tokens.push("$VAR osto DATE " + _("and") + "$");
                }
                return s + "\n\n" + tokens.join("\n");
            };
            let qbbuttons = {};
            qbbuttons[_("Update")] = function() {
                // Construct the query from the selected values
                let q = "-- " + $(".qb").toPOST() + "&v=1\n";
                if ($("#qbgrp").val()) { q += "-- GRP:" + $("#qbgrp").val() + "\n"; }
                q += "\nSELECT \n " + expand_additional($("#qbfields").val()).join(",\n ");
                q += "\nFROM \n v_" + $("#qbtype").val();
                let critout = [];
                $.each($("#qbcriteria").val(), function(i, v) {
                    $.each(reports_querybuilder.qb_active_criteria, function(ii, vv) {
                        let [ display, value, sql ] = vv;
                        if (v == value) { critout.push(sql); return false; }
                    });
                });
                if (critout.length > 0) { q += "\nWHERE \n " + critout.join("\n AND "); }
                if ($("#qbsort").val().length > 0) { q += "\nORDER BY \n " + $("#qbsort").val().join(",\n "); }
                q = expand_var_tokens(q);
                $("#sql").sqleditor("value", q);
                $(this).dialog("close");
            };
            qbbuttons[_("Cancel")] = function() { $(this).dialog("close"); };
            $("#dialog-qb").dialog({
                autoOpen: false,
                resizable: true,
                height: 600,
                width: 900,
                modal: true,
                dialogClass: "dialogshadow",
                buttons: qbbuttons,
                show: dlgfx.add_show,
                hide: dlgfx.add_hide
            });
            $("#qbtype").change( reports_querybuilder.qb_change_type );
            $("#qbsort").change( reports_querybuilder.qb_change_sort );
            // Build the criteria lists
            reports_querybuilder.qb_animal_criteria = Array.from(QB_ANIMAL_CRITERIA);
            reports_querybuilder.qb_incident_criteria = Array.from(QB_INCIDENT_CRITERIA);
            reports_querybuilder.qb_medical_criteria = Array.from(QB_MEDICAL_CRITERIA);
            reports_querybuilder.qb_payment_criteria = Array.from(QB_PAYMENT_CRITERIA);
            reports_querybuilder.qb_person_criteria = Array.from(QB_PERSON_CRITERIA);
            reports_querybuilder.qb_waitinglist_criteria = Array.from(QB_WAITINGLIST_CRITERIA);
            $.each(controller.additionalfields, function(i, v) {
                if (common.array_in(v.LINKTYPE, ADDITIONAL_ANIMAL)) { 
                    reports_querybuilder.qb_animal_criteria.push(
                        [_("Additional field {0} has a value").replace("{0}", v.FIELDNAME), "af" + v.ID,
                            "EXISTS(SELECT Value FROM additional WHERE AdditionalFieldID=" + v.ID + " AND LinkID=v_animal.ID AND Value<>'' AND Value<>'0')" ]);
                }
                if (common.array_in(v.LINKTYPE, ADDITIONAL_WAITINGLIST)) { 
                    reports_querybuilder.qb_waitinglist_criteria.push(
                        [_("Additional field {0} has a value").replace("{0}", v.FIELDNAME), "af" + v.ID,
                            "EXISTS(SELECT Value FROM additional WHERE AdditionalFieldID=" + v.ID + " AND LinkID=v_animalwaitinglist.ID AND Value<>'' AND Value<>'0')" ]);
                }
                if (common.array_in(v.LINKTYPE, ADDITIONAL_PERSON)) { 
                    reports_querybuilder.qb_person_criteria.push(
                        [_("Additional field {0} has a value").replace("{0}", v.FIELDNAME), "af" + v.ID,
                            "EXISTS(SELECT Value FROM additional WHERE AdditionalFieldID=" + v.ID + " AND LinkID=v_owner.ID AND Value<>'' AND Value<>'0')" ]);
                }
            });
            $.each(controller.additionalfields, function(i, v) {
                if (common.array_in(v.LINKTYPE, ADDITIONAL_ANIMAL)) { 
                    reports_querybuilder.qb_animal_criteria.push(
                        [_("Additional field {0} is blank").replace("{0}", v.FIELDNAME), "naf" + v.ID,
                            "NOT EXISTS(SELECT Value FROM additional WHERE AdditionalFieldID=" + v.ID + " AND LinkID=v_animal.ID AND Value<>'' AND Value<>'0')" ]);
                }
                if (common.array_in(v.LINKTYPE, ADDITIONAL_WAITINGLIST)) { 
                    reports_querybuilder.qb_waitinglist_criteria.push(
                        [_("Additional field {0} is blank").replace("{0}", v.FIELDNAME), "naf" + v.ID,
                            "NOT EXISTS(SELECT Value FROM additional WHERE AdditionalFieldID=" + v.ID + " AND LinkID=v_animalwaitinglist.ID AND Value<>'' AND Value<>'0')" ]);
                }
                if (common.array_in(v.LINKTYPE, ADDITIONAL_PERSON)) { 
                    reports_querybuilder.qb_person_criteria.push(
                        [_("Additional field {0} is blank").replace("{0}", v.FIELDNAME), "naf" + v.ID,
                            "NOT EXISTS(SELECT Value FROM additional WHERE AdditionalFieldID=" + v.ID + " AND LinkID=v_owner.ID AND Value<>'' AND Value<>'0')" ]);
                }
            });
            $.each(controller.additionalfields, function(i, v) {
                if (common.array_in(v.LINKTYPE, ADDITIONAL_ANIMAL)) { 
                    reports_querybuilder.qb_animal_criteria.push(
                        [_("Additional field {0} matches string").replace("{0}", v.FIELDNAME), "straf" + v.ID,
                            "EXISTS(SELECT Value FROM additional WHERE AdditionalFieldID=" + v.ID + " AND LinkID=v_animal.ID AND Value LIKE '%$ASK STRING " + v.FIELDNAME + " contains $%')" ]);
                }
                if (common.array_in(v.LINKTYPE, ADDITIONAL_WAITINGLIST)) { 
                    reports_querybuilder.qb_waitinglist_criteria.push(
                        [_("Additional field {0} matches string").replace("{0}", v.FIELDNAME), "straf" + v.ID,
                            "EXISTS(SELECT Value FROM additional WHERE AdditionalFieldID=" + v.ID + " AND LinkID=v_animalwaitinglist.ID AND Value LIKE '%$ASK STRING " + v.FIELDNAME + " contains $%')" ]);
                }
                if (common.array_in(v.LINKTYPE, ADDITIONAL_PERSON)) { 
                    reports_querybuilder.qb_person_criteria.push(
                        [_("Additional field {0} matches string").replace("{0}", v.FIELDNAME), "straf" + v.ID,
                            "EXISTS(SELECT Value FROM additional WHERE AdditionalFieldID=" + v.ID + " AND LinkID=v_owner.ID AND Value LIKE '%$ASK STRING " + v.FIELDNAME + " contains $%')" ]);
                }
            });
            $.each(controller.additionalfields, function(i, v) {
                // date format to use with asm_to_date
                let dformat = asm.dateformat.replace("%Y", "YYYY").replace("%m", "MM").replace("%d", "DD");
                dformat = "'" + dformat + "'";
                if (common.array_in(v.LINKTYPE, ADDITIONAL_ANIMAL) && v.FIELDTYPE == 4) { 
                    reports_querybuilder.qb_animal_criteria.push(
                        [_("Additional field {0} is between two dates").replace("{0}", v.FIELDNAME), "daf" + v.ID,
                            "EXISTS(SELECT Value FROM additional WHERE AdditionalFieldID=" + v.ID + " " +
                            "AND LinkID=v_animal.ID AND asm_to_date(Value, " + dformat + ") >= '$ASK DATE From date $' " +
                            "AND asm_to_date(Value, " + dformat + ") <= '$ASK DATE To date $')" ]);
                }
                if (common.array_in(v.LINKTYPE, ADDITIONAL_WAITINGLIST) && v.FIELDTYPE == 4) { 
                    reports_querybuilder.qb_waitinglist_criteria.push(
                        [_("Additional field {0} is between two dates").replace("{0}", v.FIELDNAME), "daf" + v.ID,
                            "EXISTS(SELECT Value FROM additional WHERE AdditionalFieldID=" + v.ID + " " +
                            "AND LinkID=v_animalwaitinglist.ID AND asm_to_date(Value, " + dformat + ") >= '$ASK DATE From date $' " +
                            "AND asm_to_date(Value, " + dformat + ") <= '$ASK DATE To date $')" ]);
                }
                if (common.array_in(v.LINKTYPE, ADDITIONAL_PERSON) && v.FIELDTYPE == 4) { 
                    reports_querybuilder.qb_person_criteria.push(
                        [_("Additional field {0} is between two dates").replace("{0}", v.FIELDNAME), "daf" + v.ID,
                            "EXISTS(SELECT Value FROM additional WHERE AdditionalFieldID=" + v.ID + " " +
                            "AND LinkID=v_owner.ID AND asm_to_date(Value, " + dformat + ") >= '$ASK DATE From date $' " +
                            "AND asm_to_date(Value, " + dformat + ") <= '$ASK DATE To date $')" ]);
                }
            });
            $.each(controller.entryreasons, function(i, v) {
                reports_querybuilder.qb_animal_criteria.push(
                    [_("Entry category is {0}").replace("{0}", v.REASONNAME), "entryreason" + v.ID, "EntryReasonID=" + v.ID]);
            });
            $.each(controller.animalflags, function(i, v) {
                reports_querybuilder.qb_animal_criteria.push(
                    [_("Flag {0}").replace("{0}", v.FLAG), "flag" + v.ID, "AdditionalFlags LIKE '%" + v.FLAG + "%'" ]);
                reports_querybuilder.qb_animal_criteria.push(
                    [_("Flag missing {0}").replace("{0}", v.FLAG), "flagnot" + v.ID, "AdditionalFlags NOT LIKE '%" + v.FLAG + "%'" ]);
            });
            $.each(controller.personflags, function(i, v) {
                reports_querybuilder.qb_person_criteria.push(
                    [_("Flag {0}").replace("{0}", v.FLAG), "flag" + v.ID, "AdditionalFlags LIKE '%" + v.FLAG + "%'" ]);
                reports_querybuilder.qb_person_criteria.push(
                    [_("Flag missing {0}").replace("{0}", v.FLAG), "flagnot" + v.ID, "AdditionalFlags NOT LIKE '%" + v.FLAG + "%'" ]);
            });
            $.each(controller.jurisdictions, function(i, v) {
                reports_querybuilder.qb_animal_criteria.push(
                    [_("Jurisdiction is {0}").replace("{0}", v.JURISDICTIONNAME), "jurisdiction" + v.ID, "JurisdictionID=" + v.ID]);
                reports_querybuilder.qb_incident_criteria.push(
                    [_("Jurisdiction is {0}").replace("{0}", v.JURISDICTIONNAME), "jurisdiction" + v.ID, "JurisdictionID=" + v.ID]);
                reports_querybuilder.qb_person_criteria.push(
                    [_("Jurisdiction is {0}").replace("{0}", v.JURISDICTIONNAME), "jurisdiction" + v.ID, "JurisdictionID=" + v.ID]);
            });
            $.each(controller.incidenttypes, function(i, v) {
                reports_querybuilder.qb_incident_criteria.push(
                    [_("Type is {0}").replace("{0}", v.INCIDENTNAME), "incident" + v.ID, "IncidentTypeID=" + v.ID]);
            });
            reports_querybuilder.qb_medical_criteria.push(
                [_("Type is {0}").replace("{0}", _("Vaccination")), "medical-1", "MedicalTypeID=-1"]);
            reports_querybuilder.qb_medical_criteria.push(
                [_("Type is {0}").replace("{0}", _("Test")), "medical-2", "MedicalTypeID=-2"]);
            $.each(controller.medicaltypes, function(i, v) {
                reports_querybuilder.qb_medical_criteria.push(
                    [_("Type is {0}").replace("{0}", v.MEDICALTYPENAME), "medical" + v.ID, "MedicalTypeID=" + v.ID]);
            });
            $.each(controller.completedtypes, function(i, v) {
                reports_querybuilder.qb_incident_criteria.push(
                    [_("Completed type {0}").replace("{0}", v.COMPLETEDNAME), "completed" + v.ID, "IncidentCompletedID=" + v.ID]);
            });
            $.each(controller.donationtypes, function(i, v) {
                reports_querybuilder.qb_payment_criteria.push(
                    [_("Payment type {0}").replace("{0}", v.DONATIONNAME), "paymenttype" + v.ID, "DonationTypeID=" + v.ID]);
            });
            $.each(controller.paymentmethods, function(i, v) {
                reports_querybuilder.qb_payment_criteria.push(
                    [_("Payment method {0}").replace("{0}", v.PAYMENTNAME), "paymentmethod" + v.ID, "DonationPaymentID=" + v.ID]);
            });
            $.each(controller.locations, function(i, v) {
                reports_querybuilder.qb_animal_criteria.push(
                    [_("Location is {0}").replace("{0}", v.LOCATIONNAME), "location" + v.ID, "ShelterLocation=" + v.ID]);
            });
            $.each(controller.sizes, function(i, v) {
                reports_querybuilder.qb_animal_criteria.push(
                    [_("Size is {0}").replace("{0}", v.SIZE), "size" + v.ID, "Size=" + v.ID]);
            });
            $.each(controller.species, function(i, v) {
                reports_querybuilder.qb_animal_criteria.push(
                    [_("Species is {0}").replace("{0}", v.SPECIESNAME), "species" + v.ID, "SpeciesID=" + v.ID]);
                reports_querybuilder.qb_waitinglist_criteria.push(
                    [_("Species is {0}").replace("{0}", v.SPECIESNAME), "species" + v.ID, "SpeciesID=" + v.ID]);
            });
            $.each(controller.testtypes, function(i, v) {
                reports_querybuilder.qb_animal_criteria.push(
                    [_("Test performed {0}").replace("{0}", v.TESTNAME), "test" + v.ID, 
                        "EXISTS(SELECT ID FROM animaltest WHERE DateOfTest Is Not Null AND " +
                        "AnimalID=v_animal.ID AND TestTypeID=" + v.ID + ")"]);
            });
            $.each(controller.testtypes, function(i, v) {
                reports_querybuilder.qb_animal_criteria.push(
                    [_("Test not performed {0}").replace("{0}", v.TESTNAME), "nottest" + v.ID, 
                        "NOT EXISTS(SELECT ID FROM animaltest WHERE DateOfTest Is Not Null AND " +
                        "AnimalID=v_animal.ID AND TestTypeID=" + v.ID + ")"]);
            });
            $.each(controller.testtypes, function(i, v) {
                reports_querybuilder.qb_animal_criteria.push(
                    [_("Test due {0}").replace("{0}", v.TESTNAME), "testdue" + v.ID, 
                        "EXISTS(SELECT ID FROM animaltest WHERE DateOfTest Is Null AND " +
                        "DateRequired>='$ASK DATE {0}$' AND DateRequired<='$ASK DATE {1}$'" + 
                        "AND AnimalID=v_animal.ID AND TestTypeID=" + v.ID + ")"
                        .replace("{0}", _("Test due between"))
                        .replace("{1}", _("and"))
                    ]);
            });
            $.each(controller.animaltypes, function(i, v) {
                reports_querybuilder.qb_animal_criteria.push(
                    [_("Type is {0}").replace("{0}", v.ANIMALTYPE), "animaltype" + v.ID, "AnimalTypeID=" + v.ID]);
            });
            $.each(controller.urgencies, function(i, v) {
                reports_querybuilder.qb_waitinglist_criteria.push(
                    [_("Urgency is {0}").replace("{0}", v.URGENCY), "urgency" + v.ID, "Urgency=" + v.ID]);
            });
            $.each(controller.vaccinationtypes, function(i, v) {
                reports_querybuilder.qb_animal_criteria.push(
                    [_("Vaccination given {0}").replace("{0}", v.VACCINATIONTYPE), "vacc" + v.ID, 
                        "EXISTS(SELECT ID FROM animalvaccination WHERE DateOfVaccination Is Not Null AND " +
                        "AnimalID=v_animal.ID AND VaccinationID=" + v.ID + ")"]);
            });
            $.each(controller.vaccinationtypes, function(i, v) {
                reports_querybuilder.qb_animal_criteria.push(
                    [_("Vaccination not given {0}").replace("{0}", v.VACCINATIONTYPE), "notvacc" + v.ID, 
                        "NOT EXISTS(SELECT ID FROM animalvaccination WHERE DateOfVaccination Is Not Null AND " +
                        "AnimalID=v_animal.ID AND VaccinationID=" + v.ID + ")"]);
            });
            $.each(controller.vaccinationtypes, function(i, v) {
                reports_querybuilder.qb_animal_criteria.push(
                    [_("Vaccination due {0}").replace("{0}", v.VACCINATIONTYPE), "vaccdue" + v.ID, 
                        "EXISTS(SELECT ID FROM animalvaccination WHERE DateOfVaccination Is Null AND " +
                        "DateRequired>='$ASK DATE {0}$' AND DateRequired<='$ASK DATE {1}$'" + 
                        "AND AnimalID=v_animal.ID AND VaccinationID=" + v.ID + ")"
                        .replace("{0}", _("Vaccination due between"))
                        .replace("{1}", _("and"))
                    ]);
            });
        },

        /** Called when the sort is changed in the querybuilder dialog */
        qb_change_sort: function() {
            let groups = [ "" ];
            let cgroups = [];
            let sorts = $("#qbsort").val();
            $.each( String(sorts).split(","), function(i, v) {
                cgroups.push(v);
                groups.push(cgroups.join(","));
            });
            $("#qbgrp").html( html.list_to_options(groups) );
        },

        /** Called when the data type is changed in the querybuilder dialog */
        qb_change_type: function() {
            let type = $("#qbtype").val();
            const build_criteria = function(l) {
                // Outputs criteria into the dropdown. l is the list of criteria reports_querybuilder.qb_x_criteria
                let crit = [];
                $.each(l, function(i, v) {
                    let [ display, value, sql ] = v, hasask = "";
                    if (sql.indexOf("$ASK") != -1 || sql.indexOf("$@") != -1) { hasask = " *"; }
                    crit.push( value + "|" + display + hasask );
                });
                return crit;
            };
            const get_additional = function(t) {
                // Returns a list of additional field names for the type ready for the dropdowns
                let f = [];
                $.each(controller.additionalfields, function(i, v) {
                    if ( (t == "animal" && common.array_in(v.LINKTYPE, ADDITIONAL_ANIMAL)) ||
                        (t == "animalwaitinglist" && common.array_in(v.LINKTYPE, ADDITIONAL_WAITINGLIST)) ||
                        (t == "owner" && common.array_in(v.LINKTYPE, ADDITIONAL_PERSON)) ||
                        (t == "animalcontrol" && common.array_in(v.LINKTYPE, ADDITIONAL_INCIDENT)) ) {
                        // Use different prefixes to indicate the additional field type for
                        // expansion into different query types later
                        if (v.FIELDTYPE == 0) {
                            f.push("afc_" + v.ID + "|" + v.FIELDNAME); // Yes/No (checkbox 1/0)
                        }
                        else if (v.FIELDTYPE == 5) {
                            f.push("moneyaf_" + v.ID + "|" + v.FIELDNAME); // Money (whole pence)
                        }
                        else if (v.FIELDTYPE == 8) {
                            f.push("afa_" + v.ID + "|" + v.FIELDNAME); // Animal link (contains animal ID)
                        }
                        else if (v.FIELDTYPE == 9 || v.FIELDTYPE == 11 || v.FIELDTYPE ==  12) {
                            f.push("afp_" + v.ID + "|" + v.FIELDNAME); // Person link (contains person ID)
                        }

                        else {
                            f.push("af_" + v.ID + "|" + v.FIELDNAME); 
                        }
                    }
                });
                return f;
            };
            const get_animal_medical = function() {
                // Returns a list of extra animal medical values for the fields dropdown
                let f = [];
                $.each(controller.medicalprofiles, function(i, v) {
                    f.push("meddate_" + v.ID + "|" + _("{0} medical profile administered").replace("{0}", v.PROFILENAME));
                });
                $.each(controller.testtypes, function(i, v) {
                    f.push("testdate_" + v.ID + "|" + _("{0} test performed date").replace("{0}", v.TESTNAME));
                    f.push("testresult_" + v.ID + "|" + _("{0} test result").replace("{0}", v.TESTNAME));
                });
                $.each(controller.vaccinationtypes, function(i, v) {
                    f.push("vaccdate_" + v.ID + "|" + _("{0} vaccination given date").replace("{0}", v.VACCINATIONTYPE));
                    f.push("vaccexp_" + v.ID + "|" + _("{0} vaccination expiry date").replace("{0}", v.VACCINATIONTYPE));
                });
                return f;
            };
            if (type == "animal") {
                $("#qbfields").html(html.list_to_options(common.get_table_columns("v_animal").concat(get_additional(type)).concat(get_animal_medical())));
                $("#qbsort").html(html.list_to_options(common.get_table_columns("v_animal").concat(get_additional(type)).concat(get_animal_medical())));
                $("#qbcriteria").html(html.list_to_options(build_criteria(reports_querybuilder.qb_animal_criteria)));
                $("#qbfields").change();
                $("#qbsort").change();
                $("#qbcriteria").change();
                reports_querybuilder.qb_active_criteria = reports_querybuilder.qb_animal_criteria;
            }
            else if (type == "animalcontrol") {
                $("#qbfields").html(html.list_to_options(common.get_table_columns("v_animalcontrol").concat(get_additional(type))));
                $("#qbsort").html(html.list_to_options(common.get_table_columns("v_animalcontrol").concat(get_additional(type))));
                $("#qbcriteria").html(html.list_to_options(build_criteria(reports_querybuilder.qb_incident_criteria)));
                $("#qbfields").change();
                $("#qbsort").change();
                $("#qbcriteria").change();
                reports_querybuilder.qb_active_criteria = reports_querybuilder.qb_incident_criteria;
            }
            else if (type == "animalmedicalcombined") {
                $("#qbfields").html(html.list_to_options(common.get_table_columns("v_animalmedicalcombined")));
                $("#qbsort").html(html.list_to_options(common.get_table_columns("v_animalmedicalcombined")));
                $("#qbcriteria").html(html.list_to_options(build_criteria(reports_querybuilder.qb_medical_criteria)));
                $("#qbfields").change();
                $("#qbsort").change();
                $("#qbcriteria").change();
                reports_querybuilder.qb_active_criteria = reports_querybuilder.qb_medical_criteria;
            }
            else if (type == "animalwaitinglist") {
                $("#qbfields").html(html.list_to_options(common.get_table_columns("v_animalwaitinglist").concat(get_additional(type))));
                $("#qbsort").html(html.list_to_options(common.get_table_columns("v_animalwaitinglist").concat(get_additional(type))));
                $("#qbcriteria").html(html.list_to_options(build_criteria(reports_querybuilder.qb_waitinglist_criteria)));
                $("#qbfields").change();
                $("#qbsort").change();
                $("#qbcriteria").change();
                reports_querybuilder.qb_active_criteria = reports_querybuilder.qb_waitinglist_criteria;
            }
            else if (type == "owner") {
                $("#qbfields").html(html.list_to_options(common.get_table_columns("v_owner").concat(get_additional(type))));
                $("#qbsort").html(html.list_to_options(common.get_table_columns("v_owner").concat(get_additional(type))));
                $("#qbcriteria").html(html.list_to_options(build_criteria(reports_querybuilder.qb_person_criteria)));
                $("#qbfields").change();
                $("#qbsort").change();
                $("#qbcriteria").change();
                reports_querybuilder.qb_active_criteria = reports_querybuilder.qb_person_criteria;
            }
            else if (type == "ownerdonation") {
                $("#qbfields").html(html.list_to_options(common.get_table_columns("v_ownerdonation")));
                $("#qbsort").html(html.list_to_options(common.get_table_columns("v_ownerdonation")));
                $("#qbcriteria").html(html.list_to_options(build_criteria(reports_querybuilder.qb_payment_criteria)));
                $("#qbfields").change();
                $("#qbsort").change();
                $("#qbcriteria").change();
                reports_querybuilder.qb_active_criteria = reports_querybuilder.qb_payment_criteria;
            }
        },

        /** Called when the query builder button is clicked to show the dialog */
        qb_click: function() {
            const set_values = function(s, v) {
                if (!v || !s) { return; }
                let n = $(s);
                // We count the selected items in reverse and prepend them
                // to the beginning of the list each time, this way we
                // retain the order chosen by the user.
                $.each(v.split("%2C").reverse(), function(mi, mv) {
                    let opt = n.find("[value='" + mv + "']");
                    opt.prop("selected", true);
                    n.prepend(opt);
                });
                n.change();
            };
            // Load existing values by searching for a comment at the beginning of the query
            let enc = $("#sql").sqleditor("value");
            if (enc.indexOf("-- ") == 0) {
                $("#qbtype").val( common.url_param(enc, "qbtype") ); 
                reports_querybuilder.qb_change_type();
                set_values("#qbfields", common.url_param(enc, "qbfields"));
                set_values("#qbcriteria", common.url_param(enc, "qbcriteria"));
                set_values("#qbsort", common.url_param(enc, "qbsort"));
                set_values("#qbgrp", common.url_param(enc, "qbgrp"));
            }
            else {
                $("#qbtype").val("animal");
                reports_querybuilder.qb_change_type();
                reports_querybuilder.qb_change_sort();
            }
            $("#dialog-qb").dialog("open");
        },

        name: "reports_querybuilder",
        routes: {}, // this module has its methods called from reports.js instead of standing alone
        title: ""
    };

    common.module_register(reports_querybuilder);

});