/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var csvexport = {

        render: function() {
            return [
                html.content_header(_("Export Animals as CSV")),
                '<div class="centered" style="max-width: 900px; margin-left: auto; margin-right: auto">',
                '<form id="csvform" action="csvexport" method="post">',
                html.info(_("Export a CSV file of animal records that ASM can import into another database.") + '<br/>' +
                    _("Please see the manual for more information.")),
                '<table>',
                '<tr>',
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
                if (!$("#animals").val()) { return; }
                $("#csvform").submit();
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
