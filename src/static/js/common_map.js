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
    _markers: [],
    draw_map: async function(divid, zoom, latlong, markers) {
        var _draw_map = async function(latlong) {
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
        // No https connection - assuming test environment, providing fallback location
        else if (!document.location.href.startsWith("https://")) {
            _draw_map("0,0");
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

    redraw_markers: function(markers) {
        if (asm.mapprovider == "osm") {
            $.each(mapping._markers, function(i, v) {
                mapping.map.removeLayer(v);
            });
            mapping._markers = [];
            $.each(markers, function(i, v) {
                    if (!v.latlong || v.latlong.indexOf("0,0") == 0) { return; }
                    let ll = v.latlong.split(",");
                    let markerIcon = L.icon({
                        iconUrl: v.PINURL,
                        shadowUrl: 'static/images/mapping/marker-shadow.png',
                        iconSize:     [50, 82], // size of the icon
                        shadowSize:   [100, 164], // size of the shadow
                        iconAnchor:   [25, 80], // point of the icon which will correspond to marker's location
                        shadowAnchor: [30, 164], // the same for the shadow
                        popupAnchor:  [0, -82]  // point from which the popup should open relative to the iconAnchor
                    });
                    let marker = L.marker([ll[0], ll[1]], {icon: markerIcon}).addTo(mapping.map).bindPopup(v.POPUPTEXT);
                    mapping._markers.push(marker);
            });
            if (markers.length) {
                let group = L.featureGroup(mapping._markers);
                mapping.map.fitBounds(group.getBounds());
            }
        } else if (asm.mapprovider == "google") {
            $.each(mapping._markers, function(i, v) {
                v.setMap(null);
            });
            mapping._markers = [];
            let latlngbounds = new google.maps.LatLngBounds();
            $.each(markers, function(i, v) {
                if (!v.latlong || v.latlong.indexOf("0,0") == 0) { return; }
                let ll = v.latlong.split(",");
                let gll = new google.maps.LatLng(parseFloat(ll[0]), parseFloat(ll[1]));
                var marker = new google.maps.Marker({
                    position: gll,
                    map: mapping.map,
                    icon: v.PINURL
                });
                latlngbounds.extend(gll);
                mapping._markers.push(marker);
                var infowindow;
                if (v.POPUPTEXT) { 
                    infowindow = new google.maps.InfoWindow({ content: v.POPUPTEXT }); 
                    google.maps.event.addListener(marker, 'click', function() {
                        infowindow.open(mapping.map, marker);
                    });
                }
                if (v.popupactive) { 
                    if (infowindow) { infowindow.open(mapping.map, marker); }
                }
            });
            if (markers.length) {
                mapping.map.fitBounds(latlngbounds);
            }
        }
    },

    /** Loads a script inline and calls onload on complete.
     *  We use this instead of jQuery.getScript because this method
     *  does not trigger CSP and require 'unsafe-inline'
     */
    _get_script: function(url, onload) {
        let s= document.createElement("script");
        s.onload = onload;
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

    _leaflet_draw_map: async function(divid, zoom, latlong, markers) {
        $("head").append('<link rel="stylesheet" href="' + asm.leafletcss + '" />');
        mapping._get_script(asm.leafletjs, function() {
            var ll = latlong.split(",");
            mapping.map = L.map(divid).setView([ll[0], ll[1]], 15);
            L.Icon.Default.imagePath = asm.leafletjs.substring(0, asm.leafletjs.lastIndexOf("/")) + "/images/";
            L.tileLayer(asm.osmmaptiles, {
                referrerPolicy: 'strict-origin-when-cross-origin', // causes referer header to be sent to osm
                attribution: '<a target="_blank" href="http://osm.org/copyright">&copy; OpenStreetMap contributors</a> | ' + 
                    '<a target="_blank" href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a> | ' + 
                    '<a target="_blank" href="https://www.openstreetmap.org/fixthemap">Improve this map</a>'
            }).addTo(mapping.map);
            L.control.scale().addTo(mapping.map);
            $.each(markers, function(i, v) {
                if (!v.latlong || v.latlong.indexOf("0,0") == 0) { return; }
                ll = v.latlong.split(",");
                var marker = L.marker([ll[0], ll[1]]).addTo(mapping.map);
                mapping._markers.push(marker);
                if (v.popuptext) { marker.bindPopup(v.popuptext); }
                if (v.PINSTYLE) {
                    marker._icon.classList.add(v.PINSTYLE);
                    marker.PINSTYLE = v.PINSTYLE;
                }
                if (v.SPECIESID) { marker.SPECIESID = v.SPECIESID; }
                if (v.popupactive) { marker.openPopup(); }
            });
            if (config.bool("ShowLatLong")) {
                mapping.map.on("contextmenu", function (event) {
                    if ($(".asm-latlong").length == 0) { return; }
                    $.each(mapping._markers, function(i, v) {
                        mapping.map.removeLayer(v);
                    });
                    mapping._markers = [];
                    var marker = L.marker(event.latlng).addTo(mapping.map);
                    mapping._markers.push(marker);
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
            mapping.map = new google.maps.Map(document.getElementById(divid), mapOptions);
            if (config.bool("ShowLatLong")) {
                google.maps.event.addListener(mapping.map, 'click', function(event) {
                    if ($(".asm-latlong").length == 0) { return; }
                    $.each(mapping._markers, function(i, v) {
                        v.setMap(null);
                    });
                    var marker = new google.maps.Marker({
                        position: event.latLng,
                        map: mapping.map
                    });
                    mapping._markers.push(marker);
                    $(".latlong-lat").val(event.latLng.lat());
                    $(".latlong-long").val(event.latLng.lng());
                    $(".asm-latlong").latlong("save");
                    var infowindow = new google.maps.InfoWindow({ content: event.latLng.lat() + ", " + event.latLng.lng() }); 
                    google.maps.event.addListener(marker, 'click', function() {
                        infowindow.open(mapping.map, marker);
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
