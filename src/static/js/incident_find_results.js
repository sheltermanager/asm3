/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const incident_find_results = {

        render: function() {
            return [
                html.content_header(_("Results")),
                '<div id="asm-results">',
                '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-search"></span>',
                _("Find animal control incidents returned {0} results.").replace("{0}", controller.rows.length),
                '</p>',
                '</div>',
                '<table id="searchresults">',
                incident_find_results.render_tablehead(),
                '<tbody>',
                incident_find_results.render_tablebody(),
                '</tbody>',
                '</table>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        /**
         * Renders the table.head tag
         */
        render_tablehead: function() {
            let labels = incident_find_results.column_labels();
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
         * Renders the table body with columns
         */
        render_tablebody: function() {
            let h = [];
            $.each(controller.rows, function(ir, row) {
                h.push("<tr>");
                $.each(incident_find_results.column_names(), function(ic, name) {
                    let formatted = '';
                    h.push("<td>");
                    if (name == "Suspect") {
                        if (row.OWNERNAME1) { formatted += html.person_link(row.OWNERID, row.OWNERNAME1); }
                        if (row.OWNERNAME2) { formatted += '<br/>' + html.person_link(row.OWNER2ID, row.OWNERNAME2); }
                        if (row.OWNERNAME3) { formatted += '<br/>' + html.person_link(row.OWNER3ID, row.OWNERNAME3); }
                    } 
                    else if (name == "Caller") {
                        formatted += html.person_link(row.CALLERID, row.CALLERNAME);
                    }
                    else if (name == "Victim") {
                        formatted += html.person_link(row.VICTIMID, row.VICTIMNAME);
                    }
                    else {
                        let value = "";
                        if (row.hasOwnProperty(name.toUpperCase())) {
                            value = row[name.toUpperCase()];
                        }
                        formatted = incident_find_results.format_column(row, name, value, controller.additional);
                        if (name == "IncidentNumber") { 
                            let link = "<span style=\"white-space: nowrap\"><a href=\"incident?id=" + row.ID + "\">";
                            formatted = link + formatted + "</a></span>";
                        }
                    }
                    h.push(formatted);
                    h.push("</td>");
                });
                h.push("</tr>");
            });
            return h.join("\n");
        },
        
        bind: function() {
            $("#searchresults").table();
        },

        sync: function() {
            $("#searchresults").trigger("sorton", [[[2,1]]]);
        },

        /** 
         * Returns a list of our configured viewable column names
         */
        column_names: function() {
            let cols = [];
            $.each(config.str("IncidentSearchColumns").split(","), function(i, v) {
                cols.push(common.trim(v));
            });
            // If IncidentNumber is not present in the list, insert it as the first column to make
            // sure there's still a link displayed to the target record
            if (!common.array_in("IncidentNumber", cols)) { cols.unshift("IncidentNumber"); } 
            return cols;
        },

        /**
         * Returns a list of our configured viewable column labels
         */
        column_labels: function() {
            let names = incident_find_results.column_names();
            let labels = [];
            $.each(names, function(i, name) {
                labels.push(incident_find_results.column_label(name, controller.additional));
            });
            return labels;
        },

        /**
         * Returns the i18n translated label for a column with name
         */

        column_label: function(name, add) {
            let labels = {
                "IncidentType": _("Incident Type"),
                "IncidentNumber": _("Number"),
                "IncidentDateTime":  _("Incident Date/Time"),
                "DispatchAddress":  _("Address"),
                "DispatchTown":  _("City"),
                "DispatchPostcode":  _("Zipcode"),
                "JurisdictionName":  _("Jurisdiction"),
                "LocationName":  _("Location"),
                "Suspect":  _("Suspect"),
                "Victim":  _("Victim"),
                "DispatchDateTime":  _("Dispatch Date/Time"),
                "RespondedDateTime":  _("Responded Date/Time"),
                "DispatchedACO":  _("ACO"),
                "FollowupDateTime":  _("Followup Date"),
                "CompletedDate":  _("Completion Date"),
                "CompletedName": _("Completion Type"),
                "Caller": _("Caller"),
                "CallNotes":  _("Notes")
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
         * row: The incident resultset row
         * name: The name of the column
         * value: The value of the row/column to format from the resultset
         * add: The additional row results
         */
        format_column: function(row, name, value, add) {
            const DATE_FIELDS = [ "FollowupDateTime", "CompletedDate" ],
            DATETIME_FIELDS = [ "IncidentDateTime", "DispatchDateTime", "RespondedDateTime" ],
            STRING_FIELDS = [ "DispatchedACO", "DispatchAddress", "DispatchTown", "DispatchPostcode", "JurisdictionName", "LocationName", "CompletedName" ];
            let rv = "";
            if (name == "IncidentNumber") {
              rv  = format.padleft(row.ID, 6);
            }
            else if (name == "IncidentType") {
                rv = row.INCIDENTNAME;
            }
            else if (name == "CallNotes") {
              rv = html.truncate(value);
            }
            else if ($.inArray(name, DATETIME_FIELDS) > -1) {
              rv = format.date(value);
              if (format.time(value) != "00:00:00") {
                  rv += " " + format.time(value);
              }            
            }
            else if ($.inArray(name, DATE_FIELDS) > -1) {
              rv = format.date(value);
            }
            else if ($.inArray(name, STRING_FIELDS) > -1) {
                rv = common.nulltostr(value);
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
                
        name: "incident_find_results",
        animation: "results",
        autofocus: "#asm-content a:first",
        title: function() { return _("Results"); },
        routes: {
            "incident_find_results": function() { common.module_loadandstart("incident_find_results", "incident_find_results?" + this.rawqs); }
        }

    };

    common.module_register(incident_find_results);

});
