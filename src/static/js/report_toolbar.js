/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    // Do nothing if the toolbar has already been loaded 
    // or if an element with a no-toolbar class exists
    if ($(".asm-report-toolbar").length > 0 || $(".no-toolbar").length > 0) { return; }

    const qs = function() {
        let s = String(window.location);
        return s.substring(s.indexOf("?")+1);
    };

    let h = [
        '<div id="dialog-email" class="no-print" style="display: none">',
        '<label for="email">' + _("Send to") + '</label>',
        '<input id="email" type="text" placeholder="test@example.com" />',
        '</div>',
        '<div class="asm-report-toolbar no-print">',
        '<button id="button-print">' + _("Print") + '</button>',
        '<button id="button-email">' + _("Email") + '</button>',
        '<button id="button-csv">' + _ ("CSV") + '</button>',
        '<button id="button-excel">' + _ ("Excel") + '</button>',
        '<button id="button-pdf-portrait">' + _("PDF (Portrait)") + '</button>',
        '<button id="button-pdf-landscape">' + _("PDF (Landscape") + '</button>',
        '</div>'
    ].join("\n");

    $("body").prepend(h);

    let emailbuttons = {};
    emailbuttons[_("Cancel")] = function() {
        $("#dialog-email").dialog("close");
    };
    emailbuttons[_("Send")] = function() {
        if ($("#email").val().indexOf("@") == -1) { 
            alert(_("Invalid email address '{0}'").replace("{0}", $("#email").val())); 
            return;
        }
        window.location = "report_export_email?" + qs() + "&email=" + $("#email").val();
    };

    $("#dialog-email").dialog({
        autoOpen: false,
        width: 400,
        modal: true,
        dialogClass: "dialogshadow",
        buttons: emailbuttons
    });

    $("#button-print").button({
        icons: { primary: "ui-icon-print" },
        text: true
    }).click(function() {
        window.print();
    });

    $("#button-email").button({
        icons: { primary: "ui-icon-mail-closed" },
        text: true
    }).click(function() {
        $("#dialog-email").dialog("open");
    });

    $("#button-csv").button({
        icons: { primary: "ui-icon-calculator" },
        text: true
    }).click(function() {
        window.location = "report_export_csv?" + qs();
    });

    $("#button-excel").button({
        icons: { primary: "ui-icon-note" },
        text: true
    }).click(function() {
        window.location = "report_export_excel?" + qs();
    });

    $("#button-pdf-portrait").button({
        icons: { primary: "ui-icon-document" },
        text: true
    }).click(function() {
        window.location = "report_export_pdf?" + qs();
    });

    $("#button-pdf-landscape").button({
        icons: { primary: "ui-icon-document" },
        text: true
    }).click(function() {
        window.location = "report_export_pdf?landscape=true&" + qs();
    });

    if (String(window.location).indexOf("sent=1") != -1) { alert(_("Message sent.")); }

});
