/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var csvimport = {

        render: function() {
            if (controller.error || controller.errors) {
                // We have an import report, show it
                return [
                    html.content_header(_("Import a CSV file")),
                    '<p class="asm-menu-category">' + _("Errors") + '</p>',
                    csvimport.render_errors(),
                    html.content_footer()
                ].join("\n");
            }
            return [
                html.content_header(_("Import a CSV file")),
                '<div class="centered" style="max-width: 900px; margin-left: auto; margin-right: auto">',
                '<form id="csvform" action="csvimport" method="post" enctype="multipart/form-data">',
                html.info(_("Your CSV file should have a header row with field names ASM recognises. Please see the manual for more information.")),
                '<p>',
                '<input id="cleartables" name="cleartables" type="checkbox" /> ',
                '<label for="cleartables">' + _("Clear tables before importing") + '</label>',
                '</p>',
                '<div id="cleartablesexplain" style="display: none">',
                html.error(_("All existing data in your database will be REMOVED before importing the CSV file. This removal cannot be reversed.")),
                '</div>',
                '<p>',
                '<input id="createmissinglookups" name="createmissinglookups" type="checkbox" /> ',
                '<label for="createmissinglookups">' + _("Create missing lookup values") + '</label>',
                '</p>',
                 '<div id="createmissinglookupsexplain" style="display: none">',
                html.info(_("Any animal types, species, breeds, colors, locations, etc. in the CSV file that aren't already in the database will be created during the import.")),
                '</div>',
                '<p>',
                '<p>',
                '<input id="checkduplicates" name="checkduplicates" type="checkbox" /> ',
                '<label for="checkduplicates">' + _("Merge duplicate records") + '</label>',
                '</p>',
                 '<div id="checkduplicatesexplain" style="display: none">',
                html.info(_("People or animal records that already exist in the database will not be imported again and movement/payment data will be attached to the existing records instead.")),
                '</div>',
                '<p>',
                '<input id="filechooser" name="filechooser" type="file" /><br/>',
                '<button type="button">' + _("Import") + '</button>',
                '</p>',
                '</form>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        render_errors: function() {
            if (controller.error) {
                return html.error(controller.error);
            }
            if (controller.errors) {
                var s = "";
                if (controller.errors.length > 0) {
                    s = "<table><tr><th>" + _("Row") + "</th><th>" + _("Data") + "</th><th>" + _("Error") + "</th></tr>";
                    $.each(controller.errors, function(i, v) {
                        s += "<tr><td>" + v[0] + "</td><td>" + v[1] + "</td><td>" + v[2] + "</td></tr>";
                    });
                    s += "</table>";
                }
                s += html.info(
                        common.ntranslate(controller.errors.length, [
                            _("Import complete with {plural0} error."),
                            _("Import complete with {plural1} errors."),
                            _("Import complete with {plural2} errors."),
                            _("Import complete with {plural3} errors.")
                        ]));
                return s;
            }
        },

        bind: function() {
            $("button").button().click(function() {
                $("button").button("disable");
                $("body").css("cursor", "wait");
                $("#csvform").submit();
            });
            var cme = function() {
                if ($("#createmissinglookups").prop("checked")) {
                    $("#createmissinglookupsexplain").fadeIn();
                }
                else {
                    $("#createmissinglookupsexplain").fadeOut();
                }
            };
            var cte = function() {
                if ($("#cleartables").prop("checked")) {
                    $("#cleartablesexplain").fadeIn();
                }
                else {
                    $("#cleartablesexplain").fadeOut();
                }
            };
            var cde = function() {
                if ($("#checkduplicates").prop("checked")) {
                    $("#checkduplicatesexplain").fadeIn();
                }
                else {
                    $("#checkduplicatesexplain").fadeOut();
                }
            };
            $("#cleartables").click(cte);
            $("#cleartables").keypress(cte);
            $("#createmissinglookups").click(cme);
            $("#createmissinglookups").keypress(cme);
            $("#checkduplicates").click(cde);
            $("#checkduplicates").keypress(cde);
        },

        name: "csvimport",
        animation: "options"

    };

    common.module_register(csvimport);

});
