/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    "use strict";

    var lostfound_find_results = {
        
        mode: "lost", 

        render: function() {
            var mode = controller.name.indexOf("lost") != -1 ? "lost" : "found";
            this.mode = mode;
            return [
                html.content_header(_("Results")),
                '<div id="asm-results">',
                '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-search"></span>',
                (this.mode == "lost" ? _("Find lost animal returned {0} results.") : 
                    _("Find found animal returned {0} results.")).replace("{0}", controller.rows.length),
                '</p>',
                '</div>',
                '<table id="searchresults">',
                '<thead>',
                '<tr>',
                '<th>' + _("Number") + '</th>',
                '<th>' + _("Contact") + '</th>',
                '<th>' + _("Microchip") + '</th>',
                '<th>' + _("Area") + '</th>',
                '<th>' + _("Zipcode") + '</th>',
                '<th>' + _("Date") + '</th>',
                '<th>' + _("Age Group") + '</th>',
                '<th>' + _("Sex") + '</th>',
                '<th>' + _("Species") + '</th>',
                '<th>' + _("Breed") + '</th>',
                '<th>' + _("Color") + '</th>',
                '<th>' + _("Features") + '</th>',
                '</thead>',
                '<tbody>',
                this.render_results(),
                '</tbody>',
                '</table>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        render_results: function() {
            var h = [];
            $.each(controller.rows, function(i, r) {
                h.push('<tr>');
                if (lostfound_find_results.mode == "lost") {
                    h.push('<td><a href="lostanimal?id=' + r.ID + '">' + format.padleft(r.ID, 6) + '</a></td>');
                }
                else {
                    h.push('<td><a href="foundanimal?id=' + r.ID + '">' + format.padleft(r.ID, 6) + '</a></td>');
                }
                h.push('<td>' + html.person_link(r.OWNERID, r.OWNERNAME) + '</td>');
                h.push('<td>' + common.nulltostr(r.MICROCHIPNUMBER) + '</td>');
                if (lostfound_find_results.mode == "lost") {
                    h.push('<td>' + r.AREALOST + '</td>');
                }
                else {
                    h.push('<td>' + r.AREAFOUND + '</td>');
                }
                h.push('<td>' + r.AREAPOSTCODE + '</td>');
                if (lostfound_find_results.mode == "lost") {
                    h.push('<td>' + format.date(r.DATELOST) + '</td>');
                }
                else {
                    h.push('<td>' + format.date(r.DATEFOUND) + '</td>');
                }
                h.push('<td>' + r.AGEGROUP + '</td>');
                h.push('<td>' + r.SEXNAME + '</td>');
                h.push('<td>' + r.SPECIESNAME + '</td>');
                h.push('<td>' + r.BREEDNAME + '</td>');
                h.push('<td>' + r.BASECOLOURNAME + '</td>');
                h.push('<td>' + r.DISTFEAT + '</td>');
                h.push('</tr>');
            });
            return h.join("\n");
        },

        bind: function() {
            $("#searchresults").table();
            $("#searchresults").trigger("sorton", [[[4, 0]]]); // Sort on date descending (col 4, 0=desc)
        },

        name: "lostfound_find_results",
        animation: "results",
        autofocus: "#asm-content a:first",
        title: function() { return _("Results"); },
        routes: {
            "lostanimal_find_results": function() { common.module_loadandstart("lostfound_find_results", "lostanimal_find_results?" + this.rawqs); },
            "foundanimal_find_results": function() { common.module_loadandstart("lostfound_find_results", "foundanimal_find_results?" + this.rawqs); }
        }

    };

    common.module_register(lostfound_find_results);

});
