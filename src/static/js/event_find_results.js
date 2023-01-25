/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const event_find_results = {

        render: function() {
            return [
                html.content_header(_("Results")),
                '<div id="asm-results">',
                '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-search"></span>',
                _("Find events returned {0} results.").replace("{0}", controller.rows.length),
                '</p>',
                '</div>',
                '<table id="searchresults">',
                event_find_results.render_tablehead(),
                '<tbody>',
                event_find_results.render_tablebody(),
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
            let labels = event_find_results.column_labels();
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
                $.each(event_find_results.column_names(), function(ic, name) {
                    let formatted = '';
                    h.push("<td>");
                    if (name == "StartDateTime") {
                        formatted += html.event_link(row.ID, format.date(row.STARTDATETIME));
                    }
                    else {
                        let value = "";
                        if (row.hasOwnProperty(name.toUpperCase())) {
                            value = row[name.toUpperCase()];
                        }
                        formatted = event_find_results.format_column(row, name, value, controller.additional);
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
            $.each(config.str("EventSearchColumns").split(","), function(i, v) {
                cols.push(common.trim(v));
            });
            // If StartDateTime is not present in the list, insert it as the first column to make
            // sure there's still a link displayed to the target record
            if (!common.array_in("StartDateTime", cols)) { cols.unshift("StartDateTime"); } 
            return cols;
        },

        /**
         * Returns a list of our configured viewable column labels
         */
        column_labels: function() {
            let names = event_find_results.column_names();
            let labels = [];
            $.each(names, function(i, name) {
                labels.push(event_find_results.column_label(name, controller.additional));
            });
            return labels;
        },

        /**
         * Returns the i18n translated label for a column with name
         */

        column_label: function(name, add) {
/*
        ( "CreatedBy", _("Created By", l) ),
        ( "CreatedDate", _("Created Date", l) ),
        ( "LastChangedBy", _("Last Changed By", l) ),
        ( "LastChangedDate", _("Last Change Date", l) ),

        ( "EventName", _("Event Name", l) ),
        ( "StartDateTime", _("Start Date", l) ),
        ( "EndDateTime", _("End Date", l) ),
        ( "EventOwnerName", _("Location", l) ),
        ( "EventAddress", _("Address", l) ),
        ( "EventTown", _("City", l) ),
        ( "EventCounty", _("State", l) ),
        ( "EventPostcode", _("Zipcode", l) ),
        ( "EventCountry", _("Country", l) ),
*/
            let labels = {
                "CreatedBy": _("Created By"),
                "CreatedDate": _("Created Date"),
                "LastChangedBy":  _("Last Changed By"),
                "LastChangedDate":  _("Last Change Date"),
                "EventName":  _("Event Name"),
                "StartDateTime":  _("Start Date"),
                "EndDateTime":  _("End Date"),
                "EventOwnerName":  _("Location"),
                "EventAddress":  _("Address"),
                "EventTown":  _("City"),
                "EventCounty":  _("County"),
                "EventPostcode":  _("Zipcode"),
                "EventCountry":  _("Country"),
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
         * row: The event resultset row
         * name: The name of the column
         * value: The value of the row/column to format from the resultset
         * add: The additional row results
         */
        format_column: function(row, name, value, add) {
            const DATE_FIELDS = [ "StartDateTime", "EndDateTime" ],
            DATETIME_FIELDS = [ "CreatedDate", "LastChangedDate" ],
            STRING_FIELDS = [ "EventName", "EventOwnerName", "EventAddress", "EventTown", "EventCounty", "EventPostcode", "EventCountry" ];
            let rv = "";
            if ($.inArray(name, DATETIME_FIELDS) > -1) {
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
                
        name: "event_find_results",
        animation: "results",
        autofocus: "#asm-content a:first",
        title: function() { return _("Results"); },
        routes: {
            "event_find_results": function() { common.module_loadandstart("event_find_results", "event_find_results?" + this.rawqs); }
        }

    };

    common.module_register(event_find_results);

});
