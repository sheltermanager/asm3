/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var move_reserve = {

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="movementid" type="hidden" />',
                '<div id="page1">',
                html.content_header(_("Reserve an animal"), true),
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
                '<div id="multiplereserve" class="ui-state-error ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered"><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>',
                '<span class="centered">' + _("This animal already has an active reservation.") + '</span>',
                '</p>',
                '</div>',
                '<div id="notonshelter" class="ui-state-error ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered"><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>',
                '<span class="centered">' + _("This animal is not on the shelter.") + '</span>',
                '</p>',
                '</div>',
                '<table class="asm-table-layout">',
                '<tr>',
                '<td>',
                '<label for="animal">' + _("Animal") + '</label>',
                '</td>',
                '<td>',
                '<input id="animal" data="animal" type="hidden" class="asm-animalchooser" value=\'\' />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="person">' + _("Reservation For") + '</label>',
                '</td>',
                '<td>',
                '<input id="person" data="person" type="hidden" class="asm-personchooser" value=\'\' />',
                '</td>',
                '</tr>',
                '<tr id="movementnumberrow">',
                '<td><label for="movementnumber">' + _("Movement Number") + '</label></td>',
                '<td><input id="movementnumber" data="movementnumber" class="asm-textbox" title=',
                '"' + html.title(_("A unique number to identify this movement")) + '"',
                ' /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="reservationdate">' + _("Date") + '</label></td>',
                '<td>',
                '<input id="reservationdate" data="reservationdate" class="asm-textbox asm-datebox" title="' + html.title(_("The date the reservation is effective from")) + '" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="reservationstatus">' + _("Status") + '</label></td>',
                '<td>',
                '<select id="reservationstatus" data="reservationstatus" class="asm-selectbox">',
                html.list_to_options(controller.reservationstatuses, "ID", "STATUSNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '</table>',
                html.content_footer(),
                html.content_header(_("Payment"), true),
                '<table id="table-payment" class="asm-table-layout">',
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
                html.box(5),
                '<button id="reserve">' + html.icon("movement") + ' ' + _("Reserve") + '</button>',
                '</div>',
                '</div>',
                '<div id="page2">',
                '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em;">',
                '<p class="centered"><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                '<span class="centered">' + _("Reservation successfully created."),
                '</span>',
                '<span class="centered" id="reservefrom"></span>',
                html.icon("right"),
                '<span class="centered" id="reserveto"></span>',
                '</p>',
                '</div>',
                '<div id="asm-reserve-accordion">',
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
                // animal
                if ($("#animal").val() == "") {
                    header.show_error(_("Movements require an animal"));
                    $("label[for='animal']").addClass("ui-state-error-text");
                    $("#animal").focus();
                    return false;
                }
                // person
                if ($("#person").val() == "") {
                    header.show_error(_("This type of movement requires a person."));
                    $("label[for='person']").addClass("ui-state-error-text");
                    $("#person").focus();
                    return false;
                }
                // date
                if ($.trim($("#reservationdate").val()) == "") {
                    header.show_error(_("This type of movement requires a date."));
                    $("label[for='reservationdate']").addClass("ui-state-error-text");
                    $("#reservationdate").focus();
                    return false;
                }
                return true;
            };

            // Callback when animal is changed
            $("#animal").animalchooser().bind("animalchooserchange", function(event, rec) {
              
                // Hide things before we start
                $("#notonshelter").fadeOut();
                $("#feeinfo").fadeOut();
                $("#reserve").button("enable");

                // If the animal is not on the shelter and not fostered, show that warning
                // and stop everything else
                if (rec.ARCHIVED == "1" && rec.ACTIVEMOVEMENTTYPE != 2) {
                    $("#notonshelter").fadeIn();
                    $("#reserve").button("disable");
                    return;
                }

                // If the animal has an active reserve, show the warning, but
                // things can still continue
                if (rec.HASACTIVERESERVE == "1") {
                    $("#multiplereserve").fadeIn();
                }

                // If we have an adoption fee, show it in the info bar
                if (!config.bool("DontShowAdoptionFee") && rec.FEE) {
                    // $("#amount").currency("value", rec.FEE); #122 disabled due to less relevant for reserves
                    $("#feeinfo .subtext").html( _("This animal has an adoption fee of {0}").replace("{0}", format.currency(rec.FEE)));
                    $("#feeinfo").fadeIn();
                }

                // Update the list of document templates
                var formdata = "mode=templates&id=" + rec.ID;
                common.ajax_post("move_reserve", formdata, function(data) { $("#templatelist").html(data); });

            });

            // Callback when person is changed
            $("#person").personchooser().bind("personchooserchange", function(event, rec) {
         
                // Set the gift aid box if they are registered
                $("#giftaid").select("value", rec.ISGIFTAID);
           
                // Owner banned?
                if (rec.ISBANNED == 1 && config.bool("WarnBannedOwner")) {
                    $("#warntext").text(_("This person has been banned from adopting animals"));
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
                    $("#warntext").text(_("This person has not passed a homecheck"));
                    $("#ownerwarn").fadeIn();
                    return;
                }

                $("#ownerwarn").fadeOut();

            });

            // What to do when donation type is changed
            var donationtype_change = function() {
                if (!config.bool("DonationOnMoveReserve")) { return; }
                var dc = common.get_field(controller.donationtypes, $("#donationtype").select("value"), "DEFAULTCOST");
                $("#amount").currency("value", dc);
            };
            $("#donationtype").change(function() {
                donationtype_change();
            });

            // What to do when second donation type is changed
            var donationtype2_change = function() {
                if (!config.bool("DonationOnMoveReserve")) { return; }
                var dc = common.get_field(controller.donationtypes, $("#donationtype2").select("value"), "DEFAULTCOST");
                $("#amount2").currency("value", dc);
            };
            $("#donationtype2").change(function() {
                donationtype2_change();
            });

            $("#ownerwarn").hide();
            $("#notonshelter").hide();
            $("#feeinfo").hide();
            $("#multiplereserve").hide();

            $("#movementnumberrow").hide();
            if (config.bool("MovementNumberOverride")) {
                $("#movementnumberrow").show();
            }

            if (asm.locale != "en_GB") { $("#giftaidrow").hide(); }

            $("#page1").show();
            $("#page2").hide();
            $("#asm-reserve-accordion").accordion({
                heightStyle: "content"
            });

            // Set default values
            $("#donationtype").val(config.str("AFDefaultDonationType"));
            donationtype_change();
            $("#reservationdate").datepicker("setDate", new Date());
            $("#reservationstatus").select("value", config.str("AFDefaultReservationStatus"));

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
                $("#donationtype2").val($("#donationtype").val());
                $("#amount2").val($("#amount").val());
                if (!config.bool("CreateDonationTrx") || !config.bool("DonationTrxOverride")) {
                    $(".overrideaccount.seconddonation").hide();
                }
            }
            else {
                $(".seconddonation").hide();
            }

            // If we aren't taking payments on this screen, disable both
            if (!config.bool("DonationOnMoveReserve")) { 
                $("#table-payment").closest(".ui-widget").hide();
                $("#amount").val("0");
                $("#amount2").val("0");
            }

            $("#reserve").button().click(function() {
                if (!validation()) { return; }
                $("#reserve").button("disable");
                header.show_loading(_("Creating..."));

                var formdata = $("input, select").toPOST();
                common.ajax_post("move_reserve", formdata, function(data) {

                    $("#movementid").val(data);
                    header.hide_loading();

                    // Copy the animal/owner links to the success page so
                    // the user can go view them quickly again if they want
                    $("#reservefrom").html( $(".animalchooser-display").html() );
                    $("#reserveto").html( $(".personchooser-display .justlink").html() );

                    $("#page1").fadeOut(function() {
                        $("#page2").fadeIn();
                    });
                }, function() {
                    $("#reserve").button("enable");
                });
            });
        },

        name: "move_reserve",
        animation: "newdata",
        title: function() { return _("Reserve an animal"); },
        routes: {
            "move_reserve": function() { common.module_loadandstart("move_reserve", "move_reserve"); }
        }


    };

    common.module_register(move_reserve);

});
