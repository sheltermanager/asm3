/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const event_find = {

        render: function() {
            return [
                html.content_header(_("Find Event")),
                '<div id="eventsearchform">',
                '<div class="asm-row">',
                html.search_column([
                    html.search_field_text("name", _("Name")),
                    html.search_field_daterange("eventfrom", "eventto", _("Event Between")),
                    html.search_field_text("location", _("Location")),
                    html.search_field_text("address", _("Address")),
                    html.search_field_text("city", _("City")),
                    html.search_field_text("county", _("State")),
                    html.search_field_text("postcode", _("Zipcode")),
                    html.search_field_text("country", _("Country")),
                ].join("\n")),
                '</div>',
                '</div>',
                '<p class="centered">',
                '<button type="submit" id="searchbutton">' + _("Search") + '</button>',
                '</p>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            $("#searchbutton").button().click(function() {
                common.route("event_find_results?" + $("#eventsearchform input, #eventsearchform select").toPOST());
            });

            // We need to re-enable the return key submitting the form
            $("#eventsearchform").keypress(function(e) {
                if (e.keyCode == 13) {
                    common.route("event_find_results?" + $("#eventsearchform input, #eventsearchform select").toPOST());
                }
            });

            $("#country").closest("tr").toggle( !config.bool("HideCountry") );
            $("#county").closest("tr").toggle( !config.bool("HideTownCounty") );
        },

        name: "event_find",
        animation: "criteria",
        autofocus: "#name",
        title: function() { return _("Find event"); },
        routes: {
            "event_find": function() { common.module_loadandstart("event_find", "event_find"); }
        }

    };

    common.module_register(event_find);

});
