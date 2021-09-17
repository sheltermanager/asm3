/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const csvimport = {

        render: function() {
            return [
                html.content_header(_("Import a CSV file")),
                '<div class="centered" style="max-width: 900px; margin-left: auto; margin-right: auto">',
                '<form id="csvform" action="csvimport" method="post" enctype="multipart/form-data">',
                html.info(_("Your CSV file should have a header row with field names ASM recognises.") + '<br/>' + 
                    _("Please see the manual for more information.")),
                '<table class="leftalign">',
                '<tr>',
                '<td></td>',
                '<td>',
                '<input id="cleartables" name="cleartables" type="checkbox" data-x="cleartablesexplain" /> ',
                '<label for="cleartables">' + _("Delete database before importing") + '</label>',
                '</p>',
                '<div id="cleartablesexplain" style="display: none">',
                html.error(_("All existing data and media in your database will be REMOVED before importing the CSV file.") + "<br/>" +
                    _("This removal is permanent and cannot be reversed, are you absolutely sure you wish to do this?")),
                '</div>',
                '<p>',
                '<input id="createmissinglookups" name="createmissinglookups" type="checkbox" data-x="createmissinglookupsexplain"/> ',
                '<label for="createmissinglookups">' + _("Create missing lookup values") + '</label>',
                '</p>',
                 '<div id="createmissinglookupsexplain" style="display: none">',
                html.info(_("Any animal types, species, breeds, colors, locations, etc. in the CSV file that aren't already in the database will be created during the import.")),
                '</div>',
                '<p>',
                '<p>',
                '<input id="checkduplicates" name="checkduplicates" type="checkbox" data-x="checkduplicatesexplain" /> ',
                '<label for="checkduplicates">' + _("Merge duplicate records") + '</label>',
                '</p>',
                 '<div id="checkduplicatesexplain" style="display: none">',
                html.info(_("People or animal records that already exist in the database will not be imported again and movement/payment data will be attached to the existing records instead.")),
                '</div>',
                '<p>',
                '<p>',
                '<input id="prefixanimalcodes" name="prefixanimalcodes" type="checkbox" data-x="prefixanimalcodesexplain" /> ',
                '<label for="prefixanimalcodes">' + _("Prefix animal codes") + '</label>',
                '</p>',
                 '<div id="prefixanimalcodesexplain" style="display: none">',
                html.info(_("Animal records in the file will have a prefix added to their ANIMALCODE column to prevent clashes with existing animals in your database.")),
                '</div>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                _("Text Encoding"),
                '</td>',
                '<td>',
                '<select id="encoding" name="encoding">',
                '<option value="utf-8-sig" selected="selected">UTF-8</option>',
                '<option value="utf16">UTF-16</option>',
                '<option value="cp1252">cp1252 (Excel USA/Western Europe)</option>',
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td></td>',
                '<td>',
                '<input id="filechooser" name="filechooser" type="file" />',
                '</td>',
                '</tr>',
                '</table>',
                '<p>',
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
            $("input[type='checkbox']").click(function() {
                if ($(this).prop("checked")) {
                    $("#" + $(this).attr("data-x")).fadeIn();
                }
                else {
                    $("#" + $(this).attr("data-x")).fadeOut();
                }
            });
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
