/*global $, console, jQuery */
/*global _, asm, asm_widget, additional, common, config, dlgfx, edit_header, format, html, header, log, validate, escape, unescape */

"use strict";

/**
 * Person chooser widget. To create one, use a hidden input
 * with a class of asm-personchooser. You can also specify
 * a data-filter attribute to only search certain types of person
 * records.
 *     
 *     data-filter: all | vet | retailer | staff | fosterer | volunteer | shelter | 
 *                  aco | homechecked | homechecker | member | donor
 *     data-type:   all | individual | organization
 *     data-mode:   full | brief (full shows the address and other info, 
 *                  brief just shows the name)
 *
 * <input id="person" data-mode="full" data-filter="vet" class="asm-personchooser" data="boundfield" type="hidden" value="initialid" />
 * 
 * Local data() elements:
 * 
 *      node: Node containing the div with the displayed element
 *      dialog: The popup find dialog node
 *      dialogadd: The popup add person dialog node
 *      dialogsimilar: The popup similar person dialog node
 *      display: The node that displays the selected person
 *      title: The dialog title when finding (Find Person)
 *      addtitle: The dialog title when adding (Add Person)
 *      filter: A string containing the filter
 *      type: A string containing the type of person records to search
 *      mode: A string containing the mode the widget is operating in (brief or full)
 *      nonshelter: A boolean, true if the nonshelter flag should be set when adding animals
 *      selected: The selected animal record (a dict of values from the backend)
 *      additionalfields: Recordset of additional field definitions for people
 *
 * events: loaded (after loadbyid is complete)
 *         change (after user has clicked on a new selection)
 *         cleared (after user clicks the clear button)
 */
