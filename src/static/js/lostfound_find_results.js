/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    "use strict";

    const lostfound_find_results = {
        
        mode: "lost", 

        render: function() {
            this.mode = controller.name.indexOf("lost") != -1 ? "lost" : "found";
            return [
                html.content_header(_("Results")),
                '<div id="asm-results">',
                '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-search"></span>',
                (this.mode == "lost" ? _("Find lost animal returned {0} results.") : 
                    _("Find found animal returned {0} results.")).replace("{0}", controller.rows.length),
                '</p>',
                '</div>',
                '<table id="searchresults">',
                lostfound_find_results.render_tablehead(),
                '<tbody>',
                lostfound_find_results.render_tablebody(),
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
            let labels = lostfound_find_results.column_labels();
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
                $.each(lostfound_find_results.column_names(), function(ic, name) {
                  let formatted = '';
                    h.push("<td>");
                    if(name == "Owner"){
                      formatted += html.person_link(row.OWNERID, row.OWNERNAME);
                    } else {
                      let value = "";
                      if (row.hasOwnProperty(name.toUpperCase())) {
                          value = row[name.toUpperCase()];
                      }
                      formatted = lostfound_find_results.format_column(row, name, value);
                      if(name == 'LostFoundID') {
                        if (lostfound_find_results.mode == "lost") {
                            let link = '<a href="lostanimal?id=' + row.ID + '">';
                            formatted = link + formatted + "</a>";
                        }
                        else {
                            let link = '<a href="foundanimal?id=' + row.ID + '">';
                            formatted = link + formatted + "</a></span>";
                        }
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

        /** 
         * Returns a list of our configured viewable column names
         */
        column_names: function() {
            let cols = [];
            $.each(config.str("LostFoundAnimalSearchColumns").split(","), function(i, v) {
                cols.push(common.trim(v));
            });
            // If LostFoundID is not present in the list, insert it as the first column to make
            // sure there's still a link displayed to the target record
            if (!common.array_in("LostFoundID", cols)) { cols.unshift("LostFoundID"); } 
            return cols;
        },

        /**
         * Returns a list of our configured viewable column labels
         */
        column_labels: function() {
            let names = lostfound_find_results.column_names();
            let labels = [];
            $.each(names, function(i, name) {
                labels.push(lostfound_find_results.column_label(name));
            });
            return labels;
        },

        /**
         * Returns the i18n translated label for a column with name
         */

        column_label: function(name) {
            let labels = {
                "LostFoundID": _("Number"),
                "Owner": _("Contact"),
                "MicrochipNumber":  _("Microchip"),
                "AreaLostFound":  _("Area"),
                "AreaPostCode":  _("Zipcode"),
                "DateLostFound":  _("Date"),
                "AgeGroup":  _("Age Group"),
                "SexName":  _("Sex"),
                "SpeciesName":  _("Species"),
                "BreedName":  _("Breed"),
                "BaseColourName":  _("Color"),
                "DistFeat":  _("Features")
            };
            if (labels.hasOwnProperty(name)) {
                return labels[name];
            }
            return name;
        },

        /**
         * Returns a formatted column
         * row: The lost/found resultset row
         * name: The name of the column
         * value: The value of the row/column to format from the resultset
         */
        format_column: function(row, name, value) {
            const STRING_FIELDS = [ "MicrochipNumber", "AreaPostCode", "AgeGroup", "SexName", "SpeciesName", "BreedName", "BaseColourName", "DistFeat" ];
            let rv = "";
            if (name == "LostFoundID") {
              rv  = format.padleft(row.ID, 6)
            }
            else if (name == "AreaLostFound") {
              if (lostfound_find_results.mode == "lost") {
                  rv = common.nulltostr(row.AREALOST);
              }
              else {
                  rv = common.nulltostr(row.AREAFOUND);
              }
            }
            else if (name == "DateLostFound") {
              if (lostfound_find_results.mode == "lost") {
                  rv = format.date(row.DATELOST);
              }
              else {
                  rv = format.date(row.DATEFOUND);
              }
            }
            else if ($.inArray(name, STRING_FIELDS) > -1) {
                rv = common.nulltostr(value);
            }
            return rv;
        },
        
        name: "lostfound_find_results",
        animation: "results",
        autofocus: "#asm-content a:first",
        title: function() { return _("Results"); },
        routes: {
            "lostanimal_find_results": function() { common.module_loadandstart("lostfound_find_results", "lostanimal_find_results?" + this.rawqs); },
            "foundanimal_find_results": function() { common.module_loadandstart("lostfound_find_results", "foundanimal_find_results?" + this.rawqs); }
        }

    };

    common.module_register(lostfound_find_results);

});
