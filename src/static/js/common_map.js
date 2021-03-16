/*global $, google, asm, config, validate, L */
/*global mapping: true */

"use strict";

/**
 * Module to provide map drawing/plotting.
 * Supports leaflet and google so far.
 */
const mapping = {

    /**
     * Draws a map using our selected provider.
     * divid: The element to draw the map in
     * zoom: The zoom level for the map 1-18
     * latlong: A lat,long string to mark the center of the map (or empty string for current location)
     * markers: A list of marker objects to draw { latlong: "", popuptext: "", popupactive: false }
     */
    draw_map: function(divid, zoom, latlong, markers) {
        var _draw_map = function(latlong) {
            if (asm.mapprovider == "osm") {
                mapping._leaflet_draw_map(divid, zoom, latlong, markers);
            }
            else if (asm.mapprovider == "google") {
                mapping._google_draw_map(divid, zoom, latlong, markers);
            }
        };
        var first_valid = this._first_valid_latlong(markers);
        // A center point has been specified, use that
        if (latlong != "") {
            _draw_map(latlong);
        }
        // No center point specified, use the device location
        else if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        // We got a position from the browser
                        _draw_map(position.coords.latitude + "," + position.coords.longitude);
                    },
                    function() {
                        // The user refused or an error occurred - use the first marker pin
                        if (first_valid) { _draw_map(first_valid); }
                    }
                );
        }
        else if (first_valid) {
            // Geolocation is not supported - use the first marker pin
            _draw_map(first_valid);
        }
    },

    /** Loads a script inline and calls onload on complete.
     *  We use this instead of jQuery.getScript because this method
     *  does not trigger CSP and require 'unsafe-inline'
     */
    _get_script: function(url, onload) {
        let s= document.createElement("script");
        s.onload = onload;
        s.onerror = function() { console.log('onerror', arguments); };
        s.src = url;
        document.head.appendChild(s);
    },

    /**
     * Returns the first valid latlong value from the list of markers
     */
    _first_valid_latlong: function(markers) {
        var fv;
        $.each(markers, function(i, v) {
            if (v.latlong) {
                fv = v.latlong;
                return false;
            }
        });
        return fv;
    },

    _leaflet_draw_map: function(divid, zoom, latlong, markers) {
        $("head").append('<link rel="stylesheet" href="' + asm.leafletcss + '" />');
        mapping._get_script(asm.leafletjs, function() {
            var ll = latlong.split(",");
            var map = L.map(divid).setView([ll[0], ll[1]], 15);
            L.Icon.Default.imagePath = asm.leafletjs.substring(0, asm.leafletjs.lastIndexOf("/")) + "/images/";
            L.tileLayer(asm.osmmaptiles, {
                attribution: '<a target="_blank" href="http://osm.org/copyright">&copy; OpenStreetMap contributors</a> | ' + 
                    '<a target="_blank" href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a> | ' + 
                    '<a target="_blank" href="https://www.openstreetmap.org/fixthemap">Improve this map</a>'
            }).addTo(map);
            L.control.scale().addTo(map);
            $.each(markers, function(i, v) {
                if (!v.latlong || v.latlong.indexOf("0,0") == 0) { return; }
                ll = v.latlong.split(",");
                var marker = L.marker([ll[0], ll[1]]).addTo(map);
                if (v.popuptext) { marker.bindPopup(v.popuptext); }
                if (v.popupactive) { marker.openPopup(); }
            });
            if (config.bool("ShowLatLong")) {
                map.on("contextmenu", function (event) {
                    if ($(".asm-latlong").length == 0) { return; }
                    var marker = L.marker(event.latlng).addTo(map);
                    $(".latlong-lat").val(event.latlng.lat);
                    $(".latlong-long").val(event.latlng.lng);
                    $(".asm-latlong").latlong("save");
                    marker.bindPopup(event.latlng.lat + ", " + event.latlng.lng);
                    marker.openPopup();
                    validate.dirty(true);
                });
            }
        });
    },

    google_loaded: false,

    _google_draw_map: function(divid, zoom, latlong, markers, latsel, longsel) {
        window._goomapcallback = function() {
            var ll = latlong.split(",");
            var mapOptions = {
                zoom: zoom,
                center: new google.maps.LatLng(parseFloat(ll[0]), parseFloat(ll[1]))
            };
            var map = new google.maps.Map(document.getElementById(divid), mapOptions);
            $.each(markers, function(i, v) {
                if (!v.latlong || v.latlong.indexOf("0,0") == 0) { return; }
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
            if (config.bool("ShowLatLong")) {
                google.maps.event.addListener(map, 'click', function(event) {
                    if ($(".asm-latlong").length == 0) { return; }
                    var marker = new google.maps.Marker({
                        position: event.latLng,
                        map: map
                    });
                    $(".latlong-lat").val(event.latLng.lat());
                    $(".latlong-long").val(event.latLng.lng());
                    $(".asm-latlong").latlong("save");
                    var infowindow = new google.maps.InfoWindow({ content: event.latLng.lat() + ", " + event.latLng.lng() }); 
                    google.maps.event.addListener(marker, 'click', function() {
                        infowindow.open(map, marker);
                    });
                    validate.dirty(true);
                });
            }
        };
        var key = "";
        if (asm.mapproviderkey) {
            key = "&key=" + asm.mapproviderkey;
        }
        if (mapping.google_loaded) {
            window._goomapcallback();
        }
        else {
            mapping._get_script("//maps.google.com/maps/api/js?v=3.x&sensor=false&async=2{key}&callback=_goomapcallback".replace("{key}", key), function() { mapping.google_loaded = true; });
        }
    }

};
