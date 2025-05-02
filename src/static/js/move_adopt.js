/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, edit_header, html, validate */

$(function() {

    "use strict";

    const move_adopt = {

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="movementid" type="hidden" />',
                html.content_header(_("Adopt an animal"), true),
                html.warn('<span id="bonddata"></span>', "bonddisplay"),
                html.info(_("This animal is currently fostered, it will be automatically returned first."), "fosterinfo"),
                html.info(_("This animal is currently at a retailer, it will be automatically returned first."), "retailerinfo"),
                html.info(_("This animal has active reservations, they will be cancelled."), "reserveinfo"),
                html.info('<span class="subtext"></span>', "feeinfo"),
                html.info('<span id="awarntext"></span>', "animalwarn"),
                html.info('<span id="warntext"></span>', "ownerwarn"),
                tableform.fields_render([
                    { post_field: "animal", label: _("Animal"), type: "animal" },
                    { post_field: "person", label: _("New Owner"), type: "person" },
                    { post_field: "homechecked", label: _("Mark this owner homechecked"), type: "check", rowid: "homecheckrow" },
                    { post_field: "movementnumber", label: _("Movement Number"), type: "text", callout: _("A unique number to identify this movement"), rowid: "movementnumberrow" },
                    { post_field: "movementdate", label: _("Date"), type: "date" },
                    { post_field: "eventlink", label: _("Link to event"), type: "check", hideif: function(){return !common.has_permission("lem") || config.bool("DisableEvents");}},
                    { post_field: "event", label: _(""), type: "select"},
                    { post_field: "trial", label: _("Trial adoption"), type: "check", rowid: "trialrow1" },
                    { post_field: "trialenddate", label: _("Trial ends on"), type: "date", rowid: "trialrow2" },
                    { post_field: "insurance", label: _("Insurance"), type: "text", rowid: "insurancerow", xbutton: _("Issue a new insurance number for this animal/adoption") },
                    { post_field: "comments", label: _("Comments"), type: "textarea", rows: 3, rowid: "commentsrow" },
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
                html.content_header(_("Signed Adoption Paperwork"), true),
                tableform.fields_render([
                    { post_field: "sigpaperwork", label: _("Request signed paperwork from the adopter by email"), type: "check" },
                    { post_field: "sigtemplateid", label: _("Adoption paperwork template"), type: "select",
                        options: edit_header.template_list_options(controller.templates) },
                    { post_field: "sigemailaddress", label: _("Adopter email address"), type: "text" },
                    { post_field: "sigemailtemplateid", label: _("Email template"), type: "select", 
                        options: edit_header.template_list_options(controller.templatesemail) },
                ], { full_width: false }),
                html.content_footer(),
                html.content_header(_("Adoption Checkout"), true),
                tableform.fields_render([
                    { post_field: "checkoutcreate", label: _("Send the checkout email to the adopter"), type: "check" },
                    { post_field: "templateid", label: _("Adoption paperwork template"), type: "select",
                        options: edit_header.template_list_options(controller.templates) },
                    { post_field: "feetypeid", label: _("Adoption fee payment type"), type: "select",
                        options: { displayfield: "DONATIONNAME", valuefield: "ID", rows: controller.donationtypes } },
                    { post_field: "emailaddress", label: _("Adopter email address"), type: "text" },
                    { post_field: "emailtemplateid", label: _("Email template"), type: "select", 
                        options: edit_header.template_list_options(controller.templatesemail) },
                ], { full_width: false }),
                html.content_footer(),
                tableform.buttons_render([
                   { id: "adopt", icon: "movement", text: _("Adopt") }
                ], { render_box: true }),
                '</div>'
            ].join("\n");
        },

        bind: function() {
            
            const validation = function() {
                // Remove any previous errors
                header.hide_error();
                validate.reset();
                // animal
                if (!validate.notzero([ "animal" ])) {
                    header.show_error(_("Movements require an animal."));
                    return false;
                }
                // person
                if (!validate.notzero([ "person" ])) {
                    header.show_error(_("This type of movement requires a person."));
                    return false;
                }
                // date
                if (common.trim($("#movementdate").val()) == "") {
                    header.show_error(_("This type of movement requires a date."));
                    validate.highlight("movementdate");
                    return false;
                }
                // checkout email
                if ($("#checkoutcreate").prop("checked") && $("#emailaddress").val() == "") {
                    validate.highlight("emailaddress");
                    return false;
                }
                // checkout template
                if ($("#checkoutcreate").prop("checked") && $("#templateid").select("value") == "") {
                    validate.highlight("templateid");
                    return false;
                }
                // checkout email template
                if ($("#checkoutcreate").prop("checked") && $("#emailtemplateid").select("value") == "") {
                    validate.highlight("emailtemplateid");
                    return false;
                }
                // signed email
                if ($("#sigpaperwork").prop("checked") && $("#sigemailaddress").val() == "") {
                    validate.highlight("sigemailaddress");
                    return false;
                }
                // signed contract template
                if ($("#sigpaperwork").prop("checked") && $("#sigtemplateid").select("value") == "") {
                    validate.highlight("sigtemplateid");
                    return false;
                }
                // signed contract email template
                if ($("#sigpaperwork").prop("checked") && $("#sigemailtemplateid").select("value") == "") {
                    validate.highlight("sigemailtemplateid");
                    return false;
                }

                // mandatory additional fields
                if (!additional.validate_mandatory()) { return false; }                

                return true;
            };

            validate.indicator([ "animal", "person", "movementdate" ]);

            let lastanimal, lastperson;

            // Callback when animal is changed
            $("#animal").animalchooser().bind("animalchooserchange", async function(event, a) {
                lastanimal = a;
                // Hide things before we start
                $("#bonddisplay").fadeOut();
                $("#costdisplay").closest(".ui-widget").fadeOut();
                $("#fosterinfo").fadeOut();
                $("#reserveinfo").fadeOut();
                $("#retailerinfo").fadeOut();
                $("#feeinfo").fadeOut();
                $("#animalwarn").fadeOut();
                $("#button-adopt").button("enable");

                // Disable the adoption button if the animal cannot be adopted because it isn't
                // on the shelter or is held, a cruelty case or quarantined
                if ((a.ARCHIVED == 1 && a.ACTIVEMOVEMENTTYPE != 2 && a.ACTIVEMOVEMENTTYPE != 8) ||
                    a.ISHOLD == 1 || a.CRUELTYCASE == 1 || a.ISQUARANTINE == 1) {
                    $("#button-adopt").button("disable");
                }

                if (a.ACTIVEMOVEMENTTYPE == 2) {
                    $("#fosterinfo").fadeIn();
                }

                if (a.ACTIVEMOVEMENTTYPE == 8) {
                    $("#retailerinfo").fadeIn();
                }

                if (a.HASACTIVERESERVE == 1 && config.bool("CancelReservesOnAdoption")) {
                    $("#reserveinfo").fadeIn();
                }

                // Show bonded animal info
                if (a.BONDEDANIMALID || a.BONDEDANIMAL2ID) {
                    let bw = "";
                    if (a.BONDEDANIMAL1ARCHIVED == 0 && a.BONDEDANIMAL1NAME) {
                        bw += a.BONDEDANIMAL1CODE + " - " + a.BONDEDANIMAL1NAME;
                    }
                    if (a.BONDEDANIMAL2ARCHIVED == 0 && a.BONDEDANIMAL2NAME) {
                        if (bw != "") { bw += ", "; }
                        bw += a.BONDEDANIMAL2CODE + " - " + a.BONDEDANIMAL2NAME;
                    }
                    if (bw != "") {
                        $("#bonddata").html(_("This animal is bonded with {0}. Adoption movement records will be created for all bonded animals.").replace("{0}", bw));
                        $("#bonddisplay").fadeIn();
                    }
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
                    $("#costdisplay").closest(".ui-widget").fadeIn();
                }

                // If we have adoption fee fields, override the first donation
                // with the fee from the animal assuming it's nonzero
                if (!config.bool("DontShowAdoptionFee") && a.FEE) {
                    $("#amount1").currency("value", a.FEE);
                    if ($("#vat1").is(":checked")) { 
                        // Recalculate the tax
                        $("#vat1").change();
                    }
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
                lastperson = p;

                $("#ownerwarn").fadeOut();
                $("#checkoutcreate").closest(".ui-widget").fadeOut();
                $("#sigpaperwork").closest(".ui-widget").fadeOut();

                // Show the checkout section if it's configured and there's an animal with 
                // a non-zero adoption fee
                if (config.str("AdoptionCheckoutProcessor") != "" && lastanimal && lastanimal.FEE > 0) {
                    $("#emailaddress").val(p.EMAILADDRESS);
                    $("#templateid").select("value", config.str("AdoptionCheckoutTemplateID"));
                    $("#feetypeid").select("value", config.str("AdoptionCheckoutFeeID"));
                    $("#checkoutcreate").closest(".ui-widget").show();
                }
                // If it isnt, show the request signed contract section if that is configured
                else if (config.bool("MoveAdoptGeneratePaperwork")) {
                    $("#sigemailaddress").val(p.EMAILADDRESS);
                    $("#sigtemplateid").select("value", config.str("AdoptionCheckoutTemplateID"));
                    $("#sigpaperwork").closest(".ui-widget").show();
                }

                // Show tickbox if owner not homechecked
                if (p.IDCHECK == 0) {
                    $("#markhomechecked").attr("checked", false);
                    $("#homecheckrow").fadeIn();
                }

                // Default giftaid if the person is registered
                if (common.has_permission("oaod")) {
                    $("#payment").payments("option", "giftaid", p.ISGIFTAID == 1);
                    $("#giftaid1").prop("checked", p.ISGIFTAID == 1);
                }

                let oopostcode = $(".animalchooser-oopostcode").val();
                let bipostcode = $(".animalchooser-bipostcode").val(); 
                let warn = html.person_movement_warnings(p, oopostcode, bipostcode);

                // Check whether the animal has reservations. 
                // If it does, show a warning if this person does not have one on the animal.
                if (config.bool("WarnNoReserve") && lastanimal && lastanimal.HASACTIVERESERVE == 1) {
                    if (!common.array_in(String(lastanimal.ID), p.RESERVEDANIMALIDS.split(","))) {
                        warn.push(_("This person does not have a reservation on this animal."));
                    }
                }

                if (warn.length > 0) {
                    $("#warntext").html(warn.join("<br>"));
                    $("#ownerwarn").fadeIn();
                }

            });

            $("#costdisplay").closest(".ui-widget").hide();
            $("#checkoutcreate").closest(".ui-widget").hide();
            $("#sigpaperwork").closest(".ui-widget").hide();
            $("#bonddisplay").hide();
            $("#animalwarn").hide();
            $("#ownerwarn").hide();
            $("#notonshelter").hide();
            $("#onhold").hide();
            $("#notavailable").hide();
            $("#crueltycase").hide();
            $("#quarantine").hide();
            $("#unaltered").hide();
            $("#notmicrochipped").hide();
            $("#outstandingmedical").hide();
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

            // Payments
            if (common.has_permission("oaod")) {
                $("#payment").payments({ controller: controller });
            }

            // If checkout is turned on, hide the payments section
            $("#checkoutcreate").change(function() {
                $("#payment").toggle(!$("#checkoutcreate").prop("checked"));
            });

            // Insurance related stuff
            $("#button-insurance")
                .button({ icons: { primary: "ui-icon-cart" }, text: false })
                .click(async function() {
                $("#button-insurance").button("disable");
                let response = await common.ajax_post("move_adopt", "mode=insurance");
                $("#insurance").val(response);
                $("#button-insurance").button("enable");
            });
            if (!config.bool("UseAutoInsurance")) { $("#button-insurance").button("disable"); }

            // Events related stuff
            if ($("#eventlink").is(":checked")) {
                $("#event").closest("tr").fadeIn();
            }
            else {
                $("#event").closest("tr").fadeOut();
            }
            $("#eventlink, #movementdate").change(function() {
                if (config.bool("DisableEvents")) { return; }
                // event link needs a movement date
                if ($("#eventlink").prop("checked") && !$("#movementdate").val()) {
                    validate.notblank([ "movementdate" ]);
                    header.show_error(_("Complete adoption date before linking to event."));
                    $("#eventlink").prop("checked", false);
                }
                $("#event").empty();
                if ($("#eventlink").prop("checked")) {
                    $("#event").closest("tr").fadeIn();
                    move_adopt.populate_event_dates();
                }
                else {
                    $("#event").closest("tr").fadeOut();
                }
            });

            $("#page1").show();
            $("#page2").hide();
            $("#asm-adopt-accordion").accordion({
                heightStyle: "content"
            });

            // Set default values
            $("#movementdate").date("today");

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions", "all");

            // Show trial fields if option is set
            if (config.bool("TrialAdoptions")) {
                $("#trialrow1").show();
                $("#trialrow2").show();
            }

            const trial_change = function() {
                if ($("#trial").prop("checked")) {
                    // If there's no trial end date, and we have a default trial length, set the date
                    if (!$("#trialenddate").val() && config.integer("DefaultTrialLength")) {
                        let enddate = common.add_days(new Date(), config.integer("DefaultTrialLength"));
                        $("#trialenddate").date("setDate", enddate);
                    }
                }
            };
            $("#trial").click(trial_change).keyup(trial_change);

            $("#button-adopt").button().click(async function() {
                if (!validation()) { return; }
                $("#button-adopt").button("disable");
                header.show_loading(_("Creating..."));
                try {
                    let formdata = "mode=create&" + $("input, select, textarea").toPOST();
                    let response = await common.ajax_post("move_adopt", formdata);
                    $("#movementid").val(response);
                    header.hide_loading();
                    let u = "move_gendoc";
                    // If the option to allow editing payments after creating the adoption is set, take
                    // the user to a payment screen that allows them to see the movement payments in order
                    // to take payment, request payment by email, generate an invoice/receipt, etc.
                    if (config.bool("MoveAdoptDonationsEnabled") && !$("#checkoutcreate").prop("checked")) {
                        u = "move_donations";
                    }
                    u += "?" +
                        "linktype=MOVEMENT&id=" + response +
                        "&message=" + encodeURIComponent(common.base64_encode(_("Adoption successfully created.") + " " + 
                            $(".animalchooser-display").html() + " " + html.icon("right") + " " +
                            $(".personchooser-display .justlink").html() )) + 
                            "&animalid=" + $("#animal").val() + 
                            "&ownerid=" + $("#person").val();
                    common.route(u);
                }
                catch(err) {
                    log.error(err, err);
                    $("#button-adopt").button("enable");
                }
            });
        },

        /** Populates the event dropdown with dates within certain range
            (event start <= movement date <= event end)  */
        populate_event_dates: async function() {
            if (config.bool("DisableEvents")) { return; }
            let result = await common.ajax_post("movement", "mode=eventlink&movementdate=" + $("#movementdate").val());
            let dates = jQuery.parseJSON(result);
            let dates_range = "";
            let loc = [];
            $.each(dates, function(i, v){
                if(format.date(v.STARTDATETIME) == format.date(v.ENDDATETIME)) {
                    dates_range = format.date(v.STARTDATETIME);
                }
                else {
                    dates_range = format.date(v.STARTDATETIME) + " - " + format.date(v.ENDDATETIME);
                }
                loc = [v.EVENTADDRESS, v.EVENTTOWN, v.EVENTCOUNTY, v.EVENTCOUNTRY].filter(Boolean).join(", ");
                $("#event").append("<option value='" + v.ID + "'>" + dates_range + " " + v.EVENTNAME + " " + loc + "</option>");
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
