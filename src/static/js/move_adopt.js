/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var move_adopt = {

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="movementid" type="hidden" />',
                html.content_header(_("Adopt an animal"), true),
                '<div id="bonddisplay" class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered"><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>',
                '<span id="bonddata" class="centered"></span>',
                '</p>',
                '</div>',
                '<div id="fosterinfo" class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered">',
                '<span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                _("This animal is currently fostered, it will be automatically returned first."),
                '</p>',
                '</div>',
                '<div id="retailerinfo" class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered">',
                '<span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                _("This animal is currently at a retailer, it will be automatically returned first."),
                '</p>',
                '</div>',
                '<div id="reserveinfo" class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered">',
                '<span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                _("This animal has active reservations, they will be cancelled."),
                '</p>',
                '</div>',
                '<div id="feeinfo" class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered">',
                '<span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                '<span class="subtext"></span>',
                '</p>',
                '</div>',

                '<div id="ownerwarn" class="ui-state-error ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered"><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>',
                '<span id="warntext" class="centered"></span>',
                '</p>',
                '</div>',
                '<div id="notonshelter" class="ui-state-error ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered"><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>',
                '<span class="centered">' + _("This animal is not on the shelter.") + '</span>',
                '</p>',
                '</div>',
                '<div id="onhold" class="ui-state-error ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered"><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>',
                '<span class="centered">' + _("This animal is currently held and cannot be adopted.") + '</span>',
                '</p>',
                '</div>',
                '<table class="asm-table-layout">',
                '<tr>',
                '<td>',
                '<label for="animal">' + _("Animal") + '</label>',
                '</td>',
                '<td>',
                '<input id="animal" data="animal" class="asm-animalchooser" type="hidden" value="" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="person">' + _("New Owner") + '</label>',
                '</td>',
                '<td>',
                '<input id="person" data="person" class="asm-personchooser" type="hidden" value="" />',
                '</td>',
                '</tr>',
                '<tr id="homecheckrow">',
                '<td>',
                '</td>',
                '<td>',
                '<input id="markhomechecked" data="homechecked" class="asm-checkbox" type="checkbox" />',
                '<label for="markhomechecked">' + _("Mark this owner homechecked") + '</label>',
                '</td>',
                '</tr>',
                '<tr id="movementnumberrow">',
                '<td><label for="movementnumber">' + _("Movement Number") + '</label></td>',
                '<td><input id="movementnumber" data="movementnumber" class="asm-textbox" title=',
                '"' + html.title(_("A unique number to identify this movement")) + '"',
                ' /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="movementdate">' + _("Date") + '</label></td>',
                '<td>',
                '<input id="movementdate" data="movementdate" class="asm-textbox asm-datebox" title="' + _("The date the animal was adopted") + '" />',
                '</td>',
                '</tr>',
                '<tr id="trialrow1">',
                '<td></td>',
                '<td><input id="trial" data="trial" class="asm-checkbox" type="checkbox" title=\'' + _("Is this a trial adoption?") + '\' />',
                '<label for="trial">' + _("Trial adoption") + '</label>',
                '</td>',
                '</tr>',
                '<tr id="trialrow2">',
                '<td><label for="trialenddate">' + _("Trial ends on") + '</label></td>',
                '<td>',
                '<input id="trialenddate" data="trialenddate" class="asm-textbox asm-datebox" title=\'' + _("The date the trial adoption is over") + '\' />',
                '</td>',
                '</tr>',
                '<tr id="insurancerow">',
                '<td><label for="insurance">' + _("Insurance") + '</label></td>',
                '<td>',
                '<input id="insurance" class="asm-textbox" data="insurance" title="' + html.title(_("If the shelter provides initial insurance cover to new adopters, the policy number")) + '" />',
                '<button id="button-insurance">' + _("Issue a new insurance number for this animal/adoption") + '</button>',
                '</td>',
                '</tr>',
                '</table>',
                html.content_footer(),
                html.content_header(_("Payment"), true),
                '<table class="asm-table-layout">',
                '<tr>',
                '<td>',
                '<label for="donationtype">' + _("Type") + '</label>',
                '</td>',
                '<td>',
                '<select id="donationtype" data="donationtype" class="asm-selectbox">',
                html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="payment">' + _("Method") + '</label>',
                '</td>',
                '<td>',
                '<select id="payment" data="payment" class="asm-selectbox">',
                html.list_to_options(controller.paymenttypes, "ID", "PAYMENTNAME"),
                '</select>',
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
                '<tr>',
                '<td>',
                '<label for="amount">' + _("Amount") + '</label>',
                '</td>',
                '<td>',
                '<input id="amount" data="amount" class="asm-currencybox asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr class="seconddonation">',
                '<td>',
                '<label for="donationtype2">' + _("Type") + '</label>',
                '</td>',
                '<td>',
                '<select id="donationtype2" data="donationtype2" class="asm-selectbox">',
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
                '<tr>',
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
                '<tr class="seconddonation">',
                '<td>',
                '<label for="amount2">' + _("Amount") + '</label>',
                '</td>',
                '<td>',
                '<input id="amount2" data="amount2" class="asm-currencybox asm-textbox" />',
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
                '</table>',
                html.content_footer(),
                html.content_header(_("Boarding Cost"), true),
                '<div id="costdisplay" class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered"><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                '<span id="costdata" class="centered"></span>',
                '</p>',
                '</div>',
                '<table id="costtable" class="asm-table-layout">',
                '<tr>',
                '<td><label for="costcreate">' + _("Cost record") + '</label></td>',
                '<td>',
                '<input id="costamount" data="costamount" type="hidden" />',
                '<input id="costtype" data="costtype" type="hidden" />',
                '<select id="costcreate" data="costcreate" class="asm-selectbox">',
                '<option value="0">' + _("Don't create a cost record") + '</option>',
                '<option value="1" selected="selected">' + _("Create a cost record") + '</option>',
                '</select>',
                '</td>',
                '</tr>',
                '</table>',
                html.content_footer(),
                html.box(5),
                '<button id="adopt">' + html.icon("movement") + ' ' + _("Adopt") + '</button>',
                '</div>',
                '</div>'
            ].join("\n");
        },

        bind: function() {
            var validation = function() {
                // Remove any previous errors
                header.hide_error();
                validate.reset();
                // animal
                if ($("#animal").val() == "") {
                    header.show_error(_("Movements require an animal."));
                    validate.highlight("animal");
                    return false;
                }
                // person
                if ($("#person").val() == "") {
                    header.show_error(_("This type of movement requires a person."));
                    validate.highlight("person");
                    return false;
                }
                // date
                if ($.trim($("#movementdate").val()) == "") {
                    header.show_error(_("This type of movement requires a date."));
                    validate.highlight("movementdate");
                    return false;
                }
                return true;
            };

            // Callback when animal is changed
            var current_animal = null;
            $("#animal").animalchooser().bind("animalchooserchange", function(event, rec) {
                current_animal = rec;
                // Hide things before we start
                $("#bonddisplay").fadeOut();
                $("#costdisplay").closest(".ui-widget").fadeOut();
                $("#fosterinfo").fadeOut();
                $("#reserveinfo").fadeOut();
                $("#retailerinfo").fadeOut();
                $("#feeinfo").fadeOut();
                $("#notonshelter").fadeOut();
                $("#onhold").fadeOut();
                $("#adopt").button("enable");

                // If the animal is not on the shelter and not fostered or at a retailer, 
                // bail out now because we shouldn't be able to move the animal.
                if (rec.ARCHIVED == 1 && rec.ACTIVEMOVEMENTTYPE != 2 && rec.ACTIVEMOVEMENTTYPE != 8) {
                    $("#notonshelter").fadeIn();
                    $("#adopt").button("disable");
                    return;
                }

                // If the animal is held, we shouldn't be allowed to adopt it
                if (rec.ISHOLD == 1) {
                    $("#onhold").fadeIn();
                    $("#adopt").button("disable");
                    return;
                }

                if (rec.ACTIVEMOVEMENTTYPE == "2") {
                    $("#fosterinfo").fadeIn();
                }

                if (rec.ACTIVEMOVEMENTTYPE == "8") {
                    $("#retailerinfo").fadeIn();
                }

                if (rec.HASACTIVERESERVE == "1" && config.bool("CancelReservesOnAdoption")) {
                    $("#reserveinfo").fadeIn();
                }

                // Check for bonded animals and warn
                if (rec.BONDEDANIMALID != "0" || rec.BONDEDANIMAL2ID != "0") {
                    var bw = "";
                    if (rec.BONDEDANIMAL1NAME != "" && rec.BONDEDANIMAL1NAME != null) {
                        bw += rec.BONDEDANIMAL1CODE + " - " + rec.BONDEDANIMAL1NAME;
                    }
                    if (rec.BONDEDANIMAL2NAME != "" && rec.BONDEDANIMAL2NAME != null) {
                        if (bw != "") { bw += ", "; }
                        bw += rec.BONDEDANIMAL2CODE + " - " + rec.BONDEDANIMAL2NAME;
                    }
                    if (bw != "") {
                        $("#bonddata").html(_("This animal is bonded with {0}. Adoption movement records will be created for all bonded animals.").replace("{0}", bw));
                        $("#bonddisplay").fadeIn();
                    }
                }

                // Grab cost information if option is on
                if (config.bool("CreateBoardingCostOnAdoption")) {
                    var formdata = "mode=cost&id=" + rec.ID;
                    common.ajax_post("move_adopt", formdata)
                        .then(function(data) {
                            var bits = data.split("||");
                            $("#costdata").html(bits[1]);
                            $("#costamount").val(format.currency_to_int(bits[0]));
                            $("#costtype").val(config.str("BoardingCostType"));
                            $("#costdisplay").closest(".ui-widget").fadeIn();
                        });
                }

                // If we have adoption fee fields, override the first donation
                // with the fee from the animal assuming it's nonzero
                if (!config.bool("DontShowAdoptionFee") && rec.FEE) {
                    $("#amount").currency("value", rec.FEE);
                    $("#feeinfo .subtext").html( _("This animal has an adoption fee of {0}").replace("{0}", format.currency(rec.FEE)));
                    $("#feeinfo").fadeIn();
                }

                // Update the list of document templates
                var formdatat = "mode=templates&id=" + rec.ID;
                common.ajax_post("move_adopt", formdatat)
                    .then(function(data) { 
                        $("#templatelist").html(data); 
                    });

            });

            // Callback when person is changed
            var current_person = null;
            $("#person").personchooser().bind("personchooserchange", function(event, rec) {
                current_person = rec;

                // Show tickbox if owner not homechecked
                if (rec.IDCHECK == 0) {
                    $("#markhomechecked").attr("checked", true);
                    $("#homecheckrow").fadeIn();
                }

                // Set the gift aid box if they are registered
                $("#giftaid").select("value", rec.ISGIFTAID);
           
                // Owner banned?
                if (rec.ISBANNED == 1 && config.bool("WarnBannedOwner")) {
                    $("#warntext").html(_("This person has been banned from adopting animals"));
                    $("#ownerwarn").fadeIn();
                    return;
                }

                // Owner previously under investigation
                if (rec.INVESTIGATION > 0) {
                    $("#warntext").html(_("This person has been under investigation"));
                    $("#ownerwarn").fadeIn();
                    return;
                }

                // Owner part of animal control incident
                if (rec.INCIDENT > 0) {
                    $("#warntext").html(_("This person has an animal control incident against them"));
                    $("#ownerwarn").fadeIn();
                    return;
                }

                // Owner not homechecked?
                if (rec.IDCHECK == 0 && config.bool("WarnNoHomeCheck")) {
                    $("#warntext").html(_("This person has not passed a homecheck"));
                    $("#ownerwarn").fadeIn();
                    return;
                }

                $("#ownerwarn").fadeOut();

            });

            // What to do when donation type is changed
            var donationtype_change = function() {
                var dc = common.get_field(controller.donationtypes, $("#donationtype").select("value"), "DEFAULTCOST");
                $("#amount").currency("value", dc);
            };
            $("#donationtype").change(function() {
                donationtype_change();
            });

            // What to do when second donation type is changed
            var donationtype2_change = function() {
                var dc = common.get_field(controller.donationtypes, $("#donationtype2").select("value"), "DEFAULTCOST");
                $("#amount2").currency("value", dc);
            };
            $("#donationtype2").change(function() {
                donationtype2_change();
            });

            $("#costdisplay").closest(".ui-widget").hide();
            $("#bonddisplay").hide();
            $("#ownerwarn").hide();
            $("#notonshelter").hide();
            $("#onhold").hide();
            $("#fosterinfo").hide();
            $("#reserveinfo").hide();
            $("#feeinfo").hide();
            $("#retailerinfo").hide();
            $("#homecheckrow").hide();
            $("#trialrow1").hide();
            $("#trialrow2").hide();

            $("#movementnumberrow").hide();
            if (config.bool("MovementNumberOverride")) {
                $("#movementnumberrow").show();
            }

            if (config.bool("DontShowInsurance")) {
                $("#insurancerow").hide();
            }

            if (asm.locale != "en_GB") { $("#giftaidrow").hide(); }

            // Insurance related stuff
            $("#button-insurance")
                .button({ icons: { primary: "ui-icon-cart" }, text: false })
                .click(function() {
                $("#button-insurance").button("disable");
                common.ajax_post("move_adopt", "mode=insurance")
                    .then(function(result) {
                        $("#insurance").val(result);
                    })
                    .always(function() {
                        $("#button-insurance").button("enable");
                    });
            });
            if (!config.bool("UseAutoInsurance")) { $("#button-insurance").button("disable"); }

            $("#page1").show();
            $("#page2").hide();
            $("#asm-adopt-accordion").accordion({
                heightStyle: "content"
            });

            // Set default values
            $("#donationtype").val(config.str("AFDefaultDonationType"));
            donationtype_change();
            $("#movementdate").datepicker("setDate", new Date());

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

            // Show trial fields if option is set
            if (config.bool("TrialAdoptions")) {
                $("#trialrow1").show();
                $("#trialrow2").show();
            }

            $("#adopt").button().click(function() {
                if (!validation()) { return; }
                $("#adopt").button("disable");
                header.show_loading(_("Creating..."));

                var formdata = $("input, select").toPOST();
                common.ajax_post("move_adopt", formdata)
                    .then(function(data) {
                        $("#movementid").val(data);
                        header.hide_loading();

                        var u = "move_gendoc?" +
                            "mode=ANIMAL&id=" + $("#animal").val() +
                            "&message=" + encodeURIComponent(common.base64_encode(_("Adoption successfully created.") + " " + 
                                $(".animalchooser-display").html() + " " + html.icon("right") + " " +
                                $(".personchooser-display .justlink").html() ));
                        common.route(u);

                    })
                    .fail(function() {
                        $("#adopt").button("enable");
                    });
            });
        },

        destroy: function() {
            common.widget_destroy("#animal");
            common.widget_destroy("#person");
        },

        name: "move_adopt",
        animation: "newdata",
        autofocus: "#asm-content button:first",
        title: function() { return _("Adopt an animal"); },
        routes: {
            "move_adopt": function() { common.module_loadandstart("move_adopt", "move_adopt"); }
        }

    };

    common.module_register(move_adopt);

});
