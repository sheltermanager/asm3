/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const calendarview = {

        update_events_from_checkboxes: function() {
            let ev = "";
            $("#toggles input:checked").each(function() {
                ev += $(this).attr("data");
            });
            calendarview.calendar_events.data.ev = ev;
            $("#calendar").fullCalendar("removeEvents");
            $("#calendar").fullCalendar("removeEventSource", calendarview.calendar_events);
            $("#calendar").fullCalendar("addEventSource", calendarview.calendar_events);
        },

        calendar_events: {
            url: "calendar_events",
            type: "GET",
            data: {
                ev: "d"
            }
        },

        render: function() {
            const chk = function(id, data, icon, label) {
                return '<span class="asm-calendar-legend">' + 
                    html.icon(icon) + 
                    '<input id="' + id + '" data="' + data + '" type="checkbox" class="asm-checkbox" /> ' +
                    '<label for="' + id + '">' + label + '</label>' +
                    '</span> ';
            };
            return [
                html.content_header(_("Calendar View")),
                '<p id="toggles" class="asm-calendar-legends centered">',
                chk("toggle-diary", "d", "diary", _("Diary")),
                chk("toggle-vacc", "v", "vaccination", _("Vaccination")),
                chk("toggle-medical", "m", "medical", _("Medical")),
                chk("toggle-test", "t", "test", _("Test")),
                chk("toggle-boarding", "b", "boarding", _("Boarding")),
                chk("toggle-clinic", "c", "health", _("Clinic")),
                chk("toggle-donation", "p", "donation", _("Payment")),
                chk("toggle-incident", "o", "call", _("Incident followup")),
                chk("toggle-transport", "r", "transport", _("Transport")),
                chk("toggle-traploan", "l", "traploan", _("Equipment loan")),
                '</p>',
                '<div id="calendar" style="max-width: 900px; margin-left: auto; margin-right: auto;"></div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            $("#calendar").fullCalendar({
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'month,agendaWeek,agendaDay,listMonth'
                }, 
                isRTL: (asm.locale == "ar" || asm.locale == "he"),
                editable: false,
                firstDay: config.integer("FirstDayOfWeek"),
                eventLimit: true,
                events: [],
                eventRender: function(event, element) {
                    let title = element.find(".fc-title"),
                        listtitle = element.find(".fc-list-item-title a"),
                        time = element.find(".fc-time");
                    // Need to decode html entities in the title
                    title.html(event.title);
                    listtitle.html(event.title);
                    // We extend the default event object to support tooltips and icons
                    if (event.tooltip) { 
                        element.prop("title", html.decode(event.tooltip)); 
                    }
                    if (event.fgcol) {
                        element.css("color", event.fgcol);
                        listtitle.css("color", event.fgcol);
                    }
                    if (event.bgcol) {
                        element.css("background-color", event.bgcol);
                        element.css("border-color", event.bgcol);
                    }
                    if (event.link) { 
                        title.wrap('<a style="color: #fff" href="' + event.link + '"></a>');
                        listtitle.prop("href", event.link);
                        if (event.tooltip) { listtitle.html(event.tooltip); } // Use the more detailed version in the list
                    }
                    if (event.icon) { 
                        if (time.length > 0) {
                            time.prepend(html.icon(event.icon)); 
                        }
                        else {
                            title.prepend(html.icon(event.icon)); 
                        }
                    }
                },
                // Use ASM's translations
                buttonText: { day: _("Day"), today: _("Today"), month: _("Month"), week: _("Week"), list: _("List") },
                monthNames: [ _("January"), _("February"),_("March"),_("April"),_("May"),_("June"),
                _("July"),_("August"),_("September"),_("October"),_("November"),_("December")],
                monthNamesShort: [_("Jan"), _("Feb"), _("Mar"), _("Apr"), _("May"), _("Jun"),
                _("Jul"), _("Aug"), _("Sep"), _("Oct"), _("Nov"), _("Dec")],
                dayNames: [_("Sunday"), _("Monday"), _("Tuesday"), _("Wednesday"), _("Thursday"), _("Friday"), _("Saturday")],
                dayNamesShort: [_("Sun"), _("Mon"), _("Tue"), _("Wed"), _("Thu"), _("Fri"), _("Sat")]
            });

            $("#toggles input").change(calendarview.update_events_from_checkboxes);
        },

        sync: function() {

            // If there's an ev parameter, sync our checkboxes
            let ev = common.querystring_param("ev");
            if (!ev) { ev = "dvmtbcrolp"; }
            $("#toggles input").each(function() {
                if (ev.indexOf( $(this).attr("data") ) != -1) {
                    $(this).prop("checked", true);
                }
                else {
                    $(this).prop("checked", false);
                }
            });

            if (config.bool("DisableAnimalControl")) { $(".taganimalcontrol").hide(); }
            if (config.bool("DisableBoarding")) { $(".tagboarding").hide(); }
            if (config.bool("DisableClinic")) { $(".tagclinic").hide(); }
            if (config.bool("DisableTransport")) { $(".tagtransport").hide(); }
            if (config.bool("DisableTrapLoan")) { $(".tagtraploan").hide(); }
        },

        delay: function() {
            $("#calendar").fullCalendar("today");
            calendarview.update_events_from_checkboxes();
        },

        name: "calendarview",
        animation: "search",
        autofocus: "#toggle-diary", 
        title: function() { return _("Calendar view"); },
        routes: {
            "calendarview": function() { 
                return common.module_loadandstart("calendarview", "calendarview?" + this.rawqs);
            }
        }

    };

    common.module_register(calendarview);

});
