/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const change_password = {

        render: function() {
            return [
                html.content_header(_("Change Password")),
                html.error(_("The sheltermanager.com admin account password cannot be changed here, please visit {0}").replace("{0}", 
                    "<a href=\"https://sheltermanager.com/my/\">https://sheltermanager.com/my/</a>"), "mastererror"),
                '<div id="changepassword">',
                tableform.fields_render([
                    { type: "raw", label: _("Username"), markup: controller.username },
                    { type: "password", post_field: "oldpassword", autocomplete: "current-password", label: _("Old Password") },
                    { type: "password", post_field: "newpassword", autocomplete: "new-password", label: _("New Password") },
                    { type: "password", post_field: "confirmpassword", autocomplete: "new-password", label: _("Confirm Password") },
                ], { full_width: false }),
                tableform.buttons_render([
                   { id: "change", icon: "auth", text: _("Change Password") }
                ], { centered: true }),
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            const validation = function() {
                // Remove any previous errors
                header.hide_error();
                validate.reset();

                // Password must be supplied
                if (common.trim($("#newpassword").val()) == "") {
                    header.show_error(_("Passwords cannot be blank."));
                    return false;
                }

                // New/Confirm must match
                if (common.trim($("#newpassword").val()) != common.trim($("#confirmpassword").val())) {
                    header.show_error(_("New password and confirmation password don't match."));
                    return false;
                }

                // Test strength if option on
                if (config.bool("ForceStrongPasswords")) {
                    let np = $("#newpassword").val(), passok = true;
                    if (np.match(/[a-z]+/)) {}
                    if (!np.match(/[$@#&!]+/)) { }
                    if (!np.match(/[A-Z]+/)) { passok = false; }
                    if (!np.match(/[0-9]+/)) { passok = false; }
                    if (np.length < 8) { passok = false; }
                    if (!passok) {
                        header.show_error(_("Passwords must be longer than 8 characters and include at least one upper case character and number"));
                        return false;
                    }
                }

                return true;
            };

            const change_password = async function(mode) {
                if (!validation()) { return; }

                $("#button-change").button("disable");
                header.show_loading();
                try {
                    let formdata = $("input").toPOST();
                    await common.ajax_post("change_password", formdata);
                    header.show_info(_("Password successfully changed."));
                    $("#button-change").button("enable");
                    $("#oldpassword, #newpassword, #confirmpassword").val("");
                }
                finally {
                    header.hide_loading();
                    $("#button-change").button("enable");
                }
            };

            // Buttons
            $("#button-change").button().click(function() {
                change_password();
            });

            $("#mastererror").hide();

            // If it's the master sheltermanager.com user, don't allow changing
            if (controller.ismaster) {
                $("#changepassword").hide();
                $("#mastererror").fadeIn();
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
