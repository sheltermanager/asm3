/*global $, controller, history, FileReader */

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
                '<a id="link-back" href="#" class="list-group-item list-group-item-action">',
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
            '<button id="button-sound" class="btn btn-success mt-1" type="button" disabled="disabled">',
                '<i class="bi-play-circle"></i> ' + _("Play") + '</button>',
            '</div>',
            '<h2 class="mt-3">' + _("3. Capture Photo") + '</h2>',
            '<div>',
                '<button id="button-take" class="btn btn-primary" disabled="disabled" type="button">',
                    '<i class="bi-camera"></i> ' + _("Take Photo") + '</button>',
                '<button id="button-gallery" class="btn btn-secondary" disabled="disabled" type="button">',
                    '<i class="bi-card-image"></i> ' + _("Select from Gallery") + '</button>',
            '</div>',
            '<div>',
                '<img id="thumbnail" style="display: none; height: 200px; margin-top: 10px; margin-left: auto; margin-right: auto;" />',
                '<p id="spinner" style="text-align: center; margin-top: 10px; display: none"><span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span> <span id="spinner-message"></span></p>',
                '<input id="take-camera" type="file" capture="environment" accept="image/*" style="display: none" />',
                '<input id="take-gallery" type="file" accept="image/*" style="display: none" />',
            '</div>',
        '</form>',
        '</div>'
    ].join("\n");

    $("body").html(h);

    /** Handles processing the file and uploading to the backend */
    const upload_image = function(file) {
        let reader = new FileReader();
        reader.addEventListener("load", function() {
            $("#thumbnail").prop("src", reader.result);
            $("#thumbnail").show();
        }, false);
        reader.readAsDataURL(file);
    };

    $.each(controller.animals, function(i, v) {
        $("#animal").append('<option value="' + v.ID + '">' + v.SHELTERCODE + ' - ' + v.ANIMALNAME + '</option>');
    });

    $("#animal").change(function() {
        $("#button-take, #button-gallery").prop("disabled", $("#animal").val() == "");
    });

    $("#sound").change(function() {
        $("#button-sound").prop("disabled", $("#sound").val() == "");
    });

    $("#button-sound").click(function() {
        if (!$("#sound").val()) { return; }
        new Audio("static/audio/" + $("#sound").val()).play();
    });

    $("#link-back").click(function() {
        history.go(-1);
    });

    $("#button-take").click(function() {
        $("#take-camera").click();
    });

    $("#button-gallery").click(function() {
        $("#take-gallery").click();
    });

    $("#take-camera").change(function() {
        upload_image($("#take-camera")[0].files[0]);
    });

    $("#take-gallery").change(function() {
        upload_image($("#take-gallery")[0].files[0]);
    });

});


