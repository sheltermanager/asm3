/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const log_new = {

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
                '<td><input id="logdate" data="logdate" type="text" class="asm-textbox asm-datebox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="logtime">' + _("Time") + '</label></td>',
                '<td><input id="logtime" data="logtime" type="text" class="asm-textbox asm-timebox" /></td>',
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
            const validation = function() {
                // Remove any previous errors
                header.hide_error();
                validate.reset();
                if (controller.mode == "animal") {
                    // animal
                    if ($("#animal").val() == "" || $("#animal").val() == "0") {
                        header.show_error(_("Log requires an animal."));
                        validate.highlight("animal");
                        return false;
                    }
                }
                if (controller.mode == "person") {
                    // person
                    if ($("#person").val() == "" || $("#person").val() == "0") {
                        header.show_error(_("Log requires a person."));
                        validate.highlight("person");
                        return false;
                    }
                }
                // date
                if (common.trim($("#logdate").val()) == "") {
                    header.show_error(_("Log requires a date."));
                    validate.highlight("logdate");
                    return false;
                }
                return true;
            };

            validate.indicator([ "logdate" ]);

            // Set default values
            $("#logdate").datepicker("setDate", new Date());
            $("#logtime").val(format.time(new Date()));
            $("#type").select("value", config.integer("AFDefaultLogType"));    

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");

            $("#log").button().click(async function() {
                if (!validation()) { return; }
                $("#log").button("disable");
                try {
                    header.show_loading(_("Creating..."));
                    let formdata = $("input, select, textarea").toPOST() + "&mode=" + controller.mode;
                    await common.ajax_post("log_new", formdata);
                    header.show_info(_("Log successfully added."));
                    $("#logdate").datepicker("setDate", new Date());
                    $("#entry").val("");
                }
                finally {
                    header.hide_loading();
                    $("#log").button("enable");
                }
            });
        },

        name: "log_new",
        animation: "newdata",
        autofocus: "#asm-content button:first",
        title: function() { return _("Add a new log"); },
        routes: {
            "log_new": function() { common.module_loadandstart("log_new", "log_new?mode=" + this.qs.mode); }
        }

    };

    common.module_register(log_new);

});
