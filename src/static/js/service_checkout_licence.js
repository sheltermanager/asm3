/*global $, controller, */

// This file is called by the service handler for the "licence checkout" functionality

$(document).ready(function() {

    "use strict";

    const show_dlg = function(title, body) {
        $("#validation-title").html(title);
        $("#validation-text").html(body);
        $("#validation-dlg").modal("show");
    };

    let h = [
        '<div class="modal fade" id="validation-dlg" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="validation-title" aria-hidden="true">',
            '<div class="modal-dialog">',
                '<div class="modal-content">',
                    '<div class="modal-header">',
                        '<h5 class="modal-title" id="validation-title">Error</h5>',
                        '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>',
                    '</div>',
                    '<div id="validation-text" class="modal-body">',
                    '</div>',
                    '<div class="modal-footer">',
                        '<button type="button" class="btn btn-primary" data-bs-dismiss="modal">' + _("Close") + '</button>',
                    '</div>',
                '</div>',
            '</div>',
        '</div>',

        '<div id="pane-review" class="container text-center">',
        '<h2 class="mt-3">' + _("Review") + ' (1/3)</h2>',
        '<div class="mb-3">',
            '<img src="service?account=' + controller.database + '&method=animal_image&animalid=' + controller.row.ANIMALID + 
                '" style="width: 100%; max-width: 300px" />',
        '</div>',
        '<div class="form-group">',
        '<h3>' + controller.row.ANIMALNAME + '</h3>',
        '<p>' + controller.row.SEX + ' ' + controller.row.SPECIESNAME + ' ' + controller.row.ANIMALAGE + '</p>',
        '<p>' + _("License Fee") + ': <b>' + controller.formatfee + '</b></p>',
        '</div>',
        '<div>',
            '<button id="btn-renew" type="button" class="btn btn-primary">',
                _("Renew"),
                '<i class="bi-arrow-right-circle"></i>',
            '</button>',
        '</div>',
        '</div>',

        '<div id="pane-loading" class="container text-center" style="display: none">',
        '<h1 class="mt-5">' + _("Loading...") + '</h1>',
        '<div id="spinner" class="spinner-border spinner-border-lg"></div>',
        '</div>'

    ].join("\n");

    $("body").html(h);

    $("#btn-renew").click(function() {
        let formdata = {
            "account":      controller.database,
            "method":       "checkout_licence",
            "token":        controller.token,
            "newfee":       controller.newfee,
            "action":       "post"
        };
        $(".container").hide();
        $("#pane-loading").show();
        $.ajax({
            type: "POST",
            url: "service",
            data: formdata,
            dataType: "text",
            mimeType: "textPlain",
            success: function(response) {
                // response is a URL to redirect to the payment processor
                window.location = response;
            },
            error: function(jqxhr, textstatus, response) {
                $(".container").hide();
                $("#pane-review").show();
                show_dlg("Error", response);
            }
        });

    });

});

