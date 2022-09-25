/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, log, tableform, validate */
/*global escape, FileReader, Modernizr */

$(function() {

    const media = {

        icon_mode_active: true,

        retain_for_years: [
            "0|" + _("Indefinitely"),
            "1|" + _("1 year"),
            "2|" + _("{0} years").replace("{0}", 2),
            "3|" + _("{0} years").replace("{0}", 3),
            "4|" + _("{0} years").replace("{0}", 4),
            "5|" + _("{0} years").replace("{0}", 5),
            "6|" + _("{0} years").replace("{0}", 6),
            "7|" + _("{0} years").replace("{0}", 7),
            "8|" + _("{0} years").replace("{0}", 8),
            "9|" + _("{0} years").replace("{0}", 9)
        ],

        model: function() {

            const dialog = {
                edit_title: _("Edit media"),
                edit_perm: 'cam',
                close_on_ok: true,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "MEDIANOTES", post_field: "medianotes", label: _("Notes"), type: "textarea" },
                    { json_field: "RETAINUNTIL", post_field: "retainuntil", label: _("Retain Until"), type: "date",
                        callout: _("Automatically remove this media item on this date") }
                ]
            };

            const table = {
                rows: controller.media,
                idcolumn: "ID",
                truncatelink: 50, // Only use first 50 chars of MEDIANOTES for edit link
                edit: async function(row) {
                    tableform.fields_populate_from_json(dialog.fields, row);
                    await tableform.dialog_show_edit(dialog, row);
                    tableform.fields_update_row(dialog.fields, row);
                    await tableform.fields_post(dialog.fields, "mode=update&mediaid=" + row.ID, "media");
                    tableform.table_update(table);
                    tableform.dialog_enable_buttons();
                    if (media.icon_mode_active) { media.mode_icon(); } else { media.mode_table(); }
                },
                change: function(rows) {
                    const all_of_type = function(mime) {
                        // Returns true if all rows are of type mime
                        let rv = true;
                        $.each(rows, function(i, v) {
                            if (v.MEDIAMIMETYPE != mime) { rv = false; }
                        });
                        return rv;
                    };
                    const no_links = function() {
                        let rv = true;
                        $.each(rows, function(i, v) {
                            if (v.MEDIATYPE != 0) { rv = false; }
                        });
                        return rv;
                    };
                    $("#button-video").button("option", "disabled", true); 
                    $("#button-email").button("option", "disabled", true); 
                    $("#button-emailpdf").button("option", "disabled", true); 
                    $("#button-image").addClass("ui-state-disabled").addClass("ui-button-disabled");
                    $("#button-move").addClass("ui-state-disabled").addClass("ui-button-disabled");
                    $("#button-sign").addClass("ui-state-disabled").addClass("ui-button-disabled");
                    // Only allow the video preferred button to be pressed if the
                    // selection size is one and the selection is a video link
                    if (rows.length == 1 && rows[0].MEDIATYPE == 2) {
                        $("#button-video").button("option", "disabled", false);
                    }
                    // Only allow the image buttons to be pressed if the
                    // selection only contains images and the user has the permission to change media
                    if (rows.length > 0 && all_of_type("image/jpeg") && common.has_permission("cam")) {
                        $("#button-image").removeClass("ui-state-disabled").removeClass("ui-button-disabled");
                    }
                    // Only allow the email button to be pressed if the selection
                    // does not contain any links
                    if (rows.length > 0 && no_links()) {
                        $("#button-email").button("option", "disabled", false);
                    }
                    // Only allow the email pdf button to be pressed if the
                    // selection only contains documents
                    if (rows.length > 0 && all_of_type("text/html")) {
                        $("#button-emailpdf").button("option", "disabled", false); 
                    }
                    // Only allow the sign buttons to be pressed if the
                    // selection only contains unsigned documents
                    if (rows.length > 0 && all_of_type("text/html") && !rows[0].SIGNATUREHASH) {
                        $("#button-sign").removeClass("ui-state-disabled").removeClass("ui-button-disabled");
                    }
                    // Move is allowed as long as we have at least 1 row selected
                    if (rows.length > 0) {
                        $("#button-move").removeClass("ui-state-disabled").removeClass("ui-button-disabled");
                    }
                },
                columns: [
                    { field: "MEDIANOTES", classes: "mode-table", display: _("Notes"), 
                        sorttext: function(m) { 
                            return m.MEDIANOTES; 
                        }
                    },
                    { field: "PREVIEW", classes: "mode-table", display: "", formatter: function(m) {
                        let h = [];
                        h.push(media.render_preview_thumbnail(m));
                        h.push(media.render_mods(m, true));
                        return h.join("");
                    }},
                    { field: "SIZE", classes: "mode-table", display: _("Size"), 
                        formatter: function(m) {
                            if (m.MEDIATYPE != 0) { return ""; } // do not show a size for non-files
                            if (m.MEDIASIZE < 1024*1024) { return Math.floor(m.MEDIASIZE / 1024) + "K"; }
                            return Math.floor(m.MEDIASIZE / 1024 / 1024.0) + "M";
                        }, 
                        sorttext: function(m) { 
                            return m.MEDIASIZE; 
                        }
                    },
                    { field: "CREATEDDATE", classes: "mode-table", display: _("Added"), formatter: tableform.format_date, initialsort: true, initialsortdirection: "desc" },
                    { field: "DATE", classes: "mode-table", display: _("Updated"), formatter: tableform.format_date },
                    { field: "MEDIAMIMETYPE", classes: "mode-table", display: _("Type") },
                    { field: "PREVIEWICON", classes: "mode-icon", display: "", formatter: function(m) {
                        let h = [];
                        h.push("<div class=\"centered\">");
                        h.push(media.render_preview_thumbnail(m, true));
                        h.push("<br/>");
                        if (m.MEDIAMIMETYPE != "image/jpeg") { h.push("<span>" + html.truncate(m.MEDIANOTES, 30) + "</span><br/>" ); }
                        h.push("<span style=\"white-space: nowrap\">");
                        h.push("<input type=\"checkbox\" data-id=\"" + m.ID + "\" title=\"" + html.title(_("Select")) + "\" />");
                        h.push("<a href=\"#\" class=\"link-edit\" data-id=\"" + m.ID + "\">" + format.date(m.DATE) + "</a>");
                        h.push("</span><br/>");
                        h.push(media.render_mods(m));
                        h.push("</div>");
                        return h.join("");
                    }}
                ]
            };

            const buttons = [
                { id: "new", text: _("Attach File"), icon: "media-add", enabled: "always", perm: "aam", tooltip: _("Attach a file") },
                { id: "newlink", text: _("Attach Link"), icon: "link", enabled: "always", perm: "aam", tooltip: _("Attach a link to a web resource") },
                { id: "newdoc", text: _("New Document"), icon: "document", enabled: "always", perm: "aam", tooltip: _("Create a new document") },
                { id: "delete", text: _("Delete"), icon: "media-delete", enabled: "multi", perm: "dam" },
                { id: "email", text: _("Email"), icon: "email", enabled: "multi", perm: "emo", tooltip: _("Email a copy of the selected media files") },
                { id: "emailpdf", text: _("Email PDF"), icon: "pdf", enabled: "multi", perm: "emo", tooltip: _("Email a copy of the selected HTML documents as PDFs") },
                { id: "image", text: _("Image"), type: "buttonmenu", icon: "image", perm: "cam" },
                { id: "sign", text: _("Sign"), type: "buttonmenu", icon: "signature" },
                { id: "move", text: _("Move"), type: "buttonmenu", icon: "copy" },
                { id: "video", icon: "video", enabled: "one", perm: "cam", tooltip: _("Default video link") },
                { type: "raw", markup: '<div class="asm-mediadroptarget mode-table"><p>' + _("Drop files here...") + '</p></div>',
                    hideif: function() { return !Modernizr.filereader || !Modernizr.todataurljpeg || asm.mobileapp; }},
                { id: "viewmode", text: "", icon: "batch", enabled: "always", tooltip: _("Toggle table/icon view") }
            ];

            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;
        },

        render: function() {
            this.model();
            let h = [
                tableform.dialog_render(this.dialog),

                '<div id="dialog-add" style="display: none" title="' + html.title(_("Attach File")) + '">',
                '<div id="tipattach" class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                _("Please select a PDF, HTML or JPG image file to attach"),
                '</p>',
                '</div>',
                '<form id="addform" method="post" enctype="multipart/form-data" action="media">',
                '<input type="hidden" name="mode" value="create" />',
                '<input type="hidden" id="linkid" name="linkid" value="' + controller.linkid + '" />',
                '<input type="hidden" id="linktypeid" name="linktypeid" value="' + controller.linktypeid + '" />',
                '<input type="hidden" id="controller" name="controller" value="' + controller.name + '" />',
                '<table width="100%">',
                '<tr>',
                '<td><label for="filechooser">' + _("File") + '</label></td>',
                '<td><input id="filechooser" name="filechooser" type="file" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="retainfor">' + _("Retain for") + '</label></td>',
                '<td><select id="retainfor" name="retainfor" class="asm-selectbox">',
                html.list_to_options(media.retain_for_years),
                '</select></td>',
                '</tr>',
                '<tr id="commentsrow">',
                '<td><label for="comments">' + _("Notes") + '</label>',
                controller.name.indexOf("animal") == 0 ? '<button type="button" id="button-comments">' + _('Copy from animal comments') + '</button>' : "",
                '</td>',
                '<td><textarea id="addcomments" name="comments" rows="10" autofocus="autofocus" class="asm-textarea"></textarea>',
                '</td>',
                '</tr>',
                '</table>',
                '</form>',
                '</div>',

                '<div id="dialog-addlink" style="display: none" title="' + html.title(_("Attach link")) + '">',
                '<div id="tipattachlink" class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                _("The URL is the address of a web resource, eg: www.youtube.com/watch?v=xxxxxx"),
                '</p>',
                '</div>',
                '<input type="hidden" data="mode" value="createlink" />',
                '<input type="hidden" id="linkid" data="linkid" value="' + controller.linkid + '" />',
                '<input type="hidden" id="linktypeid" data="linktypeid" value="' + controller.linktypeid + '" />',
                '<input type="hidden" id="controller" data="controller" value="' + controller.name + '" />',
                '<table width="100%">',
                '<tr>',
                '<td><label for="linktype">' + _("Type") + '</label></td>',
                '<td><select id="linktype" data="linktype" class="asm-selectbox">',
                '<option value="1">' + _("Document Link") + '</option>',
                '<option value="2">' + _("Video Link") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="linktarget">' + _("URL") + '</label></td>',
                '<td><input id="linktarget" data="linktarget" class="asm-textbox asm-doubletextbox" /></td>',
                '</tr>',
                '<tr id="commentsrow">',
                '<td><label for="linkcomments">' + _("Notes") + '</label>',
                '</td>',
                '<td><textarea id="linkcomments" data="comments" rows="10" class="asm-textarea"></textarea>',
                '</td>',
                '</tr>',
                '</table>',
                '</div>',

                '<div id="dialog-moveanimal" style="display: none" title="' + html.title(_("Move to an animal")) + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="moveanimal">' + _("Animal") + '</label></td>',
                '<td><input type="hidden" class="asm-animalchooser" id="moveanimal" /></td>',
                '</tr>',
                '</table>',
                '</div>',

                '<div id="dialog-moveperson" style="display: none" title="' + html.title(_("Move to a person")) + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="moveperson">' + _("Person") + '</label></td>',
                '<td><input type="hidden" class="asm-personchooser" id="moveperson" /></td>',
                '</tr>',
                '</table>',
                '</div>',

                '<div id="emailform"></div>',

                '<div id="button-sign-body" class="asm-menu-body">',
                '<ul class="asm-menu-list">',
                    '<li id="button-signscreen" class="asm-menu-item"><a '
                        + ' href="#">' + html.icon("signature") + ' ' + _("Sign on screen") + '</a></li>',
                    '<li id="button-signpad" class="sharebutton asm-menu-item"><a '
                        + ' href="#">' + html.icon("mobile") + ' ' + _("Mobile signing pad") + '</a></li>',
                    '<li id="button-signemail" class="sharebutton asm-menu-item"><a '
                        + ' href="#">' + html.icon("email") + ' ' + _("Request signature by email") + '</a></li>',
                '</ul>',
                '</div>',

                '<div id="button-move-body" class="asm-menu-body">',
                '<ul class="asm-menu-list">',
                    '<li id="button-moveanimal" class="asm-menu-item"><a '
                        + ' href="#">' + html.icon("animal") + ' ' + _("Move to an animal") + '</a></li>',
                    '<li id="button-moveperson" class="asm-menu-item"><a '
                        + ' href="#">' + html.icon("person") + ' ' + _("Move to a person") + '</a></li>',
                '</ul>',
                '</div>',

                '<div id="button-image-body" class="asm-menu-body">',
                '<ul class="asm-menu-list">',
                    '<li id="button-rotateanti" class="asm-menu-item"><a '
                        + ' href="#">' + html.icon("rotate-anti") + ' ' + _("Rotate image 90 degrees anticlockwise") + '</a></li>',
                    '<li id="button-rotateclock" class="asm-menu-item"><a '
                        + ' href="#">' + html.icon("rotate-clock") + ' ' + _("Rotate image 90 degrees clockwise") + '</a></li>',
                    '<li id="button-watermark" class="asm-menu-item"><a '
                        + ' href="#">' + html.icon("watermark") + ' ' + _("Watermark image with name and logo") + '</a></li>',
                    '<li id="button-include" class="asm-menu-item"><a '
                        + ' href="#">' + html.icon("tick") + ' ' + _("Include this image when publishing") + '</a></li>',
                    '<li id="button-exclude" class="asm-menu-item"><a '
                        + ' href="#">' + html.icon("cross") + ' ' + _("Exclude this image when publishing") + '</a></li>',
                    '<li id="button-web" class="asm-menu-item"><a '
                        + ' href="#">' + html.icon("web") + ' ' + _("Make this the default image for the record") + '</a></li>',
                    '<li id="button-doc" class="asm-menu-item"><a '
                        + ' href="#">' + html.icon("document") + ' ' + _("Make this the default image when creating documents") + '</a></li>',
                    '<li id="button-jpg2pdf" class="asm-menu-item"><a '
                        + ' href="#">' + html.icon("pdf") + ' ' + _("Create a PDF of this image") + '</a></li>',

                '</ul>',
                '</div>',

                '<div id="dialog-sign" style="display: none" title="' + _("Sign document") + '">',
                '<div id="signature" style="width: 500px; height: 200px;"></div>',
                '</div>',

                '<form id="newdocform" method="post" action="media">',
                '<input type="hidden" name="controller" value="' + controller.name + '" />',
                '<input type="hidden" name="linkid" value="' + controller.linkid + '" />',
                '<input type="hidden" name="linktypeid" value="' + controller.linktypeid + '" />',
                '<input type="hidden" name="mode" value="createdoc" />',
                '</form>'
            ];

            if (controller.name == "animal_media") {
                h.push(edit_header.animal_edit_header(controller.animal, "media", controller.tabcounts));
            }
            else if (controller.name == "person_media") {
                h.push(edit_header.person_edit_header(controller.person, "media", controller.tabcounts));
            }
            else if (controller.name == "waitinglist_media") {
                h.push(edit_header.waitinglist_edit_header(controller.animal, "media", controller.tabcounts));
            }
            else if (controller.name == "lostanimal_media") {
                h.push(edit_header.lostfound_edit_header("lost", controller.animal, "media", controller.tabcounts));
            }
            else if (controller.name == "foundanimal_media") {
                h.push(edit_header.lostfound_edit_header("found", controller.animal, "media", controller.tabcounts));
            }
            else if (controller.name == "incident_media") {
                h.push(edit_header.incident_edit_header(controller.incident, "media", controller.tabcounts));
            }

            h.push(tableform.buttons_render(this.buttons)); 
            h.push(tableform.table_render(this.table));
            h.push(html.content_footer());
            return h.join("\n");
        },

        render_preview_thumbnail: function(m, notestooltip) {
            let h = [ '<div class="asm-media-thumb">' ];
            let tt = "";
            if (notestooltip) { tt = 'title="' + html.title(html.truncate(html.decode(m.MEDIANOTES), 70)) + '"'; }
            if (m.MEDIATYPE == 1 || m.MEDIATYPE == 2) {
                h.push('<a href="' + m.MEDIANAME + '">');
                let linkimage = "static/images/ui/file-video.png";
                if (m.MEDIATYPE == 1) {
                    linkimage = "static/images/ui/document-media.png";
                }
                else if (m.MEDIATYPE == 2) {
                    if (m.MEDIANAME.indexOf("youtube.com") != -1 || m.MEDIANAME.indexOf("youtu.be") != -1) {
                        linkimage = media.youtube_thumbnail(m.MEDIANAME);
                        if (!linkimage) {
                            linkimage = "static/images/ui/file-video.png";
                        }
                    }
                }
                h.push('<img class="asm-thumbnail thumbnailshadow" ' + tt + ' src="' + linkimage + '" /></a>');
            }
            else if (m.MEDIAMIMETYPE == "image/jpeg") {
                h.push('<a href="image?db=' + asm.useraccount + '&mode=media&id=' + m.ID + '&date=' + encodeURIComponent(m.DATE) + '">');
                h.push('<img class="asm-thumbnail thumbnailshadow" ' + tt + ' src="image?db=' + asm.useraccount + '&mode=media&id=' + m.ID + '&date=' + encodeURIComponent(m.DATE) + '" /></a>');
            }
            else if (m.MEDIAMIMETYPE == "text/html") {
                h.push('<a href="document_media_edit?id=' + m.ID + '&redirecturl=' + controller.name + '?id=' + m.LINKID + '"> ');
                h.push('<img class="asm-thumbnail thumbnailshadow" ' + tt + ' src="static/images/ui/document-media.png" /></a>');
            }
            else if (m.MEDIAMIMETYPE == "application/pdf") {
                h.push('<a href="' + ( asm.mobileapp ? 'media_pdfjs' : 'media' ) + '?id=' + m.ID + '">');
                h.push('<img class="asm-thumbnail thumbnailshadow" ' + tt + ' src="static/images/ui/pdf-media.png" /></a>');
            }
            else {
                h.push('<a href="media?id=' + m.ID + '">');
                h.push('<img class="asm-thumbnail thumbnailshadow" ' + tt + ' src="static/images/ui/file-media.png" /></a>');
            }
            h.push('</div>');
            return h.join("");
        },

        render_mods: function(m, withlabels) {
            let h = [], mod_out = function(icon, text) {
                if (!withlabels) { h.push(html.icon(icon, text)); }
                else { h.push('<span>' + html.icon(icon, text) + " " + text + "</span><br/>"); }
            };
            h.push('<div class="asm-media-mods">');
            if (m.MEDIATYPE > 0) {
                mod_out("link", _("Link to an external web resource"));
            }
            if (m.SIGNATUREHASH) {
                if (m.SIGNATUREHASH.indexOf("onlineform") == 0) {
                    mod_out("locked", _("Locked"));
                }
                else {
                    mod_out("signature", _("Signed"));
                }
            }
            if (m.WEBSITEPHOTO == 1 && controller.showpreferred) {
                mod_out("web", _("Default image for this record and the web"));
            }
            if (m.WEBSITEVIDEO == 1 && controller.showpreferred) {
                mod_out("video", _("Default video for publishing"));
            }
            if (m.DOCPHOTO == 1 && controller.showpreferred) {
                mod_out("document", _("Default image for documents"));
            }
            if (m.MEDIAMIMETYPE == "image/jpeg" && !m.EXCLUDEFROMPUBLISH && controller.name == "animal_media") {
                mod_out("tick", _('Include this image when publishing'));
            }
            if (m.MEDIAMIMETYPE == "image/jpeg" && m.EXCLUDEFROMPUBLISH && controller.name == "animal_media") {
                mod_out("cross", _('Exclude this image when publishing'));
            }
            if (m.RETAINUNTIL) {
                let ru = _("Retain until {0}").replace("{0}", format.date(m.RETAINUNTIL));
                mod_out("media-delete", ru);
            }
            if (config.bool("AutoRemoveDocumentMedia") && config.integer("AutoRemoveDMYears")) {
                let dd = common.add_days(format.date_js(m.DATE), config.integer("AutoRemoveDMYears") * 365);
                let ar = _("Auto remove on {0}").replace("{0}", format.date(dd));
                mod_out("media-delete", ar);
            }
            h.push('</div>');
            return h.join("");
        },

        /**
         * Called by our drag/drop upload widget (which only appears if
         * HTML5 File APIs are available
         */
        attach_files: function(files) {
            let i = 0, promises = [];
            if (!Modernizr.filereader || !Modernizr.canvas || !Modernizr.todataurljpeg) { return; }
            header.show_loading(_("Uploading..."));
            for (i = 0; i < files.length; i += 1) {
                promises.push(media.attach_file(files[i])); 
            }
            $.when.apply(this, promises).then(function() {
                header.hide_loading();
                common.route_reload();
            });
        },

        /**
         * Uploads a single file using the FileReader API. 
         * If the file is an image, scales it down and rotates it first.
         * returns a promise.
         */
        attach_file: function(file, retainfor, comments) {

            let deferred = $.Deferred();

            // If no values were supplied, make them an empty string instead
            if (!comments) { comments = ""; }
            if (!retainfor) { retainfor = ""; }

            // We're only allowed to upload files of a certain type
            if ( !media.is_jpeg(file.name) && !media.is_extension(file.name, "png") && 
                 !media.is_extension(file.name, "pdf") && !media.is_extension(file.name, "html") ) {
                header.show_error(_("Only PDF, HTML and JPG image files can be attached."));
                deferred.resolve();
                return deferred.promise();
            }

            // Is this an image, the scaling option is on and we have a resize spec?
            // If so, try to scale it down before sending
            if (file.type.match('image.*') && !config.bool("DontUseHTML5Scaling") && controller.resizeimagespec) {

                // Figure out the size we're scaling to
                let media_scaling = controller.resizeimagespec;
                let max_width = format.to_int(media_scaling.split("x")[0]);
                let max_height = format.to_int(media_scaling.split("x")[1]);
                if (!max_width) { max_width = 1024; } // This stops images being mangled if spec is bad
                if (!max_height) { max_height = 1024; }

                // Read the file to an image tag, then scale it
                let img, img_width, img_height;
                html.load_img(file)
                    .then(function(nimg) {
                        img = nimg;
                        // Calculate the new image dimensions based on our max
                        img_width = img.width; 
                        img_height = img.height;
                        if (img_width > img_height) {
                            if (img_width > max_width) {
                                img_height *= max_width / img_width;
                                img_width = max_width;
                            }
                        }
                        else {
                            if (img_height > max_height) {
                                img_width *= max_height / img_height;
                                img_height = max_height;
                            }
                        }
                        // Read the exif orientation so we can correct any rotation
                        // before scaling
                        return html.get_exif_orientation(file);
                    })
                    .then(function(orientation) {
                        // Scale and rotate the image
                        let finalfile = html.scale_image(img, img_width, img_height, orientation);
                        // Post the transformed image
                        let formdata = "mode=create&transformed=1&" +
                            "linkid=" + controller.linkid + 
                            "&linktypeid=" + controller.linktypeid + 
                            "&comments=" + encodeURIComponent(comments) + 
                            "&retainfor=" + encodeURIComponent(retainfor) + 
                            "&filename=" + encodeURIComponent(file.name) +
                            "&filetype=" + encodeURIComponent(file.type) + 
                            "&filedata=" + encodeURIComponent(finalfile);
                        return common.ajax_post("media", formdata);
                    })
                    .then(function(result) {
                        deferred.resolve();
                    })
                    .fail(function() {
                        deferred.reject(); 
                    });
            } 
            // It's not an image, or we aren't transforming images, 
            // just read it and send it to the backend
            else {
                common.read_file_as_data_url(file)
                    .then(function(result) {
                        // Post the PDF/HTML doc via AJAX
                        let formdata = "mode=create&" +
                            "linkid=" + controller.linkid + 
                            "&linktypeid=" + controller.linktypeid + 
                            "&comments=" + encodeURIComponent(comments) + 
                            "&filename=" + encodeURIComponent(file.name) +
                            "&filetype=" + encodeURIComponent(file.type) + 
                            "&filedata=" + encodeURIComponent(result);
                        return common.ajax_post("media", formdata);
                    })
                    .then(function(result) { 
                        deferred.resolve();
                    })
                    .fail(function(result) {
                        deferred.reject();
                    });
            }
            return deferred.promise();
        },

        /** 
         * Goes through our list of media elements and if we have pictures
         * but none preferred for the web or doc, select the first
         * image that is not excluded from publishing.
         * Will also select the first if there's an issue and more than
         * one preferred is selected.
         * Multi-file drag and drop doesn't auto select these values due
         * to it being a race condition.
         * Reloads if a change is made or forcereload is true.
         */
        check_preferred_images: function(forcereload) {
            let newweb, newdoc, hasweb, hasdoc, webcount = 0, doccount = 0;
            if (!controller.showpreferred) { return false; }
            $.each(controller.media, function(i, v) {
                if (media.is_jpeg(v.MEDIANAME) && v.EXCLUDEFROMPUBLISH == 0) {
                    if (!newweb) { newweb = v.ID; }
                    if (!newdoc) { newdoc = v.ID; }
                    if (v.WEBSITEPHOTO) { hasweb = true; webcount += 1; }
                    if (v.DOCPHOTO) { hasdoc = true; doccount += 1; }
                }
            });
            if (!hasweb && !hasdoc && newweb) {
                $.when(
                    common.ajax_post("media", "mode=web&ids=" + newweb),
                    common.ajax_post("media", "mode=doc&ids=" + newweb)
                ).then(function() {
                    common.route_reload();
                });
            }
            else if (!hasweb && newweb) {
                media.ajax("mode=web&ids=" + newweb);
            }
            else if (!hasdoc && newdoc) {
                media.ajax("mode=doc&ids=" + newdoc);
            }
            else if (webcount > 1 && newweb) {
                media.ajax("mode=web&ids=" + newweb);
            }
            else if (doccount > 1 && newdoc) {
                media.ajax("mode=doc&ids=" + newdoc);
            }
            else if (forcereload) {
                common.route_reload();
            }
        },

        /** Posts the file back to the server. If the option is on and we have the
         *  relevant HTML5 APIs and this is a jpeg image, scales it first */
        post_file: function() {
            
            // If we don't have a file, fail validation
            if (!validate.notblank([ "filechooser" ])) { return; }

            // If the file isn't a jpeg or a PDF, fail validation
            let fname = $("#filechooser").val();
            if ( !media.is_jpeg(fname) && !media.is_extension(fname, "png") && 
                 !media.is_extension(fname, "pdf") && !media.is_extension(fname, "html") ) {
                header.show_error(_("Only PDF, HTML and JPG image files can be attached."));
                return;
            }

            $("#dialog-add").disable_dialog_buttons();

            // Grab the selected file
            let selectedfile = $("#filechooser")[0].files[0];

            // If an image isn't selected, do the normal post
            if (!selectedfile.type.match('image.*')) {
                $("#addform").submit();
                return;
            }

            // If the config option is on to disable 
            // client side scaling, do the normal form post instead
            if (config.bool("DontUseHTML5Scaling")) {
                $("#addform").submit();
                return;
            }

            // We need the right APIs to scale an image, if we don't
            // have them just send the file to the backend
            if (!Modernizr.filereader || !Modernizr.canvas || !Modernizr.todataurljpeg) { 
                $("#addform").submit();
                return;
            }

            // Attach the file with the HTML5 APIs
            header.show_loading(_("Uploading..."));
            media.attach_file(selectedfile, $("#retainfor").val(), $("#addcomments").val())
                .then(function() {
                    header.hide_loading();
                    common.route_reload(); 
                });
        },

        is_extension: function(s, ext) {
            return s.toLowerCase().indexOf("." + ext) != -1;
        },

        is_jpeg: function(s) {
            return media.is_extension(s, "jpg") || media.is_extension(s, "jpeg");
        },

        /**
         * Turns a YouTube watch URL into the default thumbnail source
         * s: A youtube URL www.youtube.com/watch?v=ID
         */
        youtube_thumbnail: function(s) {
            let yid = "";
            if (s.indexOf("youtube.com") != -1 && s.indexOf("?v=") != -1) {
                yid = s.substring(s.lastIndexOf("=") +1);
            }
            else if (s.indexOf("youtube.com/shorts/") != -1) {
                yid = s.substring(s.lastIndexOf("/") +1);
            }
            else if (s.indexOf("youtu.be") != -1 && s.lastIndexOf("/") != -1) {
                yid = s.substring(s.lastIndexOf("/") +1);
            }
            if (yid) {
                return "https://img.youtube.com/vi/" + yid + "/default.jpg";
            }
            return "";
        },

        /**
         * Friendly function to post formdata back to the controller.
         * On success, it reloads the page, on error it shows it in the
         * header.
         */
        ajax: async function(formdata) {
            await common.ajax_post("media", formdata);
            common.route_reload();
        },

        /** Binds the event handlers to a file drop target.
         *  We do it this way because the one in the table can be dynamically
         *  removed when the table is updated in icon mode.
         *  I implemented this as a delegate against #asm-content the first time, but 
         *  originalEvent.dataTransfer.files is null when the event bubbles up.
         */
        bind_droptarget: function(selector) {

            $(selector).on("dragover", function() {
                $(".asm-mediadroptarget").addClass("asm-mediadroptarget-hover");
                return false;
            });
            $(selector).on("dragleave", function() {
                $(".asm-mediadroptarget").removeClass("asm-mediadroptarget-hover");
                return false;
            });
            $(selector).on("drop", function(e) {
                e.stopPropagation();
                e.preventDefault();
                $(".asm-mediadroptarget").removeClass("asm-mediadroptarget-hover");
                media.attach_files(e.originalEvent.dataTransfer.files);
                return false;
            });

        },

        bind: function() {

            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);

            $(".asm-tabbar").asmtabs();
            $("#emailform").emailform();

            if (Modernizr.canvas) {
                $("#signature").signature({ guideline: true });
            }

            this.bind_droptarget(".asm-mediadroptarget");

            let addbuttons = { };
            addbuttons[_("Attach")] = {
                text: _("Attach"),
                "class": "asm-dialog-actionbutton",
                click: media.post_file
            };
            addbuttons[_("Cancel")] = function() {
                $("#dialog-add").dialog("close");
            };

            $("#dialog-add").dialog({
                autoOpen: false,
                width: 550,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: addbuttons
            });

            let addlinkbuttons = { };
            addlinkbuttons[_("Attach")] = {
                text: _("Attach"),
                "class": "asm-dialog-actionbutton",
                click: function() {
                    if (!validate.notblank([ "linktarget" ])) { return; }
                    $("#dialog-addlink").disable_dialog_buttons();
                    let formdata = "mode=createlink&linkid=" + controller.linkid + 
                        "&linktypeid=" + controller.linktypeid + 
                        "&controller=" + controller.name + "&" +
                        $("#linktype, #linktarget, #linkcomments").toPOST();
                    common.ajax_post("media", formdata)
                        .then(function() {
                            $("#dialog-addlink").dialog("close").enable_dialog_buttons();
                            common.route_reload();
                        })
                        .fail(function() {
                            $("#dialog-addlink").dialog("close").enable_dialog_buttons(); 
                        });
                }
            };
            addlinkbuttons[_("Cancel")] = function() {
                $("#dialog-addlink").dialog("close");
            };

            $("#dialog-addlink").dialog({
                autoOpen: false,
                width: 550,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: addlinkbuttons
            });

            let signbuttons = {};
            signbuttons[_("Sign")] = {
                text: _("Sign"),
                "class": 'asm-dialog-actionbutton',
                click: function() {
                    if ($("#signature").signature("isEmpty")) { return; }
                    $("#dialog-sign").disable_dialog_buttons();
                    var img = $("#signature canvas").get(0).toDataURL("image/png");
                    var formdata = "mode=sign&ids=" + tableform.table_ids(media.table);
                    formdata += "&signdate=" + encodeURIComponent(format.date(new Date()) + " " + format.time(new Date()));
                    formdata += "&sig=" + encodeURIComponent(img);
                    media.ajax(formdata);
                    $("#dialog-sign").dialog("close");
                }
            };
            signbuttons[_("Clear")] = function() {
                $("#signature").signature("clear");
            };
            signbuttons[_("Cancel")] = function() {
                $("#dialog-sign").dialog("close");
            };

            $("#dialog-sign").dialog({
                autoOpen: false,
                width: 550,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.edit_show,
                hide: dlgfx.edit_hide,
                buttons: signbuttons
            });

            let moveanimalbuttons = {};
            moveanimalbuttons[_("Move")] = {
                text: _("Move"),
                "class": 'asm-dialog-actionbutton',
                click: function() {
                    if (!validate.notblank([ "moveanimal" ])) { return; }
                    let formdata = "mode=moveanimal&animalid=" + $("#moveanimal").val() + "&ids=" + tableform.table_ids(media.table);
                    media.ajax(formdata);
                    common.route_reload();
                }
            };
            moveanimalbuttons[_("Cancel")] = function() {
                $("#dialog-moveanimal").dialog("close");
            };

            $("#dialog-moveanimal").dialog({
                autoOpen: false,
                width: 450,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: moveanimalbuttons
            });

            let movepersonbuttons = {};
            movepersonbuttons[_("Move")] = {
                text: _("Move"),
                "class": 'asm-dialog-actionbutton',
                click: function() {
                    if (!validate.notblank([ "moveperson" ])) { return; }
                    let formdata = "mode=moveperson&personid=" + $("#moveperson").val() + "&ids=" + tableform.table_ids(media.table);
                    media.ajax(formdata);
                    common.route_reload();
                }
            };
            movepersonbuttons[_("Cancel")] = function() {
                $("#dialog-moveperson").dialog("close");
            };

            $("#dialog-moveperson").dialog({
                autoOpen: false,
                width: 450,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: movepersonbuttons
            });

            $("#button-viewmode").button().click(function() {
                if (media.icon_mode_active) {
                    media.mode_table();
                }
                else {
                    media.mode_icon();
                }
            });

            $("#button-new").button().click(function() {
                media.new_media();
            });

            $("#button-newdoc").button().click(function() {
                $("#newdocform").submit();
            });

            $("#button-newlink").button().click(function() {
                media.new_link();
            });

            $("#button-comments")
                .button({ icons: { primary: "ui-icon-arrow-1-ne" }, text: false })
                .click(function() {
                    $("#addcomments").val(controller.animal.ANIMALCOMMENTS);
                });

            $("#button-delete").button({disabled: true}).click(function() {
                tableform.delete_dialog(function() {
                    $("#dialog-delete").disable_dialog_buttons();
                    let formdata = "mode=delete&ids=" + tableform.table_ids(media.table);
                    media.ajax(formdata);
                });
            });

            // If we aren't including preferred, hide the buttons
            if (!controller.showpreferred) {
                $("#button-web").hide();
                $("#button-doc").hide();
                $("#button-video").hide();
            }

            // If watermarking isn't available, hide it
            if (!controller.canwatermark) {
                $("#button-watermark").hide();
            }

            // Only show include/exclude for animals
            if (controller.name != "animal_media") {
                $("#button-include").hide();
                $("#button-exclude").hide();
            }

            // If this browser doesn't support canvas, hide the sign on screen link
            if (!Modernizr.canvas) {
                $("#button-signscreen").hide();
            }

            $("#button-web").click(function() {
                let formdata = "mode=web&ids=" + tableform.table_ids(media.table);
                media.ajax(formdata);
            });

            $("#button-video").button().click(function() {
                $("#button-video").button("disable");
                let formdata = "mode=video&ids=" + tableform.table_ids(media.table);
                media.ajax(formdata);
            });

            $("#button-rotateanti").click(function() {
                let formdata = "mode=rotateanti&ids=" + tableform.table_ids(media.table);
                media.ajax(formdata);
            });

            $("#button-rotateclock").click(function() {
                let formdata = "mode=rotateclock&ids=" + tableform.table_ids(media.table);
                media.ajax(formdata);
            });

            $("#button-watermark").click(function() {
                let formdata = "mode=watermark&ids=" + tableform.table_ids(media.table);
                media.ajax(formdata);
            });

            $("#button-jpg2pdf").click(function() {
                let formdata = "mode=jpg2pdf&ids=" + tableform.table_ids(media.table);
                media.ajax(formdata);
            });

            $("#button-doc").click(function() {
                let formdata = "mode=doc&ids=" + tableform.table_ids(media.table);
                media.ajax(formdata);
            });

            $("#button-include").click(function() {
                let formdata = "mode=include&ids=" + tableform.table_ids(media.table);
                media.ajax(formdata);
            });

            $("#button-exclude").click(function() {
                let formdata = "mode=exclude&ids=" + tableform.table_ids(media.table);
                media.ajax(formdata);
            });

            let defaultemail = "", defaultname = "", toaddresses = [];
            // If we have a person, default the email address
            if (controller.person && controller.person.EMAILADDRESS) {
                defaultemail = controller.person.EMAILADDRESS;
                defaultname = controller.person.OWNERNAME;
            }
            // Use the latest reservation/person if the animal is on shelter/foster and a reserve is available
            else if (controller.animal && controller.animal.ARCHIVED == 0 && controller.animal.RESERVEDOWNEREMAILADDRESS) {
                defaultemail = controller.animal.RESERVEDOWNEREMAILADDRESS;
                defaultname = controller.animal.RESERVEDOWNERNAME;
            }
            else if (controller.animal && controller.animal.CURRENTOWNEREMAILADDRESS) {
                defaultemail = controller.animal.CURRENTOWNEREMAILADDRESS;
                defaultname = controller.animal.CURRENTOWNERNAME;
            }
            // Other useful email addresses for animals
            if (controller.animal && controller.animal.RESERVEDOWNEREMAILADDRESS) { 
                toaddresses.push(controller.animal.RESERVEDOWNEREMAILADDRESS);
            }
            if (controller.animal && controller.animal.CURRENTOWNEREMAILADDRESS) { 
                toaddresses.push(controller.animal.CURRENTOWNEREMAILADDRESS);
            }
            if (controller.animal && controller.animal.ADOPTIONCOORDINATOREMAILADDRESS) {
                toaddresses.push(controller.animal.ADOPTIONCOORDINATOREMAILADDRESS);
            }
            if (controller.animal && controller.animal.ORIGINALOWNEREMAILADDRESS) {
                toaddresses.push(controller.animal.ORIGINALOWNEREMAILADDRESS);
            }
            if (controller.animal && controller.animal.BROUGHTINBYEMAILADDRESS) {
                toaddresses.push(controller.animal.BROUGHTINBYEMAILADDRESS);
            }

            $("#button-email").button().click(function() {
                $("#emailform").emailform("show", {
                    title: _("Email media"),
                    post: "media",
                    formdata: "mode=email" +
                        "&ids=" + tableform.table_ids(media.table),
                    name: defaultname,
                    email: defaultemail,
                    toaddresses: toaddresses,
                    subject: media.selected_filenames(),
                    attachments: media.selected_filenames(),
                    animalid: (controller.animal && controller.animal.ID),
                    personid: (controller.person && controller.person.ID),
                    templates: controller.templates,
                    logtypes: controller.logtypes
                });
            });

            $("#button-emailpdf").button().click(function() {
                $("#emailform").emailform("show", {
                    title: _("Email PDF"),
                    post: "media",
                    formdata: "mode=emailpdf" +
                        "&ids=" + tableform.table_ids(media.table),
                    name: defaultname,
                    email: defaultemail,
                    toaddresses: toaddresses,
                    subject: common.replace_all(media.selected_filenames(), ".html", ".pdf"),
                    attachments: common.replace_all(media.selected_filenames(), ".html", ".pdf"),
                    animalid: (controller.animal && controller.animal.ID),
                    personid: (controller.person && controller.person.ID),
                    templates: controller.templates,
                    logtypes: controller.logtypes
                });
            });

            $("#button-image").asmmenu().addClass("ui-state-disabled").addClass("ui-button-disabled");
            $("#button-move").asmmenu().addClass("ui-state-disabled").addClass("ui-button-disabled");
            $("#button-sign").asmmenu().addClass("ui-state-disabled").addClass("ui-button-disabled");

            $("#button-signemail").click(function() {
                $("#button-sign").asmmenu("hide_all");
                $("#emailform").emailform("show", {
                    title: _("Email document for electronic signature"),
                    post: "media",
                    formdata: "mode=emailsign" +
                        "&ids=" + tableform.table_ids(media.table),
                    name: defaultname,
                    email: defaultemail,
                    subject: _("Document signing request"),
                    animalid: (controller.animal && controller.animal.ID),
                    personid: (controller.person && controller.person.ID),
                    templates: controller.templates,
                    logtypes: controller.logtypes,
                    message: _("Please use the links below to electronically sign these documents.")
                });
            });

            $("#button-signscreen").click(function() {
                $("#button-sign").asmmenu("hide_all");
                $("#dialog-sign").dialog("open");
                return false;
            });

            $("#button-signpad").click(function() {
                $("#button-sign").asmmenu("hide_all");
                let formdata = "mode=signpad&ids=" + tableform.table_ids(media.table);
                common.ajax_post("media", formdata)
                    .then(function(result) {
                        header.show_info(_("Sent to mobile signing pad."));
                    });
                return false;
            });

            if (controller.sigtype != "touch") {
                $("#button-sign").hide();
            }

            $("#button-moveanimal").click(function() {
                $("#button-move").asmmenu("hide_all");
                $("#dialog-moveanimal").dialog("open");
            });

            $("#button-moveperson").click(function() {
                $("#button-move").asmmenu("hide_all");
                $("#dialog-moveperson").dialog("open");
            });

        },

        new_link: function() {
           $("#dialog-addlink textarea, #linktarget").val("");
           $("#linktype").select("value", "2");
           $("#dialog-addlink").dialog("open"); 
        },

        new_media: function() {
           $("#dialog-add textarea").val("");
           $("#dialog-add").dialog("open"); 
        },

        mode_icon: function() {
            // Switches to icon mode by changing the table
            // layout and only showing the icon column
            $(".mode-table").hide();
            $(".mode-icon").show();
            $("#tableform thead").hide();
            $("#tableform").css({ "text-align": "center" });
            $("#tableform tr").css({ "display": "inline-block", "vertical-align": "bottom", "border": "1px none transparent" });
            $(".asm-media-thumb img").css({
                "min-width": "85px",
                "min-height": "85px",
                "width": "85px",
                "height": "85px",
                "object-fit": "contain"
            });
            // Add the drop icon if it is not present in the table
            if ($("#tableform .asm-mediadroptarget").length == 0) {
                $("#tableform tbody").prepend('<div class="asm-mediadroptarget mode-icon" style="height: 150px"><p>' + _("Drop files here...") + '</p></div>');
                media.bind_droptarget("#tableform .asm-mediadroptarget");
            }
            media.icon_mode_active = true;
        },

        mode_table: function() {
            // Switches to table mode.
            $(".mode-icon").hide();
            $(".mode-table").show();
            $("#tableform thead").show();
            $("#tableform").css({ "text-align": "left" });
            $("#tableform tr").css({ "display": "table-row", "vertical-align": "middle" });
            // Resize the thumbnails based on the number of media records
            // to fit more rows on screen
            let thumbnail_size = 85;
            if (controller.media.length >= 0) { thumbnail_size = 85; }
            if (controller.media.length > 10) { thumbnail_size = 70; }
            if (controller.media.length > 20) { thumbnail_size = 55; }
            if (controller.media.length > 30) { thumbnail_size = 30; }
            thumbnail_size += "px";
            $(".asm-media-thumb img").css({
                "min-width": thumbnail_size,
                "min-height": thumbnail_size,
                "width": thumbnail_size,
                "height": thumbnail_size,
                "object-fit": "contain"
            });
            media.icon_mode_active = false;
        },

        /** Return a comma separated readable list of selected filenames */
        selected_filenames: function() {
            let items = [];
            $.each(tableform.table_selected_rows(media.table), function(i, v) {
                let s = String(v.MEDIANOTES), ext = v.MEDIANAME.substring(v.MEDIANAME.lastIndexOf("."));
                s = s.replace(" ", "_").replace("/", "_");
                if (s.indexOf(ext) == -1) { s += ext; }
                items.push(s);
            });
            return items.join(", ");
        },

        sync: function() {

            if (controller.newmedia) { media.new_media(); }

            // Start in the correct mode
            if (config.bool("MediaTableMode")) { 
                this.mode_table();
            }
            else {
                this.mode_icon();
            }

            // Check if we have pictures but no preferred set and choose one if we don't
            media.check_preferred_images();
        },

        destroy: function() {
            tableform.dialog_destroy();
            common.widget_destroy("#dialog-add");
            common.widget_destroy("#dialog-addlink");
            common.widget_destroy("#dialog-sign");
            common.widget_destroy("#dialog-moveanimal");
            common.widget_destroy("#dialog-moveperson");
            common.widget_destroy("#emailform");
        },

        name: "media",
        animation: "formtab",
        title:  function() { 
            let t = "";
            if (controller.name == "animal_media") {
                t = common.substitute(_("{0} - {1} ({2} {3} aged {4})"), { 
                    0: controller.animal.ANIMALNAME, 1: controller.animal.CODE, 2: controller.animal.SEXNAME,
                    3: controller.animal.SPECIESNAME, 4: controller.animal.ANIMALAGE }); 
            }
            else if (controller.name == "foundanimal_media") { t = common.substitute(_("Found animal - {0} {1} [{2}]"), {
                0: controller.animal.AGEGROUP, 1: controller.animal.SPECIESNAME, 2: controller.animal.OWNERNAME});
            }
            else if (controller.name == "incident_media") { t = common.substitute(_("Incident {0}, {1}: {2}"), {
                0: controller.incident.ACID, 1: controller.incident.INCIDENTNAME, 2: format.date(controller.incident.INCIDENTDATETIME)});
            }
            else if (controller.name == "lostanimal_media") { t = common.substitute(_("Lost animal - {0} {1} [{2}]"), {
                0: controller.animal.AGEGROUP, 1: controller.animal.SPECIESNAME, 2: controller.animal.OWNERNAME});
            }
            else if (controller.name == "person_media") { t = controller.person.OWNERNAME; }
            else if (controller.name == "waitinglist_media") { t = common.substitute(_("Waiting list entry for {0} ({1})"), {
                0: controller.animal.OWNERNAME, 1: controller.animal.SPECIESNAME });
            }
            return t;
        },

        routes: {
            "animal_media": function() { common.module_loadandstart("media", "animal_media?" + this.rawqs); },
            "foundanimal_media": function() { common.module_loadandstart("media", "foundanimal_media?" + this.rawqs); },
            "incident_media": function() { common.module_loadandstart("media", "incident_media?" + this.rawqs); },
            "lostanimal_media": function() { common.module_loadandstart("media", "lostanimal_media?" + this.rawqs); },
            "person_media": function() { common.module_loadandstart("media", "person_media?" + this.rawqs); },
            "waitinglist_media": function() { common.module_loadandstart("media", "waitinglist_media?" + this.rawqs); }
        }


    };

    common.module_register(media);

});
