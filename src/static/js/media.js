/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */
/*global escape, FileReader */

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

                '<div id="dialog-email" style="display: none" title="' + html.title(_("Email media"))  + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="emailto">' + _("To") + '</label></td>',
                '<td><input id="emailto" type="text" class="asm-doubletextbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="emailnote">' + _("Message") + '</label></td>',
                '<td><textarea id="emailnote" class="asm-textarea" rows="5"></textarea></td>',
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
                '<td><textarea id="emailpdfnote" class="asm-textarea" rows="5"></textarea></td>',
                '</tr>',
                '</table>',
                '</div>',

                '<div id="tipios6" class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                _("You will need to upgrade to iOS 6 or higher to upload files."),
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
                '<td><textarea id="addcomments" name="comments" rows="10" title=',
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
                '<form id="addlinkform" method="post" action="' + controller.name + '">',
                '<input type="hidden" name="mode" value="createlink" />',
                '<input type="hidden" id="linkid" name="linkid" value="' + controller.linkid + '" />',
                '<input type="hidden" id="linktypeid" name="linktypeid" value="' + controller.linktypeid + '" />',
                '<input type="hidden" id="controller" name="controller" value="' + controller.name + '" />',
                '<table width="100%">',
                '<tr>',
                '<td><label for="linktype">' + _("Type") + '</label></td>',
                '<td><select id="linktype" name="linktype" class="asm-selectbox">',
                '<option value="1">' + _("Document Link") + '</option>',
                '<option value="2">' + _("Video Link") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="linktarget">' + _("URL") + '</label></td>',
                '<td><input id="linktarget" name="linktarget" class="asm-textbox" /></td>',
                '</tr>',
                '<tr id="commentsrow">',
                '<td><label for="linkcomments">' + _("Notes") + '</label>',
                '</td>',
                '<td><textarea id="linkcomments" name="comments" rows="10" class="asm-textarea"></textarea>',
                '</td>',
                '</tr>',
                '</table>',
                '</form>',
                '</div>',

                '<div id="dialog-edit" style="display: none" title="' + _("Edit media notes") + '">',
                '<form id="editform" method="post" action="' + controller.name + '">',
                '<input type="hidden" name="linkid" value="' + controller.linkid + '" />',
                '<input type="hidden" name="mode" value="update" />',
                '<input type="hidden" id="mediaid" name="mediaid" value="" />',
                '<textarea id="editcomments" name="comments" rows="10" class="asm-textarea"></textarea>',
                '</form>',
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
                { id: "sign", text: _("Sign"), icon: "signature", tooltip: _("Electronically sign this document") },
                { id: "signpad", text: _("Signing Pad"), icon: "mobile", tooltip: _("Electronically sign this document with the signing pad mobile interface") },
                { id: "rotateanti", icon: "rotate-anti", tooltip: _("Rotate image 90 degrees anticlockwise") },
                { id: "rotateclock", icon: "rotate-clock", tooltip: _("Rotate image 90 degrees clockwise") },
                { id: "web", icon: "web", tooltip: _("Make this the default image when viewing this record and publishing to the web") },
                { id: "doc", icon: "document", tooltip: _("Make this the default image when creating documents") },
                { id: "video", icon: "video", tooltip: _("Make this the default video link when publishing to the web") }
            ]));

            h.push("<div id='asm-mediacontainer'>");
            h.push(media.render_table());
            h.push("</div>");
            h.push(html.content_footer());
            return h.join("\n");
        },

        render_table: function() {

            var h = [];
            h.push('<table id="asm-mediaicons">');
            h.push('<tr>');

            var col = 0;
            $.each(controller.media, function(i, m) {
                h.push('<td id="mrow-' + m.ID + '" data="' + m.ID + '" align="center" width="100px" valign="top" style="border: 1px solid #aaa; padding: 5px">');
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
                        if (m.MEDIANAME.indexOf("youtube.com") != -1) {
                            linkimage = media.youtube_thumbnail(m.MEDIANAME);
                            if (!linkimage) {
                                linkimage = "static/images/ui/file-video.png";
                            }
                        }
                    }
                    h.push('<img class="asm-thumbnail thumbnailshadow" src="' + linkimage + '" height="70px" ');
                    h.push('title="' + html.title(fullnotes) + '" /></a>');
                    h.push('<br />');
                    h.push('<a class="viewlink" title="' + _('View media') + '" href="media?id=' + m.ID + '">' + shortnotes + '</a>');
                    h.push('</a>');
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
                    h.push('</a>');
                }
                else if (media.is_extension(m.MEDIANAME, "pdf")) {
                    h.push('<a href="media?id=' + m.ID + '">');
                    h.push('<img class="asm-thumbnail thumbnailshadow" src="static/images/ui/pdf-media.png" height="70px" ');
                    h.push('title="' + html.title(fullnotes) + '" /></a>');
                    h.push('<br />');
                    h.push('<a class="viewlink" title="' + _('View PDF') + '" href="media?id=' + m.ID + '">' + shortnotes + '</a>');
                    h.push('</a>');
                }
                else {
                    h.push('<a href="media?id=' + m.ID + '">');
                    h.push('<img class="asm-thumbnail thumbnailshadow" src="static/images/ui/file-media.png" height="70px" ');
                    h.push('title="' + html.title(fullnotes) + '" /></a>');
                    h.push('<br />');
                    h.push('<a class="viewlink" title="' + _('View media') + '" href="media?id=' + m.ID + '">' + shortnotes + '</a>');
                    h.push('</a>');
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
                if (m.WEBSITEPHOTO == 1 && controller.showPreferred) {
                    h.push(html.icon("web", _("Default image for this record and the web")));
                }
                if (m.WEBSITEVIDEO == 1 && controller.showPreferred) {
                    h.push(html.icon("video", _("Default video for publishing")));
                }
                if (m.DOCPHOTO == 1 && controller.showPreferred) {
                    h.push(html.icon("document", _("Default image for documents")));
                }
                if (media.is_extension(m.MEDIANAME, "jpg") && m.WEBSITEPHOTO == 0 && !m.EXCLUDEFROMPUBLISH && controller.name == "animal_media") {
                    h.push('<img class="incexc" data="' + m.ID + '" src="static/images/ui/tick.gif" title="' + _('Include this image when publishing') + '" />');
                }
                if (media.is_extension(m.MEDIANAME, "jpg") && m.WEBSITEPHOTO == 0 && m.EXCLUDEFROMPUBLISH && controller.name == "animal_media") {
                    h.push('<img class="incexc" data="' + m.ID + '" src="static/images/ui/cross.gif" title="' + _('Exclude this image when publishing') + '" />');
                }
                h.push('</span>');
                h.push('</td>');
                col += 1;
                if (col == 6) {
                    col = 0;
                    h.push('</tr><tr>');
                }
            });

            h.push('</tr>');
            h.push('</table>');
            return h.join("\n");
        },


        // Posts the image back to the server. If HTML5 File APIs are available,
        // uses a Canvas to scale the image first.
        post: function() {
            
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

            // If we don't support the HTML5 File APIs, fall back gracefully
            if (!window.File && !window.FileReader && !window.FileList && !window.Blob) {
                $("#addform").submit();
                return;
            }

            // FileReader isn't supported in Safari below version 6.0, but
            // the FileReader object/type does exist in Safari 5, so it 
            // only fails when you try to instantiate one.
            try { var safaritest = new FileReader(); }
            catch(ex) {
                $("#addform").submit();
                return;
            }

            // Grab the selected file
            var selectedfile = $("#filechooser")[0].files[0];

            // If an image isn't selected, do the normal post
            if (!selectedfile.type.match('image.*')) {
                $("#addform").submit();
                return;
            }

            // If the config option is on to disable HTML5 
            // client side scaling, do the normal post instead
            if (config.bool("DontUseHTML5Scaling")) {
                $("#addform").submit();
                return;
            }

            // Figure out the size we're scaling to
            var media_scaling = config.str("IncomingMediaScaling");
            if (media_scaling == "") { media_scaling = "320x200"; }
            var max_width = parseInt(media_scaling.substring(0, media_scaling.indexOf("x")), 10);
            var max_height = parseInt(media_scaling.substring(media_scaling.indexOf("x") + 1), 10);

            // Read the file to an image tag, then render it to
            // an HTML5 canvas to scale it
            var img = document.createElement("img");
            var reader = new FileReader();
            reader.onload = function(e) { img.src = e.target.result; };
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
                ctx.drawImage(this, 0, 0, img_width, img_height);
                var finalfile = canvas.toDataURL("image/jpeg");

                // Post the scaled image via AJAX
                var formdata = "linkid=" + controller.linkid + "&linktypeid= " + 
                    controller.linktypeid + "&comments=" + encodeURIComponent($("#addcomments").val()) +
                    "&base64image=" + encodeURIComponent(finalfile);
                common.ajax_post(controller.name, formdata, function(result) { window.location = controller.name + "?id=" + controller.linkid; });
            };
            reader.readAsDataURL(selectedfile);
        },

        is_extension: function(s, ext) {
            return s.toLowerCase().indexOf("." + ext) != -1;
        },

        /**
         * Turns a YouTube watch URL into the default thumbnail source
         * s: A youtube URL www.youtube.com/watch?v=ID
         */
        youtube_thumbnail: function(s) {
            var eqpos = s.lastIndexOf("="),
                yid = "";
            if (eqpos != -1) {
                yid = s.substring(eqpos+1);
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
            common.ajax_post(controller.name, formdata, function() { 
                window.location = controller.name + "?id=" + controller.linkid;
            });
        },

        bind: function() {

            $(".asm-tabbar").asmtabs();
            $("#signature").signature({ guideline: true });
            $("#tipattach").show();
            $("#tipios6").hide();

            // If this is an idevice and the file upload box is
            // disabled, it needs upgrading to iOS6 or better.
            if (common.is_idevice() && $("#filechooser").attr("disabled")) {
                $("#tipattach").hide();
                $("#tipios6").show();
            }

            $("#asm-mediaicons input").change(function() {
                if ($("#asm-mediaicons input:checked").size() > 0) {
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
                $("#button-sign").button("option", "disabled", true); 
                $("#button-signpad").button("option", "disabled", true); 

                // Only allow the image preferred buttons to be pressed if the
                // selection size is one and the selection is an image
                if ($("#asm-mediaicons input:checked").size() == 1) {
                    $("#asm-mediaicons input:checked").each(function() {
                        var mname = $(this).parent().parent().find(".media-name").val();
                        if (media.is_extension(mname, "jpg") || media.is_extension(mname, "jpeg")) {
                            $("#button-web").button("option", "disabled", false); 
                            $("#button-doc").button("option", "disabled", false); 
                        }
                    });
                }

                // Only allow the video preferred button to be pressed if the
                // selection size is one and the selection is a video link
                if ($("#asm-mediaicons input:checked").size() == 1) {
                    $("#asm-mediaicons input:checked").each(function() {
                        var mtype = $(this).parent().parent().find(".media-type").val();
                        if (mtype == 2) {
                            $("#button-video").button("option", "disabled", false);
                        }
                    });
                }

                // Only allow the rotate buttons to be pressed if the
                // selection only contains images
                $("#asm-mediaicons input:checked").each(function() {
                    var mname = $(this).parent().parent().find(".media-name").val();
                    if (media.is_extension(mname, "jpg") || media.is_extension(mname, "jpeg")) {
                        $("#button-rotateanti").button("option", "disabled", false); 
                        $("#button-rotateclock").button("option", "disabled", false); 
                    }
                });

                // Only allow the email button to be pressed if we have a selection 
                if ($("#asm-mediaicons input:checked").size() > 0) {
                    $("#button-email").button("option", "disabled", false); 
                }

                // Only allow the email pdf button to be pressed if the
                // selection only contains documents
                $("#asm-mediaicons input:checked").each(function() {
                    var mname = $(this).parent().parent().find(".media-name").val();
                    if (media.is_extension(mname, "html")) {
                        $("#button-emailpdf").button("option", "disabled", false); 
                    }
                });

                // Only allow the sign buttons to be pressed if the
                // selection only contains unsigned documents
                $("#asm-mediaicons input:checked").each(function() {
                    var mname = $(this).parent().parent().find(".media-name").val();
                    var issigned = $(this).parent().find(".asm-icon-signature").length > 0;
                    if (media.is_extension(mname, "html") && !issigned ) {
                        $("#button-sign").button("option", "disabled", false); 
                        $("#button-signpad").button("option", "disabled", false); 
                    }
                });


            });

            var emailbuttons = { };
            emailbuttons[_("Send")] = function() {
                if (!validate.notblank([ "emailto" ])) { return; }
                var formdata = "mode=email&email=" + encodeURIComponent($("#emailto").val()) + 
                    "&emailnote=" + encodeURIComponent($("#emailnote").val()) + 
                    "&ids=" + $("#asm-mediaicons input").tableCheckedData();
                $("#dialog-email").dialog("close");
                common.ajax_post(controller.name, formdata, function(result) { 
                    header.show_info(_("Email successfully sent to {0}").replace("{0}", result));
                });
            };
            emailbuttons[_("Cancel")] = function() {
                $("#dialog-email").dialog("close");
            };

            $("#dialog-email").dialog({
                autoOpen: false,
                width: 550,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: emailbuttons
            });

            var emailpdfbuttons = { };
            emailpdfbuttons[_("Send")] = function() {
                if (!validate.notblank([ "emailpdfto" ])) { return; }
                var formdata = "mode=emailpdf&email=" + encodeURIComponent($("#emailpdfto").val()) + 
                    "&emailnote=" + encodeURIComponent($("#emailpdfnote").val()) + 
                    "&ids=" + $("#asm-mediaicons input").tableCheckedData();
                $("#dialog-emailpdf").dialog("close");
                common.ajax_post(controller.name, formdata, function(result) { 
                    header.show_info(_("Email successfully sent to {0}").replace("{0}", result));
                });
            };
            emailpdfbuttons[_("Cancel")] = function() {
                $("#dialog-emailpdf").dialog("close");
            };

            $("#dialog-emailpdf").dialog({
                autoOpen: false,
                width: 550,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: emailpdfbuttons
            });

            var addbuttons = { };
            addbuttons[_("Attach")] = media.post;
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
                $("#addlinkform").submit();
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
                common.ajax_post(controller.name, formdata, function(result) { 
                    $("#mrow-" + mediaid + " .asm-thumbnail").attr("title", html.title($("#editcomments").val()));
                    $("#mrow-" + mediaid + " .viewlink").text(html.truncate($("#editcomments").val(), 70));
                    $("#dialog-edit").dialog("close");
                    $("#dialog-edit").enable_dialog_buttons();
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
                var formdata = "mode=sign&ids=" + $("#asm-mediaicons input").tableCheckedData();
                formdata += "&signdate=" + encodeURIComponent(format.date(new Date()) + " " + format.time(new Date()));
                formdata += "&sig=" + encodeURIComponent(img);
                media.ajax(formdata);
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
                    var formdata = "mode=delete&ids=" + $("#asm-mediaicons input").tableCheckedData();
                    $("#dialog-delete").disable_dialog_buttons();
                    media.ajax(formdata);
                });
            });

            // If we aren't including preferred, hide the buttons
            if (!controller.showPreferred) {
                $("#button-web").hide();
                $("#button-doc").hide();
                $("#button-video").hide();
            }

            $("#button-web").button({disabled: true}).click(function() {
                $("#button-web").button("disable");
                var formdata = "mode=web&ids=" + $("#asm-mediaicons input").tableCheckedData();
                media.ajax(formdata);
            });

            $("#button-video").button({disabled: true}).click(function() {
                $("#button-video").button("disable");
                var formdata = "mode=video&ids=" + $("#asm-mediaicons input").tableCheckedData();
                media.ajax(formdata);
            });

            $("#button-email").button({disabled: true}).click(function() {
                // If we have a person, default the email address
                if (controller.person) {
                    $("#emailto").val(controller.person.EMAILADDRESS);
                }
                $("#dialog-email").dialog("open");
            });

            $("#button-emailpdf").button({disabled: true}).click(function() {
                // If we have a person, default the email address
                if (controller.person) {
                    $("#emailto").val(controller.person.EMAILADDRESS);
                }
                $("#dialog-emailpdf").dialog("open");
            });

            $("#button-sign").button({disabled: true}).click(function() {
                $("#dialog-sign").dialog("open");
            });

            $("#button-signpad").button({disabled: true}).click(function() {
                var formdata = "mode=signpad&ids=" + $("#asm-mediaicons input").tableCheckedData();
                common.ajax_post(controller.name, formdata, function(result) {
                    header.show_info(_("Sent to mobile signing pad."));
                });
            });

            $("#button-rotateanti").button({disabled: true}).click(function() {
                $("#button-rotateanti").button("disable");
                var formdata = "mode=rotateanti&ids=" + $("#asm-mediaicons input").tableCheckedData();
                media.ajax(formdata);
            });

            $("#button-rotateclock").button({disabled: true}).click(function() {
                $("#button-rotateclock").button("disable");
                var formdata = "mode=rotateclock&ids=" + $("#asm-mediaicons input").tableCheckedData();
                media.ajax(formdata);
            });


            $("#button-doc").button({disabled: true}).click(function() {
                $("#button-doc").button("disable");
                var formdata = "mode=doc&ids=" + $("#asm-mediaicons input").tableCheckedData();
                media.ajax(formdata);
            });

            $(".incexc").css("cursor", "pointer").click(function() {
                var img = $(this), formdata = "";
                if (img.attr("src").indexOf("tick") != -1) {
                    // Exclude
                    formdata = "mode=exclude&mediaid=" + img.attr("data") + "&exclude=1";
                    common.ajax_post(controller.name, formdata, function(result) { 
                        img.attr("src", "static/images/ui/cross.gif");
                        img.attr("title", _("Exclude this image when publishing"));
                    });
                }
                else {
                    // Include
                    formdata = "mode=exclude&mediaid=" + img.attr("data") + "&exclude=0";
                    common.ajax_post(controller.name, formdata, function(result) { 
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
                0: controller.animal.ACID, 1: controller.animal.INCIDENTNAME, 2: format.date(controller.animal.INCIDENTDATETIME)});
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
            "animal_media": function() { common.module_loadandstart("media", "animal_media?id=" + this.qs.id); },
            "foundanimal_media": function() { common.module_loadandstart("media", "foundanimal_media?id=" + this.qs.id); },
            "incident_media": function() { common.module_loadandstart("media", "incident_media?id=" + this.qs.id); },
            "lostanimal_media": function() { common.module_loadandstart("media", "lostanimal_media?id=" + this.qs.id); },
            "person_media": function() { common.module_loadandstart("media", "person_media?id=" + this.qs.id); },
            "waitinglist_media": function() { common.module_loadandstart("media", "waitinglist_media?id=" + this.qs.id); }
        }


    };

    common.module_register(media);

});
