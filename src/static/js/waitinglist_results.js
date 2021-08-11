/*global $, jQuery, _, asm, additional, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const waitinglist_results = {

        render: function() {
            return [
                html.content_header(_("Waiting List")),
                '<div id="waitinglistcriteria">',
                '<table class="asm-table-layout">',
                '<tr>',
                    '<td>',
                    '<label for="priorityfloor">' + _("Priority Floor") + '</label>',
                    '</td>',
                    '<td>',
                    '<select id="priorityfloor" data="priorityfloor" class="asm-selectbox">',
                    html.list_to_options(controller.urgencies, "ID", "URGENCY"),
                    '</select>',
                    '</td>',
                    '<td>',
                    '<label for="includeremoved">' + _("Include Removed") + '</label>',
                    '</td>',
                    '<td>',
                    '<select id="includeremoved" data="includeremoved" class="asm-selectbox">',
                    html.list_to_options(controller.yesno, "ID", "NAME"),
                    '</select>',
                    '</td>',
                '</tr>',
                '<tr>',
                    '<td>',
                    '<label for="species">' + _("Species") + '</label>',
                    '</td>',
                    '<td>',
                    '<select id="species" data="species" class="asm-selectbox">',
                    '<option value="-1">' + _("(all)") + '</option>',
                    html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                    '</select>',
                    '</td>',
                    '<td>',
                    '<label for="size">' + _("Size") + '</label>',
                    '</td>',
                    '<td>',
                    '<select id="size" data="size" class="asm-selectbox">',
                    '<option value="-1">' + _("(all)") + '</option>',
                    html.list_to_options(controller.sizes, "ID", "SIZE"),
                    '</select>',
                    '</td>',
                '</tr>',
                '<tr>',
                    '<td>',
                    '<label for="namecontains">' + _("Name Contains") + '</label>',
                    '</td>',
                    '<td>',
                    '<input id="namecontains" data="namecontains" class="asm-textbox" />',
                    '</td>',
                    '<td>',
                    '<label for="addresscontains">' + _("Address Contains") + '</label>',
                    '</td>',
                    '<td>',
                    '<input id="addresscontains" data="addresscontains" class="asm-textbox" />',
                    '</td>',
                '</tr>',
                '<tr>',
                    '<td>',
                    '<label for="descriptioncontains">' + _("Description Contains") + '</label>',
                    '</td>',
                    '<td>',
                    '<input id="descriptioncontains" data="descriptioncontains" class="asm-textbox" />',
                    '</td>',
                    '<td></td>',
                    '<td>',
                    '<button id="button-refresh">' + html.icon("refresh") + ' ' + _("Refresh") + '</button>',
                    '</td>',
                '</tr>',
                '</table>',
                '</div>',
                '<div class="asm-toolbar">',
                '<button id="button-new">' + html.icon("new") + ' ' + _("New Waiting List Entry") + '</button>',
                '<button id="button-delete">' + html.icon("delete") + ' ' + _("Delete") + '</button>',
                '<button id="button-complete">' + html.icon("complete") + ' ' + _("Remove") + '</button>',
                '<button class="bhighlight" data="1" title="' + html.title(_("Highlight")) + '">' + html.icon("highlight1") + '</button>',
                '<button class="bhighlight" data="2" title="' + html.title(_("Highlight")) + '">' + html.icon("highlight2") + '</button>',
                '<button class="bhighlight" data="3" title="' + html.title(_("Highlight")) + '">' + html.icon("highlight3") + '</button>',
                '<button class="bhighlight" data="4" title="' + html.title(_("Highlight")) + '">' + html.icon("highlight4") + '</button>',
                '<button class="bhighlight" data="5" title="' + html.title(_("Highlight")) + '">' + html.icon("highlight5") + '</button>',
                '</div>',
                '<table id="table-waitinglist">',
                waitinglist_results.render_tablehead(),
                '<tbody>',
                '</tbody>',
                '</table>',
                html.content_footer()
            ].join("\n");
        },

        /**
         * Renders the table.head tag with columns in the right order
         */
        render_tablehead: function() {
            let labels = waitinglist_results.column_labels();
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
            $.each(controller.rows, function(i, row) {
                h.push("<tr>");
                $.each(waitinglist_results.column_names(), function(i, name) {
                    let link = "<span style=\"white-space: nowrap\">";
                    link += "<input type=\"checkbox\" class=\"asm-checkbox\" data=\"" + row.ID + "\" />";
                    link += "<a id=\"action-" + row.ID + "\" href=\"waitinglist?id=" + row.ID + "\">";
                    // Choose a cell style based on whether a highlight is selected or the urgency
                    let tdclass = "";
                    if (row.HIGHLIGHT != "") {
                        tdclass = "asm-wl-highlight" + row.HIGHLIGHT;
                    }
                    else if (row.URGENCY == 5) { tdclass = "asm-wl-lowest"; }
                    else if (row.URGENCY == 4) { tdclass = "asm-wl-low"; }
                    else if (row.URGENCY == 3) { tdclass = "asm-wl-medium"; }
                    else if (row.URGENCY == 2) { tdclass = "asm-wl-high"; }
                    else if (row.URGENCY == 1) { tdclass = "asm-wl-urgent"; }
                    h.push("<td class=\"" + tdclass + "\">");
                    let value = "";
                    if (row.hasOwnProperty(name.toUpperCase())) {
                        value = row[name.toUpperCase()];
                    }
                    let formatted = waitinglist_results.format_column(row, name, value, controller.additional);
                    if (name == "OwnerName") {
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
            $("#table-waitinglist").table({ 
                style_td: false, 
                row_hover: false,
                row_select: false
            });

            $("#table-waitinglist").on("change", "input", function() {
                if ($("#table-waitinglist input:checked").length > 0) {
                    $("#button-delete").button("option", "disabled", false); 
                    $("#button-complete").button("option", "disabled", false); 
                    $(".bhighlight").button("option", "disabled", false); 
                }
                else {
                    $("#button-delete").button("option", "disabled", true); 
                    $("#button-complete").button("option", "disabled", true); 
                    $(".bhighlight").button("option", "disabled", true); 
                }
            });

            $("#button-refresh").button().click(function() {
                common.route("waitinglist_results?" + $("#waitinglistcriteria .asm-selectbox, #waitinglistcriteria .asm-textbox").toPOST());
            });

            $("#button-new").button().click(function() {
                common.route("waitinglist_new");
            });

            $("#button-complete").button({disabled: true}).click(async function() {
                $("#button-complete").button("disable");
                let formdata = "mode=complete&ids=" + $("#table-waitinglist input").tableCheckedData();
                await common.ajax_post("waitinglist_results", formdata);
                common.route_reload(); 
            });

            $(".bhighlight").button({disabled: true}).click(async function() {
                let formdata = "mode=highlight&himode=" + $(this).attr("data") + "&ids=" + $("#table-waitinglist input").tableCheckedData();
                await common.ajax_post("waitinglist_results", formdata);
                common.route_reload(); 
            });

            $("#button-delete").button({disabled: true}).click(async function() {
                await tableform.delete_dialog();
                let formdata = "mode=delete&ids=" + $("#table-waitinglist input").tableCheckedData();
                await common.ajax_post("waitinglist_results", formdata);
                common.route_reload(); 
            });
        },

        sync: function() {
            
            $("#priorityfloor").select("value", controller.selpriorityfloor);
            $("#includeremoved").select("value", controller.selincluderemoved);
            $("#species").select("value", controller.selspecies);
            $("#namecontains").val(controller.selnamecontains);
            $("#addresscontains").val(controller.seladdresscontains);
            $("#descriptioncontains").val(controller.descriptioncontains);

            // load the table results
            $("#table-waitinglist tbody").append(this.render_tablebody());

            // reinject target links
            common.inject_target();

            // update and retrigger the sort
            $("#table-waitinglist").trigger("update");
            $("#table-waitinglist").trigger("sorton", [[[0,0]]]);
        },

        /** 
         * Returns a list of our configured viewable column names
         */
        column_names: function() {
            let cols = [];
            $.each(config.str("WaitingListViewColumns").split(","), function(i, v) {
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
            let names = waitinglist_results.column_names();
            let labels = [];
            $.each(names, function(i, name) {
                labels.push(waitinglist_results.column_label(name, controller.additional));
            });
            return labels;
        },

        /**
         * Returns the number of configured viewable columns
         */
        column_count: function() {
            return waitinglist_results.column_names().length;
        },

        /**
         * Returns the i18n translated label for a column with name.
         * add - additional fields to scan for labels
         */
        column_label: function(name, add) {
            let labels = {
                "Number": _("Number"),
                "CreatedBy": _("Created By"),
                "Rank": _("Rank"),
                "SpeciesID": _("Species"),
                "Size": _("Size"),
                "DatePutOnList": _("Date Put On"),
                "TimeOnList": _("Time On List"),
                "OwnerName": _("Name"),
                "OwnerAddress": _("Address"),
                "OwnerTown": _("City"),
                "OwnerCounty": _("State"),
                "OwnerPostcode": _("Zipcode"),
                "HomeTelephone": _("Home Phone"),
                "WorkTelephone": _("Work Phone"),
                "MobileTelephone": _("Cell Phone"),
                "EmailAddress": _("Email"),
                "AnimalDescription": _("Description"),
                "ReasonForWantingToPart": _("Reason"),
                "CanAffordDonation": _("Donation?"),
                "Urgency": _("Urgency"),
                "DateRemovedFromList": _("Removed"),
                "ReasonForRemoval": _("Removal Reason"),
                "Comments": _("Comments")
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
            const DATE_FIELDS = [ "DatePutOnList", "DateRemovedFromList" ],
                STRING_FIELDS = [ "CreatedBy", "OwnerName", "OwnerAddress", "OwnerTown", "OwnerCounty", 
                    "OwnerPostcode", "HomeTelephone", "WorkTelephone", "MobileTelephone", 
                    "EmailAddress", "AnimalDescription", "ReasonForWantingToPart", 
                    "ReasonForRemoval", "Comments", "Rank", "TimeOnList" ],
                YES_NO_FIELDS = [ "CanAffordDonation" ];
            let rv = "";
            if (name == "Number") {
                rv = format.padleft(row.ID, 6);
            }
            else if (name == "SpeciesID") {
                rv = row.SPECIESNAME;
            }
            else if (name == "Size") {
                rv = row.SIZENAME;
            }
            else if (name == "Urgency") {
                rv = row.URGENCYNAME;
            }
            else if ($.inArray(name, DATE_FIELDS) > -1) {
                rv = format.date(value);
            }
            else if ($.inArray(name, STRING_FIELDS) > -1) {
                rv = value;
            }
            else if ($.inArray(name, YES_NO_FIELDS) > -1) {
                if (value == 0) { rv = _("No"); }
                if (value == 1) { rv = _("Yes"); }
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
                        else if (v.FIELDTYPE == additional.PERSON_LOOKUP) {
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

        name: "waitinglist_results",
        animation: "book",
        autofocus: "#priorityfloor",
        title: function() { return _("Waiting List"); },
        routes: {
            "waitinglist_results": function() { common.module_loadandstart("waitinglist_results", "waitinglist_results?" + this.rawqs); }
        }

    };

    common.module_register(waitinglist_results);

});
