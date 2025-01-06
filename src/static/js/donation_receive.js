/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const donation_receive = {

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="donationid" type="hidden" />',
                html.content_header(_("Receive a payment"), true),
                tableform.fields_render([
                    { post_field: "animal", type: "animal", label: _("Animal (optional)") },
                    { post_field: "person", type: "person", label: _("Person") },
                    { post_field: "movement", type: "select", label: _("Movement"), options: "" },
                    { post_field: "received", type: "date", label: _("Received") },
                ], { full_width: false }),
                html.content_footer(),
                '<div id="payment"></div>',
                html.box(5),
                tableform.buttons_render([
                    { id: "receive", icon: "donation", text: _("Receive") }
                ]),
                '</div></div>'
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

            $("#button-receive").button().click(async function() {
                if (!validation()) { return; }
                $("#button-receive").button("disable");
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
                    $("#button-receive").button("enable");
                }
            });

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");

            $("#movementrow").hide();
        
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
            $("#movementrow").fadeIn();
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
