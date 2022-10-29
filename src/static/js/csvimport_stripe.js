/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const csvimport_stripe = {

        render: function() {
            return [
                html.content_header(_("Import a Stripe CSV file")),
                '<div style="max-width: 900px; margin-left: auto; margin-right: auto">',
                '<form id="csvform" action="csvimport_stripe" method="post" enctype="multipart/form-data">',
                html.info(_("The CSV file should be created by the Export button on Stripe's payments screen.")),
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
                html.list_to_options(controller.paymentmethods, "ID", "PAYMENTNAME"), 
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="mflags">' + _("Flags") + '</label>',
                '</td>',
                '<td>',
                '<select id="mflags" name="mflags" class="asm-bsmselect" multiple="multiple">',
                '</select>',
                '<input id="flags" name="flags" type="hidden" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="encoding">' + _("Text Encoding") + '</label></td>',
                '<td>',
                '<select id="encoding" class="asm-selectbox" name="encoding">',
                '<option value="utf-8-sig" selected="selected">UTF-8</option>',
                '<option value="cp1252">Windows cp1252</option>',
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
                '<p class="centered">',
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
                $("#flags").val($("#mflags").val()); // Copy mflags to flags so a single value for the list is posted
                $("#import").button("disable");
                $("#csvform").submit();
            });
        },

        sync: function() {
            html.person_flag_options(null, controller.flags, $("#mflags"));
        },

        name: "csvimport_stripe",
        animation: "options",
        autofocus: "#type",
        title: function() { return _("Import a Stripe CSV file"); },
        routes: {
            "csvimport_stripe": function() { common.module_loadandstart("csvimport_stripe", "csvimport_stripe"); }
        }

    };

    common.module_register(csvimport_stripe);

});
