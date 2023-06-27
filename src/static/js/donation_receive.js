/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const donation_receive = {

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="donationid" type="hidden" />',
                html.content_header(_("Receive a payment"), true),
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
                '<tr style="display: none">',
                '<td><label for="movement">' + _("Movement") + '</label></td>',
                '<td>',
                '<select id="movement" data="movement" class="asm-selectbox"></select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="received">' + _("Received") + '</label></td>',
                '<td>',
                '<input id="received" data="received" class="asm-textbox asm-datebox" title=\'' + _("The date the payment was received") + '\' />',
                '</td>',
                '</tr>',
                /* NOT EDITABLE - LET BACKEND SUPPLY
                '<tr>',
                '<td><label for="receiptnumber">' + _("Receipt No") + '</label></td>',
                '<td>',
                '<input id="receiptnumber" data="receiptnumber" class="asm-textbox" type="text" />',
                '</td>',
                '</tr>',
                */
                '</table>',
                html.content_footer(),
                '<div id="payment"></div>',
                html.box(5),
                '<button id="receive">' + html.icon("donation") + ' ' + _("Receive") + '</button>',
                '</div>',
                '</div>'
            ].join("\n");
        },

        bind: function() {
            const validation = function() {
                // Remove any previous errors
                header.hide_error();
                validate.reset();
                // person
                if ($("#person").val() == "") {
                    header.show_error(_("Payments require a person"));
                    validate.highlight("person");
                    return false;
                }
                // date
                if (common.trim($("#received").val()) == "") {
                    header.show_error(_("Payments require a received date"));
                    validate.highlight("received");
                    return false;
                }
                return true;
            };

            // Callback when person is changed
            $("#person").personchooser().bind("personchooserchange", function(event, rec) {
                // Default giftaid if the person is registered
                $("#payment").payments("option", "giftaid", rec.ISGIFTAID == 1);
                $("#giftaid1").prop("checked", rec.ISGIFTAID == 1);
                // Update movements if available
                donation_receive.update_movements(rec.ID);
            });

            // Payments
            $("#payment").payments({ controller: controller });

            // Set default values
            $("#received").date("today");

            /* NOT NECESSARY, BACKEND WILL SUPPLY
            common.ajax_post("donation", "mode=nextreceipt")
                .then(function(result) {
                    $("#receiptnumber").val(result);
                });
            */

            $("#receive").button().click(async function() {
                if (!validation()) { return; }
                $("#receive").button("disable");
                header.show_loading(_("Creating..."));
                try {
                    let formdata = "mode=create&" + $("input, select").toPOST();
                    let result = await common.ajax_post("donation_receive", formdata);
                    header.hide_loading();
                    if (!result) {
                        header.show_error(_("Failed to create payment.")); 
                    }
                    else {
                        let msg = _("Payment of {0} successfully received ({1}).")
                                .replace("{0}", $("#totalamount").html())
                                .replace("{1}", $("#received").val());
                        let u = "move_gendoc?" +
                            "linktype=DONATION&id=" + result +
                            "&message=" + encodeURIComponent(common.base64_encode(msg));
                        common.route(u);
                    }
                }
                finally {
                    $("#receive").button("enable");
                }
            });

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");
        
        },

        update_movements: async function(personid) {
            let formdata = "mode=personmovements&personid=" + personid;
            let result = await common.ajax_post("donation", "mode=personmovements&personid=" + personid);
            let h = "<option value=\"0\"></option>";
            $.each(jQuery.parseJSON(result), function(i,v) {
                h += "<option value=\"" + v.ID + "\">";
                h += v.ADOPTIONNUMBER + " - " + v.MOVEMENTNAME + ": " + v.ANIMALNAME;
                h += "</option>";
            });
            $("#movement").html(h);
            $("#movement").closest("tr").fadeIn();
        },

        destroy: function() {
            common.widget_destroy("#animal");
            common.widget_destroy("#person");
        },

        name: "donation_receive",
        animation: "newdata",
        autofocus: "#asm-content button:first",
        title: function() { return _("Receive a payment"); },
        routes: {
            "donation_receive": function() {
                common.module_loadandstart("donation_receive", "donation_receive");
            }
        }


    };

    common.module_register(donation_receive);

});
