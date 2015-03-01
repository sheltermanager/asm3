/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var calendarview = {

        update_events_from_checkboxes: function() {
            var ev = "";
            $("#toggles input:checked").each(function() {
                ev += $(this).attr("data");
            });
            calendarview.calendar_events.data.ev = ev;
            $("#calendar").fullCalendar("removeEvents");
            $("#calendar").fullCalendar("removeEventSource", calendarview.calendar_events);
            $("#calendar").fullCalendar("addEventSource", calendarview.calendar_events);
        },

        calendar_events: {
            url: "calendarview",
            type: "GET",
            data: {
                ev: "d"
            }
        },

        render: function() {
            return [
                html.content_header(_("Calendar View")),
                '<p id="toggles" class="centered">',
                '<span class="asm-calendar-legend">',
                html.icon("diary") + '<input id="toggle-diary" data="d" type="checkbox" class="asm-checkbox" />' + 
                '<label for="toggle-diary">' + _("Diary") + '</label>',
                '</span> ',
                '<span class="asm-calendar-legend">',
                html.icon("vaccination") + '<input id="toggle-vacc" data="v" type="checkbox" class="asm-checkbox" />' + 
                '<label for="toggle-vacc">' + _("Vaccination") + '</label>',
                '</span> ',
                '<span class="asm-calendar-legend">',
                html.icon("medical") + '<input id="toggle-medical" data="m" type="checkbox" class="asm-checkbox" />' + 
                '<label for="toggle-medical">' + _("Medical") + '</label>',
                '</span> ',
                '<span class="asm-calendar-legend">',
                html.icon("test") + '<input id="toggle-test" data="t" type="checkbox" class="asm-checkbox" />' + 
                '<label for="toggle-test">' + _("Test") + '</label>',
                '</span> ',
                '<span class="asm-calendar-legend">',
                html.icon("donation") + '<input id="toggle-donation" data="p" type="checkbox" class="asm-checkbox" />' + 
                '<label for="toggle-donation">' + _("Payment") + '</label>',
                '</span> ',
                '<span class="asm-calendar-legend">',
                html.icon("call") + '<input id="toggle-incident" data="o" type="checkbox" class="asm-checkbox" />' + 
                '<label for="toggle-incident">' + _("Incident followup") + '</label>',
                '</span> ',
                '<span class="asm-calendar-legend">',
                html.icon("transport") + '<input id="toggle-transport" data="r" type="checkbox" class="asm-checkbox" />' + 
                '<label for="toggle-transport">' + _("Transport") + '</label>',
                '</span>',
                '<span class="asm-calendar-legend">',
                html.icon("traploan") + '<input id="toggle-traploan" data="l" type="checkbox" class="asm-checkbox" />' + 
                '<label for="toggle-traploan">' + _("Trap loan") + '</label>',
                '</span>',
                '</p>',
                '<div id="calendar" style="max-width: 900px; margin-left: auto; margin-right: auto;" />',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            $("#calendar").fullCalendar({
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'month,agendaWeek,agendaDay'
                }, 
                editable: false,
                lang: asm.locale,
                firstDay: 1,
                events: [],
                eventRender: function(event, element) {
                    // Need to decode html entities in the title
                    element.find(".fc-event-title").html(event.title);
                    // We extend the default event object to support tooltips and icons
                    if (event.tooltip) { element.prop("title", html.decode(event.tooltip)); }
                    if (event.link) { 
                        element.find(".fc-event-title").wrap('<a style="color: #fff" href="' + event.link + '"></a>');
                    }
                    if (event.icon) { 
                        if (element.find(".fc-event-time").length > 0) {
                            element.find(".fc-event-time").prepend(html.icon(event.icon)); 
                        }
                        else {
                            element.find(".fc-event-title").prepend(html.icon(event.icon)); 
                        }
                    }
                }
            });

            $("#toggles input").change(calendarview.update_events_from_checkboxes);
        },

        sync: function() {

            // If there's an ev parameter, sync our checkboxes
            var ev = common.querystring_param("ev");
            if (!ev) { ev = "dvmtrolp"; }
            $("#toggles input").each(function() {
                if (ev.indexOf( $(this).attr("data") ) != -1) {
                    $(this).prop("checked", true);
                }
                else {
                    $(this).prop("checked", false);
                }
            });

            setTimeout(function() {
                $("#calendar").fullCalendar("today");
                calendarview.update_events_from_checkboxes();
            }, 500);
        }
    };

    common.module(calendarview, "calendarview", "search");

});
