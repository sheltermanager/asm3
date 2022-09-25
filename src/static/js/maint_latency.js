/*global $, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const maint_latency = {

        formdata: "junk=123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890",

        render: function() {
            return [
                html.content_header(_("Latency Tester")),
                '<p class="centered"><button id="button-test">Test Latency</button></p>',
                '<p id="testoutput" class="centered" style="color: green"></p>',
                html.content_footer()
            ].join("\n");
        },

        bind: function () {

            $("#button-test").button().click(function() {
                $("#button-test").button("disable");
                common.ajax_post("maint_latency", maint_latency.formdata)
                    .then(function(r, ms) {
                        $("#testoutput").append("Test 1: " + ms + "ms<br/>");
                        return common.ajax_post("maint_latency", maint_latency.formdata);
                    })
                    .then(function(r, ms) {
                        $("#testoutput").append("Test 2: " + ms + "ms<br/>");
                        return common.ajax_post("maint_latency", maint_latency.formdata);
                    })
                    .then(function(r, ms) {
                        $("#testoutput").append("Test 3: " + ms + "ms<br/>");
                    });
            });

        },

        sync: function() {
        },

        name: "maint_latency",
        animation: "options",
        title: function() { return _("Latency"); },
        routes: {
            "maint_latency": function() { common.module_start("maint_latency"); }
        }

    };

    common.module_register(maint_latency);

});
