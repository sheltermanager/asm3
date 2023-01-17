/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const event_find = {

        render: function() {
            return [
                html.content_header(_("Find Event")),
                '<div id="eventsearchform">',
                '<table class="asm-table-layout">',

                '<tr>',
                '<td>',
                '<label for="name">' + _("Name") + '</label>',
                '</td>',
                '<td>',
                '<input id="name" data="name" class="asm-textbox" />',
                '</td>',
                '</tr>',

                '<tr>',
                '<td><label for="eventfrom">' + _("Event Between") + '</label></td>',
                '<td><input id="eventfrom" data="eventfrom" class="asm-textbox asm-datebox" /></td>',
                '<td><label for="eventto">' + _("and") + '</label></td>',
                '<td><input id="eventto" data="eventto" class="asm-textbox asm-datebox" /></td>',
                '</tr>',

                '<tr>',
                '<td><label for="location">' + _("Location") + '</label>',
                '</td>',
                '<td>',
                '<input id="location" data="location" class="asm-textbox" />',
                '</td>',

                '<tr>',
                '<td>',
                '<label for="address">' + _("Address") + '</label>',
                '</td>',
                '<td>',
                '<input id="address" data="address" class="asm-textbox" />',
                '</td>',
                '</tr>',

                '<tr>',
                '<td>',
                '<label for="city">' + _("City") + '</label>',
                '</td>',
                '<td>',
                '<input id="city" data="city" class="asm-textbox" />',
                '</td>',
                '</tr>',

                '<tr id="statecounty">',
                '<td><label for="county">' + _("State") + '</label></td>',
                '<td><input class="asm-textbox newform" maxlength="100" id="county" data="county" type="text" /></td>',
                '</tr>',

                '<tr>',
                '<td><label for="postcode">' + _("Zipcode") + '</label></td>',
                '<td><input class="asm-textbox newform" id="postcode" data="postcode" type="text" /></td>',
                '</tr>',

                '<tr id="countryrow">',
                '<td><label for="country">' + _("Country") + '</label></td>',
                '<td><input class="asm-textbox newform" id="country" data="country" type="text" /></td>',
                '</tr>',

                '</table>',
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

            $("#countryrow").toggle( !config.bool("HideCountry") );
            $("#statecounty").toggle( !config.bool("HideTownCounty") );


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