$.fn.personchooser = asm_widget({

    _create: function(t) {
        let self = this;
        t.data("mode", t.attr("data-mode"));
        if (!t.data("mode")) { t.data("mode", "full"); }
        t.data("type", t.attr("data-type"));
        if (!t.data("type")) { t.data("type", "all"); }
        self.set_type.call(self, t, t.data("type")); 
        t.data("filter", t.attr("data-filter"));
        if (!t.data("filter")) { t.data("filter", "all"); }
        self.set_filter.call(self, t, t.data("filter")); 
        let h = [
            '<div class="personchooser asm-chooser-container">',
            '<input class="personchooser-banned" type="hidden" value="" />',
            '<input class="personchooser-postcode" type="hidden" value = "" />',
            '<input class="personchooser-idcheck" type="hidden" value = "" />',
            '<div class="personchooser-noperm" style="display: none">' + _("Forbidden") + '</div>',
            '<table class="personchooser-perm" style="margin-left: 0px; margin-right: 0px; width: 100%; ">',
            '<tr>',
            '<td class="personchooser-display"></td>',
            '<td valign="top" style="text-align: end; white-space: nowrap">',
            '<button class="personchooser-link-find">' + _("Select a person") + '</button>',
            '<button class="personchooser-link-new">' + _("Add a person") + '</button>',
            '<button class="personchooser-link-clear">' + _("Clear") + '</button>',
            '</td>',
            '</tr>',
            '</table>',
            '<div class="personchooser-similar" style="display: none" title="' + html.title(_("Similar Person")) + '">',
                '<p><span class="ui-icon ui-icon-alert"></span>',
                _("This person is very similar to another person on file, carry on creating this record?"),
                '<br /><br />',
                '<span class="similar-person"></span>',
                '</p>',
            '</div>',
            '<div class="personchooser-find" style="display: none" title="' + t.data("title") + '">',
            '<input class="asm-textbox" type="text" />',
            '<button>' + _("Search") + '</button>',
            '<img style="height: 16px" src="static/images/wait/rolling_3a87cd.svg" />',
            '<table width="100%">',
            '<thead>',
                '<tr class="ui-widget-header">',
                    '<th>' + _("Name") + '</th>',
                    '<th>' + _("Code") + '</th>',
                    '<th>' + _("Address") + '</th>',
                    '<th>' + _("City") + '</th>',
                    '<th>' + _("State") + '</th>',
                    '<th>' + _("Zipcode") + '</th>',
                    (!config.bool("HideCountry") ? '<th>' + _("Country") + '</th>' : ""),
                '</tr>',
            '</thead>',
            '<tbody></tbody>',
            '</table>',
            '</div>',
            '<div class="personchooser-add" style="display: none" title="' + t.data("addtitle") + '">',
            '<table width="100%" class="chooser-addfields">',
            '<tr>',
            '<td><label>' + _("Class") + '</label></td>',
            '<td><select data="ownertype" class="asm-selectbox chooser">',
            '<option value="1">' + _("Individual") + '</option>',
            '<option value="3">' + _("Couple") + '</option>',
            '<option value="2">' + _("Organization") + '</option>',
            '</select></td>',
            '</tr>',
            '<tr class="tag-individual">',
            '<td><label>' + _("Title") + '</label></td>',
            '<td><input class="asm-textbox chooser" data="title" type="text" />',
            '<input class="asm-textbox chooser tag-couple" data="title2" type="text" /></td>',
            '</tr>',
            '<tr class="tag-individual">',
            '<td><label>' + _("Initials") + '</label></td>',
            '<td><input class="asm-textbox chooser" maxlength="50" data="initials" type="text" />',
            '<input class="asm-textbox chooser tag-couple" maxlength="50" data="initials2" type="text" /></td>',
            '</tr>',
            '<tr class="tag-individual">',
            '<td><label>' + _("First name(s)") + '</label></td>',
            '<td><input class="asm-textbox chooser" maxlength="200" data="forenames" type="text" />',
            '<input class="asm-textbox chooser tag-couple" maxlength="200" data="forenames2" type="text" /></td>',
            '</tr>',
            '<tr>',
            '<td><label class="tag-individual">' + _("Last name") + '</label>',
            '<label class="tag-organisation">' + _("Organization name") + '</label>',
            '<span class="asm-has-validation">*</span>',
            '</td>',
            '<td><input class="asm-textbox chooser" maxlength="100" data="surname" type="text" />',
            '<input class="asm-textbox chooser tag-couple" maxlength="100" data="surname2" type="text" /></td>',
            '</tr>',
            '<tr>',
            '<td><label>' + _("Address") + '</label></td>',
            '<td><textarea class="asm-textareafixed chooser personchooser-address" data="address" rows="3"></textarea></td>',
            '</tr>',
            '<tr class="personchooser-towncountyrow">',
            '<td><label>' + _("City") + '</label></td>',
            '<td><input class="asm-textbox chooser personchooser-town" maxlength="100" data="town" type="text" /></td>',
            '</tr>',
            '<tr class="personchooser-towncountyrow">',
            '<td><label>' + _("State") + '</label></td>',
            '<td>',
            common.iif(config.bool("USStateCodes"),
                '<select data="county" class="asm-selectbox chooser personchooser-county">' +
                html.states_us_options(config.str("OrganisationCounty")) + '</select>',
                '<input type="text" data="county" maxlength="100" class="asm-textbox chooser personchooser-county" />'),
            '</td>',
            '</tr>',
            '<tr>',
            '<td><label>' + _("Zipcode") + '</label></td>',
            '<td><input class="asm-textbox chooser personchooser-postcode" data="postcode" type="text" />',
            '<button class="personchooser-postcodelookup">' + _("Lookup Address") + '</button>',
            '</td>',
            '</tr>',
            '<tr class="personchooser-countryrow">',
            '<td><label>' + _("Country") + '</label></td>',
            '<td><input class="asm-textbox chooser personchooser-country" data="country" type="text" /></td>',
            '</tr>',
            '<tr class="personchooser-homeworkphonerow">',
            '<td><label>' + _("Home Phone") + '</label></td>',
            '<td><input class="asm-textbox asm-phone chooser" data="hometelephone" type="text" /></td>',
            '</tr>',
            '<tr class="personchooser-homeworkphonerow">',
            '<td><label>' + _("Work Phone") + '</label></td>',
            '<td><input class="asm-textbox asm-phone chooser" data="worktelephone" type="text" />',
            '<input class="asm-textbox asm-phone chooser tag-couple" data="worktelephone2" type="text" /></td>',
            '</tr>',
            '<tr>',
            '<td><label>' + _("Cell Phone") + '</label></td>',
            '<td><input class="asm-textbox asm-phone chooser" data="mobiletelephone" type="text" />',
            '<input class="asm-textbox asm-phone chooser tag-couple" data="mobiletelephone2" type="text" /></td>',
            '</tr>',
            '<tr>',
            '<td><label>' + _("Email Address") + '</label></td>',
            '<td><input class="asm-textbox chooser" maxlength="200" data="emailaddress" type="text" />',
            '<input class="asm-textbox chooser tag-couple" maxlength="200" data="emailaddress2" type="text" /></td>',
            '</tr>',
            '<tr class="personchooser-dateofbirthrow">',
            '<td><label>' + _("Date Of Birth") + '</label></td>',
            '<td><input type="text" data="dateofbirth" class="asm-textbox asm-datebox chooser" />',
            '<input type="text" data="dateofbirth2" class="asm-textbox asm-datebox chooser tag-couple" />',
            '</td>',
            '</tr>',
            '<tr class="personchooser-idnumberrow">',
            '<td><label>' + _("ID Number") + '</label></td>',
            '<td><input type="text" data="idnumber" class="asm-textbox chooser" />',
            '<input type="text" data="idnumber2" class="asm-textbox chooser tag-couple" />',
            '</td>',
            '</tr>',
            '<tr>',
            '<tr class="personchooser-jurisdictionrow">',
            '<td><label>' + _("Jurisdiction") + '</label></td>',
            '<td>',
            '<select data="jurisdiction" class="asm-selectbox chooser personchooser-jurisdiction">',
            '</select>',
            '</td>',
            '</tr>',
            '<tr>',
            '<td><label>' + _("Flags") + '</label></td>',
            '<td>',
            '<select class="personchooser-flags chooser" data="flags" multiple="multiple">',
            '</select>',
            '</td>',
            '</tr>',
            '<tr class="personchooser-gdprrow">',
            '<td><label>' + _("GDPR Contact Opt-In") + '</label></td>',
            '<td>',
            '<select class="personchooser-gdpr chooser" data="gdprcontactoptin" multiple="multiple">',
            edit_header.gdpr_contact_options(),
            '</select>',
            '</td>',
            '</tr>',
            '<tr class="personchooser-siterow">',
            '<td><label>' + _("Site") + '</label></td>',
            '<td>',
            '<select class="asm-selectbox chooser personchooser-site" data="site">',
            '</select>',
            '</td>',
            '</tr>',
            '</table>',
            '</div>',
            '</div>'
        ].join("\n");
        
        let node = $(h);
        let dialog = node.find(".personchooser-find");
        let dialogadd = node.find(".personchooser-add");
        let dialogsimilar = node.find(".personchooser-similar");
        let display = node.find(".personchooser-display");
        t.data("node", node);
        t.data("dialog", dialog);
        t.data("dialogadd", dialogadd);
        t.data("dialogsimilar", dialogsimilar);
        t.data("display", display);

        // Start with nothing selected
        t.data("selected", null);

        t.parent().append(node); // TODO: could this be t.after() ?

        // Disable based on view person permission
        if (!common.has_permission("vo")) {
            node.find(".personchooser-perm").hide();
            node.find(".personchooser-noperm").show();
        }

        // Hide sites for non-multi-site
        if (!config.bool("MultiSiteEnabled")) {
            dialogadd.find(".personchooser-siterow").hide();
        }

        // Hide jurisdictions for no animal control
        if (config.bool("DisableAnimalControl")) {
            dialogadd.find(".personchooser-jurisdictionrow").hide();
        }

        // Hide dob/id number
        if (config.bool("HidePersonDateOfBirth")) {
            dialogadd.find(".personchooser-dateofbirthrow").hide();
        }
        if (config.bool("HideIDNumber")) {
            dialogadd.find(".personchooser-idnumberrow").hide();
        }

        // Hide country if option set
        if (config.bool("HideCountry")) {
            dialogadd.find(".personchooser-countryrow").hide();
        }

        if (config.bool("HideTownCounty")) {
            dialogadd.find(".personchooser-towncountyrow").hide();
        }

        if (config.bool("HideHomeWorkPhone")) {
            dialogadd.find(".personchooser-homeworkphonerow").hide();
        }

        // Hide GDPR if option not on
        if (!config.bool("ShowGDPRContactOptIn")) {
            dialogadd.find(".personchooser-gdprrow").hide();
        }
        
        // Create the find dialog
        let pcbuttons = {};
        pcbuttons[_("Cancel")] = function() { $(this).dialog("close"); };
        dialog.dialog({
            autoOpen: false,
            height: common.vheight(600),
            width: common.vwidth(800),
            modal: true,
            dialogClass: "dialogshadow",
            show: dlgfx.edit_show,
            hide: dlgfx.edit_hide,
            buttons: pcbuttons
        });
        dialog.find("table").table({ sticky_header: false });
        dialog.find("input").keydown(function(event) { if (event.keyCode == 13) { self.find.call(self, t); return false; }});
        dialog.find("button").button().click(function() { self.find.call(self, t); });
        dialog.find("img").hide();
        
        // Create the add dialog
        let check_org = function() {
            // Individual
            if (dialogadd.find("[data='ownertype']").val() == 1) {
                dialogadd.find(".tag-organisation").fadeOut();
                dialogadd.find(".tag-couple").fadeOut();
                dialogadd.find(".tag-individual").fadeIn();
            }
            // Organisation
            else if (dialogadd.find("[data='ownertype']").val() == 2) {
                dialogadd.find(".tag-couple").fadeOut();
                dialogadd.find(".tag-individual").fadeOut();
                dialogadd.find(".tag-organisation").fadeIn();
            }
            // Couple
            else if (dialogadd.find("[data='ownertype']").val() == 3) {
                dialogadd.find(".tag-organisation").fadeOut();
                dialogadd.find(".tag-individual").fadeIn();
                dialogadd.find(".tag-couple").fadeIn();
            }
        };
        // change ownertype to organization
        if (t.attr("data-type") == "organization") {
            dialogadd.find("[data='ownertype']").val(2);
        }
        dialogadd.find("[data='ownertype']").change(check_org);
        
        let pcaddbuttons = {};
        pcaddbuttons[_("Create this person")] = function() {
            let valid = true, dialogadd = t.data("dialogadd");
            // Validate fields that can't be blank
            dialogadd.find("label").removeClass(validate.ERROR_LABEL_CLASS);
            dialogadd.find("input[data='surname']").each(function() {
                if (common.trim($(this).val()) == "") {
                    $(this).parent().parent().find("label").addClass(validate.ERROR_LABEL_CLASS);
                    $(this).focus();
                    valid = false;
                    return false;
                }
            });
            if (!valid) { return; }
            if (!additional.validate_mandatory_node(dialogadd)) { return; }
            // Disable the dialog buttons before we make any ajax requests
            dialogadd.disable_dialog_buttons();
            // check for similar people
            self.check_similar.call(self, t);
        };
        pcaddbuttons[_("Cancel")] = function() {
            $(this).dialog("close");
        };

        dialogadd.dialog({
            autoOpen: false,
            width: 600,
            modal: true,
            dialogClass: "dialogshadow",
            show: dlgfx.add_show,
            hide: dlgfx.add_hide,
            buttons: pcaddbuttons,
            open: function() {
                check_org();
                // If we're in multi site mode, use the active user's site
                if (config.bool("MultiSiteEnabled")) {
                    dialogadd.find(".personchooser-site").select("value", asm.siteid);
                }
                // Default the country
                dialogadd.find(".personchooser-country").val(config.str("OrganisationCountry"));
                // Default the jurisdiction
                dialogadd.find(".personchooser-jurisdiction").select("value", config.str("DefaultJurisdiction"));
                // Postcode lookup button
                dialogadd.find(".personchooser-postcodelookup")
                    .button({ icons: { primary: "ui-icon-search" }, text: false })
                    .click(async function() {
                        let country = dialogadd.find(".personchooser-country").val();
                        let postcode = dialogadd.find(".personchooser-postcode").val();
                        if (!postcode) { return; }
                        if (!country) { country = config.str("OrganisationCountry"); }
                        let formdata = "mode=postcodelookup&country=" + country + "&postcode=" + postcode + "&locale=" + asm.locale + "&account=" + asm.useraccount;
                        const response = await common.ajax_post("person_embed", formdata);
                        const rows = jQuery.parseJSON(response);
                        dialogadd.find(".personchooser-address").val( rows[0].street );
                        dialogadd.find(".personchooser-town").val( rows[0].town );
                        dialogadd.find(".personchooser-county").val( rows[0].county );
                    });
                // Change additional fields to default
                additional.reset_default(t.data("additionalfields"));
                // If we have a filter, set the appropriate person flags to match
                if (t.data("filter")) {
                    dialogadd.find(".personchooser-flags option[value='" + t.data("filter") + "']").prop("selected", true);
                    dialogadd.find(".personchooser-flags").change();
                }
            },
            close: function() {
                dialogadd.find("input, textarea").val("");
                dialogadd.find(".personchooser-flags option").prop("selected", false);
                dialogadd.find(".personchooser-flags").change();
                dialogadd.find(".personchooser-gdpr option").prop("selected", false);
                dialogadd.find(".personchooser-gdpr").change();
                dialogadd.find("label").removeClass(validate.ERROR_LABEL_CLASS);
                dialogadd.enable_dialog_buttons();
            }
        });

        node.find(".personchooser-link-find")
            .button({ icons: { primary: "ui-icon-search" }, text: false })
            .click(function() {
                dialog.dialog("open");
            });
        
        node.find(".personchooser-link-new")
            .button({ icons: { primary: "ui-icon-plus" }, text: false })
            .click(function() {
                dialogadd.dialog("open");
            });
        
        node.find(".personchooser-link-clear")
            .button({ icons: { primary: "ui-icon-trash" }, text: false })
            .click(function() {
                self.clear.call(self, t, true);
            });

        /// Go to the backend to get the additional fields, towns, counties and person flags with lookup data
        $.ajax({
            type: "GET",
            url:  "person_embed",
            cache: true, // this data can be cached for a few minutes
            data: { mode: "lookup" },
            dataType: "text",
            success: function(data, textStatus, jqXHR) {
                let h = "";
                let d = jQuery.parseJSON(data);
                t.data("additionalfields", d.additional);
                // Add person flag options to the screen
                html.person_flag_options(null, d.flags, dialogadd.find(".personchooser-flags"));
                // Setup autocomplete widgets with the towns/counties
                dialogadd.find(".personchooser-town").autocomplete({ source: d.towns, minLength: 4 });
                if (!config.bool("USStateCodes")) {
                    dialogadd.find(".personchooser-county").autocomplete({ source: d.counties, minLength: 3 });
                }
                // Toggle visibility of postcode lookup
                dialogadd.find(".personchooser-postcodelookup").toggle( d.postcodelookup );
                // When the user changes a town, suggest a county if it's blank
                dialogadd.find(".personchooser-town").blur(function() {
                    if (dialogadd.find(".personchooser-county").val() == "" && dialogadd.find(".personchooser-town").val() != "") {
                        dialogadd.find(".personchooser-county").val(d.towncounties[dialogadd.find(".personchooser-town").val()]);
                    }
                });
                // Setup person flag select widget
                dialogadd.find(".personchooser-flags").attr("title", _("Select"));
                dialogadd.find(".personchooser-flags").asmSelect({
                    animate: true,
                    sortable: true,
                    removeLabel: '<strong>X</strong>',
                    listClass: 'bsmList-custom',  
                    listItemClass: 'bsmListItem-custom',
                    listItemLabelClass: 'bsmListItemLabel-custom',
                    removeClass: 'bsmListItemRemove-custom'
                });
                // Setup GDPR select widget
                dialogadd.find(".personchooser-gdpr").attr("title", _("Select"));
                dialogadd.find(".personchooser-gdpr").asmSelect({
                    animate: true,
                    sortable: true,
                    removeLabel: '<strong>X</strong>',
                    listClass: 'bsmList-custom',  
                    listItemClass: 'bsmListItem-custom',
                    listItemLabelClass: 'bsmListItemLabel-custom',
                    removeClass: 'bsmListItemRemove-custom'
                });
                // Setup phone number widgets
                dialogadd.find(".asm-phone").phone();
                // Add sites
                dialogadd.find(".personchooser-site").html('<option value="0">' + _("(all)") + '</option>' + 
                    html.list_to_options(d.sites, "ID", "SITENAME"));
                // Add jurisdictions
                dialogadd.find(".personchooser-jurisdiction").html(html.list_to_options(d.jurisdictions, "ID", "JURISDICTIONNAME"));
                dialogadd.find(".personchooser-jurisdiction").select();
                dialogadd.find(".personchooser-jurisdiction").select("value", config.str("DefaultJurisdiction"));
                dialogadd.find(".personchooser-jurisdiction").select("removeRetiredOptions", "all");
                // Add new additional fields
                dialogadd.find(".chooser-addfields").append(additional.additional_new_fields(d.additional, false, "additional chooser"));
                // Bind additional fields that are themselves embedded choosers
                // NOTE: We count how many times we have been embedded via parent classes to stop infinite recursion
                if (common.count_parents_with_class(node, "chooser-addfields") < 1) {
                    dialogadd.find(".asm-animalchooser").animalchooser();
                    dialogadd.find(".asm-animalchoosermulti").animalchoosermulti();
                    dialogadd.find(".asm-personchooser").personchooser();
                }
                // Hide retired options from the lookups
                dialogadd.find(".asm-selectbox").select("removeRetiredOptions", "all");
                // Was there a value already set by the markup? If so, use it
                if (t.val() != "" && t.val() != "0") {
                    self.loadbyid.call(self, t, t.val());
                }
            },
            error: function(jqxhr, textstatus, response) {
                log.error(response);
            }
        });
    },

    destroy: function(t) {
        let dialog = t.data("dialog"), dialogadd = t.data("dialogadd"), dialogsimilar = t.data("dialogsimilar");
        // Next 3 lines are to clean up additional fields that created choosers
        try { dialogadd.find(".asm-animalchooser").animalchooser("destroy"); } catch (eac) {}
        try { dialogadd.find(".asm-animalchoosermulti").animalchoosermulti("destroy"); } catch (eacm) {}
        try { dialogadd.find(".asm-personchooser").personchooser("destroy"); } catch (epc) {}
        try { dialog.dialog("destroy"); } catch (ex) {}
        try { dialog.remove(); } catch (er) {}
        try { dialogadd.dialog("destroy"); } catch (exa) {}
        try { dialogadd.remove(); } catch (era) {}
        try { dialogsimilar.dialog("destroy"); } catch (exs) {}
        try { dialogsimilar.remove(); } catch (ers) {}
    },

    /**
     * Load a person record from ID
     */
    loadbyid: function(t, personid) {
        let self = this;
        if (!personid || personid == "0" || personid == "") { return; }
        self.clear.call(self, t);
        t.val(personid);
        let node = t.data("node"), display = t.data("display"), dialog = t.data("dialog");
        let formdata = "mode=id&id=" + personid;
        $.ajax({
            type: "POST",
            url:  "person_embed",
            data: formdata,
            dataType: "text",
            success: function(data, textStatus, jqXHR) {
                let h = "";
                let people = jQuery.parseJSON(data);
                let rec = people[0];
                t.val(rec.ID);
                t.data("selected", rec);
                display.html(self.render_display.call(self, t, rec));
                node.find(".personchooser-briefexpander").click(function() {
                    let widget = $(this);
                    if (widget.hasClass("ui-icon-triangle-1-e")) {
                        widget.removeClass("ui-icon-triangle-1-e");
                        widget.addClass("ui-icon-triangle-1-s");
                        widget.closest(".personchooser-display").find(".personchooser-ownerinfo").slideDown(common.fx_speed);
                    } else {
                        widget.removeClass("ui-icon-triangle-1-s");
                        widget.addClass("ui-icon-triangle-1-e");
                        widget.closest(".personchooser-display").find(".personchooser-ownerinfo").slideUp(common.fx_speed);
                    }
                });
                node.find(".personchooser-banned").val(rec.ISBANNED);
                node.find(".personchooser-idcheck").val(rec.IDCHECK);
                node.find(".personchooser-postcode").val(rec.OWNERPOSTCODE);
                common.inject_target(); 
                t.trigger("loaded", [ rec ]);
            },
            error: function(jqxhr, textstatus, response) {
                log.error(response);
            }
        });
    },

    /**
     * Does the backend find and updates the onscreen table
     * in the find dialog
     */
    find: function(t) {
        let self = this, 
            dialog = t.data("dialog"),
            node = t.data("node"),
            display = t.data("display");
        dialog.find("img").show();
        dialog.find("button").button("disable");
        let q = encodeURIComponent(dialog.find("input").val());
        let formdata = "mode=find&filter=" + t.data("filter") + "&type=" + t.data("type") + "&q=" + q;
        $.ajax({
            type: "POST",
            url:  "person_embed",
            data: formdata,
            dataType: "text",
            success: function(data, textStatus, jqXHR) {
                let h = "";
                let people = jQuery.parseJSON(data);
                $.each(people, function(i, p) {
                    h += "<tr>";
                    h += "<td><a href=\"#\" data=\"" + i + "\">" + p.OWNERNAME + "</a></td>";
                    h += "<td>" + p.OWNERCODE + "</td>";
                    h += "<td>" + p.OWNERADDRESS + "</td>";
                    h += "<td>" + p.OWNERTOWN + "</td>";
                    h += "<td>" + p.OWNERCOUNTY + "</td>";
                    h += "<td>" + p.OWNERPOSTCODE + "</td>";
                    if (!config.bool("HideCountry")) { h += "<td>" + p.OWNERCOUNTRY + "</td>"; }
                    h += "</tr>";
                });
                dialog.find("table > tbody").html(h);
                // Remove any existing events from previous searches
                dialog.off("click", "a");
                // Use delegation to bind click events for 
                // the person once clicked. Triggers the change callback
                dialog.on("click", "a", function(e) {
                    let rec = people[$(this).attr("data")];
                    t.val(rec.ID);
                    t.data("selected", rec);
                    display.html(self.render_display.call(self, t, rec));
                    node.find(".personchooser-briefexpander").click(function() {
                        let widget = $(this);
                        if (widget.hasClass("ui-icon-triangle-1-e")) {
                            widget.removeClass("ui-icon-triangle-1-e");
                            widget.addClass("ui-icon-triangle-1-s");
                            widget.closest(".personchooser-display").find(".personchooser-ownerinfo").slideDown(common.fx_speed);
                        } else {
                            widget.removeClass("ui-icon-triangle-1-s");
                            widget.addClass("ui-icon-triangle-1-e");
                            widget.closest(".personchooser-display").find(".personchooser-ownerinfo").slideUp(common.fx_speed);
                        }
                    });
                    node.find(".personchooser-banned").val(rec.ISBANNED);
                    node.find(".personchooser-idcheck").val(rec.IDCHECK);
                    node.find(".personchooser-postcode").val(rec.OWNERPOSTCODE);
                    try { validate.dirty(true); } catch(exp) { }
                    dialog.dialog("close");
                    t.trigger("change", [ rec ]);
                    return false;
                });
                dialog.find("table").trigger("update");
                dialog.find("img").hide();
                dialog.find("button").button("enable");
                common.inject_target(); 
            },
            error: function(jqxhr, textstatus, response) {
                dialog.dialog("close");
                dialog.find("img").hide();
                dialog.find("button").button("enable");
                log.error(response);
            }
        });
    },

    /**
     * Returns a string containing the html content for the display element.
     * @param rec The person record.
     */
    render_display: function(t, rec) {
        let disp = "<span class=\"justlink\">";
        if (t.data("mode") == "brief") {
            disp += "<span class='personchooser-briefexpander ui-icon ui-icon-triangle-1-e'></span>";
        }
        disp += "<a class=\"asm-embed-name\" href=\"person?id=" + rec.ID + "\">" + rec.OWNERNAME + " - " + rec.OWNERCODE + "</a></span>";
        if (rec.POPUPWARNING) {
            disp += " " + html.icon("warning", rec.POPUPWARNING);
        }
        if (t.data("mode") == "full") {
            disp += "<br/>" + rec.OWNERADDRESS + "<br/>" + rec.OWNERTOWN + "<br/>" + rec.OWNERCOUNTY + 
                "<br/>" + rec.OWNERPOSTCODE + 
                (!config.bool("HideCountry") ? "<br/>" + rec.OWNERCOUNTRY : "") +
                "<br/>" + rec.HOMETELEPHONE + "<br/>" + rec.WORKTELEPHONE + 
                "<br/>" + rec.MOBILETELEPHONE + "<br/>" + rec.EMAILADDRESS;
        } else {
            disp += "<div class='personchooser-ownerinfo' style='display: none;'>" + rec.OWNERADDRESS + "<br/>" + rec.OWNERTOWN + "<br/>" + rec.OWNERCOUNTY + 
                "<br/>" + rec.OWNERPOSTCODE + 
                (!config.bool("HideCountry") ? "<br/>" + rec.OWNERCOUNTRY : "") +
                "<br/>" + rec.HOMETELEPHONE + "<br/>" + rec.WORKTELEPHONE + 
                "<br/>" + rec.MOBILETELEPHONE + "<br/>" + rec.EMAILADDRESS + "</div>";
        }
        return disp;
    },

    /**
     * Posts the add dialog to the backend to create the owner
     */
    add_person: function(t) {
        let self = this, 
            dialogadd = t.data("dialogadd"), dialogsimilar = t.data("dialogsimilar"),
            display = t.data("display"), node = t.data("node");
        let formdata = "mode=add&" + dialogadd.find("input, textarea, select").toPOST();
        $.ajax({
            type: "POST",
            url:  "person_embed",
            data: formdata,
            dataType: "text",
            success: function(result) {
                let people = jQuery.parseJSON(result);
                let rec = people[0];
                t.val(rec.ID);
                t.data("selected", rec);
                let disp = "<span class=\"justlink\"><a class=\"asm-embed-name\" href=\"person?id=" + rec.ID + "\">" + rec.OWNERNAME + "</a></span>";
                if (t.data("mode") == "full") {
                    disp += "<br/>" + rec.OWNERADDRESS + "<br/>" + rec.OWNERTOWN + "<br/>" + rec.OWNERCOUNTY + "<br/>" + rec.OWNERPOSTCODE + 
                        (!config.bool("HideCountry") ? "<br/>" + rec.OWNERCOUNTRY : "") + 
                        "<br/>" + rec.HOMETELEPHONE + "<br/>" + rec.WORKTELEPHONE + "<br/>" + rec.MOBILETELEPHONE + "<br/>" + rec.EMAILADDRESS;
                }
                display.html(disp);
                node.find(".personchooser-banned").val(rec.ISBANNED);
                node.find(".personchooser-idcheck").val(rec.IDCHECK);
                node.find(".personchooser-postcode").val(rec.OWNERPOSTCODE);
                try { 
                    validate.dirty(true); 
                } 
                catch(ev) { }
                dialogadd.dialog("close");
                common.inject_target(); 
                try { 
                    dialogsimilar.dialog("close"); 
                } 
                catch(es) { }
                t.trigger("change", [ rec ]);
            },
            error: function(jqxhr, textstatus, response) {
                dialogadd.dialog("close");
                log.error(response);
            }
        });
    },

    /**
     * Pops up the similar dialog box to prompt the user to decide
     * whether they want to create the owner or not. If they do,
     * calls add_person to do the adding.
     */
    show_similar: function(t) {
        let b = {}, self = this, dialogsimilar = t.data("dialogsimilar"), dialogadd = t.data("dialogadd");
        b[_("Create")] = function() {
            dialogsimilar.disable_dialog_buttons();
            self.add_person.call(self, t);
            dialogsimilar.close();
            dialogadd.close();
        };
        b[_("Cancel")] = function() { 
            $(this).dialog("close");
            dialogadd.enable_dialog_buttons();
        };
        dialogsimilar.dialog({
                resizable: false,
                modal: true,
                width: 500,
                dialogClass: "dialogshadow",
                show: dlgfx.delete_show,
                hide: dlgfx.delete_hide,
                buttons: b,
                close: function() {
                dialogsimilar.enable_dialog_buttons(); 
                }
        });
    },

    /**
     * Checks to see whether we have a similar person
     * on file. If we do, calls show_siilar to popup the
     * confirmation dialog
     */
    check_similar: async function(t) {
        let self = this, dialogadd = t.data("dialogadd"), dialogsimilar = t.data("dialogsimilar");
        let matchfound = false;
        let formdata = "mode=similar&" + dialogadd.find("input[data='emailaddress'], input[data='mobiletelephone'], input[data='surname'], input[data='forenames'], textarea[data='address']").toPOST();
        let homephone = dialogadd.find("input[data='hometelephone']").val();
        let result = await common.ajax_post("person_embed", formdata);
        let people = jQuery.parseJSON(result);
        let rec = people[0];
        if (rec) {
            matchfound = true;
            let disp = "<span class=\"justlink\"><a class=\"asm-embed-name\" href=\"#\">" + rec.OWNERNAME + "</a></span>";
            if (t.data("mode") == "full") {
                disp += "<br/>" + rec.OWNERADDRESS + "<br/>" + rec.OWNERTOWN + "<br/>" + rec.OWNERCOUNTY + "<br/>" + rec.OWNERPOSTCODE + 
                    (!config.bool("HideCountry") ? "<br/>" + rec.OWNERCOUNTRY : "") + 
                    "<br/>" + rec.HOMETELEPHONE + "<br/>" + rec.WORKTELEPHONE + "<br/>" + rec.MOBILETELEPHONE + 
                    " " + common.nulltostr(rec.MOBILETELEPHONE2) + "<br/>" + rec.EMAILADDRESS + " " + common.nulltostr(rec.EMAILADDRESS2);
            }
            dialogsimilar.find(".similar-person").html(disp);
            // When the user clicks the name of the similar person,
            // select it for the field instead
            dialogsimilar.find(".asm-embed-name").click(function() {
                self.loadbyid.call(self, t, rec.ID);
                dialogsimilar.dialog("close");
                dialogadd.dialog("close");
                return false;
            });
            self.show_similar.call(self, t);
        }
        // Do a second check just in case the user put a cell phone number in the home phone field
        else if (homephone) {
            formdata = "mode=similar&mobiletelephone=" + homephone + "&" + dialogadd.find("input[data='emailaddress'], input[data='surname'], input[data='forenames'], textarea[data='address']").toPOST();
            result = await common.ajax_post("person_embed", formdata);
            let people = jQuery.parseJSON(result);
            let rec = people[0];
            if (rec) {
                matchfound = true;
                let disp = "<span class=\"justlink\"><a class=\"asm-embed-name\" href=\"#\">" + rec.OWNERNAME + "</a></span>";
                if (t.data("mode") == "full") {
                    disp += "<br/>" + rec.OWNERADDRESS + "<br/>" + rec.OWNERTOWN + "<br/>" + rec.OWNERCOUNTY + "<br/>" + rec.OWNERPOSTCODE + 
                        (!config.bool("HideCountry") ? "<br/>" + rec.OWNERCOUNTRY : "") + 
                        "<br/>" + rec.HOMETELEPHONE + "<br/>" + rec.WORKTELEPHONE + "<br/>" + rec.MOBILETELEPHONE + 
                        " " + common.nulltostr(rec.MOBILETELEPHONE2) + "<br/>" + rec.EMAILADDRESS + " " + common.nulltostr(rec.EMAILADDRESS2);
                }
                dialogsimilar.find(".similar-person").html(disp);
                // When the user clicks the name of the similar person,
                // select it for the field instead
                dialogsimilar.find(".asm-embed-name").click(function() {
                    self.loadbyid.call(self, t, rec.ID);
                    dialogsimilar.dialog("close");
                    dialogadd.dialog("close");
                    return false;
                });
                self.show_similar.call(self, t);
            }
        }
        if (!matchfound) { self.add_person.call(self, t); }
    },

    clear: function(t, fireclearedevent) {
        t.val("0");
        t.data("display").html("");
        t.data("selected", null);
        if (fireclearedevent) { t.trigger("cleared"); }
    },

    is_empty: function(t) {
        return t.data("selected") == null;
    },

    /**
     * Returns the selected person record. If there's nothing
     * selected, undefined/null is returned
     */
    get_selected: function(t) {
        return t.data("selected");
    },

    /**
     * Changes the find filter to f.
     */
    set_filter: function(t, f) {
        let title = "";
        t.data("filter", f);
        // Choose the title from the filter
        if (f == "vet") { title = _("Find vet"); }
        else if (f == "retailer") { title = _("Find retailer"); }
        else if (f == "staff") { title = _("Find staff"); }
        else if (f == "fosterer") { title = _("Find fosterer"); }
        else if (f == "volunteer") { title = _("Find volunteer"); }
        else if (f == "volunteerandstaff") { title = _("Find staff/volunteer"); }
        else if (f == "shelter") { title = _("Find shelter"); }
        else if (f == "aco") { title = _("Find aco"); }
        else if (f == "homechecked") { title = _("Find homechecked"); }
        else if (f == "homechecker") { title = _("Find homechecker"); }
        else if (f == "member") { title = _("Find member"); }
        else if (f == "donor") { title = _("Find donor"); }
        else if (f == "driver") { title = _("Find driver"); }
        else if (f == "sponsor") { title = _("Find sponsor"); }
        else if (f == "supplier") { title = _("Find supplier"); }
        else { title = _("Find person"); }
        t.data("title", title);
        if (t.data("dialog")) {
            t.data("dialog").dialog("option", "title", title);
        }
    },

    /**
     * Sets the owner type to t for find operations and updates the title
     */
    set_type: function(t, newtype){
        t.data("type", newtype);
        if (newtype == "organization") {
            t.data("title", _("Find organization"));
            t.data("addtitle", _("Add organization"));
        }
        else {
            t.data("title", _("Find person"));
            t.data("addtitle", _("Add person"));
        }
    }
});
