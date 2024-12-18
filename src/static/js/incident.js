/*global $, jQuery, _, asm, additional, common, config, controller, dlgfx, edit_header, format, header, html, mapping, tableform, validate */

$(function() {

    "use strict";

    const incident = {

        render_details: function() {
            return [
                '<h3><a href="#">' + _("Details") + '</a></h3>',
                '<div>',
                tableform.fields_render([
                    { type: "raw", label: _("Number"), markup: '<span class="asm-waitinglist-number">' + format.padleft(controller.incident.ACID, 6) + '</span>' },
                    { post_field: "incidentcode", json_field: "INCIDENTCODE", type: "text", label: _("Code") },
                    { post_field: "site", json_field: "SITEID", type: "select", label: _("Site"), 
                        options: { displayfield: "SITENAME", rows: controller.sites, prepend: '<option value="0">' + _("(all)") + '</option>' }},
                    { post_field: "incidenttype", json_field: "INCIDENTTYPEID", type: "select", label: _("Type"), 
                        options: { displayfield: "INCIDENTNAME", rows: controller.incidenttypes }},
                    { post_field: "viewroles", json_field: "VIEWROLEIDS", type: "selectmulti", label: _("View Roles"), 
                        callout: _("Only allow users with one of these roles to view this incident"),
                        options: { displayfield: "ROLENAME", rows: controller.roles }},
                    { post_field: "incident", json_field: "INCIDENTDATETIME", type: "datetime", label: _("Incident Date/Time"), halfsize: true }, 
                    { post_field: "callnotes", json_field: "CALLNOTES", type: "textarea", label: _("Notes"), rows: 3 },
                    { post_field: "completed", json_field: "COMPLETEDDATE", type: "datetime", label: _("Completion Date/Time"), halfsize: true },
                    { post_field: "completedtype", json_field: "INCIDENTCOMPLETEDID", type: "select", 
                        options: { displayfield: "COMPLETEDNAME", rows: controller.completedtypes, prepend: '<option value="0"> </option>' }},
                    { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 16) },
                    { type: "nextcol" },
                    { post_field: "call", json_field: "CALLDATETIME", type: "datetime", label: _("Call Date/Time"), halfsize: true },
                    { post_field: "calltaker", json_field: "CALLTAKER", type: "select", 
                        options: { displayfield: "USERNAME", valuefield: "USERNAME", rows: controller.users, prepend: '<option> </option>' }},
                    { post_field: "caller", json_field: "CALLERID", type: "person", label: _("Caller"), colclasses: "bottomborder" },
                    { post_field: "victim", json_field: "VICTIMID", type: "person", label: _("Victim") }
                ]),
                '</div>'
            ].join("\n");
        },

        render_dispatch: function() {
            return [
                '<h3><a href="#">' + _("Dispatch") + '</a></h3>',
                '<div>',
                tableform.fields_render([
                    { post_field: "dispatchaddress", json_field: "DISPATCHADDRESS", type: "textarea", label: _("Address"), rows: 5, classes: "asm-textareafixed" },
                    { post_field: "dispatchtown", json_field: "DISPATCHTOWN", type: "text", label: _("City"), maxlength: 100, rowclasses: "towncounty" },
                    common.iif(config.bool("USStateCodes"),
                        { post_field: "dispatchcounty", json_field: "DISPATCHCOUNTY", type: "select", label: _("State"), options: html.states_us_options(), rowclasses: "towncounty" },
                        { post_field: "dispatchcounty", json_field: "DISPATCHCOUNTY", type: "text", label: _("State"), maxlength: 100, rowclasses: "towncounty" }),
                    { post_field: "dispatchpostcode", json_field: "DISPATCHPOSTCODE", type: "text", label: _("Zipcode") },
                    { post_field: "dispatchlatlong", json_field: "DISPATCHLATLONG", type: "latlong", label: _("Latitude/Longitude"), 
                        callout: _("Right-click on the map to change the marker location") },
                    { post_field: "pickuplocation", json_field: "PICKUPLOCATIONID", type: "select", label: _("Pickup Location"), 
                        options: { displayfield: "LOCATIONNAME", rows: controller.pickuplocations, prepend: '<option value="0"></option>'}},
                    { post_field: "jurisdiction", json_field: "JURISDICTIONID", type: "select", label: _("Jurisidiction"), 
                        options: { displayfield: "JURISDICTIONNAME", rows: controller.jurisdictions }},
                    { type: "nextcol" },
                    { post_field: "dispatchedaco", json_field: "DISPATCHEDACO", type: "selectmulti", label: _("Dispatched ACO"), 
                        options: { displayfield: "USERNAME", valuefield: "USERNAME", rows: controller.acos }},
                    { post_field: "dispatch", json_field: "DISPATCHDATETIME", type: "datetime", label: _("Dispatch Date/Time"), halfsize: true },
                    { post_field: "responded", json_field: "RESPONDEDDATETIME", type: "datetime", label: _("Responded Date/Time"), halfsize: true },
                    { post_field: "followup", json_field: "FOLLOWUPDATETIME", type: "datetime", label: _("Followup Date/Time"), halfsize: true,
                        xmarkup: tableform.render_check({ post_field: "followupcomplete", json_field: "FOLLOWUPCOMPLETE", tooltip: _("Complete"), justwidget: true }) },
                    { post_field: "followup2", json_field: "FOLLOWUPDATETIME2", type: "datetime", label: _("Followup Date/Time"), halfsize: true,
                        xmarkup: tableform.render_check({ post_field: "followupcomplete2", json_field: "FOLLOWUPCOMPLETE2", tooltip: _("Complete"), justwidget: true }) },
                    { post_field: "followup3", json_field: "FOLLOWUPDATETIME3", type: "datetime", label: _("Followup Date/Time"), halfsize: true, 
                        xmarkup: tableform.render_check({ post_field: "followupcomplete3", json_field: "FOLLOWUPCOMPLETE3", tooltip: _("Complete"), justwidget: true }) },
                    { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 17) },
                    { type: "nextcol" },
                    { type: "raw", fullrow: true, markup: '<div id="embeddedmap" style="z-index: 1; width: 100%; height: 300px; color: #000"></div>' }
                ]),
                '</div>'
            ].join("\n");
        },

        render_owner: function() {
            return [
                '<h3><a href="#">' + _("Suspect/Animal") + '</a></h3>',
                '<div>',
                tableform.fields_render([
                    { post_field: "owner", json_field: "OWNERID", type: "person", label: _("Suspect 1"), colclasses: "bottomborder" },
                    { post_field: "owner", json_field: "OWNER2ID", type: "person", label: _("Suspect 2"), colclasses: "bottomborder" },
                    { post_field: "owner", json_field: "OWNER3ID", type: "person", label: _("Suspect 3") },
                    { type: "nextcol" },
                    { post_field: "species", json_field: "SPECIESID", type: "select", label: _("Species"), 
                        options: { displayfield: "SPECIESNAME", rows: controller.species }}, 
                    { post_field: "sex", json_field: "SEX", type: "select", label: _("Sex"), 
                        options: { displayfield: "SEX", rows: controller.sexes }},
                    { post_field: "agegroup", json_field: "AGEGROUP", type: "select", label: _("Age Group"), 
                        options: '<option value="Unknown">' + _("(unknown)") + '</option>' + html.list_to_options(controller.agegroups) },
                    { post_field: "animaldescription", json_field: "ANIMALDESCRIPTION", type: "textarea", label: _("Description") },
                    { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 18) },
                    { type: "raw", fullrow: true, markup: 
                        '<p class="asm-menu-category">' + _("Animals") + 
                        ' <button id="button-linkanimal">' + _("Link an animal") + '</button></p>' +
                        '<div id="animallist"></div>' }
                ]),
                '</div>'
            ].join("\n");
        },

        load_animallinks: function() {
            let h = [];
            $.each(controller.animallinks, function(i, v) {
                h.push('<span class="linkedanimal"><button data="' + v.ID + '">' + _("Remove") + '</button> ' 
                    + html.animal_link(v, { emblemsright: true, showlocation: false }) + '</span><br />');
            });
            $("#animallist").empty().html(h.join("\n"));
            $("#animallist button").button({ icons: { primary: "ui-icon-trash" }, text: false })
                .click(async function() {
                    let node = $(this),
                        animalid = node.attr("data");
                    node.button("disable");
                    await common.ajax_post("incident", "mode=linkanimaldelete&id=" + controller.incident.ID + "&animalid=" + animalid);
                    node.closest(".linkedanimal").fadeOut().then().remove();
                });
        },

        render: function() {
            return [
                '<div id="button-document-body" class="asm-menu-body">',
                '<ul class="asm-menu-list">',
                edit_header.template_list(controller.templates, "ANIMALCONTROL", controller.incident.ID),
                '</ul>',
                '</div>',
                '<div id="dialog-clone-confirm" style="display: none" title="' + html.title(_("Clone")) + '">',
                '<p><span class="ui-icon ui-icon-alert"></span> ' + _("Clone this incident?") + '</p>',
                '</div>',
                '<div id="emailform"></div>',
                '<div id="dialog-linkanimal" style="display: none" title="' + html.title(_("Link an animal")) + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="linkanimal">' + _("Animal") + '</label></td>',
                '<td><input id="linkanimal" data="linkanimal" type="hidden" class="asm-animalchooser" /></td>',
                '</tr>',
                '</table>',
                '</div>',
                edit_header.incident_edit_header(controller.incident, "details", controller.tabcounts),
                tableform.buttons_render([
                    { id: "save", text: _("Save"), icon: "save", tooltip: _("Save this incident") },
                    { id: "clone", text: _("Clone"), icon: "copy", tooltip: _("Clone this incident") },
                    { id: "delete", text: _("Delete"), icon: "delete", tooltip: _("Delete this incident") },
                    //{ id: "toanimal", text: _("Create Animal"), icon: "animal-add", tooltip: _("Create a new animal from this incident") }
                    { id: "document", text: _("Document"), type: "buttonmenu", icon: "document", tooltip: _("Generate a document from this incident") },
                    { id: "email", text: _("Email"), icon: "email", tooltip: _("Email incident notes to ACO") },
                    { id: "dispatch", text: _("Dispatch"), icon: "calendar", perm: "cacd", tooltip: _("Mark dispatched now") },
                    { id: "respond", text: _("Respond"), icon: "calendar", perm: "cacr", tooltip: _("Mark responded now") },
                    { id: "map", text: _("Map"), icon: "map", tooltip: _("Find this address on a map") }
                ]),
                '<div id="asm-details-accordion">',
                this.render_details(),
                '<h3 id="asm-additional-accordion"><a href="#">' + _("Additional") + '</a></h3>',
                '<div>',
                additional.additional_fields(controller.additional),
                '</div>',
                this.render_dispatch(),
                this.render_owner(),
                html.audit_trail_accordion(controller),
                '</div> <!-- accordion -->',
                html.content_footer()
            ].join("\n");
        },

        enable_widgets: function() {
            // Hide additional accordion section if there aren't
            // any additional fields declared
            let ac = $("#asm-additional-accordion");
            let an = ac.next();
            if (an.find(".additional").length == 0) {
                ac.hide(); an.hide();
            }

            if (!common.has_permission("caci")) { $("#button-save").hide(); }
            if (!common.has_permission("aaci")) { $("#button-clone").hide(); }
            if (!common.has_permission("aa")) { $("#button-toanimal").hide(); }
            if (!common.has_permission("daci")) { $("#button-delete").hide(); }
            if (!common.has_permission("gaf")) { $("#button-document").hide(); }

            // Hide the site chooser if multi-site is off
            $("#siterow").toggle( config.bool("MultiSiteEnabled") );
            
            $("#dispatchlatlongrow").toggle( config.bool("ShowLatLong") );

            // Hide the view roles controls if incident permissions are off
            if (!config.bool("IncidentPermissions")) {
                $("#viewrolesrow").hide();
            }

            // If a dispatch time is already set, disable the dispatch button
            if ($("#dispatchtime").val()) {
                $("#button-dispatch").button("disable");
            }
            else {
                $("#button-dispatch").button("enable");
            }
            // If a responded time is already set, disable the respond button
            if ($("#respondedtime").val()) {
                $("#button-respond").button("disable");
            }
            else {
                $("#button-respond").button("enable");
            }

        },

        get_map_url: function() {
            let add = $("#dispatchaddress").val().replace("\n", ",");
            let town = $("#dispatchtown").val();
            let county = $("#dispatchcounty").val();
            let postcode = $("#dispatchpostcode").val();
            let map = add;
            if (town != "") { map += "," + town; }
            if (county != "") { map += "," + county; }
            if (postcode != "") { map += "," + postcode; }
            map = encodeURIComponent(map);
            return map;
        },

        show_mini_map: function() {
            setTimeout(() => {
                mapping.draw_map("embeddedmap", 15, controller.incident.DISPATCHLATLONG, [{ 
                    latlong: controller.incident.DISPATCHLATLONG, popuptext: controller.incident.DISPATCHADDRESS, popupactive: true }]);
            }, 50);
        },

        validation: function() {

            // Remove any previous errors
            header.hide_error();
            validate.reset();

            // incident date
            if (common.trim($("#incidentdate").val()) == "") {
                header.show_error(_("Incident date cannot be blank"));
                $("#asm-details-accordion").accordion("option", "active", 0);
                validate.highlight("incidentdate");
                return false;
            }

            // times
            if (!validate.validtime([ "incidenttime", "calltime", "completedtime", "dispatchtime", "respondedtime", 
                "followuptime", "followup2time", "followup3time" ])) { 
                return false; 
            }

            // any additional fields that are marked mandatory
            if (!additional.validate_mandatory()) {
                return false;
            }

            return true;
        },

        bind: function() {

            $(".asm-tabbar").asmtabs();
            $("#emailform").emailform();

            $("#asm-details-accordion").accordion({
                heightStyle: "content",
                activate: function(event, ui) {
                    // Show the minimap when the dispatch panel activates.
                    // No map api likes being loaded in a hidden div and this avoids that
                    if (config.bool("ShowPersonMiniMap") && $("#dispatchaddress").val()) {
                        if ($("#asm-details-accordion").accordion("option", "active") == 2) {
                            incident.show_mini_map();
                        }
                    }
                }
            }); 

            validate.save = function(callback) {
                if (!incident.validation()) { header.hide_loading(); return; }
                validate.dirty(false);
                let formdata = "mode=save" +
                    "&id=" + $("#incidentid").val() + 
                    "&recordversion=" + controller.incident.RECORDVERSION + 
                    "&" + $("input, select, textarea").not(".chooser").toPOST();
                common.ajax_post("incident", formdata)
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

            $("#button-clone").button().click(async function() {
                await tableform.show_okcancel_dialog("#dialog-clone-confirm", _("Clone"));
                let formdata = "mode=clone&id=" + controller.incident.ID;
                header.show_loading(_("Cloning..."));
                let response = await common.ajax_post("incident", formdata);
                header.hide_loading();
                common.route("incident?id=" + response + "&cloned=true"); 
            });

            $("#button-toanimal").button().click(async function() {
                $("#button-toanimal").button("disable");
                let formdata = "mode=toanimal&id=" + $("#incidentid").val();
                let result = await common.ajax_post("incident", formdata);
                common.route("animal?id=" + result); 
            });

            $("#button-email").button().click(function() {
                let emailaddress = "", emailname = "";
                $.each(controller.users, function(i, v) {
                    if (common.array_in(v.USERNAME, String($("#dispatchedaco").val()).split(","))) {
                        if (emailaddress != "") { emailaddress += ", "; }
                        emailname = v.REALNAME;
                        emailaddress += v.EMAILADDRESS;
                    }
                });
                let i = controller.incident;
                let msg = [ 
                    _("Type") + ": " + i.INCIDENTNAME,
                    _("Date/Time") + ": " + format.date(i.INCIDENTDATETIME) + " " + format.time(i.INCIDENTDATETIME),
                    _("Address") + ": " + i.DISPATCHADDRESS + ' ' + i.DISPATCHTOWN + ' ' + i.DISPATCHCOUNTY + ' ' + i.DISPATCHPOSTCODE,
                    _("Notes") + ": " + common.nulltostr(i.CALLNOTES),
                    _("Caller") + ": " + common.nulltostr(i.CALLERNAME),
                    _("Victim") + ": " + common.nulltostr(i.VICTIMNAME),
                    _("Suspect") + ": " + common.nulltostr(i.OWNERNAME1)
                ].join("\n");
                let subject = html.decode(_("Dispatch {0}: {1}")
                        .replace("{0}", format.padleft(controller.incident.ACID, 6))
                        .replace("{1}", $("#dispatchaddress").val()) );
                $("#emailform").emailform("show", {
                    title: _("Email incident notes to ACO"),
                    post: "incident",
                    formdata: "mode=email&incidentid=" + controller.incident.ID,
                    animalcontrolid: controller.incident.ID,
                    name: common.iif(emailaddress.indexOf(",") == -1, emailname, ""),
                    email: emailaddress,
                    logtypes: controller.logtypes,
                    message: "<p>" + common.replace_all(html.decode(msg), "\n", "<br/>") + "</p>",
                    subject: subject,
                    templates: controller.templatesemail
                });
            });

            $("#button-delete").button().click(async function() {
                await tableform.delete_dialog(null, _("This will permanently remove this incident, are you sure?"));
                let formdata = "mode=delete&id=" + $("#incidentid").val();
                await common.ajax_post("incident", formdata);
                $("#dialog-delete").dialog("close"); 
                common.route("main");
            });

            $("#button-dispatch").button().click(function() {
                if (!$("#dispatchtime").val()) {
                    $("#dispatchdate").date("today");
                    $("#dispatchtime").val(format.time(new Date()));
                    $("#asm-details-accordion").accordion("option", "active", 2);
                    $("#button-dispatch").button("disable");
                    header.show_loading(_("Saving..."));
                    validate.save(function() {
                        common.route_reload();
                    });
                }
            });

            // Setup the document menu button
            $("#button-document").asmmenu();

            $("#button-respond").button().click(function() {
                if (!$("#respondedtime").val()) {
                    $("#respondeddate").date("today");
                    $("#respondedtime").val(format.time(new Date()));
                    $("#asm-details-accordion").accordion("option", "active", 2);
                    $("#button-respond").button("disable");
                    header.show_loading(_("Saving..."));
                    validate.save(function() {
                        common.route_reload();
                    });
                }
            });

            $("#button-map").button().click(function() {
                let mapq = incident.get_map_url();
                let maplinkref = String(asm.maplink).replace("{0}", mapq);
                window.open(maplinkref, "_blank");
            });

            $("#button-linkanimal")
                .button({ icons: { primary: "ui-icon-link" }, text: false })
                .click(async function() {
                    $("#linkanimal").animalchooser("clear");
                    await tableform.show_okcancel_dialog("#dialog-linkanimal", _("Link"), { notzero: [ "linkanimal" ] });
                    let a = $("#linkanimal").animalchooser("get_selected");
                    await common.ajax_post("incident", "mode=linkanimaladd&id=" + controller.incident.ID + "&animalid=" + a.ID);
                    controller.animallinks.push(a);
                    incident.load_animallinks();
                });

            $("#completedtype").change(function() {
                if (!$("#completeddate").val()) {
                    $("#completeddate").val(format.date(new Date()));
                    $("#completedtime").val(format.time(new Date()));
                }
                if ($("#completedtype").val() == "0") {
                    $("#completeddate, #completedtime").val("");
                }
            });

        },

        sync: function() {

            // If any of the dispatched ACOs are not in the list (can happen if a
            // user account is later deleted), add it to the aco list so that it doesn't
            // disappear.
            $.each(controller.incident.DISPATCHEDACO.split(","), function(ia, aco) {
                let acoinlist = false;
                $.each(controller.users, function(i, v) {
                    if (v.USERNAME == aco) { acoinlist = true; return false; }
                });
                if (!acoinlist) {
                    $("#dispatchedaco").append("<option value=\"" + html.title(aco) + "\">" + aco + "</option>");
                }
            });

            // Load the data into the controls for the screen
            $("#asm-content input, #asm-content select, #asm-content textarea").fromJSON(controller.incident);

            // Update the lat/long
            $(".asm-latlong").latlong("load");

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");

            // Update on-screen fields from the data and display the screen
            incident.enable_widgets();
            incident.load_animallinks();

            // Dirty handling
            validate.bind_dirty([ "incident_" ]);
            validate.indicator([ "incidentdate", "calldate" ]);

        },

        destroy: function() {
            validate.unbind_dirty();
            common.widget_destroy("#animal");
            common.widget_destroy("#owner");
            common.widget_destroy("#owner2");
            common.widget_destroy("#owner3");
            common.widget_destroy("#caller", "personchooser");
            common.widget_destroy("#victim", "personchooser");
            common.widget_destroy("#emailform");
            common.widget_destroy("#dialog-linkanimal");
            common.widget_destroy("#dialog-clone-confirm");
            common.widget_destroy("#emailbody", "richtextarea");
        },

        name: "incident",
        animation: "formtab",
        autofocus: "#incidenttype",
        title: function() {
            return common.substitute(_("Incident {0}, {1}: {2}"), {
                0: controller.incident.ACID, 1: controller.incident.INCIDENTNAME, 2: format.date(controller.incident.INCIDENTDATETIME)});
        },
        routes: {
            "incident": function() { 
                common.module_loadandstart("incident", "incident?id=" + this.qs.id);
            }
        }

    };

    common.module_register(incident);

});

