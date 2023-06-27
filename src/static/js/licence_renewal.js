/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const licence_renewal = {

        lastperson: null,

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="donationid" type="hidden" />',
                html.content_header(_("Renew license"), true),
                '<table class="asm-table-layout">',
                '<tr>',
                '<td>',
                '<label for="animal">' + _("Animal (optional)") + '</label>',
                '</td>',
                '<td>',
                '<input id="animal" data="animal" type="hidden" class="asm-animalchooser" value=\'\' />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="person">' + _("Person") + '</label>',
                '</td>',
                '<td>',
                '<input id="person" data="person" type="hidden" class="asm-personchooser" value=\'\' />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="issuedate">' + _("Issued") + '</label></td>',
                '<td>',
                '<input id="issuedate" data="issuedate" type="text" class="asm-textbox asm-datebox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="expirydate">' + _("Expiry") + '</label></td>',
                '<td>',
                '<input id="expirydate" data="expirydate" type="text" class="asm-textbox asm-datebox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="number">' + _("Number") + '</label></td>',
                '<td>',
                '<input id="number" data="number" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="type">' + _("Type") + '</label></td>',
                '<td>',
                '<select id="type" data="type" class="asm-selectbox">',
                html.list_to_options(controller.licencetypes, "ID", "LICENCETYPENAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="fee">' + _("Fee") + '</label></td>',
                '<td>',
                '<input id="fee" data="fee" type="text" class="asm-textbox asm-currencybox" />',
                '</td>',
                '</tr>',
                '</table>',
                html.content_footer(),
                '<div id="payment"></div>',
                html.box(5),
                '<button id="renew">' + html.icon("licence") + ' ' + _("Renew licence") + '</button>',
                '</div>',
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

            // Payments
            $("#payment").payments({ controller: controller });

            // When type changes, update the fee
            $("#type").change(licence_renewal.type_change);

            $("#renew").button().click(async function() {
                if (!validation()) { return; }
                $("#renew").button("disable");
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
                    $("#renew").button("enable");
                }
            });
        },

        sync: function() {
            $("#issuedate").date("today");
            licence_renewal.type_change();

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
