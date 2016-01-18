/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    var person_links = {

        render: function() {
            var s = [
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
            $.each(controller.links, function(i, li) {
                var tdclass = "";
                if (li.DMOD.indexOf("D") != -1) {
                    tdclass = "style=\"color: red\"";
                }
                s.push('<tr>');
                s.push('<td ' + tdclass + '>' + li.TYPEDISPLAY + '</td>');
                s.push('<td ' + tdclass + '>' + format.date(li.DDATE) + '</td>');
                s.push('<td ' + tdclass + '>');
                if (li.TYPE == "OO") { s.push('<a href="animal?id=' + li.LINKID + '">' + li.LINKDISPLAY + '</a>'); }
                if (li.TYPE == "BI") { s.push('<a href="animal?id=' + li.LINKID + '">' + li.LINKDISPLAY + '</a>'); }
                if (li.TYPE == "PB") { s.push('<a href="animal?id=' + li.LINKID + '">' + li.LINKDISPLAY + '</a>'); }
                if (li.TYPE == "OV") { s.push('<a href="animal?id=' + li.LINKID + '">' + li.LINKDISPLAY + '</a>'); }
                if (li.TYPE == "CV") { s.push('<a href="animal?id=' + li.LINKID + '">' + li.LINKDISPLAY + '</a>'); }
                if (li.TYPE == "WL") { s.push('<a href="waitinglist?id=' + li.LINKID + '">' + li.LINKDISPLAY + '</a>'); }
                if (li.TYPE == "LA") { s.push('<a href="lostanimal?id=' + li.LINKID + '">' + li.LINKDISPLAY + '</a>'); }
                if (li.TYPE == "FA") { s.push('<a href="foundanimal?id=' + li.LINKID + '">' + li.LINKDISPLAY + '</a>'); }
                if (li.TYPE == "AC") { s.push('<a href="incident?id=' + li.LINKID + '">' + li.LINKDISPLAY + '</a>'); }
                if (li.TYPE == "AT") { s.push('<a href="animal_transport?id=' + li.LINKID + '">' + li.LINKDISPLAY + '</a>'); }
                if (li.TYPE == "AP") { s.push('<a href="animal?id=' + li.LINKID + '">' + li.LINKDISPLAY + '</a>'); }
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
