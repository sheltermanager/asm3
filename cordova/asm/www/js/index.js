/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, alert, device */

document.addEventListener("deviceready", function() {

    if (navigator.notification) {
        window.alert = function(message) {
            navigator.notification.alert(
                message,
                null,       // callback
                "ASM",
                'OK'        // button
            );
        };
    }

    $("#account").blur(function() {
        var a = $("#account").val();
        a = $.trim(a);
        a = a.toLowerCase();
        $("#account").val(a);
    });

    $("#username").blur(function() {
        var u = $("#username").val();
        u = $.trim(u);
        u = u.toLowerCase();
        $("#username").val(u);
    });

    $("#button-login").click(function() {
        
        var base, params, url = "https://sheltermanager.com/service/findserver?a=" + $("#account").val();

        if (!$("#account").val() || !$("#username").val() || !$("#password").val()) {
            window.alert("Account, username and password must be supplied");
            return;
        }

        $("#button-login span").show();

        $.getJSON(url + "&callback=?")
            .then(function(data) {
                
                if (!data.server) {
                    window.alert("Invalid account number");
                    return $.Deferred().reject();
                }

                window.localStorage.setItem("asm_server", data.server);
                base = "https://" + data.server + ".sheltermanager.com/";
                params = "database=" + $("#account").val() + "&username=" + $("#username").val() + "&password=" + $("#password").val();
                url = base + "login_jsonp?" + params + "&mobile=true&callback=?";

                return $.getJSON(url);

            })
            .then(function(data) {

                if (data.response == "FAIL") {
                    window.alert("Incorrect account, username or password");
                }
                else if (data.response == "DISABLED") {
                    window.alert("This account is disabled");
                }
                else {
                    
                    window.localStorage.setItem("asm_account", $("#account").val());
                    window.localStorage.setItem("asm_username", $("#username").val());
                    window.localStorage.setItem("asm_password", $("#password").val());
                    window.localStorage.setItem("asm_ui", $("#ui").val());
                    window.localStorage.setItem("asm_remember", $("#remember").is(":checked") ? "true" : "false");

                    var ui = $("#ui").val();
                    if (ui == "mobile" || ui == "main") {
                        window.open(base + ui, "_blank", "location=yes,toolbar=yes,hardwareback=yes,zoom=no,closebuttoncaption=Close");
                    }
                    else if (ui == "upload") {
                        window.location = "upload.html";
                    }
                }

            })
            .fail(function(xhr, msg) {
                if (!msg) { return; }
                alert(msg);
            })
            .always(function() {
                $("#button-login span").hide();
            });

    });

    if (device.platform != "iOS") {
        $("#button-signup").show();
        $("#button-signup").click(function() {
            window.open("https://sheltermanager.com/site/en_signup.html", "_system");
        });
    }

    var account = window.localStorage.getItem("asm_account"),
        username = window.localStorage.getItem("asm_username"),
        password = window.localStorage.getItem("asm_password"),
        ui = window.localStorage.getItem("asm_ui"),
        remember = window.localStorage.getItem("asm_remember") == "true";

    if (account) {
        $("#account").val(account);
        $("#ui").val(ui);
        $("#username, #password").val("");
        $("#remember").prop("checked", remember);
        if (remember) {
            $("#username").val(username);
            $("#password").val(password);
        }
    }

}, false);
