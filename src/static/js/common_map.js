/*jslint browser: true, forin: true, eqeq: true, plusplus: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, google, asm, config, L */
/*global google_loaded: true, geo: true, mapping: true */

(function($) {

    google_loaded = false;

    /**
     * Module to perform geocoding.
     * Supports mapquest, nominatim and google so far.
     */
    geo = {

        /**
         * Get a geocode lat/long for an address.
         * Returns a promise that will resolve with the lat/long value.
         */
        get_lat_long: function(address, town, city, postcode) {
            var deferred = $.Deferred();
            var callback = function(lat, lng) {
                if ($.isNumeric(lat) && $.isNumeric(lng)) { 
                    deferred.resolve(lat, lng); 
                }
                else { 
                    deferred.reject(); 
                }
            };
            if (asm.geoprovider == "nominatim") {
                this._nominatim_get_lat_long(address, town, city, postcode, callback);
            }
            else if (asm.geoprovider == "smcom") {
                this._smcom_get_lat_long(address, town, city, postcode, callback);
            }
            else if (asm.geoprovider == "google") {
                this._google_get_lat_long(address, town, city, postcode, callback);
            }
            else if (asm.geoprovider == "mapquest") {
                this._mapquest_get_lat_long(address, town, city, postcode, callback);
            }
            return deferred.promise();
        },

        /** Returns true if we should only be calculating geocodes from the postcode */
        _only_use_postcode: function() {
            return config.bool("GeocodeWithPostcodeOnly") || asm.locale == "en_GB";
        },

        /** Gets the lat/long position for an address from google */
        _google_get_lat_long: function(address, town, city, postcode, callback) {
            var add = address.replace("\n", ",") + ", " + town  + ", " + city + ", " + postcode;
            if (this._only_use_postcode()) { add = postcode; }
            window._googeocallback = function() {
                var geocoder = new google.maps.Geocoder();
                geocoder.geocode( { 'address': add }, function(results, status) {
                    if (status == google.maps.GeocoderStatus.OK) {
                        callback(results[0].geometry.location.lat(), results[0].geometry.location.lng());
                    }
                    else {
                        callback(0, 0);
                    }
                });
            };
            var key = "";
            if (asm.geoproviderkey) {
                key = "&key=" + asm.geoproviderkey;
            }
            if (google_loaded) {
                window._googeocallback();
            }
            else {
                $.getScript("//maps.google.com/maps/api/js?v=3.x&sensor=false&async=2{key}&callback=_googeocallback".replace("{key}", key), function() { google_loaded = true; });
            }
        },

        /** Gets the lat/long position for an address from nominatim */
        _nominatim_get_lat_long: function(address, town, city, postcode, callback) {
            var add = encodeURIComponent(address.replace("\n", ",") + "," + town).replace(/ /g, "+");
            if (this._only_use_postcode()) { add = postcode.replace(/ /g, "+"); }
            $.getJSON("http://nominatim.openstreetmap.org/search?format=json&q=" + add + "&json_callback=?", function(data) {
                if (!data || !data[0] || !data[0].lat) {
                    callback(0, 0);
                }
                else {
                    callback(data[0].lat, data[0].lon);
                }
            });
        },

        /** Gets the lat/long position for an address from sheltermanager.com */
        _smcom_get_lat_long: function(address, town, city, postcode, callback) {
            var add = encodeURIComponent(address.replace("\n", ",") + "," + town).replace(/ /g, "+");
            if (this._only_use_postcode()) { add = postcode.replace(/ /g, "+"); }
            var url = "/geocode?format=json&q=" + add;
            $.ajax({
                type: "GET",
                dataType: "json",
                mimeType: "text/json",
                url: url,
                success: function(data) {
                    callback(data[0].lat, data[0].lon);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    callback(0, 0);
                }
            });
        },

        /** Gets the lat/long position for an address from mapquest */
        _mapquest_get_lat_long: function(address, town, city, postcode, callback) {
            var add = (address.replace("\n", ",") + "," + town + "," + city + "," + postcode).replace(/'/g, '');
            if (this._only_use_postcode()) { add = postcode; }
            var url = "http://www.mapquestapi.com/geocoding/v1/address?";
            if (asm.geoproviderkey) {
                url += "key=" + asm.geoproviderkey + "&";
            }
            url += "outFormat=json&inFormat=json&json=";
            url += encodeURIComponent("{location: '" + add + "',options:{maxResults:1}}");
            $.ajax({
                type: "POST",
                dataType: "json",
                mimeType: "text/json",
                url: url,
                success: function(response) {
                    if (response.results[0]) {
                        var ll = response.results[0].locations[0].latLng;
                        if (ll && ll.lat) {
                            callback(ll.lat, ll.lng);
                            return;
                        }
                    }
                    return callback(0, 0);
                }
            });
        },

        /** Returns a hash of an address */
        address_hash: function(address, town, city, postcode) {
            var addrhash = String(address + town + city + postcode);
            addrhash = addrhash.replace(/ /g, '').replace(/,/g, '').replace(/\n/g, '');
            if (addrhash.length > 220) { addrhash = addrhash.substring(0, 220); }
            return addrhash;
        }

    };

    /**
     * Module to provide map drawing/plotting.
     * Supports leaflet and google so far.
     */
    mapping = {

        /**
         * Draws a map using our selected provider.
         * divid: The element to draw the map in
         * zoom: The zoom level for the map 1-18
         * latlong: A lat,long string to mark the center of the map
         * markers: A list of marker objects to draw { latlong: "", popuptext: "", popupactive: false }
         */
        draw_map: function(divid, zoom, latlong, markers) {
            if (asm.mapprovider == "osm") {
                this._leaflet_draw_map(divid, zoom, latlong, markers);
            }
            else if (asm.mapprovider == "google") {
                this._google_draw_map(divid, zoom, latlong, markers);
            }
        },

        _leaflet_draw_map: function(divid, zoom, latlong, markers) {
            $("head").append('<link rel="stylesheet" href="' + asm.leafletcss + '" />');
            $.getScript(asm.leafletjs, function() {
                var ll = latlong.split(",");
                var map = L.map(divid).setView([ll[0], ll[1]], 15);
                L.Icon.Default.imagePath = asm.leafletjs.substring(0, asm.leafletjs.lastIndexOf("/")) + "/images";
                L.tileLayer(asm.osmmaptiles, {
                    attribution: '&copy; <a target="_blank" href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                }).addTo(map);
                L.control.scale().addTo(map);
                $.each(markers, function(i, v) {
                    if (!v || v.indexOf("0,0") == 0) { return; }
                    ll = v.latlong.split(",");
                    var marker = L.marker([ll[0], ll[1]]).addTo(map);
                    if (v.popuptext) { marker.bindPopup(v.popuptext); }
                    if (v.popupactive) { marker.openPopup(); }
                });
            });
        },

        _google_draw_map: function(divid, zoom, latlong, markers) {
            window._goomapcallback = function() {
                var ll = latlong.split(",");
                var mapOptions = {
                    zoom: zoom,
                    center: new google.maps.LatLng(parseFloat(ll[0]), parseFloat(ll[1]))
                };
                var map = new google.maps.Map(document.getElementById(divid), mapOptions);
                $.each(markers, function(i, v) {
                    if (!v || v.indexOf("0,0") == 0) { return; }
                    ll = v.latlong.split(",");
                    var marker = new google.maps.Marker({
                        position: new google.maps.LatLng(parseFloat(ll[0]), parseFloat(ll[1])),
                        map: map
                    });
                    var infowindow;
                    if (v.popuptext) { 
                        infowindow = new google.maps.InfoWindow({ content: v.popuptext }); 
                        google.maps.event.addListener(marker, 'click', function() {
                            infowindow.open(map, marker);
                        });
                    }
                    if (v.popupactive) { 
                        if (infowindow) { infowindow.open(map, marker); }
                    }
                });
            };
            var key = "";
            if (asm.geoproviderkey) {
                key = "&key=" + asm.geoproviderkey;
            }
            if (google_loaded) {
                window._goomapcallback();
            }
            else {
                $.getScript("//maps.google.com/maps/api/js?v=3.x&sensor=false&async=2{key}&callback=_goomapcallback".replace("{key}", key), function() { google_loaded = true; });
            }
        }

    };

} (jQuery));
