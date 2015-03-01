$(function() {
    
    var JSONP_URL = "https://sheltermanager.com/asm/service?method={0}&account={1}&username={2}&password={3}&callback=?";
    var UPLOAD_URL = "http://sheltermanager.com/asm/service";

    refresh_animals = function() {
        $.mobile.loadingMessage = "Loading...";
        $.mobile.showPageLoadingMsg();
        $.getJSON(JSONP_URL
            .replace("{0}", "jsonp_shelter_animals")
            .replace("{1}", $("#database").val())
            .replace("{2}", $("#username").val())
            .replace("{3}", $("#password").val()), 
        function(animals) {
            $.mobile.changePage("#photo");
            for (ai in animals) {
                var a = animals[ai];
                var hasimage = "";
                if (a.WEBSITEMEDIANAME == "null") {
                    hasimage = " (no image)";
                }
                $("#animal").append("<option value='" + a.ID + "'>" + 
                    a.SHELTERCODE + " - " + 
                    a.ANIMALNAME + hasimage + "</option>");
            }
            $("#animal").selectmenu("refresh");
            $.mobile.hidePageLoadingMsg();
        });
    };


    $("#loginbutton").click(function() {
        $("#loginbutton").button("disable");
        refresh_animals();
    });

    success = function() {
        $.mobile.hidePageLoadingMsg();
        $("#thumbnail").hide();
    };

    fail = function(message) {
        $.mobile.hidePageLoadingMsg();
        alert("Failed uploading image to sheltermanager.com");
    };

    onPhotoURISuccess = function(imageURI) {
        var img = $("#thumbnail")[0];
        img.style.display = 'block';
        img.src = imageURI;

        $.mobile.loadingMessage = "Uploading image...";
        $.mobile.showPageLoadingMsg();

        var options = new FileUploadOptions();
        options.fileKey = "filechooser";
        options.fileName = "image.jpg";
        options.mimeType = "image/jpeg";
        options.chunkedMode = false;
     
        var params = new Object();
        params.method = "upload_animal_image";
        params.account = $("#database").val();
        params.username = $("#username").val();
        params.password = $("#password").val();
        params.animalid = $("#animal").val();
        options.params = params;
     
        var ft = new FileTransfer();
        ft.upload(imageURI, UPLOAD_URL, success, fail, options);
    };

    $("#take").click(function() {
        navigator.camera.getPicture(onPhotoURISuccess, fail, { 
            quality: 30, 
            destinationType: navigator.camera.DestinationType.FILE_URI,
            sourceType: navigator.camera.PictureSourceType.CAMERA
        });
    });

    $("#gallery").click(function() {
        navigator.camera.getPicture(onPhotoURISuccess, fail, { 
            quality: 30, 
            destinationType: navigator.camera.DestinationType.FILE_URI,
            sourceType: navigator.camera.PictureSourceType.PHOTOLIBRARY
        });
    });

});
