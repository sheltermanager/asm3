/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    var dialog = {
        add_title: _("Add rota item"),
        edit_title: _("Edit rota item"),
        close_on_ok: true,
        columns: 1,
        width: 550,
        fields: [
            { json_field: "OWNERID", post_field: "person", label: _("Person"), type: "person", validation: "notzero" },
            { json_field: "STARTDATETIME", post_field: "startdate", label: _("Start Date"), type: "date", validation: "notblank", defaultval: new Date() },
            { json_field: "STARTDATETIME", post_field: "starttime", label: _("Start Time"), type: "time", validation: "notblank", defaultval: "09:00" },
            { json_field: "ENDDATETIME", post_field: "enddate", label: _("End Date"), type: "date", validation: "notblank", defaultval: new Date() },
            { json_field: "ENDDATETIME", post_field: "endtime", label: _("End Time"), type: "time", validation: "notblank", defaultval: "17:00" },

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
                    { id: "prev", text: _("Previous"), icon: "rotate-anti" },
                    { id: "next", text: _("Next"), icon: "rotate-clock" },
                    { id: "clone", text: _("Copy"), icon: "copy", tooltip: _("Copy the rota this week to another week") }
                ]),
                '<table class="asm-staff-rota">',
                '<thead></thead>',
                '<tbody></tbody>',
                '</table>',
                html.content_footer()
            ].join("\n");
        },

        generate_table: function() {
            // Render the header - one blank column followed by a column
            // for each day of the week.
            var h = [
                '<tr>',
                '<th></th>'
                ],
                days = [], 
                css = "",
                i, 
                outputday = false,
                d = format.date_js(controller.startdate);

            for (i = 0; i < 7; i += 1) {
                css = "";
                if (format.date(d) == format.date(new Date())) { css = 'asm-staff-rota-today'; }
                h.push('<th class="' + css + '">' + format.weekdayname(i) + '. ' + format.monthname(d.getMonth()) + '. ' + d.getDate() + '</th>');
                days.push(d);
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
                $.each(days, function(id, d) {
                    h.push('<td>');
                    $.each(controller.rows, function(ir, r) {
                        if (r.OWNERID == p.ID && format.date(r.STARTDATETIME) == format.date(d)) {
                            if (r.ROTATYPEID == 1) { 
                                css = 'asm-staff-rota-shift'; 
                                h.push('<a class="asm-staff-rota-shift" href="#" data="' + r.ID + '">' + format.time(r.STARTDATETIME) + '-' + format.time(r.ENDDATETIME) + '</a><br />');
                            }
                            else { 
                                h.push('<a class="asm-staff-rota-timeoff" href="#" data="' + r.ID + '">' + r.ROTATYPENAME + '</a><br />');
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
            $(".asm-staff-rota").on("click", "a", function() {
                var id = $(this).attr("data");
                var row = common.get_row(controller.rows, id, "ID");
                tableform.dialog_show_edit(dialog, row, function() {
                    tableform.fields_update_row(dialog.fields, row);
                    row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                    row.ROTATYPENAME = common.get_field(controller.rotatypes, row.ROTATYPEID, "ROTATYPE");
                    tableform.fields_post(dialog.fields, "mode=update&rotaid=" + row.ID, controller.name, function(response) {
                        staff_rota.generate_table();
                    });
                });
            });
            $("#button-clone").button();
            $("#button-prev").button();
            $("#button-next").button();
        },

        sync: function() {
            staff_rota.generate_table();
        }

    };

    common.module(staff_rota, "staff_rota", "book");

});
