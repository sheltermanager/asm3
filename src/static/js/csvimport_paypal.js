/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const csvimport_paypal = {

        render: function() {
            return [
                html.content_header(_("Import a PayPal CSV file")),
                '<form id="csvform" action="csvimport_paypal" method="post" enctype="multipart/form-data">',
                html.info(_("The CSV file should be created by PayPal's \"All Activity\" report.")),
                tableform.fields_render([
                    { name: "type", type: "select", label: _("Type"), 
                        options: { displayfield: "DONATIONNAME", valuefield: "ID", rows: controller.donationtypes }},
                    { name: "payment", type: "select", label: _("Method"), 
                        options: { displayfield: "PAYMENTNAME", valuefield: "ID", rows: controller.paymentmethods }},
                    { name: "mflags", type: "selectmulti", label: _("Flags"), 
                        xmarkup: '<input id="flags" name="flags" type="hidden" />', options: "" },
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
            $("#button-import").button().click(function() {
                if (!$("#filechooser").val()) { validate.highlight("filechooser"); return; }
                $("#flags").val($("#mflags").val()); // Copy mflags to flags so a single value for the list is posted
                $("#button-import").button("disable");
                $("#csvform").submit();
            });
        },

        sync: function() {
            html.person_flag_options(null, controller.flags, $("#mflags"));
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
