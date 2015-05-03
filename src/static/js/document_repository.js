/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var dialog = {
        add_title: _("Upload Document"),
        close_on_ok: true,
        html_form_action: "document_repository",
        html_form_enctype: "multipart/form-data",
        columns: 1,
        width: 550,
        fields: [
            { post_field: "filechooser", label: _("Document file"), type: "file", validation: "notblank" },
            { post_field: "path", label: _("Path"), type: "text" }
        ]
    };

    var table = {
        rows: controller.rows,
        idcolumn: "ID",
        edit: function(row) {
            window.location = "document_repository?dbfsid=" + row.ID;
        },
        columns: [
            { field: "NAME", display: _("Document file") },
            { field: "PATH", display: _("Path"), initialsort: true },
            { field: "MIMETYPE", display: _("Type") }
        ]
    };

    var buttons = [
         { id: "new", text: _("New"), icon: "new", enabled: "always", perm: "ard", 
             click: function() { 
                 tableform.dialog_show_add(dialog, function() {
                     $("#form-tableform").submit();
                 });
             } 
         },
         { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "drd", 
             click: function() { 
                 tableform.delete_dialog(function() {
                     tableform.buttons_default_state(buttons);
                     var ids = tableform.table_ids(table);
                     common.ajax_post("document_repository", "mode=delete&ids=" + ids , function() {
                         tableform.table_remove_selected_from_json(table, controller.rows);
                         tableform.table_update(table);
                     });
                 });
             } 
         }
    ];

    var document_repository = {

        render: function() {
            var s = "";
            s += tableform.dialog_render(dialog);
            s += html.content_header(_("Document Repository"));
            s += html.info(_("This screen allows you to add extra documents to your database, for staff training, reference materials, etc."));
            s += tableform.buttons_render(buttons);
            s += tableform.table_render(table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.dialog_bind(dialog);
            tableform.buttons_bind(buttons);
            tableform.table_bind(table, buttons);
            // Assign name attribute to the path as we're using straight form POST for uploading
            $("#path").attr("name", "path");
        },

        name: "document_repository",
        animation: "options"

    };

    common.module_register(document_repository);

});
