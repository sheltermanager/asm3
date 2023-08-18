/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    "use strict";

    const timeline = {

        render: function() {
            let h = [], lastdate, modifier = "";
            h.push('<div id="asm-content" class="ui-helper-reset ui-widget-content ui-corner-all" style="padding: 10px;">');
            h.push('<div class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em">' +
                '<p><span class="ui-icon ui-icon-search"></span>' +
                _("Showing {0} timeline events.").replace("{0}", controller.resultcount)  +
                "</p></div>");
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
                h.push('<p class="asm-timeline-item">' + html.event_text(e, { includeicon: true, includelink: true }) + '</p>');
            });
            h.push("</div>");
            return h.join("\n");
        },

        name: "timeline",
        animation: "results",
        autofocus: "#asm-content a:first",
        title: function() { return _("Timeline"); },
        routes: {
            "timeline": function() { common.module_loadandstart("timeline", "timeline"); }
        }

    };

    common.module_register(timeline);

});
