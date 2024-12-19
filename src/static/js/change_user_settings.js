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

        /** Sorts a list of pairs by the second element in each list */
        pair_sort_second: function(l) {
            return l.sort(function(a, b) {
                if (a[1] < b[1]) return -1;
                if (a[1] > b[1]) return 1;
                return 0;
            });
        },

        /** Reorders the list l and moves the selected items in configitem to the front */
        pair_selected_to_front: function(l, configitem) {
            let ci = configitem.split(",").reverse();
            $.each(ci, function(i, v) {
                v = String(v).trim();
                $.each(l, function(iv, vl) {
                    if (vl[0] == v) {
                        l.splice(iv, 1); // Remove matching element from the list
                        l.splice(0, 0, [ vl[0], vl[1] ]); // Reinsert it at the front
                        return false; // Break the loop
                    }
                });
            });
            return l;
        },

        /** Renders the list of quicklink options */
        quicklink_options: function() {
            let ql = [];
            $.each(header.QUICKLINKS_SET, function(k, v) {
                ql.push([ k, v[2] ]);
            });
            ql = this.pair_sort_second(ql);
            let userql = config.str(asm.user + "_QuicklinksID");
            if (userql == "") { userql = config.str("QuicklinksID"); }
            ql = this.pair_selected_to_front(ql, userql);
            return this.two_pair_options(ql);
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
                html.error(_("Your administrator requires all users to enable 2FA below in order to use the system."), "force2fa"),
                tableform.fields_render([
                    { label: _("Username"), type: "raw", markup: asm.user },
                    { post_field: "realname", label: _("Real name"), type: "text", doublesize: true },
                    { post_field: "email", label: _("Email Address"), type: "text", doublesize: true },
                    { post_field: "emaildefault", label: _("Make this the default reply address when I send email"), type: "check" },
                    { post_field: "theme", label: _("Visual Theme"), type: "select", options: change_user_settings.theme_list() },
                    { post_field: "locale", label: _("Locale"), type: "select", classes: "asm-iconselectmenu", 
                        options: '<option value="" data-style="background-image: url(static/images/flags/' + config.str("Locale") + '.png)">' + _("(use system)") + '</option>' + 
                            this.two_pair_options(controller.locales, true), colclasses: "bottomborder" },
                    { post_field: "quicklinksid", label: _("Quicklinks"), type: "selectmulti", options: change_user_settings.quicklink_options(), colclasses: "bottomborder" },
                    { post_field: "quickreportsid", label: _("Quick Reports"), type: "selectmulti", options: { displayfield: "TITLE", rows: controller.reports}, colclasses: "bottomborder" },
                    { post_field: "shelterview", label: _("Shelter view"), type: "select", 
                        options: '<option value="">' + _("(use system)") + '</option>' + html.shelter_view_options() },
                    { post_field: "signature", type: "raw", label: _("Signature"), 
                        xlabel: ' <button id="button-change" type="button" style="vertical-align: middle">' + _("Clear and sign again") + '</button>',
                        markup: '<div id="signature" style="width: 500px; height: 200px; display: none"></div>' +
                            '<img id="existingsig" style="display: none; border: 0" />' },
                    { post_field: "button-enable2fa", type: "raw", label: _("Two factor authentication (2FA)"), 
                        markup: '<input id="enabletotp" data="enabletotp" type="hidden" val="0" />' +
                            '<button id="button-enable2fa">' + _("Enable 2FA") + '</button>' +
                            '<button id="button-disable2fa" class="asm-redbutton">' + _("Disable 2FA") + '</button>' },
                    { rowclasses: "enable2fa", type: "raw", label: "", 
                        markup: html.info(_("Scan the QR code below with the Google Authenticator app for your mobile device.")) },
                    { rowclasses: "enable2fa", type: "raw", label: "", 
                        markup: '<div id="qr2fa" style="padding: 10px; background: #fff; display: inline-block"></div>' },
                    { rowclasses: "enable2fa", post_field: "twofavalidcode", type: "text", label: _("Enter the code from your app") },
                    { rowclasses: "disable2fa", post_field: "twofavalidpassword", type: "password", label: _("Confirm Password") }
                ], { full_width: false }),
                tableform.buttons_render([
                   { id: "save", icon: "save", text: _("Save") }
                ], { centered: true }),
                html.content_footer()
            ].join("\n");
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

            $("#button-save").button().click(async function() {
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

            $("#button-enable2fa").button().click(function() {
                $(".enable2fa").show();
            });

            $("#button-disable2fa").button().click(function() {
                $(".disable2fa").show();
            });

            // When the visual theme is changed, switch the CSS file and
            // the background.
            $("#theme").change(function() {
                let theme = $("#theme").val();
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
            if (common.querystring_param("force2fa") == "1") { 
                $("#force2fa").show(); 
                validate.highlight("button-enable2fa");
            }
            else {
                $("#force2fa").hide();
            }
            $("#realname").val(html.decode(u.REALNAME));
            $("#email").val(u.EMAILADDRESS);
            $("#locale").select("value", u.LOCALEOVERRIDE);
            $("#theme").select("value", u.THEMEOVERRIDE);
            $("#enabletotp").val(u.ENABLETOTP);
            $(".enable2fa, .disable2fa").hide();
            $("#button-enable2fa").toggle(u.ENABLETOTP == 0);
            $("#button-disable2fa").toggle(u.ENABLETOTP == 1);
            let userql = config.str(asm.user + "_QuicklinksID");
            if (userql == "") { userql = config.str("QuicklinksID"); }
            let ql = userql.split(",");
            $.each(ql, function(i, v) {
                $("#quicklinksid").find("option[value='" + common.trim(v + "']")).attr("selected", "selected");
            });
            $("#quicklinksid").change();
            let fr = config.str(asm.user + "_QuickReportsID").split(",");
            $.each(fr, function(i, v) {
                $("#quickreportsid").find("option[value='" + common.trim(v.split("=")[0] + "']")).attr("selected", "selected");
            });
            $("#quickreportsid").change();

            let usersv = config.str(asm.user + "_ShelterView");
            $("#shelterview").select("value", usersv);
            let emaildefault = config.bool(asm.user + "_EmailDefault");
            $("#emaildefault").prop("checked", emaildefault);
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
            if (controller.smcom && asm.user == asm.useraccount) { $("#enabletotp").closest("tr").hide(); } // disable 2FA for smcom master user for now
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
