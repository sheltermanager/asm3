/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const boarding_availability = {

        render: function() {
            return "<p>Hello World</p>"
        },

        name: "boarding_availability",
        animation: "book",
        title: function() { return _("Boarding Availability"); },
        routes: {
            "boarding_availability": function() { common.module_loadandstart("boarding_availability", "boarding_availability?" + this.rawqs); }
        }

    };

    common.module_register(boarding_availability);

});
