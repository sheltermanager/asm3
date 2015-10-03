/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, alert */

$(function() {

    $("button").click(function() {
        
        var base, params, url = "https://sheltermanager.com/service/findserver?a=" + $("#account").val();

        $.getJSON(url + "&callback=?")
            .then(function(data) {
                
                if (!data.server) {
                    alert("Invalid account number");
                    return $.Deferred().reject();
                }

                base = "https://" + data.server + ".sheltermanager.com/";
                params = "database=" + $("#account").val() + "&username=" + $("#username").val() + "&password=" + $("#password").val();
                params += "&logout=" + encodeURIComponent(window.location.href);
                url = base + "login_jsonp?" + params + "&callback=?";

                return $.getJSON(url);

            })
            .then(function(data) {

                if (data.response == "FAIL") {
                    alert("Incorrect account, username or password");
                }
                else if (data.response == "DISABLED") {
                    alert("This account is disabled");
                }
                else {
                    window.localStorage.setItem("asm_account", $("#account").val());
                    window.localStorage.setItem("asm_username", $("#username").val());
                    window.localStorage.setItem("asm_password", $("#password").val());
                    window.location = base + $("#ui").val();
                }

            })
            .fail(function(xhr, msg) {
                alert(msg);
            });

    });

    var account = window.localStorage.getItem("asm_account"),
        username = window.localStorage.getItem("asm_username"),
        password = window.localStorage.getItem("asm_password");
    if (account && username && password) {
        $("#account").val(account);
        $("#username").val(username);
        $("#password").val(password);
    }

    alert(window.location.href);

});

