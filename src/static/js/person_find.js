/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    "use strict";

    const person_find = {

        render: function() {
            return [
                html.content_header(_("Find Person")),
                '<div id="personsearchform">',
                '<p class="asm-search-selector">',
                '<a id="asm-search-selector-simple" href="#">' + _("Simple") + '</a> |',
                '<a id="asm-search-selector-advanced" href="#">' + _("Advanced") + '</a>',
                '</p>',
                '<div id="asm-criteria-simple">',
                '<table class="asm-table-layout">',
                '<tr>',
                '<td>',
                '<label for="q">' + _("Search") + '</label>',
                '</td>',
                '<td>',
                '<input id="mode" data="mode" type="hidden" value="SIMPLE" />',
                '<input id="q" type="search" data="q" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '</table>',
                '</div>',
                '<div id="asm-criteria-advanced">',
                '<table class="asm-table-layout">',
                '<tr>',
                '<td>',
                '<label for="code">' + _("Code contains") + '</label>',
                '</td>',
                '<td>',
                '<input id="code" data="code" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="idnumber">' + _("ID contains") + '</label>',
                '</td>',
                '<td>',
                '<input id="idnumber" data="idnumber" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="name">' + _("Name contains") + '</label>',
                '</td>',
                '<td>',
                '<input id="name" data="name" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="address">' + _("Address contains") + '</label>',
                '</td>',
                '<td>',
                '<input id="address" data="address" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr id="towncountyrow">',
                '<td>',
                '<label for="town">' + _("City contains") + '</label>',
                '</td>',
                '<td>',
                '<input id="town" data="town" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="county">' + _("State contains") + '</label>',
                '</td>',
                '<td>',
                '<input id="county" data="county" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="postcode">' + _("Zipcode contains") + '</label>',
                '</td>',
                '<td>',
                '<input id="postcode" data="postcode" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="homecheck">' + _("Homecheck areas") + '</label>',
                '</td>',
                '<td>',
                '<input id="homecheck" data="homecheck" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="phone">' + _("Phone contains") + '</label>',
                '</td>',
                '<td>',
                '<input id="phone" data="phone" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="email">' + _("Email") + '</label>',
                '</td>',
                '<td>',
                '<input id="email" data="email" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="createdby">' + _("Created By") + '</label>',
                '</td>',
                '<td>',
                '<select id="createdby" data="createdby" class="asm-selectbox">',
                '<option value="">' + _("(anyone)") + '</option>',
                html.list_to_options(controller.users, "USERNAME", "USERNAME"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="createdsince">' + _("Created Since") + '</label>',
                '</td>',
                '<td>',
                '<input id="createdsince" data="createdsince" type="text" class="asm-textbox asm-datebox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="jurisdiction">' + _("Jurisdiction") + '</label>',
                '</td>',
                '<td>',
                '<select id="jurisdiction" data="jurisdiction" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.jurisdictions, "ID", "JURISDICTIONNAME"),
                '</select>',
                '</td>',
                '<td></td>', // EMPTY
                '<tr>',
                '<td>',
                '<label for="comments">' + _("Comments contain") + '</label>',
                '</td>',
                '<td>',
                '<input id="comments" data="comments" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="filter">' + _("Flags") + '</label>',
                '</td>',
                '<td>',
                '<select id="filter" data="filter" multiple="multiple" class="asm-bsmselect">',
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="medianotes">' + _("Media notes contain") + '</label>',
                '</td>',
                '<td>',
                '<input id="medianotes" data="medianotes" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="gdpr">' + _("GDPR Contact Opt-In") + '</label>',
                '</td>',
                '<td>',
                '<select id="gdpr" data="gdpr" multiple="multiple" class="asm-bsmselect">',
                edit_header.gdpr_contact_options(),
                '</select>',
                '</td>',
                '</tr>',
                additional.additional_search_fields(controller.additionalfields, 2),
                '</table>',
                '</div>',
                '<p class="centered">',
                '<button id="searchbutton" type="button">' + _("Search") + '</button>',
                '</p>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            // Switch to simple search criteria
            const simple_mode = function() {
                $("#mode").val("SIMPLE");
                $("#asm-search-selector-advanced").removeClass("asm-link-disabled");
                $("#asm-search-selector-simple").addClass("asm-link-disabled");
                $("#asm-criteria-advanced").slideUp(function() {
                    $("#asm-criteria-simple").slideDown(function() {
                        $("input[data='q']").focus();
                    });
                });
            };

            // Switch to advanced search criteria
            const advanced_mode = function() {
                $("#mode").val("ADVANCED");
                $("input[data='q']").val("");
                $("#asm-search-selector-simple").removeClass("asm-link-disabled");
                $("#asm-search-selector-advanced").addClass("asm-link-disabled");
                $("#asm-criteria-simple").slideUp(function() {
                    $("#asm-criteria-advanced").slideDown(function() {
                        $("input[data='name']").focus();
                    });
                });
            };

            // Handle switching between modes via the links
            $("#asm-search-selector-simple").click(function() {
                simple_mode();
            });

            $("#asm-search-selector-advanced").click(function() {
                advanced_mode();
            });

            // Load the person flag options
            html.person_flag_options(null, controller.flags, $("#filter"), true, true);

            $("label[for='gdpr']").toggle( config.bool("ShowGDPRContactOptIn") );
            $("#gdpr").closest("td").toggle( config.bool("ShowGDPRContactOptIn") );

            // Search button - we don't use the traditional submit because
            // the bsmselect widget craps extra values into the form and 
            // breaks filtering by flag
            $("#searchbutton").button().click(function() {
                common.route("person_find_results?" + $("#personsearchform input, #personsearchform select").toPOST());
            });

            // We need to re-enable the return key submitting the form
            $("#personsearchform").keypress(function(e) {
                if (e.keyCode == 13) {
                    common.route("person_find_results?" + $("#personsearchform input, #personsearchform select").toPOST());
                }
            });

            // Get the default mode and set that
            $("#asm-criteria-simple").hide();
            $("#asm-criteria-advanced").hide();
            if (config.bool("AdvancedFindOwner")) {
                advanced_mode();
            }
            else {
                simple_mode();
            }
        },

        name: "person_find",
        animation: "criteria",
        title: function() { return _("Find Person"); },
        routes: {
            "person_find": function() { common.module_loadandstart("person_find", "person_find"); }
        }

    };

    common.module_register(person_find);

});
