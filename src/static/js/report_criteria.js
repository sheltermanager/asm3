/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    "use strict";

    const report_criteria = {

        render: function() {

            let h = [
                html.content_header(controller.title),
                '<div id="criteriaform">',
                '<input data-post="id" type="hidden" value="' + controller.id + '" />',
                '<input data-post="hascriteria" type="hidden" value="true" />',
                '<div id="displayfields">',
                '<table>'
            ];

            $.each(controller.criteria, function(i, v) {
                let [name, rtype, question] = v;
                if (rtype == "DATE") {
                    h.push('<tr>' +
                        '<td>' + question + '</td>' +
                        '<td>' +
                        '<input class="asm-textbox asm-datebox" id="report-' + name + '" data-post="' + name + '">' +
                        '</td></tr>');
                }
                else if (rtype == "STRING") {
                    h.push('<tr>' +
                        '<td>' + question + '</td>' +
                        '<td>' +
                        '<input class="asm-textbox" id="report-' + name + '" data-post="' + name + '">' +
                        '</td></tr>');
                }
                else if (rtype == "LOOKUP") {
                    let values = question.substring(question.indexOf("|")+1).split(",");
                    if (question.indexOf("|") != -1) { question = question.substring(0, question.indexOf("|")); } 
                    h.push('<tr>' +
                        '<td>' + question + '</td>' +
                        '<td>' +
                        '<select class="asm-selectbox" id="report-' + name + '" data-post="' + name + '">' +
                        html.list_to_options(values) +
                        '</select>' +
                        '</td></tr>');
                }
                else if (rtype == "NUMBER") {
                    h.push('<tr>' +
                        '<td>' + question + '</td>' +
                        '<td>' +
                        '<input class="asm-textbox asm-numberbox" id="report-' + name + '" data-post="' + name + '">' +
                        '</td></tr>');
                }
                else if (rtype == "ANIMAL" || rtype == "FSANIMAL" || rtype == "ALLANIMAL") {
                    h.push('<tr>' +
                        '<td>' + _("Animal") + '</td>' +
                        '<td>' +
                        '<input class="asm-animalchooser" id="report-' + name + '" data-post="' + name + '" type="hidden" />' +
                        '</td></tr>');
                }
                else if (rtype == "ANIMALS") {
                    h.push('<tr>' +
                        '<td>' + _("Animals") + '</td>' +
                        '<td>' +
                        '<input class="asm-animalchoosermulti" id="report-' + name + '" data-post="' + name + '" type="hidden" />' +
                        '</td></tr>');
                }
                else if (rtype == "ANIMALFLAG") {
                    h.push('<tr>' + 
                        '<td>' + _("Flag") + '</td>' +
                        '<td>' +
                        '<select class="asm-selectbox animalflags" id="report-' + name + '" data-post="' + name + '"></select>' +
                        '</td></tr>');
                }
                else if (rtype == "DONATIONTYPE" || rtype == "PAYMENTTYPE") {
                    h.push('<tr>' + 
                        '<td>' + _("Payment Type") + '</td>' +
                        '<td>' +
                        '<select class="asm-selectbox" id="report-' + name + '" data-post="' + name + '">' + 
                        html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME") +
                        '</select>' +
                        '</td></tr>');
                }
                else if (rtype == "ENTRYCATEGORY") {
                    h.push('<tr>' + 
                        '<td>' + _("Entry Category") + '</td>' +
                        '<td>' +
                        '<select class="asm-selectbox" id="report-' + name + '" data-post="' + name + '">' + 
                        html.list_to_options(controller.entryreasons, "ID", "REASONNAME") +
                        '</select>' +
                        '</td></tr>');
                }
                else if (rtype == "LITTER") {
                    h.push('<tr>' + 
                        '<td>' + _("Litter") + '</td>' +
                        '<td>' +
                        '<select class="asm-selectbox" id="report-' + name + '" data-post="' + name + '">' + 
                        html.list_to_options(controller.litters, "value", "label") +
                        '</select>' +
                        '</td></tr>');
                }
                else if (rtype == "LOCATION") {
                    h.push('<tr>' + 
                        '<td>' + _("Location") + '</td>' +
                        '<td>' +
                        '<select class="asm-selectbox" id="report-' + name + '" data-post="' + name + '">' + 
                        html.list_to_options(controller.locations, "ID", "LOCATIONNAME") +
                        '</select>' +
                        '</td></tr>');
                }
                else if (rtype == "LOGTYPE") {
                    h.push('<tr>' + 
                        '<td>' + _("Log Type") + '</td>' +
                        '<td>' +
                        '<select class="asm-selectbox" id="report-' + name + '" data-post="' + name + '">' + 
                        html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME") +
                        '</select>' +
                        '</td></tr>');
                }
                else if (rtype == "MEDIAFLAG") {
                    h.push('<tr>' + 
                        '<td>' + _("Flag") + '</td>' +
                        '<td>' +
                        '<select class="asm-selectbox mediaflags" id="report-' + name + '" data-post="' + name + '"></select>' +
                        '</td></tr>');
                }
                else if (rtype == "PAYMENTMETHOD" || rtype == "PAYMENTTYPE") {
                    h.push('<tr>' + 
                        '<td>' + _("Payment Method") + '</td>' +
                        '<td>' +
                        '<select class="asm-selectbox" id="report-' + name + '" data-post="' + name + '">' + 
                        html.list_to_options(controller.paymentmethods, "ID", "PAYMENTNAME") +
                        '</select>' +
                        '</td></tr>');
                }
                else if (rtype == "PERSONFLAG") {
                    h.push('<tr>' + 
                        '<td>' + _("Flag") + '</td>' +
                        '<td>' +
                        '<select class="asm-selectbox personflags" id="report-' + name + '" data-post="' + name + '"></select>' +
                        '</td></tr>');
                }
                else if (rtype == "PERSON") {
                    h.push('<tr>' +
                        '<td>' + _("Person") + '</td>' +
                        '<td>' +
                        '<input class="asm-personchooser" id="report-' + name + '" data-post="' + name + '" type="hidden" />' +
                        '</td></tr>');
                }
                else if (rtype == "SITE") {
                    h.push('<tr>' + 
                        '<td>' + _("Site") + '</td>' +
                        '<td>' +
                        '<select class="asm-selectbox" id="report-' + name + '" data-post="' + name + '">' + 
                        html.list_to_options(controller.sites, "ID", "SITENAME") +
                        '</select>' +
                        '</td></tr>');
                }
                else if (rtype == "SPECIES") {
                    h.push('<tr>' + 
                        '<td>' + _("Species") + '</td>' +
                        '<td>' +
                        '<select class="asm-selectbox" id="report-' + name + '" data-post="' + name + '">' + 
                        html.list_to_options(controller.species, "ID", "SPECIESNAME") +
                        '</select>' +
                        '</td></tr>');
                }
                else if (rtype == "TYPE") {
                    h.push('<tr>' + 
                        '<td>' + _("Type") + '</td>' +
                        '<td>' +
                        '<select class="asm-selectbox" id="report-' + name + '" data-post="' + name + '">' + 
                        html.list_to_options(controller.types, "ID", "ANIMALTYPE") +
                        '</select>' +
                        '</td></tr>');
                }
            });

            h.push('<tr>' + 
                '<td></td>' + 
                '<td><button id="submitcriteria">' + _("Generate") + '</button></td>' +
                '</tr></table>');

            h.push('</div>' +
                '</div>' +
                html.content_footer() );

            return h.join("\n");
        },

        bind: function() {

            $("#submitcriteria").button().click(function() {
                report_criteria.submit();
            });

            $("#displayfields input").keypress(function(e) {
                if (e.which == 13) {
                    report_criteria.submit();
                    return false;
                }
            });

        },

        sync: function() {
            // Set date inputs to today in the local timezone
            $(".asm-datebox").val( format.date(new Date()) );

            // Special handling for flags
            html.animal_flag_options(null, controller.animalflags, $(".animalflags"));
            html.media_flag_options(controller.mediaflags, $(".mediaflags"));
            html.person_flag_options(null, controller.personflags, $(".personflags"));
        },

        delay: function() {
            // Focus the first displayed criteria field
            $("#displayfields input, #displayfields select").first().focus();
        },

        destroy: function() {
        },

        submit: function() {
            common.route(controller.target + "?" + $("#criteriaform input, #criteriaform select").toPOST(true));
        },

        name: "report_criteria",
        animation: "newdata",
        title: function() { return controller.title; }

    };

    common.module_register(report_criteria);

});
