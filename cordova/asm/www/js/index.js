/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, alert */

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

    $("#button-login").click(function() {
        
        var base, params, url = "https://sheltermanager.com/service/findserver?a=" + $("#account").val();

        $.getJSON(url + "&callback=?")
            .then(function(data) {
                
                if (!data.server) {
                    window.alert("Invalid account number");
                    return $.Deferred().reject();
                }

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
                    window.open(base + $("#ui").val(), "_self", "location=yes,hardwareback=yes,zoom=no");
                }

            })
            .fail(function(xhr, msg) {
                if (!msg) { return; }
                alert(msg);
            });

    });

    $("#button-signup").click(function() {
        window.open("https://sheltermanager.com/site/en_signup.html", "_system");
    });

    var account = window.localStorage.getItem("asm_account"),
        username = window.localStorage.getItem("asm_username"),
        password = window.localStorage.getItem("asm_password");
    if (account && username && password) {
        $("#account").val(account);
        $("#username").val(username);
        $("#password").val(password);
    }

}, false);
