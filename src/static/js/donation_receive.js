/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var donation_receive = {

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="donationid" type="hidden" />',
                '<div id="page1">',
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
                '<tr>',
                '<td><label for="received">' + _("Received") + '</label></td>',
                '<td>',
                '<input id="received" data="received" class="asm-textbox asm-datebox" title=\'' + _("The date the payment was received") + '\' />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="type">' + _("Type") + '</label>',
                '</td>',
                '<td>',
                '<select id="type" data="type" class="asm-selectbox">',
                html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<td>',
                '<label for="payment">' + _("Method") + '</label>',
                '</td>',
                '<td>',
                '<select id="payment" data="payment" class="asm-selectbox">',
                html.list_to_options(controller.paymenttypes, "ID", "PAYMENTNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="amount">' + _("Amount") + '</label>',
                '</td>',
                '<td>',
                '<input id="amount" data="amount" class="asm-currencybox asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr class="overrideaccount">',
                '<td></td>',
                '<td>',
                html.info(_("Create a matching transaction for this payment and deposit it in this account")),
                '</td>',
                '</tr>',
                '<tr class="overrideaccount">',
                '<td>',
                '<label for="destaccount">' + _("Deposit account") + '</label>',
                '</td>',
                '<td>',
                '<select id="destaccount" data="destaccount" class="asm-selectbox">',
                html.list_to_options(controller.accounts, "ID", "CODE"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr class="seconddonation">',
                '<td>',
                '<label for="type2">' + _("Type") + '</label>',
                '</td>',
                '<td>',
                '<select id="type2" data="type2" class="asm-selectbox">',
                html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr class="seconddonation">',
                '<td>',
                '<label for="payment2">' + _("Method") + '</label>',
                '</td>',
                '<td>',
                '<select id="payment2" data="payment2" class="asm-selectbox">',
                html.list_to_options(controller.paymenttypes, "ID", "PAYMENTNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr class="seconddonation">',
                '<td>',
                '<label for="amount2">' + _("Amount") + '</label>',
                '</td>',
                '<td>',
                '<input id="amount2" data="amount2" class="asm-currencybox asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr class="seconddonation overrideaccount">',
                '<td></td>',
                '<td>',
                html.info(_("Create a matching transaction for this payment and deposit it in this account")),
                '</td>',
                '</tr>',
                '<tr class="seconddonation overrideaccount">',
                '<td>',
                '<label for="destaccount2">' + _("Deposit account") + '</label>',
                '</td>',
                '<td>',
                '<select id="destaccount2" data="destaccount2" class="asm-selectbox">',
                html.list_to_options(controller.accounts, "ID", "CODE"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr id="giftaidrow">',
                '<td><label for="giftaid">' + _("Gift Aid") + '</label></td>',
                '<td><select id="giftaid" data="giftaid" class="asm-selectbox">',
                '<option value="0">' + _("Not eligible for gift aid") + '</option>',
                '<option value="1">' + _("Eligible for gift aid") + '</option>',
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '</table>',
                '<div class="centered" style="margin-top: 10px">',
                '<button id="receive">' + html.icon("donation") + ' ' + _("Receive") + '</button>',
                '</div>',
                html.content_footer(),
                '</div>',
                '<div id="page2">',
                html.info("", "successmessage"),
                '<div id="asm-donation-accordion">',
                '<h3><a href="#">' + _("Generate documentation") + '</a></h3>',
                '<div id="templatelist">',
                '</div>',
                '</div>',
                '</div>'
            ].join("\n");
        },

        bind: function() {
            var validation = function() {
                // Remove any previous errors
                header.hide_error();
                $("label").removeClass("ui-state-error-text");
                // person
                if ($("#person").val() == "") {
                    header.show_error(_("Payments require a person"));
                    $("label[for='person']").addClass("ui-state-error-text");
                    $("#person").focus();
                    return false;
                }
                // date
                if ($.trim($("#received").val()) == "") {
                    header.show_error(_("Payments require a received date"));
                    $("label[for='received']").addClass("ui-state-error-text");
                    $("#received").focus();
                    return false;
                }
                return true;
            };

            // Look up default amount when type is changed
            var donationtype_change = function() {
                common.ajax_post("move_adopt", "mode=donationdefault&donationtype=" + $("#type").val())
                    .then(function(result) { 
                        $("#amount").currency("value", result); 
                    });
            };

            var donationtype2_change = function() {
                common.ajax_post("move_adopt", "mode=donationdefault&donationtype=" + $("#type2").val())
                    .then(function(result) { 
                        $("#amount2").currency("value", result); 
                    });
            };

            $("#type").change(function() {
                donationtype_change();
            });

            $("#type2").change(function() {
                donationtype2_change();
            });

            // Hide giftaid for non-GB
            if (asm.locale != "en_GB") { $("#giftaidrow").hide(); }

            // If we're creating accounting transactions and the override
            // option is set, allow override of the destination account
            if (config.bool("CreateDonationTrx") && config.bool("DonationTrxOverride")) {
                $(".overrideaccount").show();
                // Set it to the default account
                $("#destaccount").val(config.str("DonationTargetAccount"));
            }
            else {
                $(".overrideaccount").hide();
            }

            // Show second donation field if option is set
            if (config.bool("SecondDonationOnMove")) {
                $(".seconddonation").show();
                $("#donationtype2").val(config.str("AFDefaultDonationType"));
                donationtype2_change();
                if (!config.bool("CreateDonationTrx") || !config.bool("DonationTrxOverride")) {
                    $(".overrideaccount.seconddonation").hide();
                }
            }
            else {
                $(".seconddonation").hide();
            }

            $("#page1").show();
            $("#page2").hide();
            $("#asm-donation-accordion").accordion({
                heightStyle: "content"
            });

            // Set default values
            $("#type").val(config.str("AFDefaultDonationType"));
            donationtype_change();
            $("#destaccount, #destaccount2").select("value", config.str("DonationTargetAccount"));
            $("#received").datepicker("setDate", new Date());

            $("#receive").button().click(function() {
                if (!validation()) { return; }
                $("#receive").button("disable");
                header.show_loading(_("Creating..."));

                var formdata = $("input, select").toPOST();
                common.ajax_post("donation_receive", formdata)
                    .then(function(result) { 
                        header.hide_loading();
                        $("#successmessage p").append(
                            _("Payment of {0} successfully received ({1}).")
                                .replace("{0}", $("#amount").val())
                                .replace("{1}", $("#received").val()));
                        // Update the list of document templates
                        return common.ajax_post("donation_receive", "mode=templates&id=" + result);
                    })
                    .then(function(data) { 
                        $("#templatelist").html(data); 
                        $("#page1").fadeOut(function() {
                            $("#page2").fadeIn();
                        });
                    })
                    .always(function() {
                        $("#receive").button("enable");
                    });
            });
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
