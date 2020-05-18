/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    var csvexport = {

        render: function() {
            return [
                html.content_header(_("Export Animals as CSV")),
                '<div class="centered" style="max-width: 900px; margin-left: auto; margin-right: auto">',
                '<form id="csvform" action="csvexport_animals" method="get">',
                html.info(_("Export a CSV file of animal records that ASM can import into another database.") + '<br/>' +
                    _("Please see the manual for more information.")),
                '<table>',
                '<tr>',
                '<td>',
                '<label for="filter">' + _("Filter") + '</label>',
                '</td>',
                '<td>',
                '<select id="filter" name="filter" class="asm-selectbox">',
                '<option value="all">' + _("All Animals") + '</option>',
                '<option value="shelter">' + _("All On-Shelter Animals") + '</option>',
                '<option value="selshelter">' + _("Selected On-Shelter Animals") + '</option>',
                '<option value="nonshelter">' + _("Non-Shelter Animals") + '</option>',
                '</select>',
                '</td>',
                '</tr>',
                '<tr id="animalsrow">',
                '<td>',
                '<label for="animals">' + _("Animals") + '</label>',
                '</td>',
                '<td>',
                '<input id="animals" name="animals" type="hidden" class="asm-animalchoosermulti" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td></td>',
                '<td><input type="checkbox" name="includeimage" id="includeimage" /> <label for="includeimage">' + _("Include preferred photo") + '</label></td>',
                '</tr>',
                '</table>',
                '</form>',
                '<p>',
                '<button id="submit" type="button">' + _("Export") + '</button>',
                '</p>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            $("#submit").button().click(function() {
                $("#csvform").submit();
            });

            $("#animalsrow").hide();
            $("#filter").change(function() {
                if ($("#filter").select("value") == "selshelter") { 
                    $("#animalsrow").fadeIn(); 
                }
                else {
                    $("#animalsrow").fadeOut(); 
                }
            });
        },

        destroy: function() {
            common.widget_destroy("#animals");
        },

        name: "csvexport",
        animation: "options",
        title: function() { return _("Export Animals as CSV"); },
        routes: {
            "csvexport": function() { common.module_start("csvexport"); }
        }

    };

    common.module_register(csvexport);

});
