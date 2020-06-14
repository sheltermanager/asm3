/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    "use strict";

    const mailmerge_criteria = {

        render: function() {

            return [
                html.content_header(controller.title),
                '<div id="criteriaform">',
                '<input data-post="id" type="hidden" value="' + controller.id + '" />',
                "<input data-post=\"hascriteria\" type=\"hidden\" value=\"true\" />",
                controller.criteriahtml,
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {

            $("#submitcriteria").button().click(function() {
                common.route("mailmerge?" + $("#criteriaform input, #criteriaform select").toPOST(true));
            });

        },

        sync: function() {
        },

        destroy: function() {
        },

        name: "mailmerge_criteria",
        animation: "newdata",
        title: function() { return controller.title; }

    };

    common.module_register(mailmerge_criteria);

});
