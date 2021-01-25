/*global $, jQuery, _, additional, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const incident_new = {

        render: function() {
            return [
                html.content_header(_("Report a new incident")),
                '<table class="asm-table-layout">',
                '<tr>',
                '<td><label for="incidenttype">' + _("Type") + '</label></td>',
                '<td><select id="incidenttype" data-post="incidenttype" class="asm-selectbox">',
                html.list_to_options(controller.incidenttypes, "ID", "INCIDENTNAME"),
                '</td>',
                '</tr>',
                '<tr id="viewrolesrow">',
                '<td><label for="viewroles">' + _("View Roles") + '</label>',
                '<span id="callout-viewroles" class="asm-callout">' + _("Only allow users with one of these roles to view this incident") + '</span>',
                '</td>',
                '<td><select id="viewroles" data-post="viewroles" class="asm-bsmselect" multiple="multiple">',
                html.list_to_options(controller.roles, "ID", "ROLENAME"),
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="incidentdate">' + _("Incident Date/Time") + '</label></td>',
                '<td><input id="incidentdate" data-post="incidentdate" class="asm-halftextbox asm-datebox" />',
                '<input id="incidenttime" data-post="incidenttime" class="asm-halftextbox asm-timebox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="callnotes">' + _("Notes") + '</label></td>',
                '<td><textarea id="callnotes" data-post="callnotes" class="asm-textarea" rows="3"></textarea></td>',
                '</tr>',
                '<tr>',
                '<tr>',
                '<td><label for="calldate">' + _("Call Date/Time") + '</label></td>',
                '<td><input id="calldate" data-post="calldate" class="asm-halftextbox asm-datebox" />',
                '<input id="calltime" data-post="calltime" class="asm-halftextbox asm-timebox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="calltaker">' + _("Taken By") + '</label></td>',
                '<td><select id="calltaker" data-post="calltaker" class="asm-selectbox">',
                '<option> </option>',
                html.list_to_options(controller.users, "USERNAME", "USERNAME"),
                '</td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Caller") + '</td>',
                '<td>',
                '<input id="caller" data-post="caller" type="hidden" class="asm-personchooser" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Victim") + '</td>',
                '<td>',
                '<input id="victim" data-post="victim" type="hidden" class="asm-personchooser" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Suspect") + '</td>',
                '<input id="owner" data-post="owner" type="hidden" class="asm-personchooser" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="dispatchaddress">' + _("Dispatch Address") + '</label></td>',
                '<td>',
                '<textarea id="dispatchaddress" title="' + html.title(_("Address")) + '" data-post="dispatchaddress" rows="5" class="asm-textareafixed"></textarea>',
                '</td>',
                '</tr>',
                '<tr class="towncounty">',
                '<td><label for="dispatchtown">' + _("City") + '</label></td>',
                '<td>',
                '<input type="text" id="dispatchtown" data-post="dispatchtown" maxlength="100" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr class="towncounty">',
                '<td><label for="dispatchcounty">' + _("State") + '</label></td>',
                '<td>',
                common.iif(config.bool("USStateCodes"),
                    '<select id="dispatchcounty" data-post="dispatchcounty" class="asm-selectbox">' +
                    html.states_us_options(config.str("OrganisationCounty")) + '</select>',
                    '<input type="text" id="dispatchcounty" data-post="dispatchcounty" maxlength="100" ' + 
                    'class="asm-textbox" />'),
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="dispatchpostcode">' + _("Zipcode") + '</label></td>',
                '<td>',
                '<input type="text" id="dispatchpostcode" data-post="dispatchpostcode" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="pickuplocation">' + _("Pickup Location") + '</label></td>',
                '<td><select id="pickuplocation" data-post="pickuplocation" class="asm-selectbox">',
                '<option value="0"></option>',
                html.list_to_options(controller.pickuplocations, "ID", "LOCATIONNAME"),
                '</select></td>',
                '</tr>',
                '<tr id="jurisdictionrow">',
                '<td><label for="jurisdiction">' + _("Jurisdiction") + '</label></td>',
                '<td>',
                '<select id="jurisdiction" data="jurisdiction" class="asm-selectbox">',
                html.list_to_options(controller.jurisdictions, "ID", "JURISDICTIONNAME"),
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
                '<div class="centered">',
                '<input type="hidden" data-post="species" value="' + config.integer("AFDefaultSpecies") + '" />',
                '<button id="addedit">' + html.icon("call") + ' ' + _("Create and edit") + '</button>',
                '<button id="add">' + html.icon("call") + ' ' + _("Create") + '</button>',
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
                if (!validate.notblank([ "incidentdate", "incidenttime" ])) { return false; }
                if (!validate.validtime([ "incidenttime", "calltime" ])) { return false; }
                // mandatory additional fields
                if (!additional.validate_mandatory()) { return false; }
                return true;
            };
            const add_incident = async function(mode) {
                if (!validation()) { 
                    $("#asm-content button").button("enable"); 
                    return; 
                }
                try {
                    header.show_loading(_("Creating..."));
                    let formdata = $("input, textarea, select").not(".chooser").toPOST();
                    let incidentid = await common.ajax_post("incident_new", formdata);
                    if (mode == "addedit") {
                        common.route("incident?id=" + incidentid);
                    }
                    else if (mode == "add") {
                        header.show_info(_("Incident {0} successfully created.").replace("{0}", incidentid));
                    }
                }
                finally {
                    $("#asm-content button").button("enable");
                }
            };

            $("#add").button().click(function() {
                $("#asm-content button").button("disable");
                add_incident("add");
            });

            $("#addedit").button().click(function() {
                $("#asm-content button").button("disable");
                add_incident("addedit");
            });

            $("#reset").button().click(function() {
                incident_new.reset();
            });

            $("#dispatchtown").autocomplete({ source: controller.towns });
            $("#dispatchtown").blur(function() {
                if ($("#dispatchcounty").val() == "") {
                    $("#dispatchcounty").val(controller.towncounties[$("#dispatchtown").val()]);
                }
            });
            if (!config.bool("USStateCodes")) { $("#dispatchcounty").autocomplete({ source: controller.counties }); }

            if (!config.bool("MultiSiteEnabled")) {
                $("#siterow").hide();
            }
            else {
                $("#site").select("value", asm.siteid);
            }

            if (!config.bool("IncidentPermissions")) {
                $("#viewrolesrow").hide();
            }

        },

        sync: function() {
            incident_new.reset();
        },

        destroy: function() {
            common.widget_destroy("#owner");
            common.widget_destroy("#caller", "personchooser");
            common.widget_destroy("#victim", "personchooser");
        },

        reset: function() {
            $("#dispatchaddress, #dispatchtown, #dispatchcounty, #dispatchpostcode").val("").change();
            if (config.bool("USStateCodes")) { $("#dispatchcounty").select("value", config.str("OrganisationCounty")); }
            $(".asm-checkbox").prop("checked", false).change();
            $(".asm-personchooser").personchooser("clear");
            $("#incidentdate").val(format.date(new Date()));
            $("#incidenttime").val(format.time(new Date()));
            $("#calldate").val(format.date(new Date()));
            $("#calltime").val(format.time(new Date()));
            $("#calltaker").select("value", asm.user);
            $("#incidenttype").select("value", config.str("DefaultIncidentType"));
            $("#jurisdiction").select("value", config.str("DefaultJurisdiction"));

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");
        },

        name: "incident_new",
        animation: "newdata",
        autofocus: "#incidenttype",
        title: function() { return _("Report a new incident"); },
        routes: {
            "incident_new": function() { common.module_loadandstart("incident_new", "incident_new"); }
        }

    };

    common.module_register(incident_new);

});
