/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const log_new = {

        render: function() {
            return [
                html.content_header(_("Add a new log")),
                tableform.fields_render([
                    { post_field: "animal", type: "animal", label: _("Animal"), 
                        hideif: function() { return controller.mode != "animal"; }},
                    { post_field: "person", type: "person", label: _("Person"), 
                        hideif: function() { return controller.mode != "person"; }},
                    { post_field: "type", type: "select", label: _("Type"), 
                        options: { displayfield: "LOGTYPENAME", rows: controller.logtypes }},
                    { post_field: "logdate", type: "date", label: _("Date") },
                    { post_field: "logtime", type: "time", label: _("Time") },
                    { post_field: "entry", type: "textarea", label: _("Note"), rows: 8 }
                ], { full_width: false }),
                tableform.buttons_render([
                   { id: "log", icon: "log", text: _("Create Log") }
                ], { centered: true }),
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
            $("#logdate").date("today");
            $("#logtime").val(format.time(new Date()));
            $("#type").select("value", config.integer("AFDefaultLogType"));    

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");

            $("#button-log").button().click(async function() {
                if (!validation()) { return; }
                $("#button-log").button("disable");
                try {
                    header.show_loading(_("Creating..."));
                    let formdata = $("input, select, textarea").toPOST() + "&mode=" + controller.mode;
                    await common.ajax_post("log_new", formdata);
                    header.show_info(_("Log successfully added."));
                    $("#logdate").date("today");
                    $("#entry").val("");
                }
                finally {
                    header.hide_loading();
                    $("#button-log").button("enable");
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
