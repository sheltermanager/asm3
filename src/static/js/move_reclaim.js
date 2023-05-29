/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const move_reclaim = {

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="movementid" type="hidden" />',
                html.content_header(_("Reclaim an animal"), true),
                '<div id="fosterinfo" class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered">',
                '<span class="ui-icon ui-icon-info"></span>',
                _("This animal is currently fostered, it will be automatically returned first."),
                '</p>',
                '</div>',
                '<div id="retailerinfo" class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered">',
                '<span class="ui-icon ui-icon-info"></span>',
                _("This animal is currently at a retailer, it will be automatically returned first."),
                '</p>',
                '</div>',
                '<div id="reserveinfo" class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered">',
                '<span class="ui-icon ui-icon-info"></span>',
                _("This animal has active reservations, they will be cancelled."),
                '</p>',
                '</div>',
                '<div id="notonshelter" class="ui-state-error ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered"><span class="ui-icon ui-icon-alert"></span>',
                '<span class="centered">' + _("This animal is not on the shelter.") + '</span>',
                '</p>',
                '</div>',
                '<div id="crueltycase" class="ui-state-error ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered"><span class="ui-icon ui-icon-alert"></span>',
                '<span class="centered">' + _("This animal is part of a cruelty case and should not leave the shelter.") + '</span>',
                '</p>',
                '</div>',
                '<div id="quarantine" class="ui-state-error ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered"><span class="ui-icon ui-icon-alert"></span>',
                '<span class="centered">' + _("This animal is currently quarantined and should not leave the shelter.") + '</span>',
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
                if (common.trim($("#movementdate").val()) == "") {
                    header.show_error(_("This type of movement requires a date."));
                    validate.highlight("movementdate");
                    return false;
                }
                // mandatory additional fields
                if (!additional.validate_mandatory()) { return false; }
                return true;
            };

            validate.indicator([ "animal", "person", "movementdate" ]);

            // Callback when animal is changed
            $("#animal").animalchooser().bind("animalchooserchange", function(event, rec) {
                
                // Hide things before we start
                $("#costdisplay").closest(".ui-widget").fadeOut();
                $("#fosterinfo").fadeOut();
                $("#reserveinfo").fadeOut();
                $("#retailerinfo").fadeOut();
                $("#notonshelter").fadeOut();
                $("#crueltycase").fadeOut();
                $("#quarantine").fadeOut();
                $("#reclaim").button("enable");

                // If the animal is not on the shelter and not fostered or at a retailer, 
                // bail out now because we shouldn't be able to move the animal.
                if (rec.ARCHIVED == 1 && rec.ACTIVEMOVEMENTTYPE != 2 && rec.ACTIVEMOVEMENTTYPE != 8) {
                    $("#notonshelter").fadeIn();
                    $("#reclaim").button("disable");
                    return;
                }

                // If the animal is a cruelty case, we should not allow reclaim
                if (rec.CRUELTYCASE == 1) {
                    $("#crueltycase").fadeIn();
                    $("#reclaim").button("disable");
                }

                // If the animal is quarantined, we shouldn't allow reclaim either
                if (rec.ISQUARANTINE == 1) {
                    $("#quarantine").fadeIn();
                    $("#reclaim").button("disable");
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
                    let formdata = "mode=cost&id=" + rec.ID;
                    common.ajax_post("move_reclaim", formdata)
                        .then(function(data) {
                            let [costamount, costdata] = data.split("||");
                            $("#costamount").val(format.currency_to_int(costamount));
                            $("#costdata").html(costdata);
                            $("#costtype").val(config.str("BoardingCostType"));
                            $("#costdisplay").closest(".ui-widget").fadeIn();
                        });
                }

            });

            // Callback when person is changed
            $("#person").personchooser().bind("personchooserchange", function(event, rec) {

                // Default giftaid if the person is registered
                if (common.has_permission("oaod")) {
                    $("#payment").payments("option", "giftaid", rec.ISGIFTAID == 1);
                    $("#giftaid1").prop("checked", rec.ISGIFTAID == 1);
                }

            });

            // Payments
            if (common.has_permission("oaod")) {
                $("#payment").payments({ controller: controller });
            }

            $("#costdisplay").closest(".ui-widget").hide();
            $("#notonshelter").hide();
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
            $("#movementdate").datepicker("setDate", new Date());

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
