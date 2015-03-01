/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var batch = {

        render: function() {
            return [
                html.content_header(_("Trigger Batch Processes")),
                '<div class="centered" style="max-width: 800px; margin-left: auto; margin-right: auto">',
                html.warn(_("These batch processes are run each night by the system and should not need to be run manually.") + '<br/><br/><b>' + 
                    _("Some batch processes may take a few minutes to run and could prevent other users being able to use the system for a short time.")
                    + '</b>'),
                '<div id="progress" style="margin-top: 10px"></div>',
                '<div id="tasks">',

                '<p id="p-genshelterpos">' + _("Recalculate on-shelter animal locations") + ' <button id="button-genshelterpos">' + _("Go") + '</button></p>',
                '<p id="p-genallpos">' + _("Recalculate ALL animal locations") + ' <button id="button-genallpos">' + _("Go") + '</button></p>',
                '<p id="p-genlookingfor">' + _("Regenerate 'Person looking for' report") + ' <button id="button-genlookingfor">' + _("Go") + '</button></p>',
                '<p id="p-genownername">' + _("Regenerate person names in selected format") + ' <button id="button-genownername">' + _("Go") + '</button></p>',
                '<p id="p-genlostfound">' + _("Regenerate 'Match lost and found animals' report") + ' <button id="button-genlostfound">' + _("Go") + '</button></p>',
                '<p id="p-genfigyear">' + _("Regenerate annual animal figures for") + ' <input id="figyear" class="asm-textbox asm-datebox" />',
                '<button id="button-genfigyear">' + _("Go") + '</button></p>',
                '<p id="p-genfigmonth">' + _("Regenerate monthly animal figures for") + ' <input id="figmonth" class="asm-textbox asm-datebox" />',
                '<button id="button-genfigmonth">' + _("Go") + '</button></p>',
                
                '</div>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        runmode: function(btn, formdata) {
            $("#tasks p").hide();
            $("#p-" + btn).show();
            $("#button-" + btn).button("disable");
            $("#progress").show().progressbar({ value: false });
            common.ajax_post("batch", formdata, function() {
                $("#button-" + btn).button("enable");
                $("#progress").hide();
                $("#tasks p").show();
            });
        },

        bind: function() {
            $("#button-genfigyear").button().click(function() { batch.runmode("genfigyear", "mode=genfigyear&figyear=" + $("#figyear").val()); });
            $("#button-genfigmonth").button().click(function() { batch.runmode("genfigmonth", "mode=genfigmonth&figmonth=" + $("#figmonth").val()); });
            $("#button-genshelterpos").button().click(function() { batch.runmode("genshelterpos", "mode=genshelterpos"); });
            $("#button-genallpos").button().click(function() { batch.runmode("genallpos", "mode=genallpos"); });
            $("#button-genlookingfor").button().click(function() { batch.runmode("genlookingfor", "mode=genlookingfor"); });
            $("#button-genownername").button().click(function() { batch.runmode("genownername", "mode=genownername"); });
            $("#button-genlostfound").button().click(function() { batch.runmode("genlostfound", "mode=genlostfound"); });
        }

    };

    common.module(batch, "batch", "options");

});
