/*global $, jQuery, _, asm, additional, common, config, controller, dlgfx, edit_header, format, geo, header, html, mapping, validate */

$(function() {

    "use strict";

    const lostfound_map = {

        render: function() {
            let headerheight = $("body").outerHeight() + 64;
            let overlayheight = $("body").outerHeight() + 60;
            return [
                html.content_header(_("Lost and Found Animals")),
                '<div id="embeddedmap" style="z-index: 1; width: 100%; height: calc(100vh - ' + headerheight + 'px); color: #000;"></div>',
                '<div id="asm-mapoverlay" style="z-index: 999; position: absolute; top: ' + overlayheight + 'px; right: 25px; background-color: white; padding: 10px; border: 1px solid #aaa;">',
                    _("Species") + " ",
                    tableform.render_select(
                        { post_field: "species", label: _("Species"), justwidget: true, options: '<option value="0">' + _("(all)") + '</option>' + html.list_to_options(controller.species, "ID", "SPECIESNAME") }
                    ),
                    tableform.render_check(
                        { post_field: "lost", label: _("Lost"), justwidget: true }
                    ),
                    tableform.render_check(
                        { post_field: "found", label: _("Found"), justwidget: true }
                    ),
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            $("#species").on("change", function() {
                $.each(mapping.markers, function(i, v) {
                    if (v.PINSTYLE == "asm-lostanimalpin" && !$("#lost").prop("checked")) {
                        mapping.map.removeLayer(v);
                    } else if (v.PINSTYLE == "asm-foundanimalpin" && !$("#found").prop("checked")) {
                        mapping.map.removeLayer(v);
                    } else if ($("#species").val() == 0 || v.SPECIESID == $("#species").val()) {
                        mapping.map.addLayer(v);
                        if (v.PINSTYLE) { v._icon.classList.add(v.PINSTYLE); }
                    } else {
                        mapping.map.removeLayer(v);
                    }
                });
            });
            $("#lost").on("change", function() {
                $("#species").change();
            });
            $("#found").on("change", function() {
                $("#species").change();
            });
        },

        sync: function() {
            $("#lost").prop("checked", true);
            $("#found").prop("checked", true);
        },

        delay: function() {
            let first_valid = "";
            $.each(controller.rows, function(i, v) {
                v.latlong = v.AREALATLONG;
                if (v.LOSTORFOUND == "lost") {
                    v.popuptext = "<b>" + v.AREA + "</b><br /><a target='_blank' href='lostanimal?id=" + v.ID + "'>" + 
                        v.SPECIESNAME + " " + _("lost {0}").replace("{0}", format.date(v.LFDATE)) + "</a>";
                } else {
                    v.popuptext = "<b>" + v.AREA + "</b><br /><a target='_blank' href='foundanimal?id=" + v.ID + "'>" + 
                        v.SPECIESNAME + " " + _("found {0}").replace("{0}", format.date(v.LFDATE)) + "</a>";
                }
                if (v.latlong && v.latlong.indexOf("0,0") == -1) { first_valid = v.latlong; }
            });
            console.log(controller.rows);
            mapping.draw_map("embeddedmap", 10, first_valid, controller.rows);
        },

        name: "lostfound_map",
        animation: "results",
        title: function() { return _("Lost and Found Animals"); },
        routes: {
            "lostfound_map": function() { common.module_loadandstart("lostfound_map", "lostfound_map"); }
        }

    };

    common.module_register(lostfound_map);

});

