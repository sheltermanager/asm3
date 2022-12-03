/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const roles = {

        render: function() {
            const cl = function(s) { return "<p class='asm-header'>" + s + "</p>"; };
            const cr = function(token, s) { return "<input id='" + token + "' type='checkbox' class='token' /> <label for='" + token + "'>" + s + "</label><br />"; };
            let h = [
                '<div id="dialog-add" style="display: none" title="' + html.title(_("Add role")) + '">',
                '<input type="hidden" id="roleid" />',
                '<input type="hidden" id="rolemap" />',
                '<table width="100%">',
                '<tr>',
                '<td><label for="rolename">' + _("Name") + '</label></td>',
                '<td><input id="rolename" type="text" data="rolename" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '</table>',
                '<table width="100%">',
                '<tr>',
                '<td width="33%" valign="top">',
                '<p>',
                cl(_("Animals")),
                cr("aa", _("Add Animals")),
                cr("ca", _("Change Animals")),
                cr("va", _("View Animals")),
                cr("da", _("Delete Animals")),
                cr("cloa", _("Clone Animals")),
                cr("ma", _("Merge Animals")),
                cr("gaf", _("Generate Documents")),
                cl(_("Litters")),
                cr("all", _("Add Litter")),
                cr("vll", _("View Litter")),
                cr("cll", _("Change Litter")),
                cr("dll", _("Delete Litter")),
                cl(_("Tests")),
                cr("aat", _("Add Tests")),
                cr("vat", _("View Tests")),
                cr("cat", _("Change Tests")),
                cr("dat", _("Delete Tests")),
                cl(_("Vaccinations")),
                cr("aav", _("Add Vaccinations")),
                cr("vav", _("View Vaccinations")),
                cr("cav", _("Change Vaccinations")),
                cr("dav", _("Delete Vaccinations")),
                cr("bcav", _("Bulk Complete Vaccinations")),
                cl(_("Medical")),
                cr("maam", _("Add Medical Records")),
                cr("mvam", _("View Medical Records")),
                cr("mcam", _("Change Medical Records")),
                cr("mdam", _("Delete Medical Records")),
                cr("bcam", _("Bulk Complete Medical Records")),
                cl(_("Clinic")),
                cr("acl", _("Add Clinic Appointment")),
                cr("vcl", _("View Clinic Appointment")),
                cr("ccl", _("Change Clinic Apointment")),
                cr("dcl", _("Delete Clinic Appointment")),
                cl(_("Diets")),
                cr("daad", _("Add Diets")),
                cr("dvad", _("View Diets")),
                cr("dcad", _("Change Diets")),
                cr("ddad", _("Delete Diets")),
                cl(_("Transport")),
                cr("atr", _("Add Transport")),
                cr("vtr", _("View Transport")),
                cr("ctr", _("Change Transport")),
                cr("dtr", _("Delete Transport")),
                cl(_("Media")),
                cr("aam", _("Add Media")),
                cr("vam", _("View Media")),
                cr("cam", _("Change Media")),
                cr("dam", _("Delete Media")),
                cl(_("Document Repository")),
                cr("ard", _("Add Document to Repository")),
                cr("vrd", _("View Document Repository")),
                cr("drd", _("Delete Document from Repository")),
                cl(_("Online Forms")),
                cr("aof", _("Add Online Forms")),
                cr("vof", _("View Online Forms")),
                cr("eof", _("Change Online Forms")),
                cr("dof", _("Delete Online Forms")),
                cr("vif", _("View Incoming Forms")),
                cr("dif", _("Delete Incoming Forms")),
                '</p>',
                '</td>',
                '<td width="33%" valign="top">',
                '<p>',
                cl(_("People")),
                cr("ao", _("Add Person")),
                cr("vo", _("View Person")),
                cr("vso", _("View Staff Person Records")),
                cr("vvo", _("View Volunteer Person Records")),
                cr("volk", _("View Person Links")),
                cr("co", _("Change Person")),
                cr("emo", _("Email Person")),
                cr("mo", _("Merge Person")),
                cr("do", _("Delete Person")),
                cl(_("Citations")),
                cr("aacc", _("Add Citations")),
                cr("vacc", _("View Citations")),
                cr("cacc", _("Change Citations")),
                cr("dacc", _("Delete Citations")),
                cl(_("Investigations")),
                cr("aoi", _("Add Investigation")),
                cr("voi", _("View Investigations")),
                cr("coi", _("Change Investigation")),
                cr("doi", _("Delete Investigation")),
                cl(_("Licenses")),
                cr("aapl", _("Add Licenses")),
                cr("vapl", _("View Licenses")),
                cr("capl", _("Change Licenses")),
                cr("dapl", _("Delete Licenses")),
                cl(_("Movements")),
                cr("aamv", _("Add Movement")),
                cr("vamv", _("View Movement")),
                cr("camv", _("Change Movement")),
                cr("damv", _("Delete Movement")),
                cl(_("Log")),
                cr("ale", _("Add Log")),
                cr("vle", _("View Log")),
                cr("cle", _("Change Log")),
                cr("dle", _("Delete Log")),
                cl(_("Diary")),
                cr("adn", _("Add Diary")),
                cr("vdn", _("View Diary")),
                cr("emdn", _("Edit My Diary Notes")),
                cr("eadn", _("Edit All Diary Notes")),
                cr("bcn", _("Bulk Complete Diary")),
                cr("ddn", _("Delete Diary")),
                cr("edt", _("Edit Diary Tasks")),
                cl(_("Lost and Found")),
                cr("ala", _("Add Lost Animal")),
                cr("vla", _("View Lost Animal")),
                cr("cla", _("Change Lost Animal")),
                cr("dla", _("Delete Lost Animal")),
                cr("afa", _("Add Found Animal")),
                cr("vfa", _("View Found Animal")),
                cr("cfa", _("Change Found Animal")),
                cr("dfa", _("Delete Found Animal")),
                cr("mlaf", _("Match Lost and Found")),
                cl(_("Waiting List")),
                cr("awl", _("Add Waiting List")),
                cr("vwl", _("View Waiting List")),
                cr("cwl", _("Change Waiting List")),
                cr("dwl", _("Delete Waiting List")),
                cr("bcwl", _("Bulk Complete Waiting List")),
                cl(_("Events")),
                cr("ae", _("Add Event")),
                cr("ve", _("View Event")),
                cr("ce", _("Change Event")),
                cr("de", _("Delete Event")),
                cr("vea", _("View Event Animals")),
                cr("cea", _("Change Event Animals")),
                cr("lem", _("Link Event Movement")),
                '</p>',
                '</td>',
                '<td width="33%" valign="top">',
                '<p>',
                cl(_("Animal Control")),
                cr("aaci", _("Add Incidents")),
                cr("vaci", _("View Incidents")),
                cr("caci", _("Change Incidents")),
                cr("daci", _("Delete Incidents")),
                cr("cacd", _("Dispatch Incident")),
                cr("cacr", _("Respond to Incident")),
                cl(_("Trap Loans")),
                cr("aatl", _("Add Trap Loans")),
                cr("vatl", _("View Trap Loans")),
                cr("catl", _("Change Trap Loans")),
                cr("datl", _("Delete Trap Loans")),
                cl(_("Accounts")),
                cr("aac", _("Add Accounts")),
                cr("vac", _("View Accounts")),
                cr("cac", _("Change Accounts")),
                cr("ctrx", _("Change Transactions")),
                cr("dac", _("Delete Accounts")),
                cl(_("Costs")),
                cr("caad", _("Add Cost")),
                cr("cvad", _("View Cost")),
                cr("ccad", _("Change Cost")),
                cr("cdad", _("Delete Cost")),
                cl(_("Payments")),
                cr("oaod", _("Add Payments")),
                cr("ovod", _("View Payments")),
                cr("ocod", _("Change Payments")),
                cr("odod", _("Delete Payments")),
                cl(_("Rota")),
                cr("aoro", _("Add Rota")),
                cr("voro", _("View Rota")),
                cr("vsro", _("View Staff Rota")),
                cr("coro", _("Change Rota")),
                cr("doro", _("Delete Rota")),
                cl(_("Stock Control")),
                cr("asl", _("Add Stock")),
                cr("vsl", _("View Stock")),
                cr("csl", _("Change Stock")),
                cr("dsl", _("Delete Stock")),
                cl(_("Vouchers")),
                cr("vaov", _("Add Vouchers")),
                cr("vvov", _("View Vouchers")),
                cr("vcov", _("Change Vouchers")),
                cr("vdov", _("Delete Vouchers")),
                cl(_("System")),
                cr("asm", _("Access Settings Menu")),
                cr("cso", _("Change System Options")),
                cr("cpo", _("Change Publishing Options")),
                cr("eav", _("Export Animals as CSV")),
                cr("icv", _("Import CSV File")),
                cr("maf", _("Modify Additional Fields")),
                cr("mdt", _("Modify Document Templates")),
                cr("ml", _("Modify Lookups")),
                cr("tbp", _("Trigger Batch Processes")),
                cr("usi", _("Use SQL Interface")),
                cr("uipb", _("Publish Animals to the Internet")),
                cr("mmeo", _("Send mass emails and perform mail merges")),
                cr("vatr", _("View Audit Trail")),
                cl(_("Users")),
                cr("asu", _("Add Users")),
                cr("esu", _("Edit Users")),
                cl(_("Reports")),
                cr("ccr", _("Add Report")),
                cr("vcr", _("View Report")),
                cr("hcr", _("Change Report")),
                cr("excr", _("Export Report")),
                cr("dcr", _("Delete Report")),
                '</p>',
                '</td>',
                '</tr>',
                '</table>',
                '</div>',

                html.content_header(_("User Roles")),

                '<div class="asm-toolbar">',
                '<button id="button-new">' + html.icon("new") + ' ' +_("New Role") + '</button>',
                '<button id="button-clone">' + html.icon("copy") + ' ' +_("Clone") + '</button>',
                '<button id="button-delete">' + html.icon("delete") + ' ' + _("Delete") + '</button>',
                '</div>',

                '<table id="table-roles">',
                '<thead>',
                '<tr>',
                '<th>' + _("Name") + '</th>',
                '</tr>',
                '</thead>',
                '<tbody>'
            ];

            $.each(controller.rows, function(i, r) {
                h.push('<tr id="rolerow-' + r.ID + '">');
                h.push('<td>');
                h.push('<span style="white-space: nowrap">');
                h.push('<input type="checkbox" data="' + r.ID + '" title="' + html.title(_('Select')) + '" />');
                h.push('<a href="#" class="role-edit-link" data="' + r.ID + '">' + r.ROLENAME + '</a>');
                h.push('</span>');
                h.push('<input class="role-name" type="hidden" value="' + html.title(r.ROLENAME) + '" />');
                h.push('<input class="role-map" type="hidden" value="' + r.SECURITYMAP + '" />');
                h.push('</td>');
                h.push('</tr>');
            });

            h.push('</tbody>');
            h.push('</table>');
            h.push(html.content_footer());
            return h.join("\n");
        },

        bind: function() {
            $("#table-roles").table();

            $("#table-roles input").change(function() {
                if ($("#table-roles input:checked").length > 0) {
                    $("#button-delete").button("option", "disabled", false); 
                }
                else {
                    $("#button-delete").button("option", "disabled", true); 
                }
                if ($("#table-roles input:checked").length == 1) {
                    $("#button-clone").button("option", "disabled", false);
                }
                else {
                    $("#button-clone").button("option", "disabled", true);
                }
            });

            validate.indicator([ "rolename" ]);

            let addbuttons = { };
            addbuttons[_("Create")] = async function() {
                validate.reset("dialog-add");
                if (!validate.notblank([ "rolename" ])) { return; }
                let securitymap = "";
                $(".token").each(function() {
                    if ($(this).is(":checked")) { securitymap += $(this).attr("id") + " *"; }
                });
                let formdata = "mode=create&securitymap=" + securitymap + "&" + $("#dialog-add input").toPOST();
                $("#dialog-add").disable_dialog_buttons();
                try {
                    await common.ajax_post("roles", formdata);
                    common.route_reload(); 
                }
                finally {
                    $("#dialog-add").dialog("close"); 
                }
            };
            addbuttons[_("Cancel")] = function() {
                $("#dialog-add").dialog("close");
            };

            let editbuttons = { };
            editbuttons[_("Save")] = async function() {
                validate.reset("dialog-add");
                if (!validate.notblank([ "rolename" ])) { return; }
                let securitymap = "";
                $(".token").each(function() {
                    if ($(this).is(":checked")) { securitymap += $(this).attr("id") + " *"; }
                });
                let formdata = "mode=update&roleid=" + $("#roleid").val() + "&" + 
                    "securitymap=" + securitymap + "&" +
                    $("#dialog-add input").toPOST();
                $("#dialog-add").disable_dialog_buttons();
                try {
                    await common.ajax_post("roles", formdata);
                    common.route_reload(); 
                }
                finally {
                    $("#dialog-add").dialog("close"); 
                }
            };
            editbuttons[_("Cancel")] = function() {
                $("#dialog-add").dialog("close");
            };

            $("#dialog-add").dialog({
                autoOpen: false,
                modal: true,
                width: 900,
                height: 500,
                dialogClass: "dialogshadow",
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: addbuttons
            });
         
            $("#button-new").button().click(function() {
               validate.reset("dialog-add");
               $("#dialog-add .asm-textbox").val("");
               $("#dialog-add input:checkbox").prop("checked", false);
               $("#dialog-add").dialog("option", "buttons", addbuttons);
               $("#dialog-add").dialog("option", "title", _("Add role"));
               $("#dialog-add").dialog("open"); 
            });

            $("#button-clone").button({disabled: true}).click(function() {
                let rid = "";
                $("#table-roles :checked").each(function() {
                    rid = $(this).attr("data");
                });
                $("#dialog-add .asm-textbox").val("");
                let rrow = "#rolerow-" + rid + " ";
                let rolename = $(rrow + ".role-name").val();
                let perms = $(rrow + ".role-map").val().replace(/\*/g, "").split(" ");
                $("#rolename").val(_("Copy of {0}").replace("{0}", rolename));
                $(".token").prop("checked", false);
                $.each(perms, function(i, v) {
                    if (v) { $("#" + v).prop("checked", true); }
                });
                validate.reset("dialog-add");
                $("#dialog-add").dialog("option", "buttons", addbuttons);
                $("#dialog-add").dialog("option", "title", _("Add role"));
                $("#dialog-add").dialog("open"); 
            });

            $("#button-delete").button({disabled: true}).click(async function() {
                await tableform.delete_dialog(null, _("This will permanently remove the selected roles, are you sure?"));
                let formdata = "mode=delete&ids=";
                $("#table-roles input").each(function() {
                    if ($(this).attr("type") == "checkbox") {
                        if ($(this).is(":checked")) {
                            formdata += $(this).attr("data") + ",";
                        }
                    }
                });
                await common.ajax_post("roles", formdata);
                common.route_reload(); 
            });

            $(".role-edit-link")
            .click(function() {
                let rid = $(this).attr("data");
                let rrow = "#rolerow-" + rid + " ";
                validate.reset("dialog-add");
                $("#roleid").val($(this).attr("data"));
                $("#rolename").val($(rrow + ".role-name").val());
                let perms = $(rrow + ".role-map").val().replace(/\*/g, "").split(" ");
                $(".token").prop("checked", false);
                $.each(perms, function(i, v) {
                    if (v) { $("#" + v).prop("checked", true); }
                });
                $("#dialog-add").dialog("option", "buttons", editbuttons);
                $("#dialog-add").dialog("option", "title", _("Edit role"));
                $("#dialog-add").dialog("open");
                return false; // prevents # href
            });

        },

        destroy: function() {
            common.widget_destroy("#dialog-add");
        },

        name: "roles",
        animation: "options",
        title: function() { return _("Edit roles"); },
        routes: {
            "roles": function() { common.module_loadandstart("roles", "roles"); }
        }

    };

    common.module_register(roles);

});
