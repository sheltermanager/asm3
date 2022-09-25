/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const incident_find = {

        render: function() {
            return [
                html.content_header(_("Find Incident")),
                '<div id="incidentsearchform">',
                '<table class="asm-table-layout">',

                '<tr>',
                '<td>',
                '<label for="number">' + _("Number") + '</label>',
                '</td>',
                '<td>',
                '<input id="number" data="number" class="asm-textbox asm-numberbox" />',
                '</td>',
                '<td>',
                '<label for="callername">' + _("Caller Name") + '</label>',
                '</td>',
                '<td>',
                '<input id="callername" data="callername" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="callerphone">' + _("Caller Phone") + '</label>',
                '</td>',
                '<td>',
                '<input id="callerphone" data="callerphone" class="asm-textbox" />',
                '</td>',
                '</tr>',

                '<tr>',
                '<td>',
                '<label for="victimname">' + _("Victim Name") + '</label>',
                '</td>',
                '<td>',
                '<input id="victimname" data="victimname" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="incidenttype">' + _("Incident Type") + '</label>',
                '</td>',
                '<td>',
                '<select id="incidenttype" data="incidenttype" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.incidenttypes, "ID", "INCIDENTNAME"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="completedtype">' + _("Completed Type") + '</label>',
                '</td>',
                '<td>',
                '<select id="completedtype" data="completedtype" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.completedtypes, "ID", "COMPLETEDNAME"),
                '</select>',
                '</td>',
                '</tr>',

                '<tr>',
                '<td>',
                '<label for="dispatchedaco">' + _("Dispatched ACO") + '</label>',
                '</td>',
                '<td>',
                '<select id="dispatchedaco" data="dispatchedaco" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.users, "USERNAME", "USERNAME"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="callnotes">' + _("Notes") + '</label>',
                '</td>',
                '<td>',
                '<input id="callnotes" data="callnotes" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="jurisdiction">' + _("Jurisdiction") + '</label>',
                '</td>',
                '<td>',
                '<select id="jurisdiction" data="jurisdiction" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.jurisdictions, "ID", "JURISDICTIONNAME"),
                '</select>',
                '</td>',
                '</tr>',

                '<tr>',
                '<td>',
                '<label for="address">' + _("Address") + '</label>',
                '</td>',
                '<td>',
                '<input id="address" data="address" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="city">' + _("City") + '</label>',
                '</td>',
                '<td>',
                '<input id="city" data="city" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="postcode">' + _("Zipcode") + '</label>',
                '</td>',
                '<td>',
                '<input id="postcode" data="postcode" class="asm-textbox" />',
                '</td>',
                '</tr>',

                '<tr>',
                '<td>',
                '<label for="description">' + _("Description") + '</label>',
                '</td>',
                '<td>',
                '<input id="description" data="description" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="agegroup">' + _("Age Group") + '</label></td>',
                '<td>',
                '<select id="agegroup" data="agegroup" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.agegroups),
                '</select>',
                '</td>',
                '<td><label for="pickuplocation">' + _("Pickup Location") + '</label></td>',
                '<td><select id="pickuplocation" data="pickuplocation" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.pickuplocations, "ID", "LOCATIONNAME"),
                '</select></td>',
                '</tr>',

                '<tr>',
                '<td>',
                '<label for="sex">' + _("Sex") + '</label></td>',
                '<td>',
                '<select id="sex" data="sex" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.sexes, "ID", "SEX"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="species">' + _("Species") + '</label></td>',
                '<td>',
                '<select id="species" data="species" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="filter">' + _("Filter") + '</label></td>',
                '<td>',
                '<select id="filter" data="filter" class="asm-selectbox">',
                '<option value="">' + _("(all)") + '</option>',
                '<option value="incomplete" selected="selected">' + _("Incomplete incidents") + '</option>',
                '<option value="undispatched">' + _("Not dispatched") + '</option>',
                '<option value="requirefollowup">' + _("Require followup") + '</option>',
                '<option value="completed">' + _("Completed") + '</option>',
                '</select>',
                '</td>',
                '</tr>',
                
                '<tr>',
                '<td><label for="incidentfrom">' + _("Incident Between") + '</label></td>',
                '<td><input id="incidentfrom" data="incidentfrom" class="asm-textbox asm-datebox" /></td>',
                '<td><label for="incidentto">' + _("and") + '</label></td>',
                '<td><input id="incidentto" data="incidentto" class="asm-textbox asm-datebox" /></td>',
                '</tr>',

                '<tr>',
                '<td><label for="dispatchfrom">' + _("Dispatch Between") + '</label></td>',
                '<td><input id="dispatchfrom" data="dispatchfrom" class="asm-textbox asm-datebox" /></td>',
                '<td><label for="dispatchto">' + _("and") + '</label></td>',
                '<td><input id="dispatchto" data="dispatchto" class="asm-textbox asm-datebox" /></td>',
                '</tr>',

                '<tr>',
                '<td><label for="respondedfrom">' + _("Responded Between") + '</label></td>',
                '<td><input id="respondedfrom" data="respondedfrom" class="asm-textbox asm-datebox" /></td>',
                '<td><label for="respondedto">' + _("and") + '</label></td>',
                '<td><input id="respondedto" data="respondedto" class="asm-textbox asm-datebox" /></td>',
                '</tr>',

                '<tr>',
                '<td><label for="followupfrom">' + _("Followup Between") + '</label></td>',
                '<td><input id="followupfrom" data="followupfrom" class="asm-textbox asm-datebox" /></td>',
                '<td><label for="followupto">' + _("and") + '</label></td>',
                '<td><input id="followupto" data="followupto" class="asm-textbox asm-datebox" /></td>',
                '</tr>',

                '<tr>',
                '<td><label for="completedfrom">' + _("Completed Between") + '</label></td>',
                '<td><input id="completedfrom" data="completedfrom" class="asm-textbox asm-datebox" /></td>',
                '<td><label for="completedto">' + _("and") + '</label></td>',
                '<td><input id="completedto" data="completedto" class="asm-textbox asm-datebox" /></td>',
                '</tr>',

                '</table>',
                '<p class="centered">',
                '<button type="submit" id="searchbutton">' + _("Search") + '</button>',
                '</p>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {

            $("#searchbutton").button().click(function() {
                common.route("incident_find_results?" + $("#incidentsearchform input, #incidentsearchform select").toPOST());
            });

            // We need to re-enable the return key submitting the form
            $("#incidentsearchform").keypress(function(e) {
                if (e.keyCode == 13) {
                    common.route("incident_find_results?" + $("#incidentsearchform input, #incidentsearchform select").toPOST());
                }
            });

        },

        name: "incident_find",
        animation: "criteria",
        autofocus: "#number",
        title: function() { return _("Find Incident"); },
        routes: {
            "incident_find": function() { common.module_loadandstart("incident_find", "incident_find"); }
        }

    };

    common.module_register(incident_find);

});
