/*global $, jQuery, FileReader, Modernizr, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const maint_find_replace = {

        render: function() {
            let s = [
                html.content_header(_("Find/replace")),
                '<table id="findreplacetable">',
                '<tbody>',
                '<tr><td>' + _("Vaccine manufacturer") + '</td><td>',
                tableform.fields_render([
                    { post_field: "manufacturerfind", type: "select", justwidget: true,
                        options: controller.manufacturers
                    }
                ]),
                '</td><td>' + _("replace with") + '</td>',
                '<td>',
                tableform.fields_render([
                    { post_field: "manufacturerreplace", type: "autotext", justwidget: true,
                        options: controller.manufacturers
                    }
                ]),
                '</td>',
                '<td><button id="replacemanufacturers">' + _("Go") + '</button></td></tr>',
                '<tr><td>' + _("City") + '</td><td>',
                tableform.fields_render([
                    { post_field: "cityfind", type: "select", justwidget: true,
                        options: controller.towns
                    }
                ]),
                '</td><td>' + _("replace with") + '</td>',
                '<td>',
                tableform.fields_render([
                    { post_field: "cityreplace", type: "autotext", justwidget: true,
                        options: controller.towns
                    }
                ]),
                '</td>',
                '<td><button id="replacecities">' + _("Go") + '</button></td></tr>',
                '<tr><td>' + _("State") + '</td><td>',
                tableform.fields_render([
                    { post_field: "statefind", type: "select", justwidget: true,
                        options: controller.counties
                    }
                ]),
                '</td><td>' + _("replace with") + '</td>',
                '<td>',
                tableform.fields_render([
                    { post_field: "statereplace", type: "autotext", justwidget: true,
                        options: controller.counties
                    }
                ]),
                '</td>',
                '<td><button id="replacestates">' + _("Go") + '</button></td></tr>',
                '</tbody>',
                '</table>',
                html.content_footer()
            ].join("\n");

            return s;
        },

        bind: function() {

            // Replace manufacturer names
            $("#replacemanufacturers").click(async function() {
                let formdata = "mode=replacemanufacturers&" + $("#manufacturerfind, #manufacturerreplace").toPOST();
                let result = await common.ajax_post("maint_find_replace", formdata);
                $("#manufacturerfind option:selected").remove();
                let termpresent = false;
                $.each($("#manufacturerfind option"), function(i, v) {
                    if ( $(v).val() == $("#manufacturerreplace").val() ) {
                        termpresent = true;
                        return;
                    }
                });
                if (!termpresent) {
                    $("#manufacturerfind").append('<option>' + $("#manufacturerreplace").val() + '</option>');
                }
                header.show_info(_("{0} vaccination record(s) affected").replace("{0}", result));
            });

            // Replace city/town names
            $("#replacecities").click(async function() {
                let formdata = "mode=replacecities&" + $("#cityfind, #cityreplace").toPOST();
                let result = await common.ajax_post("maint_find_replace", formdata);
                $("#cityfind option:selected").remove();
                let termpresent = false;
                $.each($("#cityfind option"), function(i, v) {
                    if ( $(v).val() == $("#cityreplace").val() ) {
                        termpresent = true;
                        return;
                    }
                });
                if (!termpresent) {
                    $("#cityfind").append('<option>' + $("#cityreplace").val() + '</option>');
                }
                header.show_info(_("{0} person record(s) affected").replace("{0}", result));
            });

            // Replace state/county names
            $("#replacestates").click(async function() {
                let formdata = "mode=replacestates&" + $("#statefind, #statereplace").toPOST();
                let result = await common.ajax_post("maint_find_replace", formdata);
                $("#statefind option:selected").remove();
                let termpresent = false;
                $.each($("#statefind option"), function(i, v) {
                    if ( $(v).val() == $("#statereplace").val() ) {
                        termpresent = true;
                        return;
                    }
                });
                if (!termpresent) {
                    $("#statefind").append('<option>' + $("#statereplace").val() + '</option>');
                }
                header.show_info(_("{0} person record(s) affected").replace("{0}", result));
            });

        },

        sync: function() {
            $("#findreplacetable button").button();
        },

        name: "maint_find_replace",
        animation: "newdata",
        title: function() { return _("Find/replace"); },
        routes: {
            "maint_find_replace": function() { common.module_loadandstart("maint_find_replace", "maint_find_replace"); }
        }

    };

    common.module_register(maint_find_replace);

});
