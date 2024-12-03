/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const csvexport = {

        render: function() {
            return [
                html.content_header(_("Export Animals as CSV")),
                '<form id="csvform" action="csvexport_animals" method="get">',
                html.info(_("Export a CSV file of animal records that ASM can import into another database.") + '<br/>' +
                    _("Please see the manual for more information.")),
                tableform.fields_render([
                    { type: "select", name: "filter", label: _("Filter"),
                        options: [ '<option value="all">' + _("All Animals") + '</option>',
                        '<option value="shelter" selected="selected">' + _("All On-Shelter Animals") + '</option>',
                        '<option value="selshelter">' + _("Selected On-Shelter Animals") + '</option>',
                        '<option value="nonshelter">' + _("Non-Shelter Animals") + '</option>',
                        '<option value="where">' + _("Custom WHERE clause") + '</option>' ].join("\n") },
                    { type: "animalmulti", name: "animals", label: _("Animals") },
                    { type: "text", name: "where", label: _("WHERE clause"), 
                        callout: _("Supply a WHERE clause to the animal table. Eg: 'Archived=0 AND ShelterLocation=2'") },
                    { type: "select", name: "media", label: _("Media"), 
                        options: [ '<option value="none" selected="selected">' + _("Do not include media") + '</option>',
                        '<option value="photo">' + _("Include primary photo") + '</option>',
                        '<option value="photos">' + _("Include all photos") + '</option>',
                        '<option value="all">' + _("Include all photos, documents and PDFs") + '</option>' ].join("\n") },
                ], { full_width: false }),
                tableform.buttons_render([
                   { id: "submit", icon: "save", text: _("Export") }
                ], { centered: true }),
                '</form>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            $("#button-submit").button().click(function() {
                $("#csvform").submit();
            });

            $("#animalsrow, #whererow").hide();
            $("#filter").change(function() {
                if ($("#filter").select("value") == "selshelter") { 
                    $("#animalsrow").fadeIn(); 
                }
                else {
                    $("#animalsrow").fadeOut(); 
                }
                if ($("#filter").select("value") == "where") { 
                    $("#whererow").fadeIn(); 
                }
                else {
                    $("#whererow").fadeOut(); 
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
