/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const roles = {

        model: function() {
            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    validate.reset("dialog-add");
                    $("#roleid").val(row.ID);
                    $("#rolename").val(row.ROLENAME);
                    let perms = row.SECURITYMAP.replace(/\*/g, "").split(" ");
                    $(".token").prop("checked", false);
                    $.each(perms, function(i, v) {
                        if (v) { $("#" + v).prop("checked", true); }
                    });
                    $("#dialog-add").dialog("option", "buttons", roles.editbuttons);
                    $("#dialog-add").dialog("option", "title", _("Edit role"));
                    $("#dialog-add").dialog("open");
                    return false; // prevents # href
                },
                columns: [
                    { field: "ROLENAME", display: _("Name") }
                ]
            };
            const buttons = [
                { id: "new", text: _("New Role"), icon: "new", enabled: "always",
                    click: function() {
                        validate.reset("dialog-add");
                        $("#dialog-add .asm-textbox").val("");
                        $("#dialog-add input:checkbox").prop("checked", false);
                        $("#dialog-add").dialog("option", "buttons", roles.addbuttons);
                        $("#dialog-add").dialog("option", "title", _("Add role"));
                        $("#dialog-add").dialog("open"); 
                    }
                },
                { id: "clone", text: _("Clone"), icon: "copy", enabled: "one", 
                    click: function() {
                        let row = tableform.table_selected_row(roles.table);
                        $("#dialog-add .asm-textbox").val("");
                        let perms = row.SECURITYMAP.replace(/\*/g, "").split(" ");
                        $("#rolename").val(_("Copy of {0}").replace("{0}", row.ROLENAME));
                        $(".token").prop("checked", false);
                        $.each(perms, function(i, v) {
                            if (v) { $("#" + v).prop("checked", true); }
                        });
                        validate.reset("dialog-add");
                        $("#dialog-add").dialog("option", "buttons", roles.addbuttons);
                        $("#dialog-add").dialog("option", "title", _("Add role"));
                        $("#dialog-add").dialog("open"); 
                    }
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", 
                    click: async function() {
                        await tableform.delete_dialog(null, _("This will permanently remove the selected roles, are you sure?"));
                        let formdata = "mode=delete&ids=" + tableform.table_ids(roles.table);
                        await common.ajax_post("roles", formdata);
                        common.route_reload(); 
                    }
                }
            ];
            this.table = table;
            this.buttons = buttons;
        },

        render_dialog: function() {
            const cl = function(s) { return "<p class='asm-header'>" + s + "</p>"; };
            const cr = function(token, s) { return "<input id='" + token + "' type='checkbox' class='token' /> <label for='" + token + "'>" + s + "</label><br />"; };
            return [
                '<div id="dialog-add" style="display: none" title="' + html.title(_("Add role")) + '">',
                '<input type="hidden" id="roleid" />',
                '<input type="hidden" id="rolemap" />',
                tableform.fields_render([
                    { post_field: "rolename", type: "text", label: _("Name") }
                ]),
                '<div class="asm-row">',
                '<div class="asm-col">',
                '<p>',
                cl(_("Animals")),
                cr("aa", _("Add Animals")),
                cr("ca", _("Change Animals")),
                cr("va", _("View Animals")),
                cr("da", _("Delete Animals")),
                cr("cloa", _("Clone Animals")),
                cr("ma", _("Merge Animals")),
                cr("gaf", _("Generate Documents")),
                cr("rsu", _("Reserve/Sponsor Units")),
                cr("vti", _("View Timeline")),
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
                cl(_("Boarding")),
                cr("abi", _("Add Boarding")),
                cr("vbi", _("View Boarding")),
                cr("cbi", _("Change Boarding")),
                cr("dbi", _("Delete Boarding")),
                cl(_("Clinic")),
                cr("acl", _("Add Clinic Appointment")),
                cr("vcl", _("View Clinic Appointment")),
                cr("vcrc", _("View Consulting Room")),
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
                '</div>',
                '<div class="asm-col">',
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
                '</div>',
                '<div class="asm-col">',
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
                '</div>', // col
                '</div>', // row
                '</div>'  // dialog
            ].join("\n");
        },

        bind_dialog: function() {
            let addbuttons = { };
            addbuttons[_("Create")] = {
                text: _("Create"),
                "class": "asm-dialog-actionbutton",
                click: async function() {
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
                }
            };
            addbuttons[_("Cancel")] = function() {
                $("#dialog-add").dialog("close");
            };
            this.addbuttons = addbuttons;

            let editbuttons = { };
            editbuttons[_("Save")] = {
                text: _("Save"),
                "class": "asm-dialog-actionbutton",
                click: async function() {
                    validate.reset("dialog-add");
                    if (!validate.notblank([ "rolename" ])) { return; }
                    let securitymap = "";
                    $(".token").each(function() {
                        if ($(this).is(":checked")) { securitymap += $(this).attr("id") + " *"; }
                    });
                    let formdata = "mode=update&roleid=" + $("#roleid").val() + "&" + 
                        "securitymap=" + securitymap + "&" + $("#dialog-add input").toPOST();
                    $("#dialog-add").disable_dialog_buttons();
                    try {
                        await common.ajax_post("roles", formdata);
                        common.route_reload(); 
                    }
                    finally {
                        $("#dialog-add").dialog("close"); 
                    }
                }
            };
            editbuttons[_("Cancel")] = function() {
                $("#dialog-add").dialog("close");
            };
            this.editbuttons = editbuttons;

            $("#dialog-add").dialog({
                autoOpen: false,
                modal: true,
                width: 900,
                height: 500,
                dialogClass: "dialogshadow",
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: roles.addbuttons
            });
        },

        render: function() {
            this.model();
            return [
                this.render_dialog(),
                html.content_header(_("User Roles")),
                tableform.buttons_render(this.buttons),
                tableform.table_render(this.table),
                html.content_footer()
            ].join("\n");

        },

        bind: function() {
            tableform.table_bind(this.table, this.buttons);
            tableform.buttons_bind(this.buttons);
            this.bind_dialog();

            validate.indicator([ "rolename" ]);
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
