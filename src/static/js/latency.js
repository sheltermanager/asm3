/*global $, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const latency = {

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
                common.ajax_post("latency", latency.formdata)
                    .then(function(r, ms) {
                        $("#testoutput").append("Test 1: " + ms + "ms<br/>");
                        return common.ajax_post("latency", latency.formdata);
                    })
                    .then(function(r, ms) {
                        $("#testoutput").append("Test 2: " + ms + "ms<br/>");
                        return common.ajax_post("latency", latency.formdata);
                    })
                    .then(function(r, ms) {
                        $("#testoutput").append("Test 3: " + ms + "ms<br/>");
                    });
            });

        },

        sync: function() {
        },

        name: "latency",
        animation: "options",
        title: function() { return _("Latency"); },
        routes: {
            "latency": function() { common.module_start("latency"); }
        }

    };

    common.module_register(latency);

});
