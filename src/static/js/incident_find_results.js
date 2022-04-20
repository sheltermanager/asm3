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
         * Renders the table.head tag with columns in the right order
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

        // render_results: function() {
        //     let h = [];
        //     $.each(controller.rows, function(i, r) {
        //         h.push('<tr>');
        //         h.push('<td><a href="incident?id=' + r.ID + '">' + r.INCIDENTNAME + '</a></td>');
        //         h.push('<td>' + format.padleft(r.ID, 6) + '</td>');
        //         h.push('<td>' + format.date(r.INCIDENTDATETIME) + ' ' + format.time(r.INCIDENTDATETIME) + '</td>');
        //         h.push('<td>' + common.nulltostr(r.DISPATCHADDRESS) + '</td>');
        //         h.push('<td>' + common.nulltostr(r.DISPATCHTOWN) + '</td>');
        //         h.push('<td>' + common.nulltostr(r.DISPATCHPOSTCODE) + '</td>');
        //         h.push('<td>' + common.nulltostr(r.JURISDICTIONNAME) + '</td>');
        //         h.push('<td>' + common.nulltostr(r.LOCATIONNAME) + '</td>');
        //         h.push('<td>');
        //         if (r.OWNERNAME1) { h.push(html.person_link(r.OWNERID, r.OWNERNAME1)); }
        //         if (r.OWNERNAME2) { h.push('<br/>' + html.person_link(r.OWNER2ID, r.OWNERNAME2)); }
        //         if (r.OWNERNAME3) { h.push('<br/>' + html.person_link(r.OWNER3ID, r.OWNERNAME3)); }
        //         h.push('</td>');
        //         h.push('<td>' + format.date(r.DISPATCHDATETIME) + ' ' + format.time(r.DISPATCHDATETIME) + '</td>');
        //         h.push('<td>' + format.date(r.RESPONDEDDATETIME) + ' ' + format.time(r.RESPONDEDDATETIME) + '</td>');
        //         h.push('<td>' + common.nulltostr(r.DISPATCHEDACO) + '</td>');
        //         h.push('<td>' + format.date(r.FOLLOWUPDATETIME) + '</td>');
        //         h.push('<td>' + format.date(r.COMPLETEDDATE) + '</td>');
        //         h.push('<td>' + common.nulltostr(r.COMPLETEDNAME) + '</td>');
        //         h.push('<td>' + html.truncate(r.CALLNOTES) + '</td>');
        //         h.push('</tr>');
        //     });
        //     return h.join("\n");
        // },

        /**
         * Renders the table body with columns in the right order and
         * highlighting styling applied, etc.
         */
        render_tablebody: function() {
            let h = [];
            $.each(controller.rows, function(ir, row) {
                h.push("<tr>");
                $.each(incident_find_results.column_names(), function(ic, name) {
                  let formatted = '';
                    // Generate the incident selector
                    h.push("<td>");
                    if(name == "Suspect"){
                      if (row.OWNERNAME1) { formatted += html.person_link(row.OWNERID, row.OWNERNAME1); }
                      if (row.OWNERNAME2) { formatted += '<br/>' + html.person_link(row.OWNER2ID, row.OWNERNAME2); }
                      if (row.OWNERNAME3) { formatted += '<br/>' + html.person_link(row.OWNER3ID, row.OWNERNAME3); }
                    } else {
                      let value = "";
                      if (row.hasOwnProperty(name.toUpperCase())) {
                          value = row[name.toUpperCase()];
                      }
                      formatted = incident_find_results.format_column(row, name, value);
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
                labels.push(incident_find_results.column_label(name));
            });
            return labels;
        },

        /**
         * Returns the i18n translated label for a column with name
         */

        column_label: function(name) {
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
                "DispatchDateTime":  _("Dispatch Date/Time"),
                "RespondedDateTime":  _("Responded Date/Time"),
                "DispatchedACO":  _("ACO"),
                "FollowupDateTime":  _("Followup Date"),
                "CompletedDate":  _("Completion Date"),
                "CompletedName": _("Completion Type"),
                "CallNotes":  _("Notes")
            };
            if (labels.hasOwnProperty(name)) {
                return labels[name];
            }
            return name;
        },
        
        /**
         * Returns a formatted column
         * row: The incident resultset row
         * name: The name of the column
         * value: The value of the row/column to format from the resultset
         */
        format_column: function(row, name, value) {
            const DATE_FIELDS = [ "FollowupDateTime", "CompletedDate" ],
            DATETIME_FIELDS = [ "IncidentDateTime", "DispatchDateTime", "RespondedDateTime" ],
            STRING_FIELDS = [ "DispatchedACO", "DispatchAddress", "DispatchTown", "DispatchPostcode", "JurisdictionName", "LocationName", "CompletedName" ];
            let rv = "";
            if (name == "IncidentNumber") {
              rv  = format.padleft(row.ID, 6)
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
