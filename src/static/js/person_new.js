/*global $, jQuery, _, additional, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    "use strict";

    const person_new = {

        render: function() {
            return [
                '<div id="dialog-similar" style="display: none" title="' + html.title(_("Similar Person")) + '">',
                '<p><span class="ui-icon ui-icon-alert"></span>',
                _("This person is very similar to another person on file, carry on creating this record?"),
                '<br /><br />',
                '<span class="similar-person"></span>',
                '</p>',
                '</div>',
                html.content_header(_("Add a new person")),
                tableform.fields_render([
                    { post_field: "ownertype", type: "select", label: _("Class"), 
                        options: html.list_to_options([ '1|' + _("Individual"), '3|' + _("Couple"), '2|' + _("Organization") ])},
                    { post_field: "title", type: "text", label: _("Title"), maxlength: 50, 
                        rowclasses: "tag-individual", classes: "newform", 
                        xmarkup: tableform.render_text({ justwidget: true, post_field: "title2", classes: "tag-couple newform", maxlength: 50 }) },
                    { post_field: "initials", type: "text", label: _("Initials"), maxlength: 50, 
                        rowclasses: "tag-individual", classes: "newform", 
                        xmarkup: tableform.render_text({ justwidget: true, post_field: "initials2", classes: "tag-couple newform", maxlength: 50 }) },
                    { post_field: "forenames", type: "text", label: _("First name(s)"), maxlength: 50, 
                        rowclasses: "tag-individual", classes: "newform", 
                        xmarkup: tableform.render_text({ justwidget: true, post_field: "forenames2", classes: "tag-couple newform", maxlength: 50 }) },
                    { post_field: "surname", type: "text", label: _("Last name"), maxlength: 100,
                        labelclasses: "tag-individual", classes: "newform", 
                        xlabel: '<label for="surname" class="tag-organisation">' + _("Organization name") + '</label>',
                        xmarkup: tableform.render_text({ justwidget: true, post_field: "surname2", classes: "tag-couple newform", maxlength: 100 }) },
                    { post_field: "address", type: "textarea", label: _("Address"), classes: "asm-textareafixed newform", rows: 3},
                    { post_field: "town", type: "autotext", label: _("City"), classes: "newform", rowclasses: "towncounty", 
                        maxlength: 100, options: controller.towns, minlength: 3 },
                    common.iif(config.bool("USStateCodes"),
                        { post_field: "county", type: "select", label: _("State"), classes: "newform", rowclasses: "towncounty", 
                            options: html.states_us_options(config.str("OrganisationCounty")) },
                        { post_field: "county", type: "autotext", label: _("State"), classes: "newform", rowclasses: "towncounty", 
                            maxlength: 100, options: controller.counties, minlength: 3 }),
                    { post_field: "postcode", type: "text", label: _("Zipcode"), classes: "newform",  
                        xmarkup: '<button id="button-postcodelookup">' + _("Lookup Address") + '</button>' },
                    { post_field: "country", type: "text", label: _("Country") }, 
                    { post_field: "hometelephone", type: "phone", label: _("Home Phone"), classes: "newform" },
                    { post_field: "worktelephone", type: "phone", label: _("Work Phone"), classes: "newform",
                        xmarkup: tableform.render_phone({ justwidget: true, post_field: "worktelephone2", classes: "tag-couple newform" }) },
                    { post_field: "mobiletelephone", type: "phone", label: _("Cell Phone"), classes: "newform",
                        xmarkup: tableform.render_phone({ justwidget: true, post_field: "mobiletelephone2", classes: "tag-couple newform" }) },
                    { post_field: "emailaddress", type: "text", label: _("Email Address"), classes: "newform",
                        xmarkup: tableform.render_text({ justwidget: true, post_field: "emailaddress2", classes: "tag-couple newform" }) },
                    { post_field: "dateofbirth", type: "date", label: _("Date Of Birth"), classes: "newform",
                        xmarkup: tableform.render_date({ justwidget: true, post_field: "dateofbirth2", classes: "tag-couple newform" }) },
                    { post_field: "idnumber", type: "text", label: _("ID Number"), classes: "newform",
                        callout: _("Driving license, passport or other identification number"),
                        xmarkup: tableform.render_text({ justwidget: true, post_field: "idnumber2", classes: "tag-couple newform" }) },
                    { post_field: "jurisdiction", type: "select", label: _("Jurisdiction"), classes: "newform", 
                        options: { displayfield: "JURISDICTIONNAME", rows: controller.jurisdictions }},
                    { post_field: "flags", type: "selectmulti", label: _("Flags") },
                    { post_field: "gdprcontactoptin", type: "selectmulti", label: _("GDPR Contact Opt-In"), 
                        options: edit_header.gdpr_contact_options() },
                    { post_field: "site", type: "select", label: _("Site"), 
                        options: { displayfield: "SITENAME", rows: controller.sites, prepend: '<option value="0">' + _("(all)") + '</option>' }},
                    { type: "additional", markup: additional.additional_new_fields(controller.additional) }
                ], { full_width: false }),
                tableform.buttons_render([
                   { id: "addedit", icon: "person-add", text: _("Create and edit") },
                   { id: "add", icon: "person-add", text: _("Create") },
                   { id: "reset", icon: "delete", text: _("Reset") }
                ], { centered: true }),
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            const validation = function() {
                // Remove any previous errors
                header.hide_error();
                validate.reset();
                if (!validate.notblank([ "surname" ])) { return false; }
                // email
                if (common.trim($("#emailaddress").val()) != "") {
                    if (!validate.email($("#emailaddress").val())) {
                        header.show_error(_("Invalid email address '{0}'").replace("{0}", $("#emailaddress").val()));
                        validate.highlight("emailaddress");
                        return false;
                    }
                }
                // mandatory additional fields
                if (!additional.validate_mandatory()) { return false; }
                return true;
            };

            const add_person = async function() {
                if (!validation()) { 
                    $("#asm-content button").button("enable"); 
                    return; 
                }
                header.show_loading(_("Creating..."));
                try {
                    let formdata = $("input, textarea, select").not(".chooser").toPOST();
                    let personid = await common.ajax_post("person_new", formdata);
                    if (personid && person_new.create_and_edit) { 
                        common.route("person?id=" + personid); 
                    }
                    else {
                        header.show_info(_("Person successfully created"));
                    }
                }
                finally {
                    $("#asm-content button").button("enable");
                }
            };

            const similar_dialog = function() {
                let b = {}; 
                b[_("Create")] = function() {
                    $("#dialog-similar").disable_dialog_buttons();
                    add_person();
                    $("#asm-content button").button("enable");
                };
                b[_("Cancel")] = function() { 
                    $(this).dialog("close");
                    $("#asm-content button").button("enable");
                };
                $("#dialog-similar").dialog({
                     resizable: false,
                     modal: true,
                     width: 500,
                     dialogClass: "dialogshadow",
                     show: dlgfx.delete_show,
                     hide: dlgfx.delete_hide,
                     buttons: b
                });
            };

            const check_for_similar = async function() {
                if (!validation()) { 
                    $("#asm-content button").button("enable"); 
                    return; 
                }
                let formdata = "mode=similar&" + $("#emailaddress, #mobiletelephone, #surname, #forenames, #address").toPOST();
                let result = await common.ajax_post("person_embed", formdata);
                let people = jQuery.parseJSON(result);
                let rec = people[0];
                if (rec) {
                    let disp = "<span class=\"justlink\"><a class=\"asm-embed-name\" href=\"person?id=" + rec.ID + "\">" + rec.OWNERNAME + "</a></span>";
                    disp += "<br/>" + rec.OWNERADDRESS + "<br/>" + rec.OWNERTOWN + "<br/>" + rec.OWNERCOUNTY + "<br/>" + rec.OWNERPOSTCODE + "<br/>" + rec.HOMETELEPHONE + "<br/>" + rec.WORKTELEPHONE + "<br/>" + rec.MOBILETELEPHONE + " " + common.nulltostr(rec.MOBILETELEPHONE2) + "<br/>" + rec.EMAILADDRESS + " " + common.nulltostr(rec.EMAILADDRESS2);
                    $(".similar-person").html(disp);
                    similar_dialog();
                    return;
                }
                // Do a second check in case the user put a cell phone number in the home number field.
                // This is quite common in US databases where cell phone numbers have area codes like landlines.
                if ($("#hometelephone").val()) {
                    formdata = "mode=similar&mobiletelephone=" + $("#hometelephone").val() + "&" + $("#emailaddress, #surname, #forenames, #address").toPOST();
                    result = await common.ajax_post("person_embed", formdata);
                    people = jQuery.parseJSON(result);
                    rec = people[0];
                    if (rec) {
                        let disp = "<span class=\"justlink\"><a class=\"asm-embed-name\" href=\"person?id=" + rec.ID + "\">" + rec.OWNERNAME + "</a></span>";
                        disp += "<br/>" + rec.OWNERADDRESS + "<br/>" + rec.OWNERTOWN + "<br/>" + rec.OWNERCOUNTY + "<br/>" + rec.OWNERPOSTCODE + "<br/>" + rec.HOMETELEPHONE + "<br/>" + rec.WORKTELEPHONE + "<br/>" + rec.MOBILETELEPHONE + "<br/>" + rec.EMAILADDRESS;
                        $(".similar-person").html(disp);
                        similar_dialog();
                        return;
                    }
                }
                // No similar matches found, fall through to just adding the person
                add_person();
            };

            const check_org = function() {
                // Individual
                if ($("#ownertype").val() == 1) {
                    $(".tag-organisation").fadeOut();
                    $(".tag-couple").fadeOut();
                    $(".tag-individual").fadeIn();
                }
                // Organisation
                else if ($("#ownertype").val() == 2) {
                    $(".tag-couple").fadeOut();
                    $(".tag-individual").fadeOut();
                    $(".tag-organisation").fadeIn();
                }
                // Couple
                else if ($("#ownertype").val() == 3) {
                    $(".tag-organisation").fadeOut();
                    $(".tag-individual").fadeIn();
                    $(".tag-couple").fadeIn();
                }
            };

            $("#ownertype").change(check_org);
            check_org();

            // Load the person flag options
            html.person_flag_options(null, controller.flags, $("#flags"));

            $(".towncounty").toggle( !config.bool("HideTownCounty")); 
            $(".homeworkphone").toggle( !config.bool("HideHomeWorkPhone"));
            $("#countryrow").toggle( !config.bool("HideCountry") );
            $("#dateofbirthrow").toggle( !config.bool("HidePersonDateOfBirth") );
            $("#idnumberrow").toggle( !config.bool("HideIDNumber") );
            $("#gdprcontactoptinrow").toggle( config.bool("ShowGDPRContactOptIn") );

            if (config.bool("DisableAnimalControl")) {
                $("#jurisdictionrow").hide();
            }

            if (!config.bool("MultiSiteEnabled")) {
                $("#siterow").hide();
            }
            else {
                $("#site").select("value", asm.siteid);
            }

            $("#town").blur(function() {
                if ($("#county").val() == "" && $("#town").val() != "") {
                    $("#county").val(controller.towncounties[$("#town").val()]);
                }
            });

            $("#button-postcodelookup")
                .button({ icons: { primary: "ui-icon-search" }, text: false })
                .click(async function() {
                    let country = $("#country").val();
                    let postcode = $("#postcode").val();
                    if (!postcode) { return; }
                    if (!country) { country = config.str("OrganisationCountry"); }
                    let formdata = "mode=postcodelookup&country=" + country + "&postcode=" + postcode + "&locale=" + asm.locale + "&account=" + asm.useraccount;
                    const response = await common.ajax_post("person_embed", formdata);
                    const rows = jQuery.parseJSON(response);
                    $("#address").val( rows[0].street );
                    $("#town").val( rows[0].town );
                    $("#county").val( rows[0].county );
                });

            $("#button-postcodelookup").toggle( controller.postcodelookup );

            $("#button-add").button().click(function() {
                person_new.create_and_edit = false;
                $("#asm-content button").button("disable");
                check_for_similar();
            });

            $("#button-addedit").button().click(function() {
                person_new.create_and_edit = true;
                $("#asm-content button").button("disable");
                check_for_similar();
            });


            $("#button-reset").button().click(function() {
                person_new.reset();
            });
        },

        sync: function() {
            person_new.reset();
        },

        reset: function() {
            $(".newform").val("").change();
            if (config.bool("USStateCodes")) { $("#county").select("value", config.str("OrganisationCounty")); }
            $("#country").val( config.str("OrganisationCountry") );
            $("#jurisdiction").select("value", config.str("DefaultJurisdiction"));
            $(".asm-checkbox").prop("checked", false).change();
            $(".asm-personchooser").personchooser("clear");
            $("#flags option").prop("selected", false);
            $("#flags").change();

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");

        },

        destroy: function() {
            common.widget_destroy("#dialog-similar");
        },

        name: "person_new",
        animation: "newdata",
        autofocus: "#ownertype",
        title: function() { return _("Add a new person"); },
        routes: {
            "person_new": function() { common.module_loadandstart("person_new", "person_new"); }
        }

    };

    common.module_register(person_new);

});
