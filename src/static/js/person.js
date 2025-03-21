/*global $, jQuery, _, additional, asm, common, config, controller, dlgfx, edit_header, format, header, html, mapping, tableform, validate */

$(function() {

    "use strict";

    const person = {

        render_dialogs: function() {
            return [
                '<div id="dialog-merge" style="display: none" title="' + html.title(_("Select person to merge")) + '">',
                html.info(_("Select a person to merge into this record. The selected person will be removed, and their movements, diary notes, log entries, etc. will be reattached to this record.")),
                html.capture_autofocus(),
                tableform.fields_render([
                    { post_field: "mergeperson", type: "person", label: _("Person") }
                ], { full_width: true }),
                '</div>',
                '<div id="emailform"></div>',
                '<div id="dialog-popupwarning" style="display: none" title="' + html.title(_("Warning")) + '">',
                '<p>' + html.error(html.lf_to_br(controller.person.POPUPWARNING)) + '</p>',
                '</div>'
            ].join("\n");
        },

        render_details: function() {
            return [
                '<h3><a href="#">' + _("Name and Address") + '</a></h3>',
                '<div>',
                tableform.fields_render([
                    { type: "raw", label: _("Code"), markup: '<span class="asm-person-code">' + controller.person.OWNERCODE + '</span>' },
                    { post_field: "site", json_field: "SITEID", type: "select", label: _("Site"), 
                        options: { displayfield: "SITENAME", rows: controller.sites }},
                    { post_field: "ownertype", json_field: "OWNERTYPE", type: "select", label: _("Class"), 
                        options: html.list_to_options([ '1|' + _("Individual"), '3|' + _("Couple"), '2|' + _("Organization") ])},
                    { post_field: "viewroles", json_field: "VIEWROLEIDS", type: "selectmulti", label: _("View Roles"), 
                        callout: _("Only allow users with one of these roles to view this person record"),
                        options: { displayfield: "ROLENAME", rows: controller.roles }},
                    { post_field: "title", json_field: "OWNERTITLE", type: "text", label: _("Title"), maxlength: 50, 
                        rowclasses: "tag-individual",  colclasses: "nowrap",
                        xmarkup: tableform.render_text({ justwidget: true, post_field: "title2", json_field: "OWNERTITLE2", classes: "tag-couple", maxlength: 50 }) },
                    { post_field: "initials", json_field: "OWNERINITIALS", type: "text", label: _("Initials"), maxlength: 50, 
                        rowclasses: "tag-individual",  colclasses: "nowrap",
                        xmarkup: tableform.render_text({ justwidget: true, post_field: "initials2", json_field: "OWNERINITIALS2", classes: "tag-couple", maxlength: 50 }) },
                    { post_field: "forenames", json_field: "OWNERFORENAMES", type: "text", label: _("First name(s)"), maxlength: 50, 
                        rowclasses: "tag-individual",  colclasses: "nowrap",
                        xmarkup: tableform.render_text({ justwidget: true, post_field: "forenames2", json_field: "OWNERFORENAMES2", classes: "tag-couple", maxlength: 50 }) },
                    { post_field: "surname", json_field: "OWNERSURNAME", type: "text", label: _("Last name"), maxlength: 100,
                        labelclasses: "tag-individual", colclasses: "nowrap",
                        xlabel: '<label for="surname" class="tag-organisation">' + _("Organization name") + '</label>',
                        xmarkup: tableform.render_text({ justwidget: true, post_field: "surname2", json_field: "OWNERSURNAME2", classes: "tag-couple", maxlength: 100 }) },
                    { post_field: "hometelephone", json_field: "HOMETELEPHONE", type: "phone", label: _("Home Phone"), rowclasses: "homeworkphone" },
                    { post_field: "worktelephone", json_field: "WORKTELEPHONE", type: "phone", label: _("Work Phone"),  rowclasses: "homeworkphone", colclasses: "nowrap",
                        xmarkup: tableform.render_phone({ justwidget: true, post_field: "worktelephone2", json_field: "WORKTELEPHONE2", classes: "tag-couple" }) },
                    { post_field: "mobiletelephone", json_field: "MOBILETELEPHONE", type: "phone", label: _("Cell Phone"), colclasses: "nowrap",
                        xmarkup: tableform.render_phone({ justwidget: true, post_field: "mobiletelephone2", json_field: "MOBILETELEPHONE2", classes: "tag-couple" }) },
                    { post_field: "emailaddress", json_field: "EMAILADDRESS", type: "text", label: _("Email Address"), colclasses: "nowrap",
                        xmarkup: tableform.render_text({ justwidget: true, post_field: "emailaddress2", json_field: "EMAILADDRESS2", classes: "tag-couple" }) },
                    { post_field: "dateofbirth", json_field: "DATEOFBIRTH", type: "date", label: _("Date Of Birth"), colclasses: "nowrap", rowclasses: "tag-individual tag-couple",
                        xmarkup: tableform.render_date({ justwidget: true, post_field: "dateofbirth2", json_field: "DATEOFBIRTH2", classes: "tag-couple" }) },
                    { post_field: "idnumber", json_field: "IDENTIFICATIONNUMBER", type: "text", label: _("ID Number"),  colclasses: "nowrap", rowclasses: "tag-individual tag-couple",
                        callout: _("Driving license, passport or other identification number"),
                        xmarkup: tableform.render_text({ justwidget: true, post_field: "idnumber2", json_field: "IDENTIFICATIONNUMBER2", classes: "tag-couple" }) },
                    { post_field: "jurisdiction", json_field: "JURISDICTIONID", type: "select", label: _("Jurisdiction"), 
                        options: { displayfield: "JURISDICTIONNAME", rows: controller.jurisdictions }},
                    { post_field: "gdprcontactoptin", json_field: "GDPRCONTACTOPTIN", type: "selectmulti", label: _("GDPR Contact Opt-In"), 
                        options: edit_header.gdpr_contact_options() },
                    { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 7) },

                    { type: "nextcol" },

                    { post_field: "address", json_field: "OWNERADDRESS", type: "textarea", label: _("Address"), classes: "asm-textareafixed", rows: 5},
                    { post_field: "town", json_field: "OWNERTOWN", type: "autotext", label: _("City"), rowclasses: "towncounty", 
                        maxlength: 100, options: controller.towns, minlength: 4 },
                    common.iif(config.bool("USStateCodes"),
                        { post_field: "county", json_field: "OWNERCOUNTY", type: "select", label: _("State"), rowclasses: "towncounty", 
                            options: html.states_us_options(config.str("OrganisationCounty")) },
                        { post_field: "county", json_field: "OWNERCOUNTY", type: "autotext", label: _("State"), rowclasses: "towncounty", 
                            minlength: 3, options: controller.counties }),
                    { post_field: "postcode", json_field: "OWNERPOSTCODE", type: "text", label: _("Zipcode") },
                    { post_field: "country", json_field: "OWNERCOUNTRY", type: "text", label: _("Country") }, 
                    { post_field: "latlong", json_field: "LATLONG", type: "latlong", label: _("Latitude/Longitude"), 
                        callout: _("Right-click on the map to change the marker location") },

                    { type: "nextcol" },

                    { type: "raw", fullrow: true, markup: '<div id="embeddedmap" style="z-index: 1; width: 100%; height: 300px; color: #000"></div>' }

                ], { full_width: true }),
                '</div>'
            ].join("\n");
        },

        render_type: function() {
            return [
                '<h3><a href="#">' + _("Type") + '</a></h3>',
                '<div>',
                tableform.fields_render([ 
                    { post_field: "flags", type: "selectmulti", label: _("Flags") },
                    { post_field: "homecheckedby", json_field: "HOMECHECKEDBY", type: "person", label: _("Homechecked by"), personfilter: "homechecker" },
                    { post_field: "homechecked", json_field: "DATELASTHOMECHECKED", type: "date", label: _("on") }, 
                    { post_field: "membershipnumber", json_field: "MEMBERSHIPNUMBER", type: "text", label: _("Membership Number") },
                    { post_field: "membershipexpires", json_field: "MEMBERSHIPEXPIRYDATE", type: "date", label: _("Membership Expiry") },
                    { post_field: "fostercapacity", json_field: "FOSTERCAPACITY", type: "number", label: _("Foster Capacity"), 
                        callout: _("If this person is a fosterer, the maximum number of animals they can care for.") },
                    { post_field: "accountnumber", json_field: "ACCOUNTNUMBER", type: "text", label: _("Account number")},
                    { post_field: "minimumorder", json_field: "MINIMUMORDER", type: "currency", label: _("Minimum number")},
                    { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 8) },

                    { type: "nextcol" },

                    { post_field: "comments", json_field: "COMMENTS", type: "textarea", label: _("Comments"), rows: 7 },
                    { post_field: "popupwarning", json_field: "POPUPWARNING", type: "textarea", label: _("Warning"), rows: 2,
                        callout: _("Show a warning when viewing this person") }
                ], { full_width: true }),
                '</div>'
            ].join("\n");
        },

        render_homechecker: function() {
            return [
                '<h3 id="accordion-homechecker"><a href="#">' + _("Homechecker") + '</a></h3>',
                '<div>',
                tableform.fields_render([
                    { post_field: "areas", json_field: "HOMECHECKAREAS", type: "textarea", label: _("Homecheck Areas"),
                        rows: 8, labelpos: "above", 
                        callout:_("A list of areas this person will homecheck - eg: S60 S61") },
                    
                    { type: "nextcol" },

                    { type: "raw", fullrow: true, 
                        markup: [
                            '<p class="asm-header"><label>' + _("Homecheck History") + '</label></p>',
                            '<table id="homecheckhistory" width="100%">',
                            '<thead>',
                            '<tr>',
                            '<th>' + _("Date") + '</th>',
                            '<th>' + _("Person") + '</th>',
                            '<th>' + _("Comments") + '</th>',
                            '</tr>',
                            '</thead>',
                            '<tbody>',
                            '</tbody>',
                            '</table>'
                        ].join("\n")
                    }
                ]),
                '</div>'
            ].join("\n");
        },

        render_lookingfor: function() {
            return [
                '<h3 id="accordion-lookingfor"><a href="#">' + _("Looking for") + ' <span id="tabcriteria" style="display: none" class="asm-icon asm-icon-animal"></span></a></h3>',
                '<div>',
                tableform.fields_render([
                    { post_field: "matchactive", json_field: "MATCHACTIVE", type: "select", label: _("Status"), 
                        options: '<option value="0">' + _("Inactive - do not include") + '</option>' +
                            '<option value="1">' + _("Active") + '</option>' },
                    { post_field: "matchadded", json_field: "MATCHADDED", type: "date", label: _("Added"), rowclasses: "lft" },
                    { post_field: "matchexpires", json_field: "MATCHEXPIRES", type: "date", label: _("Expires"), rowclasses: "lft" },
                    { post_field: "matchagedfrom", json_field: "MATCHAGEFROM", type: "number", label: _("Aged From"), rowclasses: "lft" },
                    { post_field: "matchagedto", json_field: "MATCHAGETO", type: "number", label: _("Aged To"), rowclasses: "lft" },
                    { post_field: "matchcommentscontain", json_field: "MATCHCOMMENTSCONTAIN", type: "textarea", 
                        callout: _("Animal comments MUST contain this phrase in order to match."),
                        label: _("Comments Contain"), rows: 5, classes: "asm-textareafixed", rowclasses: "lft" },

                    { type: "nextcol" },

                    { post_field: "matchsex", json_field: "MATCHSEX", type: "select", label: _("Sex"), rowclasses: "lfs", 
                        options: { displayfield: "SEX", rows: controller.sexes, prepend: '<option value="-1">' + _("(any)") + '</option>' }},
                    { post_field: "matchsize", json_field: "MATCHSIZE", type: "select", label: _("Size"), rowclasses: "lfs", 
                        options: { displayfield: "SIZE", rows: controller.sizes, prepend: '<option value="-1">' + _("(any)") + '</option>' }},
                    { post_field: "matchcolour", json_field: "MATCHCOLOUR", type: "select", label: _("Color"), rowclasses: "lfs", 
                        options: { displayfield: "BASECOLOUR", rows: controller.colours, prepend: '<option value="-1">' + _("(any)") + '</option>' }},
                    { post_field: "matchtype", json_field: "MATCHANIMALTYPE", type: "select", label: _("Type"), rowclasses: "lfs", 
                        options: { displayfield: "ANIMALTYPE", rows: controller.animaltypes, prepend: '<option value="-1">' + _("(any)") + '</option>' }},
                    { post_field: "matchspecies", json_field: "MATCHSPECIES", type: "select", label: _("Species"), rowclasses: "lfs", 
                        options: { displayfield: "SPECIESNAME", rows: controller.species, prepend: '<option value="-1">' + _("(any)") + '</option>' }},
                    { post_field: "matchbreed1", json_field: "MATCHBREED", type: "select", label: _("Breed"), rowclasses: "lfs", 
                        options: { displayfield: "BREEDNAME", rows: controller.breeds, prepend: '<option value="-1">' + _("(any)") + '</option>' }},
                    { post_field: "matchbreed2", json_field: "MATCHBREED2", type: "select", label: _("or"), rowclasses: "lfs", 
                        options: { displayfield: "BREEDNAME", rows: controller.breeds, prepend: '<option value="-1">' + _("(any)") + '</option>' }},
                    { post_field: "matchflags", json_field: "MATCHFLAGS", type: "selectmulti", label: _("Flags"), rowclasses: "lfs", 
                        options: { displayfield: "FLAG", valuefield: "FLAG", rows: controller.animalflags }},

                    { type: "nextcol" },

                    { post_field: "matchgoodwithcats", json_field: "MATCHGOODWITHCATS", type: "select", label: _("Good with cats"), rowclasses: "lfs", 
                        options: { displayfield: "NAME", rows: controller.ynun, prepend: '<option value="-1">' + _("(any)") + '</option>' }},
                    { post_field: "matchgoodwithdogs", json_field: "MATCHGOODWITHDOGS", type: "select", label: _("Good with dogs"), rowclasses: "lfs", 
                        options: { displayfield: "NAME", rows: controller.ynun, prepend: '<option value="-1">' + _("(any)") + '</option>' }},
                    { post_field: "matchgoodwithchildren", json_field: "MATCHGOODWITHCHILDREN", type: "select", label: _("Good with children"), rowclasses: "lfs", 
                        options: { displayfield: "NAME", rows: controller.ynunk, prepend: '<option value="-1">' + _("(any)") + '</option>' }},
                    { post_field: "matchgoodwithelderly", json_field: "MATCHGOODWITHELDERLY", type: "select", label: _("Good with elderly"), rowclasses: "lfs", 
                        options: { displayfield: "NAME", rows: controller.ynunk, prepend: '<option value="-1">' + _("(any)") + '</option>' }},
                    { post_field: "matchgoodonlead", json_field: "MATCHGOODONLEAD", type: "select", label: _("Good on lead"), rowclasses: "lfs", 
                        options: { displayfield: "NAME", rows: controller.ynun, prepend: '<option value="-1">' + _("(any)") + '</option>' }},
                    { post_field: "matchgoodtraveller", json_field: "MATCHGOODTRAVELLER", type: "select", label: _("Good traveller"), rowclasses: "lfs", 
                        options: { displayfield: "NAME", rows: controller.ynun, prepend: '<option value="-1">' + _("(any)") + '</option>' }},
                    { post_field: "matchhousetrained", json_field: "MATCHHOUSETRAINED", type: "select", label: _("Housetrained"), rowclasses: "lfs", 
                        options: { displayfield: "NAME", rows: controller.ynun, prepend: '<option value="-1">' + _("(any)") + '</option>' }},
                    { post_field: "matchcratetrained", json_field: "MATCHCRATETRAINED", type: "select", label: _("Crate trained"), rowclasses: "lfs", 
                        options: { displayfield: "NAME", rows: controller.ynun, prepend: '<option value="-1">' + _("(any)") + '</option>' }},
                    { post_field: "matchenergylevel", json_field: "MATCHENERGYLEVEL", type: "select", label: _("Energy level"), 
                        rowclasses: "lfs", options: html.list_to_options([
                            "-1|" + _("(any)"),
                            "1|" + _("1 - Very low"),
                            "2|" + _("2 - Low"),
                            "3|" + _("3 - Medium"),
                            "4|" + _("4 - High"),
                            "5|" + _("5 - Very high") ])
                    },
                    
                ]),
                '</div>'
            ].join("\n");
        },

        render_toolbar: function() {
            return tableform.buttons_render([
                { id: "save", text: _("Save"), icon: "save", tooltip: _("Save this person") },
                { id: "delete", text: _("Delete"), icon: "delete", tooltip: _("Delete this person") },
                { id: "anonymise", text: _("Anonymize"), icon: "delete", tooltip: _("Remove personally identifiable data") },
                { id: "merge", text: _("Merge"), icon: "copy", tooltip: _("Merge another person into this one") },
                { id: "document", text: _("Document"), type: "buttonmenu", icon: "document", tooltip: _("Generate a document from this person") },
                { id: "lookingfor", text: _("Looking For"), icon: "animal-find", tooltip: _("Find animals matching the looking for criteria of this person") },
                { id: "map", text: _("Map"), icon: "map", tooltip: _("Find this address on a map") },
                { id: "email", text: _("Email"), icon: "email", tooltip: _("Email this person") }
            ]);
        },

        render_submenus: function() {
            return [
                '<div id="button-document-body" class="asm-menu-body">',
                '<ul class="asm-menu-list">',
                edit_header.template_list(controller.templates, "PERSON", controller.person.ID),
                '</ul>',
                '</div>',
            ].join("\n");
        },

        render: function() {
            return [
                person.render_submenus(),
                person.render_dialogs(),
                edit_header.person_edit_header(controller.person, "person", controller.tabcounts),
                person.render_toolbar(),
                '<div id="asm-details-accordion">',
                person.render_details(),
                person.render_type(),
                '<h3 id="asm-additional-accordion"><a href="#">' + _("Additional") + '</a></h3>',
                '<div>',
                additional.additional_fields(controller.additional),
                '</div>',
                person.render_homechecker(),
                person.render_lookingfor(),
                html.audit_trail_accordion(controller),
                '</div> <!-- accordion -->',
                '</div> <!-- asmcontent -->',
                '</div> <!-- tabs -->'
            ].join("\n");
        },

        enable_widgets: function() {

            // DATA ===========================================

            // Hide the view roles controls if incident permissions are off
            if (!config.bool("PersonPermissions")) {
                $("#viewrolesrow").hide();
            }

            // If the looking for status is inactive, disable the fields
            if ($("#matchactive").val() == "0") {
                $(".lft").fadeOut();
                $(".lfs").fadeOut();
                $("#button-lookingfor").button("option", "disabled", true);
            }
            else {
                $(".lft").fadeIn();
                $(".lfs").fadeIn();
                $("#button-lookingfor").button("option", "disabled", false);
            }

            // Individual
            if (!$("#ownertype").val() || $("#ownertype").val() == 1) {
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

            // if the member flag is selected and membership number is blank,
            // default the membership number from the person id.
            if ($("#flags option[value='member']").is(":selected")) {
                if (common.trim($("#membershipnumber").val()) == "") {
                    $("#membershipnumber").val( 
                        format.padleft($("#personid").val(), 10));
                }
            }

            if ($("#flags option[value='member']").is(":selected")) {
                $("label[for='membershipnumber']").html(_("Membership Number"));
                $("#membershipnumber").prop("title", _("If this person is a member, their membership number"));
                $("#membershipnumberrow").fadeIn();
                $("#membershipexpiresrow").fadeIn();
            }

            // If the vet flag is selected, change the membership number label
            // and hide the expiry field so we can use membership for licence
            if ($("#flags option[value='vet']").is(":selected")) {
                $("label[for='membershipnumber']").html(_("License Number"));
                $("#membershipnumber").prop("title", _("The veterinary license number."));
                $("#membershipnumberrow").fadeIn();
                $("#membershipexpiresrow").fadeOut();
            }

            // If neither member or vet flag is set, hide the membership number field
            if (!$("#flags option[value='vet']").is(":selected") && !$("#flags option[value='member']").is(":selected")) {
                $("#membershipnumberrow").fadeOut();
                $("#membershipexpiresrow").fadeOut();
            }

            // If the fosterer flag is set, show/hide the fosterer capacity field
            if ($("#flags option[value='fosterer']").is(":selected")) {
                $("#fostercapacityrow").fadeIn();
            }
            else {
                $("#fostercapacityrow").fadeOut();
            }

            // If the supplier flag is set, show/hide the account number and minimum order fields
            if ($("#flags option[value='supplier']").is(":selected")) {
                $("#accountnumberrow").fadeIn();
                $("#minimumorderrow").fadeIn();
            }
            else {
                $("#accountnumberrow").fadeOut();
                $("#minimumorderrow").fadeOut();
            }

            // If the homechecked flag is set, or the option is not on to
            // hide them, show/hide the homechecked by/date fields
            if ($("#flags option[value='homechecked']").is(":selected") || !config.bool("HideHomeCheckedNoFlag")) {
                $("#homecheckedbyrow").fadeIn();
                $("#homecheckedrow").fadeIn();
            }
            else {
                $("#homecheckedbyrow").fadeOut();
                $("#homecheckedrow").fadeOut();
            }

            // Hide the homechecker section if this person isn't a homechecker
            if ($("#flags option[value='homechecker']").is(":selected")) {
                $("#accordion-homechecker").show();
            }
            else {
                $("#accordion-homechecker").hide();
                $("#accordion-homechecker").next().hide();
            }

            // Hide additional accordion section if there aren't
            // any additional fields declared
            let ac = $("#asm-additional-accordion");
            let an = ac.next();
            if (an.find(".additional").length == 0) {
                ac.hide(); an.hide();
            }

            // CONFIG ===========================
            $(".towncounty").toggle( !config.bool("HideTownCounty") );
            $(".homeworkphone").toggle( !config.bool("HideHomeWorkPhone") );
            $("#countryrow").toggle( !config.bool("HideCountry") );
            $("#latlongrow").toggle( config.bool("ShowLatLong") );
            $("#siterow").toggle( config.bool("MultiSiteEnabled") );
            $("#jurisdictionrow").toggle( !config.bool("DisableAnimalControl") );
            $("#dateofbirthrow").toggle( !config.bool("HidePersonDateOfBirth") );
            $("#idnumberrow").toggle( !config.bool("HideIDNumber") );
            $("#button-anonymise").toggle( config.bool("AnonymisePersonalData") );
            $("#gdprcontactoptinrow").toggle( config.bool("ShowGDPRContactOptIn") );
            $("#button-lookingfor").toggle( !config.bool("HideLookingFor") );
            if (config.bool("HideLookingFor")) {
                $("#accordion-lookingfor").hide();
                $("#accordion-lookingfor").next().hide();
            }

            // SECURITY =============================================================
            if (!common.has_permission("co")) { $("#button-save, #button-anonymise").hide(); }
            if (!common.has_permission("do")) { $("#button-delete, #button-anonymise").hide(); }
            if (!common.has_permission("gaf")) { $("#button-document").hide(); }
            if (!common.has_permission("mo")) { $("#button-merge").hide(); }

            // ACCORDION ICONS =======================================================

        },

        validation: function() {

            // Remove any previous errors
            header.hide_error();
            validate.reset();

            // name
            if (common.trim($("#surname").val()) == "") {
                header.show_error(_("Name cannot be blank"));
                $("#asm-details-accordion").accordion("option", "active", 0);
                validate.highlight("surname");
                return false;
            }

            // email
            if (common.trim($("#emailaddress").val()) != "") {
                if (!validate.email($("#emailaddress").val())) {
                    header.show_error(_("Invalid email address '{0}'").replace("{0}", $("#emailaddress").val()));
                    validate.highlight("emailaddress");
                    return false;
                }
            }

            // email2
            if (common.trim($("#emailaddress2").val()) != "") {
                if (!validate.email($("#emailaddress2").val())) {
                    header.show_error(_("Invalid email address '{0}'").replace("{0}", $("#emailaddress2").val()));
                    validate.highlight("emailaddress");
                    return false;
                }
            }

            // any additional fields that are marked mandatory
            if (!additional.validate_mandatory()) {
                return false;
            }

            return true;
        },

        get_map_url: function() {
            let add = $("#address").val().replace("\n", ",");
            let town = $("#town").val();
            let county = $("#county").val();
            let postcode = $("#postcode").val();
            let map = add;
            if (town != "") { map += "," + town; }
            if (county != "") { map += "," + county; }
            if (postcode != "") { map += "," + postcode; }
            map = encodeURIComponent(map);
            return map;
        },

        show_popup_warning: async function() {
            if (controller.person.POPUPWARNING) {
                await tableform.show_okcancel_dialog("#dialog-popupwarning", _("Ok"), { hidecancel: true });
            }
        },

        bind: function() {

            // Load the tab strip and accordion
            $(".asm-tabbar").asmtabs();
            $("#asm-details-accordion").accordion({
                heightStyle: "content"
            }); 

            // Setup the document menu button
            $("#button-document").asmmenu();
            
            // Email dialog for sending emails
            $("#emailform").emailform();

            // Set the county field when leaving town
            $("#town").blur(function() {
                if ($("#county").val() == "") {
                    $("#county").val(controller.towncounties[$("#town").val()]);
                }
            });

            // Controls that update the screen when changed
            $("#ownertype").change(person.enable_widgets);
            $("#matchactive").change(person.enable_widgets);
            $("#flags").change(person.enable_widgets);

            validate.save = function(callback) {
                if (!person.validation()) { header.hide_loading(); return; }
                validate.dirty(false);
                let formdata = "mode=save" +
                    "&id=" + $("#personid").val() + 
                    "&recordversion=" + controller.person.RECORDVERSION + 
                    "&" + $("input, select, textarea").not(".chooser").toPOST();
                common.ajax_post("person", formdata)
                    .then(callback)
                    .fail(function() { 
                        validate.dirty(true); 
                    });
            };

           // Toolbar buttons
            $("#button-save").button().click(function() {
                header.show_loading(_("Saving..."));
                validate.save(function() {
                    common.route_reload();
                });
            });

            $("#button-anonymise").button().click(function() {
                $("#title, #initials, #forenames, #address, #email, #hometelephone, #worktelephone, #mobiletelephone").val("");
                $("#surname").val(_("No longer retained"));
                validate.dirty(true);
            });

            $("#button-delete").button().click(async function() {
                await tableform.delete_dialog(null, _("This will permanently remove this person, are you sure?"));
                let formdata = "mode=delete&personid=" + $("#personid").val();
                await common.ajax_post("person", formdata);
                validate.dirty(false);
                common.route("main"); 
            });

            $("#button-merge").button().click(function() {
                let mb = {}; 
                mb[_("Merge")] = async function() { 
                    $("#dialog-merge").dialog("close");
                    let formdata = "mode=merge&personid=" + $("#personid").val() + "&mergepersonid=" + $("#mergeperson").val();
                    await common.ajax_post("person", formdata);
                    validate.dirty(false);
                    common.route_reload(); 
                };
                mb[_("Cancel")] = function() { $(this).dialog("close"); };
                $("#dialog-merge").dialog({
                     width: 600,
                     resizable: false,
                     modal: true,
                     dialogClass: "dialogshadow",
                     show: dlgfx.delete_show,
                     hide: dlgfx.delete_hide,
                     buttons: mb
                });
            });

            $("#button-lookingfor").button().click(function() {
                validate.save(function() {
                    common.route("person_lookingfor?ajax=false&personid=" + controller.person.ID);
                });
            });

            $("#button-email").button().click(function() {
                let email = $("#emailaddress").val(), email2 = $("#emailaddress2").val();
                if (email2) { email += ", " + email2; }
                $("#emailform").emailform("show", {
                    post: "person",
                    formdata: "mode=email&personid=" + $("#personid").val(),
                    name: $("#forenames").val() + " " + $("#surname").val(),
                    email: email,
                    logtypes: controller.logtypes,
                    personid: controller.person.ID,
                    templates: controller.templatesemail
                });
            });

        },

        sync: function() {

            // Load the data into the controls for the screen
            $("#asm-content input, #asm-content select, #asm-content textarea").fromJSON(controller.person);

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");

            // Update the lat/long
            $(".asm-latlong").latlong("load");

            // Load person flags
            html.person_flag_options(controller.person, controller.flags, $("#flags"));

            // Load homecheck history
            let h = [];
            $.each(controller.homecheckhistory, function(i, v) {
                h.push("<tr>");
                h.push('<td class="centered">' + format.date(v.DATELASTHOMECHECKED) + '</td>');
                h.push('<td class="centered"><a class="asm-embed-name" href="person?id=' + v.ID + '">' + v.OWNERNAME + '</a></td>');
                h.push('<td class="centered">' + v.COMMENTS + '</td>');
                h.push('</tr>');
            });
            $("#homecheckhistory tbody").html(h.join("\n"));

            // Update on-screen fields from the data and display the screen
            person.enable_widgets();

            // Map button
            $("#button-map").button().click(function() {
                let mapq = person.get_map_url();
                let maplinkref = String(asm.maplink).replace("{0}", mapq);
                window.open(maplinkref, "_blank");
            });

            // Dirty handling
            validate.bind_dirty([ "person_" ]);

            // If a popup warning has been set, display it
            person.show_popup_warning();

        },

        delay: function() {
            if (config.bool("ShowPersonMiniMap")) {
                mapping.draw_map("embeddedmap", 15, controller.person.LATLONG, [{ 
                    latlong: controller.person.LATLONG, popuptext: controller.person.OWNERADDRESS, popupactive: true }]);
            }
        },

        destroy: function() {
            validate.unbind_dirty();
            common.widget_destroy("#dialog-merge");
            common.widget_destroy("#dialog-popupwarning");
            common.widget_destroy("#emailform");
            common.widget_destroy("#mergeperson", "personchooser");
            common.widget_destroy("#homecheckedby", "personchooser");
        },

        name: "person",
        animation: "formtab",
        autofocus: "#ownertype",
        title: function() { return controller.person.OWNERCODE + ' - ' + controller.person.OWNERNAME; },
        routes: {
            "person": function() { common.module_loadandstart("person", "person?id=" + this.qs.id); }
        }

    };

    common.module_register(person);

});
