/*global $, baseurl, buildno, jswindowprint, onlysavewhendirty, pdfenabled, visualaids, readonly, tinymce, tinyMCE */

$(function() {

    "use strict";
   
    let rw_toolbar = "save pdf print | undo redo | fontselect fontsizeselect | bold italic underline forecolor backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent pagebreak | link image";
    
    // Add the text direction options for RTL languages
    let locale = $("#locale").val();
    if (locale == "ar" || locale == "he") { rw_toolbar += " | ltr rtl"; }

    let ro_toolbar = "pdf print";

    // Set the containing div and textarea to the vertical 
    // height of the viewport and 80% width
    let h = $(window).height(),
        w = Math.floor(($(window).width() / 100.0) * 80.0);
    // max-width is 775px
    if (w > 775) { w = 775; }
    $("div").css({ height: h - 20, width: w });
    $("#wp").css({ height: h - 20, width: w });

    tinymce.init({
        selector: "#wp",
        content_css: "static/css/asm-tinymce.css?k=" + buildno,
        plugins: [
            "advlist autolink directionality lists link image charmap print preview",
            "hr anchor pagebreak searchreplace wordcount visualblocks visualchars code fullscreen",
            "insertdatetime media nonbreaking save table contextmenu directionality",
            "emoticons template paste textcolor save"
            ],
        toolbar1: readonly ? ro_toolbar : rw_toolbar,

        // Disable some items if we're in read only mode
        menubar: !readonly,

        // Whether to show visual aids (dotted line around tables without borders)
        visual: visualaids,

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

        // Available fonts
        font_formats: [ "Andale Mono=andale mono,times",
                      "Arial=arial,helvetica,sans-serif",
                      "Arial Black=arial black,avant garde",
                      "Book Antiqua=book_antiquaregular,palatino",
                      "Calibri=calibri,sans-serif",
                      "Courier New=courier_new,courier",
                      "Lucida Console=lucida_console,courier",
                      "Georgia=georgia,palatino",
                      "Helvetica=helvetica",
                      "Impact=impactregular,chicago",
                      "Myriad Pro Condensed=myriad pro condensed,sans-serif",
                      "Symbol=symbol",
                      "Tahoma=tahoma,arial,helvetica,sans-serif",
                      "Terminal=terminal,monaco",
                      "Times New Roman=times new roman,times",
                      "Trebuchet MS=trebuchet ms,geneva",
                      "Verdana=verdana,geneva",
                      "Webdings=webdings",
                      "Wingdings=wingdings,zapf dingbats" ].join(";"),

        // Allow inline style tags
        valid_children: '+body[style]',

        setup: function(ed) {

            // Add a PDF button
            if (pdfenabled) {
                ed.ui.registry.addIcon("pdf", '<img src="static/images/ui/tinymce-pdf.png" />');
                ed.ui.registry.addButton("pdf", {
                    tooltip: "View this document as a PDF",
                    icon: "pdf",
                    onAction: function() {
                        $("input[name='mode']").val("pdf");
                        $("form").submit();
                    }
                });
            }

            // Override normal page break behaviour. Note that there's a race condition
            // and the normal plugin command gets registered after this, so we have to
            // put it in a timer so that our command is added last to override everything else.
            setTimeout(function() {
                ed.addCommand("mcePageBreak", function() {
                    tinyMCE.execCommand("mceInsertContent", false, "<div class='mce-pagebreak' style='page-break-before: always; clear: both;'>&nbsp;</div>");
                });
            }, 1000);

            // When the tab key is pressed, insert some fixed width spaces
            // instead of tabbing to the next field (which doesn't exist).
            ed.on("keydown", function(evt) {
                if (evt.keyCode == 9){
                    ed.execCommand('mceInsertContent', false, '&emsp;&emsp;');
                    evt.preventDefault();
                    return false;
                }
            });

            setTimeout(function() {

                // Start in fullscreen mode
                // ed.execCommand('mceFullScreen');

                // If we're in readonly mode, prevent editing of the content and
                // disable the CTRL+S save shortcut
                if (readonly) {
                    $("iframe").contents().find("body").removeAttr("contenteditable");
                    ed.addShortcut('ctrl+s', '', function () {});
                }

                // Handle saving ourself so we can set the right mode
                ed.addCommand("mceSave", function() {
                    $("input[name='mode']").val("save");
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
            let ismobile = navigator.userAgent.match(/Android|iPhone|iPad|Kindle/i);
            
            if (ismobile || !jswindowprint) {
                setTimeout(function() {
                    ed.addCommand("mcePrint", function() {
                        $("input[name='mode']").val("print");
                        $("form").submit();
                    });
                }, 1000);
            }

        }
    });

});
