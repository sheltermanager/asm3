/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, edit_header, html, validate */

$(function() {

    "use strict";

    const move_reserve = {

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="movementid" type="hidden" />',
                html.content_header(_("Reserve an animal"), true),
                html.textbar('<span class="subtext"></span>', { id: "feeinfo", maxwidth: "600px" }),
                html.textbar('<span id="awarntext"></span>', { id: "animalwarn", state: "error", icon: "alert", maxwidth: "600px" }),
                html.textbar('<span id="warntext"></span>', { id: "ownerwarn", state: "error", icon: "alert", maxwidth: "600px" }),
                html.textbar(_("This animal already has an active reservation."), { id: "multiplereserve", state: "error", icon: "alert", maxwidth: "600px" }),
                html.textbar(_("This animal is not on the shelter."), { id: "notonshelter", state: "error", icon: "alert", maxwidth: "600px" }),
                tableform.fields_render([
                    { post_field: "animal", label: _("Animal"), type: "animal" },
                    { post_field: "person", label: _("Reservation For"), type: "person" },
                    { post_field: "movementnumber", label: _("Movement Number"), type: "text", rowid: "movementnumberrow", 
                        callout: _("A unique number to identify this movement") },
                    { post_field: "reservationdate", label: _("Date"), type: "date" },
                    { post_field: "reservationstatus", label: _("Status"), type: "select", 
                        options: { displayfield: "STATUSNAME", valuefield: "ID", rows: controller.reservationstatuses }},
                    { post_field: "comments", label: _("Comments"), type: "textarea", rows: 3 }
                ], 1, { full_width: false }),
                '<table class="asm-table-layout">',
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
                if (!validate.notzero([ "animal", "person" ])) { return false; }
                if (!validate.notblank([ "reservationdate" ])) { return false; }
                // mandatory additional fields
                if (!additional.validate_mandatory()) { return false; }                
                return true;
            };

            validate.indicator([ "animal", "person", "reservationdate" ]);

            // Callback when animal is changed
            $("#animal").animalchooser().bind("animalchooserchange", function(event, a) {
              
                // Hide things before we start
                $("#notonshelter").fadeOut();
                $("#animalwarn").fadeOut();
                $("#feeinfo").fadeOut();
                $("#reserve").button("enable");

                // If the animal is not on the shelter and not fostered or at a retailer, show that warning
                // and prevent the reserve
                if (a.ARCHIVED == 1 && a.ACTIVEMOVEMENTTYPE != 2 && a.ACTIVEMOVEMENTTYPE != 8) {
                    $("#reserve").button("disable");
                }

                // If we have an adoption fee, show it in the info bar
                if (!config.bool("DontShowAdoptionFee") && a.FEE) {
                    // $("#amount").currency("value", a.FEE); #122 disabled due to less relevant for reserves
                    $("#feeinfo .subtext").html( _("This animal has an adoption fee of {0}").replace("{0}", format.currency(a.FEE)));
                    $("#feeinfo").fadeIn();
                }

                let warn = html.animal_movement_warnings(a, true);
                if (warn.length > 0) {
                    $("#awarntext").html(warn.join("<br>"));
                    $("#animalwarn").fadeIn();
                }

            });

            // Callback when person is changed
            $("#person").personchooser().bind("personchooserchange", async function(event, rec) {
                let response = await edit_header.person_with_adoption_warnings(rec.ID);
                let p = jQuery.parseJSON(response)[0];

                $("#ownerwarn").fadeOut();
         
                // Default giftaid if the person is registered
                if (common.has_permission("oaod")) {
                    $("#payment").payments("option", "giftaid", p.ISGIFTAID == 1);
                    $("#giftaid1").prop("checked", p.ISGIFTAID == 1);
                }

                let oopostcode = $(".animalchooser-oopostcode").val();
                let bipostcode = $(".animalchooser-bipostcode").val(); 
                let warn = html.person_movement_warnings(p, oopostcode, bipostcode);
                if (warn.length > 0) {
                    $("#warntext").html(warn.join("<br>"));
                    $("#ownerwarn").fadeIn();
                }
            });

            // Payments
            if (common.has_permission("oaod")) {
                $("#payment").payments({ controller: controller });
            }

            $("#animalwarn").hide();
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
