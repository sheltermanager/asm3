/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var incident_find_results = {

        render: function() {
            return [
                html.content_header(_("Results")),
                '<div id="asm-results">',
                '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-search" style="float: left; margin-right: .3em;"></span>',
                controller.resultsmessage,
                '</p>',
                '</div>',
                '<table id="searchresults">',
                '<thead>',
                '<tr>',
                '<th>' + _("Type") + '</th>',
                '<th>' + _("Number") + '</th>',
                '<th>' + _("Incident Date/Time") + '</th>',
                '<th>' + _("Address") + '</th>',
                '<th>' + _("Zipcode") + '</th>',
                '<th>' + _("Suspect") + '</th>',
                '<th>' + _("Animal") + '</th>',
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
            var h = [];
            $.each(controller.rows, function(i, r) {
                h.push('<tr>');
                h.push('<td><a href="incident?id=' + r.ID + '">' + r.INCIDENTNAME + '</a></td>');
                h.push('<td>' + format.padleft(r.ID, 6) + '</td>');
                h.push('<td>' + format.date(r.INCIDENTDATETIME) + ' ' + format.time(r.INCIDENTDATETIME) + '</td>');
                h.push('<td>' + common.nulltostr(r.DISPATCHADDRESS) + '</td>');
                h.push('<td>' + common.nulltostr(r.DISPATCHPOSTCODE) + '</td>');
                h.push('<td>');
                if (r.OWNERNAME1) { h.push('<a href="person?id=' + r.OWNERID + '">' + common.nulltostr(r.OWNERNAME1) + '</a> '); }
                if (r.OWNERNAME2) { h.push('<br/><a href="person?id=' + r.OWNER2ID + '">' + common.nulltostr(r.OWNERNAME2) + '</a> '); }
                if (r.OWNERNAME3) { h.push('<br/><a href="person?id=' + r.OWNER3ID + '">' + common.nulltostr(r.OWNERNAME3) + '</a>'); }
                h.push('</td>');
                h.push('<td>' + (r.ANIMALID ? 
                    '<a href="animal?id=' + r.ANIMALID + '">' + common.nulltostr(r.SHELTERCODE) + ' ' + common.nulltostr(r.ANIMALNAME) + '</a>' :
                    "") + '</td>');
                h.push('<td>' + format.date(r.DISPATCHDATETIME) + ' ' + format.time(r.DISPATCHDATETIME) + '</td>');
                h.push('<td>' + format.date(r.RESPONDEDDATETIME) + ' ' + format.time(r.RESPONDEDDATETIME) + '</td>');
                h.push('<td>' + common.nulltostr(r.DISPATCHEDACO) + '</td>');
                h.push('<td>' + format.date(r.FOLLOWUPDATETIME) + '</td>');
                h.push('<td>' + format.date(r.COMPLETEDDATE) + '</td>');
                h.push('<td>' + common.nulltostr(r.COMPLETEDNAME) + '</td>');
                h.push('<td>' + common.nulltostr(r.CALLNOTES) + '</td>');
                h.push('</tr>');
            });
            return h.join("\n");
        },

        bind: function() {
            $("#searchresults").table();
        },

        sync: function() {
            $("#searchresults").trigger("sorton", [[[2,1]]]);
        }
    };

    common.module(incident_find_results, "incident_find_results", "results");

});
