/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, alert */
/*global FileTransfer, FileUploadOptions */

document.addEventListener("deviceready", function() {

    var account = window.localStorage.getItem("asm_account"),
        username = window.localStorage.getItem("asm_username"),
        password = window.localStorage.getItem("asm_password"),
        server = window.localStorage.getItem("asm_server"),
        SHELTER_ANIMALS_URL = "https://{s}.sheltermanager.com/service?method={m}&account={a}&username={u}&password={p}&callback=?",
        UPLOAD_URL = "http://{s}.sheltermanager.com/service";

    if (navigator.notification) {
        window.alert = function(message) {
            navigator.notification.alert(
                message,
                null,       // callback
                "ASM",
                'OK'        // button
            );
        };
    }
   
    var show_loading = function() {
        $("#spinner").show();
        $("#button-take, #button-gallery").prop("disabled", true);
    };

    var hide_loading = function() {
        $("#spinner").hide();
        $("#button-take, #button-gallery").prop("disabled", false);
    };

    var load_animals = function() {
        var url = SHELTER_ANIMALS_URL
            .replace("{m}", "jsonp_shelter_animals")
            .replace("{a}", account)
            .replace("{u}", username)
            .replace("{p}", password)
            .replace("{s}", server);
        show_loading();
        $.getJSON(url, 
            function(animals) {
                var h = [];
                $.each(animals, function(i, a) {
                    var hasimage = "";
                    if (a.WEBSITEMEDIANAME == "null") {
                        hasimage = " (no image)";
                    }
                    h.push("<option value='" + a.ID + "'>" + 
                        a.SHELTERCODE + " - " + 
                        a.ANIMALNAME + hasimage + "</option>");
                });
                $("#animal").html(h.join("\n"));
                hide_loading();
            });
    };

    var success = function() {
        hide_loading();
        $("#thumbnail").hide();
    };

    var fail = function(message) {
        hide_loading();
        alert("Failed uploading image to sheltermanager.com");
    };

    var onPhotoURISuccess = function(imageURI) {
 
        show_loading();
       
        var img = $("#thumbnail")[0];
        img.style.display = 'block';
        img.src = imageURI;

        var options = new FileUploadOptions();
        options.fileKey = "filechooser";
        options.fileName = "image.jpg";
        options.mimeType = "image/jpeg";
        options.chunkedMode = false;
        options.params = {
            method: "upload_animal_image",
            account: account,
            username: username,
            password: password,
            animalid: $("#animal").val()
        };
     
        var ft = new FileTransfer();
        ft.upload(imageURI, UPLOAD_URL.replace("{s}", server), success, fail, options);
    };

    $("#button-take").click(function() {
        navigator.camera.getPicture(onPhotoURISuccess, fail, { 
            quality: 30, 
            destinationType: navigator.camera.DestinationType.FILE_URI,
            sourceType: navigator.camera.PictureSourceType.CAMERA
        });
    });

    $("#button-gallery").click(function() {
        navigator.camera.getPicture(onPhotoURISuccess, fail, { 
            quality: 30, 
            destinationType: navigator.camera.DestinationType.FILE_URI,
            sourceType: navigator.camera.PictureSourceType.PHOTOLIBRARY
        });
    });

    load_animals();

});
