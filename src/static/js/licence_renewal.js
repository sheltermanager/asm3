/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const licence_renewal = {

        lastperson: null,

        render: function() {
            return [
                '<div id="asm-content">',
                html.content_header(_("Renew license"), true),
                tableform.fields_render([
                    { post_field: "animal", type: "animal", label: _("Animal (optional)") },
                    { post_field: "person", type: "person", label: _("Person") },
                    { post_field: "issuedate", type: "date", label: _("Issued") },
                    { post_field: "expirydate", type: "date", label: _("Expiry") },
                    { post_field: "number", type: "text", label: _("Number") },
                    { post_field: "type", type: "select", label: _("Type"), options: { displayfield: "LICENCETYPENAME", rows: controller.licencetypes }},
                    { post_field: "fee", type: "currency", label: _("Fee") }
                ], { full_width: false }),
                html.content_footer(),
                '<div id="payment"></div>',
                tableform.buttons_render([
                   { id: "renew", icon: "licence", text: _("Renew licence") }
                ], { render_box: true }),
                '</div>'
            ].join("\n");
        },

        type_change: function() {
            let dc = common.get_field(controller.licencetypes, $("#type").select("value"), "DEFAULTCOST");
            $("#amount1").currency("value", dc);
            $("#fee").currency("value", dc);
            $("#payment").payments("update_totals");
        },

        bind: function() {
            const validation = function() {
                // Remove any previous errors
                header.hide_error();
                validate.reset();
                // person
                if ($("#person").val() == "") {
                    header.show_error(_("License requires a person"));
                    validate.highlight("person");
                    return false;
                }
                // number
                if ($("#number").val() == "") {
                    header.show_error(_("License requires a number"));
                    validate.highlight("number");
                    return false;
                }
                // date
                if (common.trim($("#issuedate").val()) == "" || common.trim($("#expirydate").val()) == "") {
                    header.show_error(_("License requires issued and expiry dates"));
                    validate.highlight("issuedate");
                    return false;
                }
                return true;
            };

            // Callback when person is changed
            $("#person").personchooser().bind("personchooserchange", function(event, rec) {
                licence_renewal.lastperson = rec;
                // Default giftaid if the person is registered
                $("#payment").payments("option", "giftaid", rec.ISGIFTAID == 1);
                $("#giftaid1").prop("checked", rec.ISGIFTAID == 1);
            });

            // Generate code button
            $("#number").after('<button id="button-number">' + _("Generate a unique license number") + '</button>');
            $("#button-number")
                .button({ icons: { primary: "ui-icon-refresh" }, text: false })
                .click(function() {
                    $("#number").val(format.padleft(common.generate_random_code(10, true), 10));
                });

            // Payments
            $("#payment").payments({ controller: controller });

            // When type changes, update the fee
            $("#type").change(licence_renewal.type_change);

            $("#button-renew").button().click(async function() {
                if (!validation()) { return; }
                $("#button-renew").button("disable");
                try {
                    header.show_loading(_("Creating..."));
                    let formdata = $("input, select").toPOST();
                    let result = await common.ajax_post("licence_renewal", formdata);
                    header.hide_loading();
                    if (!result) {
                        header.show_error(_("Failed to renew license.")); 
                    }
                    else {
                        let msg = _("Licence for {0} successfully renewed {1} - {2}")
                                .replace("{0}", licence_renewal.lastperson.OWNERNAME)
                                .replace("{1}", $("#issuedate").val())
                                .replace("{2}", $("#expirydate").val());
                        let u = "move_gendoc?" +
                            "linktype=LICENCE&id=" + result +
                            "&message=" + encodeURIComponent(common.base64_encode(msg));
                        common.route(u);
                    }
                }
                finally {
                    $("#button-renew").button("enable");
                }
            });
        },

        sync: function() {
            $("#issuedate").date("today");
            licence_renewal.type_change();

            validate.indicator([ "person", "number", "issuedate" ]);

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");
        },

        destroy: function() {
            common.widget_destroy("#animal");
            common.widget_destroy("#person");
        },

        name: "licence_renewal",
        animation: "newdata",
        autofocus: "#asm-content button:first",
        title: function() { return _("Renew license"); },
        routes: {
            "licence_renewal": function() {
                common.module_loadandstart("licence_renewal", "licence_renewal");
            }
        }


    };

    common.module_register(licence_renewal);

});
