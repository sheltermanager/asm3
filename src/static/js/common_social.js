/*jslint browser: true, forin: true, eqeq: true, plusplus: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, alert, asm, console, FB, jQuery */
/*global social: true */

(function($) {

    social = {

        facebook_access_token: null,
        facebook_loaded: false,

        /** Log in to facebook. Handles loading the SDK. Other Facebook
         *  methods call this, so it should not need to be called directly.
         * callback: method to fire after login
         * scope: additional facebook permissions required (string, eg: "manage_pages")
         */
        facebook_login: function(callback, scope) {
            var dologin = function() {
                FB.getLoginStatus(function(response) {
                    if (response.status !== 'connected') {
                        FB.login(function(response) {
                            social.facebook_access_token = FB.getAuthResponse().accessToken;
                            if (callback) { callback(response); }
                        }, scope);
                    }
                    else {
                        social.facebook_access_token = FB.getAuthResponse().accessToken;
                        if (callback) { callback(response); }
                    }
                });
            };
            if (social.facebook_loaded) {
                dologin();
                return;
            }
            $.getScript('//connect.facebook.net/en_US/sdk.js', function(){
                social.facebook_loaded = true;
                FB.init({
                    appId: asm.facebookappid,
                    version: 'v2.3' 
                });     
                dologin();
            });
        },

        /**
         * Returns a list of available facebook pages the user can post to
         * callback: method to fire after login
         */
        facebook_get_pages: function(callback) {
            social.facebook_login(function() {
                FB.api('/me/accounts', function(response) {
                    if (callback) { callback(response.data); }
                });
            }, {scope: "manage_pages" });
        },

        /**
         * Posts a photo to Facebook
         * pageid: The page id to post to
         * access_token: An access token allowing posting to the page
         * image_url: A URL to the image to send
         * message: The message to include with the image
         * callback: method to fire on completion.
         */
        facebook_post_photo: function(pageid, access_token, image_url, message, callback) {
            var apiurl = "/me/photos?access_token=" + access_token;
            if (pageid) {
                apiurl = "/" + pageid + "/photos?access_token=" + access_token;
            }
            social.facebook_login(function() {
                FB.api(apiurl, 'post', { url: image_url, message: message, access_token: access_token }, function(response) {
                    if (!response || response.error) {
                        alert('Facebook error occured: ' + JSON.stringify(response.error));
                    } else {
                        if (callback) { callback(); }
                    }
                });
            }, {scope: "manage_pages,publish_actions,publish_stream" });
        }

    };

} (jQuery));

