/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, _, common, controller, login: true, Modernizr */

$(function() {

    login = {
        render: function() {
            var h = [
                '<div id="asm-login-window" class="dialogshadow" style="display: none">',
                '<div id="asm-login-splash" />',
                '<table width="100%" style="margin-left: auto; margin-right: auto; text-align: right; padding: 10px">',
                '<tr class="asm-account-row hidden">',
                '<td>',
                    '<label for="database">' + (controller.smcom ? _("SM Account") : _("Database")) + '</label>',
                '</td>',
                '<td>',
                    '<input class="asm-textbox" id="database" name="database" type="text" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                    '<label for="username">' + _("Username") + '</label>',
                '</td>',
                '<td>',
                    '<input class="asm-textbox" id="username" name="username" type="text" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                    '<label for="password">' + _("Password") + '</label>',
                '</td>',
                '<td>',
                    '<input class="asm-textbox" id="password" name="password" type="password" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '</td>',
                '<td>',
                    '<input class="asm-checkbox" id="rememberme" name="rememberme" type="checkbox" />',
                    '<label for="rememberme">' + _("Remember me on this computer") + '</label>',
                '</td>',
                '</tr>',
                '</table>',

                '<div class="centered" style="padding: 5px">',
                    '<button id="loginbutton" class="ui-priority-primary asm-dialog-actionbutton">',
                        '<img id="flag" style="vertical-align: middle;" />',
                        _("Login"),
                        '<img id="loginspinner" src="static/images/wait/rolling_white.svg" style="display: none; vertical-align: middle; height: 16px" />',
                    '</button>',
                '</div>',
                '<div class="centered" style="margin-bottom: 5px">',
                    '<span id="forgottenpassword" style="display: none; margin-top: 5px;"><a href="#"></a></span>',
                '</div>',
                '<div class="centered asm-login-fail" style="display: none">',
                    '<div class="ui-state-error">',
                        '<p>',
                            '<span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>',
                            _("Invalid username or password."),
                        '</p>',
                    '</div>',
                '</div>',
                '<div class="centered asm-login-disabled" style="display: none">',
                    '<div class="ui-state-error">',
                        '<p>',
                            '<span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>',
                            _("Account disabled."),
                        '</p>',
                    '</div>',
                '</div>',
                '<div class="centered asm-login-error" style="display: none">',
                    '<div class="ui-state-error">',
                        '<p>',
                            '<span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>',
                            _("Error contacting server."),
                        '</p>',
                    '</div>',
                '</div>',
                '<div class="centered asm-login-tip" style="display: none">',
                '<div class="ui-state-highlight" style="margin-top: 20px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                _("The default username is 'user' with the password 'letmein'"),
                '</p>',
                '</div>',
                '</div>',
                '<div class="centered emergencynotice" style="display: none">',
                    '<div class="ui-state-error">',
                        '<p>',
                            '<span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>',
                            '<span class="emergencynoticetext"></span>',
                        '</p>',
                    '</div>',
                '</div>',

                '</div>'

            ].join("\n");
            return h;
        },

        login: function() {

            $("#loginbutton").button("disable");
            $("#loginspinner").fadeIn();

            var username = $("input#username").val();
            var password = $("input#password").val();
            var database = $("input#database").val();
            var formdata = { "database": database, 
                             "username" : username, 
                             "password" : password,
                             // TODO: disabled for now
                             // "mobile"   : common.is_mobile_browser(),
                             "nologconnection" : controller.nologconnection };
            $.ajax({
                type: "POST",
                url: "login",
                data: formdata,
                success: function(data) {
                    $("#loginspinner").fadeOut();
                    if (String(data).indexOf("FAIL") != -1) {
                        $(".asm-login-fail").fadeIn("slow").delay(3000).fadeOut("slow");
                        $("input#username").focus();
                        $("#loginbutton").button("enable");
                    }
                    else if (String(data).indexOf("DISABLED") != -1) {
                        $(".asm-login-disabled").fadeIn("slow").delay(3000).fadeOut("slow");
                        $("input#username").focus();
                        $("#loginbutton").button("enable");
                    }
                    else if (String(data).indexOf("WRONGSERVER") != -1) {
                        // This is smcom specific - if the database is not on this
                        // server, go back to the main login screen to prompt for an account
                        window.location = "https://sheltermanager.com/asm/login";
                    }
                    else {
                        // We have a successful login!
                        // If remember me is ticked, store the login info on 
                        // the user's machine.
                        if ($("#rememberme").prop("checked")) {
                            common.local_set("asmusername", username);
                            common.local_set("asmpassword", password);
                            common.local_set("asmaccount", database);
                        }
                        else {
                            // Remember me wasn't ticked, remove any stored login info
                            common.local_delete("asmusername");
                            common.local_delete("asmpassword");
                            common.local_delete("asmaccount");
                        }
                        $("#asm-login-window").fadeOut("slow", function() {
                            if (!controller.target) { 
                                controller.target = "main"; 
                            }
                            window.location = controller.target;
                        });
                    }
                },
                error: function() {
                    $("#loginspinner").fadeOut();
                    $(".asm-login-error").fadeIn("slow").delay(3000).fadeOut("slow");
                    $("input#username").focus();
                    $("#loginbutton").button("enable");
                }
            });
        },

        bind: function() {

            var self = this;

            // Position the login box to the center of the browser
            $("#asm-login-window").css({
                position: "absolute",
                left: ($(window).width() - $("#asm-login-window").outerWidth()) / 2,
                top: ($(window).height() - $("#asm-login-window").outerHeight()) / 2
            });

            // Set the splash image. If the database has a custom one set, we'll
            // use that otherwise one of our set.
            if (controller.customsplash) {
                if (controller.multipledatabases) {
                    $("#asm-login-splash").css({
                        "background-image": "url(login_splash?smaccount=" + controller.smaccount + ")"
                    });
                }
                else {
                    $("#asm-login-splash").css({
                        "background-image": "url(login_splash)"
                    });
                }
            }
            else {
                $("#asm-login-window").css({
                    "background-image": "url(static/images/splash/splash_logo.jpg)"
                });
            }
            
            // Set the flag icon based on the locale
            $("#flag")
                .attr("src", "static/images/flags/" + controller.locale + ".png")
                .attr("title", controller.locale);

            // Show the tip if there are no animals in the db
            if (!controller.hasanimals) { $(".asm-login-tip").fadeIn("slow"); }

            // Show things
            $("#asm-login-window").fadeIn("slow");

            if (controller.forgottenpassword) {
                $("#forgottenpassword a").attr("href", controller.forgottenpassword);
                $("#forgottenpassword a").html(controller.forgottenpasswordlabel);
                $("#forgottenpassword").show();
            }

            if (controller.emergencynotice) {
                $(".emergencynoticetext").html(controller.emergencynotice);
                $(".emergencynotice").fadeIn("slow");
            }

            // If we have multiple databases, enable the account row
            // and set the focus accordingly
            if (controller.multipledatabases) {
                $(".asm-account-row").show();
                $("input#database").focus();
                if (controller.smaccount) {
                    $("#database").val(controller.smaccount);
                    $("input#username").focus();
                }
            }
            else {
                $(".asm-account-row").hide();
                $("input#username").focus();
            }

            // If we were passed a username, stick it in
            if (controller.husername) {
                $("input#username").val(controller.husername);
            }

            // If we were passed a password, copy it in and
            // might as well try and authenticate too
            if (controller.hpassword) {
                $("input#password").val(controller.hpassword);
                $("#loginbutton").button();
                self.login();
            }

            // If we weren't passed a username or password, have a look
            // to see if we remembered one previously
            if (common.local_get("asmusername")) {
                $("#rememberme").prop("checked", true);
                $("input#username").val(common.local_get("asmusername"));
                $("input#password").val(common.local_get("asmpassword"));
                $("input#database").val(common.local_get("asmaccount"));
            }

            // Login when a button is pressed or enter
            // is pressed in any of our fields
            $("#loginbutton").button().click(function() {
                self.login();
            });

            $("input#username").keypress(function(e) {
                if (e.which == 13) { self.login(); }
            });

            $("input#password").keypress(function(e) {
                if (e.which == 13) { self.login(); }
            });

            $("input#database").keypress(function(e) {
                if (e.which == 13) { self.login(); }
            });
        }
    };

});
