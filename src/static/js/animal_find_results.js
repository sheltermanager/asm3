/*global $, _, asm, additional, common, config, controller, edit_header, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const animal_find_results = {

        render: function() {
            return [
                html.content_header(_("Results")),
                '<div id="asm-results">',
                '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-search"></span>',
                _("Search returned {0} results.").replace("{0}", controller.rows.length),
                controller.wasonshelter ? "<br />" + _("You didn't specify any search criteria, so an on-shelter search was assumed.") : "",
                '</p>',
                '</div>',
                '<table id="table-searchresults">',
                animal_find_results.render_tablehead(),
                '<tbody>',
                animal_find_results.render_tablebody(),
                '</tbody>',
                '</table>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        /**
         * Renders the table.head tag with columns in the right order
         */
        render_tablehead: function() {
            const labels = animal_find_results.column_labels();
            let s = [];
            s.push("<thead>");
            s.push("<tr>");
            $.each(labels, function(i, label) {
                s.push("<th>" + label + "</th>");
            });
            s.push("</tr>");
            s.push("</thead>");
            return s.join("\n");
        },

        /**
         * Renders the table body with columns in the right order and
         * highlighting styling applied, etc.
         */
        render_tablebody: function() {
            let h = [];
            $.each(controller.rows, function(ir, row) {
                h.push("<tr>");
                $.each(animal_find_results.column_names(), function(ic, name) {
                    // Style the whole row if the animal is deceased
                    if (row.DECEASEDDATE) { h.push('<td class="asm-search-deceased">'); } else { h.push("<td>"); }
                    let value = "";
                    if (row.hasOwnProperty(name.toUpperCase())) {
                        value = row[name.toUpperCase()];
                    }
                    let formatted = animal_find_results.format_column(row, name, value, controller.additional);
                    if (name == "AnimalName") {
                        formatted = '<span style="white-space: nowrap">' +
                            '<a id="action-' + row.ID + '" href="animal?id="' + row.ID + '">' + formatted + '</a>' +
                            '<span data-sort="' + html.title(formatted)  + '"></span> ' + 
                            html.animal_emblems(row) + '</span>';
                    }
                    h.push(formatted);
                    h.push("</td>");
                });
                h.push("</tr>");
            });
            return h.join("\n");
        },


        bind: function() {
            $("#table-searchresults").table();
        },

        sync: function() {
            // retrigger the sort
            $("#table-searchresults").trigger("sorton", [[[0,0]]]);
        },

        /** 
         * Returns a list of our configured viewable column names
         */
        column_names: function() {
            let cols = [];
            $.each(config.str("SearchColumns").split(","), function(i, v) {
                cols.push(common.trim(v));
            });
            // If AnimalName is not present in the list, insert it as the first column to make
            // sure there's still a link displayed to the target record
            if (!common.array_in("AnimalName", cols)) { cols.unshift("AnimalName"); } 
            return cols;
        },

        /**
         * Returns a list of our configured viewable column labels
         */
        column_labels: function() {
            const names = animal_find_results.column_names();
            let labels = [];
            $.each(names, function(i, name) {
                labels.push(animal_find_results.column_label(name, controller.additional));
            });
            return labels;
        },

        /**
         * Returns the number of configured viewable columns
         */
        column_count: function() {
            return animal_find_results.column_names().length;
        },

        /**
         * Returns the i18n translated label for a column with name
         * add: Additional fields to scan for labels
         */
        column_label: function(name, add) {
            const labels = {
                "Adoptable": _("Adoptable"),
                "AnimalTypeID": _("Type"),
                "AnimalName": _("Name"),
                "BaseColourID": _("Color"),
                "CreatedBy": _("Created By"),
                "SpeciesID": _("Species"),
                "BreedName":  _("Breed"),
                "CoatType":  _("Coat Type"),
                "Markings":  _("Features"),
                "ShelterCode":  _("Code"),
                "AcceptanceNumber":  _("Litter Ref"),
                "DateOfBirth":  _("Date Of Birth"),
                "AgeGroup":  _("Age"),
                "AnimalAge":  _("Age"),
                "DeceasedDate":  _("Died"),
                "Sex":  _("Sex"),
                "IdentichipNumber":  _("Microchip"),
                "IdentichipDate":  _("Date"),
                "TattooNumber":  _("Tattoo"),
                "TattooDate":  _("Tattoo"),
                "Neutered":  _("Altered"),
                "NeuteredDate":  _("Altered"),
                "CombiTested":  _("FIV/L Tested"),
                "CombiTestDate":  _("FIV/L Tested"),
                "CombiTestResult":  _("FIV"),
                "FLVResult":  _("FLV"),
                "HeartwormTested":  _("Heartworm Tested"),
                "HeartwormTestDate":  _("Heartworm Tested"),
                "HeartwormTestResult":  _("Heartworm"),
                "Declawed":  _("Declawed"),
                "HiddenAnimalDetails":  _("Hidden"),
                "AnimalComments":  _("Description"),
                "ReasonForEntry":  _("Entry Reason"),
                "ReasonNO":  _("Reason Not From Owner"),
                "DateBroughtIn":  _("Brought In"),
                "EntryReasonID":  _("Entry Reason"),
                "HealthProblems":  _("Health Problems"),
                "ActiveDietName": _("Diet"),
                "PTSReason":  _("Euthanized"),
                "PTSReasonID":  _("Euthanized"),
                "IsGoodWithCats":  _("Good with Cats"),
                "IsGoodWithDogs":  _("Good with Dogs"),
                "IsGoodWithChildren":  _("Good with Children"),
                "IsHouseTrained":  _("Housetrained"),
                "IsNotAvailableForAdoption":  _("Not Available for Adoption"),
                "IsHold":  _("Hold"),
                "HoldUntilDate": _("Hold until"),
                "IsPickup": _("Picked Up"),
                "PickupAddress": _("Pickup Address"),
                "PickupLocationID": _("Pickup Location"), 
                "JurisdictionID": _("Jurisdiction"),
                "IsQuarantine":  _("Quarantine"),
                "HasSpecialNeeds":  _("Special Needs"),
                "AdditionalFlags": _("Flags"),
                "ShelterLocation":  _("Location"),
                "ShelterLocationUnit":  _("Unit"),
                "AdoptionCoordinatorID": _("Coordinator"),
                "Fosterer": _("Fosterer"),
                "OwnerID": _("Owner"),
                "Size":  _("Size"),
                "RabiesTag":  _("RabiesTag"),
                "TimeOnShelter":  _("On Shelter"),
                "DaysOnShelter":  _("On Shelter"),
                "HasActiveReserve": _("Reserved"),
                "Image": _("Image")
            };
            if (labels.hasOwnProperty(name)) {
                return labels[name];
            }
            if (add) {
                let addrow = common.get_row(add, name, "FIELDNAME");
                if (addrow) { return addrow.FIELDLABEL; }
            }
            return name;
        },

        /**
         * Returns a formatted column
         * row: A row from the get_waitinglist query
         * name: The name of the column
         * value: The value of the row/column to format from the resultset
         * add: The additional row results
         */
        format_column: function(row, name, value, add) {
            const DATE_FIELDS = [ "DateOfBirth", "DeceasedDate", "IdentichipDate", "TattooDate", 
                "NeuteredDate", "CombiTestDate", "HeartwormTestDate", "DateBroughtIn", "HoldUntilDate" ];
            const STRING_FIELDS = [ "AnimalName", "BreedName", "CreatedBy", "AcceptanceNumber", 
                "ActiveDietName", "AgeGroup", "IdentichipNumber", "TattooNumber", "PickupAddress", 
                "RabiesTag", "DaysOnShelter", "ShelterLocationUnit" ];
            const COMMENT_FIELDS = [ "AnimalComments", "Markings", "ReasonForEntry", "HiddenAnimalDetails", "HealthProblems", "PTSReason" ];
            const YES_NO_UNKNOWN_FIELDS = [ "IsGoodWithCats", "IsGoodWithDogs", "IsGoodWithChildren",
                "IsHouseTrained" ];
            const YES_NO_FIELDS = [ "Neutered", "CombiTested", "HeartwormTested", "Declawed", 
                "HasActiveReserve", "HasSpecialNeeds", "IsHold", "IsNotAvailableForAdoption", "IsPickup", "IsQuarantine" ];
            const POS_NEG_UNKNOWN_FIELDS = [ "CombiTestResult", "FLVResult", "HeartwormTestResult" ];
            let rv = "";
            if (name == "Adoptable") {
                let isa = html.is_animal_adoptable(row);
                rv = '<span class="' + (isa[0] ? "asm-search-adoptable" : "asm-search-notforadoption") + '">' +
                    isa[1] + '</span>';
            }
            else if (name == "OwnerID") { rv = html.person_link(row.OWNERID, row.OWNERNAME); }
            else if (name == "AdoptionCoordinatorID") { rv = html.person_link(row.ADOPTIONCOORDINATORID, row.ADOPTIONCOORDINATORNAME); }
            else if (name == "AnimalTypeID") { rv = row.ANIMALTYPENAME; }
            else if ( name == "BaseColourID") { rv = row.BASECOLOURNAME; }
            else if ( name == "SpeciesID") { rv = row.SPECIESNAME; }
            else if ( name == "CoatType") { rv = row.COATTYPENAME; }
            else if ( name == "Sex") { rv = row.SEXNAME; }
            else if ( name == "EntryReasonID") { rv = row.ENTRYREASONNAME; }
            else if ( name == "PickupLocationID") { rv = row.PICKUPLOCATIONNAME; }
            else if ( name == "JurisdictionID") { rv = row.JURISDICTIONNAME; }
            else if ( name == "PTSReasonID") { rv = row.DECEASEDDATE ? row.PTSREASONNAME : ""; }
            else if ( name == "AnimalAge") {
                rv  = '<span data-sort="' + row.DATEOFBIRTH + '"></span>' + row.ANIMALAGE;
            }
            else if ( name == "TimeOnShelter") {
                rv  = '<span data-sort="' + row.DAYSONSHELTER + '"></span>' + row.TIMEONSHELTER;
            }
            else if ( name == "ShelterLocation") { 
                rv = row.DISPLAYLOCATIONNAME; 
                if (row.SHELTERLOCATIONUNIT && !row.ACTIVEMOVEMENTID) {
                    rv += ' <span class="asm-search-locationunit">' + row.SHELTERLOCATIONUNIT + '</span>';
                }
                if (row.NONSHELTERANIMAL == 1) { 
                    rv = "";
                }
            }
            else if ( name == "Fosterer" ) {
                if (row.ACTIVEMOVEMENTTYPE == 2) {
                    rv = html.person_link(row.CURRENTOWNERID, row.CURRENTOWNERNAME);
                }
            }
            else if ( name == "AdditionalFlags") {
                rv = edit_header.animal_flags(row);
            }
            else if ( name == "Size") { rv = row.SIZENAME; }
            else if ( name == "Weight") { 
                if (config.bool("ShowWeightInLbs")) {
                    let kg = format.to_float(row.WEIGHT),
                        lb = format.to_int(row.WEIGHT),
                        oz = (kg - lb) * 16.0;
                    rv = lb + " lb, " + oz + " oz";
                }
                else if (config.bool("ShowWeightInLbsFraction")) {
                    rv = row.WEIGHT + " lb";
                }
                else {
                    rv = row.WEIGHT + " kg";
                }
            }
            else if ( name == "ShelterCode") { rv = row.CODE; }
            else if ( name == "IdentichipNumber") { rv = common.nulltostr(row.IDENTICHIPNUMBER) + " " + common.nulltostr(row.IDENTICHIP2NUMBER); }
            else if ($.inArray(name, DATE_FIELDS) > -1) {
                rv = format.date(value);
                if (format.time(value) != "00:00:00") {
                    rv += " " + format.time(value);
                }
            }
            else if ($.inArray(name, STRING_FIELDS) > -1) {
                rv = value;
            }
            else if ($.inArray(name, COMMENT_FIELDS) > -1) {
                rv = html.truncate(value);
            }
            else if ($.inArray(name, YES_NO_FIELDS) > -1) {
                if (value == 0) { rv = _("No"); }
                if (value == 1) { rv = _("Yes"); }
            }
            else if ($.inArray(name, YES_NO_UNKNOWN_FIELDS) > -1) {
                if (value == 0) { rv = _("Yes"); }
                else if (value == 1) { rv = _("No"); }
                else { rv = _("Unknown"); }
            }
            else if ($.inArray(name, POS_NEG_UNKNOWN_FIELDS) > -1) {
                if (value == 1) { rv = _("Negative"); }
                else if (value == 2) { rv = _("Positive"); }
                else { rv = _("Unknown"); }
            }
            else if ( name == "Image" ) {
                rv = html.animal_link_thumb_bare(row);
            }
            else if (add) {
                $.each(add, function(i, v) {
                    if (v.LINKID == row.ID && v.FIELDNAME.toLowerCase() == name.toLowerCase()) {
                        if (v.FIELDTYPE == additional.YESNO) { 
                            rv = v.VALUE == "1" ? _("Yes") : _("No");
                        }
                        else if (v.FIELDTYPE == additional.MONEY) {
                            rv = format.currency(v.VALUE);
                        }
                        else if (v.FIELDTYPE == additional.ANIMAL_LOOKUP) {
                            rv = '<a href="animal?id=' + v.VALUE + '">' + v.ANIMALNAME + '</a>';
                        }
                        else if (additional.is_person_type(v.FIELDTYPE)) {
                            rv = html.person_link(v.VALUE, v.OWNERNAME);
                        }
                        else {
                            rv = v.VALUE;
                        }
                        return false; // break
                    }
                });
            }
            return rv;
        },

        name: "animal_find_results",
        animation: "results",
        autofocus: "#asm-content a:first", 
        title: function() { return _("Results"); },
        routes: {
            "animal_find_results": function() {
                common.module_loadandstart("animal_find_results", "animal_find_results?" + this.rawqs);
            }
        }

    };

    common.module_register(animal_find_results);

});
