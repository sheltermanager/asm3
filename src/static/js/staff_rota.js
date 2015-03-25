/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    var staff_rota = {

        render: function() {
            return [
                html.content_header(_("Staff Rota")),
                tableform.buttons_render([
                    { id: "prev", text: _("Previous"), icon: "rotate-anti" },
                    { id: "next", text: _("Next"), icon: "rotate-clock" },
                    { id: "clone", text: _("Copy"), icon: "copy", tooltip: _("Copy the rota this week to another week") }
                ]),
                staff_rota.render_table(),
                html.content_footer()
            ].join("\n");
        },

        render_table: function() {
            // Render the header - one blank column followed by a column
            // for each day of the week.
            var h = [
                '<table class="asm-staff-rota">',
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

            // Render a row for each person with their rota for the week
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
                                h.push('<span class="asm-staff-rota-shift">' + format.time(r.STARTDATETIME) + '-' + format.time(r.ENDDATETIME) + '</span><br />');
                            }
                            else { 
                                h.push('<span class="asm-staff-rota-timeoff">' + r.ROTATYPENAME + '</span><br />');
                            }
                        }
                    });
                    h.push('</td>');
                });
                h.push("</tr>");
            });

            h.push('</table>');
            return h.join("\n");
        },

        bind: function() {
            $("#button-clone").button();
            $("#button-prev").button();
            $("#button-next").button();
        }

    };

    common.module(staff_rota, "staff_rota", "book");

});
