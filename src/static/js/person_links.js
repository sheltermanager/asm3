/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    "use strict";

    const person_links = {

        render: function() {
            let s = [
                edit_header.person_edit_header(controller.person, "links", controller.tabcounts),
                '<table id="table-links">',
                '<thead>',
                '<tr>',
                '<th>' + _("Type") + '</th>',
                '<th>' + _("Date") + '</th>',
                '<th></th>',
                '<th></th>',
                '</tr>',
                '</thead>',
                '<tbody>'
            ];
            const typemap = {
                "CO": [ _("Current Owner"), "animal?id=" ],
                "OO": [ _("Original Owner"), "animal?id=" ],
                "BI": [ _("Brought In By"), "animal?id=" ],
                "RO": [ _("Returned By"), "animal?id=" ],
                "AO": [ _("Adoption Coordinator"), "animal?id=" ],
                "AEH": [ _("Animal Entry History"), "animal?id=" ],
                "OV": [ _("Owner Vet"), "animal?id=" ],
                "CV": [ _("Current Vet"), "animal?id=" ],
                "AV": [ _("Altering Vet"), "animal?id=" ],
                "WL": [ _("Waiting List Contact"), "waitinglist?id=" ],
                "LA": [ _("Lost Animal Contact"), "lostanimal?id=" ],
                "FA": [ _("Found Animal Contact"), "foundanimal?id=" ],
                "ACS": [ _("Animal Control Incident"), "incident?id=" ],
                "ACC": [ _("Animal Control Caller"), "incident?id=" ],
                "ACV": [ _("Animal Control Victim"), "incident?id=" ],
                "ATD": [ _("Driver"), "animal_transport?id=" ],
                "ATP": [ _("Pickup Address"), "animal_transport?id=" ],
                "ATR": [ _("Dropoff Address"), "animal_transport?id=" ],
                "AFA": [ "", "animal?id=" ],
                "AFP": [ "", "person?id=" ],
                "AFI": [ "", "incident?id=" ]
            };
            $.each(controller.links, function(i, li) {
                let tdclass = "";
                if (li.DMOD.indexOf("D") != -1) {
                    tdclass = "style=\"color: red\"";
                }
                let info = typemap[li.TYPE], label = info[0], url = info[1];
                if (label == "") { label = li.TYPEDISPLAY; }
                s.push('<tr>');
                s.push('<td ' + tdclass + '>' + label + '</td>');
                s.push('<td ' + tdclass + '>' + format.date(li.DDATE) + '</td>');
                s.push('<td ' + tdclass + '>');
                s.push('<a href="' + url + li.LINKID + '">' + li.LINKDISPLAY + '</a>');
                if (li.DMOD.indexOf("D") != -1) { s.push( html.icon("death", _("Deceased"))); }
                s.push('</td>');
                s.push('<td ' + tdclass + '>' + li.FIELD2 + '</td>');
                s.push('</tr>');
            });
            s.push('</tbody>');
            s.push('</table>');
            s.push('</div>');
            s.push(html.content_footer());
            return s.join("\n");
        },

        bind: function() {
            $("#table-links").table();
            $(".asm-tabbar").asmtabs();
        },

        name: "person_links",
        animation: "formtab",
        title: function() { return controller.person.OWNERNAME; },
        routes: {
            "person_links": function() { common.module_loadandstart("person_links", "person_links?id=" + this.qs.id); }
        }

    };

    common.module_register(person_links);

});
