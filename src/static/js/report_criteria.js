/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    "use strict";

    const report_criteria = {

        render: function() {

            return [
                html.content_header(controller.title),
                '<div id="criteriaform">',
                '<input data-post="id" type="hidden" value="' + controller.id + '" />',
                '<input data-post="hascriteria" type="hidden" value="true" />',
                '<div id="displayfields">',
                controller.criteriahtml,
                '</div>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {

            $("#submitcriteria").button().click(function() {
                report_criteria.submit();
            });

            $("#displayfields input").keypress(function(e) {
                if (e.which == 13) {
                    report_criteria.submit();
                    return false;
                }
            });

        },

        sync: function() {
            // Focus the first displayed criteria field
            setTimeout(function() {
                $("#displayfields input, #displayfields select").first().focus();
            }, 100);
        },

        destroy: function() {
        },

        submit: function() {
            common.route(controller.target + "?" + $("#criteriaform input, #criteriaform select").toPOST(true));
        },

        name: "report_criteria",
        animation: "newdata",
        title: function() { return controller.title; }

    };

    common.module_register(report_criteria);

});
