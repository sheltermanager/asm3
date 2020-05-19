/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    "use strict";

    var presets = {
        "Avery 5160" :  [ "letter", "inch", "2.75", "1.0", "0.19", "0.5", "3", "10" ],
        "Avery 5360" :  [ "letter", "inch", "2.83", "1.5", "0", "0.25", "3", "7" ],
        "Avery 5363" :  [ "letter", "inch", "2.83", "1.375", "0", "0", "3", "8" ],
        "Avery A4 L7159" : [ "a4", "cm", "6.65", "3.39", "0.65", "1.31", "3", "8" ],
        "Avery A4 L7161" : [ "a4", "cm", "6.60", "4.66", "0.72", "0.88", "3", "6" ],
        "Avery A4 L7162" : [ "a4", "cm", "10.16", "3.39", "0.47", "1.30", "2", "8" ],
        "OL5350" :      [ "letter", "inch", "2.83", "1.5", "0", "0.25", "3", "7" ],
        "OL6950" :      [ "letter", "inch", "2.75", "1", "0.375", "0.625", "3", "10" ],
        "OL870" :       [ "letter", "inch", "2.83", "1.375", "0", "0", "3", "8" ],
        "OL875" :       [ "letter", "cm", "6.99", "2.54", "0.48", "1.27", "3", "10" ],
        "OL950" :       [ "letter", "inch", "2.75", "0.875", "0.1875", "0.6875", "3", "11" ]
    };

    var mailmerge = {

        previewloaded: false,

        render: function() {
            var hf = [
                '<input type="hidden" name="mode" value="{mode}" />',
                '<input type="hidden" name="mergeparams" data="mergeparams" value="' + encodeURIComponent(controller.mergeparams) + '" />',
                '<input type="hidden" name="mergereport" data="mergereport" value="' + controller.mergereport + '" />',
                '<input type="hidden" name="mergetitle" data="mergetitle" value="' + encodeURIComponent(controller.mergetitle) + '" />'
            ].join("\n");
            return [
                html.content_header(controller.title),

                controller.numrows > 0 ? '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em;">' : "",
                controller.numrows > 0 ? '<p class="centered"><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>' : "",
                controller.numrows > 0 ? _("{0} record(s) match the mail merge.").replace("{0}", controller.numrows) : "",
                controller.numrows == 0 ? '<div class="ui-state-error ui-corner-all" style="margin-top: 5px; padding: 0 .7em;">' : "",
                controller.numrows == 0 ? '<p class="centered"><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>' : "",
                controller.numrows == 0 ? _("{0} record(s) match the mail merge.").replace("{0}", controller.numrows) : "",
                '</p>',
                '</div>',

                '<div id="asm-mailmerge-accordion">',
                '<h3><a href="#">' + _("Produce a CSV File") + '</a></h3>',
                '<div>',
                '<form action="mailmerge" method="post">',
                hf.replace("{mode}", "csv"),
                '<p class="centered">',
                '<input id="includeheader" type="checkbox" name="includeheader" class="asm-checkbox" />',
                '<label for="includeheader">' + _("Include CSV header line") + '</label>',
                '<button id="button-csv" type="submit">' + _("Download") + '</button>',
                '</p>',
                '</form>',
                '</div>',

                '<h3 id="printlabel"><a href="#">' + _("Produce a PDF of printable labels") + '</a></h3>',
                '<div>',
                '<form action="mailmerge" method="post">',
                hf.replace("{mode}", "labels"),
                '<table width="100%">',
                '<tr>',
                '<td><label for="labeltype">' + _("Type") + '</label></td>',
                '<td><select id="labeltype" class="asm-selectbox">',
                '</select></td>',
                '<tr>',
                '<td></td><td><hr /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="papersize">' + _("Paper Size") + '</label></td>',
                '<td><select id="papersize" name="papersize" class="asm-selectbox">',
                '<option value="a4">' + _("A4") + '</option>',
                '<option value="letter">' + _("Letter") + '</option>',
                '</select></td>',
                '<td><label for="units">' + _("Units") + '</label></td>',
                '<td><select id="units" name="units" class="asm-selectbox">',
                '<option value="cm">' + _("cm") + '</option>',
                '<option value="inch">' + _("inches") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="hpitch">' + _("Horizontal Pitch") + '</label></td>',
                '<td><input id="hpitch" name="hpitch" type="text" class="asm-halftextbox asm-numberbox" /></td>',
                '<td><label for="vpitch">' + _("Vertical Pitch") + '</label></td>',
                '<td><input id="vpitch" name="vpitch" type="text" class="asm-halftextbox asm-numberbox" /></td>',
                '<td><label for="lmargin">' + _("Left Margin") + '</label></td>',
                '<td><input id="lmargin" name="lmargin" type="text" class="asm-halftextbox asm-numberbox" /></td>',
                '<td><label for="tmargin">' + _("Top Margin") + '</label></td>',
                '<td><input id="tmargin" name="tmargin" type="text" class="asm-halftextbox asm-numberbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="cols">' + _("Columns") + '</label></td>',
                '<td><input id="cols" name="cols" type="text" class="asm-halftextbox asm-numberbox" /></td>',
                '<td><label for="rows">' + _("Rows") + '</label></td>',
                '<td><input id="rows" name="rows" type="text" class="asm-halftextbox asm-numberbox" /></td>',
                '</tr>',
                '</table>',
                '<p class="centered"><button id="button-pdflabels" type="submit">' + _("Download") + '</button></p>',
                '</form>',
                '</div>',

                '<h3><a href="#">' + _("Send emails") + '</a></h3>',
                '<div id="sendemail">',
                hf.replace("{mode}", "email"),
                '<table width="100%">',
                '<tr>',
                '<td><label for="emailfrom">' + _("From") + '</label></td>',
                '<td><input id="emailfrom" data="from" type="text" class="asm-doubletextbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="emailsubject">' + _("Subject") + '</label></td>',
                '<td><input id="emailsubject" data="subject" type="text" class="asm-doubletextbox" /></td>',
                '</tr>',
                '<tr>',
                '<td colspan="2">',
                '<div id="emailbody" data="body" data-height="300px" data-margin-top="24px" class="asm-richtextarea"></div>',
                '<p>',
                '<label for="emailtemplate">' + _("Template") + '</label>',
                '<select id="emailtemplate" class="asm-selectbox">',
                '</select>',
                '</p>',
                '</td>',
                '<td>',
                '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em;">',
                '<p class="centered"><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                _("Valid tokens for the subject and text") + ':',
                '<br/><br/>',
                mailmerge.render_fields(),
                '</p>',
                '</div>',
                '</td>',
                '</tr>',
                '</table>',
                '<p class="centered"><button id="button-email">' + _("Send Emails") + '</button></p>',
                '</div>',

                '<h3><a href="#">' + _("Generate documents") + '</a></h3>',
                '<div>',
                '<form id="mailmerge-letters" action="mailmerge" method="post">',
                hf.replace("{mode}", "document"),
                '<input type="hidden" id="templateid" name="templateid" value = "" />',
                '<ul class="asm-menu-list">',
                edit_header.template_list(controller.templates, "#", 0),
                '</ul>',
                '</form>',
                '</div>',

                '<h3 id="lmatching"><a href="#">' + _("View matching records") + '</a></h3>',
                '<div id="matching">',
                hf.replace("{mode}", "preview"),
                '</div>',
                
                html.content_footer()
            ].join("\n");
        },

        render_fields: function() {
            var h = [];
            $.each(controller.fields, function(i, v) {
                h.push("&lt;&lt;" + v + "&gt;&gt; <br />");
            });
            return h.join("\n");
        },

        bind: function() {

            var preset_change = function() {
                var bits = presets[$("#labeltype").val()];
                if (bits === undefined) { return; }
                $("#papersize").select("value", bits[0]);
                $("#units").select("value", bits[1]);
                $("#hpitch").val(bits[2]);
                $("#vpitch").val(bits[3]);
                $("#lmargin").val(bits[4]);
                $("#tmargin").val(bits[5]);
                $("#cols").val(bits[6]);
                $("#rows").val(bits[7]);
            };

            var types = "";
            $.each(presets, function(key, value) {
                types += "<option>" + key + "</option>";
            });
            $("#labeltype").html(types);

            $("#labeltype").change(preset_change);
            preset_change();

            $("#asm-mailmerge-accordion").accordion({
                heightStyle: "content"
            });

            $("#button-csv, #button-pdflabels").button();
            $("#button-email").button().click(function() {
                $("#button-email").button("disable");
                var formdata = "mode=email&" + $("#sendemail input, #sendemail .asm-richtextarea").toPOST();
                common.ajax_post("mailmerge", formdata)
                    .then(function() { 
                        header.show_info(_("Messages successfully sent"));
                        $("#asm-mailmerge-accordion").hide();
                    });
            });

            $("#mailmerge-letters .templatelink").each(function() {
                // When a template is clicked, copy the template ID
                // into a hidden field and submit it
                $(this).attr("href", "#");
                $(this).click(function() {
                    $("#templateid").val( $(this).attr("data") );
                    $("#mailmerge-letters").submit();
                    return false;
                });
            });

            if (controller && controller.numrows == 0) {
                $("#asm-mailmerge-accordion").hide();
            } 
            else {
                $("#emailfrom").val(html.decode(config.str("Organisation")) + " <" + config.str("EmailAddress") + ">");
                $("#emailtemplate").html( edit_header.template_list_options(controller.templates) );
                $("#emailtemplate").change(function() {
                    var formdata = "mode=emailtemplate&dtid=" + $("#emailtemplate").val();
                    header.show_loading(_("Loading..."));
                    common.ajax_post("document_gen", formdata, function(result) {
                        $("#emailbody").html(result); 
                    });
                });

            }
        },

        sync: function() {

            // Default the email signature for bulk emails
            var sig = config.str("EmailSignature");
            if (sig) {
                $("#emailbody").richtextarea("value", "<p>&nbsp;</p>" + sig);
            }

            // When the preview slider is chosen, load the preview data
            $("#asm-mailmerge-accordion").on("accordionactivate", function(event, ui) {
                if (ui.newHeader.attr("id") == "lmatching" && !mailmerge.previewloaded) {
                    mailmerge.previewloaded = true;
                    header.show_loading();
                    var formdata = "mode=preview&" + $("#matching input").toPOST();
                    common.ajax_post("mailmerge", formdata).then(function(data) {
                        // Create a table of matching rows
                        var h = [], d = jQuery.parseJSON(data);
                        h.push("<table><thead><tr>");
                        $.each(controller.fields, function(i, v) {
                            h.push("<th>" + v + "</th>");
                        });
                        h.push("</tr></thead><tbody>");
                        $.each(d, function(i, v) {
                            h.push("<tr>");
                            $.each(controller.fields, function(fi, fv) {
                                h.push("<td>" + v[fv] + "</td>");
                            });
                            h.push("</tr>");
                        });
                        h.push("</tbody></table>");
                        $("#matching").html(h.join("\n"));
                        $("#matching table").table();
                    });
                }
            });

            // If the data don't have person columns, hide the label generating stuff
            if (!controller.hasperson) {
                $("#printlabel").hide().next().hide();
            }

            // If there are more than MailMergeMaxEmails results, hide the 
            // email section and replace it with a message explaining why.
            if (controller.numrows > config.integer("MailMergeMaxEmails")) {
                $("#sendemail").html( html.error( _("Please tighten the scope of your email campaign to {0} emails or less.").replace("{0}", config.str("MailMergeMaxEmails")) +
                    " " + _("Sending {0} emails is considered abusive and will damage the reputation of the email server.").replace("{0}", controller.numrows) ) );
            }

        },

        destroy: function() {
            common.widget_destroy("#emailbody", "richtextarea");
        },

        name: "mailmerge",
        animation: "newdata",
        autofocus: "#includeheader",
        title: function() { return controller.title; }

    };

    common.module_register(mailmerge);

});
