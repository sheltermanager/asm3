/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true */
/*global $, baseurl, buildno, onlysavewhendirty, jswindowprint, readonly, tinymce, tinyMCE */

$(function() {
   
    var rw_toolbar = "save pdf print | undo redo | fontselect fontsizeselect | bold italic forecolor backcolor | alignleft aligncenter alignright alignjustify | forecolor backcolor | bullist numlist outdent indent pagebreak | link image";
    var ro_toolbar = "pdf print";

    // Set the containing div and textarea to the vertical 
    // height of the viewport and a suitable printable width
    var h = $(window).height(),
        w = "775";
    $("div").css({
        height: h,
        width: w
    });
    $("#wp").css({
        height: h - 160,
        width: w
    });

    tinymce.init({
        selector: "#wp",
        theme: "modern",
        content_css: "css?v=asm-tinymce.css&k=" + buildno,
        plugins: [
            "advlist autolink lists link image charmap print preview",
            "hr anchor pagebreak searchreplace wordcount visualblocks visualchars code fullscreen",
            "insertdatetime media nonbreaking save table contextmenu directionality",
            "emoticons template paste textcolor save"
            ],
        toolbar1: readonly ? ro_toolbar : rw_toolbar,

        // Disable some items if we're in read only mode
        menubar: !readonly,

        // readonly: readonly, // This takes out too much stuff, we remove contenteditable from iframe instead.

        // enable browser spellchecking and allow saving at any time
        gecko_spellcheck: true,
        browser_spellcheck: true,
        save_enablewhendirty: onlysavewhendirty,

        // stop tinymce stripping data url images
        paste_data_images: true,

        // Necessary for fontsizeselect to work
        convert_fonts_to_spans: true,
        fontsize_formats: "8pt 10pt 11pt 12pt 14pt 16pt 18pt 20pt 22pt 24pt 36pt 72pt",

        setup: function(ed) {

            // Add a PDF button
            ed.addButton("pdf", {
                title: "PDF",
                image: "static/images/icons/pdf.png",
                onclick: function() {
                    $("input[name='savemode']").val("pdf");
                    $("form").submit();
                }
            });

            // Override normal page break behaviour. Note that there's a race condition
            // and the normal plugin command gets registered after this, so we have to
            // put it in a timer so that our command is added last to override everything else.
            setTimeout(function() {
                ed.addCommand("mcePageBreak", function() {
                    tinyMCE.execCommand("mceInsertContent", false, "<div class='mce-pagebreak' style='page-break-before: always; clear: both; border: 0'>&nbsp;</div>");
                });
            }, 1000);

            setTimeout(function() {

                // Start in fullscreen mode
                // ed.execCommand('mceFullScreen');

                // If we're in readonly mode, prevent editing of the content and
                // disable the CTRL+S save shortcut
                if (readonly) {
                    $("iframe").contents().find("body").removeAttr("contenteditable");
                    ed.addShortcut('ctrl+s', '', function () {});
                }

                // Handle saving ourself so we can set the right savemode
                ed.addCommand("mceSave", function() {
                    $("input[name='savemode']").val("save");
                    $("form").submit();
                });

            }, 1000);

            // Mobile devices cannot support TinyMCE's use of sending the content
            // to an iframe and then calling window.print() as they all involve sending
            // the complete page to a service to do the printing.
            // For these devices, we post back to the server, which returns a printable
            // version of the document.
            // The user can also override this with a config option 
            // !jswindowprint (use iframe/window.print)
            var ismobile = (navigator.userAgent.indexOf("ndroid") != -1 ||
                navigator.userAgent.indexOf("iPhone") != -1 ||
                navigator.userAgent.indexOf("iPad") != -1 ||
                navigator.userAgent.indexOf("Kindle") != -1);
            
            if (ismobile || !jswindowprint) {
                setTimeout(function() {
                    ed.addCommand("mcePrint", function() {
                        $("input[name='savemode']").val("print");
                        $("form").submit();
                    });
                }, 1000);
            }

        }
    });

});
