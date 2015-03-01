/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var log_new = {

        render: function() {
            return [
                html.content_header(_("Add a new log")),
                '<table class="asm-table-layout">',
                '<tr>',
                '<td>',
                controller.mode == "animal" ? '<label for="animal">' + _("Animal") + '</label>' : 
                    '<label for="person">' + _("Person") + '</label>',
                '</td>',
                '<td>',
                controller.mode == "animal" ? '<input id="animal" data="animal" type="hidden" class="asm-animalchooser" value=\'\' />' :
                    '<input id="person" data="person" type="hidden" class="asm-personchooser" value=\'\' />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="type">' + _("Type") + '</label></td>',
                '<td><select id="type" data="type" class="asm-selectbox">',
                html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="logdate">' + _("Date") + '</label></td>',
                '<td><input id="logdate" data="logdate" type="textbox" class="asm-textbox asm-datebox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="entry">' + _("Note") + '</label></td>',
                '<td><textarea id="entry" data="entry" rows="8" class="asm-textarea"></textarea></td>',
                '</tr>',
                '</table>',
                '<div class="centered">',
                '<button id="log">' + html.icon("log") + ' ' + _("Create Log") + '</button>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            var validation = function() {
                // Remove any previous errors
                header.hide_error();
                $("label").removeClass("ui-state-error-text");
                if (controller.mode == "animal") {
                    // animal
                    if ($("#animal").val() == "" || $("#animal").val() == "0") {
                        header.show_error(_("Log requires an animal."));
                        $("label[for='animal']").addClass("ui-state-error-text");
                        $("#animal").focus();
                        return false;
                    }
                }
                if (controller.mode == "person") {
                    // person
                    if ($("#person").val() == "" || $("#person").val() == "0") {
                        header.show_error(_("Log requires a person."));
                        $("label[for='person']").addClass("ui-state-error-text");
                        $("#person").focus();
                        return false;
                    }
                }
                // date
                if ($.trim($("#logdate").val()) == "") {
                    header.show_error(_("Log requires a date."));
                    $("label[for='logdate']").addClass("ui-state-error-text");
                    $("#logdate").focus();
                    return false;
                }
                return true;
            };

            // Set default values
            $("#logdate").datepicker("setDate", new Date());

            $("#log").button().click(function() {
                if (!validation()) { return; }
                $("#log").button("disable");
                header.show_loading(_("Creating..."));
                var formdata = $("input, select, textarea").toPOST() + "&mode=" + controller.mode;
                common.ajax_post("log_new", formdata, function() { 
                    header.hide_loading();
                    header.show_info(_("Log successfully added."));
                    $("#logdate").datepicker("setDate", new Date());
                    $("#entry").val("");
                    $("#log").button("enable");
                }, function() {
                    $("#log").button("enable");
                });
            });
        }
    };

    common.module(log_new, "log_new", "newdata");

});
