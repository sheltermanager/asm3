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

        show_mini_map: function() {
            setTimeout(() => {
                let first_valid = "";
                $.each(controller.rows, function(i, v) {
                    v.latlong = v.DISPATCHLATLONG;
                    v.popuptext = "<b>" + v.DISPATCHADDRESS + "</b><br /><a target='_blank' href='incident?id=" + v.ACID + "'>" + 
                        v.INCIDENTNAME + " " + common.nulltostr(v.OWNERNAME) + "</a>";
                    if (v.latlong && v.latlong.indexOf("0,0") == -1) { first_valid = v.latlong; }
                });
                mapping.draw_map("embeddedmap", 10, first_valid, controller.rows); 
            }, 50);
        },

        bind: function() {
        },

        sync: function() {
            this.show_mini_map();
        },

        name: "incident_map",
        animation: "results",
        title: function() { return _("Active Incidents"); },
        routes: {
            "incident_map": function() { common.module_loadandstart("incident_map", "incident_map"); }
        }

    };

    common.module_register(incident_map);

});

