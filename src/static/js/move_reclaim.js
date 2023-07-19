/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const move_reclaim = {

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="movementid" type="hidden" />',
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
                    { post_field: "comments", label: _("Comments"), type: "textarea", rows: 3 }
                ], 1, { full_width: false }),
                '<table class="asm-table-layout">',
                additional.additional_new_fields(controller.additional),
                '</table>',
                html.content_footer(),
                '<div id="payment"></div>',
                html.content_header(_("Boarding Cost"), true),
                '<div id="costdisplay" class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered"><span class="ui-icon ui-icon-info"></span>',
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
            $("#animal").animalchooser().bind("animalchooserchange", function(event, a) {
                
                // Hide things before we start
                $("#costdisplay").closest(".ui-widget").fadeOut();
                $("#fosterinfo").fadeOut();
                $("#reserveinfo").fadeOut();
                $("#retailerinfo").fadeOut();
                $("#animalwarn").fadeOut();
                $("#reclaim").button("enable");

                // If the animal is not on the shelter and not fostered or at a retailer, 
                // bail out now because we shouldn't be able to move the animal.
                if (a.ARCHIVED == 1 && a.ACTIVEMOVEMENTTYPE != 2 && a.ACTIVEMOVEMENTTYPE != 8) {
                    $("#reclaim").button("disable");
                }

                if (a.ACTIVEMOVEMENTTYPE == "2") {
                    $("#fosterinfo").fadeIn();
                }

                if (a.ACTIVEMOVEMENTTYPE == "8") {
                    $("#retailerinfo").fadeIn();
                }

                if (a.HASACTIVERESERVE == "1" && config.bool("CancelReservesOnAdoption")) {
                    $("#reserveinfo").fadeIn();
                }

                // Grab cost information if option is on
                if (config.bool("CreateBoardingCostOnAdoption")) {
                    let formdata = "mode=cost&id=" + a.ID;
                    common.ajax_post("move_reclaim", formdata)
                        .then(function(data) {
                            let [costamount, costdata] = data.split("||");
                            $("#costamount").val(format.currency_to_int(costamount));
                            $("#costdata").html(costdata);
                            $("#costtype").val(config.str("BoardingCostType"));
                            $("#costdisplay").closest(".ui-widget").fadeIn();
                        });
                }

                let warn = html.animal_movement_warnings(a);
                if (warn.length > 0) {
                    $("#awarntext").html(warn.join("<br>"));
                    $("#animalwarn").fadeIn();
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
                    $("#ownerwarn").fadeIn();
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

            $("#reclaim").button().click(async function() {
                if (!validation()) { return; }
                $("#reclaim").button("disable");
                header.show_loading(_("Creating..."));
                try {
                    let formdata = "mode=create&" + $("input, select, textarea").toPOST();
                    let data = await common.ajax_post("move_reclaim", formdata);
                    $("#movementid").val(data);
                    let u = "move_gendoc?" +
                        "linktype=MOVEMENT&id=" + data + 
                        "&message=" + encodeURIComponent(common.base64_encode(_("Reclaim successfully created.") + " " + 
                            $(".animalchooser-display").html() + " " + html.icon("right") + " " +
                            $(".personchooser-display .justlink").html() ));
                    common.route(u);
                }
                finally {
                    header.hide_loading();
                    $("#reclaim").button("enable");
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
