/*global $, jQuery, _, additional, asm, common, config, controller, dlgfx, edit_header, format, header, html, mapping, tableform, validate */

$(function() {

    "use strict";

    const person = {

        render_dialogs: function() {
            return [
                '<div id="dialog-merge" style="display: none" title="' + html.title(_("Select person to merge")) + '">',
                '<div class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-info"></span>',
                _("Select a person to merge into this record. The selected person will be removed, and their movements, diary notes, log entries, etc. will be reattached to this record."),
                '</p>',
                '</div>',
                html.capture_autofocus(),
                '<table width="100%">',
                '<tr>',
                '<td><label for="mergeperson">' + _("Person") + '</label></td>',
                '<td>',
                '<input id="mergeperson" data="mergeperson" type="hidden" class="asm-personchooser" value="" />',
                '</td>',
                '</tr>',
                '</table>',
                '</div>',
                '<div id="emailform"></div>',
                '<div id="dialog-popupwarning" style="display: none" title="' + html.title(_("Warning")) + '">',
                '<p>' + html.error(controller.person.POPUPWARNING) + '</p>',
                '</div>'
            ].join("\n");
        },

        render_details: function() {
            return [
                '<h3><a href="#">' + _("Name and Address") + '</a></h3>',
                '<div>',
                '<table width="100%">',
                '<tr>',
                // left table
                '<td width="35%" class="asm-nested-table-td">',
                '<table class="additionaltarget" data="to7">',
                '<tr>',
                '<td><label for="code">' + _("Code") + '</label></td>',
                '<td>',
                '<span class="asm-person-code">' + controller.person.OWNERCODE + '</span>',
                '</td>',
                '</tr>',
                '<tr id="siterow">',
                '<td><label for="site">' + _("Site") + '</label></td>',
                '<td>',
                '<select id="site" data-json="SITEID" data-post="site" class="asm-selectbox">',
                '<option value="0">' + _("(all)") + '</option>',
                html.list_to_options(controller.sites, "ID", "SITENAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="ownertype">' + _("Class") + '</label></td>',
                '<td>',
                '<select id="ownertype" data-json="OWNERTYPE" data-post="ownertype" class="asm-selectbox">',
                '<option value="1">' + _("Individual") + '</option>',
                '<option value="3">' + _("Couple") + '</option>',
                '<option value="2">' + _("Organization") + '</option>',
                '</select>',
                '</td>',
                '</tr>',
                '<tr class="tag-individual">',
                '<td><label for="title">' + _("Title") + '</label></td>',
                '<td class="nowrap">',
                '<input type="text" id="title" data-json="OWNERTITLE" data-post="title" maxlength="50" class="asm-textbox" />',
                '<input type="text" id="title2" data-json="OWNERTITLE2" data-post="title2" maxlength="50" class="asm-textbox tag-couple" />',
                '</td>',
                '</tr>',
                '<tr class="tag-individual">',
                '<td><label for="initials">' + _("Initials") + '</label></td>',
                '<td class="nowrap">',
                '<input type="text" id="initials" data-json="OWNERINITIALS" data-post="initials" maxlength="50" class="asm-textbox" />',
                '<input type="text" id="initials" data-json="OWNERINITIALS2" data-post="initials2" maxlength="50" class="asm-textbox tag-couple" />',
                '</td>',
                '</tr>',
                '<tr class="tag-individual">',
                '<td><label for="forenames">' + _("First name(s)") + '</label></td>',
                '<td class="nowrap">',
                '<input type="text" id="forenames" data-json="OWNERFORENAMES" data-post="forenames" maxlength="200" class="asm-textbox" />',
                '<input type="text" id="forenames2" data-json="OWNERFORENAMES2" data-post="forenames2" maxlength="200" class="asm-textbox tag-couple" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="surname" class="tag-individual">' + _("Last name") + '</label>',
                '<label for="surname" class="tag-organisation">' + _("Organization name") + '</label>',
                '<span class="asm-has-validation">*</span>',
                '</td>',
                '<td class="nowrap">',
                '<input type="text" id="surname" data-json="OWNERSURNAME" data-post="surname" maxlength="100" class="asm-textbox" />',
                '<input type="text" id="surname2" data-json="OWNERSURNAME2" data-post="surname2" maxlength="100" class="asm-textbox tag-couple" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="hometelephone">' + _("Home Phone") + '</label></td>',
                '<td>',
                '<input type="text" id="hometelephone" data-json="HOMETELEPHONE" data-post="hometelephone" class="asm-textbox asm-phone" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="worktelephone">' + _("Work Phone") + '</label></td>',
                '<td class="nowrap">',
                '<input type="text" id="worktelephone" data-json="WORKTELEPHONE" data-post="worktelephone" class="asm-textbox asm-phone" />',
                '<input type="text" id="worktelephone2" data-json="WORKTELEPHONE2" data-post="worktelephone2" class="asm-textbox asm-phone tag-couple" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="mobiletelephone">' + _("Cell Phone") + '</label></td>',
                '<td class="nowrap">',
                '<input type="text" id="mobiletelephone" data-json="MOBILETELEPHONE" data-post="mobiletelephone" class="asm-textbox asm-phone" />',
                '<input type="text" id="mobiletelephone2" data-json="MOBILETELEPHONE2" data-post="mobiletelephone2" class="asm-textbox asm-phone tag-couple" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="email">' + _("Email") + '</label></td>',
                '<td class="nowrap">',
                '<input type="text" id="email" data-json="EMAILADDRESS" data-post="emailaddress" maxlength="200" class="asm-textbox" />',
                '<input type="text" id="email2" data-json="EMAILADDRESS2" data-post="emailaddress2" maxlength="200" class="asm-textbox tag-couple" />',
                '</td>',
                '</tr>',
                '<tr id="dateofbirthrow">',
                '<td><label for="dateofbirth">' + _("Date Of Birth") + '</label></td>',
                '<td class="nowrap">',
                '<input type="text" id="dateofbirth" data-json="DATEOFBIRTH" data-post="dateofbirth" class="asm-textbox asm-datebox" />',
                '<input type="text" id="dateofbirth2" data-json="DATEOFBIRTH2" data-post="dateofbirth2" class="asm-textbox asm-datebox tag-couple" />',
                '</td>',
                '</tr>',
                '<tr id="idnumberrow">',
                '<td><label for="idnumber">' + _("ID Number") + '</label>',
                '<span id="idnumber-callout" class="asm-callout">',
                _("Driving license, passport or other identification number"),
                '</span>',
                '</td>',
                '<td class="nowrap">',
                '<input type="text" id="idnumber" data-json="IDENTIFICATIONNUMBER" data-post="idnumber" maxlength="200" class="asm-textbox" />',
                '<input type="text" id="idnumber2" data-json="IDENTIFICATIONNUMBER2" data-post="idnumber2" maxlength="200" class="asm-textbox tag-couple" />',
                '</td>',
                '</tr>',
                '<tr id="jurisdictionrow">',
                '<td><label for="jurisdiction">' + _("Jurisdiction") + '</label></td>',
                '<td>',
                '<select id="jurisdiction" data-json="JURISDICTIONID" data-post="jurisdiction" class="asm-selectbox">',
                html.list_to_options(controller.jurisdictions, "ID", "JURISDICTIONNAME"),
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
                '</table>',
                // right table 
                '<td width="30%" class="asm-nested-table-td">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="address">' + _("Address") + '</label></td>',
                '<td>',
                '<textarea id="address" title="' + html.title(_("Address")) + '" data-json="OWNERADDRESS" data-post="address" rows="5" class="asm-textareafixed"></textarea>',
                '</td>',
                '</tr>',
                '<tr class="towncounty">',
                '<td><label for="town">' + _("City") + '</label></td>',
                '<td>',
                '<input type="text" id="town" data-json="OWNERTOWN" data-post="town" maxlength="100" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr class="towncounty">',
                '<td><label for="county">' + _("State") + '</label></td>',
                '<td>',
                common.iif(config.bool("USStateCodes"),
                    '<select id="county" data-json="OWNERCOUNTY" data-post="county" class="asm-selectbox">' +
                    html.states_us_options() + '</select>',
                    '<input type="text" id="county" data-json="OWNERCOUNTY" data-post="county" maxlength="100" ' + 
                    'class="asm-textbox" />'),
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="postcode">' + _("Zipcode") + '</label></td>',
                '<td>',
                '<input type="text" id="postcode" data-json="OWNERPOSTCODE" data-post="postcode" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr id="countryrow">',
                '<td><label for="country">' + _("Country") + '</label></td>',
                '<td><input class="asm-textbox newform" id="country" data-json="OWNERCOUNTRY" data-post="country" type="text" /></td>',
                '</tr>',
                '<tr id="latlongrow">',
                '<td><label for="latlong">' + _("Latitude/Longitude"),
                '<span class="asm-callout">' + _("Right-click on the map to change the marker location") + '</span>',
                '</label></td>',
                '<td><input type="text" class="asm-latlong" id="latlong" data-json="LATLONG" data-post="latlong" /></td>',
                '</tr>',
                // end right table
                '</table>',
                // Third column, embedded map placeholder
                '</td>',
                '<td width="35%" class="asm-nested-table-td">',
                '<div id="embeddedmap" style="z-index: 1; width: 100%; height: 300px; color: #000"></div>',
                // end outer table
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_type: function() {
            return [
                '<h3><a href="#">' + _("Type") + '</a></h3>',
                '<div>',
                // Outer table
                '<table width="100%">',
                '<tr>',
                '<td width="50%" class="asm-nested-table-td">',
                // Left table
                '<table class="additionaltarget" data="to8">',
                '<tr>',
                '<td><label for="flags">' + _("Flags") + '</label></td>',
                '<td>',
                '<select id="flags" data="flags" class="asm-bsmselect" multiple="multiple">',
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="homecheckedby">' + _("Homechecked by") + '</label></td>',
                '<td>',
                '<input id="homecheckedby" data-json="HOMECHECKEDBY" data-post="homecheckedby" type="hidden" data-filter="homechecker" class="asm-personchooser" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="homechecked">' + _("on") + '</label></td>',
                '<td><input type="text" id="homechecked" data-json="DATELASTHOMECHECKED" data-post="homechecked" title="' + html.title(_("The date this person was homechecked.")) + '" class="asm-textbox asm-datebox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="membershipnumber">' + _("Membership Number") + '</label></td>',
                '<td><input type="text" id="membershipnumber" data-json="MEMBERSHIPNUMBER" data-post="membershipnumber" title="' + html.title(_("If this person is a member, their membership number.")) + '" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="membershipexpires">' + _("Membership Expiry") + '</label></td>',
                '<td><input type="text" id="membershipexpires" data-json="MEMBERSHIPEXPIRYDATE" data-post="membershipexpires" title="' + html.title(_("If this person is a member, the date that membership expires.")) + '" class="asm-textbox asm-datebox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="fostercapacity">' + _("Foster Capacity") + '</label></td>',
                '<td><input type="text" id="fostercapacity" data-json="FOSTERCAPACITY" data-post="fostercapacity" title="' + html.title(_("If this person is a fosterer, the maximum number of animals they can care for.")) + '" class="asm-textbox asm-numberbox" /></td>',
                '</tr>',
                '</table>',
                '</td>',
                '<td class="asm-nested-table-td">',
                // Right table
                '<table width="100%">',
                '<tr>',
                '<td><label for="comments">' + _("Comments") + '</label></td>',
                '<td>',
                '<textarea id="comments" title="' + _("Comments") + '" data-json="COMMENTS" data-post="comments" rows="7" class="asm-textarea"></textarea>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="popupwarning">' + _("Warning") + '</label>',
                '<span id="callout-popupwarning" class="asm-callout">' + _("Show a warning when viewing this person") + '</span>',
                '</td>',
                '<td>',
                '<textarea id="popupwarning" title="' + _("Warning") + '" data-json="POPUPWARNING" data-post="popupwarning" rows="2" class="asm-textarea"></textarea>',
                '</td>',
                '</tr>',
                '</table>',
                '<!-- end outer table -->',
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_homechecker: function() {
            return [
                '<h3 id="accordion-homechecker"><a href="#">' + _("Homechecker") + '</a></h3>',
                '<div>',
                // outer table
                '<table width="100%">',
                '<tr>',
                '<td width="50%" class="asm-nested-table-td">',
                '<p class="asm-header"><label for="areas">' + _("Homecheck Areas") + '</label></p>',
                '<textarea id="areas" class="asm-textarea" data-json="HOMECHECKAREAS" data-post="areas" rows="8" title="' + html.title(_("A list of areas this person will homecheck - eg: S60 S61")) + '"></textarea>',
                '</td>',
                '<td width="50%" valign="top" class="asm-nested-table-td">',
                // history table
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
                '</table>',
                // end outer table
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_lookingfor: function() {
            return [
                '<h3 id="accordion-lookingfor"><a href="#">' + _("Looking for") + ' <span id="tabcriteria" style="display: none" class="asm-icon asm-icon-animal"></span></a></h3><div>',
                // Outer table
                '<table width="100%">',
                '<tr>',
                '<td class="asm-nested-table-td">',
                // left table
                '<table>',
                '<tr>',
                '<td><label for="matchactive">' + _("Status") + '</label></td>',
                '<td><select class="asm-selectbox" id="matchactive" data-json="MATCHACTIVE" data-post="matchactive">',
                '<option value="0">' + _("Inactive - do not include") + '</option>',
                '<option value="1">' + _("Active") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchadded">' + _("Added") + '</label></td>',
                '<td><input type="text" class="lft asm-textbox asm-datebox" id="matchadded" data-json="MATCHADDED" data-post="matchadded" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchexpires">' + _("Expires") + '</label></td>',
                '<td><input type="text" class="lft asm-textbox asm-datebox" id="matchexpires" data-json="MATCHEXPIRES" data-post="matchexpires" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchagedfrom">' + _("Aged From") + '</label></td>',
                '<td><input type="text" class="lft asm-textbox asm-numberbox" id="agedfrom" data-json="MATCHAGEFROM" data-post="agedfrom" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchagedto">' + _("Aged To") + '</label></td>',
                '<td><input type="text" class="lft asm-textbox asm-numberbox" id="agedto" data-json="MATCHAGETO" data-post="agedto" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchcommentscontain">' + _("Comments Contain") + '</label>',
                '<span id="callout-commentscontain" class="asm-callout">' + _("Animal comments MUST contain this phrase in order to match."),
                '<br/>',
                _("DO NOT use this field to store notes about what the person is looking for.") + '</span>',
                '</td>',
                '<td><textarea id="commentscontain" data-json="MATCHCOMMENTSCONTAIN" data-post="commentscontain" rows="5" maxlength="255" class="lft asm-textareafixed"></textarea></td>',
                '</tr>',
                '</table>',
                '</td>',
                '<td class="asm-nested-table-td">',
                // right table
                '<table>',
                '<tr>',
                '<td><label for="matchsex">' + _("Sex") + '</label></td>',
                '<td><select id="matchsex" data-json="MATCHSEX" data-post="matchsex" class="lfs asm-selectbox">',
                '<option value="-1">' + _("(any)") + '</option>',
                html.list_to_options(controller.sexes, "ID", "SEX"),
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchsize">' + _("Size") + '</label></td>',
                '<td><select id="matchsize" data-json="MATCHSIZE" data-post="matchsize" class="lfs asm-selectbox">',
                '<option value="-1">' + _("(any)") + '</option>',
                html.list_to_options(controller.sizes, "ID", "SIZE"),
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchcolour">' + _("Color") + '</label></td>',
                '<td><select id="matchcolour" data-json="MATCHCOLOUR" data-post="matchcolour" class="lfs asm-selectbox">',
                '<option value="-1">' + _("(any)") + '</option>',
                html.list_to_options(controller.colours, "ID", "BASECOLOUR"),
                '</select></td>',
                '</tr>',

                '<tr>',
                '<td><label for="matchtype">' + _("Type") + '</label></td>',
                '<td><select id="matchtype" data-json="MATCHANIMALTYPE" data-post="matchtype" class="lfs asm-selectbox">',
                '<option value="-1">' + _("(any)") + '</option>',
                html.list_to_options(controller.animaltypes, "ID", "ANIMALTYPE"),
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchspecies">' + _("Species") + '</label></td>',
                '<td><select id="matchspecies" data-json="MATCHSPECIES" data-post="matchspecies" class="lfs asm-selectbox">',
                '<option value="-1">' + _("(any)") + '</option>',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchbreed1">' + _("Breed") + '</label></td>',
                '<td><select id="matchbreed1" data-json="MATCHBREED" data-post="matchbreed1" class="lfs asm-selectbox">',
                '<option value="-1">' + _("(any)") + '</option>',
                html.list_to_options_breeds(controller.breeds, "ID", "BREEDNAME"),
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchbreed2">' + _("or") + '</label></td>',
                '<td><select id="matchbreed2" data-json="MATCHBREED2" data-post="matchbreed2" class="lfs asm-selectbox">',
                '<option value="-1">' + _("(any)") + '</option>',
                html.list_to_options_breeds(controller.breeds, "ID", "BREEDNAME"),
                '</select></td>',
                '</tr>',
                '</table>',
                // far right table
                '</td>',
                '<td class="asm-nested-table-td">',
                '<table>',
                '<tr>',
                '<td><label for="matchgoodwithcats">' + _("Good with cats") + '</label></td>',
                '<td><select id="matchgoodwithcats" data-json="MATCHGOODWITHCATS" data-post="matchgoodwithcats" class="lfs asm-halftextbox selectbox">',
                '<option value="-1">' + _("(any)") + '</option>',
                html.list_to_options(controller.ynun, "ID", "NAME"),
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchgoodwithdogs">' + _("Good with dogs") + '</label></td>',
                '<td><select id="matchgoodwithdogs" data-json="MATCHGOODWITHDOGS" data-post="matchgoodwithdogs" class="lfs asm-halftextbox selectbox">',
                '<option value="-1">' + _("(any)") + '</option>',
                html.list_to_options(controller.ynun, "ID", "NAME"),
                '</select></td>',
                '</tr>',
                '',
                '<tr>',
                '<td><label for="matchgoodwithchildren">' + _("Good with children") + '</label></td>',
                '<td><select id="matchgoodwithchildren" data-json="MATCHGOODWITHCHILDREN" data-post="matchgoodwithchildren" class="lfs asm-halftextbox selectbox">',
                '<option value="-1">' + _("(any)") + '</option>',
                html.list_to_options(controller.ynunk, "ID", "NAME"),
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchhousetrained">' + _("Housetrained") + '</label></td>',
                '<td><select id="matchhousetrained" data-json="MATCHHOUSETRAINED" data-post="matchhousetrained" class="lfs asm-halftextbox selectbox">',
                '<option value="-1">' + _("(any)") + '</option>',
                html.list_to_options(controller.ynun, "ID", "NAME"),
                '</select></td>',
                '</tr>',
                '</table>',
                // end outer table
                '</td>',
                '</tr>',
                '</table>',
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

            // If the looking for status is inactive, disable the fields
            if ($("#matchactive").val() == "0") {
                $(".lft").closest("tr").fadeOut();
                $(".lfs").closest("tr").fadeOut();
                $("#button-lookingfor").button("option", "disabled", true);
            }
            else {
                $(".lft").closest("tr").fadeIn();
                $(".lfs").closest("tr").fadeIn();
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
                $("#membershipnumber").closest("tr").fadeIn();
                $("#membershipexpires").closest("tr").fadeIn();
            }

            // If the vet flag is selected, change the membership number label
            // and hide the expiry field so we can use membership for licence
            if ($("#flags option[value='vet']").is(":selected")) {
                $("label[for='membershipnumber']").html(_("License Number"));
                $("#membershipnumber").prop("title", _("The veterinary license number."));
                $("#membershipnumber").closest("tr").fadeIn();
                $("#membershipexpires").closest("tr").fadeOut();
            }

            // If neither member or vet flag is set, hide the membership number field
            if (!$("#flags option[value='vet']").is(":selected") && !$("#flags option[value='member']").is(":selected")) {
                $("#membershipnumber").closest("tr").fadeOut();
                $("#membershipexpires").closest("tr").fadeOut();
            }

            // If the fosterer flag is set, show/hide the fosterer capacity field
            if ($("#flags option[value='fosterer']").is(":selected")) {
                $("#fostercapacity").closest("tr").fadeIn();
            }
            else {
                $("#fostercapacity").closest("tr").fadeOut();
            }

            // If the homechecked flag is set, or the option is not on to
            // hide them, show/hide the homechecked by/date fields
            if ($("#flags option[value='homechecked']").is(":selected") || !config.bool("HideHomeCheckedNoFlag")) {
                $("#homecheckedby").closest("tr").fadeIn();
                $("#homechecked").closest("tr").fadeIn();
            }
            else {
                $("#homecheckedby").closest("tr").fadeOut();
                $("#homechecked").closest("tr").fadeOut();
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
            if (common.trim($("#email").val()) != "") {
                if (!validate.email($("#email").val())) {
                    header.show_error(_("Invalid email address '{0}'").replace("{0}", $("#email").val()));
                    validate.highlight("email");
                    return false;
                }
            }

            // email2
            if (common.trim($("#email2").val()) != "") {
                if (!validate.email($("#email2").val())) {
                    header.show_error(_("Invalid email address '{0}'").replace("{0}", $("#email2").val()));
                    validate.highlight("email");
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

        show_mini_map: function() {
            setTimeout(function() {
                mapping.draw_map("embeddedmap", 15, controller.person.LATLONG, [{ 
                    latlong: controller.person.LATLONG, popuptext: controller.person.OWNERADDRESS, popupactive: true }]);
            }, 50);
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

            if (!config.bool("USStateCodes")) {
                $("#county").autocomplete({ source: controller.counties, minLength: 3 });
            }
            $("#town").autocomplete({ source: controller.towns, minLength: 4 });
            $("#town").blur(function() {
                if ($("#county").val() == "") {
                    $("#county").val(controller.towncounties[$("#town").val()]);
                }
            });

            additional.relocate_fields();

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
                let email = $("#email").val(), email2 = $("#email2").val();
                if (email2) { email += ", " + email2; }
                $("#emailform").emailform("show", {
                    post: "person",
                    formdata: "mode=email&personid=" + $("#personid").val(),
                    name: $("#forenames").val() + " " + $("#surname").val(),
                    email: email,
                    logtypes: controller.logtypes,
                    personid: controller.person.ID,
                    templates: controller.templates
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

            if (config.bool("ShowPersonMiniMap")) {
                person.show_mini_map();
            }

            // Dirty handling
            validate.bind_dirty([ "person_" ]);

            // If a popup warning has been set, display it
            person.show_popup_warning();

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
