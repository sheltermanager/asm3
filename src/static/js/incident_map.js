/*global $, jQuery, _, asm, additional, common, config, controller, dlgfx, edit_header, format, geo, header, html, mapping, validate */

$(function() {

    "use strict";

    const incident_map = {

        render: function() {
            return [
                html.content_header(_("Active Incidents")),
                '<div id="embeddedmap" style="z-index: 1; width: 100%; height: 600px; color: #000"></div>',
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
                v.latlong = v.LATLONG;
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
            if (controller.name == "incident_map") {
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

