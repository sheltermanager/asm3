/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    "use strict";

    const person_find = {

        render: function() {
            let col1 = [
                html.search_field_text("code", _("Code contains")),
                html.search_field_text("idnumber", _("ID contains")),
                html.search_field_text("name", _("Name contains")),
                html.search_field_text("address", _("Address contains")),
                html.search_field_text("town", _("City contains")),
                html.search_field_text("county", _("State contains")),
                html.search_field_text("postcode", _("Zipcode contains")),
                html.search_field_text("homecheck", _("Homecheck areas")),
                html.search_field_text("phone", _("Phone contains")),
                html.search_field_text("email", _("Email contains")),
            ].join("\n");
            let col2 = [
                html.search_field_select("createdby", _("Created By"), '<option value="">' + _("(anyone)") + '</option>' + html.list_to_options(controller.users, "USERNAME", "USERNAME"), false),
                html.search_field_date("createdsince", _("Created Since")),
                html.search_field_select("jurisdiction", _("Jurisdiction"), html.list_to_options(controller.jurisdictions, "ID", "JURISDICTIONNAME")),
                html.search_field_select("site", _("Site"), html.list_to_options(controller.sites, "ID", "SITENAME")),
                html.search_field_text("comments", _("Comments contains")),
                html.search_field_text("medianotes", _("Media notes contain")),
                html.search_field_mselect("gdpr", _("GDPR Contact Opt-In"), edit_header.gdpr_contact_options()),
                html.search_field_mselect("filter", _("Flags"), ""),
            ].join("\n");
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
                html.search_row([
                    html.search_column(col1),
                    html.search_column(col2),
                    html.search_column(additional.additional_search_fields(controller.additionalfields, 1)),
                ]),
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
                let showsite = config.bool("MultiSiteEnabled") && asm.siteid;
                $("#site").closest("tr").toggle(showsite);
            });

            // Load the person flag options
            html.person_flag_options(null, controller.flags, $("#filter"), false, true);

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
