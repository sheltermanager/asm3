/*global $, jQuery, FileReader, Modernizr, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const document_repository = {

        model: function() {
            const dialog = {
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

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    common.route("document_repository_file?ajax=false&dbfsid=" + encodeURIComponent(row.ID));
                },
                button_click: function() {
                    common.copy_to_clipboard($(this).attr("data"));
                    header.show_info(_("Successfully copied to the clipboard."));
                    return false;
                },
                columns: [
                    { field: "NAME", display: _("Document file"),
                        formatter: function(row) {
                            let absurl = asm.serviceurl + "?";
                            if (asm.useraccountalias) { absurl += "account=" + asm.useraccountalias + "&"; }
                            absurl += "method=document_repository&mediaid=" + row.ID;
                            return "<span style=\"white-space: nowrap\">" +
                                "<input type=\"checkbox\" data-id=\"" + row.ID + "\" />" +
                                '<a href="#" class="link-edit" data-id="' + row.ID + '">' + row.NAME + '</a> ' +
                                '<button type="button" data-icon="extlink" data="' + absurl + '">' + 
                                _("Copy absolute service URL to the clipboard (for external use in web pages and emails)") + 
                                '</button></span>';
                        }
                    },
                    { field: "PATH", display: _("Path"), initialsort: true },
                    { field: "MIMETYPE", display: _("Type") }
                ]
            };

            const buttons = [
                { id: "new", text: _("New"), icon: "new", enabled: "always", perm: "ard", 
                    click: async function() { 
                        await tableform.dialog_show_add(dialog);
                        $("#form-tableform").submit();
                     } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "drd", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("document_repository", "mode=delete&ids=" + encodeURIComponent(ids));
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "email", text: _("Email"), icon: "email", enabled: "multi", perm: "emo",
                    click: function() {
                        $("#emailform").emailform("show", {
                            title: _("Email media"),
                            post: "document_repository",
                            formdata: "mode=email" +
                                "&ids=" + tableform.table_ids(table),
                            subject: tableform.table_selected_row(table).NAME,
                            templates: controller.templates
                        });
                    }
                },
                { type: "raw", markup: '<div class="asm-mediadroptarget"><p>' + _("Drop files here...") + '</p></div>',
                    hideif: function() { return !Modernizr.filereader || !Modernizr.todataurljpeg || common.browser_is.mobile || asm.mobileapp; }},
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        attach_files: function(files) {
            let i = 0, promises = [];
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

            let deferred = $.Deferred(),
                docreader = new FileReader();

            docreader.onload = function(e) {
                // TODO: File size check?
                // Post the file data via AJAX
                let formdata = "mode=create&filename=" + encodeURIComponent(file.name) +
                    "&filetype=" + encodeURIComponent(file.type) + 
                    "&filedata=" + encodeURIComponent(e.target.result);
                common.ajax_post("document_repository", formdata)
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
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += '<div id="emailform"></div>';
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
            $("#emailform").emailform();
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
            common.widget_destroy("#emailform");
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
