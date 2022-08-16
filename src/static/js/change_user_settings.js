/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, log, validate */

$(function() {

    "use strict";

    const change_user_settings = {

        /** Where we have a list of pairs, first is value, second is label */
        two_pair_options: function(o, isflag) {
            let s = [];
            $.each(o, function(i, v) {
                let ds = "";
                if (isflag) {
                    ds = 'data-style="background-image: url(static/images/flags/' + v[0] + '.png)"';
                }
                s.push('<option value="' + v[0] + '" ' + ds + '>' + v[1] + '</option>');
            });
            return s.join("\n");
        },

        theme_list: function() {
            let s = [];
            $.each(controller.themes, function(i, v) {
                s.push('<option value="' + v[0] + '">' + _(v[3]) + '</option>');
            });
            return s.join("\n");
        },

        render: function() {
            return [
                html.content_header(_("Change User Settings")),
                '<table class="asm-table-layout">',
                '<tr>',
                    '<td>' + _("Username") + '</td>',
                    '<td>' + asm.user + '</td>',
                '</tr>',
                '<tr>',
                    '<td>',
                    '<label for="realname">' + _("Real name") + '</label>',
                    '</td>',
                    '<td>',
                    '<input id="realname" data="realname" class="asm-doubletextbox" />',
                    '</td>',
                '</tr>',
                '<tr>',
                    '<td>',
                    '<label for="email">' + _("Email Address") + '</label>',
                    '</td>',
                    '<td>',
                    '<input id="email" data="email" class="asm-doubletextbox" />',
                    '</td>',
                '</tr>',
                '<tr>',
                    '<td>',
                    '<label for="systemtheme">' + _("Visual Theme") + '</label>',
                    '</td>',
                    '<td>',
                    '<select id="systemtheme" data="theme" class="asm-selectbox">',
                    this.theme_list(),
                    '</select>',
                    '</td>',
                '</tr>',
                '<tr>',
                    '<td>',
                    '<label for="olocale">' + _("Locale") + '</label>',
                    '</td>',
                    '<td>',
                    '<select id="olocale" data="locale" class="asm-doubleselectbox asm-iconselectmenu">',
                    '<option value="" data-style="background-image: url(static/images/flags/' + config.str("Locale") + '.png)">' + _("(use system)") + '</option>',
                    this.two_pair_options(controller.locales, true),
                    '</select>',
                    '</td>',
                '</tr>',
                '<tr>',
                    '<td>',
                    '<label for="signature">' + _("Signature") + '</label>',
                    '<button id="button-change" type="button" style="vertical-align: middle">' + _("Clear and sign again") + '</button>',
                    '</td>',
                    '<td>',
                    '<div id="signature" style="width: 500px; height: 200px; display: none"></div>',
                    '<img id="existingsig" style="display: none; border: 0" />',
                    '</td>',
                '</tr>',
                '<tr>',
                    '<td></td>',
                    '<td>',
                    '<input id="enabletotp" data="enabletotp" class="asm-checkbox" type="checkbox" />',
                    '<label for="enabletotp">' + _("Enable two-factor authentication (2FA)") + '</label>',
                    '</td>',
                '<tr>',
                '<tr class="totp">',
                    '<td></td>',
                    '<td>' + html.info( _("Scan the QR code below with the Google Authenticator app for your mobile device.") ) + '</td>',
                '</tr>',
                '<tr class="totp">',
                    '<td></td>',
                    '<td><div id="qr2fa" style="padding: 10px; background: #fff;"></div></td>',
                '</tr>',

                '</table>',
                '<p class="centered">',
                    '<button id="save">' + html.icon("save") + ' ' + _("Save") + '</button>',
                '</p>',
                html.content_footer()
            ].join("\n");
        },

        totp_change: function() {
            $(".totp").toggle( $("#enabletotp").prop("checked") );
        },

        bind: function() {

            try {
                $("#signature").signature({ guideline: true });
                $("#button-change")
                    .button({ icons: { primary: "ui-icon-pencil" }, text: false })
                    .click(function() {
                        $("#existingsig").hide();
                        $("#signature").show();
                        $("#signature").signature("clear");
                    });
            }
            catch (excanvas) {
                log.error("failed creating signature canvas");   
            }

            $("#enabletotp").change(change_user_settings.totp_change);

            $("#save").button().click(async function() {
                $(".asm-content button").button("disable");
                header.show_loading();
                let formdata = $("input, select").toPOST();
                try {
                    if (!$("#signature").signature("isEmpty")) {
                        formdata += "&signature=" + encodeURIComponent($("#signature canvas").get(0).toDataURL("image/png"));
                    }
                } catch (excanvas) {
                    log.error("failed reading signature canvas", excanvas);
                }
                try {
                    await common.ajax_post("change_user_settings", formdata);
                    common.route("main", true);
                }
                catch(err) {
                    log.error(err, err);
                    $(".asm-content button").button("enable");
                }
            });

            // When the visual theme is changed, switch the CSS file and
            // the background.
            $("#systemtheme").change(function() {
                let theme = $("#systemtheme").val();
                if (theme == "") { theme = asm.theme; }
                $.each(controller.themes, function(i, v) {
                    let [tcode, tjq, tbg, tname] = v;
                    if (tcode == theme) {
                        let href = asm.jqueryuicss.replace("%(theme)s", tjq);
                        $("#jqt").attr("href", href);
                        $("body").css("background-color", tbg);
                        return false;
                    }
                });
            });

        },

        sync: function() {
            let u = controller.user;
            $("#realname").val(html.decode(u.REALNAME));
            $("#email").val(u.EMAILADDRESS);
            $("#olocale").select("value", u.LOCALEOVERRIDE);
            $("#systemtheme").select("value", u.THEMEOVERRIDE);
            $("#enabletotp").prop("checked", u.ENABLETOTP == 1);
            this.totp_change();
            if (controller.sigtype != "touch") { 
                $("#signature").closest("tr").hide(); 
            }
            if (u.SIGNATURE) {
                $("#signature").hide();
                $("#existingsig").attr("src", u.SIGNATURE).show();
            }
            else {
                $("#existingsig").hide();
                $("#signature").show();
            }
            let issuer = "ASM";
            if (controller.smcom) { issuer = "sheltermanager"; }
            let tfa_url = "otpauth://totp/" + issuer + ":" + encodeURIComponent(u.USERNAME) + "?secret=" + encodeURIComponent(u.OTPSECRET) + "&issuer=" + encodeURIComponent(issuer);
            new QRCode(document.getElementById("qr2fa"), tfa_url);
        },

        name: "change_user_settings",
        animation: "options",
        autofocus: "#realname",
        title: function() { return _("Change User Settings"); },
        routes: {
            "change_user_settings": function() { common.module_loadandstart("change_user_settings", "change_user_settings"); }
        }

    };

    common.module_register(change_user_settings);

});
