/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var move_reclaim = {

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="movementid" type="hidden" />',
                html.content_header(_("Reclaim an animal"), true),
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
                '<input id="animal" data="animal" class="asm-animalchooser" type="hidden" value="" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="person">' + _("Owner") + '</label>',
                '</td>',
                '<td>',
                '<input id="person" data="person" class="asm-personchooser" type="hidden" value="" />',
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
                '<input id="movementdate" data="movementdate" class="asm-textbox asm-datebox" title="' + _("The date the animal was reclaimed") + '" />',
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
                '<button id="reclaim">' + html.icon("movement") + ' ' + _("Reclaim") + '</button>',
                '</div>',
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
                $("#costdisplay").closest(".ui-widget").fadeOut();
                $("#fosterinfo").fadeOut();
                $("#reserveinfo").fadeOut();
                $("#retailerinfo").fadeOut();
                $("#notonshelter").fadeOut();
                $("#reclaim").button("enable");

                // If the animal is not on the shelter and not fostered or at a retailer, 
                // bail out now because we shouldn't be able to move the animal.
                if (rec.ARCHIVED == 1 && rec.ACTIVEMOVEMENTTYPE != 2 && rec.ACTIVEMOVEMENTTYPE != 8) {
                    $("#notonshelter").fadeIn();
                    $("#reclaim").button("disable");
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

                // Grab cost information if option is on
                if (config.bool("CreateBoardingCostOnAdoption")) {
                    var formdata = "mode=cost&id=" + rec.ID;
                    common.ajax_post("move_reclaim", formdata)
                        .then(function(data) {
                            var bits = data.split("||");
                            $("#costdata").html(bits[1]);
                            $("#costamount").val(bits[0]);
                            $("#costtype").val(config.str("BoardingCostType"));
                            $("#costdisplay").closest(".ui-widget").fadeIn();
                        });
                }

                // Update the list of document templates
                var formdatat = "mode=templates&id=" + rec.ID;
                common.ajax_post("move_reclaim", formdatat)
                    .then(function(data) { 
                        $("#templatelist").html(data); 
                    });

            });

            // Callback when person is changed
            var current_person = null;
            $("#person").personchooser().bind("personchooserchange", function(event, rec) {
                current_person = rec;

                // Set the gift aid box if they are registered
                $("#giftaid").select("value", rec.ISGIFTAID);

            });

            // What to do when donation type is changed
            var donationtype_change = function() {
                var dc = common.get_field(controller.donationtypes, $("#donationtype").select("value"), "DEFAULTCOST");
                $("#amount").currency("value", dc);
            };
            $("#donationtype").change(function() {
                donationtype_change();
            });

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

            $("#costdisplay").closest(".ui-widget").hide();
            $("#notonshelter").hide();
            $("#fosterinfo").hide();
            $("#reserveinfo").hide();
            $("#retailerinfo").hide();

            $("#movementnumberrow").hide();
            if (config.bool("MovementNumberOverride")) {
                $("#movementnumberrow").show();
            }

            if (asm.locale != "en_GB") { $("#giftaidrow").hide(); }

            // Set default values
            $("#donationtype").val(config.str("AFDefaultDonationType"));
            donationtype_change();
            $("#movementdate").datepicker("setDate", new Date());

            $("#reclaim").button().click(function() {
                if (!validation()) { return; }
                $("#reclaim").button("disable");
                header.show_loading(_("Creating..."));

                var formdata = $("input, select").toPOST();
                common.ajax_post("move_reclaim", formdata)
                    .then(function(data) {

                        $("#movementid").val(data);

                        var u = "move_gendoc?" +
                            "mode=ANIMAL&id=" + $("#animal").val() +
                            "&message=" + encodeURIComponent(common.base64_encode(_("Reclaim successfully created.") + " " + 
                                $(".animalchooser-display").html() + " " + html.icon("right") + " " +
                                $(".personchooser-display .justlink").html() ));
                        common.route(u);

                    })
                    .always(function() {
                        header.hide_loading();
                        $("#reclaim").button("enable");
                    });
            });
        },

        destroy: function() {
            common.widget_destroy("#animal");
            common.widget_destroy("#person");
        },

        name: "move_reclaim",
        animation: "newdata",
        autofocus: "#asm-content button:first",
        title: function() { return _("Reclaim an animal"); },
        routes: {
            "move_reclaim": function() { common.module_loadandstart("move_reclaim", "move_reclaim"); }
        }


    };

    common.module_register(move_reclaim);

});
