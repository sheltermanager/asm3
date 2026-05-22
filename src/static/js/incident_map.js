/*global $, jQuery, _, asm, additional, common, config, controller, dlgfx, edit_header, format, geo, header, html, mapping, validate */

$(function() {

    "use strict";

    const incident_map = {

        render: function() {
            let headerheight = $("body").outerHeight() + 50;
            let title = _("Active Incidents");
            if (controller.name == "recent_incident_map") {
                title = _("Recent Incidents");
            }
            return [
                html.content_header(title),
                '<div id="embeddedmap" style="position: absolute;z-index: 1; width: 100%; height: calc(100% - ' + headerheight + 'px); color: #000"></div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
        },

        sync: function() {
        },

        delay: function() {
            let first_valid = "";
            $.each(controller.rows, function(i, v) {
                if (v.DISPATCHLATLONG) {
                    v.latlong = v.DISPATCHLATLONG;
                } else {
                    v.latlong = v.LATLONG;
                }
                if (v.INCIDENTTYPE == 1) {
                    v.popuptext = "<b>" + v.ADDRESS + "</b><br /><a target='_blank' href='animal?id=" + v.ID + "'>" + 
                        v.INCIDENTNAME + " " + _("Reclaimed") + "</a>";
                } else if (v.INCIDENTTYPE == 2) {
                    v.popuptext = "<b>" + v.ADDRESS + "</b><br /><a target='_blank' href='animal?id=" + v.ID + "'>" + 
                        v.INCIDENTNAME + " " + _("Non-Shelter") + "</a>";
                } else {
                    v.popuptext = "<b>" + v.ADDRESS + "</b><br /><a target='_blank' href='incident?id=" + v.ID + "'>" + 
                        v.INCIDENTNAME + " " + common.nulltostr(v.OWNERNAME) + "</a>";
                }
                if (v.latlong && v.latlong.indexOf("0,0") == -1) { first_valid = v.latlong; }
            });
            mapping.draw_map("embeddedmap", 10, first_valid, controller.rows); 
        },

        name: "incident_map",
        animation: "results",
        title: function() {
            if (controller.name == "active_incident_map") {
                return _("Active Incidents");
            } else {
                return _("Recent Incidents");
            }
        },
        routes: {
            "recent_incident_map": function() { common.module_loadandstart("incident_map", "recent_incident_map"); },
            "incident_map": function() { common.module_loadandstart("incident_map", "incident_map"); }
        }

    };

    common.module_register(incident_map);

});

