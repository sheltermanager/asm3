/*global $, controller */

// This file is called by the service handler for the "sign by email" functionality

$(document).ready(function() {

    "use strict";

    const show_dlg = function(title, body) {
        $("#errortitle").html(title);
        $("#errortext").html(body);
        $("#errordlg").modal("show");
    };

    let h = [
        '<div class="modal fade" id="errordlg" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="errortitle" aria-hidden="true">',
            '<div class="modal-dialog">',
                '<div class="modal-content">',
                    '<div class="modal-header">',
                        '<h5 class="modal-title" id="errortitle">Error</h5>',
                        '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>',
                    '</div>',
                    '<div id="errortext" class="modal-body">',
                    '</div>',
                    '<div class="modal-footer">',
                        '<button type="button" class="btn btn-primary" data-bs-dismiss="modal">' + _("Close") + '</button>',
                    '</div>',
                '</div>',
            '</div>',
        '</div>',
        '<div class="container">',
        '<h2>' + _("Signing") + ': ' + controller.notes + '</h2>',
        '<div class="accordion" id="accordion-paperwork">',
            '<div class="accordion-item">',
                '<h2 class="accordion-header" id="header-paperwork">',
                '<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-paperwork" aria-expanded="true" aria-controls="collapse-paperwork">',
                _("View"),
                '</button>',
                '</h2>',
                '<div id="collapse-paperwork" class="accordion-collapse collapse" aria-labelledby="heading-paperwork" data-bs-parent="#accordion-paperwork">',
                    '<div class="accordion-body">',
                    controller.content,
                    '</div>',
                '</div>',
            '</div>',
        '</div>',
        '<div id="signature" style="max-height: 300px; max-width: 800px; width: 95vw; height: 70vh; border: 1px solid #aaa;"></div>',
        '<div class="mb-3">',
            '<small class="text-muted">' + _("Once signed, this document cannot be edited or tampered with.") + '</small>',
        '</div>',
        '<div class="form-group">',
        '<label for="sendsigned" class="form-label">',
            '<input type="checkbox" id="sendsigned" checked="checked" />',
            _("Email me a signed copy of the document at {0}").replace("{0}", controller.email),
        '</label>',
        '</div>',
        '<div id="buttons">',
            '<button id="sig-sign" type="button" class="btn btn-primary">',
                '<i class="bi-vector-pen"></i>',
                _("Sign"),
                '<div id="spinner" class="spinner-border spinner-border-sm" style="display: none"></div>',
            '</button>',
        '</div>',
        '</div>'
    ].join("\n");

    $("body").html(h);

    $("#signature").asmsignature({ guideline: true, bootstrapsupport: true });

    $("#sig-sign").click(function() {
        let formdata = {
            "account":      controller.account,
            "method":       "sign_document",
            "formid":       controller.id, 
            //"sig":          encodeURIComponent($("#signature").asmsignature("value")),
            "email":        controller.email,
            "sendsigned":   $("#sendsigned").is(":checked") ? "on" : ""
        };

        formdata += "&sig=" + encodeURIComponent($("#signature").asmsignature("value"));

        /*if ($("#signature").asmsignature("isEmpty")) {
            show_dlg("Error", _("Signature is required"));
            return;
        }*/

        $("#sig-sign").prop("disabled", true);
        $("#spinner").show();

        $.ajax({
            type: "POST",
            url: "service",
            data: formdata,
            dataType: "text",
            mimeType: "textPlain",
            success: function(response) {
                $("#sig-sign").hide();
                show_dlg(_("Thank you"), _("Thank you, the document is now signed."));
            },
            error: function(jqxhr, textstatus, response) {
                $("#spinner").hide();
                $("#sig-sign").prop("disabled", false);
                show_dlg("Error", response);
            }
        });
    });

    $("#reviewlink").click(function() {
        $("#reviewlink").fadeOut();
        $("#review").slideDown();
    });

    if (controller.signed) {
        show_dlg(_("Already Signed"), _("Sorry, this document has already been signed"));
        $("#sig-sign").hide();
    }

});

