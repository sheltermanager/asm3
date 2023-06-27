/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, edit_header, html, validate */

$(function() {

    "use strict";

    const move_reserve = {

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="movementid" type="hidden" />',
                html.content_header(_("Reserve an animal"), true),
                '<div id="feeinfo" class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered">',
                '<span class="ui-icon ui-icon-info"></span>',
                '<span class="subtext"></span>',
                '</p>',
                '</div>',
                '<div id="ownerwarn" class="ui-state-error ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered"><span class="ui-icon ui-icon-alert"></span>',
                '<span id="warntext" class="centered"></span>',
                '</p>',
                '</div>',
                '<div id="multiplereserve" class="ui-state-error ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered"><span class="ui-icon ui-icon-alert"></span>',
                '<span class="centered">' + _("This animal already has an active reservation.") + '</span>',
                '</p>',
                '</div>',
                '<div id="notonshelter" class="ui-state-error ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered"><span class="ui-icon ui-icon-alert"></span>',
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
                '<tr id="commentsrow">',
                '<td><label for="comments">' + _("Comments") + '</label></td>',
                '<td>',
                '<textarea class="asm-textarea" id="comments" data="comments" rows="3"></textarea>',
                '</td>',
                '</tr>',
                additional.additional_new_fields(controller.additional),
                '</table>',
                html.content_footer(),
                '<div id="payment"></div>',
                html.box(5),
                '<button id="reserve">' + html.icon("movement") + ' ' + _("Reserve") + '</button>',
                '</div>',
                '</div>'
            ].join("\n");
        },

        bind: function() {
            const validation = function() {
                // Remove any previous errors
                header.hide_error();
                validate.reset();
                // animal
                if ($("#animal").val() == "") {
                    header.show_error(_("Movements require an animal"));
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
                if (common.trim($("#reservationdate").val()) == "") {
                    header.show_error(_("This type of movement requires a date."));
                    validate.highlight("reservationdate");
                    return false;
                }
                // mandatory additional fields
                if (!additional.validate_mandatory()) { return false; }                

                return true;
            };

            validate.indicator([ "animal", "person", "reservationdate" ]);

            // Callback when animal is changed
            $("#animal").animalchooser().bind("animalchooserchange", function(event, rec) {
              
                // Hide things before we start
                $("#notonshelter").fadeOut();
                $("#feeinfo").fadeOut();
                $("#reserve").button("enable");

                // If the animal is not on the shelter and not fostered or at a retailer, show that warning
                // and stop everything else
                if (rec.ARCHIVED == 1 && rec.ACTIVEMOVEMENTTYPE != 2 && rec.ACTIVEMOVEMENTTYPE != 8) {
                    $("#notonshelter").fadeIn();
                    $("#reserve").button("disable");
                    return;
                }

                // If the animal has an active reserve, show the warning, but
                // things can still continue
                if (rec.HASACTIVERESERVE == 1) {
                    $("#multiplereserve").fadeIn();
                }

                // If we have an adoption fee, show it in the info bar
                if (!config.bool("DontShowAdoptionFee") && rec.FEE) {
                    // $("#amount").currency("value", rec.FEE); #122 disabled due to less relevant for reserves
                    $("#feeinfo .subtext").html( _("This animal has an adoption fee of {0}").replace("{0}", format.currency(rec.FEE)));
                    $("#feeinfo").fadeIn();
                }

            });

            // Callback when person is changed
            $("#person").personchooser().bind("personchooserchange", function(event, rec) {

                edit_header.person_with_adoption_warnings(rec.ID).then(function(data) {
                    rec = jQuery.parseJSON(data)[0];
         
                    // Default giftaid if the person is registered
                    if (common.has_permission("oaod")) {
                        $("#payment").payments("option", "giftaid", rec.ISGIFTAID == 1);
                        $("#giftaid1").prop("checked", rec.ISGIFTAID == 1);
                    }

                    // Owner banned?
                    if (rec.ISBANNED == 1 && config.bool("WarnBannedOwner")) {
                        $("#warntext").text(_("This person has been banned from adopting animals."));
                        $("#ownerwarn").fadeIn();
                        return;
                    }

                    // Owner previously under investigation
                    if (rec.INVESTIGATION > 0) {
                        $("#warntext").html(_("This person has been under investigation."));
                        $("#ownerwarn").fadeIn();
                        return;
                    }

                    // Owner part of animal control incident
                    if (rec.INCIDENT > 0) {
                        $("#warntext").html(_("This person has an animal control incident against them."));
                        $("#ownerwarn").fadeIn();
                        return;
                    }

                    // Owner not homechecked?
                    if (rec.IDCHECK == 0 && config.bool("WarnNoHomeCheck")) {
                        $("#warntext").text(_("This person has not passed a homecheck."));
                        $("#ownerwarn").fadeIn();
                        return;
                    }

                    $("#ownerwarn").fadeOut();

                });

            });

            // Payments
            if (common.has_permission("oaod")) {
                $("#payment").payments({ controller: controller });
            }

            $("#ownerwarn").hide();
            $("#notonshelter").hide();
            $("#feeinfo").hide();
            $("#multiplereserve").hide();

            $("#movementnumberrow").hide();
            if (config.bool("MovementNumberOverride")) {
                $("#movementnumberrow").show();
            }

            // Set default values
            $("#reservationdate").date("today");
            $("#reservationstatus").select("value", config.str("AFDefaultReservationStatus"));

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions", "all");

            // If we aren't taking payments on this screen, disable both
            if (!config.bool("DonationOnMoveReserve")) { 
                $("#payment").hide();
                $("#amount1").val("0");
            }

            $("#reserve").button().click(async function() {
                if (!validation()) { return; }
                $("#reserve").button("disable");
                header.show_loading(_("Creating..."));
                try {
                    let formdata = "mode=create&" + $("input, select, textarea").toPOST();
                    let data = await common.ajax_post("move_reserve", formdata);
                    $("#movementid").val(data);
                    let u = "move_gendoc?" +
                        "linktype=MOVEMENT&id=" + data + 
                        "&message=" + encodeURIComponent(common.base64_encode(_("Reservation successfully created.") + " " + 
                            $(".animalchooser-display").html() + " " + html.icon("right") + " " +
                            $(".personchooser-display .justlink").html() ));
                    common.route(u);
                }
                finally { 
                    header.hide_loading();
                    $("#reserve").button("enable");
                }
            });
        },

        destroy: function() {
            common.widget_destroy("#animal");
            common.widget_destroy("#person");
        },

        name: "move_reserve",
        animation: "newdata",
        autofocus: "#asm-content button:first",
        title: function() { return _("Reserve an animal"); },
        routes: {
            "move_reserve": function() { common.module_loadandstart("move_reserve", "move_reserve"); }
        }


    };

    common.module_register(move_reserve);

});
