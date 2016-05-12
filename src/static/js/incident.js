/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, additional, common, config, controller, dlgfx, edit_header, format, geo, header, html, mapping, tableform, validate */

$(function() {

    var incident = {

        render_details: function() {
            return [
                '<h3><a href="#">' + _("Details") + '</a></h3>',
                '<div>',
                '<table width="100%">',
                '<tr>',
                '<!-- left column -->',
                '<td width="35%">',
                '<table width="100%" class="additionaltarget" data="to16">',
                '<tr>',
                '<td>' + _("Number") + '</td>',
                '<td><span class="asm-waitinglist-number">',
                format.padleft(controller.incident.ACID, 6),
                '</span></td>',
                '</tr>',
                '<tr>',
                '<td><label for="incidenttype">' + _("Type") + '</label></td>',
                '<td><select id="incidenttype" data-json="INCIDENTTYPEID" data-post="incidenttype" class="asm-selectbox">',
                html.list_to_options(controller.incidenttypes, "ID", "INCIDENTNAME"),
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
                '<td><label for="completeddate">' + _("Completion Date") + '</label></td>',
                '<td><input id="completeddate" data-json="COMPLETEDDATE" data-post="completeddate" class="asm-textbox asm-datebox" />',
                '</tr>',
                '<tr>',
                '<td><label for="completedtype">' + _("Completion Type") + '</label></td>',
                '<td><select id="completedtype" data-json="INCIDENTCOMPLETEDID" data-post="completedtype" class="asm-selectbox">',
                '<option value="0"> </option>',
                html.list_to_options(controller.completedtypes, "ID", "COMPLETEDNAME"),
                '</td>',
                '</tr>',
                '</table>',
                '</td>',
                '<!-- right column -->',
                '<td width="35%">',
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
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_dispatch: function() {
            return [
                '<h3><a href="#">' + _("Dispatch") + '</a></h3>',
                '<div>',
                '<table width="100%">',
                '<tr>',
                '<!-- left table -->',
                '<td width="35%">',
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
                '<input type="text" id="dispatchcounty" data-json="DISPATCHCOUNTY" data-post="dispatchcounty" maxlength="100" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="dispatchpostcode">' + _("Zipcode") + '</label></td>',
                '<td>',
                '<input type="text" id="dispatchpostcode" data-json="DISPATCHPOSTCODE" data-post="dispatchpostcode" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="pickuplocation">' + _("Pickup Location") + '</label></td>',
                '<td><select id="pickuplocation" data-json="PICKUPLOCATIONID" data-post="pickuplocation" class="asm-selectbox">',
                '<option value="0"></option>',
                html.list_to_options(controller.pickuplocations, "ID", "LOCATIONNAME"),
                '</select></td>',
                '</tr>',
                '<!-- end left table -->',
                '</table>',
                '<!-- Second column -->',
                '</td>',
                '<td width="30%">',
                '<table width="100%" class="additionaltarget" data="to17">',
                '<tr>',
                '<td><label for="dispatchedaco">' + _("Dispatched ACO") + '</label></td>',
                '<td><select id="dispatchedaco" data-json="DISPATCHEDACO" data-post="dispatchedaco" class="asm-selectbox">',
                '<option> </option>',
                html.list_to_options(controller.users, "USERNAME", "USERNAME"),
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
                '</table>',
                '<!-- Third column, embedded map placeholder -->',
                '</td>',
                '<td width="35%">',
                '<input type="hidden" id="latlong" data-json="DISPATCHLATLONG" data-post="dispatchlatlong" />',
                '<div id="embeddedmap" style="width: 100%; height: 300px; color: #000" />',
                '<!-- end outer table -->',
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_owner: function() {
            return [
                '<h3><a href="#">' + _("Suspect/Animal") + '</a></h3>',
                '<div>',
                '<table width="100%">',
                '<tr>',
                '<td width="50%">',
                '<!-- left table -->',
                '<table width="100%" class="additionaltarget" data="to18">',
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
                '<!-- right table -->',
                '</td>',
                '<td>',
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
                '</table>',
                '<!-- end right table -->',

                '<p class="asm-menu-category">' + _("Animals") + ' <button id="button-linkanimal">' + _("Link an animal") + '</button></p>',
                '<div id="animallist">',
                '</div>',

                '</td>',
                '</tr>',
                '</table>',

                '</div>'
            ].join("\n");
        },

        load_animallinks: function() {
            var h = [];
            $.each(controller.animallinks, function(i, v) {
                h.push('<span class="linkedanimal"><button data="' + v.ID + '">' + _("Remove") + '</button> ' 
                    + html.animal_link(v, { emblemsright: true, showlocation: false }) + '</span><br />');
            });
            $("#animallist").empty().html(h.join("\n"));
            $("#animallist button").button({ icons: { primary: "ui-icon-trash" }, text: false })
                .click(function() {
                    var node = $(this),
                        animalid = node.attr("data");
                    node.button("disable");
                    common.ajax_post("incident", "mode=linkanimaldelete&id=" + controller.incident.ID + "&animalid=" + animalid)
                        .then(function() {
                            node.closest(".linkedanimal").fadeOut().then().remove();
                        });
                });
        },

        render: function() {
            return [
                '<div id="button-document-body" class="asm-menu-body">',
                '<ul class="asm-menu-list">',
                edit_header.template_list(controller.templates, "ANIMALCONTROL", controller.incident.ID),
                '</ul>',
                '</div>',
                '<div id="dialog-email" style="display: none" title="' + html.title(_("Email incident notes to ACO"))  + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="emailfrom">' + _("From") + '</label></td>',
                '<td><input id="emailfrom" data="from" type="text" class="asm-doubletextbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="emailto">' + _("To") + '</label></td>',
                '<td><input id="emailto" data="to" type="text" class="asm-doubletextbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="emailcc">' + _("CC") + '</label></td>',
                '<td><input id="emailcc" data="cc" type="text" class="asm-doubletextbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="emailsubject">' + _("Subject") + '</label></td>',
                '<td><input id="emailsubject" data="subject" type="text" class="asm-doubletextbox" /></td>',
                '</tr>',
                '</table>',
                '<div id="emailbody" data="body" data-margin-top="24px" data-height="400px" class="asm-richtextarea"></div>',
                '</div>',
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
                    { id: "delete", text: _("Delete"), icon: "delete", tooltip: _("Delete this incident") },
                    //{ id: "toanimal", text: _("Create Animal"), icon: "animal-add", tooltip: _("Create a new animal from this incident") }
                    { id: "document", text: _("Document"), type: "buttonmenu", icon: "document", tooltip: _("Generate a document from this incident") },
                    { id: "email", text: _("Email"), icon: "email", tooltip: _("Email incident notes to ACO") },
                    { id: "dispatch", text: _("Dispatch"), icon: "calendar", tooltip: _("Mark dispatched now") },
                    { id: "respond", text: _("Respond"), icon: "calendar", tooltip: _("Mark responded now") }
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
            var ac = $("#asm-additional-accordion");
            var an = ac.next();
            if (an.find(".additional").length == 0) {
                ac.hide(); an.hide();
            }

            if (!common.has_permission("caci")) { $("#button-save").hide(); }
            if (!common.has_permission("aa")) { $("#button-toanimal").hide(); }
            if (!common.has_permission("daci")) { $("#button-delete").hide(); }
            if (!common.has_permission("gaf")) { $("#button-document").hide(); }

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
            var add = $("#address").val().replace("\n", ",");
            var town = $("#town").val();
            var county = $("#county").val();
            var postcode = $("#postcode").val();
            var map = add;
            if (town != "") { map += "," + town; }
            if (county != "") { map += "," + county; }
            if (postcode != "") { map += "," + postcode; }
            map = encodeURIComponent(map);
            return map;
        },

        show_mini_map: function() {
            setTimeout(function() {
                mapping.draw_map("embeddedmap", 15, controller.incident.DISPATCHLATLONG, [{ 
                    latlong: controller.incident.DISPATCHLATLONG, popuptext: controller.incident.DISPATCHADDRESS, popupactive: true }]);
            }, 50);
        },

        get_geocode: function(showminimap) {
            // Gets the geocode for the dispatch address. If showminimap is true,
            // displays the minimap as well.
            var i = controller.incident;
            var addrhash = geo.address_hash(i.DISPATCHADDRESS, i.DISPATCHTOWN, i.DISPATCHCOUNTY, i.DISPATCHPOSTCODE);
            // Do we already have a LATLONG? If it's upto date,
            // just show the map position
            if (i.DISPATCHLATLONG) {
                var b = i.DISPATCHLATLONG.split(",");
                if (b[2] == addrhash) {
                    incident.show_mini_map();
                    return;
                }
            }
            // Lookup the LATLONG and then show the map
            geo.get_lat_long(i.DISPATCHADDRESS, i.DISPATCHTOWN, i.DISPATCHCOUNTY, i.DISPATCHPOSTCODE)
                .then(function(lat, lon) {
                    var latlon = lat + "," + lon + "," + addrhash;
                    i.DISPATCHLATLONG = latlon;
                    $("#latlong").val(latlon);
                    // We updated the latlong, rather than dirtying the form, send it to the DB
                    common.ajax_post("incident", "mode=latlong&incidentid=" + i.ACID + "&latlong=" + encodeURIComponent(latlon));
                    if (showminimap) { incident.show_mini_map(); }
                });
        },

        validation: function() {

            // Remove any previous errors
            header.hide_error();
            validate.reset();

            // incident date
            if ($.trim($("#incidentdate").val()) == "") {
                header.show_error(_("Incident date cannot be blank"));
                $("#asm-details-accordion").accordion("option", "active", 0);
                validate.highlight("incidentdate");
                return false;
            }

            // times
            if (!validate.validtime([ "incidenttime", "calltime", "dispatchtime", "respondedtime", 
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
            $("#asm-details-accordion").accordion({
                heightStyle: "content",
                activate: function(event, ui) {
                    // Show the minimap when the dispatch panel activates.
                    // No map api likes being loaded in a hidden div and this avoids that
                    if (config.bool("ShowPersonMiniMap") && $("#dispatchaddress").val()) {
                        if ($("#asm-details-accordion").accordion("option", "active") == 2) {
                            incident.get_geocode(true);
                        }
                    }
                }
            }); 

            validate.save = function(callback) {
                if (!incident.validation()) { header.hide_loading(); return; }
                validate.dirty(false);
                var formdata = "mode=save" +
                    "&id=" + $("#incidentid").val() + 
                    "&recordversion=" + controller.incident.RECORDVERSION + 
                    "&" + $("input, select, textarea").toPOST();
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

            $("#button-toanimal").button().click(function() {
                $("#button-toanimal").button("disable");
                var formdata = "mode=toanimal&id=" + $("#incidentid").val();
                common.ajax_post("incident", formdata)
                    .then(function(result) { 
                        common.route("animal?id=" + result); 
                    });
            });

            $("#button-email").button().click(function() {
                var b = {}; 
                b[_("Send")] = function() { 
                    var formdata = "mode=email&" +
                        $("#dialog-email input, #dialog-email select, #dialog-email .asm-richtextarea").toPOST();
                    common.ajax_post("incident", formdata)
                        .then(function() { 
                            header.show_info(_("Message successfully sent"));
                            $("#dialog-email").dialog("close");
                        });
                };
                b[_("Cancel")] = function() { $(this).dialog("close"); };
                $("#dialog-email").dialog({
                     resizable: false,
                     modal: true,
                     dialogClass: "dialogshadow",
                     width: 640,
                     show: dlgfx.add_show,
                     hide: dlgfx.add_hide,
                     buttons: b
                });
                var mailaddresses = [];
                var conf_org = html.decode(config.str("Organisation").replace(",", ""));
                var conf_email = config.str("EmailAddress");
                var org_email = conf_org + " <" + conf_email + ">";
                var dispatch_user;
                $.each(controller.users, function(i, v) {
                    if (v.USERNAME == $("#dispatchedaco").select("value")) {
                        dispatch_user = v;
                    }
                });
                mailaddresses.push(org_email);
                $("#emailfrom").val(org_email);
                if (asm.useremail) {
                    mailaddresses.push(html.decode(asm.userreal) + " <" + asm.useremail + ">");
                }
                $("#emailfrom").autocomplete({source: mailaddresses});
                $("#emailfrom").autocomplete("widget").css("z-index", 1000);
                if (dispatch_user) {
                    $("#emailto").val(dispatch_user.EMAILADDRESS);
                }
                var i = controller.incident;
                var msg = [ 
                    _("Type") + ": " + i.INCIDENTNAME,
                    _("Date/Time") + ": " + format.date(i.INCIDENTDATETIME) + " " + format.time(i.INCIDENTDATETIME),
                    _("Address") + ": " + i.DISPATCHADDRESS + ' ' + i.DISPATCHTOWN + ' ' + i.DISPATCHCOUNTY + ' ' + i.DISPATCHPOSTCODE,
                    _("Notes") + ": " + common.nulltostr(i.CALLNOTES),
                    _("Caller") + ": " + common.nulltostr(i.CALLERNAME),
                    _("Victim") + ": " + common.nulltostr(i.VICTIMNAME),
                    _("Suspect") + ": " + common.nulltostr(i.OWNERNAME1)
                ].join("\n");
                $("#emailsubject").val(
                    html.decode(_("Dispatch {0}: {1}")
                        .replace("{0}", format.padleft(controller.incident.ACID, 6))
                        .replace("{1}", $("#dispatchaddress").val()) ));
                $("#emailbody").richtextarea("value", "<p>" + common.replace_all(html.decode(msg), "\n", "<br/>") + "</p>");
                $("#emailsubject").focus();
            });

            $("#button-delete").button().click(function() {
                tableform.delete_dialog(null, _("This will permanently remove this incident, are you sure?"))
                    .then(function() {
                        var formdata = "mode=delete&id=" + $("#incidentid").val();
                        return common.ajax_post("incident", formdata);
                    })
                    .then(function() { 
                        $("#dialog-delete").dialog("close"); 
                        common.route("main");
                    });
            });

            $("#button-dispatch").button().click(function() {
                if (!$("#dispatchtime").val()) {
                    $("#dispatchdate").datepicker("setDate", new Date());
                    $("#dispatchtime").val(format.time(new Date()));
                    $("#asm-details-accordion").accordion("option", "active", 2);
                    $("#button-dispatch").button("disable");
                    validate.dirty(true);
                }
            });

            // Setup the document menu button
            $("#button-document").asmmenu();

            $("#button-respond").button().click(function() {
                if (!$("#respondedtime").val()) {
                    $("#respondeddate").datepicker("setDate", new Date());
                    $("#respondedtime").val(format.time(new Date()));
                    $("#asm-details-accordion").accordion("option", "active", 2);
                    $("#button-respond").button("disable");
                    validate.dirty(true);
                }
            });

            $("#button-linkanimal")
                .button({ icons: { primary: "ui-icon-link" }, text: false })
                .click(function() {
                    $("#linkanimal").animalchooser("clear");
                    tableform.show_okcancel_dialog("#dialog-linkanimal", _("Link"), { notzero: [ "linkanimal" ] })
                        .then(function() {
                            var a = $("#linkanimal").animalchooser("get_selected");
                            return common.ajax_post("incident", "mode=linkanimaladd&id=" + controller.incident.ID + "&animalid=" + a.ID);
                        })
                        .then(function() {
                            var a = $("#linkanimal").animalchooser("get_selected");
                            controller.animallinks.push(a);
                            incident.load_animallinks();
                        });
            });

            additional.relocate_fields();

        },

        sync: function() {

            // Load the data into the controls for the screen
            $("#asm-content input, #asm-content select, #asm-content textarea").fromJSON(controller.incident);

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");

            // Update on-screen fields from the data and display the screen
            incident.enable_widgets();
            incident.load_animallinks();

            // Dirty handling
            validate.bind_dirty([ "incident_" ]);

        },

        destroy: function() {
            validate.unbind_dirty();
            common.widget_destroy("#animal");
            common.widget_destroy("#owner");
            common.widget_destroy("#owner2");
            common.widget_destroy("#owner3");
            common.widget_destroy("#caller", "personchooser");
            common.widget_destroy("#victim", "personchooser");
            common.widget_destroy("#dialog-email");
            common.widget_destroy("#dialog-linkanimal");
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

