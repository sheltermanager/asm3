/*global $, controller */

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
        '<div id="waiting-container" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("Waiting for documents...") + '</h2>',
            '<div>',
                '<button id="sig-refresh" type="button" class="btn btn-primary">',
                    '<i class="bi-arrow-clockwise"></i>',
                    _("Reload"),
                '</button>',
                '<button id="sig-home" type="button" class="btn btn-secondary">',
                    '<i class="bi-house"></i>',
                    _("Home"),
                '</button>',
                '<button id="sig-logout" type="button" class="btn btn-secondary">',
                    '<i class="bi-door-closed"></i>',
                    _("Logout"),
                '</button>',
            '</div>',
        '</div>',
        '<div id="signing-container" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("Signing") + ': ' + controller.names + '</h2>',
            '<div class="accordion" id="accordion-paperwork">',
                '<div class="accordion-item">',
                    '<h2 class="accordion-header" id="header-paperwork">',
                    '<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-paperwork" aria-expanded="true" aria-controls="collapse-paperwork">',
                    _("View"),
                    '</button>',
                    '</h2>',
                    '<div id="collapse-paperwork" class="accordion-collapse collapse" aria-labelledby="heading-paperwork" data-bs-parent="#accordion-paperwork">',
                        '<div class="accordion-body">',
                        controller.preview,
                        '</div>',
                    '</div>',
                '</div>',
            '</div>',
            '<div id="signature" style="max-height: 300px; max-width: 800px; width: 95vw; height: 70vh; border: 1px solid #aaa;"></div>',
            '<div class="mb-3">',
                '<small class="text-muted">' + _("Once signed, this document cannot be edited or tampered with.") + '</small>',
            '</div>',
            '<div>',
                '<button id="sig-sign" type="button" class="btn btn-primary">',
                    '<i class="bi-vector-pen"></i>',
                    _("Sign"),
                    '<div id="spinner" class="spinner-border spinner-border-sm" style="display: none"></div>',
                '</button>',
                '<button id="sig-clear" type="button" class="btn btn-secondary">',
                    '<i class="bi-x"></i>',
                    _("Clear") + '</button>',
            '</div>',
        '</div>'
    ].join("\n");

    $("body").html(h);

    setTimeout(function() {
        $("#signature").signature({ guideline: true });
    }, 200);

    $("#sig-clear").click(function() {
        $("#signature").signature("clear");
    });

    $("#sig-sign").click(function() {
        let formdata = {
            "ids":          controller.ids, 
            "sig":          $("#signature canvas").get(0).toDataURL("image/png"),
            "signdate":     moment().format("YYYY-MM-DD HH:mm:ss")
        };

        if ($("#signature").signature("isEmpty")) {
            show_dlg("Error", _("Signature is required"));
            return;
        }

        $("#sig-sign").prop("disabled", true);
        $("#spinner").show();

        $.ajax({
            type: "POST",
            url: "mobile_sign",
            data: formdata,
            dataType: "text",
            mimeType: "textPlain",
            success: function(response) {
                location.reload();
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

    if (controller.mobileapp) { $("#sig-logout").hide(); }

    $("#waiting-container").toggle(controller.count == 0);
    $("#signing-container").toggle(controller.count != 0);

    $("#sig-home").click(function() {
        window.location = "mobile";
    });

    $("#sig-refresh").click(function() {
        location.reload();
    });

    $("#sig-logout").click(function() {
        window.location = "mobile_logout";
    });

});


