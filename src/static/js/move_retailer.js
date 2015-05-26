/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var move_retailer = {

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="movementid" type="hidden" />',
                '<div id="page1">',
                html.content_header(_("Move an animal to a retailer"), true),
                '<div id="notonshelter" class="ui-state-error ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered"><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>',
                '<span class="centered">' + _("This animal is not on the shelter.") + '</span>',
                '</p>',
                '</div>',
                '<table class="asm-table-layout">',
                '<tr>',
                '<td>',
                '<label for="animal">' + _("Animal") + '</label>',
                '</td>',
                '<td>',
                '<input id="animal" data="animal" type="hidden" class="asm-animalchooser" value=\'\' />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="person">' + _("Retailer") + '</label>',
                '</td>',
                '<td>',
                '<input id="person" data="person" data-filter="retailer" type="hidden" class="asm-personchooser" value=\'\' />',
                '</td>',
                '</tr>',
                '<tr id="movementnumberrow">',
                '<td><label for="movementnumber">' + _("Movement Number") + '</label></td>',
                '<td><input id="movementnumber" data="movementnumber" class="asm-textbox" title=',
                '"' + html.title(_("A unique number to identify this movement")) + '"',
                ' /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="retailerdate">' + _("Date") + '</label></td>',
                '<td>',
                '<input id="retailerdate" data="retailerdate" class="asm-textbox asm-datebox" title="' + html.title(_("The date the retailer movement is effective from")) + '" />',
                '</td>',
                '</tr>',
                '</table>',
                html.content_footer(),
                html.box(5),
                '<button id="retailer">' + html.icon("movement") + ' ' + _("Move") + '</button>',
                '</div>',
                '</div>',
                '<div id="page2">',
                '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em;">',
                '<p class="centered"><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                '<span class="centered">' + _("Retailer movement successfully created."),
                '</span>',
                '<span class="centered" id="retailerfrom"></span>',
                html.icon("right"),
                '<span class="centered" id="retailerto"></span>',
                '</p>',
                '</div>',
                '<div id="asm-retailer-accordion">',
                '<h3><a href="#">' + _("Generate documentation") + '</a></h3>',
                '<div id="templatelist">',
                '</div>',
                '</div>',
                '</div>'
            ].join("\n");
        },

        bind: function() {
            var validation = function() {
                // Remove any previous errors
                header.hide_error();
                $("label").removeClass("ui-state-error-text");
                // animal
                if ($("#animal").val() == "") {
                    header.show_error(_("Movements require an animal"));
                    $("label[for='animal']").addClass("ui-state-error-text");
                    $("#animal").focus();
                    return false;
                }
                // person
                if ($("#person").val() == "") {
                    header.show_error(_("This type of movement requires a person."));
                    $("label[for='person']").addClass("ui-state-error-text");
                    $("#person").focus();
                    return false;
                }
                // date
                if ($.trim($("#retailerdate").val()) == "") {
                    header.show_error(_("This type of movement requires a date."));
                    $("label[for='retailerdate']").addClass("ui-state-error-text");
                    $("#retailerdate").focus();
                    return false;
                }
                return true;
            };

            // Callback when animal is changed
            $("#animal").animalchooser().bind("animalchooserchange", function(event, rec) {
              
                // Hide things before we start
                $("#notonshelter").fadeOut();
                $("#retailer").button("enable");

                // If the animal is not on the shelter, show that warning
                // and stop everything else
                if (rec.ARCHIVED == "1") {
                    $("#notonshelter").fadeIn();
                    $("#retailer").button("disable");
                    return;
                }

                // Update the list of document templates
                var formdata = "mode=templates&id=" + rec.ID;
                common.ajax_post("move_retailer", formdata)
                    .then(function(data) { 
                        $("#templatelist").html(data); 
                    });

            });


            $("#notonshelter").hide();

            $("#page1").show();
            $("#page2").hide();
            $("#asm-retailer-accordion").accordion({
                heightStyle: "content"
            }); 

            $("#movementnumberrow").hide();
            if (config.bool("MovementNumberOverride")) {
                $("#movementnumberrow").show();
            }

            // Set default values
            $("#retailerdate").datepicker("setDate", new Date());

            $("#retailer").button().click(function() {
                if (!validation()) { return; }
                $("#retailer").button("disable");
                header.show_loading(_("Creating..."));

                var formdata = $("input, select").toPOST();
                common.ajax_post("move_retailer", formdata)
                    .then(function(data) {

                        $("#movementid").val(data);

                        // Copy the animal/owner links to the success page so
                        // the user can go view them quickly again if they want
                        $("#retailerfrom").html( $(".animalchooser-display").html() );
                        $("#retailerto").html( $(".personchooser-display .justlink").html() );

                        $("#page1").fadeOut(function() {
                            $("#page2").fadeIn();
                        });
                    })
                    .always(function() {
                        header.hide_loading();
                        $("#retailer").button("enable");
                    });
            });

        },

        destroy: function() {
            common.widget_destroy("#animal");
            common.widget_destroy("#person");
        },

        name: "move_retailer",
        animation: "newdata",
        autofocus: "#asm-content button:first",
        title: function() { return _("Move an animal to a retailer"); },
        routes: {
            "move_retailer": function() { common.module_loadandstart("move_retailer", "move_retailer"); }
        }

    };

    common.module_register(move_retailer);

});
