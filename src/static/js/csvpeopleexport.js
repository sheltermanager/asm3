/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const csvpeopleexport = {

        render: function() {
            return [
                html.content_header(_("Export People as CSV")),
                '<form id="csvpeopleform" action="csvexport_people" method="get">',
                html.info(_("Export a CSV file of person records that ASM can import into another database.") + '<br/>' +
                    _("Please see the manual for more information.")),
                tableform.fields_render([
                    { type: "select", name: "filter", label: _("Filter"),
                        options: [ '<option value="all">' + _("All People") + '</option>',
                        '<option value="flaggedpeople">' + _("People with flags") + '</option>',
                        '<option value="where">' + _("Custom WHERE clause") + '</option>' ].join("\n") },
                    { type: "selectmulti", name: "flagselect", label: _("Flags") },
                    { type: "hidden", name: "flags" },
                    { type: "text", name: "where", label: _("WHERE clause"), 
                        callout: _("Supply a WHERE clause to the animal table. Eg: 'OwnerPostCode LIKE 'S66%''") },
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

        sync: function() {
            html.person_flag_options(false, controller.flags, $("#flagselect"));
        },

        bind: function() {
            $("#button-submit").button().click(function() {
                $("#csvpeopleform").submit();
            });
            $("#flagselectrow, #whererow").hide();
            $("#filter").change(function() {
                if ($("#filter").select("value") == "flaggedpeople") { 
                    $("#flagselectrow").fadeIn(); 
                }
                else {
                    $("#flagselectrow").fadeOut(); 
                }
                if ($("#filter").select("value") == "where") { 
                    $("#whererow").fadeIn(); 
                }
                else {
                    $("#whererow").fadeOut(); 
                }
            });
            $("#flagselect").change(function() {
                let flagvalues = $("#flagselect").val().join(",");
                $("#flags").val(flagvalues);
            });
        },

        destroy: function() {
            common.widget_destroy("#animals");
        },

        name: "csvpeopleexport",
        animation: "options",
        title: function() { return _("Export People as CSV"); },
        routes: {
            "csvpeopleexport": function() { common.module_start("csvpeopleexport"); }
        }

    };

    common.module_register(csvpeopleexport);

});
