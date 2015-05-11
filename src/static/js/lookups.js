/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var tablelist = [];

    var lookups = {

        model: function() {

            // The list of tables has two elements for value/label,
            // flatten it to value|label to work with the dropdownfilter
            // button type
            tablelist = [];
            $.each(controller.tables, function(i, v) {
                tablelist.push(v.join("|"));
            });

            var dialog = {
                add_title: _("Add {0}").replace("{0}", html.decode(controller.tablelabel)),
                edit_title: _("Edit {0}").replace("{0}", html.decode(controller.tablelabel)),
                close_on_ok: true,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: controller.namefield, post_field: "lookupname", label: controller.namelabel, type: "text", validation: "notblank" },
                    { hideif: function() { return !controller.hasspecies; }, 
                        json_field: "SPECIESID", post_field: "species", label: _("Species"), type: "select", 
                        options: { displayfield: "SPECIESNAME", valuefield: "ID", rows: controller.species }},
                    { hideif: function() { return !controller.haspfspecies; },
                        json_field: "PETFINDERSPECIES", post_field: "pfspecies", label: _("Publisher Species"), type: "select", 
                        tooltip: _("Species to use when publishing to third party services and adoption sites"),
                        options: controller.petfinderspecies },
                    { hideif: function() { return !controller.haspfbreed; },
                        json_field: "PETFINDERBREED", post_field: "pfbreed", label: _("Publisher Breed"), type: "select", 
                        tooltip: _("Breed to use when publishing to third party services and adoption sites"),
                        options: controller.petfinderbreeds },
                    { hideif: function() { return !controller.hasdefaultcost; },
                        json_field: "DEFAULTCOST", post_field: "defaultcost", label: _("Default Cost"), type: "currency" },
                    { hideif: function() { return !controller.hasunits; },
                        json_field: "UNITS", post_field: "units", label: _("Units"), type: "textarea", 
                        tooltip: _("Comma separated list of units for this location") },
                    { hideif: function() { return controller.descfield == ""; },
                        json_field: controller.descfield, post_field: "lookupdesc", label: _("Description"), type: "textarea" }
                ]
            };

            var table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.dialog_show_edit(dialog, row, function() {
                        tableform.fields_update_row(dialog.fields, row);
                        if (row.SPECIESID) {
                            row.SPECIESNAME = common.get_field(controller.species, row.SPECIESID, "SPECIESNAME");
                        }
                        tableform.fields_post(dialog.fields, 
                            "mode=update&lookup=" + controller.tablename + "&namefield=" + controller.namefield + "&id=" + row.ID, "lookups", 
                            function(response) {
                                tableform.table_update(table);
                            });
                    });
                },
                columns: [
                    { field: controller.namefield, display: controller.namelabel, initialsort: true },
                    { field: "SPECIESNAME", display: _("Species"), hideif: function(row) {
                        return !controller.hasspecies;
                    }},
                    { field: "PETFINDERSPECIES", display: _("Publisher"), hideif: function(row) {
                        if (asm.locale == "en" && (controller.haspfspecies || controller.haspfbreed)) { return false; }
                        if (asm.locale == "en_AU" && (controller.haspfspecies || controller.haspfbreed)) { return false; }
                        return true;
                    }, formatter: function(row) {
                        if (controller.haspfspecies) { return row.PETFINDERSPECIES; }
                        if (controller.haspfbreed) { return row.PETFINDERBREED; }
                    }},
                    { field: controller.descfield, display: _("Description"), hideif: function(row) { return controller.descfield == ""; }},
                    { field: "UNITS", display: _("Units"), hideif: function(row) { return !controller.hasunits; }},
                    { field: "DEFAULTCOST", display: _("Default Cost"), formatter: tableform.format_currency,
                        hideif: function(row) { return !controller.hasdefaultcost; }}
                ]
            };

            var buttons = [
                 { id: "new", text: _("New"), icon: "new", enabled: "always", hideif: function() { return !controller.canadd; },
                     click: function() { 
                        tableform.dialog_show_add(dialog, function() {
                            tableform.fields_post(dialog.fields, 
                                 "mode=create&lookup=" + controller.tablename + "&namefield=" + controller.namefield, "lookups", function(response) {
                                 var row = {};
                                 row.ID = response;
                                 tableform.fields_update_row(dialog.fields, row);
                                 if (row.SPECIESID) {
                                     row.SPECIESNAME = common.get_field(controller.species, row.SPECIESID, "SPECIESNAME");
                                 }
                                 controller.rows.push(row);
                                 tableform.table_update(table);
                            });
                        });
                     } 
                 },
                 { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", hideif: function() { return !controller.candelete; },
                     click: function() { 
                         tableform.delete_dialog(function() {
                             tableform.buttons_default_state(buttons);
                             var ids = tableform.table_ids(table);
                             common.ajax_post("lookups", "mode=delete&lookup=" + controller.tablename + "&ids=" + ids , function() {
                                 tableform.table_remove_selected_from_json(table, controller.rows);
                                 tableform.table_update(table);
                             });
                         });
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
            var s = "";
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
