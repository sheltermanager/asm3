/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, FileReader, Modernizr, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var document_repository = {

        model: function() {
            var dialog = {
                add_title: _("Upload Document"),
                close_on_ok: true,
                html_form_action: "document_repository",
                html_form_enctype: "multipart/form-data",
                columns: 1,
                width: 550,
                fields: [
                    { post_field: "filechooser", label: _("Document file"), type: "file", validation: "notblank" },
                    { post_field: "path", label: _("Path"), type: "text" },
                    { type: "raw", label: "", markup: '<input type="hidden" name="mode" value="create" />' }
                ]
            };

            var table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    common.route("document_repository_file?ajax=false&dbfsid=" + row.ID);
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
                         tableform.dialog_show_add(dialog)
                             .then(function() {
                                $("#form-tableform").submit();
                             });
                     } 
                 },
                 { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "drd", 
                     click: function() { 
                         tableform.delete_dialog()
                             .then(function() {
                                tableform.buttons_default_state(buttons);
                                 var ids = tableform.table_ids(table);
                                 return common.ajax_post("document_repository", "mode=delete&ids=" + ids);
                             })
                             .then(function() {
                                 tableform.table_remove_selected_from_json(table, controller.rows);
                                 tableform.table_update(table);
                             });
                     } 
                 },
                { type: "raw", markup: '<div style="min-height: 40px" class="asm-mediadroptarget"><p>' + _("Drop files here...") + '</p></div>',
                    hideif: function() { return !Modernizr.filereader || !Modernizr.todataurljpeg || asm.mobileapp; }}
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        attach_files: function(files) {
            var i = 0, promises = [];
            if (!Modernizr.filereader || !Modernizr.todataurljpeg) { return; }
            header.show_loading(_("Uploading..."));
            for (i = 0; i < files.length; i += 1) {
                promises.push(document_repository.attach_file(files[i])); 
            }
            $.when.apply(this, promises).then(function() {
                header.hide_loading();
                common.route_reload();
            });
        },

        /**
         * Uploads a single file using the FileReader API. 
         * returns a promise.
         */
        attach_file: function(file, comments) {

            var deferred = $.Deferred(),
                docreader = new FileReader();

            docreader.onload = function(e) {
                // TODO: File size check?
                // Post the file data via AJAX
                var formdata = "mode=create&filename=" + encodeURIComponent(file.name) +
                    "&filetype=" + encodeURIComponent(file.type) + 
                    "&filedata=" + encodeURIComponent(e.target.result);
                common.ajax_post(controller.name, formdata)
                    .then(function(result) { 
                        deferred.resolve();
                    })
                    .fail(function() {
                        deferred.reject(); 
                    });
            };
            docreader.readAsDataURL(file);
            return deferred.promise();
        },

        render: function() {
            var s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Document Repository"));
            s += html.info(_("This screen allows you to add extra documents to your database, for staff training, reference materials, etc."));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
            // Assign name attribute to the path as we're using straight form POST for uploading
            $("#path").attr("name", "path");
            // Handle drag and drop
            $(".asm-mediadroptarget").on("dragover", function() {
                $(".asm-mediadroptarget").addClass("asm-mediadroptarget-hover");
                return false;
            });
            $(".asm-mediadroptarget").on("dragleave", function() {
                $(".asm-mediadroptarget").removeClass("asm-mediadroptarget-hover");
                return false;
            });
            $(".asm-mediadroptarget").on("drop", function(e) {
                e.stopPropagation();
                e.preventDefault();
                $(".asm-mediadroptarget").removeClass("asm-mediadroptarget-hover");
                document_repository.attach_files(e.originalEvent.dataTransfer.files);
                return false;
            });
        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        name: "document_repository",
        animation: "options",
        title: function() { return _("Document Repository"); },
        routes: {
            "document_repository": function() {
                common.module_loadandstart("document_repository", "document_repository");
            }
        }

    };

    common.module_register(document_repository);

});
