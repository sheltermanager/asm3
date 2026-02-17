/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, edit_header, html, validate */

$(function() {

    "use strict";

    const move_workflow = {

        render: function() {
            let personfilter = "all";
            if (controller.mode == "foster") {
                personfilter = "fosterer";
            } else if (controller.mode == "transfer") {
                personfilter = "shelter";
            } else if (controller.mode == "retail") {
                personfilter = "retailer";
            }
            return [
                '<div id="asm-content">',
                '<div id="dialog-adopt-confirm" style="display: none" title="' + html.title(_("Confirm")) + '">',
                '<p><span class="ui-icon ui-icon-alert"></span> ' + _("This will create {0} records. Are you sure that you would like to continue?").replace('{0}', '<span id="numofmovements">0</span>') + '</p>',
                '</div>',
                '<input id="movementid" type="hidden" />',
                html.content_header(_("Adopt animal(s)"), true),
                html.warn('<span id="bonddata"></span>', "bonddisplay"),
                html.info(_("This animal is currently fostered, it will be automatically returned first."), "fosterinfo"),
                html.info(_("This animal is currently at a retailer, it will be automatically returned first."), "retailerinfo"),
                html.info(_("This animal has active reservations, they will be cancelled."), "reserveinfo"),
                html.info('<span class="subtext"></span>', "feeinfo"),
                html.info('<span id="awarntext"></span>', "animalwarn"),
                html.info('<span id="warntext"></span>', "ownerwarn"),
                tableform.fields_render([
                    { post_field: "animals", label: _("Animals"), type: "animalmulti", validation: "notblank" },
                    { post_field: "person", label: _("New Owner"), type: "person", personfilter: personfilter },
                    { post_field: "homechecked", label: _("Mark this person homechecked"), type: "check", rowid: "homecheckrow" },
                    { post_field: "movementnumber", label: _("Movement Number"), type: "text", callout: _("A unique number to identify this movement"), rowid: "movementnumberrow" },
                    { post_field: "movementdate", label: _("Date"), type: "date" },
                    { post_field: "reservationstatus", label: _("Status"), type: "select", 
                        options: { displayfield: "STATUSNAME", valuefield: "ID", rows: controller.reservationstatuses}, 
                        hideif: function() {
                            return controller.mode != "reserve";
                        }
                    },
                    { post_field: "eventlink", label: _("Link to event"), type: "check", hideif: function(){return !common.has_permission("lem") || config.bool("DisableEvents");}},
                    { post_field: "event", label: _(""), type: "select"},
                    { post_field: "trial", label: _("Trial adoption"), type: "check", rowid: "trialrow1" },
                    { post_field: "trialenddate", label: _("Trial ends on"), type: "date", rowid: "trialrow2" },
                    { post_field: "comments", label: _("Comments"), type: "textarea", rows: 3, rowid: "commentsrow" },
                    { type: "additional", markup: additional.additional_new_fields(controller.additional) }
                ], { full_width: false }),
                html.content_footer(),
                html.content_header(_("Insurance"), true),
                tableform.fields_render([
                    { type: "raw", rowid: "insurancerow", markup: '<table id="insurancetable"></table>', doublesize: true },
                ], { full_width: false }),
                html.content_footer(),
                // '<div id="payment"></div>',
                 html.content_header(_("Payment"), true),
                tableform.fields_render([
                    { post_field: "paymentmethod", label: _("Payment method"), type: "select",
                        options: { displayfield: "PAYMENTNAME", valuefield: "ID", rows: controller.paymentmethods } },
                    // { post_field: "destaccount", label: _("Deposit accocunt"), type: "select",
                    //     options: { displayfield: "CODE", valuefield: "ID", rows: controller.accounts } },
                ], { full_width: false }),
                html.content_footer(),
                html.content_header(_("Boarding Costs"), true),
                html.info("<span id=\"costdata\"></span>", "costdisplay"),
                '<input id="costtype" data="costtype" type="hidden" />',
                tableform.fields_render([
                    { post_field: "costcreate", label: _("Create a cost record"), type: "check" }
                ], { full_width: false }),
                html.content_footer(),
                html.content_header(_("Signed Paperwork"), true),
                tableform.fields_render([
                    { post_field: "sigpaperwork", label: _("Request signed paperwork from the adopter by email"), type: "check" },
                    { post_field: "sigtemplateid", label: _("Adoption paperwork template"), type: "select",
                        options: edit_header.template_list_options(controller.templates) },
                    { post_field: "sigemailaddress", label: _("Adopter email address"), type: "text" },
                    { post_field: "sigemailtemplateid", label: _("Email template"), type: "select", 
                        options: edit_header.template_list_options(controller.templatesemail) },
                ], { full_width: false }),
                html.content_footer(),
                html.content_header(_("Checkout"), true),
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
                html.content_header(_("Extra Paperwork"), true),
                tableform.fields_render([
                    { post_field: "nonsigtemplateids", label: _("Paperwork templates"), type: "selectmulti",
                        options: { displayfield: "NAME", valuefield: "ID", rows: controller.templates } },
                ], { full_width: false }),
                html.content_footer(),
                tableform.buttons_render([
                   { id: "adopt", icon: "movement", text: _("Adopt") }
                ], { render_box: true }),
                '</div>'
            ].join("\n");
        },

        sync: function() {
            // $("#payment .ui-widget-content").prepend('<div id="adoptionfees"></div>');
            $("#paymentmethod").select("value", config.str("AFDefaultPaymentMethod"));
            // $("#destaccount").select("value", config.str("DonationTargetAccount"));

            if (controller.mode == "reserve") {
                $("#personrow label").html(_("Person"));
                $("#trialrow1, #trialrow2").hide();
                $("#reservationstatus").select("value", config.str("AFDefaultReservationStatus"));
                $(".ui-accordion-header").first().html(_("Reserve animal(s)"));
                $($(".ui-accordion")[1]).hide(); // Hide insurance
                $($(".ui-accordion")[3]).hide(); // Hide boarding costs
                $("#costcreaterow").hide(); // Hide create cost checkbox row
                $("#button-adopt").html('<span class="asm-icon asm-icon-reservation"></span>' + _("Reserve"));
            } else if (controller.mode == "foster") {
                $("#personrow label").html(_("Fosterer"));
                $("#trialrow1, #trialrow2").hide();
                $(".ui-accordion-header").first().html(_("Foster animal(s)"));
                $($(".ui-accordion")[1]).hide(); // Hide insurance
                $($(".ui-accordion")[3]).hide(); // Hide boarding costs
                $("#costcreaterow").hide(); // Hide create cost checkbox row
                $($(".ui-accordion")[2]).hide(); // Hide payment tab
                // $("#payment").hide(); // Hide payment panel
                $("#eventlinkrow").hide();
                $("#button-adopt").html('<span class="asm-icon asm-icon-movement"></span>' + _("Foster"));
            } else if (controller.mode == "transfer") {
                $("#personrow label").html(_("Transfer to"));
                $("#trialrow1, #trialrow2").hide();
                $(".ui-accordion-header").first().html(_("Transfer animal(s)"));
                $($(".ui-accordion")[1]).hide(); // Hide insurance
                $($(".ui-accordion")[3]).hide(); // Hide boarding costs
                $("#costcreaterow").hide(); // Hide create cost checkbox row
                $($(".ui-accordion")[2]).hide(); // Hide payment tab
                // $("#payment").hide(); // Hide payment panel
                $("#eventlinkrow").hide();
                $("#button-adopt").html('<span class="asm-icon asm-icon-movement"></span>' + _("Transfer"));
            } else if (controller.mode == "retail") {
                $("#personrow label").html(_("Retailer"));
                $("#trialrow1, #trialrow2").hide();
                $(".ui-accordion-header").first().html(_("Move animal(s)"));
                $($(".ui-accordion")[1]).hide(); // Hide insurance
                $($(".ui-accordion")[3]).hide(); // Hide boarding costs
                $("#costcreaterow").hide(); // Hide create cost checkbox row
                $($(".ui-accordion")[2]).hide(); // Hide payment tab
                // $("#payment").hide(); // Hide payment panel
                $("#eventlinkrow").hide();
                $("#button-adopt").html('<span class="asm-icon asm-icon-movement"></span>' + _("Move"));
            } else if (controller.mode == "reclaim") {
                $("#personrow label").html(_("Owner"));
                $("#trialrow1, #trialrow2").hide();
                $(".ui-accordion-header").first().html(_("Reclaim animal(s)"));
                $($(".ui-accordion-header")[1]).hide(); // Hide insurance tab
                $($(".ui-accordion")[3]).hide(); // Hide insurance panel
                $($(".ui-widget-content")[11]).hide(); // Hide insurance panel
                $("#eventlinkrow").hide();
                $("#button-adopt").html('<span class="asm-icon asm-icon-movement"></span>' + _("Reclaim"));
            }
        },

        bind: function() {
            $("#animals").on("cleared", function() {
                move_workflow.bondedanimals = [];
                move_workflow.adoptionfees = {};
                $("#animals").change();
            });
            
            const validation = function() {
                // Remove any previous errors
                header.hide_error();
                validate.reset();
                // animal
                if (!validate.notblank([ "animals" ])) {
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

            let lastperson;

            // Callback when animal is changed
            $("#animals").on("change", function(event, animals) {
                move_workflow.bondedanimals = [];
                move_workflow.adoptionfees = {};
                while (move_workflow.add_bonded_animals()) {}
                move_workflow.process_animals();
            });
            

            // Callback when person is changed
            $("#person").on("change", async function(event, rec) {
                let response = await edit_header.person_with_adoption_warnings(rec.ID);
                let p = jQuery.parseJSON(response)[0];
                lastperson = p;

                $("#ownerwarn").hide();
                $("#checkoutcreate").closest(".ui-widget").hide();
                $("#sigpaperwork").closest(".ui-widget").hide();
                $("#nonsigtemplateids").closest(".ui-widget").hide();

                // Show the checkout section if it's configured and there's an animal with 
                // a non-zero adoption fee
                let animalselected = false;
                let adoptionfeefound = false;
                let reservedanimals = [];
                if ($("#animals").val()) {
                    animalselected = true;
                    $.each($("#animals").animalchoosermulti("get_selected_rows"), function(i, v) {
                        if (v.FEE > 0) {
                            adoptionfeefound = true;
                        }
                        if (v.HASACTIVERESERVE) {
                            reservedanimals.push([v.ID, v.SHELTERCODE, v.ANIMALNAME]);
                        }
                    });
                }
                if (config.str("AdoptionCheckoutProcessor") && config.str("AdoptionCheckoutProcessor") != "null" && animalselected && adoptionfeefound) {
                    $("#emailaddress").val(p.EMAILADDRESS);
                    $("#templateid").select("value", config.str("AdoptionCheckoutTemplateID"));
                    $("#feetypeid").select("value", config.str("AdoptionCheckoutFeeID"));
                    $("#checkoutcreate").closest(".ui-widget").show();
                    $("#nonsigtemplateids").closest(".ui-widget").show();
                }
                // If it isnt, show the request signed contract section if that is configured
                else if (config.bool("MoveAdoptGeneratePaperwork")) {
                    $("#sigemailaddress").val(p.EMAILADDRESS);
                    $("#sigtemplateid").select("value", config.str("AdoptionCheckoutTemplateID"));
                    $("#sigpaperwork").closest(".ui-widget").show();
                    $("#nonsigtemplateids").closest(".ui-widget").show();
                }

                // Show tickbox if owner not homechecked
                if (p.IDCHECK == 0) {
                    $("#markhomechecked").attr("checked", false);
                    $("#homecheckrow").show();
                }

                // Default giftaid if the person is registered
                // if (common.has_permission("oaod")) {
                //     $("#payment").payments("set_giftaid", p.ISGIFTAID == 1);
                //     $("#giftaid1").prop("checked", p.ISGIFTAID == 1);
                // }

                let oopostcode = $(".animalchooser-oopostcode").val();
                let bipostcode = $(".animalchooser-bipostcode").val(); 
                let warn = html.person_movement_warnings(p, oopostcode, bipostcode);

                // Check whether the animal has reservations. 
                // If it does, show a warning if this person does not have one on the animal.
                if (config.bool("WarnNoReserve") && animalselected && reservedanimals) {
                    $.each(reservedanimals, function(i, v) {
                        if (!common.array_in(String(v[0]), p.RESERVEDANIMALIDS.split(","))) {
                            warn.push(_(v[1] + " " + v[2] + " is reserved by another person."));
                        }
                    });
                }

                if (warn.length > 0) {
                    $("#warntext").html(warn.join("<br>"));
                    $("#ownerwarn").show();
                }

            });

            $("#costdisplay").closest(".ui-widget").hide();
            $("#checkoutcreate").closest(".ui-widget").hide();
            $("#sigpaperwork").closest(".ui-widget").hide();
            $("#nonsigtemplateids").closest(".ui-widget").hide();
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
            // if (common.has_permission("oaod")) {
            //     $("#payment").payments({ controller: controller });
            // }

            // $("#payment #paymentlines tr").remove();
            // $("#payment").payments("update_totals");

            // If checkout is turned on, hide the payments section
            $("#checkoutcreate").change(function() {
                // $("#payment").toggle(!$("#checkoutcreate").prop("checked"));
                $($(".ui-accordion-header")[2]).toggle();
            });

            // Insurance related stuff
            $("#button-insurance")
                .button({ icons: { primary: "ui-icon-cart" }, text: false })
                .click(async function() {
                $("#button-insurance").button("disable");
                let response = await common.ajax_post("move_workflow", "mode=insurance");
                $("#insurance").val(response);
                $("#button-insurance").button("enable");
            });
            if (!config.bool("UseAutoInsurance")) { $("#button-insurance").button("disable"); }

            // Events related stuff
            if ($("#eventlink").is(":checked")) {
                $("#eventrow").show();
            }
            else {
                $("#eventrow").hide();
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
                    $("#eventrow").show();
                    move_workflow.populate_event_dates();
                }
                else {
                    $("#eventrow").hide();
                }
            });

            $("#page1").show();
            $("#page2").hide();

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
                $("#numofmovements").html($("#animals").animalchoosermulti("value").split(",").length);
                let confirmbuttontext = _("Adopt");
                if (controller.mode == "reserve") {
                    confirmbuttontext = _("Reserve");
                } else if (controller.mode == "foster") {
                    confirmbuttontext = _("Foster");
                } else if (controller.mode == "transfer") {
                    confirmbuttontext = _("Transfer");
                } else if (controller.mode == "retail") {
                    confirmbuttontext = _("Move");
                } else if (controller.mode == "reclaim") {
                    confirmbuttontext = _("Reclaim");
                }
                await tableform.show_okcancel_dialog("#dialog-adopt-confirm", confirmbuttontext);
                if (!validation()) { return; }
                $("#button-adopt").button("disable");
                header.show_loading(_("Creating..."));
                try {
                    let formdata = "movementtype=" + controller.mode + "&";
                    formdata += "mode=create&" + $("input, select, textarea").not(".asm-incnumber").toPOST(); // Exclude additional incremental number fields
                    
                    // Process additional incremental number fields
                    $.each($(".asm-incnumber"), function(i, v) {
                        $(v).val(parseInt(v) + 1);
                    });
                    formdata += "&" + $(".asm-incnumber").toPOST(false, true);

                    // Process adoption fees
                    $.each(move_workflow.adoptionfees, function(i, v){
                        formdata += "&adoptionfee" + i + "=" + v;
                    });
                    let response = await common.ajax_post("move_workflow", formdata);
                    let jsondata = JSON.parse(response.replace(/'/g, '"'));
                    header.hide_loading();
                    $(".ui-accordion").hide();
                    $("#button-adopt").hide();
                    let successmessage = [
                        html.content_header(_("Adoption(s) successfully created")),
                        '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em;">',
                        '<p><span class="ui-icon ui-icon-info"></span> ' + _("Details") + '</p>',
                    ];
                    successmessage.push("<p>" + $(".animalchoosermulti-display").html() + "</p>");
                    if (controller.mode == "reserve") {
                        successmessage.push("<p>" + _("reserved by") + "</p>");
                    } else if (controller.mode == "foster") {
                        successmessage.push("<p>" + _("fostered by") + "</p>");
                    } else if (controller.mode == "transfer") {
                        successmessage.push("<p>" + _("transfered to") + "</p>");
                    } else if (controller.mode == "retail") {
                        successmessage.push("<p>" + _("moved to") + "</p>");
                    } else if (controller.mode == "reclaim") {
                        successmessage.push("<p>" + _("reclaimed by") + "</p>");
                    } else {
                        successmessage.push("<p>" + _("adopted to") + "</p>");
                    }
                    successmessage.push("<p>" + $(".personchooser-display .justlink").html() + "</p>");

                    if (jsondata.length) {
                        successmessage.push("<p>Extra adoption paperwork</p><ul>");
                        $.each(jsondata, function(i, v) {
                            successmessage.push('<li><a href="/document_media_edit?id=' + v[0] + '&redirecturl=person_media?id=' + $("#person").val() + '"><b>' + v[1] + '</b></a></li>');
                        });
                        successmessage.push("</ul>");
                    }
                    if (config.bool("MoveAdoptDonationsEnabled") && !$("#checkoutcreate").prop("checked")) {
                        successmessage.push('<p><a href="/person_donations?id=' + $("#person").val() + '"><button id="asm-settlebutton">' + _("Settle Payments") + '</button></a>');
                    }

                    successmessage.push('</div>');
                    successmessage.push(html.content_footer());
                    $("#asm-body-container").html(successmessage.join("\n"));
                    $("#asm-settlebutton").button();
                    $("#asm-content").show();
                    // If the option to allow editing payments after creating the adoption is set, take
                    // the user to a payment screen that allows them to see the movement payments in order
                    // to take payment, request payment by email, generate an invoice/receipt, etc.
                    // let movementdata = "";
                    // JSON.parse(response.movementdata);
                    // console.log(JSON.parse(response));
                    // if (config.bool("MoveAdoptDonationsEnabled") && !$("#checkoutcreate").prop("checked")) {
                    //     let u = "move_donations?" +
                    //         "linktype=MOVEMENT&id=" + response +
                    //         "&message=" + encodeURIComponent(common.base64_encode(_("Adoption successfully created.") + " " + 
                    //             $(".animalchooser-display").html() + " " + html.icon("right") + " " +
                    //             $(".personchooser-display .justlink").html() )) + 
                    //             "&animalid=" + $("#animals").val() + 
                    //             "&ownerid=" + $("#person").val();
                    //     common.route(u);
                    // }
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

        add_bonded_animals: function() {
            let additionalids = [];
            let currentval = $("#animals").animalchoosermulti("value");
            if (currentval) {
                $.each($("#animals").animalchoosermulti("get_selected_rows"), function(i, a) {
                    if (a.BONDEDANIMALID && a.BONDEDANIMAL1ARCHIVED == 0) {
                        if (!currentval.split(",").includes(a.BONDEDANIMALID.toString()) && !additionalids.includes(a.BONDEDANIMALID)) {
                            move_workflow.bondedanimals.push(
                                [
                                    a.BONDEDANIMALID,
                                    _("{0} {1} is bonded to {2} {3} who is not selected, they will be included.").replace("{0}", a.SHELTERCODE).replace("{1}", a.ANIMALNAME).replace("{2}", a.BONDEDANIMAL1CODE).replace("{3}", a.BONDEDANIMAL1NAME)
                                ]
                            );
                            additionalids.push(a.BONDEDANIMALID);
                        }
                    }
                    if (a.BONDEDANIMAL2ID && a.BONDEDANIMAL2ARCHIVED == 0) {
                        if (!currentval.split(",").includes(a.BONDEDANIMAL2ID.toString()) && !additionalids.includes(a.BONDEDANIMAL2ID)) {
                            move_workflow.bondedanimals.push(
                                [
                                    a.BONDEDANIMAL2ID,
                                    _("{0} {1} is bonded to {2} {3} who is not selected, they will be included.").replace("{0}", a.SHELTERCODE).replace("{1}", a.ANIMALNAME).replace("{2}", a.BONDEDANIMAL2CODE).replace("{3}", a.BONDEDANIMAL2NAME)
                                ]
                            );
                            additionalids.push(a.BONDEDANIMAL2ID);
                        }
                    }
                });

                if (additionalids.length) {
                    let newids = additionalids.join(",");
                    let newval = currentval + "," + newids;
                    $("#animals").animalchoosermulti("value", newval);
                    return true;
                } else {
                    return false;
                }
            }
            return false;
        },

        process_animals: async function() {
            // Hide things before we start
            $("#bonddisplay").hide();
            $("#costdisplay").closest(".ui-widget").hide();
            $("#fosterinfo").hide();
            $("#reserveinfo").hide();
            $("#retailerinfo").hide();
            $("#feeinfo").hide();
            $("#animalwarn").hide();
            $("#button-adopt").button("enable");
            $("#costdata").html("");
            $("#payment #paymentlines tr").remove();
            $("#payment").payments("update_totals");
            $("#insurancetable tr").remove();
            $("#adoptionfees").html('<h3 align="center">' + _("Adoption fees") + '</h3>');

            let disable = false;
            let fosters = [];
            let atretailer = [];
            let reservations = [];
            // let bondedanimals = [];
            let noadoptionfee = [];
            let warn = [];
            let costs = [];

            $.each($("#animals").animalchoosermulti("get_selected_rows"), function(i, a) {
                if ((a.ARCHIVED == 1 && a.ACTIVEMOVEMENTTYPE != 2 && a.ACTIVEMOVEMENTTYPE != 8) ||
                    a.ISHOLD == 1 || a.CRUELTYCASE == 1 || a.ISQUARANTINE == 1) {
                    disable = true;
                }
                if (a.ACTIVEMOVEMENTTYPE == 2) {
                    fosters.push(
                        _("{0} {1} is currently fostered and will be automatically returned first.").replace("{0}", a.SHELTERCODE).replace("{1}", a.ANIMALNAME)
                    );
                }
                if (a.ACTIVEMOVEMENTTYPE == 8) {
                    atretailer.push(
                        _("{0} {1} is currently at a retailer and will be automatically returned first.").replace("{0}", a.SHELTERCODE).replace("{1}", a.ANIMALNAME)
                    );
                }
                if (a.HASACTIVERESERVE == 1 && config.bool("CancelReservesOnAdoption")) {
                    reservations.push(
                        _("{0} {1} has active reservations, they will be cancelled.").replace("{0}", a.SHELTERCODE).replace("{1}", a.ANIMALNAME)
                    );
                }
                // Grab cost information if option is on
                if ( ( controller.mode == "adopt" || controller.mode == "reclaim") && config.bool("CreateBoardingCostOnAdoption") ) {
                    let formdata = "mode=cost&id=" + a.ID;
                    common.ajax_post("move_workflow", formdata).then(function(response) {
                        let [costamount, costdata] = response.split("||");
                        costs.push(a.SHELTERCODE + " " + a.ANIMALNAME + " " + costdata);
                        // hiddencostinputs.push('<input id="animalcost' + a.ID + '" type=hidden value="' + costamount + '">');
                        // totalcost += parseInt(costamount);
                        if (config.bool("CreateBoardingCostOnAdoption")) {
                            $("#costamount").val(costamount);
                            $("#costtype").val(config.str("BoardingCostType"));
                            $("#costdata").html(costs.join("<br>"));
                            $("#costdisplay").after('<input id="animalcost' + a.ID + '" data-post="animalcost' + a.ID + '" type=hidden value="' + costamount + '">');
                            $("#costcreate").prop("checked", true);
                            $("#costdisplay").closest(".ui-widget").show();
                        }
                    });
                }
                if ( ( controller.mode == "adopt" || controller.mode == "reclaim") && !config.bool("DontShowAdoptionFee") && a.FEE ) {
                    move_workflow.adoptionfees[a.ID] = a.FEE;
                    $(".takepayment").first().click();
                    let newrow = $("#paymentlines tr").last();
                    newrow.attr("data-animalid", a.ID);
                    newrow.find(".amount").currency("value", a.FEE);
                    newrow.find(".unitprice").currency("value", a.FEE);
                    newrow.find(".asm-textbox").last().val(a.SHELTERCODE + " " + a.ANIMALNAME);
                    // $("#adoptionfees").html($("#adoptionfees").html() + 
                    //     [
                    //         '<div class="asm-adoptionfee">',
                    //         a.SHELTERCODE + " " + a.ANIMALNAME + " " + format.currency(a.FEE),
                    //         '</div>'
                    //     ].join("\n")
                    // );
                    // $("#amount1").currency("value", a.FEE);
                    // if ($("#vat1").is(":checked")) { 
                        // Recalculate the tax
                        $("#vat1").change();
                    // }

                    if (newrow.find(".asm-checkbox").is(":checked")) {
                        newrow.find(".asm-checkbox").change();
                    }
                    // $("#feeinfo .subtext").html( _("This animal has an adoption fee of {0}").replace("{0}", format.currency(a.FEE)));
                    noadoptionfee.push(a);
                    // $("#feeinfo").show();
                }
                let warnings = html.animal_movement_warnings(a, true, true);
                warn = warn.concat(warnings);
                if (warn.length > 0) {
                    $("#awarntext").html(warn.join("<br>"));
                    $("#animalwarn").show();
                }
                if (controller.mode == "adopt") {
                    $("#insurancetable").html($("#insurancetable").html() + '<tr><td>' + a.SHELTERCODE + ' ' + a.ANIMALNAME + ' (' + a.SPECIESNAME + ')</td><td>' +
                    tableform.fields_render([
                        { post_field: "insurance" + a.ID, type: "text", rowclasses: "insurancerow", xbutton: _("Issue a new insurance number for this animal/adoption") },
                    ]) + 
                    '</td></tr>');
                    $(".insurancerow button")
                        .button({ icons: { primary: "ui-icon-cart" }, text: false })
                        .click(async function() {
                            $(this).button("disable");
                            let response = await common.ajax_post("move_workflow", "mode=insurance");
                            $(this).prev().val(response);
                            $(this).button("enable");
                        }
                    );
                    $("#payment").payments("update_totals");
                }
            });
            if (disable) { $("#button-adopt").button("disable"); }
            if (fosters.length) {
                $("#fosterinfo").html('<div class="ui-state-highlight ui-corner-all" style="padding: 5px;"><p><span class="ui-icon ui-icon-info"></span>' + fosters.join("<br>") + '</p></div>');
                $("#fosterinfo").show();
            }
            if (atretailer.length) {
                $("#retailerinfo").html('<div class="ui-state-highlight ui-corner-all" style="padding: 5px;"><p><span class="ui-icon ui-icon-info"></span>' + atretailer.join("<br>") + '</p></div>');
                $("#retailerinfo").show();
            }
            if (reservations.length) {
                $("#reserveinfo").html('<div class="ui-state-highlight ui-corner-all" style="padding: 5px;"><p><span class="ui-icon ui-icon-info"></span>' + reservations.join("<br>") + '</p></div>');
                $("#reserveinfo").show();
            }
            if (move_workflow.bondedanimals.length) {
                let bondedmessages = [];
                let bondedids = [];
                $.each(move_workflow.bondedanimals, function(i, v) {
                    bondedids.push(v[0]);
                    bondedmessages.push(v[1]);
                });
                $("#bonddisplay").html('<div class="ui-state-highlight ui-corner-all" style="padding: 5px;"><p><span class="ui-icon ui-icon-alert"></span>' + bondedmessages.join("<br>") + '</p></div>');
                $("#bonddisplay").show();
            }
        },

        destroy: function() {
            common.widget_destroy("#animal");
            common.widget_destroy("#person");
        },

        name: "move_workflow",
        animation: "newdata",
        autofocus: "#asm-content button:first",
        title: function() {
            if (controller.mode == "reserve") {
                return _("Reserve animal(s)");
            } else if (controller.mode == "foster") {
                return _("Foster animal(s)");
            } else if (controller.mode == "transfer") {
                return _("Transfer animal(s)");
            } else if (controller.mode == "retail") {
                return _("Move animal(s)");
            } else if (controller.mode == "reclaim") {
                return _("Reclaim animal(s)");
            }
            return _("Adopt animal(s)");
        },
        routes: {
            "move_reserve_multi": function() { common.module_loadandstart("move_workflow", "move_reserve_multi"); },
            "move_foster_multi": function() { common.module_loadandstart("move_workflow", "move_foster_multi"); },
            "move_transfer_multi": function() { common.module_loadandstart("move_workflow", "move_transfer_multi"); },
            "move_retailer_multi": function() { common.module_loadandstart("move_workflow", "move_retailer_multi"); },
            "move_reclaim_multi": function() { common.module_loadandstart("move_workflow", "move_reclaim_multi"); },
            "move_adopt_multi": function() { common.module_loadandstart("move_workflow", "move_adopt_multi"); },
        }
    };

    common.module_register(move_workflow);

});
