/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var publish = {

        render: function() {
            return [
                '<div id="asm-content"',
                'class="ui-helper-reset ui-widget-content ui-corner-all centered"',
                'style="width: 60%; margin-left: auto; margin-right: auto; padding: 20px">',
                '<div id="alreadyrunning" class="ui-state-error ui-corner-all" style="margin-top: 20px; padding: 0 .7em; display: none">',
                '<p><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>',
                _("A publish job is already running."),
                '</p>',
                '</div>',

                '<div id="progress" style="margin-top: 10px"></div>',
                '<div id="stopped" class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em; display: none">',
                '<p><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                _("No publishers are running."),
                '</p>',
                '</div>',

                '<div id="lasterror" class="ui-state-error ui-corner-all" style="margin-top: 20px; padding: 0 .7em; display: none">',
                '<p><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>',
                '<span id="lasterrortext"></span>',
                '</p>',
                '</div>',

                '<div id="complete" class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em; display: none">',
                '<p><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                _("Publishing complete."),
                '</p>',
                '</div>',

                '<div id="running" class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em; display: none">',
                '<p><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                '<span id="runningtext"></span>',
                '</p>',
                '</div>',

                '<div id="stop" class="centered">',
                '<button id="button-stop">' + _("Stop Publishing") + '</button>',
                '</div>',
                '</div>'
            ].join("\n");
        },

        bind: function() {

            $("#progress").progressbar();

            $("#button-stop").button().click(function() {
                $("#button-stop").button("disable");
                common.ajax_post("publish", "mode=stop")
                    .then(function() { 
                        $("#button-stop").button("enable");
                        publish.forcestop = true;
                    });
            });

        },

        sync: function() {

            publish.polling = true;

            if (controller.failed) {
                $("#alreadyrunning").fadeIn().delay(publish.poll_interval).fadeOut();
            }

            // Do the first poll a short time after loading
            setTimeout(publish.poll, 1000);
        },

        poll: function() {
            common.ajax_post("publish", "mode=poll").then(function(result) { 
                var bits = result.split("|");
                var publishername = bits[0];
                var progress = bits[1];
                var lasterror = bits[2];
                
                var newtext = _("{0} is running ({1}&#37; complete).").replace("{0}", publishername).replace("{1}", progress);
                $("#progress").progressbar("option", "value", parseInt(progress, 10));
                $("#runningtext").html(newtext);

                // Show the last error if there was one
                if (lasterror != "") {
                    $("#lasterrortext").html(lasterror);
                    $("#lasterror").fadeIn();
                    $("#stop").hide();
                    return;
                }

                // Publisher complete
                if (progress == "100") {
                    $("#complete").fadeIn();
                    $("#running").hide();
                    $("#progress").hide();
                    $("#stop").hide();
                    return;
                }

                // No publisher running
                if (publishername == "NONE") {

                    // Did the user force a stop?
                    if (publish.forcestop) {
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

                // Publisher is running
                else {
                    $("#running").fadeIn();
                    $("#progress").fadeIn();
                    $("#stop").fadeIn();
                    $("#complete").hide();
                    $("#stopped").hide();
                }

                // Only schedule another poll if polling is enabled
                // (note that publishing complete/error conditions
                //  above drop out without telling us to poll any more).
                if (publish.polling) {
                    setTimeout(publish.poll, publish.poll_interval);
                }

            });

        },

        destroy: function() {
            publish.polling = false;
        },

        forcestop: false,    // true if the user hit stop
        polling: false,      // true if the screen is polling the server for updates
        poll_interval: 5000, // time between polls in ms

        name: "publish",
        animation: "default",
        title: function() { return _("Publishing"); },
        routes: {
            "publish": function() { common.module_loadandstart("publish", "publish?" + this.rawqs); }
        }

    };

    common.module_register(publish);

});

