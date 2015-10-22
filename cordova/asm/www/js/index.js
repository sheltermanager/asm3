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

    alert("device.platform=" + device.platform);
    if (device.platform == "ios") {
        $("#button-signup").hide();
    }
    else {
        $("#button-signup").click(function() {
            window.open("https://sheltermanager.com/site/en_signup.html", "_system");
        });
    }

    var account = window.localStorage.getItem("asm_account"),
        username = window.localStorage.getItem("asm_username"),
        password = window.localStorage.getItem("asm_password"),
        ui = window.localStorage.getItem("asm_ui");

    if (account && username && password) {
        $("#account").val(account);
        $("#username").val(username);
        $("#password").val(password);
        $("#ui").val(ui);
    }

}, false);
