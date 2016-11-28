/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, log, tableform, validate */
/*global escape, FileReader, Modernizr */

$(function() {

    var media = {

        render: function() {
            var h = [
                '<div id="dialog-add" style="display: none" title="' + html.title(_("Attach File")) + '">',
                '<div id="tipattach" class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                _("Please select a PDF, HTML or JPG image file to attach"),
                '</p>',
                '</div>',
                '<form id="addform" method="post" enctype="multipart/form-data" action="' + controller.name + '">',
                '<input type="hidden" id="linkid" name="linkid" value="' + controller.linkid + '" />',
                '<input type="hidden" id="linktypeid" name="linktypeid" value="' + controller.linktypeid + '" />',
                '<input type="hidden" id="controller" name="controller" value="' + controller.name + '" />',
                '<table width="100%">',
                '<tr>',
                '<td><label for="filechooser">' + _("File") + '</label></td>',
                '<td><input id="filechooser" name="filechooser" type="file" /></td>',
                '</tr>',
                '<tr id="commentsrow">',
                '<td><label for="comments">' + _("Notes") + '</label>',
                controller.name.indexOf("animal") == 0 ? '<button type="button" id="button-comments">' + _('Copy from animal comments') + '</button>' : "",
                '</td>',
                '<td><textarea id="addcomments" name="comments" rows="10" autofocus="autofocus" title=',
                '"' + html.title(_("If this is the web preferred image, web publishers will use these notes as the animal description")) + '"',
                ' class="asm-textarea"></textarea>',
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
                '<td><input id="linktarget" data="linktarget" class="asm-textbox" /></td>',
                '</tr>',
                '<tr id="commentsrow">',
                '<td><label for="linkcomments">' + _("Notes") + '</label>',
                '</td>',
                '<td><textarea id="linkcomments" data="comments" rows="10" class="asm-textarea"></textarea>',
                '</td>',
                '</tr>',
                '</table>',
                '</div>',

                '<div id="dialog-edit" style="display: none" title="' + _("Edit media notes") + '">',
                '<form id="editform" method="post" action="' + controller.name + '">',
                '<input type="hidden" name="linkid" value="' + controller.linkid + '" />',
                '<input type="hidden" name="mode" value="update" />',
                '<input type="hidden" id="mediaid" name="mediaid" value="" />',
                '<textarea id="editcomments" name="comments" rows="10" class="asm-textarea"></textarea>',
                '</form>',
                '</div>',

                '<div id="dialog-email" style="display: none" title="' + html.title(_("Email media"))  + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="emailto">' + _("To") + '</label></td>',
                '<td><input id="emailto" type="text" class="asm-doubletextbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="emailnote">' + _("Message") + '</label></td>',
                '<td><div id="emailnote" class="asm-richtextarea" data-margin-top="24px" data-height="200px"></div></td>',
                '</tr>',
                '</table>',
                '</div>',

                '<div id="dialog-emailpdf" style="display: none" title="' + html.title(_("Email PDF"))  + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="emailpdfto">' + _("To") + '</label></td>',
                '<td><input id="emailpdfto" type="text" class="asm-doubletextbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="emailpdfnote">' + _("Message") + '</label></td>',
                '<td><div id="emailpdfnote" class="asm-richtextarea" data-margin-top="24px" data-height="200px"></div></td>',
                '</tr>',
                '</table>',
                '</div>',

                '<div id="dialog-emailsign" style="display: none" title="' + html.title(_("Email document for electronic signature"))  + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="emailsignto">' + _("To") + '</label></td>',
                '<td><input id="emailsignto" type="text" class="asm-doubletextbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="emailsignnote">' + _("Message") + '</label></td>',
                '<td><textarea id="emailsignnote" class="asm-textarea" rows="5"></textarea></td>',
                '</tr>',
                '</table>',
                '</div>',

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

                '<form id="newdocform" method="post" action="' + controller.name + '">',
                '<input type="hidden" name="linkid" value="' + controller.linkid + '" />',
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

            h.push(tableform.buttons_render([
                { id: "new", text: _("Attach File"), icon: "media-add", tooltip: _("Attach a file") },
                { id: "newlink", text: _("Attach Link"), icon: "link", tooltip: _("Attach a link to a web resource") },
                { id: "newdoc", text: _("New Document"), icon: "document", tooltip: _("Create a new document") },
                { id: "delete", text: _("Delete"), icon: "media-delete" },
                { id: "email", text: _("Email"), icon: "email", tooltip: _("Email a copy of the selected media files") },
                { id: "emailpdf", text: _("Email PDF"), icon: "pdf", tooltip: _("Email a copy of the selected HTML documents as PDFs") },
                { id: "sign", text: _("Sign"), type: "buttonmenu", icon: "signature" },
                { id: "rotateanti", icon: "rotate-anti", tooltip: _("Rotate image 90 degrees anticlockwise") },
                { id: "rotateclock", icon: "rotate-clock", tooltip: _("Rotate image 90 degrees clockwise") },
                { id: "web", icon: "web", tooltip: _("Make this the default image when viewing this record and publishing to the web") },
                { id: "doc", icon: "document", tooltip: _("Make this the default image when creating documents") },
                { id: "video", icon: "video", tooltip: _("Make this the default video link when publishing to the web") }
            ]));

            h.push(media.render_items());
            h.push(html.content_footer());
            return h.join("\n");
        },

        render_items: function() {

            var h = [];
            h.push('<div class="asm-mediaicons">');

            // Show our drag and drop target for uploading files if the right APIs are available
            // and we're not in mobile app mode
            if (Modernizr.canvas && Modernizr.filereader && Modernizr.todataurljpeg && !asm.mobileapp) {
                h.push('<div class="asm-mediadroptarget"><p>' + _("Drop files here...") + '</p></div>');
            }

            $.each(controller.media, function(i, m) {
                h.push('<div class="asm-mediaicon" id="mrow-' + m.ID + '" data="' + m.ID + '" >');
                h.push('<input type="hidden" class="media-name" value="' + html.title(m.MEDIANAME) + '" />');
                h.push('<input type="hidden" class="media-type" value="' + html.title(m.MEDIATYPE) + '" />');
                var fullnotes = html.decode(m.MEDIANOTES),
                    shortnotes = html.truncate(html.decode(m.MEDIANOTES), 70);
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
                    h.push('<img class="asm-thumbnail thumbnailshadow" src="' + linkimage + '" height="70px" ');
                    h.push('title="' + html.title(fullnotes) + '" /></a>');
                    h.push('<br />');
                    h.push('<a class="viewlink" title="' + _('View media') + '" href="' + m.MEDIANAME + '">' + shortnotes + '</a>');
                }
                else if (media.is_extension(m.MEDIANAME, "jpg") || media.is_extension(m.MEDIANAME, "jpeg")) {
                    h.push('<a href="image?mode=media&id=' + m.ID + '&date=' + encodeURIComponent(m.DATE) + '">');
                    h.push('<img class="asm-thumbnail thumbnailshadow" src="image?mode=media&id=' + m.ID + '&date=' + encodeURIComponent(m.DATE) + '" title="' + html.title(fullnotes) + '" /></a>');
                }
                else if (media.is_extension(m.MEDIANAME, "html")) {
                    h.push('<a href="document_media_edit?id=' + m.ID + '&redirecturl=' + controller.name + '?id=' + m.LINKID + '"> ');
                    h.push('<img class="asm-thumbnail thumbnailshadow" src="static/images/ui/document-media.png" height="70px" ');
                    h.push('title="' + html.title(fullnotes) + '" /></a>');
                    h.push('<br />');
                    h.push('<a class="viewlink" title="' + _('Edit document') + '" href="document_media_edit?id=' + m.ID + '&redirecturl=' + controller.name + '?id=' + m.LINKID + '">' + shortnotes + '</a>');
                }
                else if (media.is_extension(m.MEDIANAME, "pdf")) {
                    h.push('<a href="media?id=' + m.ID + '">');
                    h.push('<img class="asm-thumbnail thumbnailshadow" src="static/images/ui/pdf-media.png" height="70px" ');
                    h.push('title="' + html.title(fullnotes) + '" /></a>');
                    h.push('<br />');
                    h.push('<a class="viewlink" title="' + _('View PDF') + '" href="media?id=' + m.ID + '">' + shortnotes + '</a>');
                }
                else {
                    h.push('<a href="media?id=' + m.ID + '">');
                    h.push('<img class="asm-thumbnail thumbnailshadow" src="static/images/ui/file-media.png" height="70px" ');
                    h.push('title="' + html.title(fullnotes) + '" /></a>');
                    h.push('<br />');
                    h.push('<a class="viewlink" title="' + _('View media') + '" href="media?id=' + m.ID + '">' + shortnotes + '</a>');
                }
                h.push('<br />');
                h.push('<span style="white-space: nowrap">');
                h.push('<input id="select-' + m.ID + '" class="media-selector" type="checkbox" data="' + m.ID + '" />');
                h.push('<a href="#" class="media-edit-link" data="' + m.ID + '" title="' + html.title(_("Edit notes")) + '">');
                h.push(html.icon("edit"));
                h.push(format.date(m.DATE));
                h.push('</a>');
                if (m.MEDIATYPE > 0) {
                    h.push(html.icon("link", _("Link to an external web resource")));
                }
                if (m.SIGNATUREHASH) {
                    h.push(html.icon("signature", _("Signed")));
                }
                if (m.WEBSITEPHOTO == 1 && controller.showpreferred) {
                    h.push(html.icon("web", _("Default image for this record and the web")));
                }
                if (m.WEBSITEVIDEO == 1 && controller.showpreferred) {
                    h.push(html.icon("video", _("Default video for publishing")));
                }
                if (m.DOCPHOTO == 1 && controller.showpreferred) {
                    h.push(html.icon("document", _("Default image for documents")));
                }
                if (media.is_extension(m.MEDIANAME, "jpg") && m.WEBSITEPHOTO == 0 && !m.EXCLUDEFROMPUBLISH && controller.name == "animal_media") {
                    h.push('<img class="incexc" data="' + m.ID + '" src="static/images/ui/tick.gif" title="' + _('Include this image when publishing') + '" />');
                }
                if (media.is_extension(m.MEDIANAME, "jpg") && m.WEBSITEPHOTO == 0 && m.EXCLUDEFROMPUBLISH && controller.name == "animal_media") {
                    h.push('<img class="incexc" data="' + m.ID + '" src="static/images/ui/cross.gif" title="' + _('Exclude this image when publishing') + '" />');
                }
                h.push('</span>');
                h.push('</div>');
            });
            h.push('</div>');
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
        attach_file: function(file, comments) {

            var deferred = $.Deferred();

            // If no comments were supplied, make them an empty string instead
            if (!comments) { comments = ""; }

            // We're only allowed to upload files of a certain type
            if ( !media.is_extension(file.name, "jpg") && !media.is_extension(file.name, "jpeg") && 
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
                    var canvas = document.createElement("canvas");
                    canvas.width = img_width;
                    canvas.height = img_height;
                    var ctx = canvas.getContext("2d");
                    ctx.drawImage(img, 0, 0, img_width, img_height);
                    var finalfile = canvas.toDataURL("image/jpeg");

                    // Post the scaled image
                    var formdata = "linkid=" + controller.linkid + "&linktypeid=" + controller.linktypeid + 
                        "&comments=" + encodeURIComponent(comments) + 
                        "&filename=" + encodeURIComponent(file.name) +
                        "&filetype=" + encodeURIComponent(file.type) + 
                        "&filedata=" + encodeURIComponent(finalfile);
                    common.ajax_post(controller.name, formdata)
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
                    var formdata = "linkid=" + controller.linkid + 
                        "&linktypeid=" + controller.linktypeid + 
                        "&comments=" + encodeURIComponent(comments) + 
                        "&filename=" + encodeURIComponent(file.name) +
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
            }
            return deferred.promise();
        },

        /** 
         * Goes through our list of media elements and if we have pictures
         * but none preferred for the web or doc, select the first.
         * Multi-file drag and drop doesn't auto select these values due
         * to it being a race condition.
         * Reloads if a change is made or forcereload is true.
         */
        check_preferred_images: function(forcereload) {
            var newweb, newdoc, hasweb, hasdoc;
            if (!controller.showpreferred) { return false; }
            $.each(controller.media, function(i, v) {
                if (v.MEDIANAME.indexOf(".jpg") != -1 || v.MEDIANAME.indexOf(".jpeg") != -1) { 
                    if (!newweb) { newweb = v.ID; }
                    if (!newdoc) { newdoc = v.ID; }
                    if (v.WEBSITEPHOTO) { hasweb = true; }
                    if (v.DOCPHOTO) { hasdoc = true; }
                }
            });
            if (!hasweb && !hasdoc && newweb) {
                $.when(
                    common.ajax_post(controller.name, "mode=web&ids=" + newweb),
                    common.ajax_post(controller.name, "mode=doc&ids=" + newweb)
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
            if ( !media.is_extension(fname, "jpg") && !media.is_extension(fname, "jpeg") && 
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
            media.attach_file(selectedfile, $("#addcomments").val())
                .then(function() {
                    header.hide_loading();
                    common.route_reload(); 
                });
        },

        is_extension: function(s, ext) {
            return s.toLowerCase().indexOf("." + ext) != -1;
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
            common.ajax_post(controller.name, formdata)
                .then(function() { 
                    common.route_reload();
                });
        },

        bind: function() {

            $(".asm-tabbar").asmtabs();
            $("#tipattach").show();

            if (Modernizr.canvas) {
                $("#signature").signature({ guideline: true });
            }

            $(".asm-mediaicons").on("change", "input[type='checkbox']", function() {

                // If the selected element is ticked, apply a highlight style
                // to the media item
                if ($(this).is(":checked")) {
                    $(this).closest(".asm-mediaicon").addClass("ui-state-highlight");
                }
                else {
                    $(this).closest(".asm-mediaicon").removeClass("ui-state-highlight");
                }

                if ($(".asm-mediaicons input:checked").size() > 0) {
                    $("#button-delete").button("option", "disabled", false); 
                }
                else {
                    $("#button-delete").button("option", "disabled", true); 
                }
                $("#button-web").button("option", "disabled", true); 
                $("#button-video").button("option", "disabled", true); 
                $("#button-doc").button("option", "disabled", true); 
                $("#button-rotateanti").button("option", "disabled", true); 
                $("#button-rotateclock").button("option", "disabled", true); 
                $("#button-email").button("option", "disabled", true); 
                $("#button-emailpdf").button("option", "disabled", true); 
                $("#button-sign").addClass("ui-state-disabled").addClass("ui-button-disabled");

                // Only allow the image preferred buttons to be pressed if the
                // selection size is one and the selection is an image
                if ($(".asm-mediaicons input:checked").size() == 1) {
                    $(".asm-mediaicons input:checked").each(function() {
                        var mname = $(this).parent().parent().find(".media-name").val();
                        if (media.is_extension(mname, "jpg") || media.is_extension(mname, "jpeg")) {
                            $("#button-web").button("option", "disabled", false); 
                            $("#button-doc").button("option", "disabled", false); 
                        }
                    });
                }

                // Only allow the video preferred button to be pressed if the
                // selection size is one and the selection is a video link
                if ($(".asm-mediaicons input:checked").size() == 1) {
                    $(".asm-mediaicons input:checked").each(function() {
                        var mtype = $(this).parent().parent().find(".media-type").val();
                        if (mtype == 2) {
                            $("#button-video").button("option", "disabled", false);
                        }
                    });
                }

                // Only allow the rotate buttons to be pressed if the
                // selection only contains images
                $(".asm-mediaicons input:checked").each(function() {
                    var mname = $(this).parent().parent().find(".media-name").val();
                    if (media.is_extension(mname, "jpg") || media.is_extension(mname, "jpeg")) {
                        $("#button-rotateanti").button("option", "disabled", false); 
                        $("#button-rotateclock").button("option", "disabled", false); 
                    }
                });

                // Only allow the email button to be pressed if we have a selection 
                if ($(".asm-mediaicons input:checked").size() > 0) {
                    $("#button-email").button("option", "disabled", false); 
                }

                // Only allow the email pdf button to be pressed if the
                // selection only contains documents
                $(".asm-mediaicons input:checked").each(function() {
                    var mname = $(this).parent().parent().find(".media-name").val();
                    if (media.is_extension(mname, "html")) {
                        $("#button-emailpdf").button("option", "disabled", false); 
                    }
                });

                // Only allow the sign buttons to be pressed if the
                // selection only contains unsigned documents
                $(".asm-mediaicons input:checked").each(function() {
                    var mname = $(this).parent().parent().find(".media-name").val();
                    var issigned = $(this).parent().find(".asm-icon-signature").length > 0;
                    if (media.is_extension(mname, "html") && !issigned ) {
                        $("#button-sign").removeClass("ui-state-disabled").removeClass("ui-button-disabled");
                    }
                });


            });

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
                common.ajax_post(controller.name, formdata)
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

            var editbuttons = { };
            editbuttons[_("Save")] = function() {
                var mediaid = $("#mediaid").val();
                var formdata = "mode=update&mediaid=" + mediaid;
                formdata += "&comments=" + encodeURIComponent($("#editcomments").val());
                $("#dialog-edit").disable_dialog_buttons();
                common.ajax_post(controller.name, formdata)
                    .then(function(result) { 
                        $("#mrow-" + mediaid + " .asm-thumbnail").attr("title", html.title($("#editcomments").val()));
                        $("#mrow-" + mediaid + " .viewlink").text(html.truncate($("#editcomments").val(), 70));
                    })
                    .always(function() {
                        $("#dialog-edit").dialog("close").enable_dialog_buttons();
                    });
            };
            editbuttons[_("Cancel")] = function() {
                $("#dialog-edit").dialog("close");
            };

            $("#dialog-edit").dialog({
                autoOpen: false,
                width: 550,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.edit_show,
                hide: dlgfx.edit_hide,
                buttons: editbuttons
            });

            var signbuttons = {};
            signbuttons[_("Sign")] = function() {
                if ($("#signature").signature("isEmpty")) { return; }
                $("#dialog-sign").disable_dialog_buttons();
                var img = $("#signature canvas").get(0).toDataURL("image/png");
                var formdata = "mode=sign&ids=" + $(".asm-mediaicons input").tableCheckedData();
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
                    var formdata = "mode=delete&ids=" + $(".asm-mediaicons input").tableCheckedData();
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

            // If this browser doesn't support fileinput, disable the attach button
            if (!Modernizr.fileinput) {
                $("#button-new").button("option", "disabled", true);
            }

            // If this browser doesn't support canvas, hide the sign on screen link
            if (!Modernizr.canvas) {
                $("#button-signscreen").hide();
            }

            $("#button-web").button({disabled: true}).click(function() {
                $("#button-web").button("disable");
                var formdata = "mode=web&ids=" + $(".asm-mediaicons input").tableCheckedData();
                media.ajax(formdata);
            });

            $("#button-video").button({disabled: true}).click(function() {
                $("#button-video").button("disable");
                var formdata = "mode=video&ids=" + $(".asm-mediaicons input").tableCheckedData();
                media.ajax(formdata);
            });

            $("#button-email").button({disabled: true}).click(function() {
                // If we have a person, default the email address
                if (controller.person) {
                    $("#emailto").val(controller.person.EMAILADDRESS);
                }
                else if (controller.animal) {
                    $("#emailto").val(controller.animal.CURRENTOWNEREMAILADDRESS);
                }
                // Default the email sig
                if (config.str("EmailSignature")) {
                    $("#emailnote").richtextarea("value", "<p>&nbsp;</p>" + config.str("EmailSignature"));
                }
                tableform.show_okcancel_dialog("#dialog-email", _("Send"), { width: 550, notblank: [ "emailto" ] })
                    .then(function() {
                        var formdata = "mode=email&email=" + encodeURIComponent($("#emailto").val()) + 
                            "&emailnote=" + encodeURIComponent($("#emailnote").richtextarea("value")) + 
                            "&ids=" + $(".asm-mediaicons input").tableCheckedData();
                        return common.ajax_post(controller.name, formdata);
                    })
                    .then(function(result) { 
                        header.show_info(_("Email successfully sent to {0}").replace("{0}", result));
                    });
            });

            $("#button-emailpdf").button({disabled: true}).click(function() {
                // If we have a person, default the email address
                if (controller.person) {
                    $("#emailpdfto").val(controller.person.EMAILADDRESS);
                }
                else if (controller.animal) {
                    $("#emailpdfto").val(controller.animal.CURRENTOWNEREMAILADDRESS);
                }
                // Default the email sig
                if (config.str("EmailSignature")) {
                    $("#emailpdfnote").richtextarea("value", "<p>&nbsp;</p>" + config.str("EmailSignature"));
                }
                tableform.show_okcancel_dialog("#dialog-emailpdf", _("Send"), { width: 550, notblank: [ "emailpdfto" ] })
                    .then(function() {
                        var formdata = "mode=emailpdf&email=" + encodeURIComponent($("#emailpdfto").val()) + 
                            "&emailnote=" + encodeURIComponent($("#emailpdfnote").richtextarea("value")) + 
                            "&ids=" + $(".asm-mediaicons input").tableCheckedData();
                        $("#dialog-emailpdf").dialog("close");
                        return common.ajax_post(controller.name, formdata);
                    })
                    .then(function(result) { 
                        header.show_info(_("Email successfully sent to {0}").replace("{0}", result));
                    });
            });

            $("#button-sign").asmmenu().addClass("ui-state-disabled").addClass("ui-button-disabled");

            $("#button-signemail").click(function() {
                $("#button-sign").asmmenu("hide_all");
                // If we have a person, default the email address
                if (controller.person) {
                    $("#emailsignto").val(controller.person.EMAILADDRESS);
                }
                $("#emailsignnote").html( _("Please use the links below to electronically sign these documents.") );
                tableform.show_okcancel_dialog("#dialog-emailsign", _("Send"), { width: 550, notblank: [ "emailsignto" ] })
                    .then(function() {
                        var formdata = "mode=emailsign&email=" + encodeURIComponent($("#emailsignto").val()) + 
                            "&emailnote=" + encodeURIComponent($("#emailsignnote").val()) + 
                            "&ids=" + $(".asm-mediaicons input").tableCheckedData();
                        $("#dialog-emailsign").dialog("close");
                        return common.ajax_post(controller.name, formdata);
                    })
                    .then(function(result) { 
                        header.show_info(_("Email successfully sent to {0}").replace("{0}", result));
                    });
                return false;
            });

            $("#button-signscreen").click(function() {
                $("#button-sign").asmmenu("hide_all");
                $("#dialog-sign").dialog("open");
                return false;
            });

            $("#button-signpad").click(function() {
                $("#button-sign").asmmenu("hide_all");
                var formdata = "mode=signpad&ids=" + $(".asm-mediaicons input").tableCheckedData();
                common.ajax_post(controller.name, formdata)
                    .then(function(result) {
                        header.show_info(_("Sent to mobile signing pad."));
                    });
                return false;
            });

            if (controller.sigtype != "touch") {
                $("#button-sign").hide();
            }

            $("#button-rotateanti").button({disabled: true}).click(function() {
                $("#button-rotateanti").button("disable");
                var formdata = "mode=rotateanti&ids=" + $(".asm-mediaicons input").tableCheckedData();
                media.ajax(formdata);
            });

            $("#button-rotateclock").button({disabled: true}).click(function() {
                $("#button-rotateclock").button("disable");
                var formdata = "mode=rotateclock&ids=" + $(".asm-mediaicons input").tableCheckedData();
                media.ajax(formdata);
            });


            $("#button-doc").button({disabled: true}).click(function() {
                $("#button-doc").button("disable");
                var formdata = "mode=doc&ids=" + $(".asm-mediaicons input").tableCheckedData();
                media.ajax(formdata);
            });

            $(".incexc").css("cursor", "pointer").click(function() {
                var img = $(this), formdata = "";
                if (img.attr("src").indexOf("tick") != -1) {
                    // Exclude
                    formdata = "mode=exclude&mediaid=" + img.attr("data") + "&exclude=1";
                    common.ajax_post(controller.name, formdata)
                        .then(function(result) { 
                            img.attr("src", "static/images/ui/cross.gif");
                            img.attr("title", _("Exclude this image when publishing"));
                        });
                }
                else {
                    // Include
                    formdata = "mode=exclude&mediaid=" + img.attr("data") + "&exclude=0";
                    common.ajax_post(controller.name, formdata)
                        .then(function(result) { 
                            img.attr("src", "static/images/ui/tick.gif");
                            img.attr("title", _("Include this image when publishing"));
                        });
                }
            });

            $(".media-edit-link")
            .click(function() {
                var mid = $(this).attr("data");
                var mrow = "#mrow-" + mid + " ";
                var comments = $(mrow + " .asm-thumbnail").attr("title");
                $("#editcomments").val(comments);
                $("#mediaid").val(mid);
                $("#dialog-edit").dialog("open");
                return false; // prevents # href
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

        sync: function() {

            if (controller.newmedia) { media.new_media(); }

            // Check if we have pictures but no preferred set and choose one if we don't
            media.check_preferred_images();
        },

        destroy: function() {
            common.widget_destroy("#dialog-email");
            common.widget_destroy("#dialog-emailpdf");
            common.widget_destroy("#dialog-emailsign");
            common.widget_destroy("#dialog-add");
            common.widget_destroy("#dialog-addlink");
            common.widget_destroy("#dialog-edit");
            common.widget_destroy("#dialog-sign");
            common.widget_destroy("#emailnote", "richtextarea");
            common.widget_destroy("#emailpdfnote", "richtextarea");
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
