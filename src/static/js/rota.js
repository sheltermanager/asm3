/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    var rota = {},
        weekdays = [
            { ID: 1, display: _("Monday") },
            { ID: 2, display: _("Tuesday") },
            { ID: 3, display: _("Wednesday") },
            { ID: 4, display: _("Thursday") },
            { ID: 5, display: _("Friday") },
            { ID: 6, display: _("Saturday") },
            { ID: 7, display: _("Sunday") }
        ];

    $.each(controller.rows, function(i, v) {
        v.WEEKDAYNAME = common.get_field(weekdays, v.WEEKDAY, "display");
    });

    var dialog = {
        add_title: _("Add weekly rota item"),
        edit_title: _("Edit weekly rota item"),
        close_on_ok: true,
        columns: 1,
        width: 550,
        fields: [
            { json_field: "OWNERID", post_field: "person", label: _("Person"), type: "person", validation: "notzero" },
            { json_field: "WEEKDAY", post_field: "weekday", label: _("Weekday"), type: "select", options: { displayfield: "display", valuefield: "ID", rows: weekdays }},
            { json_field: "STARTTIME", post_field: "starttime", label: _("Start Time"), type: "text", classes: "asm-timebox", validation: "notblank", defaultval: "09:00" },
            { json_field: "ENDTIME", post_field: "endtime", label: _("End Time"), type: "text", classes: "asm-timebox", validation: "notblank", defaultval: "17:00" },
            { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
        ]
    };

    var table = {
        rows: controller.rows,
        idcolumn: "ID",
        edit: function(row) {
            tableform.dialog_show_edit(dialog, row, function() {
                tableform.fields_update_row(dialog.fields, row);
                row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                tableform.fields_post(dialog.fields, "mode=update&rotaid=" + row.ID, controller.name, function(response) {
                    tableform.table_update(table);
                    row.WEEKDAYNAME = common.get_field(weekdays, row.WEEKDAY, "display");
                });
            });
        },
        columns: [
            { field: "WEEKDAYNAME", display: _("Weekday") },
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
            { field: "STARTTIME", display: _("Start Time") },
            { field: "ENDTIME", display: _("End Time") },
            { field: "COMMENTS", display: _("Comments") }
        ]
    };

    var buttons = [
         { id: "new", text: _("New Rota"), icon: "new", enabled: "always", perm: "aoro",
             click: function() { 
                 $("#person").personchooser("clear");
                 if (controller.person) {
                     $("#person").personchooser("loadbyid", controller.person.ID);
                 }
                 tableform.dialog_show_add(dialog, function() {
                     tableform.fields_post(dialog.fields, "mode=create", controller.name, function(response) {
                         var row = {};
                         row.ID = response;
                         tableform.fields_update_row(dialog.fields, row);
                         row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                         row.WEEKDAYNAME = common.get_field(weekdays, row.WEEKDAY, "display");
                         controller.rows.push(row);
                         tableform.table_update(table);
                     });
                 });
             } 
         },
         { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "doro",
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
         { id: "hours", text: _("Create Shifts"), icon: "rotahours", enabled: "always", perm: "aorh",
             tooltip: _("Create shift records from this rota"),
             click: function() {
                $("#dialog-shift").dialog("open");
             }
         }
    ];

    rota = {

        render_toshiftdialog: function() {
            return [
                '<div id="dialog-shift" style="display: none" title="' + html.title(_("To Shifts")) + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="shiftstartdate">' + _("Start") + '</label></td>',
                '<td>',
                '<input id="shiftstartdate" data="startdate" type="text" class="asm-textbox asm-halftextbox asm-datebox" />',
                '<input id="shiftstarttime" date="starttime" type="text" class="asm-textbox asm-halftextbox asm-timebox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="shiftenddate">' + _("End") + '</label></td>',
                '<td>',
                '<input id="shiftenddate" data="enddate" type="text" class="asm-textbox asm-halftextbox asm-datebox" />',
                '<input id="shiftendtime" date="endtime" type="text" class="asm-textbox asm-halftextbox asm-timebox" />',
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render: function() {
            var s = "";
            s += tableform.dialog_render(dialog);
            s += this.render_toshiftdialog();
            if (controller.name.indexOf("person_") == 0) {
                s += edit_header.person_edit_header(controller.person, "rota", controller.tabcounts);
            }
            else {
                s += html.content_header(controller.title);
            }
            s += tableform.buttons_render(buttons);
            s += tableform.table_render(table);
            s += html.content_footer();
            return s;
        },

        bind_toshiftdialog: function() {

            var buttons = { };
            buttons[_("Create")] = function() {
                $("#dialog-shift label").removeClass("ui-state-error-text");
                if (!validate.notblank([ "shiftstartdate", "shiftenddate" ])) { return; }
                $("#dialog-shift").disable_dialog_buttons();
                common.ajax_post(controller.name, "mode=createhours&" + $("#dialog-shift input").toPOST(), function() {
                    $("#dialog-shift").dialog("close");
                    $("#dialog-shift").enable_dialog_buttons();
                    header.show_info(_("Shifts successfully created."));
                });
            };
            buttons[_("Cancel")] = function() {
                $("#dialog-shift").dialog("close");
            };

            $("#dialog-shift").dialog({
                autoOpen: false,
                width: 300,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.edit_show,
                hide: dlgfx.edit_hide,
                buttons: buttons
            });
        },


        bind: function() {
            $(".asm-tabbar").asmtabs();
            tableform.dialog_bind(dialog);
            tableform.buttons_bind(buttons);
            tableform.table_bind(table, buttons);
            this.bind_toshiftdialog();
        }

    };

    common.module(rota, "rota", "formtab");

});
