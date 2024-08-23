/*global $, jQuery, _, asm, additional, common, config, controller, dlgfx, edit_header, format, header, html, mapping, tableform, validate */

$(function() {

    "use strict";

    const incident = {

        render_details: function() {
            return [
                '<h3><a href="#">' + _("Details") + '</a></h3>',
                '<div>',
                '<div class="row">',
                '<div class="col-sm">',
                // first col
                '<table width="100%">',
                '<tr>',
                '<td>' + _("Number") + '</td>',
                '<td><span class="asm-waitinglist-number">',
                format.padleft(controller.incident.ACID, 6),
                '</span></td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Code") + '</td>',
                '<td><input id="incidentcode" data-json="INCIDENTCODE" data-post="incidentcode" class="asm-textbox" /></td>',
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
                '<td><label for="incidenttype">' + _("Type") + '</label></td>',
                '<td><select id="incidenttype" data-json="INCIDENTTYPEID" data-post="incidenttype" class="asm-selectbox">',
                html.list_to_options(controller.incidenttypes, "ID", "INCIDENTNAME"),
                '</td>',
                '</tr>',
                '<tr id="viewrolesrow">',
                '<td><label for="viewroles">' + _("View Roles") + '</label>',
                '<span id="callout-viewroles" class="asm-callout">' + _("Only allow users with one of these roles to view this incident") + '</span>',
                '</td>',
                '<td><select id="viewroles" data-json="VIEWROLEIDS" data-post="viewroles" class="asm-bsmselect" multiple="multiple">',
                html.list_to_options(controller.roles, "ID", "ROLENAME"),
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="incidentdate">' + _("Incident Date/Time") + '</label></td>',
                '<td><input id="incidentdate" data-json="INCIDENTDATETIME" data-post="incidentdate" class="asm-halftextbox asm-datebox" />',
                '<input id="incidenttime" data-json="INCIDENTDATETIME" data-post="incidenttime" class="asm-halftextbox asm-timebox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="callnotes">' + _("Notes") + '</label></td>',
                '<td><textarea id="callnotes" data-json="CALLNOTES" data-post="callnotes" class="asm-textarea" rows="3"></textarea></td>',
                '</tr>',
                '<tr>',
                '<td><label for="completeddate">' + _("Completion Date/Time") + '</label></td>',
                '<td><input id="completeddate" data-json="COMPLETEDDATE" data-post="completeddate" class="asm-halftextbox asm-datebox" />',
                '<input id="completedtime" data-json="COMPLETEDDATE" data-post="completedtime" class="asm-halftextbox asm-timebox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="completedtype">' + _("Completion Type") + '</label></td>',
                '<td><select id="completedtype" data-json="INCIDENTCOMPLETEDID" data-post="completedtype" class="asm-selectbox">',
                '<option value="0"> </option>',
                html.list_to_options(controller.completedtypes, "ID", "COMPLETEDNAME"),
                '</td>',
                '</tr>',
                additional.additional_fields_linktype(controller.additional, 16), 
                '</table>',
                '</div>', // col-sm
                // second col
                '<div class="col-sm">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="calldate">' + _("Call Date/Time") + '</label></td>',
                '<td><input id="calldate" data-json="CALLDATETIME" data-post="calldate" class="asm-halftextbox asm-datebox" />',
                '<input id="calltime" data-json="CALLDATETIME" data-post="calltime" class="asm-halftextbox asm-timebox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="calltaker">' + _("Taken By") + '</label></td>',
                '<td><select id="calltaker" data-json="CALLTAKER" data-post="calltaker" class="asm-selectbox">',
                '<option> </option>',
                html.list_to_options(controller.users, "USERNAME", "USERNAME"),
                '</td>',
                '<tr>',
                '<td>' + _("Caller") + '</td>',
                '<td>',
                '<input id="caller" data-json="CALLERID" data-post="caller" type="hidden" class="asm-personchooser" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Victim") + '</td>',
                '<td>',
                '<input id="victim" data-json="VICTIMID" data-post="victim" type="hidden" class="asm-personchooser" />',
                '</td>',
                '</tr>',
                '</table>',
                '</div>', // col-sm
                '</div>', // row
                '</div>', // end accordion section
            ].join("\n");
        },

        render_dispatch: function() {
            return [
                '<h3><a href="#">' + _("Dispatch") + '</a></h3>',
                '<div>',
                '<div class="row">',
                '<div class="col-sm">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="dispatchaddress">' + _("Address") + '</label></td>',
                '<td>',
                '<textarea id="dispatchaddress" title="' + html.title(_("Address")) + '" data-json="DISPATCHADDRESS" data-post="dispatchaddress" rows="5" class="asm-textareafixed"></textarea>',
                '</td>',
                '</tr>',
                '<tr class="towncounty">',
                '<td><label for="dispatchtown">' + _("City") + '</label></td>',
                '<td>',
                '<input type="text" id="dispatchtown" data-json="DISPATCHTOWN" data-post="dispatchtown" maxlength="100" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr class="towncounty">',
                '<td><label for="dispatchcounty">' + _("State") + '</label></td>',
                '<td>',
                common.iif(config.bool("USStateCodes"),
                    '<select id="dispatchcounty" data-json="DISPATCHCOUNTY" data-post="dispatchcounty" class="asm-selectbox">' +
                    html.states_us_options() + '</select>',
                    '<input type="text" id="dispatchcounty" data-json="DISPATCHCOUNTY" data-post="dispatchcounty" maxlength="100" ' + 
                    'class="asm-textbox" />'),
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="dispatchpostcode">' + _("Zipcode") + '</label></td>',
                '<td>',
                '<input type="text" id="dispatchpostcode" data-json="DISPATCHPOSTCODE" data-post="dispatchpostcode" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr id="dispatchlatlongrow">',
                '<td><label for="dispatchlatlong">' + _("Latitude/Longitude"),
                '<span class="asm-callout">' + _("Right-click on the map to change the marker location") + '</span>',
                '</label></td>',
                '<td><input type="text" class="asm-latlong" id="dispatchlatlong" data-json="DISPATCHLATLONG" data-post="dispatchlatlong" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="pickuplocation">' + _("Pickup Location") + '</label></td>',
                '<td><select id="pickuplocation" data-json="PICKUPLOCATIONID" data-post="pickuplocation" class="asm-selectbox">',
                '<option value="0"></option>',
                html.list_to_options(controller.pickuplocations, "ID", "LOCATIONNAME"),
                '</select></td>',
                '</tr>',
                '<tr id="jurisdictionrow">',
                '<td><label for="jurisdiction">' + _("Jurisdiction") + '</label></td>',
                '<td>',
                '<select id="jurisdiction" data-json="JURISDICTIONID" data-post="jurisdiction" class="asm-selectbox">',
                html.list_to_options(controller.jurisdictions, "ID", "JURISDICTIONNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '</table>',
                '</div>', // col-sm
                '<div class="col-sm">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="dispatchedaco">' + _("Dispatched ACO") + '</label></td>',
                '<td><select id="dispatchedaco" data-json="DISPATCHEDACO" data-post="dispatchedaco" class="asm-bsmselect" multiple="multiple">',
                html.list_to_options(controller.acos, "USERNAME", "USERNAME"),
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="dispatchdate">' + _("Dispatch Date/Time") + '</label></td>',
                '<td><span style="white-space: nowrap">',
                '<input id="dispatchdate" data-json="DISPATCHDATETIME" data-post="dispatchdate" class="asm-halftextbox asm-datebox" />',
                '<input id="dispatchtime" data-json="DISPATCHDATETIME" data-post="dispatchtime" class="asm-halftextbox asm-timebox" /></span></td>',
                '</tr>',
                '<tr>',
                '<td><label for="respondeddate">' + _("Responded Date/Time") + '</label></td>',
                '<td><span style="white-space: nowrap">',
                '<input id="respondeddate" data-json="RESPONDEDDATETIME" data-post="respondeddate" class="asm-halftextbox asm-datebox" />',
                '<input id="respondedtime" data-json="RESPONDEDDATETIME" data-post="respondedtime" class="asm-halftextbox asm-timebox" /></span></td>',
                '</tr>',
                '<tr>',
                '<td><label for="followupdate">' + _("Followup Date/Time") + '</label></td>',
                '<td><span style="white-space: nowrap">',
                '<input id="followupdate" data-json="FOLLOWUPDATETIME" data-post="followupdate" class="asm-halftextbox asm-datebox" />',
                '<input id="followuptime" data-json="FOLLOWUPDATETIME" data-post="followuptime" class="asm-halftextbox asm-timebox" />',
                '<input id="followupcomplete" data-json="FOLLOWUPCOMPLETE" data-post="followupcomplete" class="asm-checkbox" type="checkbox" title="' + html.title(_("Complete")) + '" /></span>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="followupdate2">' + _("Followup Date/Time") + '</label></td>',
                '<td><span style="white-space: nowrap">',
                '<input id="followupdate2" data-json="FOLLOWUPDATETIME2" data-post="followupdate2" class="asm-halftextbox asm-datebox" />',
                '<input id="followuptime2" data-json="FOLLOWUPDATETIME2" data-post="followuptime2" class="asm-halftextbox asm-timebox" />',
                '<input id="followupcomplete2" data-json="FOLLOWUPCOMPLETE2" data-post="followupcomplete2" class="asm-checkbox" type="checkbox" title="' + html.title(_("Complete")) + '" /></span>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="followupdate3">' + _("Followup Date/Time") + '</label></td>',
                '<td><span style="white-space: nowrap">',
                '<input id="followupdate3" data-json="FOLLOWUPDATETIME3" data-post="followupdate3" class="asm-halftextbox asm-datebox" />',
                '<input id="followuptime3" data-json="FOLLOWUPDATETIME3" data-post="followuptime3" class="asm-halftextbox asm-timebox" />',
                '<input id="followupcomplete3" data-json="FOLLOWUPCOMPLETE3" data-post="followupcomplete3" class="asm-checkbox" type="checkbox" title="' + html.title(_("Complete")) + '" /></span>',
                '</td>',
                '</tr>',
                additional.additional_fields_linktype(controller.additional, 17), 
                '</table>',
                '</div>', // col-sm
                // Third column, embedded map placeholder
                '<div class="col-sm">',
                '<div id="embeddedmap" style="z-index: 1; width: 100%; height: 300px; color: #000"></div>',
                '</div>', // col-sm
                '</div>', // row
                '</div>', // end accordion section
            ].join("\n");
        },

        render_owner: function() {
            return [
                '<h3><a href="#">' + _("Suspect/Animal") + '</a></h3>',
                '<div>',
                '<div class="row">',
                // left column 
                '<div class="col-sm">',
                '<table width="100%">',
                '<tr>',
                '<td>' + _("Suspect 1") + '</td>',
                '<input id="owner" data-json="OWNERID" data-post="owner" type="hidden" class="asm-personchooser" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Suspect 2") + '</td>',
                '<input id="owner2" data-json="OWNER2ID" data-post="owner2" type="hidden" class="asm-personchooser" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Suspect 3") + '</td>',
                '<input id="owner3" data-json="OWNER3ID" data-post="owner3" type="hidden" class="asm-personchooser" />',
                '</td>',
                '</tr>',
                '</table>',
                '</div>', // col-sm
                // right column
                '<div class="col-sm">',
                '<table width="100%">',
                '<td><label for="species">' + _("Species") + '</label></td>',
                '<td nowrap="nowrap">',
                '<select id="species" data-json="SPECIESID" data-post="species" class="asm-selectbox">',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="sex">' + _("Sex") + '</label></td>',
                '<td nowrap="nowrap">',
                '<select id="sex" data-json="SEX" data-post="sex" class="asm-selectbox">',
                html.list_to_options(controller.sexes, "ID", "SEX"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="agegroup">' + _("Age Group") + '</label></td>',
                '<td nowrap="nowrap">',
                '<select id="agegroup" data-json="AGEGROUP" data-post="agegroup" class="asm-selectbox">',
                '<option value="Unknown">' + _("(unknown)") + '</option>',
                html.list_to_options(controller.agegroups),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="animaldescription">' + _("Description") + '</label></td>',
                '<td><textarea id="animaldescription" data-json="ANIMALDESCRIPTION" data-post="animaldescription" class="asm-textarea"></textarea></td>',
                '</tr>',
                additional.additional_fields_linktype(controller.additional, 18), 
                '</table>',
                '<p class="asm-menu-category">' + _("Animals") + ' <button id="button-linkanimal">' + _("Link an animal") + '</button></p>',
                '<div id="animallist">',
                '</div>',
                '</div>', // col-sm
                '</div>', // row
                '</div>', // end accordion section
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
                "followuptime", "followuptime2", "followuptime3" ])) { 
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
                    formdata: "mode=email",
                    animalcontrolid: controller.incident.ID,
                    name: common.iif(emailaddress.indexOf(",") == -1, emailname, ""),
                    email: emailaddress,
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

