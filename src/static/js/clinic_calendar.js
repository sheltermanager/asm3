/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const clinic_calendar = {

        update_events: function() {
            clinic_calendar.calendar_events.data.apptfor = $("#consultant").select("value");
            $("#calendar").fullCalendar("removeEvents");
            $("#calendar").fullCalendar("removeEventSource", clinic_calendar.calendar_events);
            $("#calendar").fullCalendar("addEventSource", clinic_calendar.calendar_events);
        },

        calendar_events: {
            url: "calendar_events",
            type: "GET",
            data: {
                ev: "c",
                apptfor: ""
            }
        },

        render: function() {
            return [
                html.content_header(_("Clinic Calendar")),
                '<p id="toggles" class="asm-calendar-legends centered">',
                '<select id="consultant" class="asm-selectbox">',
                '<option value="">' + _("(everyone)") + '</option>',
                html.list_to_options(controller.forlist, "USERNAME", "USERNAME"),
                '</select>',
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
                    if (event.tooltip) { element.prop("title", html.decode(event.tooltip)); }
                    if (event.link) { title.wrap('<a style="color: #fff" href="' + event.link + '"></a>'); }
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

            $("#consultant").change(clinic_calendar.update_events);
        },

        sync: function() {
            // If there's an apptfor parameter, sync our checkboxes
            let apptfor = common.querystring_param("apptfor");
            $("#consultant").select("value", apptfor);
            setTimeout(function() {
                $("#calendar").fullCalendar("today");
                clinic_calendar.update_events();
            }, 500);
        },

        name: "clinic_calendar",
        animation: "search",
        autofocus: "#consultant", 
        title: function() { return _("Clinic Calendar"); },
        routes: {
            "clinic_calendar": function() { 
                return common.module_loadandstart("clinic_calendar", "clinic_calendar?" + this.rawqs);
            }
        }

    };

    common.module_register(clinic_calendar);

});
