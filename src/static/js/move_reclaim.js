/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const move_reclaim = {

        render: function() {
            return [
                '<div id="asm-content">',
                html.content_header(_("Reclaim an animal"), true),
                html.textbar(_("This animal is currently fostered, it will be automatically returned first."), { id: "fosterinfo", maxwidth: "600px" }),
                html.textbar(_("This animal is currently at a retailer, it will be automatically returned first."), { id: "retailerinfo", maxwidth: "600px" }),
                html.textbar(_("This animal has active reservations, they will be cancelled."), { id: "reserveinfo", maxwidth: "600px" }),
                html.textbar('<span id="awarntext"></span>', { id: "animalwarn", state: "error", icon: "alert", maxwidth: "600px" }),
                html.textbar('<span id="warntext"></span>', { id: "ownerwarn", state: "error", icon: "alert", maxwidth: "600px" }),
                tableform.fields_render([
                    { post_field: "animal", label: _("Animal"), type: "animal" },
                    { post_field: "person", label: _("Owner"), type: "person" },
                    { post_field: "movementnumber", label: _("Movement Number"), type: "text", rowid: "movementnumberrow", 
                        callout: _("A unique number to identify this movement") },
                    { post_field: "movementdate", label: _("Date"), type: "date" },
                    { post_field: "comments", label: _("Comments"), type: "textarea", rows: 3 },
                    { type: "additional", markup: additional.additional_new_fields(controller.additional) }
                ], { full_width: false }),
                html.content_footer(),
                '<div id="payment"></div>',
                html.content_header(_("Boarding Cost"), true),
                html.info("<span id=\"costdata\"></span>", "costdisplay"),
                '<input id="costamount" data="costamount" type="hidden" />',
                '<input id="costtype" data="costtype" type="hidden" />',
                tableform.fields_render([
                    { post_field: "costcreate", label: _("Create a cost record"), type: "check" }
                ], { full_width: false }),
                html.content_footer(),
                tableform.buttons_render([
                   { id: "reclaim", icon: "movement", text: _("Reclaim") }
                ], { render_box: true }),
                '</div>'
            ].join("\n");
        },

        bind: function() {
            const validation = function() {
                // Remove any previous errors
                header.hide_error();
                validate.reset();
                if (!validate.notzero([ "animal", "person" ])) { return false; }
                if (!validate.notblank([ "movementdate" ])) { return false; }
                // mandatory additional fields
                if (!additional.validate_mandatory()) { return false; }
                return true;
            };

            validate.indicator([ "animal", "person", "movementdate" ]);

            // Callback when animal is changed
            $("#animal").animalchooser().bind("animalchooserchange", async function(event, a) {
                
                // Hide things before we start
                $("#costdisplay").closest(".ui-widget").hide();
                $("#fosterinfo").hide();
                $("#reserveinfo").hide();
                $("#retailerinfo").hide();
                $("#animalwarn").hide();
                $("#button-reclaim").button("enable");

                // If the animal is not on the shelter and not fostered or at a retailer, 
                // bail out now because we shouldn't be able to move the animal.
                if (a.ARCHIVED == 1 && a.ACTIVEMOVEMENTTYPE != 2 && a.ACTIVEMOVEMENTTYPE != 8) {
                    $("#button-reclaim").button("disable");
                }

                if (a.ACTIVEMOVEMENTTYPE == "2") {
                    $("#fosterinfo").show();
                }

                if (a.ACTIVEMOVEMENTTYPE == "8") {
                    $("#retailerinfo").show();
                }

                if (a.HASACTIVERESERVE == "1" && config.bool("CancelReservesOnAdoption")) {
                    $("#reserveinfo").show();
                }

                // Grab cost information if option is on
                if (config.bool("CreateBoardingCostOnAdoption")) {
                    let formdata = "mode=cost&id=" + a.ID;
                    let response = await common.ajax_post("move_adopt", formdata);
                    const [costamount, costdata] = response.split("||");
                    $("#costcreate").prop("selected", true);
                    $("#costdata").html(costdata);
                    $("#costamount").val(format.currency_to_int(costamount));
                    $("#costtype").val(config.str("BoardingCostType"));
                    $("#costdisplay").closest(".ui-widget").show();
                }

                let warn = html.animal_movement_warnings(a);
                if (warn.length > 0) {
                    $("#awarntext").html(warn.join("<br>"));
                    $("#animalwarn").show();
                }

            });

            // Callback when person is changed
            $("#person").personchooser().bind("personchooserchange", function(event, p) {

                // Default giftaid if the person is registered
                if (common.has_permission("oaod")) {
                    $("#payment").payments("option", "giftaid", p.ISGIFTAID == 1);
                    $("#giftaid1").prop("checked", p.ISGIFTAID == 1);
                }

                let warn = html.person_movement_warnings(p);
                if (warn.length > 0) {
                    $("#warntext").html(warn.join("<br>"));
                    $("#ownerwarn").show();
                }
            });

            // Payments
            if (common.has_permission("oaod")) {
                $("#payment").payments({ controller: controller });
            }

            $("#costdisplay").closest(".ui-widget").hide();
            $("#notonshelter").hide();
            $("#animalwarn").hide();
            $("#ownerwarn").hide();
            $("#crueltycase").hide();
            $("#quarantine").hide();
            $("#fosterinfo").hide();
            $("#reserveinfo").hide();
            $("#retailerinfo").hide();

            $("#movementnumberrow").hide();
            if (config.bool("MovementNumberOverride")) {
                $("#movementnumberrow").show();
            }

            // Set default values
            $("#movementdate").date("today");

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions", "all");

            $("#button-reclaim").button().click(async function() {
                if (!validation()) { return; }
                $("#button-reclaim").button("disable");
                header.show_loading(_("Creating..."));
                try {
                    let formdata = "mode=create&" + $("input, select, textarea").toPOST();
                    let data = await common.ajax_post("move_reclaim", formdata);
                    let u = "move_gendoc?" +
                        "linktype=MOVEMENT&id=" + data + 
                        "&message=" + encodeURIComponent(common.base64_encode(_("Reclaim successfully created.") + " " + 
                            $(".animalchooser-display").html() + " " + html.icon("right") + " " +
                            $(".personchooser-display .justlink").html() ));
                    common.route(u);
                }
                finally {
                    header.hide_loading();
                    $("#button-reclaim").button("enable");
                }
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
