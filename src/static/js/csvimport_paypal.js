/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var csvimport_paypal = {

        render: function() {
            return [
                html.content_header(_("Import a PayPal CSV file")),
                '<div class="centered" style="max-width: 900px; margin-left: auto; margin-right: auto">',
                '<form id="csvform" action="csvimport_paypal" method="post" enctype="multipart/form-data">',
                html.info(_("The CSV file should be created by PayPal's \"All Activity\" report.")),
                '<table>',
                '<tr>',
                '<td>',
                '<label for="type">' + _("Type") + '</label>',
                '</td>',
                '<td>',
                '<select id="type" name="type" class="asm-selectbox">',
                html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"), 
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="payment">' + _("Method") + '</label>',
                '</td>',
                '<td>',
                '<select id="payment" name="payment" class="asm-selectbox">',
                html.list_to_options(controller.paymenttypes, "ID", "PAYMENTNAME"), 
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="flags">' + _("Flags") + '</label>',
                '</td>',
                '<td>',
                '<select id="flags" name="flags" class="asm-bsmselect" multiple="multiple">',
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td></td>',
                '<td>',
                '<input id="filechooser" name="filechooser" type="file" /><br/>',
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
        },

        sync: function() {
            html.person_flag_options(null, controller.flags, $("#flags"));
        },

        name: "csvimport_paypal",
        animation: "options",
        autofocus: "#type",
        title: function() { return _("Import a PayPal CSV file"); },
        routes: {
            "csvimport_paypal": function() { common.module_loadandstart("csvimport_paypal", "csvimport_paypal"); }
        }

    };

    common.module_register(csvimport_paypal);

});
