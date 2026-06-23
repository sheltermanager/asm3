/*global $, jQuery, _, asm, additional, common, config, controller, dlgfx, edit_header, format, geo, header, html, mapping, validate */

$(function() {

    "use strict";

    const mapview = {

        update_markers_from_checkboxes: async function() {
            if (asm.mapprovider == "osm") {
                let leafletloaded = await mapview._check_leaflet_loaded();
                if (leafletloaded) {
                    mapview._update_markers_from_checkboxes();
                } else {
                    window.setTimeout(async function() {
                        leafletloaded = await mapview._check_leaflet_loaded();
                        if (leafletloaded) {
                            mapview._update_markers_from_checkboxes();
                        } else {
                            mapview.update_markers_from_checkboxes();
                        }
                    }, 500);
                }
            } else if (asm.mapprovider == "google") {
                let googlemapsloaded = await mapview._check_googlemaps_loaded();
                if (googlemapsloaded) {
                    mapview._update_markers_from_checkboxes();
                } else {
                    window.setTimeout(async function() {
                        googlemapsloaded = await mapview._check_googlemaps_loaded();
                        if (googlemapsloaded) {
                            mapview._update_markers_from_checkboxes();
                        } else {
                            mapview.update_markers_from_checkboxes();
                        }
                    }, 500);
                }
            }
        },

        _update_markers_from_checkboxes: async function() {
            let mk = "";
            $("#toggles input:checked").each(function() {
                mk += $(this).attr("data");
            });
            let floorjsdate = $("#datefloor").datepicker("getDate");
            let rawmarkers = await common.ajax_post("map_markers", "mode=getmarkers&mk=" + mk + "&floor=" + format.date(floorjsdate));
            rawmarkers = jQuery.parseJSON(rawmarkers);
            let markers = [];
            let speciesid = parseInt($("#speciesfilter").val());
            if (rawmarkers.length && speciesid) {
                $.each(rawmarkers, function(i, v) {
                    if (speciesid == v.SPECIESID) {
                        markers.push(v);
                    }
                });
            } else {
                markers = rawmarkers;
            }
            mapping.redraw_markers(markers);
        },

        map_markers: [],

        render: function() {
            const chk = function(id, data, icon, label, tag="") {
                if (tag) {tag = " " + tag;}
                return '<span class="asm-map-legend' + tag + '">' + 
                    html.icon(icon) + 
                    '<input id="' + id + '" data="' + data + '" type="checkbox" class="asm-checkbox" /> ' +
                    '<label for="' + id + '">' + label + '</label>' +
                    '</span> ';
            };
            let headerheight = $("body").outerHeight() + 64;
            let overlayheight = $("body").outerHeight() + 45;
            return [
                html.content_header(_("Map View")),
                '<p id="toggles" class="asm-map-legends centered" style="top: ' + overlayheight + 'px;">',
                    '<span class="asm-map-legend" style="padding: 5px;">', 
                    html.icon("animal"),
                    tableform.render_select(
                        { post_field: "speciesfilter", label: _("Species"), justwidget: true, options: '<option value="0">' + _("(all)") + '</option>' + html.list_to_options(controller.species, "ID", "SPECIESNAME") }
                    ),
                    '<label for="speciesfilter">' + _("Species") + '</label>',
                    '</span>',
                    chk("toggle-lost", "l", "animal-lost", _("Lost")),
                    chk("toggle-found", "f", "animal-found", _("Found")),
                    chk("toggle-activeincident", "a", "call", _("Active Incidents")),
                    chk("toggle-recentincident", "i", "call-complete", _("Recent Incidents")),
                    chk("toggle-nonshelter", "n", "nonshelter", _("Non-Shelter")),
                    chk("toggle-reclaim", "r", "location", _("Reclaims")),
                    '<span class="asm-map-legend" style="padding: 5px;">', 
                    html.icon("diary"),
                    tableform.render_date(
                        { post_field: "datefloor", justwidget: true }
                    ),
                    '<label for="datefloor">' + _("Floor") + '</label>',
                    '</span>',
                '</p>',
                '<div id="embeddedmap" style="z-index: 1; width: 100%; height: calc(100vh - ' + headerheight + 'px); color: #000;"></div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            $("#speciesfilter").change(function() {
                mapview.update_markers_from_checkboxes();
            });
            $("#toggles input").change(function() {
                mapview.update_markers_from_checkboxes();
            });
        },

        sync: function() {
             // If there's an mk parameter, sync our checkboxes
            let mk = common.querystring_param("mk");
            if (mk.includes("a")) {
                mk = mk.replace("i", "");
            }
            if (!mk) { mk = "lfianr"; }
            $("#toggles input").each(function() {
                if (mk.indexOf( $(this).attr("data") ) != -1) {
                    $(this).prop("checked", true);
                }
                else {
                    $(this).prop("checked", false);
                }
            });

            // If there's a species parameter, sync the species select
            let sid = common.querystring_param("sid");
            if (sid) {
                $("#speciesfilter").val(sid);
            }

            // If there's a floor parameter, sync the floor input
            let fl = common.querystring_param("fl");
            if (fl) {
                $("#datefloor").datepicker("setDate", fl);
            } else {
                let datefloor = new Date();
                datefloor.setDate(datefloor.getDate() - 90);
                $("#datefloor").datepicker("setDate", datefloor);
            }
        },

        _check_leaflet_loaded: function() {
            try {
                let leafletlibrary = L;
                return true
            } catch(error) {
                return false
            }
        },

        _check_googlemaps_loaded: function() {
            try {
                let googlelibrary = google;
                return true
            } catch(error) {
                return false
            }
        },

        delay: async function() {
            $("#embeddedmap").html('<img id="adam" src=/static/images/wait/rolling_3a87cd.svg style="margin-left: auto;margin-right: auto;">');
            await mapping.draw_map("embeddedmap", 10, false, []);
            $("#adam").remove();
            mapview.update_markers_from_checkboxes();
        },

        name: "mapview",
        animation: "results",
        title: function() { return _("Map View"); },
        routes: {
            "map_view": function() { common.module_loadandstart("mapview", "map_view?" + this.rawqs); }
        }

    };

    common.module_register(mapview);

});

