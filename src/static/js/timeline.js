/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    var timeline = {

        render: function() {
            var h = [], lastdate, modifier = "";
            h.push('<div id="asm-content" class="ui-helper-reset ui-widget-content ui-corner-all" style="padding: 10px;">');
            if (controller.explain != "") {
                h.push('<div class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em">' +
                    '<p><span class="ui-icon ui-icon-search" style="float: left; margin-right: .3em;"></span>' +
                    controller.explain + "</p></div>");
            }
            if (controller.recent.length == 0) {
                h.push('<p class="asm-search-result">' + _("No results found.") + '</p>');
            }
            $.each(controller.recent, function(i, e) {
                if (lastdate != format.date(e.EVENTDATE)) {
                    lastdate = format.date(e.EVENTDATE);
                    modifier = "";
                    if (lastdate == format.date(new Date())) {
                        modifier = ": " + _("today");
                    }
                    if (lastdate == format.date(common.subtract_days(new Date(), 1))) {
                        modifier = ": " + _("yesterday");
                    }
                    h.push('<p class="asm-timeline-large-date">' + lastdate + ' ' + modifier + '</p>');
                }
                h.push('<p class="asm-timeline-item">' + html.event_text(e) + '</p>');
            });
            h.push("</div>");
            return h.join("\n");
        },

        name: "timeline",
        animation: "results"

    };

    common.module_register(timeline);

});
