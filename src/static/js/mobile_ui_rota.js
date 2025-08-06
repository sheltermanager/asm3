/*global $, jQuery, controller */
/*global common, config, format, html */
/*global _, mobile, mobile_ui_addanimal, mobile_ui_animal, mobile_ui_addanimal, mobile_ui_person */
/*global mobile_ui_stock: true */

"use strict";

const mobile_ui_rota = {

    bind: () => {

    },

    sync: () => {
        if (controller.rotadata) {
            let daysofweek = [_("Sun"), _("Mon"), _("Tue"), _("Wed"), _("Thu"), _("Fri"), _("Sat")];
            let date = common.today_no_time();
            let o = '<table cellpadding=5>';
            $.each([1, 2, 3, 4, 5, 6, 7], function(i, count) {
                o += '<tr><th>' + daysofweek[date.getDay()] + '</th><td>';
                $.each(controller.rotadata, function(i, rotarow) {
                    let startdatetime = format.date_js(rotarow.STARTDATETIME, true);
                    let enddatetime = format.date_js(rotarow.ENDDATETIME, true);
                    if (startdatetime <= date && enddatetime >= date) {
                        o += rotarow.WORKTYPENAME;
                        let starttime = "00:00";
                        let endtime = "23:59";
                        if (startdatetime.getTime() == date.getTime()) {
                            starttime = format.time(rotarow.STARTDATETIME, '%H:%M');
                        }
                        if (enddatetime.toISOString() == date.toISOString()) {
                            endtime = format.time(rotarow.ENDDATETIME, '%H:%M');
                        }
                        o += ' ' + starttime + ' to ' + endtime;
                    }
                });
                o += '</td></tr>';
                date.setDate(date.getDate() + 1);
            });
            o += '</table>';
            $("#hp-rota .card-body").append(o);
        } else {
            $("#hp-rota").hide();
        }
    }
};
