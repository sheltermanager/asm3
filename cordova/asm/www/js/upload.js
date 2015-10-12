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
   
    var show_loading = function(msg) {
        $("#spinner").show();
        $("#button-take, #button-gallery").prop("disabled", true);
        if (msg) {
            $("#spinner-message").html(msg);
        }
    };

    var hide_loading = function() {
        $("#spinner").hide();
        $("#button-take, #button-gallery").prop("disabled", false);
        $("#spinner-message").html("");
    };

    var load_animals = function() {
        var url = SHELTER_ANIMALS_URL
            .replace("{m}", "jsonp_shelter_animals")
            .replace("{a}", account)
            .replace("{u}", username)
            .replace("{p}", password)
            .replace("{s}", server);
        show_loading("retreiving animals...");
        $.getJSON(url, 
            function(animals) {
                var h = [];
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
            });
    };

    var success = function() {
        hide_loading();
        $("#thumbnail").hide();
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

    $("#button-take").click(function() {
        navigator.camera.getPicture(onPhotoURISuccess, fail_selection, { 
            quality: 30, 
            destinationType: navigator.camera.DestinationType.FILE_URI,
            sourceType: navigator.camera.PictureSourceType.CAMERA
        });
    });

    $("#button-gallery").click(function() {
        navigator.camera.getPicture(onPhotoURISuccess, fail_selection, { 
            quality: 30, 
            destinationType: navigator.camera.DestinationType.FILE_URI,
            sourceType: navigator.camera.PictureSourceType.PHOTOLIBRARY
        });
    });

    load_animals();

});
