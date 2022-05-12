/*global $, controller */

$(document).ready(function() {

    "use strict";

    const show_dlg = function(title, body) {
        $("#errortitle").html(title);
        $("#errortext").html(body);
        $("#errordlg").modal("show");
    };

    let h = [
        '<div class="modal fade" id="errordlg" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="errortitle" aria-hidden="true">',
            '<div class="modal-dialog">',
                '<div class="modal-content">',
                    '<div class="modal-header">',
                        '<h5 class="modal-title" id="errortitle">Error</h5>',
                        '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>',
                    '</div>',
                    '<div id="errortext" class="modal-body">',
                    '</div>',
                    '<div class="modal-footer">',
                        '<button type="button" class="btn btn-primary" data-bs-dismiss="modal">' + _("Close") + '</button>',
                    '</div>',
                '</div>',
            '</div>',
        '</div>',
        '<div id="login-container" class="container">',
            '<center><img src="static/images/logo/icon-128.png"></center>',
            '<form method="post" action="mobile_login">',
            '<div class="mb-3">',
                '<label for="smaccount" class="form-label">' + _("Database") + '</label>',
                '<input type="text" class="form-control" id="smaccount">',
            '</div>',
            '<div class="mb-3">',
                '<label for="username" class="form-label">' + _("Username") + '</label>',
                '<input type="text" class="form-control" id="username">',
            '</div>',
            '<div class="mb-3">',
                '<label for="password" class="form-label">' + _("Password") + '</label>',
                '<input type="password" class="form-control" id="password">',
            '</div>',
            '<center><button id="btn-login" type="button" class="btn btn-primary">Login',
            '<div id="spinner" class="spinner-border spinner-border-sm" style="display: none"></div>',
            '</button>',
            '</center>',
            '</form>',
        '</div>'
    ].join("\n");

    $("body").html(h);

    const do_login = function() {
        let formdata = {
            "smaccount":    $("#smaccount").val(),
            "username":     $("#username").val(),
            "password":     $("#password").val()
        };
        if (!$("#username").val() || !$("#password").val()) {
            show_dlg("Error", _("Username and password are required"));
            return;
        }

        $("#btn-login").prop("disabled", true);
        $("#spinner").show();

        $.ajax({
            type: "POST",
            url: "login",
            data: formdata,
            dataType: "text",
            mimeType: "textPlain",
            success: function(response) {
                $("#spinner").hide();
                $("#btn-login").prop("disabled", false);
                if (response == "FAIL") {
                    show_dlg("Error", _("Invalid username or password."));
                }
                else if (response == "DISABLED") {
                    show_dlg("Error", _("Account disabled."));
                }
                else if (response == "WRONGSERVER") {
                    // This is smcom specific - if the database is not on this
                    // server, go back to the main login screen to prompt for an account
                    window.location = controller.smcomloginurl;
                }
                else {
                    window.location = "mobile";
                }
            },
            error: function(jqxhr, textstatus, response) {
                $("#spinner").hide();
                $("#btn-login").prop("disabled", false);
                show_dlg("Error", _("Error contacting server."));
            }
        });
    };

    if (controller.smcom) { $("label[for='smaccount']").text(_("SM Account")); }
    if (!controller.multipledatabases) { $("#smaccount").parent().hide(); }

    if (controller.smaccount) { $("#smaccount").val(controller.smaccount); }
    if (controller.username) { $("#username").val(controller.username); }
    if (controller.password) { $("#password").val(controller.password); }

    $("#btn-login").click(do_login);

});


