/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const task = {

        render: function() {
            return [
                '<div id="asm-content"',
                'class="ui-helper-reset ui-widget-content ui-corner-all centered"',
                'style="width: 60%; margin-left: auto; margin-right: auto; padding: 20px">',
                '<div id="alreadyrunning" class="ui-state-error ui-corner-all" style="margin-top: 20px; padding: 0 .7em; display: none">',
                '<p><span class="ui-icon ui-icon-alert"></span>',
                _("A task is already running."),
                '</p>',
                '</div>',

                '<div id="progress" style="margin-top: 10px"></div>',
                '<div id="stopped" class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em; display: none">',
                '<p><span class="ui-icon ui-icon-info"></span>',
                _("No tasks are running."),
                '</p>',
                '</div>',

                '<div id="lasterror" class="ui-state-error ui-corner-all" style="margin-top: 20px; padding: 0 .7em; display: none">',
                '<p><span class="ui-icon ui-icon-alert"></span>',
                '<span id="lasterrortext"></span>',
                '</p>',
                '</div>',

                '<div id="complete" class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em; display: none">',
                '<p><span class="ui-icon ui-icon-info"></span>',
                _("Task complete."),
                '</p>',
                '</div>',

                '<div id="running" class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em; display: none">',
                '<p><span class="ui-icon ui-icon-info"></span>',
                '<span id="runningtext"></span>',
                '</p>',
                '</div>',

                '<div id="returned" class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em; display: none">',
                '</div>',

                '<div id="stop" class="centered">',
                '<button id="button-stop">' + _("Stop") + '</button>',
                '</div>',
                '</div>'
            ].join("\n");
        },

        bind: function() {

            $("#progress").progressbar();

            $("#button-stop").button().click(async function() {
                $("#button-stop").button("disable");
                await common.ajax_post("task", "mode=stop");
                $("#button-stop").button("enable");
                task.forcestop = true;
            });

        },

        sync: function() {

            task.polling = true;

            if (controller.failed) {
                $("#alreadyrunning").fadeIn().delay(task.poll_interval).fadeOut();
            }

            // Do the first poll a short time after loading
            setTimeout(task.poll, 1000);
        },

        poll: async function() {
            let result = await common.ajax_post("task", "mode=poll");
            let [taskname, progress, lasterror, returnvalue] = result.split("|");
            let newtext = _("{0} is running ({1}&#37; complete).").replace("{0}", taskname).replace("{1}", progress);
            $("#progress").progressbar("option", "value", parseInt(progress, 10));
            $("#runningtext").html(newtext);

            // Show the last error if there was one and stop
            if (lasterror) {
                $("#lasterrortext").html(lasterror);
                $("#lasterror").fadeIn();
                $("#complete").fadeIn();
                $("#running").hide();
                $("#progress").hide();
                $("#stop").hide();
                return;
            }

            // Show the return value if there is one and stop
            if (returnvalue) {
                $("#returned").html(returnvalue);
                $("#returned").fadeIn();
                $("#complete").fadeIn();
                $("#running").hide();
                $("#progress").hide();
                $("#stop").hide();
                return;
            }

            // Task complete - stop
            // NOTE: No longer used, a task must have a return value or an error to complete
            // The reason for this is that for some complex tasks, such as csvexport_animals, 
            // the progress meter could be incremented to 100% before the task had fully 
            // finished and the return value was available.
            /*
            if (progress == "100") {
                $("#complete").fadeIn();
                $("#running").hide();
                $("#progress").hide();
                $("#stop").hide();
                return;
            }
            */

            // No task running
            if (taskname == "NONE") {

                // Did the user force a stop?
                if (task.forcestop) {
                    $("#stopped").fadeIn();
                    $("#running").hide();
                    $("#progress").hide();
                    $("#stop").hide();
                }
                
                // Ok, nothing was running
                else {
                    $("#stopped").fadeIn();
                    $("#running").hide();
                    $("#progress").hide();
                    $("#stop").hide();
                }

            }

            // Task is running
            else {
                $("#running").fadeIn();
                $("#progress").fadeIn();
                $("#stop").fadeIn();
                $("#complete").hide();
                $("#stopped").hide();
            }

            // Only schedule another poll if polling is enabled
            // (note that task complete/error conditions
            //  above drop out without telling us to poll any more).
            if (task.polling) {
                setTimeout(task.poll, task.poll_interval);
            }
        },

        destroy: function() {
            task.polling = false;
        },

        forcestop: false,    // true if the user hit stop
        polling: false,      // true if the screen is polling the server for updates
        poll_interval: 5000, // time between polls in ms

        name: "task",
        animation: "default",
        title: function() { return _("Executing Task"); },
        routes: {
            "task": function() { common.module_loadandstart("task", "task?" + this.rawqs); }
        }

    };

    common.module_register(task);

});

