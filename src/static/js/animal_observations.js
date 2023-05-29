/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const animal_observations = {

        render: function() {

            let h = [
                html.content_header(_("Daily Observations")),
                tableform.buttons_render([
                    { type: "raw", markup: '<button id="button-selectall">' + _("Select all") + '</button>' },
                    { id: "save", icon: "save", tooltip: _("Write observation logs for all selected rows") },
                    { id: "location", type: "dropdownfilter", options: html.list_to_options(controller.internallocations, "ID", "LOCATIONNAME") }
                ]),
                '<table class="asm-daily-observations">',
            ];

            // Render the header - behaviour item columns
            let colnames = [], colwidgets = [];
            for (let i = 0; i < 50; i++) {
                let name = config.str("Behave" + i + "Name"), value = config.str("Behave" + i + "Values");
                if (name) { 
                    colnames.push(name);
                    if (value) {
                        colwidgets.push('<select class="asm-selectbox asm-halfselectbox widget" data-name="' + html.title(name) + '">' +
                            '<option value=""></option>' + html.list_to_options(value.split("|")) + '</select>');
                    }
                    else {
                        colwidgets.push('<input type="text" class="asm-textbox widget" data-name="' + html.title(name) + '" />');
                    }
                }
            }

            // Output the column headings in the table
            h.push('<thead><tr><th>' + _("Animal") + '</th>');
            $.each(colnames, function(i, v) {
                h.push('<th>' + v + '</th>');
            });
            h.push('</tr></thead>');
            
            // Render a row for each animal 
            h.push('<tbody>');
            $.each(controller.animals, function(i, a) {
                // omit animals who aren't on shelter
                if (a.ACTIVEMOVEMENTTYPE) { return; }
                h.push('<tr data-animalid="' + a.ID + '" data-locationid="' + a.SHELTERLOCATION + '" style="display: none">');
                h.push('<td><input type="checkbox" class="asm-checkbox selector" /> ');
                h.push(html.animal_link(a, { showunit: true, emblemsright: true }));
                h.push('</td>');
                $.each(colnames, function(i, c) {
                    h.push('<td class="centered">' + colwidgets[i] + '</td>');
                });
                h.push('</tr>');
            });
            h.push('</tbody></table>');
            h.push(html.content_footer());
            return h.join("\n");
        },

        change_location: function() {
            $(".asm-daily-observations tbody tr").each(function() {
                $(this).toggle( $(this).attr("data-locationid") == $("#location").val() );
            });
        },

        bind: function() {

            $(".asm-daily-observations").table();
            
            $("#button-selectall").button({
                icons: { primary: "ui-icon-check" },
                text:  false
            }).click(function() {
                $(".asm-daily-observations .selector:visible").prop("checked", true);
                $(".asm-daily-observations tbody tr:visible").addClass("ui-state-highlight");
                $(".asm-daily-observations tbody tr:visible").removeClass("asm-completerow");
                $(".asm-daily-observations .widget:visible").prop("disabled", false);
            });

            $("#button-save").button().click(async function() {
                // Send the logs to the backend in the format:
                //    ANIMALID==FIELD1=VALUE1, FIELD2=VALUE2||ANIMALID==FIELD1=VALUE1,
                //    52==Wet food=Mostly, Pen state=Dirty
                // means the backend can split by || to get animals, then by == to get 
                // animalid and value string for the log.
                let formdata = { "mode": "save", "logtype": config.str("BehaveLogType") }, logs = [];
                $(".asm-daily-observations tbody tr").each(function() {
                    if (! $(this).find(".selector").is(":checked")) { return; } // skip unselected rows
                    let animalid = $(this).attr("data-animalid"), avs = [];
                    // Build a packed set of values for this animal
                    $(this).find(".widget").each(function() {
                        avs.push( $(this).attr("data-name") + "=" + $(this).val() );
                    });
                    logs.push( animalid + "==" + avs.join(", ") );
                });
                formdata.logs = logs.join("||");
                if (formdata.logs == "") { return; }
                header.show_loading(_("Saving..."));
                let response = await common.ajax_post("animal_observations", formdata);
                header.hide_loading();
                header.show_info(_("{0} observation logs successfully written.").replace("{0}", response));
                // Unselect the previously selected values
                $(".asm-daily-observations .selector").prop("checked", false);
                $(".asm-daily-observations .widget").val("").prop("disabled", true);
                $(".asm-daily-observations tr").removeClass("ui-state-highlight");
                $(".asm-daily-observations tbody tr").addClass("asm-completerow");
            });

            $(".asm-daily-observations").on("click", ".selector", function() {
                if ($(this).is(":checked")) {
                    $(this).closest("tr").removeClass("asm-completerow");
                    $(this).closest("tr").find(".widget").prop("disabled", false);
                }
                else {
                    $(this).closest("tr").addClass("asm-completerow");
                    $(this).closest("tr").find(".widget").prop("disabled", true);
                }
            });

            // Everything is disabled by default
            $(".asm-daily-observations tbody tr").addClass("asm-completerow");
            $(".asm-daily-observations .widget").prop("disabled", true);

            $("#location").change(this.change_location);

        },

        sync: function() {
            this.change_location();
        },

        destroy: function() {
        },

        name: "animal_observations",
        animation: "book",
        title: function() { return _("Daily Observations"); },
        routes: {
            "animal_observations": function() { common.module_loadandstart("animal_observations", "animal_observations?" + this.rawqs); }
        }

    };

    common.module_register(animal_observations);

});
