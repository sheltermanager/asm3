/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const staff_rota = {

        model: function() {
            const dialog = {
                add_title: _("Add rota item"),
                edit_title: _("Edit rota item"),
                edit_perm: 'coro',
                close_on_ok: false,
                delete_button: true,
                delete_perm: 'doro',
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "OWNERID", post_field: "person", personmode: "brief", personfilter: "volunteerandstaff", 
                        label: _("Person"), type: "person", validation: "notzero" },
                    { json_field: "ROTATYPEID", post_field: "type", label: _("Type"), type: "select", 
                        options: { displayfield: "ROTATYPE", valuefield: "ID", rows: controller.rotatypes }},
                    { json_field: "WORKTYPEID", post_field: "worktype", label: _("Work"), type: "select", 
                        options: { displayfield: "WORKTYPE", valuefield: "ID", rows: controller.worktypes }},
                    { json_field: "STARTDATETIME", post_field: "startdate", label: _("Starts"), type: "date", validation: "notblank", defaultval: new Date() },
                    { json_field: "STARTDATETIME", post_field: "starttime", label: _("at"), type: "time", validation: "notblank", defaultval: config.str("DefaultShiftStart") },
                    { json_field: "ENDDATETIME", post_field: "enddate", label: _("Ends"), type: "date", validation: "notblank", defaultval: new Date() },
                    { json_field: "ENDDATETIME", post_field: "endtime", label: _("at"), type: "time", validation: "notblank", defaultval: config.str("DefaultShiftEnd") },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };
            this.dialog = dialog;
        },

        render: function() {
            this.model();
            return [
                tableform.dialog_render(this.dialog),
                staff_rota.render_clonedialog(),
                html.content_header(_("Staff Rota")),
                tableform.buttons_render([
                    { id: "prev", icon: "rotate-anti", tooltip: _("Week beginning {0}").replace("{0}", format.date(controller.prevdate)) },
                    { id: "today", icon: "diary", tooltip: _("This week") },
                    { id: "next", icon: "rotate-clock", tooltip: _("Week beginning {0}").replace("{0}", format.date(controller.nextdate)) },
                    { id: "clone", text: _("Clone"), icon: "copy", perm: 'aoro', tooltip: _("Clone the rota this week to another week") },
                    { id: "delete", text: _("Delete"), icon: "delete", perm: 'doro', tooltip: _("Delete all rota entries for this week") },
                    { type: "raw", markup: '<span style="float: right"><select id="flags" multiple="multiple" class="asm-bsmselect"></select></span>' }
                ]),
                '<table class="asm-staff-rota">',
                '<thead></thead>',
                '<tbody></tbody>',
                '</table>',
                html.info(_("To add people to the rota, create new person records with the staff or volunteer flag."), "emptyhint"), 
                html.content_footer()
            ].join("\n");
        },

        days: [],

        generate_table: function() {

            // Render the header - week number, followed by a column
            // for each day of the week.
            let h = [ '<tr>' ],
                css = "",
                title = "",
                i, 
                d = format.date_js(controller.startdate),
                weekno = 1,
                selattr = "",
                weekoptions = [],
                // We add 6 days when calling these two functions so that if
                // d is in the last week of the year, we show the dropdown list
                // for the next year instead of the one we are leaving.
                w = format.first_iso_monday_of_year(common.add_days(d, 6)),
                thisweekno = format.date_weeknumber(common.add_days(d, 6));
            
            // Generate a list of options for every week of the year
            while (weekno <= 52) {
                selattr = "";
                if (weekno == thisweekno) { selattr = 'selected="selected"'; }
                weekoptions.push('<option value="' + format.date(w) + '" ' + selattr + '>' + _("{0}, Week {1}").replace("{0}", format.date(w)).replace("{1}", weekno) + '</option>');
                w.setDate(w.getDate() + 7);
                weekno += 1;
            }

            h.push('<th><select id="weekselector" class="weekselector asm-selectbox">' + weekoptions.join("\n") + '</select></th>');
            staff_rota.days = [];
            for (i = 0; i < 7; i += 1) {
                css = "";
                if (format.date(d) == format.date(new Date())) { css = 'asm-staff-rota-today'; } else { css = 'asm-staff-rota-day'; }
                h.push('<th class="' + css + '">' + format.weekdayname(i) + '. ' + format.monthname(d.getMonth()) + ' ' + d.getDate() + '</th>');
                staff_rota.days.push(d);
                d = common.add_days(d, 1);
            }
            h.push('</tr>');
            $(".asm-staff-rota thead").html(h.join("\n"));

            // If there aren't any staff, show a hint box
            $("#emptyhint").toggle(controller.staff.length == 0);
            
            // Render a row for each person with their rota for the week
            h = [];
            $.each(controller.staff, function(i, p) {
                if (p.ISSTAFF) {
                    title = _("Staff");
                    css = "asm-staff-rota-staff-odd";
                    if (i % 2 == 0) { css = "asm-staff-rota-staff-even"; }
                }
                else {
                    title = _("Volunteer");
                    css = "asm-staff-rota-volunteer-odd";
                    if (i % 2 == 0) { css = "asm-staff-rota-volunteer-even"; }
                }
                // If there are some flags set in the filter box, make sure this person has them before
                // rendering their row
                if ($("#flags").val().length > 0) {
                    if (!p.ADDITIONALFLAGS) { return; }
                    if (!common.array_overlap($("#flags").val(), p.ADDITIONALFLAGS.split("|"))) { return ; }
                }
                h.push("<tr>");
                h.push('<td class="' + css + '" title="' + html.title(title) + '">');
                h.push('<a href="person_rota?id=' + p.ID + '" class="' + html.title(title) + '">' + p.OWNERNAME + '</a>');
                h.push("</td>");
                $.each(staff_rota.days, function(id, d) {
                    h.push('<td data-person="' + p.ID + '" data-date="' + format.date(d) + '" class="asm-staff-rota-cell">');
                    $.each(controller.rows, function(ir, r) {
                        if (r.OWNERID == p.ID && format.date_in_range(d, r.STARTDATETIME, r.ENDDATETIME, true)) {
                            let period = format.time(r.STARTDATETIME, "%H:%M") + ' - ' + format.time(r.ENDDATETIME, "%H:%M");
                            if (r.ROTATYPEID < 10) {
                                if (r.ROTATYPEID == 1) { css = 'asm-staff-rota-shift'; }
                                if (r.ROTATYPEID == 2) { css = 'asm-staff-rota-overtime'; }
                                h.push('<a class="' + css + '" href="#" data-id="' + r.ID + '">' + 
                                    period + '<br />');
                                h.push('<span class="asm-staff-rota-shift-work">' + r.WORKTYPENAME + '</span></a><br/>');
                            }
                            else { 
                                h.push('<a class="asm-staff-rota-timeoff" href="#" data-id="' + r.ID + 
                                    '" title="' + period + '">' + r.ROTATYPENAME + '</a><br />');
                            }
                        }
                    });
                    h.push('</td>');
                });
                h.push("</tr>");
            });
            $(".asm-staff-rota tbody").html(h.join("\n"));
        },

        get_flags_param: function(encode) {
            let flags = $("#flags").val();
            if (!flags) { flags = []; }
            if (encode === undefined || encode === true) { return encodeURIComponent(flags.join(",")); }
            return flags.join(",");
        },

        render_clonedialog: function() {
            return [
                '<div id="dialog-clone" style="display: none" title="' + html.title(_("Clone Rota")) + '">',
                tableform.fields_render([
                    { post_field: "newdate", type: "date", label: _("To week beginning"), date_nopast: true, date_onlydays: "1," }
                ]),
                '</div>'
            ].join("\n");
        },

        type_change: function() {
            $("#worktyperow").toggle(format.to_int($("#type").val()) <= 10);
        },

        bind: function() {

            let dialog = this.dialog;
            tableform.dialog_bind(dialog);

            $(".asm-staff-rota").on("click", "a", function(e) {
                let id = $(this).attr("data-id");
                let row = common.get_row(controller.rows, id, "ID");
                tableform.dialog_show_edit(dialog, row, { onload: function() { staff_rota.type_change(); }} )
                    .then(function() {
                        tableform.fields_update_row(dialog.fields, row);
                        row.ROTATYPENAME = common.get_field(controller.rotatypes, row.ROTATYPEID, "ROTATYPE");
                        row.WORKTYPENAME = common.get_field(controller.worktypes, row.WORKTYPEID, "WORKTYPE");
                        return tableform.fields_post(dialog.fields, "mode=update&rotaid=" + row.ID, controller.name);
                    })
                    .then(function(response) {
                        staff_rota.generate_table();
                        tableform.dialog_close();
                    })
                    .fail(function(type, row) {
                        if (type == "delete") {
                            common.ajax_post(controller.name, "mode=delete&ids=" + id)
                                .then(function() {
                                    common.delete_row(controller.rows, id, "ID");
                                    staff_rota.generate_table();
                                })
                                .always(function() {
                                    tableform.dialog_close();
                                });
                        }
                    });
                return false;
            });

            $(".asm-staff-rota").on("click", "td", function(e) {
                let personid = $(this).attr("data-person");
                let date = $(this).attr("data-date");
                if (!personid && !date) { return; }
                tableform.dialog_show_add(dialog, {
                    onadd: async function() {
                        let response = await tableform.fields_post(dialog.fields, "mode=create", controller.name);
                        let row = {};
                        row.ID = response;
                        tableform.fields_update_row(dialog.fields, row);
                        row.ROTATYPENAME = common.get_field(controller.rotatypes, row.ROTATYPEID, "ROTATYPE");
                        row.WORKTYPENAME = common.get_field(controller.worktypes, row.WORKTYPEID, "WORKTYPE");
                        controller.rows.push(row);
                        staff_rota.generate_table();
                        tableform.dialog_close();
                    },
                    onload: function() {
                        $("#startdate").val(date);
                        $("#enddate").val(date);
                        $("#starttime").val(config.str("DefaultShiftStart"));
                        $("#endtime").val(config.str("DefaultShiftEnd"));
                        $("#person").personchooser("loadbyid", personid);
                        $("#type").val(1);
                        staff_rota.type_change();
                    }
                });
            });

            $(".asm-staff-rota").on("change", "#weekselector", function() {
                common.route(controller.name + "?flags=" + staff_rota.get_flags_param() + "&start=" + $("#weekselector").select("value"));
            });

            $("#startdate").change(function() {
                $("#enddate").val($("#startdate").val());
            });

            $("#button-clone").button().click(async function() {
                await tableform.show_okcancel_dialog("#dialog-clone", _("Clone"), { width: 500, notblank: [ "newdate" ] });
                let formdata = { mode: "clone", 
                    startdate: format.date(staff_rota.days[0]), 
                    newdate: $("#newdate").val(), 
                    flags: staff_rota.get_flags_param(false) };
                await common.ajax_post(controller.name, formdata);
                header.show_info(_("Rota cloned successfully."));
            });

            $("#button-delete").button().click(async function() {
                let startdate = format.date(staff_rota.days[0]);
                await tableform.delete_dialog(null, _("This will remove ALL rota entries for the week beginning {0}. This action is irreversible, are you sure?").replace("{0}", startdate));
                await common.ajax_post(controller.name, "mode=deleteweek&startdate=" + startdate);
                common.route(controller.name + "?flags=" + staff_rota.get_flags_param() + "&start=" + startdate);
            });

            $("#button-prev").button().click(function() {
                common.route(controller.name + "?flags=" + staff_rota.get_flags_param() + "&start=" + format.date(controller.prevdate));
            });

            $("#button-today").button().click(function() {
                common.route(controller.name + "?flags=" + staff_rota.get_flags_param());
            });

            $("#button-next").button().click(function() { 
                common.route(controller.name + "?flags=" + staff_rota.get_flags_param() + "&start=" + format.date(controller.nextdate));
            });

            $("#flags").change(function() {
                staff_rota.generate_table(); 
            });

            $("#type").change(staff_rota.type_change);

        },

        sync: function() {
            // Load the full set of flags into the select
            html.person_flag_options(null, controller.flags, $("#flags"));
            // Now remove irrelevant built in flags 
            $.each([ "adopter", "banned", "deceased", "donor", "excludefrombulkemail", 
                "giftaid", "homechecked", "member", "retailer", "shelter", "sponsor", "supplier" ], function(i, v) {
                $("#flags option[value='" + v + "']").remove();
            });
            $("#flags").change();
            // Mark set any flags that were passed from the backend as params to the page
            if (controller.flagsel) {
                $.each(controller.flagsel.split(","), function(i, v) {
                    $("#flags option[value='" + v + "']").prop("selected", true); 
                });
                $("#flags").change();
            }
            staff_rota.generate_table();
        },

        destroy: function() {
            common.widget_destroy("#dialog-clone");
            common.widget_destroy("#person");
            tableform.dialog_destroy();
        },

        name: "staff_rota",
        animation: "book",
        title: function() { return _("Staff Rota"); },
        routes: {
            "staff_rota": function() { common.module_loadandstart("staff_rota", "staff_rota?" + this.rawqs); }
        }

    };

    common.module_register(staff_rota);

});
