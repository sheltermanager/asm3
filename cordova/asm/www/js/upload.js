/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, alert, device, Media */
/*global FileTransfer, FileUploadOptions */

document.addEventListener("deviceready", function() {

    var account = window.localStorage.getItem("asm_account"),
        username = window.localStorage.getItem("asm_username"),
        password = window.localStorage.getItem("asm_password"),
        server = window.localStorage.getItem("asm_server"),
        lastsound = window.localStorage.getItem("asm_lastsound"),
        SHELTER_ANIMALS_URL = "https://{s}.sheltermanager.com/service?method={m}&account={a}&username={u}&password={p}&callback=?",
        UPLOAD_URL = "https://{s}.sheltermanager.com/service";

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

    var sort_single = function(fieldname) {
        /* Sorts a list of dictionaries by fieldname.
         * Use a - prefix in front of fieldname to sort
         * descending. */
        var sortOrder = 1;
        if (fieldname[0] === "-") {
            sortOrder = -1;
            fieldname = fieldname.substr(1);
        }
        return function (a,b) {
            var ca = String(a[fieldname]).toUpperCase();
            var cb = String(b[fieldname]).toUpperCase();
            var result = (ca < cb) ? -1 : (ca > cb) ? 1 : 0;
            return result * sortOrder;
        };
    };
 
    var enable_buttons = function(enable) {
        $("#button-take, #button-gallery").prop("disabled", !enable);
    };
  
    var show_loading = function(msg) {
        $("#spinner").show();
        enable_buttons(false);
        if (msg) {
            $("#spinner-message").html(msg);
        }
    };

    var hide_loading = function() {
        $("#spinner").hide();
        enable_buttons(true);
        $("#spinner-message").html("");
    };

    var load_animals = function() {
        var url = SHELTER_ANIMALS_URL
            .replace("{m}", "jsonp_shelter_animals")
            .replace("{a}", account)
            .replace("{u}", username)
            .replace("{p}", password)
            .replace("{s}", server);
        show_loading("loading animals...");
        $.getJSON(url, 
            function(animals) {
                var h = [ '<option value="" selected="selected">Select an animal</option>' ];
                animals.sort(sort_single("ANIMALNAME"));
                $.each(animals, function(i, a) {
                    var hasimage = "";
                    if (!a.WEBSITEMEDIANAME) {
                        hasimage = " (no image)";
                    }
                    h.push("<option value='" + a.ID + "'>" + 
                        a.ANIMALNAME + " - " + a.SHELTERCODE + 
                        hasimage + "</option>");
                });
                $("#animal").html(h.join("\n"));
                hide_loading();
                enable_buttons(false);
            });
    };

    var success = function() {
        hide_loading();
        $("#thumbnail").hide();
        alert("Photo successfully uploaded");
    };

    var fail_selection = function(message) {
        hide_loading();
    };

    var fail_upload = function(message) {
        hide_loading();
        alert("Failed uploading image to sheltermanager.com");
    };

    var onPhotoURISuccess = function(imageURI) {
 
        show_loading("uploading photo...");
       
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
        ft.upload(imageURI, UPLOAD_URL.replace("{s}", server), success, fail_upload, options);
    };

    $("#animal").change(function() {
        enable_buttons($("#animal").val() != "");
    });

    $("#button-take").click(function() {
        if (!$("#animal").val()) { return; }
        navigator.camera.getPicture(onPhotoURISuccess, fail_selection, { 
            quality: 30, 
            destinationType: navigator.camera.DestinationType.FILE_URI,
            sourceType: navigator.camera.PictureSourceType.CAMERA
        });
    });

    $("#button-gallery").click(function() {
        if (!$("#animal").val()) { return; }
        navigator.camera.getPicture(onPhotoURISuccess, fail_selection, { 
            quality: 30, 
            destinationType: navigator.camera.DestinationType.FILE_URI,
            sourceType: navigator.camera.PictureSourceType.PHOTOLIBRARY
        });
    });

    $("#button-logout").click(function() {
        if (navigator.app) {
            navigator.app.backHistory();
        }
        else {
            history.go(-1);
        }
    });

    $("#button-sound").click(function() {
        if ($("#sound").val() == "") { return; }
        window.localStorage.setItem("asm_lastsound", $("#sound").val());
        var url = "audio/" + $("#sound").val();
        if (device.platform == "Android") { url = "/android_asset/www/" + url; } // Android needs extra path prefix
        var media = new Media(url, null, function(e) { alert("Error playing media: " + e); });
        media.play();
    });

    load_animals();
    $("#sound").val(window.localStorage.getItem("asm_lastsound"));

});
