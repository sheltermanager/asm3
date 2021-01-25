/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const incident_find_results = {

        render: function() {
            return [
                html.content_header(_("Results")),
                '<div id="asm-results">',
                '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-search"></span>',
                _("Find animal control incidents returned {0} results.").replace("{0}", controller.rows.length),
                '</p>',
                '</div>',
                '<table id="searchresults">',
                '<thead>',
                '<tr>',
                '<th>' + _("Type") + '</th>',
                '<th>' + _("Number") + '</th>',
                '<th>' + _("Incident Date/Time") + '</th>',
                '<th>' + _("Address") + '</th>',
                '<th>' + _("City") + '</th>',
                '<th>' + _("Zipcode") + '</th>',
                '<th>' + _("Jurisdiction") + '</th>',
                '<th>' + _("Location") + '</th>',
                '<th>' + _("Suspect") + '</th>',
                '<th>' + _("Dispatch Date/Time") + '</th>',
                '<th>' + _("Responded Date/Time") + '</th>',
                '<th>' + _("ACO") + '</th>',
                '<th>' + _("Followup") + '</th>',
                '<th>' + _("Completed") + '</th>',
                '<th>' + _("Type") + '</th>',
                '<th>' + _("Notes") + '</th>',
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
            let h = [];
            $.each(controller.rows, function(i, r) {
                h.push('<tr>');
                h.push('<td><a href="incident?id=' + r.ID + '">' + r.INCIDENTNAME + '</a></td>');
                h.push('<td>' + format.padleft(r.ID, 6) + '</td>');
                h.push('<td>' + format.date(r.INCIDENTDATETIME) + ' ' + format.time(r.INCIDENTDATETIME) + '</td>');
                h.push('<td>' + common.nulltostr(r.DISPATCHADDRESS) + '</td>');
                h.push('<td>' + common.nulltostr(r.DISPATCHTOWN) + '</td>');
                h.push('<td>' + common.nulltostr(r.DISPATCHPOSTCODE) + '</td>');
                h.push('<td>' + common.nulltostr(r.JURISDICTIONNAME) + '</td>');
                h.push('<td>' + common.nulltostr(r.LOCATIONNAME) + '</td>');
                h.push('<td>');
                if (r.OWNERNAME1) { h.push(html.person_link(r.OWNERID, r.OWNERNAME1)); }
                if (r.OWNERNAME2) { h.push('<br/>' + html.person_link(r.OWNER2ID, r.OWNERNAME2)); }
                if (r.OWNERNAME3) { h.push('<br/>' + html.person_link(r.OWNER3ID, r.OWNERNAME3)); }
                h.push('</td>');
                h.push('<td>' + format.date(r.DISPATCHDATETIME) + ' ' + format.time(r.DISPATCHDATETIME) + '</td>');
                h.push('<td>' + format.date(r.RESPONDEDDATETIME) + ' ' + format.time(r.RESPONDEDDATETIME) + '</td>');
                h.push('<td>' + common.nulltostr(r.DISPATCHEDACO) + '</td>');
                h.push('<td>' + format.date(r.FOLLOWUPDATETIME) + '</td>');
                h.push('<td>' + format.date(r.COMPLETEDDATE) + '</td>');
                h.push('<td>' + common.nulltostr(r.COMPLETEDNAME) + '</td>');
                h.push('<td>' + html.truncate(r.CALLNOTES) + '</td>');
                h.push('</tr>');
            });
            return h.join("\n");
        },

        bind: function() {
            $("#searchresults").table();
        },

        sync: function() {
            $("#searchresults").trigger("sorton", [[[2,1]]]);
        },

        name: "incident_find_results",
        animation: "results",
        autofocus: "#asm-content a:first",
        title: function() { return _("Results"); },
        routes: {
            "incident_find_results": function() { common.module_loadandstart("incident_find_results", "incident_find_results?" + this.rawqs); }
        }

    };

    common.module_register(incident_find_results);

});
