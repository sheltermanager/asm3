/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, geo, header, html, validate */

$(function() {

    var incident_new = {

        render: function() {
            return [
                html.content_header(_("Report a new incident")),
                '<table class="asm-table-layout">',
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
                '</tr>',
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
                '<tr>',
                '<td>' + _("Suspect") + '</td>',
                '<input id="owner" data-json="OWNERID" data-post="owner" type="hidden" class="asm-personchooser" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="dispatchaddress">' + _("Dispatch Address") + '</label></td>',
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
                '</table>',
                '<div class="centered">',
                '<button id="addedit">' + html.icon("call") + ' ' + _("Create and edit") + '</button>',
                '<button id="add">' + html.icon("call") + ' ' + _("Create") + '</button>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            var validation = function() {
                // Remove any previous errors
                header.hide_error();
                $("label").removeClass("ui-state-error-text");
                if (!validate.notblank([ "incidentdate", "incidenttime" ])) { return false; }
                if (!validate.validtime([ "incidenttime", "calltime" ])) { return false; }
                return true;
            };
            var addIncident = function(mode) {
                if (!validation()) { 
                    $("#asm-content button").button("enable"); 
                    return; 
                }
                header.show_loading(_("Creating..."));
                var formdata = $("input, textarea, select").toPOST();
                common.ajax_post("incident_new", formdata, function(incidentid) { 
                    if (mode == "addedit") {
                        common.route("incident?id=" + incidentid);
                    }
                    else if (mode == "add") {
                        header.show_info(_("Incident {0} successfully created.").replace("{0}", incidentid));
                        $("#asm-content button").button("enable");
                    }
                }, function() {
                    $("#asm-content button").button("enable");
                });
            };

            $("#add").button().click(function() {
                $("#asm-content button").button("disable");
                addIncident("add");
            });

            $("#addedit").button().click(function() {
                $("#asm-content button").button("disable");
                addIncident("addedit");
            });
        },

        sync: function() {
            $("#incidentdate").datepicker("setDate", new Date());
            $("#incidenttime").val(format.time(new Date()));
            $("#calldate").datepicker("setDate", new Date());
            $("#calltime").val(format.time(new Date()));
            $("#calltaker").select("value", asm.user);
            $("#incidenttype").select("value", config.str("DefaultIncidentType"));
        },

        name: "incident_new",
        animation: "newdata",
        title: function() { return _("Report a new incident"); },
        routes: {
            "incident_new": function() { common.module_loadandstart("incident_new", "incident_new"); }
        }

    };

    common.module_register(incident_new);

});
