/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const csvimport = {

        render: function() {
            return [
                html.content_header(_("Import a CSV file")),
                '<form id="csvform" action="csvimport" method="post" enctype="multipart/form-data">',
                html.info(_("Your CSV file should have a header row with field names ASM recognises.") + '<br/>' + 
                    _("Please see the manual for more information.")),
                tableform.fields_render([
                    { name: "cleartables", type: "check", label: _("Delete database before importing"), labelclasses: "asm-flag-dangerous",
                        callout: _("All existing data and media in your database will be REMOVED before importing the CSV file.") },
                    { name: "createmissinglookups", type: "check", label: _("Create missing lookup values"), 
                        callout: _("Any animal types, species, breeds, colors, locations, etc. in the CSV file that aren't already in the database will be created during the import.") },
                    { name: "prefixanimalcodes", type: "check", label: _("Prefix animal codes"), 
                        callout: _("Animal records in the file will have a prefix added to their ANIMALCODE column to prevent clashes with existing animals in your database.") },
                    { name: "entrytoday", type: "check", label: _("Set entry date to today"), 
                        callout: _("Animal records in the file will have their ANIMALENTRYDATE overridden to today. Useful if the animals are being transferred into your shelter.") },
                    { name: "dryrun", type: "check", label: _("Dry run"), 
                        callout: _("CSV data will be validated and checked for any problems, but no changes will be made to the database.") },
                    { name: "encoding", type: "select", label: _("Text Encoding"), 
                        options: '<option value="utf-8-sig" selected="selected">UTF-8</option>' +
                            '<option value="utf16">UTF-16</option>' +
                            '<option value="cp1252">cp1252 (Excel USA/Western Europe)</option>' },
                    { name: "filechooser", type: "file", label: _("File") }
                ], { full_width: false }),
                tableform.buttons_render([
                   { id: "import", icon: "save", text: _("Import") }
                ], { centered: true }),
                '</form>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            $("#dryrun").change(function() {
                $("#cleartablesrow").toggle();
                $("#createmissinglookupsrow").toggle();
                $("#prefixanimalcodesrow").toggle();
                $("#entrytodayrow").toggle();
            });

            $("#button-import").button().click(function() {
                if (!$("#filechooser").val()) { validate.highlight("filechooser"); return; }
                $("#button-import").button("disable");
                $("#csvform").submit();
            });
            // Do not show the clear down option for large databases
            $("#cleartablesrow").toggle(!controller.islargedb);
        },

        sync: function() {
        },

        name: "csvimport",
        animation: "options",
        autofocus: "#cleartables",
        title: function() { return _("Import a CSV file"); },
        routes: {
            "csvimport": function() { common.module_start("csvimport"); }
        }

    };

    common.module_register(csvimport);

});
