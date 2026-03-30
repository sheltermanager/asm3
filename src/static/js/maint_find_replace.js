/*global $, jQuery, FileReader, Modernizr, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const maint_find_replace = {

        render: function() {
            let s = [
                html.content_header(_("Find/replace")),
                tableform.fields_render([
                    { type: "raw", markup: '<h3>' + _("Vaccine manufacturer") + '</h3>' },
                    { post_field: "manufacturerfind", label: _("Find"), type: "select", options: controller.manufacturers },
                    { post_field: "manufacturerreplace", label: _("Replace with"), type: "autotext", options: controller.manufacturers },
                    { type: "raw", markup: '<button class="replacebutton" id="replacemanufacturers">' + _("Go") + '</button>' },
                    { type: "raw", markup: '<h3>' + _("Cities") + '</h3>' },
                    { post_field: "cityfind", label: _("Find"), type: "select", options: controller.towns },
                    { post_field: "cityreplace", label: _("Replace with"), type: "autotext", options: controller.towns },
                    { type: "raw", markup: '<button class="replacebutton" id="replacecities">' + _("Go") + '</button>' },
                    { type: "raw", markup: '<h3>' + _("States") + '</h3>' },
                    { post_field: "statefind", label: _("Find"), type: "select", options: controller.counties },
                    { post_field: "statereplace", label: _("Replace with"), type: "autotext", options: controller.counties },
                    { type: "raw", markup: '<button class="replacebutton" id="replacestates">' + _("Go") + '</button>' },
                ], { full_width: false }),
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
                if ( !$("#manufacturerfind").select("hasOption", $("#manufacturerreplace").val()) ) {
                    $("#manufacturerfind").append('<option>' + $("#manufacturerreplace").val() + '</option>');
                }
                header.show_info(_("{0} vaccination record(s) affected").replace("{0}", result));
            });

            // Replace city/town names
            $("#replacecities").click(async function() {
                let formdata = "mode=replacecities&" + $("#cityfind, #cityreplace").toPOST();
                let result = await common.ajax_post("maint_find_replace", formdata);
                $("#cityfind option:selected").remove();
                if ( !$("#cityfind").select("hasOption", $("#cityreplace").val()) ) {
                    $("#cityfind").append('<option>' + $("#cityreplace").val() + '</option>');
                }
                header.show_info(_("{0} person record(s) affected").replace("{0}", result));
            });

            // Replace state/county names
            $("#replacestates").click(async function() {
                let formdata = "mode=replacestates&" + $("#statefind, #statereplace").toPOST();
                let result = await common.ajax_post("maint_find_replace", formdata);
                $("#statefind option:selected").remove();
                if ( !$("#statefind").select("hasOption", $("#statereplace").val()) ) {
                    $("#statefind").append('<option>' + $("#statereplace").val() + '</option>');
                }
                header.show_info(_("{0} person record(s) affected").replace("{0}", result));
            });

        },

        sync: function() {
            $(".replacebutton").button();
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
