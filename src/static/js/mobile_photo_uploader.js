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
                '<select id="location" class="form-select mb-1">',
                    '<option value="">' + _("Filter by location") + '</option>',
                '</select>',
                '<select id="animal" class="form-select mb-1">',
                    '<option value="">' + _("Select an animal") + '</option>',
                '</select>',
            '</div>',
            '<h2 class="mt-3">' + _("2. Woofsqueak!") + '</h2>',
            '<div class="d-grid gap-2 d-md-block">',
            '<select id="sound" class="form-select">',
                '<option value="">Select a sound</option>',
                '<option value="squeakytoy.mp3">Squeaky Toy</option>',
                '<option value="squeakytoy2.mp3">Squeaky Toy 2</option>',
                '<option value="catflap.mp3">Cat Flap</option>',
                '<option value="doorbell.mp3">Door Bell</option>',
                '<option value="letterbox.mp3">Letterbox</option>',
                '<option value="oink.mp3">Oink!</option>',
                '<option value="woofwoof.mp3">Woof Woof!</option>',
            '</select>',
            '<button id="button-sound" class="btn btn-success btn-xs-block mt-1" type="button" disabled="disabled">',
                '<i class="bi-play-circle"></i> ' + _("Play") + '</button>',
            '</div>',
            '<h2 class="mt-3">' + _("3. Capture Photo") + '</h2>',
            '<div class="d-grid gap-2 d-md-block">',
                '<button id="button-take" class="btn btn-primary mt-1" disabled="disabled" type="button">',
                    '<i class="bi-camera"></i> ' + _("Take Photo") + '</button>',
                '<button id="button-paperwork" class="btn btn-success mt-1" disabled="disabled" type="button">',
                    '<i class="bi-file-earmark-richtext"></i> ' + _("Scan Paperwork as PDF") + '</button>',
                '<button id="button-gallery" class="btn btn-secondary mt-1" disabled="disabled" type="button">',
                    '<i class="bi-card-image"></i> ' + _("Select from Gallery") + '</button>',
                '<div id="spinner" class="spinner-border" role="status" style="display: none"><span class="visually-hidden">Loading...</span></div>',
            '</div>',
            '<div>',
                '<img id="thumbnail" style="display: none; height: 200px; margin-top: 10px; margin-left: auto; margin-right: auto;" />',
                '<i id="check" style="display: none" class="bi-check2-circle"></i>',
                '<input id="take-camera" type="file" capture="environment" accept="image/*" style="display: none" />',
                '<input id="take-gallery" type="file" accept="image/*" style="display: none" />',
                '<input id="take-paperwork" type="file" capture="environment" accept="image/*" style="display: none" />',
            '</div>',
        '</form>',
        '</div>'
    ].join("\n");

    $("body").html(h);

    /** Handles processing the file and uploading to the backend */
    const upload_image = function(file, uploadtype) {
        let reader = new FileReader();
        reader.addEventListener("load", function() {
            $("#thumbnail").prop("src", reader.result);
            $("#thumbnail").show();
            $("#check").hide();
            $("#spinner").show();
            let formdata = "animalid=" + $("#animal").val() + "&type=" + uploadtype + "&filename=" + encodeURIComponent(file.name) + "&filedata=" + encodeURIComponent(reader.result);
            $.ajax({
                method: "POST",
                url: "mobile_photo_upload",
                data: formdata,
                dataType: "text/plain",
                error: function() {
                    $("#spinner").hide();
                    $("#check").show();
                },
                success: function() {
                    $("#spinner").hide();
                    $("#check").show();
                    $("input[type='file']").val(""); // clear down file inputs so the same file can be chosen again if the user wants
                }
            });
        }, false);
        reader.readAsDataURL(file);
    };

    let distlocs = [];
    $.each(controller.animals, function(i, v) {
        if (distlocs.indexOf(v.DISPLAYLOCATION) == -1) {
            distlocs.push(v.DISPLAYLOCATION);
        }
    });
    $.each(distlocs.sort(), function(i, v) {
        $("#location").append('<option>' + v + '</option>');
    });

    const filter_animals_by_location = function() {
        $("#animal").empty();
        $("#animal").append('<option value="">' + _("Select an animal") + '</option>');
        $.each(controller.animals, function(i, v) {
            if (!$("#location").val() || v.DISPLAYLOCATION == $("#location").val()) {
                $("#animal").append('<option value="' + v.ID + '">' + v.SHELTERCODE + ' - ' + v.ANIMALNAME + '</option>');
            }
        });
        $("#animal").change();
    };

    $("#animal, #location").change(function() {
        $("#button-take, #button-gallery, #button-paperwork").prop("disabled", $("#animal").val() == "");
    });

    $("#location").change(filter_animals_by_location);
    filter_animals_by_location();

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

    $("#button-paperwork").click(function() {
        $("#take-paperwork").click();
    });

    $("#take-camera").change(function() {
        upload_image($("#take-camera")[0].files[0], "camera");
    });

    $("#take-gallery").change(function() {
        upload_image($("#take-gallery")[0].files[0], "gallery");
    });

    $("#take-paperwork").change(function() {
        upload_image($("#take-paperwork")[0].files[0], "paperwork");
    });

});


