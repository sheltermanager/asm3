/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var change_password = {

        render: function() {
            return [
                html.content_header(_("Change Password")),
                html.error(_("The sheltermanager.com admin account password cannot be changed here, please visit {0}").replace("{0}", "<a href=\"/my/\">https://sheltermanager.com/my/</a>"), "mastererror"),
                html.info(_("Your password is currently set to 'password'. This is highly insecure and we strongly suggest you choose a new password."), "suggestinfo"),
                '<div id="changepassword">',
                '<table class="asm-table-layout">',
                '<tr>',
                    '<td>' + _("Username") + '</td>',
                    '<td>' + controller.username + '</td>',
                '</tr>',
                '<tr>',
                    '<td>',
                    '<label for="oldpassword">' + _("Old Password") + '</label>',
                    '</td>',
                    '<td>',
                    '<input id="oldpassword" data="oldpassword" class="asm-textbox" type="password" />',
                    '</td>',
                '</tr>',
                '<tr>',
                    '<td>',
                    '<label for="newpassword">' + _("New Password") + '</label>',
                    '</td>',
                    '<td>',
                    '<input id="newpassword" data="newpassword" class="asm-textbox" type="password" />',
                    '</td>',
                '</tr>',
                '<tr>',
                    '<td>',
                    '<label for="confirmpassword">' + _("Confirm Password") + '</label>',
                    '</td>',
                    '<td>',
                    '<input id="confirmpassword" data="confirmpassword" class="asm-textbox" type="password" />',
                    '</td>',
                '</tr>',
                '</table>',
                '<div class="centered">',
                    '<button id="change">' + html.icon("auth") + ' ' + _("Change Password") + '</button>',
                '</div>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            var validation = function() {
                // Remove any previous errors
                header.hide_error();
                validate.reset();

                // Password must be supplied
                if ($.trim($("#newpassword").val()) == "") {
                    header.show_error(_("Passwords cannot be blank."));
                    return false;
                }

                // New/Confirm must match
                if ($.trim($("#newpassword").val()) != $.trim($("#confirmpassword").val())) {
                    header.show_error(_("New password and confirmation password don't match."));
                    return false;
                }

                return true;
            };

            var change_password = function(mode) {
                if (!validation()) { return; }

                $("#change").button("disable");
                header.show_loading();

                var formdata = $("input").toPOST();
                common.ajax_post("change_password", formdata)
                    .then(function(result) { 
                        header.show_info(_("Password successfully changed."));
                        $("#change").button("enable");
                        $("#oldpassword, #newpassword, #confirmpassword").val("");
                    })
                    .always(function() {
                        header.hide_loading();
                        $("#change").button("enable");
                    });
            };

            // Buttons
            $("#change").button().click(function() {
                change_password();
            });

            $("#mastererror").hide();
            $("#suggestinfo").hide();

            // If it's the master sheltermanager.com user, don't allow changing
            if (controller.ismaster) {
                $("#changepassword").hide();
                $("#mastererror").fadeIn();
            }

            // If we were suggesting they change their password, say so
            if (controller.issuggest) {
                $("#suggestinfo").fadeIn();
            }
        },

        name: "change_password",
        animation: "options",
        autofocus: "#oldpassword", 
        title: function() { return _("Change Password"); },
        routes: {
            "change_password": function() { return common.module_loadandstart("change_password", "change_password"); }
        }

    };

    common.module_register(change_password);

});
