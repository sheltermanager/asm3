/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var giftaid_hmrc_spreadsheet = {

        render: function() {
            return [
                html.content_header("HMRC Gift Aid Spreadsheet"),
                html.warn("WARNING: Generating gift aid spreadsheets can take a few minutes if you have many donations."),
                '<form id="hmrcform" action="giftaid_hmrc_spreadsheet" method="get">',
                '<table>',
                '<tr>',
                '<td><label for="fromdate">From</label></td>',
                '<td><input type="text" class="asm-textbox asm-datebox" name="fromdate" id="fromdate" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="todate">To</label></td>',
                '<td><input type="text" class="asm-textbox asm-datebox" name="todate" id="todate" /></td>',
                '</tr>',
                '</table>',
                '<div class="centered">',
                '<button id="button-gen" type="button">Generate</button>',
                '</div>',
                '</form>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            $("#button-gen").button().click(function() {
                if (validate.notblank([ "fromdate", "todate" ])) {
                    $("#hmrcform").submit();
                }
            });
        },

        sync: function() {

        }
    };

    common.module(giftaid_hmrc_spreadsheet, "giftaid_hmrc_spreadsheet", "report");

});
