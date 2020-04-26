/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, log, tableform, validate */
/*global escape, FileReader, Modernizr */

$(function() {

    var media = {
        thumbnail_size: 50, // Size of table thumbnails in px
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

            var dialog = {
                edit_title: _("Edit media"),
                edit_perm: 'cam',
                close_on_ok: true,
                columns: 1,
                fields: [
                    { json_field: "MEDIANOTES", post_field: "medianotes", label: _("Notes"), type: "textarea" },
                    { json_field: "RETAINUNTIL", post_field: "retainuntil", label: _("Retain Until"), type: "date",
                        callout: _("Automatically remove this media item on this date") }
                ]
            };

            var table = {
                rows: controller.media,
                idcolumn: "ID",
                truncatelink: 70, // Only use first 70 chars of MEDIANOTES for edit link
                edit: function(row) {
                    tableform.fields_populate_from_json(dialog.fields, row);
                    tableform.dialog_show_edit(dialog, row)
                        .then(function() {
                            tableform.fields_update_row(dialog.fields, row);
                            return tableform.fields_post(dialog.fields, "mode=update&mediaid=" + row.ID, "media");
                        })
                        .then(function() {
                            tableform.table_update(table);
                            tableform.dialog_enable_buttons();
                        })
                        .fail(function() {
                            tableform.dialog_enable_buttons();
                        });
                },
                change: function(rows) {
                    var all_of_type = function(mime) {
                        // Returns true if all rows are of type mime
                        var rv = true;
                        $.each(rows, function(i, v) {
                            if (v.MEDIAMIMETYPE != mime) { rv = false; }
                        });
                        return rv;
                    };
                    $("#button-web").button("option", "disabled", true); 
                    $("#button-video").button("option", "disabled", true); 
                    $("#button-doc").button("option", "disabled", true); 
                    $("#button-rotateanti").button("option", "disabled", true); 
                    $("#button-rotateclock").button("option", "disabled", true); 
                    $("#button-include").button("option", "disabled", true); 
                    $("#button-exclude").button("option", "disabled", true); 
                    $("#button-emailpdf").button("option", "disabled", true); 
                    $("#button-sign").addClass("ui-state-disabled").addClass("ui-button-disabled");
                    // Only allow the image preferred buttons to be pressed if the
                    // selection size is one and the selection is an image
                    if (rows.length == 1 && rows[0].MEDIAMIMETYPE == "image/jpeg") { 
                        $("#button-web").button("option", "disabled", false); 
                        $("#button-doc").button("option", "disabled", false); 
                    }
                    // Only allow the video preferred button to be pressed if the
                    // selection size is one and the selection is a video link
                    if (rows.length == 1 && rows[0].MEDIATYPE == 2) {
                        $("#button-video").button("option", "disabled", false);
                    }
                    // Only allow the rotate and include buttons to be pressed if the
                    // selection only contains images
                    if (rows.length > 0 && all_of_type("image/jpeg")) {
                        $("#button-rotateanti").button("option", "disabled", false); 
                        $("#button-rotateclock").button("option", "disabled", false); 
                        $("#button-include").button("option", "disabled", false); 
                        $("#button-exclude").button("option", "disabled", false); 
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
                },
                columns: [
                    { field: "MEDIANOTES", display: _("Notes") },
                    { field: "PREVIEW", display: "", formatter: function(m) {
                        var h = [];
                        if (m.MEDIATYPE == 1 || m.MEDIATYPE == 2) {
                            h.push('<a target="_blank" href="' + m.MEDIANAME + '">');
                            var linkimage = "static/images/ui/file-video.png";
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
                            h.push('<img class="asm-thumbnail thumbnailshadow" src="' + linkimage + '" height="' + media.thumbnail_size + 'px" /></a>');
                        }
                        else if (m.MEDIAMIMETYPE == "image/jpeg") {
                            h.push('<a target="_blank" href="image?mode=media&id=' + m.ID + '&date=' + encodeURIComponent(m.DATE) + '">');
                            h.push('<img class="asm-thumbnail thumbnailshadow" src="image?mode=media&id=' + m.ID + '&date=' + encodeURIComponent(m.DATE) + '" height="' + media.thumbnail_size + 'px" /></a>');
                        }
                        else if (m.MEDIAMIMETYPE == "text/html") {
                            h.push('<a target="_blank" href="document_media_edit?id=' + m.ID + '&redirecturl=' + controller.name + '?id=' + m.LINKID + '"> ');
                            h.push('<img class="asm-thumbnail thumbnailshadow" src="static/images/ui/document-media.png" height="' + media.thumbnail_size + 'px" /></a>');
                        }
                        else if (m.MEDIAMIMETYPE == "application/pdf") {
                            h.push('<a target="_blank" href="media?id=' + m.ID + '">');
                            h.push('<img class="asm-thumbnail thumbnailshadow" src="static/images/ui/pdf-media.png" height="' + media.thumbnail_size + 'px" /></a>');
                        }
                        else {
                            h.push('<a target="_blank" href="media?id=' + m.ID + '">');
                            h.push('<img class="asm-thumbnail thumbnailshadow" src="static/images/ui/file-media.png" height="' + media.thumbnail_size + 'px" /></a>');
                        }
                        return h.join("\n");
                    }},
                    { field: "MODIFIERS", display: "", formatter: function(m) {
                        var h = [], mod_out = function(icon, text) {
                            h.push('<span style="white-space: nowrap">');
                            h.push(html.icon(icon, text));
                            h.push( " " + text + "</span><br/>");
                        };
                        if (m.MEDIATYPE > 0) {
                            mod_out("link", _("Link to an external web resource"));
                        }
                        if (m.SIGNATUREHASH) {
                            mod_out("signature", _("Signed"));
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
                            var ru = _("Retain until {0}").replace("{0}", format.date(m.RETAINUNTIL));
                            mod_out("delete", ru);
                        }
                        if (config.bool("AutoRemoveDocumentMedia") && config.integer("AutoRemoveDMYears")) {
                            var dd = common.add_days(format.date_js(m.DATE), config.integer("AutoRemoveDMYears") * 365);
                            var ar = _("Auto remove on {0}").replace("{0}", format.date(dd));
                            mod_out("delete", ar);
                        }
                        return h.join("\n");
                    }},
                    { field: "SIZE", display: _("Size"), formatter: function(m) {
                        if (m.MEDIASIZE < 1024*1024) { return Math.floor(m.MEDIASIZE / 1024) + "K"; }
                        return Math.floor(m.MEDIASIZE / 1024 / 1024.0) + "M";
                    }},
                    { field: "CREATEDDATE", display: _("Added"), formatter: tableform.format_date },
                    { field: "DATE", display: _("Updated"), formatter: tableform.format_date, initialsort: true, initialsortdirection: "desc" },
                    { field: "MEDIAMIMETYPE", display: _("Type") }
                ]
            };

            var buttons = [
                { id: "new", text: _("Attach File"), icon: "media-add", enabled: "always", perm: "aam", tooltip: _("Attach a file") },
                { id: "newlink", text: _("Attach Link"), icon: "link", enabled: "always", perm: "aam", tooltip: _("Attach a link to a web resource") },
                { id: "newdoc", text: _("New Document"), icon: "document", enabled: "always", perm: "aam", tooltip: _("Create a new document") },
                { id: "delete", text: _("Delete"), icon: "media-delete", enabled: "multi", perm: "dam" },
                { id: "email", text: _("Email"), icon: "email", enabled: "multi", perm: "emo", tooltip: _("Email a copy of the selected media files") },
                { id: "emailpdf", text: _("Email PDF"), icon: "pdf", enabled: "multi", perm: "emo", tooltip: _("Email a copy of the selected HTML documents as PDFs") },
                { id: "sign", text: _("Sign"), type: "buttonmenu", icon: "signature" },
                { id: "rotateanti", icon: "rotate-anti", enabled: "multi", perm: "cam", tooltip: _("Rotate image 90 degrees anticlockwise") },
                { id: "rotateclock", icon: "rotate-clock", enabled: "multi", perm:" cam", tooltip: _("Rotate image 90 degrees clockwise") },
                { id: "include", icon: "tick", enabled: "multi", perm: "cam", tooltip: _("Include this image when publishing") }, 
                { id: "exclude", icon: "cross", enabled: "multi", perm: "cam", tooltip: _("Exclude this image when publishing") },
                { id: "web", icon: "web", enabled: "one", perm: "cam", tooltip: _("Make this the default image when viewing this record and publishing to the web") },
                { id: "doc", icon: "document", enabled: "one", perm: "cam", tooltip: _("Make this the default image when creating documents") },
                { id: "video", icon: "video", enabled: "one", perm: "cam", tooltip: _("Make this the default video link when publishing to the web") },
                { type: "raw", markup: '<div style="min-height: 40px" class="asm-mediadroptarget"><p>' + _("Drop files here...") + '</p></div>',
                    hideif: function() { return !Modernizr.filereader || !Modernizr.todataurljpeg || asm.mobileapp; }}
            ];

            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;
        },

        render: function() {
            // Set a dynamic thumbnail size based on number of elements
            if (controller.media.length >= 0) { this.thumbnail_size = 100; }
            if (controller.media.length > 10) { this.thumbnail_size = 70; }
            if (controller.media.length > 20) { this.thumbnail_size = 50; }
            if (controller.media.length > 30) { this.thumbnail_size = 30; }
            this.model();
            var h = [
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

                '<div id="emailform" />',

                '<div id="button-sign-body" class="asm-menu-body">',
                '<ul class="asm-menu-list">',
                    '<li id="button-signscreen" class="asm-menu-item"><a '
                        + '" href="#">' + html.icon("signature") + ' ' + _("Sign on screen") + '</a></li>',
                    '<li id="button-signpad" class="sharebutton asm-menu-item"><a '
                        + '" href="#">' + html.icon("mobile") + ' ' + _("Mobile signing pad") + '</a></li>',
                    '<li id="button-signemail" class="sharebutton asm-menu-item"><a '
                        + '" href="#">' + html.icon("email") + ' ' + _("Request signature by email") + '</a></li>',
                '</ul>',
                '</div>',

                '<div id="dialog-sign" style="display: none" title="' + _("Sign document") + '">',
                '<div id="signature" style="width: 500px; height: 200px;" />',
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

        /**
         * Called by our drag/drop upload widget (which only appears if
         * HTML5 File APIs are available
         */
        attach_files: function(files) {
            var i = 0, promises = [];
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
         * If the file is an image, scales it down first.
         * returns a promise.
         */
        attach_file: function(file, retainfor, comments) {

            var deferred = $.Deferred();

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

            // Is this an image? If so, try to scale it down before sending
            if (file.type.match('image.*')) {

                // Figure out the size we're scaling to
                var media_scaling = config.str("IncomingMediaScaling");
                if (!media_scaling || media_scaling == "None") { media_scaling = "640x640"; }
                var max_width = format.to_int(media_scaling.split("x")[0]);
                var max_height = format.to_int(media_scaling.split("x")[1]);
                if (!max_width) { max_width = 640; }
                if (!max_height) { max_height = 640; }

                // Read the file to an image tag, then render it to
                // an HTML5 canvas to scale it
                var img = document.createElement("img");
                var filedata = null;
                var imreader = new FileReader();
                imreader.onload = function(e) { 
                    filedata = e.target.result;
                    img.src = filedata; 
                };
                img.onload = function() {
                    // Calculate the new image dimensions based on our max
                    var img_width = img.width, img_height = img.height;
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
                    // Scale the image
                    var finalfile = html.scale_image(img, img_width, img_height);

                    // Post the scaled image
                    var formdata = "mode=create&" +
                        "linkid=" + controller.linkid + 
                        "&linktypeid=" + controller.linktypeid + 
                        "&comments=" + encodeURIComponent(comments) + 
                        "&retainfor=" + encodeURIComponent(retainfor) + 
                        "&filename=" + encodeURIComponent(file.name) +
                        "&filetype=" + encodeURIComponent(file.type) + 
                        "&filedata=" + encodeURIComponent(finalfile);
                    common.ajax_post("media", formdata)
                        .then(function(result) { 
                            deferred.resolve();
                        })
                        .fail(function() {
                            deferred.reject(); 
                        });
                };
                imreader.readAsDataURL(file);
            } 
            // It's not an image, just read it and send it to the backend
            else {
                var docreader = new FileReader();
                docreader.onload = function(e) { 
                    // Post the PDF/HTML doc via AJAX
                    var formdata = "mode=create&" +
                        "linkid=" + controller.linkid + 
                        "&linktypeid=" + controller.linktypeid + 
                        "&comments=" + encodeURIComponent(comments) + 
                        "&filename=" + encodeURIComponent(file.name) +
                        "&filetype=" + encodeURIComponent(file.type) + 
                        "&filedata=" + encodeURIComponent(e.target.result);
                    common.ajax_post("media", formdata)
                        .then(function(result) { 
                            deferred.resolve();
                        })
                        .fail(function() {
                            deferred.reject(); 
                        });
                };
                docreader.readAsDataURL(file);
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
            var newweb, newdoc, hasweb, hasdoc, webcount = 0, doccount = 0;
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
            var fname = $("#filechooser").val();
            if ( !media.is_jpeg(fname) && !media.is_extension(fname, "png") && 
                 !media.is_extension(fname, "pdf") && !media.is_extension(fname, "html") ) {
                header.show_error(_("Only PDF, HTML and JPG image files can be attached."));
                return;
            }

            $("#dialog-add").disable_dialog_buttons();

            // Grab the selected file
            var selectedfile = $("#filechooser")[0].files[0];

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
            var yid = "";
            if (s.indexOf("youtube") != -1 && s.indexOf("=") != -1) {
                yid = s.substring(s.indexOf("=") +1);
            }
            if (s.indexOf("youtu.be") != -1 && s.lastIndexOf("/") != -1) {
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
        ajax: function(formdata) {
            common.ajax_post("media", formdata)
                .then(function() { 
                    common.route_reload();
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
                media.attach_files(e.originalEvent.dataTransfer.files);
                return false;
            });


            var addbuttons = { };
            addbuttons[_("Attach")] = media.post_file;
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

            var addlinkbuttons = { };
            addlinkbuttons[_("Attach")] = function() {
                if (!validate.notblank([ "linktarget" ])) { return; }
                $("#dialog-addlink").disable_dialog_buttons();
                var formdata = "mode=createlink&linkid=" + controller.linkid + 
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

            var signbuttons = {};
            signbuttons[_("Sign")] = function() {
                if ($("#signature").signature("isEmpty")) { return; }
                $("#dialog-sign").disable_dialog_buttons();
                var img = $("#signature canvas").get(0).toDataURL("image/png");
                var formdata = "mode=sign&ids=" + tableform.table_ids(media.table);
                formdata += "&signdate=" + encodeURIComponent(format.date(new Date()) + " " + format.time(new Date()));
                formdata += "&sig=" + encodeURIComponent(img);
                media.ajax(formdata);
                $("#dialog-sign").dialog("close");
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
                    var formdata = "mode=delete&ids=" + tableform.table_ids(media.table);
                    $("#dialog-delete").disable_dialog_buttons();
                    media.ajax(formdata);
                });
            });

            // If we aren't including preferred, hide the buttons
            if (!controller.showpreferred) {
                $("#button-web").hide();
                $("#button-doc").hide();
                $("#button-video").hide();
            }

            // Only show include/exclude for animals
            if (controller.name != "animal_media") {
                $("#button-include").hide();
                $("#button-exclude").hide();
            }

            // If this browser doesn't support fileinput, disable the attach button
            if (!Modernizr.fileinput) {
                $("#button-new").button("option", "disabled", true);
            }

            // If this browser doesn't support canvas, hide the sign on screen link
            if (!Modernizr.canvas) {
                $("#button-signscreen").hide();
            }

            $("#button-web").button().click(function() {
                $("#button-web").button("disable");
                var formdata = "mode=web&ids=" + tableform.table_ids(media.table);
                media.ajax(formdata);
            });

            $("#button-video").button().click(function() {
                $("#button-video").button("disable");
                var formdata = "mode=video&ids=" + tableform.table_ids(media.table);
                media.ajax(formdata);
            });

            $("#button-rotateanti").button().click(function() {
                $("#button-rotateanti").button("disable");
                var formdata = "mode=rotateanti&ids=" + tableform.table_ids(media.table);
                media.ajax(formdata);
            });

            $("#button-rotateclock").button().click(function() {
                $("#button-rotateclock").button("disable");
                var formdata = "mode=rotateclock&ids=" + tableform.table_ids(media.table);
                media.ajax(formdata);
            });

            $("#button-doc").button().click(function() {
                $("#button-doc").button("disable");
                var formdata = "mode=doc&ids=" + tableform.table_ids(media.table);
                media.ajax(formdata);
            });

            $("#button-include").button().click(function() {
                $("#button-include").button("disable");
                var formdata = "mode=include&ids=" + tableform.table_ids(media.table);
                media.ajax(formdata);
            });

            $("#button-exclude").button().click(function() {
                $("#button-exclude").button("disable");
                var formdata = "mode=exclude&ids=" + tableform.table_ids(media.table);
                media.ajax(formdata);
            });

            var defaultemail = "", defaultname = "";
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

            $("#button-email").button().click(function() {
                $("#emailform").emailform("show", {
                    title: _("Email media"),
                    post: "media",
                    formdata: "mode=email" +
                        "&ids=" + tableform.table_ids(media.table),
                    name: defaultname,
                    email: defaultemail,
                    subject: tableform.table_selected_row(media.table).MEDIANOTES,
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
                    subject: tableform.table_selected_row(media.table).MEDIANOTES,
                    personid: (controller.person && controller.person.ID),
                    templates: controller.templates,
                    logtypes: controller.logtypes
                });
            });

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
                var formdata = "mode=signpad&ids=" + tableform.table_ids(media.table);
                common.ajax_post("media", formdata)
                    .then(function(result) {
                        header.show_info(_("Sent to mobile signing pad."));
                    });
                return false;
            });

            if (controller.sigtype != "touch") {
                $("#button-sign").hide();
            }

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

        sync: function() {

            if (controller.newmedia) { media.new_media(); }

            // Check if we have pictures but no preferred set and choose one if we don't
            media.check_preferred_images();
        },

        destroy: function() {
            tableform.dialog_destroy();
            common.widget_destroy("#dialog-add");
            common.widget_destroy("#dialog-addlink");
            common.widget_destroy("#dialog-sign");
            common.widget_destroy("#emailform");
        },

        name: "media",
        animation: "formtab",
        title:  function() { 
            var t = "";
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
