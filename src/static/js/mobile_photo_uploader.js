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
        '<div id="upload-container" class="container">',
        '<form class="form-upload">',
            '<div class="list-group mt-3">', 
                '<a id="back" href="#" class="list-group-item list-group-item-action">',
                '&#8592; ' + _("Back"),
                '</a>',
            '</div>',
            '<h2 class="mt-3">' + _("1. Choose Animal") + '</h2>',
            '<div>',
                '<select id="animal" class="form-control">',
                    '<option value="">Select an animal</option>',
                '</select>',
            '</div>',
            '<h2 class="mt-3">' + _("2. Woofsqueak!") + '</h2>',
            '<div>',
            '<select id="sound" class="form-control">',
                '<option value="">Select a sound</option>',
                '<option value="squeakytoy.mp3">Squeaky Toy</option>',
                '<option value="squeakytoy2.mp3">Squeaky Toy 2</option>',
                '<option value="catflap.mp3">Cat Flap</option>',
                '<option value="doorbell.mp3">Door Bell</option>',
                '<option value="letterbox.mp3">Letterbox</option>',
                '<option value="oink.mp3">Oink!</option>',
                '<option value="woofwoof.mp3">Woof Woof!</option>',
            '</select>',
            '<button id="button-sound" class="btn btn-secondary mt-1" type="button">',
                '<i class="bi-play-circle"></i> ' + _("Play") + '</button>',
            '</div>',
            '<h2 class="mt-3">' + _("3. Capture Photo") + '</h2>',
            '<div>',
                '<button id="button-take" class="btn btn-primary" type="button">',
                    '<i class="bi-camera"></i> ' + _("Take Photo") + '</button>',
                '<button id="button-gallery" class="btn btn-secondary" type="button">',
                    '<i class="bi-card-image"></i> ' + _("Select from Gallery") + '</button>',
                '<img id="thumbnail" style="display: none; height: 200px; margin-top: 10px; margin-left: auto; margin-right: auto;" />',
                '<p id="spinner" style="text-align: center; margin-top: 10px; display: none"><span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span> <span id="spinner-message"></span></p>',
            '</div>',
        '</form>',
        '</div>'
    ].join("\n");

    $("body").html(h);

    $("#back").click(function() {
        window.location = "mobile";
    });

});


