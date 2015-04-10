/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    var licence = {};

    var dialog = {
        add_title: _("Add license"),
        edit_title: _("Edit license"),
        edit_perm: 'capl',
        close_on_ok: false,
        columns: 1,
        width: 550,
        fields: [
            { json_field: "OWNERID", post_field: "person", label: _("Person"), type: "person", validation: "notzero" },
            { json_field: "ANIMALID", post_field: "animal", label: _("Animal (optional)"), type: "animal" },
            { json_field: "LICENCETYPEID", post_field: "type", label: _("Type"), type: "select", options: { displayfield: "LICENCETYPENAME", valuefield: "ID", rows: controller.licencetypes }},
            { json_field: "LICENCENUMBER", post_field: "number", label: _("License Number"), type: "text", validation: "notblank" },
            { json_field: "LICENCEFEE", post_field: "fee", label: _("Fee"), type: "currency" },
            { json_field: "ISSUEDATE", post_field: "issuedate", label: _("Issued"), type: "date", validation: "notblank", defaultval: new Date() },
            { json_field: "EXPIRYDATE", post_field: "expirydate", label: _("Expires"), type: "date", validation: "notblank" },
            { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
        ]
    };

    var table = {
        rows: controller.rows,
        idcolumn: "ID",
        edit: function(row) {
            tableform.dialog_show_edit(dialog, row, function() {
                tableform.fields_update_row(dialog.fields, row);
                row.LICENCETYPENAME = common.get_field(controller.licencetypes, row.LICENCETYPEID, "LICENCETYPENAME");
                row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                if (row.ANIMALID && row.ANIMALID != "0") {
                    row.ANIMALNAME = $("#animal").animalchooser("get_selected").ANIMALNAME;
                    row.SHELTERCODE = $("#animal").animalchooser("get_selected").SHELTERCODE;
                }
                else {
                    row.ANIMALID = 0;
                    row.ANIMALNAME = "";
                    row.SHELTERCODE = "";
                }
                tableform.fields_post(dialog.fields, "mode=update&licenceid=" + row.ID, controller.name, function(response) {
                    tableform.table_update(table);
                    tableform.dialog_close();
                }, function() { 
                    tableform.dialog_enable_buttons();
                });
            });
        },
        complete: function(row) {
        },
        overdue: function(row) {
            return row.EXPIRYDATE && format.date_js(row.EXPIRYDATE) < common.today_no_time();
        },
        columns: [
            { field: "LICENCETYPENAME", display: _("Type") },
            { field: "PERSON", display: _("Person"),
                formatter: function(row) {
                    if (row.OWNERID) {
                        return edit_header.person_link(row, row.OWNERID);
                    }
                    return "";
                },
                hideif: function(row) {
                    return controller.name.indexOf("person_") != -1;
                }
            },
            { field: "IMAGE", display: "", 
                formatter: function(row) {
                    if (!row.ANIMALID) { return ""; }
                    return '<a href="animal?id=' + row.ANIMALID + '"><img src=' + html.thumbnail_src(row, "animalthumb") + ' style="margin-right: 8px" class="asm-thumbnail thumbnailshadow" /></a>';
                },
                hideif: function(row) {
                    // Don't show this column if we're in the animal's record or the option is turned off
                    if (controller.name.indexOf("animal_") == 0 || !config.bool("PicturesInBooks")) {
                        return true;
                    }
                }
            },
            { field: "ANIMAL", display: _("Animal"), 
                formatter: function(row) {
                    if (!row.ANIMALID) { return ""; }
                    var s = "";
                    if (controller.name != "animal_licence") { s = html.animal_emblems(row) + " "; }
                    return s + '<a href="animal?id=' + row.ANIMALID + '">' + row.ANIMALNAME + ' - ' + row.SHELTERCODE + '</a>';
                },
                hideif: function(row) {
                    return controller.name.indexOf("animal_") != -1;
                }
            },
            { field: "LICENCENUMBER", display: _("License Number") },
            { field: "LICENCEFEE", display: _("Fee"), formatter: tableform.format_currency },
            { field: "ISSUEDATE", display: _("Issued"), formatter: tableform.format_date, initialsort: true, intialsortdirection: "desc" },
            { field: "EXPIRYDATE", display: _("Expires"), formatter: tableform.format_date },
            { field: "COMMENTS", display: _("Comments") }
        ]
    };

    var buttons = [
         { id: "new", text: _("New License"), icon: "licence", enabled: "always", perm: "aapl",
             click: function() { 
                 $("#person").personchooser("clear");
                 $("#animal").animalchooser("clear");
                 if (controller.person) {
                     $("#person").personchooser("loadbyid", controller.person.ID);
                 }
                 if (controller.animal) {
                    $("#animal").animalchooser("loadbyid", controller.animal.ID);
                 }
                 tableform.dialog_show_add(dialog, function() {
                     tableform.fields_post(dialog.fields, "mode=create", controller.name, function(response) {
                         var row = {};
                         row.ID = response;
                         tableform.fields_update_row(dialog.fields, row);
                         row.LICENCETYPENAME = common.get_field(controller.licencetypes, row.LICENCETYPEID, "LICENCETYPENAME");
                         row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                         if (row.ANIMALID && row.ANIMALID != "0") {
                             row.ANIMALNAME = $("#animal").animalchooser("get_selected").ANIMALNAME;
                             row.SHELTERCODE = $("#animal").animalchooser("get_selected").SHELTERCODE;
                         }
                         else {
                             row.ANIMALID = 0;
                             row.ANIMALNAME = "";
                             row.SHELTERCODE = "";
                         }
                         controller.rows.push(row);
                         tableform.table_update(table);
                         tableform.dialog_close();
                     }, function() {
                         tableform.dialog_enable_buttons();
                     });
                 }, function() { licence.type_change(); });
             } 
         },
         { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dapl",
             click: function() { 
                 tableform.delete_dialog(function() {
                     tableform.buttons_default_state(buttons);
                     var ids = tableform.table_ids(table);
                     common.ajax_post(controller.name, "mode=delete&ids=" + ids , function() {
                         tableform.table_remove_selected_from_json(table, controller.rows);
                         tableform.table_update(table);
                     });
                 });
             } 
         },
         { id: "offset", type: "dropdownfilter", 
             options: [ "i7|" + _("Issued in the last week"), 
                "i31|" + _("Issued in the last month"), 
                "e7|" + _("Expired in the last week"),
                "e31|" + _("Expired in the last month") ],
             click: function(selval) {
                window.location = controller.name + "?offset=" + selval;
             },
             hideif: function(row) {
                 // Don't show for animal or person records
                 if (controller.animal || controller.person) {
                     return true;
                 }
             }
         }
    ];

    licence = {

        render: function() {
            var s = "";
            s += tableform.dialog_render(dialog);
            if (controller.name.indexOf("person_") == 0) {
                s += edit_header.person_edit_header(controller.person, "licence", controller.tabcounts);
            }
            else if (controller.name.indexOf("animal_") == 0) {
                s += edit_header.animal_edit_header(controller.animal, "licence", controller.tabcounts);
            }
            else {
                s += html.content_header(controller.title);
            }
            s += tableform.buttons_render(buttons);
            s += tableform.table_render(table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            $("#type").change(licence.type_change);
            tableform.dialog_bind(dialog);
            tableform.buttons_bind(buttons);
            tableform.table_bind(table, buttons);
        },

        sync: function() {
            // If an offset is given in the querystring, update the select
            if (common.current_url().indexOf("offset=") != -1) {
                var offurl = common.current_url().substring(common.current_url().indexOf("=")+1);
                $("#offset").select("value", offurl);
            }
        },

        type_change: function() {
            var dc = common.get_field(controller.licencetypes, $("#type").select("value"), "DEFAULTCOST");
            $("#fee").currency("value", dc);
        }

    };

    common.module(licence, "licence", "formtab");

});
