/*global $, jQuery, _, additional, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const incident_new = {

        render: function() {
            return [
                html.content_header(_("Report a new incident")),
                '<div id="incident-warnings"></div>',
                tableform.fields_render([
                    { post_field: "incidenttype", type: "select", label: _("Type"), options: { displayfield: "INCIDENTNAME", rows: controller.incidenttypes }},
                    { post_field: "viewroles", type: "select", label: _("View Roles"), 
                        callout: _("Only allow users with one of these roles to view this incident"),
                        options: { displayfield: "ROLENAME", rows: controller.roles }},
                    { post_field: "incident", type: "datetime", label: _("Incident Date/Time"), halfsize: true }, 
                    { post_field: "callnotes", type: "textarea", label: _("Notes"), rows: 3, classes: "asm-textareafixed" },
                    { post_field: "call", type: "datetime", label: _("Call Date/Time"), halfsize: true }, 
                    { post_field: "calltaker", type: "select", label: _("Taken By"), options: { displayfield: "USERNAME", valuefield: "USERNAME", rows: controller.users}},
                    { post_field: "caller", type: "person", label: _("Caller"), colclasses: "bottomborder" },
                    { post_field: "victim", type: "person", label: _("Victim"), colclasses: "bottomborder" },
                    { post_field: "owner", type: "person", label: _("Suspect") },
                    { post_field: "dispatchaddress", type: "textarea", label: _("Dispatch Address"), rows: 5, classes: "asm-textareafixed" },
                    { post_field: "dispatchtown", type: "text", label: _("City"), maxlength: 100 },
                    common.iif(config.bool("USStateCodes"),
                        { post_field: "dispatchcounty", type: "select", label: _("State"), options: html.states_us_options(config.str("OrganisationCounty")) },
                        { post_field: "dispatchcounty", type: "text", label: _("State"), maxlength: 100 }),
                    { post_field: "dispatchpostcode", type: "text", label: _("Zipcode") },
                    { post_field: "pickuplocation", type: "select", label: _("Pickup Location"), 
                        options: { displayfield: "LOCATIONNAME", rows: controller.pickuplocations, prepend: '<option value="0"></option>'}},
                    { post_field: "jurisdiction", type: "select", label: _("Jurisdiction"), 
                        options: { displayfield: "JURISDICTIONNAME", rows: controller.jurisdictions }},
                    { post_field: "site", type: "select", label: _("Site"), 
                        options: { displayfield: "SITENAME", rows: controller.sites, prepend: '<option value="0">' + _("(all)") + '</option>' }},
                    { type: "additional", markup: additional.additional_new_fields(controller.additional) },
                    { type: "raw", markup: '<input type="hidden" data-post="species" value="' + config.integer("AFDefaultSpecies") + '" />' }
                ], { full_width: false }),
                tableform.buttons_render([
                   { id: "addedit", icon: "call", text: _("Create and edit") },
                   { id: "add", icon: "call", text: _("Create") },
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

            $("#button-add").button().click(function() {
                $("#asm-content button").button("disable");
                add_incident("add");
            });

            $("#button-addedit").button().click(function() {
                $("#asm-content button").button("disable");
                add_incident("addedit");
            });

            $("#button-reset").button().click(function() {
                incident_new.reset();
            });

            $("#caller").personchooser().bind("personchooserchange", function(event, rec) { 
                // Default dispatch to the caller address if it's not set
                if (!$("#dispatchaddress").val()) {
                    $("#dispatchaddress").val(rec.OWNERADDRESS);
                    $("#dispatchtown").val(rec.OWNERTOWN);
                    $("#dispatchcounty").val(rec.OWNERCOUNTY);
                    $("#dispatchpostcode").val(rec.OWNERPOSTCODE);
                }
            });

            $("#owner").personchooser().bind("personchooserchange", async function(event, rec) {
                // Warn if the suspect is flagged as dangerous
                $("#incident-warnings").empty();
                if (rec.ISDANGEROUS) {
                    $("#incident-warnings").html(html.error(_("This suspect has been flagged as dangerous")));
                }
                // Default dispatch to the suspect address if not set
                if (!$("#dispatchaddress").val()) {
                    $("#dispatchaddress").val(rec.OWNERADDRESS);
                    $("#dispatchtown").val(rec.OWNERTOWN);
                    $("#dispatchcounty").val(rec.OWNERCOUNTY);
                    $("#dispatchpostcode").val(rec.OWNERPOSTCODE);
                }
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
            validate.indicator([ "incident", "call" ]);
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
