/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const boarding_availability = {

        model: function() {
            const dialog = {
                add_title: _("Add booking"),
                edit_title: _("Edit booking"),
                edit_perm: 'coro',
                close_on_ok: false,
                delete_button: true,
                delete_perm: 'doro',
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };
            this.dialog = dialog;
        },

        render: function() {
            this.model();
            return [
                tableform.dialog_render(this.dialog),
                html.content_header(_("Boarding Availability")),
                tableform.buttons_render([
                    { id: "prev", icon: "rotate-anti", tooltip: _("Week beginning {0}").replace("{0}", format.date(controller.prevdate)) },
                    { id: "today", icon: "diary", tooltip: _("This week") },
                    { id: "next", icon: "rotate-clock", tooltip: _("Week beginning {0}").replace("{0}", format.date(controller.nextdate)) },
                    //{ id: "clone", text: _("Clone"), icon: "copy", perm: 'aoro', tooltip: _("Clone the rota this week to another week") },
                    //{ id: "delete", text: _("Delete"), icon: "delete", perm: 'doro', tooltip: _("Delete all rota entries for this week") }
                ]),
                '<table class="asm-boarding-availability">',
                '<thead></thead>',
                '<tbody></tbody>',
                '</table>',
                //html.info(_("To add people to the rota, create new person records with the staff or volunteer flag."), "emptyhint"), 
                html.content_footer()
            ].join("\n");
        },

        sync: function() {
            boarding_availability.generate_table();
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
            boarding_availability.days = [];
            for (i = 0; i < 7; i += 1) {
                css = "";
                if (format.date(d) == format.date(new Date())) { css = 'asm-staff-rota-today'; } else { css = 'asm-staff-rota-day'; }
                h.push('<th class="' + css + '">' + format.weekdayname(i) + '. ' + format.monthname(d.getMonth()) + ' ' + d.getDate() + '</th>');
                boarding_availability.days.push(d);
                d = common.add_days(d, 1);
            }
            h.push('</tr>');
            $(".asm-boarding-availability thead").html(h.join("\n"));
            
            // Render a row for each person with their rota for the week
            h = [];
            $.each(controller.internallocations, function(i, location) {
                h.push("<tr>");
                h.push('<td class="' + css + '" title="' + html.title(title) + '">');
                h.push(location.LOCATIONNAME);
                h.push("</td>");
                $.each(boarding_availability.days, function(id, d) {
                    h.push('<td data-date="' + format.date(d) + '" class="asm-staff-rota-cell">');
                    
                    h.push('</td>');
                });
                h.push("</tr>");
            });
            console.log(h.join("\n"));
            $(".asm-boarding-availability tbody").html(h.join("\n"));
        },

        bind: function() {
            /*$("#button-delete").button().click(async function() {
                let startdate = format.date(staff_rota.days[0]);
                //await tableform.delete_dialog(null, _("This will remove ALL rota entries for the week beginning {0}. This action is irreversible, are you sure?").replace("{0}", startdate));
                //await common.ajax_post(controller.name, "mode=deleteweek&startdate=" + startdate);
                //common.route(controller.name + "?flags=" + staff_rota.get_flags_param() + "&start=" + startdate);
            });*/

            $("#button-prev").button().click(function() {
                common.route(controller.name + "?start=" + format.date(controller.prevdate));
            });

            $("#button-today").button().click(function() {
                common.route(controller.name);
            });

            $("#button-next").button().click(function() { 
                common.route(controller.name + "?start=" + format.date(controller.nextdate));
            });
        },

        name: "boarding_availability",
        animation: "book",
        title: function() { return _("Boarding Availability"); },
        routes: {
            "boarding_availability": function() { common.module_loadandstart("boarding_availability", "boarding_availability?" + this.rawqs); }
        }

    };

    common.module_register(boarding_availability);

});
