/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    let tablelist = [];

    console.log("controller.tablename = " + controller.tablename);



    const lookups = {

        // locales where the publisher column/fields appear
        publisher_locales: [ "en", "en_CA", "en_GB", "en_MX", "es_MX" ],

        reschedule_options: [ 
            { "ID": 0, "NAME": _("Never") },
            { "ID": 7, "NAME": _("1 week") },
            { "ID": 14, "NAME": _("{0} weeks").replace("{0}", "2") },
            { "ID": 21, "NAME": _("{0} weeks").replace("{0}", "3") },
            { "ID": 28, "NAME": _("{0} weeks").replace("{0}", "4") },
            { "ID": 42, "NAME": _("{0} weeks").replace("{0}", "6") },
            { "ID": 56, "NAME": _("{0} weeks").replace("{0}", "8") },
            { "ID": 84, "NAME": _("{0} weeks").replace("{0}", "12") },
            { "ID": 182, "NAME": _("{0} weeks").replace("{0}", "26") },
            { "ID": 365, "NAME": _("1 year") },
            { "ID": 730, "NAME": _("{0} years").replace("{0}", "2") },
            { "ID": 1095, "NAME": _("{0} years").replace("{0}", "3") },
            { "ID": 1460, "NAME": _("{0} years").replace("{0}", "4") },
            { "ID": 1825, "NAME": _("{0} years").replace("{0}", "5") }
        ],

        model: function() {

            // Add an empty value to the account so it can be unlinked
            controller.accounts.unshift({ ID: 0, CODE: "" });

            // Add a special value for matching account created
            controller.accounts.push({ ID: -1, CODE: _("Matching account created") });

            // The list of tables has two elements for value/label,
            // flatten it to value|label to work with the dropdownfilter
            // button type
            tablelist = [];
            $.each(controller.tables, function(i, v) {
                tablelist.push(v.join("|"));
            });

            const dialog = {
                add_title: _("Add {0}").replace("{0}", html.decode(controller.tablelabel)),
                edit_title: _("Edit {0}").replace("{0}", html.decode(controller.tablelabel)),
                close_on_ok: false,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: controller.namefield, post_field: "lookupname", label: controller.namelabel, type: "text", validation: "notblank" },
                    { hideif: function() { return !controller.canretire; },
                        json_field: "ISRETIRED", post_field: "retired", label: _("Active"), defaultval: "0", type: "select",
                        options: '<option value="0">' + _("Yes") + '</option><option value="1">' + _("No") + '</option>' },
                    { hideif: function() { return !controller.hasspecies; }, 
                        json_field: "SPECIESID", post_field: "species", label: _("Species"), type: "select", 
                        options: { displayfield: "SPECIESNAME", valuefield: "ID", rows: controller.species }},
                    { hideif: function() { return !controller.haspfspecies; },
                        json_field: "PETFINDERSPECIES", post_field: "pfspecies", label: _("Publisher Species"), type: "select", 
                        callout: _("Species to use when publishing to third party services and adoption sites"),
                        options: controller.petfinderspecies },
                    { hideif: function() { return !controller.haspfbreed; },
                        json_field: "PETFINDERBREED", post_field: "pfbreed", label: _("Publisher Breed"), type: "select", 
                        callout: _("Breed to use when publishing to third party services and adoption sites"),
                        options: controller.petfinderbreeds },
                    { hideif: function() { return !controller.hasapcolour; },
                        json_field: "ADOPTAPETCOLOUR", post_field: "apcolour", label: _("Publisher Color"), type: "select", 
                        callout: _("Color to use when publishing to third party services and adoption sites"),
                        options: controller.adoptapetcolours },
                    { hideif: function() { return !controller.hasrescheduledays; },
                        json_field: "RESCHEDULEDAYS", post_field: "rescheduledays", label: _("Reschedule for"), type: "select",
                        options: { rows: lookups.reschedule_options, valuefield: "ID", displayfield: "NAME" }},
                    { hideif: function() { return !controller.hasdefaultcost; },
                        json_field: "DEFAULTCOST", post_field: "defaultcost", label: _("Default Cost"), type: "currency" },
                    { hideif: function() { return !controller.hasaccountid; },
                        json_field: "ACCOUNTID", post_field: "account", label: _("Account"), type: "select",
                        options: { rows: controller.accounts, valuefield: "ID", displayfield: "CODE" }},
                    { hideif: function() { return !controller.hassite; },
                        json_field: "SITEID", post_field: "site", label: _("Site"), type: "select", 
                        options: html.list_to_options(controller.sites, "ID", "SITENAME") },
                    { hideif: function() { return !controller.hasunits; },
                        json_field: "UNITS", post_field: "units", label: _("Units"), type: "textarea", 
                        callout: _("Comma separated list of units for this location, eg: 1,2,3,4,Isolation,Pen 5") },
                    { hideif: function() { return !controller.hasvat; },
                        json_field: "ISVAT", post_field: "vat", label: _("Sales Tax"), type: "select", 
                        options: '<option value="0">' + _("No") + '</option><option value="1">' + _("Yes") + '</option>' },
                    { hideif: function() { return controller.descfield == ""; },
                        json_field: controller.descfield, post_field: "lookupdesc", label: _("Description"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    if (lookups.is_built_in(row)) { return; } 
                    await tableform.dialog_show_edit(dialog, row, {
                        onload: function() {
                            // If we don't talk to any third party services in this locale, might as well hide
                            // the publisher fields to avoid confusion
                            if ($.inArray(asm.locale, lookups.publisher_locales) == -1) {
                                $("#pfspecies").closest("tr").hide();
                                $("#pfbreed").closest("tr").hide();
                                $("#pfapcolour").closest("tr").hide();
                            }
                        }
                        });
                    tableform.fields_update_row(dialog.fields, row);
                    if (row.SPECIESID) {
                        row.SPECIESNAME = common.get_field(controller.species, row.SPECIESID, "SPECIESNAME");
                    }
                    await tableform.fields_post(dialog.fields, "mode=update&lookup=" + controller.tablename + "&namefield=" + controller.namefield + "&id=" + row.ID, "lookups");
                    tableform.table_update(table);
                    tableform.dialog_close();
                },
                complete: function(row) {
                    if (row.ISRETIRED && row.ISRETIRED == 1) { return true; }
                    return false;
                },
                columns: [
                    { field: controller.namefield, display: controller.namelabel, initialsort: true },
                    { field: "ID", display: _("ID"), 
                        hideif: function(row) {
                            return !config.bool("ShowLookupDataID");
                        }, formatter: function(row) {
                            if (lookups.is_builtin(row)) { return _("(built in)"); }
                            return row.ID;
                        }},
                    { field: "SPECIESNAME", display: _("Species"), hideif: function(row) {
                        return !controller.hasspecies;
                    }},
                    { field: "PUBLISHER", display: _("Publisher"), hideif: function(row) {
                        if (!(controller.haspfspecies || controller.haspfbreed || controller.hasapcolour)) { return true; }
                        if ($.inArray(asm.locale, lookups.publisher_locales) == -1) { return true; }
                        return false;
                    }, formatter: function(row) {
                        if (controller.haspfspecies) { return row.PETFINDERSPECIES; }
                        if (controller.haspfbreed) { return row.PETFINDERBREED; }
                        if (controller.hasapcolour) { return row.ADOPTAPETCOLOUR; }
                    }},
                    { field: controller.descfield, display: _("Description"), hideif: function(row) { return controller.descfield == ""; }},
                    { field: "SITEID", display: _("Site"), 
                        formatter: function(row) {
                            return common.nulltostr(common.get_field(controller.sites, row.SITEID, "SITENAME"));
                        }, hideif: function(row) { 
                            return !controller.hasunits || !config.bool("MultiSiteEnabled"); 
                        }
                    },
                    { field: "UNITS", display: _("Units"), hideif: function(row) { return !controller.hasunits; }},
                    { field: "ISVAT", display: _("Sales Tax"), hideif: function(row) { return !controller.hasvat; }, 
                        formatter: function(row) { return row.ISVAT == 1 ? _("Yes") : _("No"); }},
                    { field: "RESCHEDULEDAYS", display: _("Reschedule for"), 
                        hideif: function(row) { return !controller.hasrescheduledays; },
                        formatter: function(row) { 
                            let rv = String(row.RESCHEDULEDAYS);
                            $.each(lookups.reschedule_options, function(i, v) {
                                if (row.RESCHEDULEDAYS == v.ID) { rv = v.NAME; }
                            });
                            return rv;
                        }
                    },
                    { field: "DEFAULTCOST", display: _("Default Cost"), formatter: tableform.format_currency,
                        hideif: function(row) { return !controller.hasdefaultcost; }},
                    { field: "ACCOUNT", display: _("Account"), 
                        formatter: function(row) {
                            return common.get_field(controller.accounts, row.ACCOUNTID, "CODE");
                        },
                        hideif: function(row) { 
                            return !controller.hasaccountid; 
                        }
                    }
                ]
            };

            const buttons = [
                { id: "new", text: _("New"), icon: "new", enabled: "always", hideif: function() { return !controller.canadd; },
                    click: async function() { 
                        await tableform.dialog_show_add(dialog, {
                            onload: function() {
                                $("#account").select("value", "0");
                                // If we don't talk to any third party services in this locale, might as well hide
                                // the publisher fields to avoid confusion
                                if ($.inArray(asm.locale, lookups.publisher_locales) == -1) {
                                    $("#pfspecies").closest("tr").hide();
                                    $("#pfbreed").closest("tr").hide();
                                    $("#pfapcolour").closest("tr").hide();
                                }
                            }
                            });
                        let response = await tableform.fields_post(dialog.fields, 
                            "mode=create&lookup=" + controller.tablename + "&namefield=" + controller.namefield, "lookups");
                        let row = {};
                        row.ID = response;
                        tableform.fields_update_row(dialog.fields, row);
                        if (row.SPECIESID) {
                            row.SPECIESNAME = common.get_field(controller.species, row.SPECIESID, "SPECIESNAME");
                        }
                        controller.rows.push(row);
                        tableform.dialog_close();
                        // costtype/donationtype and the create option is on, reload the screen to show the new account
                        if (controller.tablename == "costtype" && config.bool("CreateCostTrx")) {
                            common.route_reload();
                        }
                        else if (controller.tablename == "donationtype" && config.bool("CreateDonationTrx")) {
                            common.route_reload();
                        }
                        else {
                            tableform.table_update(table);
                        }
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", hideif: function() { return !controller.candelete; },
                    click: async function() {
                        if (lookups.is_builtin_selected()) { return; }
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let rawids = tableform.table_ids(table);
                        let ids = []
                        for ( let a = 0; a < rawids.length; a++ ) {
                            if ( rawids[a] >= 0 ) {
                                ids.push(rawids[a])
                            }
                        }
                        await common.ajax_post("lookups", "mode=delete&lookup=" + controller.tablename + "&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "active", text: _("Active"), icon: "tick", enabled: "multi", hideif: function() { return !controller.canretire; },
                    click: async function() {
                        if (lookups.is_builtin_selected()) { return; }
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("lookups", "mode=active&lookup=" + controller.tablename + "&ids=" + ids);
                        $.each(tableform.table_selected_rows(table), function(i, v) {
                            v.ISRETIRED = 0;
                        });
                        tableform.table_update(table);
                    }
                },
                { id: "inactive", text: _("Inactive"), icon: "cross", enabled: "multi", hideif: function() { return !controller.canretire; },
                    click: async function() {
                        if (lookups.is_builtin_selected()) { return; }
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("lookups", "mode=inactive&lookup=" + controller.tablename + "&ids=" + ids);
                        $.each(tableform.table_selected_rows(table), function(i, v) {
                            v.ISRETIRED = 1;
                        });
                        tableform.table_update(table);
                    }
                },
                { id: "lookup", type: "dropdownfilter", options: tablelist, click: function(newval) {
                    common.route("lookups?tablename=" + newval);
                }}
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        render: function() {
            let s = "";
            this.add_builtin_flags();
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Edit Lookups"));
            s += html.warn(
                _("These values are required for correct operation of the system. ONLY change them if you are translating to another language."), 
                "systemlookupwarn");
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
            $("#systemlookupwarn").hide();
            if (controller.tablename.indexOf("lks") == 0) {
                $("#systemlookupwarn").delay(500).fadeIn();
            }
            $("#lookup").val(controller.tablename);
            // Only show the site field if the lookup has it and multi site is on
            if (controller.hassite) {
                $("#site").closest("tr").toggle( config.bool("MultiSiteEnabled") );
            }
            // Hide the sites lookup if multi site isn't on
            if (!config.bool("MultiSiteEnabled")) {
                $("#lookup").find("option[value='site']").remove();
            }
        },

        add_builtin_flags: function() {
            if ( controller.tablename == "lkanimalflags" ) {
                console.log(controller.rows);
                let builtinflagrows = [
                    { ID: -1, FLAG: _("Courtesy Listing"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Cruelty Case"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Non-Shelter"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Not For Adoption"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Do Not Publish"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Do Not Register Microchip"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Quarantine"), ISRETIRED: 1 }
                ]
                controller.rows = controller.rows.concat(builtinflagrows);
            }
            if ( controller.tablename == "lkownerflags" ) {
                console.log(controller.rows);
                let builtinflagrows = [
                    { ID: -1, FLAG: _("ACO"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Adopter"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Adoption Coordinator"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Banned"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Dangerous"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Deceased"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Donor"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Driver"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Exclude from bulk email"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Fosterer"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Homechecked"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Homechecker"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Member"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Other Shelter"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Sponsor"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Staff"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Vet"), ISRETIRED: 1 },
                    { ID: -1, FLAG: _("Volunteer"), ISRETIRED: 1 }
                ]
                controller.rows = controller.rows.concat(builtinflagrows);
            }
        },

        is_builtin: function(row) {
            return row.ID < 0;
        },

        is_builtin_selected: function() {
            let rows = tableform.table_selected_rows(lookups.table), builtins = false;
            $.each(rows, function(i, v) {
                if (lookups.is_builtin(v)) { 
                    builtins = true; 
                    return false
                }
            });
            return builtins;
        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        name: "lookups",
        animation: "book",
        title: function() { return _("Edit Lookups"); },
        routes: {
            "lookups": function() { common.module_loadandstart("lookups", "lookups?" + this.rawqs); }
        }

    };

    common.module_register(lookups);

});
