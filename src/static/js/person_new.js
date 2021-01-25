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
                '<table class="asm-table-layout">',
                '<tr>',
                '<td><label for="ownertype">' + _("Class") + '</label></td>',
                '<td><select id="ownertype" data="ownertype" class="asm-selectbox">',
                '<option value="1">' + _("Individual/Couple") + '</option>',
                '<option value="2">' + _("Organization") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr class="tag-individual">',
                '<td><label for="title">' + _("Title") + '</label></td>',
                '<td><input class="asm-textbox newform" maxlength="50" id="title" data="title" type="text" /></td>',
                '</tr>',
                '<tr class="tag-individual">',
                '<td><label for="initials">' + _("Initials") + '</label></td>',
                '<td><input class="asm-textbox newform" maxlength="50" id="initials" data="initials" type="text" /></td>',
                '</tr>',
                '<tr class="tag-individual">',
                '<td><label for="forenames">' + _("First name(s)") + '</label></td>',
                '<td><input class="asm-textbox newform" maxlength="200" id="forenames" data="forenames" type="text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="surname" class="tag-individual">' + _("Last name") + '</label>',
                '<label for="surname" class="tag-organisation">' + _("Organization name") + '</label></td>',
                '<td><input class="asm-textbox newform" maxlength="100" id="surname" data="surname" type="text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="address">' + _("Address") + '</label></td>',
                '<td><textarea class="asm-textareafixed newform" id="address" data="address" rows="3"></textarea></td>',
                '</tr>',
                '<tr class="towncounty">',
                '<td><label for="town">' + _("City") + '</label></td>',
                '<td><input class="asm-textbox newform" maxlength="100" id="town" data="town" type="text" /></td>',
                '</tr>',
                '<tr class="towncounty">',
                '<td><label for="county">' + _("State") + '</label></td>',
                '<td>',
                common.iif(config.bool("USStateCodes"),
                    '<select id="county" data="county" class="asm-selectbox newform">' +
                    html.states_us_options(config.str("OrganisationCounty")) + '</select>',
                    '<input type="text" id="county" data="county" maxlength="100" class="asm-textbox newform" />'),
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="postcode">' + _("Zipcode") + '</label></td>',
                '<td><input class="asm-textbox newform" id="postcode" data="postcode" type="text" /></td>',
                '</tr>',
                '<tr id="countryrow">',
                '<td><label for="country">' + _("Country") + '</label></td>',
                '<td><input class="asm-textbox newform" id="country" data="country" type="text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="hometelephone">' + _("Home Phone") + '</label></td>',
                '<td><input class="asm-textbox asm-phone newform" id="hometelephone" data="hometelephone" type="text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="worktelephone">' + _("Work Phone") + '</label></td>',
                '<td><input class="asm-textbox asm-phone newform" id="worktelephone" data="worktelephone" type="textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="mobiletelephone">' + _("Cell Phone") + '</label></td>',
                '<td><input class="asm-textbox asm-phone newform" id="mobiletelephone" data="mobiletelephone" type="textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="emailaddress">' + _("Email Address") + '</label></td>',
                '<td><input class="asm-textbox newform" maxlength="200" id="emailaddress" data="emailaddress" type="textbox" /></td>',
                '</tr>',
                '<tr id="jurisdictionrow">',
                '<td><label for="jurisdiction">' + _("Jurisdiction") + '</label></td>',
                '<td>',
                '<select id="jurisdiction" data="jurisdiction" class="asm-selectbox">',
                html.list_to_options(controller.jurisdictions, "ID", "JURISDICTIONNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="flags">' + _("Flags") + '</label></td>',
                '<td>',
                '<select id="flags" data="flags" class="asm-bsmselect" multiple="multiple">',
                '</select>',
                '</td>',
                '</tr>',
                '<tr id="gdprcontactoptinrow">',
                '<td><label for="gdprcontactoptin">' + _("GDPR Contact Opt-In") + '</label></td>',
                '<td>',
                '<select id="gdprcontactoptin" data-json="GDPRCONTACTOPTIN" data-post="gdprcontactoptin" class="asm-bsmselect" multiple="multiple">',
                edit_header.gdpr_contact_options(),
                '</select>',
                '</td>',
                '</tr>',
                '<tr id="siterow">',
                '<td><label for="site">' + _("Site") + '</label></td>',
                '<td>',
                '<select id="site" data="site" class="asm-selectbox">',
                '<option value="0">' + _("(all)") + '</option>',
                html.list_to_options(controller.sites, "ID", "SITENAME"),
                '</select>',
                '</td>',
                '</tr>',
                additional.additional_new_fields(controller.additional),
                '</table>',
                '<input id="latlong" data="latlong" type="hidden" value="" />',
                '<div class="centered">',
                '<button id="addedit">' + html.icon("person-add") + ' ' + _("Create and edit") + '</button>',
                '<button id="add">' + html.icon("person-add") + ' ' + _("Create") + '</button>',
                '<button id="reset">' + html.icon("delete") + ' ' + _("Reset") + '</button>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            const validation = function() {
                // Remove any previous errors
                header.hide_error();
                validate.reset();
                if (!validate.notblank([ "surname" ])) { return false; }
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
                if (rec === undefined) {
                    add_person();
                }
                else {
                    let disp = "<span class=\"justlink\"><a class=\"asm-embed-name\" href=\"person?id=" + rec.ID + "\">" + rec.OWNERNAME + "</a></span>";
                    disp += "<br/>" + rec.OWNERADDRESS + "<br/>" + rec.OWNERTOWN + "<br/>" + rec.OWNERCOUNTY + "<br/>" + rec.OWNERPOSTCODE + "<br/>" + rec.HOMETELEPHONE + "<br/>" + rec.WORKTELEPHONE + "<br/>" + rec.MOBILETELEPHONE + "<br/>" + rec.EMAILADDRESS;
                    $(".similar-person").html(disp);
                    similar_dialog();
                }
            };

            const check_org = function() {
                // If it's an organisation, only show the org fields,
                // otherwise show individual
                if ($("#ownertype").val() == 2) {
                    $(".tag-organisation").fadeIn();
                    $(".tag-individual").fadeOut();
                }
                else {
                    $(".tag-organisation").fadeOut();
                    $(".tag-individual").fadeIn();
                }
            };

            $("#ownertype").change(check_org);
            check_org();

            // Load the person flag options
            html.person_flag_options(null, controller.flags, $("#flags"));

            if (config.bool("HideTownCounty")) {
                $(".towncounty").hide();
            }

            $("#countryrow").toggle( !config.bool("HideCountry") );

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

            $("#town").autocomplete({ source: controller.towns });
            $("#town").blur(function() {
                if ($("#county").val() == "") {
                    $("#county").val(controller.towncounties[$("#town").val()]);
                }
            });
            if (!config.bool("USStateCodes")) { $("#county").autocomplete({ source: controller.counties }); }

            $("#add").button().click(function() {
                person_new.create_and_edit = false;
                $("#asm-content button").button("disable");
                check_for_similar();
            });

            $("#addedit").button().click(function() {
                person_new.create_and_edit = true;
                $("#asm-content button").button("disable");
                check_for_similar();
            });


            $("#reset").button().click(function() {
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
