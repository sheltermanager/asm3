/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var lastanimal = null;
    var litters = {};

    var dialog = {
        add_title: _("Add litter"),
        edit_title: _("Edit litter"),
        edit_perm: 'cll',
        helper_text: _("Litters need at least a required date and number."),
        close_on_ok: true,
        columns: 1,
        fields: [
            { json_field: "ACCEPTANCENUMBER", post_field: "litterref", label: _("Litter Reference"), type: "text",
                tooltip: _("A unique reference for this litter"), validation: "notblank" },
            { json_field: "PARENTANIMALID", post_field: "animal", label: _("Mother"), type: "animal", animalfilter: "female" },
            { json_field: "SPECIESID", post_field: "species", label: _("Species"), type: "select", 
                options: { rows: controller.species, valuefield: "ID", displayfield: "SPECIESNAME" }},
            { json_field: "DATE", post_field: "startdate", label: _("Start date"), 
                tooltip: _("The date the litter entered the shelter"), type: "date", validation: "notblank" },
            { json_field: "NUMBERINLITTER", post_field: "numberinlitter", label: _("Number in litter"), type: "number", validation: "notblank" },
            { json_field: "INVALIDDATE", post_field: "expirydate", label: _("Expiry date"), type: "date" },
            { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
        ]
    };

    var table = {
        rows: controller.rows,
        idcolumn: "ID",
        edit: function(row) {
            tableform.fields_populate_from_json(dialog.fields, row);
            tableform.dialog_show_edit(dialog, row, function() {
                tableform.fields_update_row(dialog.fields, row);
                litters.set_extra_fields(row);
                tableform.fields_post(dialog.fields, "mode=update&litterid=" + row.ID, controller.name, function(response) {
                    tableform.table_update(table);
                },
                function(response) {
                    header.show_error(response);
                });
            });
        },
        complete: function(row) {
            return (row.INVALIDDATE && format.date_js(row.INVALIDATE) <= new Date()) || row.CACHEDANIMALSLEFT == 0;
        },
        columns: [
            { field: "ACCEPTANCENUMBER", display: _("Litter Ref"), formatter: function(row) {
                return "<span style=\"white-space: nowrap\">" +
                    "<input type=\"checkbox\" data-id=\"" + row.ID + "\" title=\"" + html.title(_("Select")) + "\" />" +
                    "<a href=\"#\" class=\"link-edit\" data-id=\"" + row.ID + "\">" + row.ACCEPTANCENUMBER + "</a>" +
                    "<a href=\"animal_find_results?mode=ADVANCED&q=&litterid=" + row.ACCEPTANCENUMBER + "\">" + 
                    html.icon("animal", _("View the animals in this litter")) + "</a>" + 
                    "</span>";
            }},
            { field: "PARENTANIMALID", display: _("Parent"), formatter: function(row) {
                if (row.PARENTANIMALID) {
                    return '<a href="animal?id=' + row.PARENTANIMALID + '">' + row.MOTHERNAME + ' - ' + row.MOTHERCODE + '</a>';
                }
                return "";
            }},
            { field: "SPECIESNAME", display: _("Species") },
            { field: "DATE", display: _("Starts"), formatter: tableform.format_date, initialsort: true },
            { field: "INVALIDDATE", display: _("Expires"), formatter: tableform.format_date },
            { field: "NUMBERINLITTER", display: _("Number in litter") },
            { field: "CACHEDANIMALSLEFT", display: _("Remaining") },
            { field: "COMMENTS", display: _("Comments") }
        ]
    };

    var buttons = [
        { id: "new", text: _("New Litter"), icon: "new", enabled: "always", perm: "all", 
             click: function() { 
                tableform.dialog_show_add(dialog, function() {
                    tableform.fields_post(dialog.fields, "mode=create", "litters", function(response) {
                        var row = {};
                        row.ID = response;
                        tableform.fields_update_row(dialog.fields, row);
                        litters.set_extra_fields(row);
                        controller.rows.push(row);
                        tableform.table_update(table);
                    });
                }, function() {
                    var formdata = "mode=nextlitterid";
                    common.ajax_post("litters", formdata, function(result) { $("#litterref").val(result); }, function() { tableform.dialog_close(); });
                });
             } 
         },
         { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dll", 
             click: function() { 
                 tableform.delete_dialog(function() {
                     tableform.buttons_default_state(buttons);
                     var ids = tableform.table_ids(table);
                     common.ajax_post("litters", "mode=delete&ids=" + ids , function() {
                         tableform.table_remove_selected_from_json(table, controller.rows);
                         tableform.table_update(table);
                     });
                 });
             } 
         }
    ];

    litters = {

        render: function() {
            var s = "";
            s += tableform.dialog_render(dialog);
            s += html.content_header(_("Litters"));
            s += tableform.buttons_render(buttons);
            s += tableform.table_render(table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.dialog_bind(dialog);
            tableform.buttons_bind(buttons);
            tableform.table_bind(table, buttons);
            $("#animal").animalchooser().bind("animalchooserchange", function(event, rec) { lastanimal = rec; $("#species").select("value", rec.SPECIESID); });
            $("#animal").animalchooser().bind("animalchooserloaded", function(event, rec) { lastanimal = rec; });
        },

        set_extra_fields: function(row) {
            row.MOTHERNAME = lastanimal.ANIMALNAME;
            row.MOTHERCODE = lastanimal.SHELTERCODE;
            row.SPECIESNAME = common.get_field(controller.species, row.SPECIESID, "SPECIESNAME");
            if (row.CACHEDANIMALSLEFT === undefined) {
                row.CACHEDANIMALSLEFT = row.NUMBERINLITTER;
            }
        },

        name: "litters",
        animation: "book"

    };

    common.module_register(litters);

});
