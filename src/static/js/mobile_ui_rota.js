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
            let date = new Date();
            date = new Date(date.getFullYear(), date.getMonth(), date.getDate());
            while (date.getDay() != controller.firstdow) {
                date.setDate(date.getDate() - 1); // To do - tested this in Chrome. Need to check that this is globally acceptable
            }
            let o = '<table cellpadding=5>'
            let count = 0;
            while (count < 7) {
                o += '<tr><th>' + daysofweek[date.getDay()] + '</th><td>';
                controller.rotadata.forEach(function(rotarow) {
                    let fromyear = parseInt(rotarow.STARTDATETIME.split("-")[0]);
                    let frommonth = parseInt(rotarow.STARTDATETIME.split("-")[1]) - 1;
                    let fromday = parseInt(rotarow.STARTDATETIME.split("-")[2].split("T")[0]);
                    let startdatetime = new Date(fromyear, frommonth, fromday);

                    let toyear = parseInt(rotarow.ENDDATETIME.split("-")[0]);
                    let tomonth = parseInt(rotarow.ENDDATETIME.split("-")[1]) - 1;
                    let today = parseInt(rotarow.ENDDATETIME.split("-")[2].split("T")[0]);
                    let enddatetime = new Date(toyear, tomonth, today);
                    

                    if (startdatetime <= date && enddatetime >= date) {
                        o += rotarow.WORKTYPENAME;
                        let starttime = "00:00";
                        let endtime = "23:59";
                        if (startdatetime.toISOString() == date.toISOString()) { // Added the toISOStrings as would not work without although I couldn't fingure out why - Adam.
                            starttime = rotarow.STARTDATETIME.split("T")[1].slice(0, 5);
                        }
                        if (enddatetime.toISOString() == date.toISOString()) { // Added the toISOStrings as would not work without although I couldn't fingure out why - Adam.
                            endtime = rotarow.ENDDATETIME.split("T")[1].slice(0, 5);
                        }
                        o += ' ' + starttime + ' to ' + endtime;
                    }
                });
                o += '</td></tr>';
                date.setDate(date.getDate() + 1); // To do - tested this in Chrome. Need to check that this is globally acceptable
                count++;
            }
            o += '</table>';
            $("#hp-rota").append(o);
        } else {
            $("#hp-rota").hide();
        }
    }
}
