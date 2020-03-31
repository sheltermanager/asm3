/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var batch = {

        render: function() {
            return [
                html.content_header(_("Trigger Batch Processes")),
                '<div class="centered" style="max-width: 800px; margin-left: auto; margin-right: auto">',
                html.warn(_("These batch processes are run each night by the system and should not need to be run manually.") + '<br/><br/><b>' + 
                    _("Some batch processes may take a few minutes to run and could prevent other users being able to use the system for a short time.")
                    + '</b>'),
                '<div id="tasks">',
                '<p>',
                '<select id="task">',
                '<option value="genshelterpos">' + _("Recalculate on-shelter animal locations") + '</option>',
                '<option value="genallpos">' + _("Recalculate ALL animal locations") + '</option>',
                '<option value="genallvariable">' + _("Recalculate ALL animal ages/times") + '</option>',
                '<option value="genlookingfor">' + _("Regenerate 'Person looking for' report") + '</option>',
                '<option value="genownername">' + _("Regenerate person names in selected format") + '</option>',
                '<option value="genownerflags">' + _("Regenerate person flags column") + '</option>',
                '<option value="genlostfound">' + _("Regenerate 'Match lost and found animals' report") + '</option>',
                '<option value="genfigyear">' + _("Regenerate annual animal figures for") + '</option>',
                '<option value="genfigmonth">' + _("Regenerate monthly animal figures for") + '</option>',
                '</select>',
                '<input id="taskdate" class="asm-textbox asm-datebox" style="display: none" />',
                '<button id="button-go">' + _("Go") + '</button>',
                '</p>',
                '</div>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        runmode: function(btn, formdata) {
            common.ajax_post("batch", formdata)
                .then(function() {
                    common.route("task");
                });
        },

        bind: function() {
            $("#button-go").button().click(function() {
                var task = $("#task").val(), taskdate = $("#taskdate").val();
                batch.runmode( task, "mode=" + task + "&taskdate=" + taskdate );
            });
            $("#task").change(function() {
                var task = $("#task").val();
                $("#taskdate").toggle(task == "genfigyear" || task == "genfigmonth");
            });
        },

        name: "batch",
        animation: "options",
        title: function() { return _("Batch"); },
        routes: {
            "batch": function() { common.module_loadandstart("batch", "batch"); }
        }

    };

    common.module_register(batch);

});
