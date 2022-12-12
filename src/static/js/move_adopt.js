/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, edit_header, html, validate */

$(function() {

    "use strict";

    const move_adopt = {

        infobox: function(id, s) {
            return '<div id="' + id + '" class="ui-state-highlight ui-corner-all" ' +
                'style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">' +
                '<p class="centered"><span class="ui-icon ui-icon-info"></span>' + s + '</p>' + 
                '</div>';
        },

        warnbox: function(id, s) {
            return '<div id="' + id + '" class="ui-state-error ui-corner-all" ' +
                'style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">' +
                '<p class="centered"><span class="ui-icon ui-icon-alert"></span>' + s + '</p>' + 
                '</div>';
        },

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="movementid" type="hidden" />',
                html.content_header(_("Adopt an animal"), true),
                this.warnbox("bonddisplay", '<span id="bonddata"></span>'),
                this.infobox("fosterinfo", _("This animal is currently fostered, it will be automatically returned first.")),
                this.infobox("retailerinfo", _("This animal is currently at a retailer, it will be automatically returned first.")),
                this.infobox("reserveinfo", _("This animal has active reservations, they will be cancelled.")),
                this.infobox("feeinfo", '<span class="subtext"></span>'),
                this.warnbox("ownerwarn", '<span id="warntext"></span>'),
                this.warnbox("notonshelter", _("This animal is not on the shelter.")),
                this.warnbox("onhold", _("This animal is currently held and cannot be adopted.")),
                this.warnbox("notavailable", _("This animal is marked not for adoption.")),
                this.warnbox("crueltycase", _("This animal is part of a cruelty case and should not leave the shelter.")),
                this.warnbox("quarantine", _("This animal is currently quarantined and should not leave the shelter.")),
                this.warnbox("unaltered", _("This animal has not been altered.")),
                this.warnbox("notmicrochipped", _("This animal has not been microchipped.")),
                this.warnbox("outstandingmedical", _("This animal has outstanding medical treatments.")),
                tableform.fields_render([
                    { post_field: "animal", label: _("Animal"), type: "animal" },
                    { post_field: "person", label: _("New Owner"), type: "person" },
                    { post_field: "homechecked", label: _("Mark this owner homechecked"), type: "check", rowid: "homecheckrow" },
                    { post_field: "movementnumber", label: _("Movement Number"), type: "text", callout: _("A unique number to identify this movement"), rowid: "movementnumberrow" },
                    { post_field: "movementdate", label: _("Date"), type: "date" },
                    { post_field: "eventlink", label: _("Link to event"), type: "check", hideif: function(){return !common.has_permission("lem");}},
                    { post_field: "event", label: _(""), type: "select"},
                    { post_field: "trial", label: _("Trial adoption"), type: "check", rowid: "trialrow1" },
                    { post_field: "trialenddate", label: _("Trial ends on"), type: "date", rowid: "trialrow2" },
                    { post_field: "insurance", label: _("Insurance"), type: "text", rowid: "insurancerow", xbutton: _("Issue a new insurance number for this animal/adoption") },
                    { post_field: "comments", label: _("Comments"), type: "textarea", rows: 3, rowid: "commentsrow" }
                ], 1, { full_width: false }),
                html.content_footer(),
                '<div id="payment"></div>',
                html.content_header(_("Boarding Cost"), true),
                this.infobox("costdisplay", "<span id=\"costdata\"></span>"),
                '<input id="costamount" data="costamount" type="hidden" />',
                '<input id="costtype" data="costtype" type="hidden" />',
                tableform.fields_render([
                    { post_field: "costcreate", label: _("Create a cost record"), type: "check" }
                ], 1, { full_width: false }),
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
                ], 1, { full_width: false }),
                html.content_footer(),
                html.box(5),
                '<button id="adopt">' + html.icon("movement") + ' ' + _("Adopt") + '</button>',
                '</div>',
                '</div>'
            ].join("\n");
        },

        bind: function() {
            if($("#eventlink")[0].checked)
                $("#event").closest("tr").fadeIn();
            else
                $("#event").closest("tr").fadeOut();

            //callback when eventlink changed its status
             $("#eventlink").change(function(){
                // event link needs a movement date
                if (this.checked && $("#movementdate").val() == ""){
                    validate.notblank([ "movementdate" ]);
                    tableform.dialog_error(_("Fill out adoption date before linking to event."));
                    this.checked = false;
                }
                $("#event").empty();
                if (this.checked){
                    $("#event").closest("tr").fadeIn();
                    move_adopt.event_dates();
                }
                else
                    $("#event").closest("tr").fadeOut();

            });
            //callback when movementdate is changed
            $("#movementdate").change(function(){
                $("#event").empty();
                // event link needs a movement date
                if ($("#movementdate").val() == ""){
                    validate.notblank([ "movementdate" ]);
                    tableform.dialog_error(_("Fill out adoption date before linking to event."));
                    $("#eventlink")[0].checked = false;
                }
                if($("#eventlink")[0].checked){
                    move_adopt.event_dates();
                }

            });

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

                return true;
            };

            validate.indicator([ "animal", "person", "movementdate" ]);

            // Callback when animal is changed
            $("#animal").animalchooser().bind("animalchooserchange", async function(event, a) {
                // Hide things before we start
                $("#bonddisplay").fadeOut();
                $("#costdisplay").closest(".ui-widget").fadeOut();
                $("#checkoutcreate").closest(".ui-widget").fadeOut();
                $("#fosterinfo").fadeOut();
                $("#reserveinfo").fadeOut();
                $("#retailerinfo").fadeOut();
                $("#feeinfo").fadeOut();
                $("#notonshelter").fadeOut();
                $("#onhold").fadeOut();
                $("#notavailable").fadeOut();
                $("#crueltycase").fadeOut();
                $("#quarantine").fadeOut();
                $("#unaltered").fadeOut();
                $("#notmicrochipped").fadeOut();
                $("#outstandingmedical").fadeOut();
                $("#adopt").button("enable");

                // If the animal is not on the shelter and not fostered or at a retailer, 
                // bail out now because we shouldn't be able to move the animal.
                if (a.ARCHIVED == 1 && a.ACTIVEMOVEMENTTYPE != 2 && a.ACTIVEMOVEMENTTYPE != 8) {
                    $("#notonshelter").fadeIn();
                    $("#adopt").button("disable");
                    return;
                }

                // If the animal is held, we shouldn't be allowed to adopt it
                if (a.ISHOLD == 1) {
                    $("#onhold").fadeIn();
                    $("#adopt").button("disable");
                    return;
                }

                // If the animal is a cruelty case, we should prevent adoption
                if (a.CRUELTYCASE == 1) {
                    $("#crueltycase").fadeIn();
                    $("#adopt").button("disable");
                    return;
                }

                // If the animal is quarantined, we shouldn't allow adoption
                if (a.ISQUARANTINE == 1) {
                    $("#quarantine").fadeIn();
                    $("#adopt").button("disable");
                    return;
                }

                // Not available for adoption (warning only)
                if (a.ISNOTAVAILABLEFORADOPTION == 1) {
                    $("#notavailable").fadeIn();
                }

                // Unaltered
                if (config.bool("WarnUnaltered") && a.NEUTERED == 0) {
                    $("#unaltered").fadeIn();
                }

                // Not microchipped
                if (config.bool("WarnNoMicrochip") && a.IDENTICHIPPED == 0) {
                    $("#notmicrochipped").fadeIn();
                }

                // Outstanding medical
                if (config.bool("WarnOSMedical") && a.HASOUTSTANDINGMEDICAL == 1) {
                    $("#outstandingmedical").fadeIn();
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

                // Check for bonded animals and warn
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
                    $("#costcreate").select("value", "1");
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

            });

            // Callback when person is changed
            $("#person").personchooser().bind("personchooserchange", async function(event, rec) {
                let response = await edit_header.person_with_adoption_warnings(rec.ID);
                let p = jQuery.parseJSON(response)[0];

                // Show the checkout section if it's configured
                if (config.str("AdoptionCheckoutProcessor") != "") {
                    $("#emailaddress").val(p.EMAILADDRESS);
                    $("#templateid").select("value", config.str("AdoptionCheckoutTemplateID"));
                    $("#feetypeid").select("value", config.str("AdoptionCheckoutFeeID"));
                    $("#checkoutcreate").closest(".ui-widget").show();
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
            
                // Owner banned?
                if (p.ISBANNED == 1 && config.bool("WarnBannedOwner")) {
                    $("#warntext").html(_("This person has been banned from adopting animals."));
                    $("#ownerwarn").fadeIn();
                    return;
                }

                // Person at this address previously banned?
                if (p.BANNEDADDRESS > 0 && config.bool("WarnBannedAddress")) {
                    $("#warntext").html(_("This person lives at the same address as someone who was previously banned."));
                    $("#ownerwarn").fadeIn();
                    return;
                }

                // Owner previously under investigation
                if (p.INVESTIGATION > 0) {
                    $("#warntext").html(_("This person has been under investigation."));
                    $("#ownerwarn").fadeIn();
                    return;
                }

                // Owner part of animal control incident
                if (p.INCIDENT > 0) {
                    $("#warntext").html(_("This person has an animal control incident against them."));
                    $("#ownerwarn").fadeIn();
                    return;
                }

                // Owner previously surrendered?
                if (p.SURRENDER > 0 && config.bool("WarnBroughtIn")) {
                    $("#warntext").html(_("This person has previously surrendered an animal."));
                    $("#ownerwarn").fadeIn();
                    return;
                }

                // Owner not homechecked?
                if (p.IDCHECK == 0 && config.bool("WarnNoHomeCheck")) {
                    $("#warntext").html(_("This person has not passed a homecheck."));
                    $("#ownerwarn").fadeIn();
                    return;
                }

                // Does this owner live in the same postcode area as the animal's
                // original owner?
                if ( format.postcode_prefix($(".animalchooser-oopostcode").val()) == format.postcode_prefix(p.OWNERPOSTCODE) ||
                     format.postcode_prefix($(".animalchooser-bipostcode").val()) == format.postcode_prefix(p.OWNERPOSTCODE) ) {
                    if (config.bool("WarnOOPostcode")) { 
                        $("#warntext").html(_("This person lives in the same area as the person who brought the animal to the shelter.")); 
                        $("#ownerwarn").fadeIn();
                        return;
                    }
                }

                $("#ownerwarn").fadeOut();
            });

            $("#costdisplay").closest(".ui-widget").hide();
            $("#checkoutcreate").closest(".ui-widget").hide();
            $("#bonddisplay").hide();
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

            $("#page1").show();
            $("#page2").hide();
            $("#asm-adopt-accordion").accordion({
                heightStyle: "content"
            });

            // Set default values
            $("#movementdate").datepicker("setDate", new Date());

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions", "all");

            // Show trial fields if option is set
            if (config.bool("TrialAdoptions")) {
                $("#trialrow1").show();
                $("#trialrow2").show();
            }


            $("#adopt").button().click(async function() {
                if (!validation()) { return; }
                $("#adopt").button("disable");
                header.show_loading(_("Creating..."));
                try {
                    let formdata = "mode=create&" + $("input, select, textarea").toPOST();
                    let response = await common.ajax_post("move_adopt", formdata);
                    $("#movementid").val(response);
                    header.hide_loading();
                    let u = "move_gendoc?" +
                        "linktype=MOVEMENT&id=" + response +
                        "&message=" + encodeURIComponent(common.base64_encode(_("Adoption successfully created.") + " " + 
                            $(".animalchooser-display").html() + " " + html.icon("right") + " " +
                            $(".personchooser-display .justlink").html() ));
                    common.route(u);
                }
                catch(err) {
                    log.error(err, err);
                    $("#adopt").button("enable");
                }
            });
        },

        event_dates: async function(){
            let result = await common.ajax_post("movement", "mode=eventlink&movementdate=" + $("#movementdate").val());
            let dates = jQuery.parseJSON(result);
            $.each(dates, function(i, v){
                $("#event").append("<option value='" + v.ID + "'>" + format.date(v.STARTDATETIME) + " - " + format.date(v.ENDDATETIME) +
                " " + v.EVENTNAME + " " + v.EVENTADDRESS + ", " + v.EVENTTOWN + ", " + v.EVENTCOUNTY + ", " + v.EVENTCOUNTRY + "</option>");
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
