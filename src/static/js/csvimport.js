/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var csvimport = {

        render: function() {
            return [
                html.content_header(_("Import a CSV file")),
                '<div class="centered" style="max-width: 900px; margin-left: auto; margin-right: auto">',
                '<form id="csvform" action="csvimport" method="post" enctype="multipart/form-data">',
                html.info(_("Your CSV file should have a header row with field names ASM recognises.") + '<br/>' + 
                    _("Please see the manual for more information.")),
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
                '<button id="import" type="button">' + _("Import") + '</button>',
                '</p>',
                '</form>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            $("#import").button().click(function() {
                if (!$("#filechooser").val()) { return; }
                $("#import").button("disable");
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
        animation: "options",
        autofocus: "#cleartables",
        title: function() { return _("Import a CSV file"); },
        routes: {
            "csvimport": function() { common.module_start("csvimport"); }
        }

    };

    common.module_register(csvimport);

});
