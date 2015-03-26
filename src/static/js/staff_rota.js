/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    var dialog = {
        add_title: _("Add rota item"),
        edit_title: _("Edit rota item"),
        close_on_ok: true,
        delete_button: true,
        delete_perm: 'doro',
        columns: 1,
        width: 550,
        fields: [
            { json_field: "OWNERID", post_field: "person", label: _("Person"), type: "person", validation: "notzero" },
            { json_field: "STARTDATETIME", post_field: "startdate", label: _("Starts"), type: "date", validation: "notblank", defaultval: new Date() },
            { json_field: "STARTDATETIME", post_field: "starttime", label: _("at"), type: "time", validation: "notblank", defaultval: "09:00" },
            { json_field: "ENDDATETIME", post_field: "enddate", label: _("Ends"), type: "date", validation: "notblank", defaultval: new Date() },
            { json_field: "ENDDATETIME", post_field: "endtime", label: _("at"), type: "time", validation: "notblank", defaultval: "17:00" },

            { json_field: "ROTATYPEID", post_field: "type", label: _("Type"), type: "select", options: { displayfield: "ROTATYPE", valuefield: "ID", rows: controller.rotatypes }},
            { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
        ]
    };

    var staff_rota = {

        render: function() {
            return [
                tableform.dialog_render(dialog),
                html.content_header(_("Staff Rota")),
                tableform.buttons_render([
                    { id: "prev", icon: "rotate-anti" },
                    { id: "next", icon: "rotate-clock" },
                    { id: "clone", text: _("Copy"), icon: "copy", tooltip: _("Copy the rota this week to another week") }
                ]),
                '<table class="asm-staff-rota">',
                '<thead></thead>',
                '<tbody></tbody>',
                '</table>',
                html.content_footer()
            ].join("\n");
        },

        days: [],

        generate_table: function() {
            // Render the header - one blank column followed by a column
            // for each day of the week.
            var h = [
                '<tr>',
                '<th></th>'
                ],
                css = "",
                i, 
                d = format.date_js(controller.startdate);

            for (i = 0; i < 7; i += 1) {
                css = "";
                if (format.date(d) == format.date(new Date())) { css = 'asm-staff-rota-today'; }
                h.push('<th class="' + css + '">' + format.weekdayname(i) + '. ' + format.monthname(d.getMonth()) + '. ' + d.getDate() + '</th>');
                staff_rota.days.push(d);
                d = common.add_days(d, 1);
            }
            h.push('</tr>');
            $(".asm-staff-rota thead").html(h.join("\n"));

            // Render a row for each person with their rota for the week
            h = [];
            $.each(controller.staff, function(i, p) {
                css = "asm-staff-rota-person-odd";
                if (i % 2 == 0) { css = "asm-staff-rota-person-even"; }
                h.push("<tr>");
                h.push('<td class="' + css + '">');
                h.push('<a href="person_rota?id=' + p.ID + '">' + p.OWNERNAME + '</a>');
                h.push("</td>");
                $.each(staff_rota.days, function(id, d) {
                    h.push('<td data-person="' + p.ID + '" data-date="' + format.date(d) + '" class="asm-staff-rota-cell">');
                    $.each(controller.rows, function(ir, r) {
                        if (r.OWNERID == p.ID && format.date(r.STARTDATETIME) == format.date(d)) {
                            if (r.ROTATYPEID == 1) { 
                                css = 'asm-staff-rota-shift'; 
                                h.push('<a class="asm-staff-rota-shift" href="#" data-id="' + r.ID + '">' + format.time(r.STARTDATETIME) + '-' + format.time(r.ENDDATETIME) + '</a><br />');
                            }
                            else { 
                                h.push('<a class="asm-staff-rota-timeoff" href="#" data-id="' + r.ID + '">' + r.ROTATYPENAME + '</a><br />');
                            }
                        }
                    });
                    h.push('</td>');
                });
                h.push("</tr>");
            });
            $(".asm-staff-rota tbody").html(h.join("\n"));
        },

        bind: function() {

            tableform.dialog_bind(dialog);

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
                    $("#person").personchooser("loadbyid", personid);
                    $("#type").val(1);
                });
            });

            $("#startdate").change(function() {
                $("#enddate").val($("#startdate").val());
            });

            $("#button-clone").button();

            $("#button-prev").button().click(function() {
                window.location = controller.name + "?start=" + format.date(common.subtract_days(staff_rota.days[0], 7));
            });

            $("#button-next").button().click(function() { 
                window.location = controller.name + "?start=" + format.date(common.add_days(staff_rota.days[0], 7));
            });
        },

        sync: function() {
            staff_rota.generate_table();
        }

    };

    common.module(staff_rota, "staff_rota", "book");

});
