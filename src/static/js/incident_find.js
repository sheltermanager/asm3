/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const incident_find = {

        options_filter: [ 
            '<option value="">' + _("(all)") + '</option>',
            '<option value="incomplete" selected="selected">' + _("Incomplete incidents") + '</option>',
            '<option value="undispatched">' + _("Not dispatched") + '</option>',
            '<option value="requirefollowup">' + _("Require followup") + '</option>',
            '<option value="completed">' + _("Completed") + '</option>' ].join("\n"),

        render: function() {
            let col1 = [
                html.search_field_number("number", _("Number")),
                html.search_field_text("code", _("Code")),
                html.search_field_text("callername", _("Caller Name")),
                html.search_field_text("callerphone", _("Caller Phone")),
                html.search_field_text("callnotes", _("Notes")),
                html.search_field_text("victimname", _("Victim Name")),
                html.search_field_select("incidenttype", _("Incident Type"), html.list_to_options(controller.incidenttypes, "ID", "INCIDENTNAME")),
                html.search_field_select("completedtype", _("Completed Type"), html.list_to_options(controller.completedtypes, "ID", "COMPLETEDNAME")),
                html.search_field_select("dispatchedaco", _("Dispatched ACO"), html.list_to_options(controller.users, "USERNAME", "USERNAME")),
            ].join("\n");
            let col2 = [
                html.search_field_select("jurisdiction", _("Jurisdiction"), html.list_to_options(controller.jurisdictions, "ID", "JURISDICTIONNAME")),
                html.search_field_text("address", _("Address")),
                html.search_field_text("city", _("City")),
                html.search_field_text("postcode", _("Zipcode")),
                html.search_field_text("description", _("Description")),
                html.search_field_select("pickuplocation", _("Pickup Location"), html.list_to_options(controller.pickuplocations, "ID", "LOCATIONNAME")),
                html.search_field_select("agegroup", _("Age Group"), html.list_to_options(controller.agegroups)),
                html.search_field_select("sex", _("Sex"), html.list_to_options(controller.sexes, "ID", "SEX")),
                html.search_field_select("species", _("Species"), html.list_to_options(controller.species, "ID", "SPECIESNAME")),
            ].join("\n");
            let col3 = [
                html.search_field_daterange("incidentfrom", "incidentto", _("Incident Between")),
                html.search_field_daterange("dispatchfrom", "dispatchto", _("Dispatch Between")),
                html.search_field_daterange("respondedfrom", "respondedto", _("Responded Between")),
                html.search_field_daterange("followupfrom", "followupto", _("Followup Between")),
                html.search_field_daterange("completedfrom", "completedto", _("Completed Between")),
                html.search_field_select("filter", _("Filter"), incident_find.options_filter),
            ].join("\n");
            return [
                html.content_header(_("Find Incident")),
                '<div id="incidentsearchform">',
                '<div class="asm-search-criteriacolumns">',
                html.search_column(col1),
                html.search_column(col2),
                html.search_column(col3),
                html.search_column(additional.additional_search_fields(controller.additionalfields, 1)),
                '</div>',
                '</div>',
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

        sync: function() {
            if (config.bool("AdvancedFindIncidentIncomplete")) {
                $("#filter").select("value", "incomplete");
            }
            else {
                $("#filter").select("value", "");
            }
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
