/*global $, jQuery, _, asm, additional, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    "use strict";

    const person_find_results = {

        render: function() {
            return [
                html.content_header(_("Results")),
                '<div id="asm-results">',
                '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-search"></span>',
                _("Search returned {0} results.").replace("{0}", controller.rows.length),
                '</p>',
                '</div>',
                '<table id="table-searchresults">',
                person_find_results.render_tablehead(),
                '<tbody>',
                person_find_results.render_tablebody(),
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
            let labels = person_find_results.column_labels();
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
                $.each(person_find_results.column_names(), function(ic, name) {

                    // Generate the person selector
                    let link = "<span style=\"white-space: nowrap\"><a id=\"action-" + row.ID + "\" href=\"person?id=" + row.ID + "\">";
                    h.push("<td>");
                    let value = "";
                    if (row.hasOwnProperty(name.toUpperCase())) {
                        value = row[name.toUpperCase()];
                    }
                    let formatted = person_find_results.format_column(row, name, value, controller.additional);
                    if (name == "OwnerName") { 
                        if (common.trim(value) == "") { 
                            formatted += _("(blank)"); 
                        }
                        formatted = link + formatted + "</a></span>";
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
            $.each(config.str("OwnerSearchColumns").split(","), function(i, v) {
                cols.push(common.trim(v));
            });
            // If OwnerName is not present in the list, insert it as the first column to make
            // sure there's still a link displayed to the target record
            if (!common.array_in("OwnerName", cols)) { cols.unshift("OwnerName"); } 
            return cols;
        },

        /**
         * Returns a list of our configured viewable column labels
         */
        column_labels: function() {
            let names = person_find_results.column_names();
            let labels = [];
            $.each(names, function(i, name) {
                labels.push(person_find_results.column_label(name, controller.additional));
            });
            return labels;
        },

        /**
         * Returns the number of configured viewable columns
         */
        column_count: function() {
            return person_find_results.column_names().length;
        },

        /**
         * Returns the i18n translated label for a column with name
         * add: Additional fields to scan for labels
         */
        column_label: function(name, add) {
            let labels = {
                "CreatedBy": _("Created By"),
                "CreatedDate": _("Created Date"),
                "OwnerTitle":  _("Title"),
                "OwnerInitials":  _("Initials"),
                "OwnerForenames":  _("Forenames"),
                "OwnerSurname":  _("Surname"),
                "OwnerName":  _("Name"),
                "OwnerAddress":  _("Address"),
                "OwnerTown":  _("City"),
                "OwnerCounty":  _("State"),
                "OwnerPostcode":  _("Zipcode"),
                "HomeTelephone":  _("Home Phone"),
                "WorkTelephone":  _("Work Phone"),
                "MobileTelephone":  _("Cell Phone"),
                "EmailAddress":  _("Email"),
                "IDCheck":  _("Homechecked"),
                "Jurisdiction": _("Jurisdiction"),
                "Comments":  _("Comments"),
                "IsBanned":  _("Banned"),
                "IsVolunteer":  _("Volunteer"),
                "IsHomeChecker":  _("Homechecker"),
                "IsMember":  _("Member"),
                "MembershipExpiryDate":  _("Expiry"),
                "MembershipNumber":  _("Number"),
                "IsDonor":  _("Donor"),
                "IsShelter":  _("Shelter"),
                "IsACO":  _("ACO"),
                "IsStaff":  _("Staff"),
                "IsFosterer":  _("Fosterer"),
                "IsRetailer":  _("Retailer"),
                "IsVet":  _("Vet"),
                "IsGiftAid":  _("GiftAid"),
                "AdditionalFlags": _("Flags"),
                "FosterCapacity": _("Foster Capacity"), 
                "LookingForSummary": _("Looking For"),
                "HomeCheckAreas":  _("Areas"),
                "DateLastHomeChecked":  _("Homechecked"),
                "HomeCheckedBy":  _("Checked By")
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
            const DATE_FIELDS = [ "CreatedDate", "MembershipExpiryDate", "DateLastHomeChecked" ];
            const STRING_FIELDS = [ "CreatedBy", "OwnerTitle", "OwnerInitials", "OwnerForenames", "OwnerSurname",
                "OwnerName", "OwnerAddress", "OwnerTown", "OwnerCounty", "OwnerPostcode",
                "HomeTelephone", "WorkTelephone", "MobileTelephone", "EmailAddress", "FosterCapacity",
                "MembershipNumber", "HomeCheckAreas", "LookingForSummary" ];
            const COMMENT_FIELDS = [ "Comments" ];
            const YES_NO_FIELDS = [ "IDCheck", "IsBanned", "IsVolunteer", "IsHomeChecker", 
                "IsMember", "IsDonor", "IsShelter", "IsACO", "IsStaff", "IsFosterer",
                "IsRetailer", "IsVet", "IsGiftAid" ];
            let rv = "";
            if (name == "Jurisdiction") {
                rv = row.JURISDICTIONNAME;
            }
            else if (name == "HomeCheckedBy") {
                rv = row.HOMECHECKEDBYNAME;
            }
            else if ($.inArray(name, DATE_FIELDS) > -1) {
                rv = format.date(value);
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
            else if ( name == "AdditionalFlags") {
                rv = edit_header.person_flags(row);
            }
            else if ( name == "Image" ) {
                rv = "<img class=\"asm-thumbnail thumbnailshadow\" src=\"" + html.thumbnail_src(row, "personthumb") + "\" />";
            }
            else if ( name == "Image" ) {
                rv = html.person_link_thumb_bare(row);
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
                            rv = '<a href="person?id=' + v.VALUE + '">' + v.OWNERNAME + '</a>';
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

        name: "person_find_results",
        animation: "results",
        autofocus: "#asm-content a:first",
        title: function() { return _("Results"); },
        routes: {
            "person_find_results": function() { common.module_loadandstart("person_find_results", "person_find_results?" + this.rawqs); }
        }

    };

    common.module_register(person_find_results);

});
