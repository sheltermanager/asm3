/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    var staff_rota = {

        model: function() {
            var dialog = {
                add_title: _("Add rota item"),
                edit_title: _("Edit rota item"),
                edit_perm: 'coro',
                close_on_ok: true,
                delete_button: true,
                delete_perm: 'doro',
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "OWNERID", post_field: "person", personmode: "brief", personfilter: "volunteerandstaff", 
                        label: _("Person"), type: "person", validation: "notzero" },
                    { json_field: "ROTATYPEID", post_field: "type", label: _("Type"), type: "select", 
                        options: { displayfield: "ROTATYPE", valuefield: "ID", rows: controller.rotatypes }},
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
                    { id: "delete", text: _("Delete"), icon: "delete", perm: 'doro', tooltip: _("Delete all rota entries for this week") }
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
            var h = [ '<tr>' ],
                css = "",
                title = "",
                i, 
                d = format.date_js(controller.startdate),
                year = d.getFullYear(),
                weekno = format.date_weeknumber(d);

            h.push('<th>' + _("{0}, Week {1}").replace("{0}", year).replace("{1}", weekno) + '</th>');
            staff_rota.days = [];
            for (i = 0; i < 7; i += 1) {
                css = "";
                if (format.date(d) == format.date(new Date())) { css = 'asm-staff-rota-today'; }
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
                h.push("<tr>");
                h.push('<td class="' + css + '" title="' + html.title(title) + '">');
                h.push('<a href="person_rota?id=' + p.ID + '" class="' + html.title(title) + '">' + p.OWNERNAME + '</a>');
                h.push("</td>");
                $.each(staff_rota.days, function(id, d) {
                    h.push('<td data-person="' + p.ID + '" data-date="' + format.date(d) + '" class="asm-staff-rota-cell">');
                    $.each(controller.rows, function(ir, r) {
                        if (r.OWNERID == p.ID && format.date_in_range(d, r.STARTDATETIME, r.ENDDATETIME, true)) {
                            var period = format.time(r.STARTDATETIME, "%H:%M") + ' - ' + format.time(r.ENDDATETIME, "%H:%M");
                            if (r.ROTATYPEID == 1) { 
                                css = 'asm-staff-rota-shift'; 
                                h.push('<a class="asm-staff-rota-shift" href="#" data-id="' + r.ID + '">' + 
                                    period + '</a><br />');
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

        render_clonedialog: function() {
            return [
                '<div id="dialog-clone" style="display: none" title="' + html.title(_("Clone Rota")) + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="newdate">' + _("To week beginning") + '</label></td>',
                '<td><input id="newdate" data="newdate" type="text" data-nopast="true" data-onlydays="1" class="asm-textbox asm-datebox" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        bind_clonedialog: function() {

            var clonebuttons = { };
            clonebuttons[_("Clone")] = function() {
                $("#dialog-clone label").removeClass("ui-state-error-text");
                if (!validate.notblank([ "newdate" ])) { return; }
                $("#dialog-clone").disable_dialog_buttons();
                var newdate = encodeURIComponent($("#newdate").val());
                common.ajax_post(controller.name, "mode=clone&startdate=" + format.date(staff_rota.days[0]) + "&newdate=" + newdate, function() {
                    $("#dialog-clone").dialog("close");
                    $("#dialog-clone").enable_dialog_buttons();
                    header.show_info(_("Rota cloned successfully."));
                });
            };
            clonebuttons[_("Cancel")] = function() {
                $("#dialog-clone").dialog("close");
            };

            $("#dialog-clone").dialog({
                autoOpen: false,
                width: 500,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.edit_show,
                hide: dlgfx.edit_hide,
                buttons: clonebuttons
            });

        },


        bind: function() {

            var dialog = this.dialog;
            tableform.dialog_bind(dialog);
            staff_rota.bind_clonedialog();

            $(".asm-staff-rota").on("click", "a", function(e) {
                var id = $(this).attr("data-id");
                var row = common.get_row(controller.rows, id, "ID");
                tableform.dialog_show_edit(dialog, row, function() {
                    tableform.fields_update_row(dialog.fields, row);
                    row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                    row.ROTATYPENAME = common.get_field(controller.rotatypes, row.ROTATYPEID, "ROTATYPE");
                    tableform.fields_post(dialog.fields, "mode=update&rotaid=" + row.ID, controller.name, function(response) {
                        staff_rota.generate_table();
                    });
                }, 
                null,
                function(row) {
                    common.ajax_post(controller.name, "mode=delete&ids=" + id, function() {
                        common.delete_row(controller.rows, id, "ID");
                        staff_rota.generate_table();
                        tableform.dialog_close();
                    }, function() {
                        tableform.dialog_close();   
                    });
                });
                return false;
            });

            $(".asm-staff-rota").on("click", "td", function(e) {
                var personid = $(this).attr("data-person");
                var date = $(this).attr("data-date");
                if (!personid && !date) { return; }
                tableform.dialog_show_add(dialog, function() {
                    tableform.fields_post(dialog.fields, "mode=create", controller.name, function(response) {
                        var row = {};
                        row.ID = response;
                        tableform.fields_update_row(dialog.fields, row);
                        row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                        row.ROTATYPENAME = common.get_field(controller.rotatypes, row.ROTATYPEID, "ROTATYPE");
                        controller.rows.push(row);
                        staff_rota.generate_table();
                    });
                }, function() {
                    $("#startdate").val(date);
                    $("#enddate").val(date);
                    $("#starttime").val(config.str("DefaultShiftStart"));
                    $("#endtime").val(config.str("DefaultShiftEnd"));
                    $("#person").personchooser("loadbyid", personid);
                    $("#type").val(1);
                });
            });

            $("#startdate").change(function() {
                $("#enddate").val($("#startdate").val());
            });

            $("#button-clone").button().click(function() {
                $("#dialog-clone").dialog("open");
            });

            $("#button-delete").button().click(function() {
                var startdate = format.date(staff_rota.days[0]);
                tableform.delete_dialog(function() {
                    common.ajax_post(controller.name, "mode=deleteweek&startdate=" + startdate, function() {
                        window.location = controller.name + "?start=" + startdate;
                    });
                }, _("This will remove ALL rota entries for the week beginning {0}. This action is irreversible, are you sure?").replace("{0}", startdate));
            });

            $("#button-prev").button().click(function() {
                window.location = controller.name + "?start=" + format.date(controller.prevdate);
            });

            $("#button-today").button().click(function() {
                window.location = controller.name;
            });

            $("#button-next").button().click(function() { 
                window.location = controller.name + "?start=" + format.date(controller.nextdate);
            });
        },

        sync: function() {
            staff_rota.generate_table();
        },

        name: "staff_rota",
        animation: "book"

    };

    common.module_register(staff_rota);

});
