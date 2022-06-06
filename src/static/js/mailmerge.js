/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    "use strict";

    const presets = {
        "Avery 5160" :  [ "letter", "inch", "8", "2.75", "1.0", "0.19", "0.5", "3", "10" ],
        "Avery 5360" :  [ "letter", "inch", "10", "2.83", "1.5", "0", "0.25", "3", "7" ],
        "Avery 5363" :  [ "letter", "inch", "8", "2.83", "1.375", "0", "0", "3", "8" ],
        "Avery A4 L7159" : [ "a4", "cm", "8", "6.65", "3.39", "0.65", "1.31", "3", "8" ],
        "Avery A4 L7161" : [ "a4", "cm", "10", "6.60", "4.66", "0.72", "0.88", "3", "6" ],
        "Avery A4 L7162" : [ "a4", "cm", "8", "10.16", "3.39", "0.47", "1.30", "2", "8" ],
        "OL5350" :      [ "letter", "inch", "10", "2.83", "1.5", "0", "0.25", "3", "7" ],
        "OL6950" :      [ "letter", "inch", "8", "2.75", "1", "0.375", "0.625", "3", "10" ],
        "OL870" :       [ "letter", "inch", "8", "2.83", "1.375", "0", "0", "3", "8" ],
        "OL875" :       [ "letter", "cm", "8", "6.99", "2.54", "0.48", "1.27", "3", "10" ],
        "OL950" :       [ "letter", "inch", "8", "2.75", "0.875", "0.1875", "0.6875", "3", "11" ]
    };

    const mailmerge = {

        previewloaded: false,
        recipientsloaded: false,

        render: function() {
            let hf = [
                '<input type="hidden" name="mode" value="{mode}" />',
                '<input type="hidden" name="mergeparams" data="mergeparams" />',
                '<input type="hidden" name="mergereport" data="mergereport" />',
                '<input type="hidden" name="mergetitle" data="mergetitle" />'
            ].join("\n");
            return [
                html.content_header(controller.title),

                controller.numrows > 0 ? '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em;">' : "",
                controller.numrows > 0 ? '<p class="centered"><span class="ui-icon ui-icon-info"></span>' : "",
                controller.numrows > 0 ? _("{0} record(s) match the mail merge.").replace("{0}", controller.numrows) : "",
                controller.numrows == 0 ? '<div class="ui-state-error ui-corner-all" style="margin-top: 5px; padding: 0 .7em;">' : "",
                controller.numrows == 0 ? '<p class="centered"><span class="ui-icon ui-icon-alert"></span>' : "",
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

                '<h3 id="printlabeltab"><a href="#">' + _("Produce a PDF of printable labels") + '</a></h3>',
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
                '<tr>',
                '<td><label for="fontpt">' + _("Font Size (pt)") + '</label></td>',
                '<td><input id="fontpt" name="fontpt" type="text" class="asm-halftextbox asm-numberbox" data-min="6" data-max="16" /></td>',
                '</tr>',
                '</table>',
                '<p class="centered"><button id="button-pdflabels" type="submit">' + _("Download") + '</button></p>',
                '</form>',
                '</div>',

                '<h3 id="sendemailtab"><a href="#">' + _("Send emails") + '</a></h3>',
                '<div id="sendemail">',
                hf.replace("{mode}", "email"),
                '<table width="100%">',
                '<tr>',
                '<td><label for="em-from">' + _("From") + '</label></td>',
                '<td><input id="em-from" data="from" type="text" class="asm-doubletextbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="em-subject">' + _("Subject") + '</label></td>',
                '<td><input id="em-subject" data="subject" type="text" class="asm-doubletextbox" /></td>',
                '</tr>',
                '<tr>',
                '<td colspan="2">',
                '<div id="em-body" data="body" data-height="300px" data-margin-top="24px" class="asm-richtextarea"></div>',
                '<p>',
                '<label for="em-template">' + _("Template") + '</label>',
                '<select id="em-template" class="asm-selectbox">',
                '</select>',
                '</p>',
                '</td>',
                '<td>',
                '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 0 .7em;">',
                '<p class="centered"><span class="ui-icon ui-icon-info"></span>',
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

                '<h3 id="matchingtab"><a href="#">' + _("View matching records") + '</a></h3>',
                '<div id="matching">',
                hf.replace("{mode}", "preview"),
                '</div>',

                '<h3 id="recipientstab"><a href="#">' + _("View email recipient list") + '</a></h3>',
                '<div id="recipients">',
                hf.replace("{mode}", "recipients"),
                '<button id="button-copyrecipients">' + _("Copy recipient list to the clipboard") + '</button>',
                '<div id="recipientslist" style="margin-top: 5px"></div>',
                '</div>',
                
                html.content_footer()
            ].join("\n");
        },

        render_fields: function() {
            let h = [];
            $.each(controller.fields, function(i, v) {
                h.push("&lt;&lt;" + v + "&gt;&gt; <br />");
            });
            return h.join("\n");
        },

        bind: function() {

            const preset_change = function() {
                let bits = presets[$("#labeltype").val()];
                if (bits === undefined) { return; }
                $("#papersize").select("value", bits[0]);
                $("#units").select("value", bits[1]);
                $("#fontpt").select("value", bits[2]);
                $("#hpitch").val(bits[3]);
                $("#vpitch").val(bits[4]);
                $("#lmargin").val(bits[5]);
                $("#tmargin").val(bits[6]);
                $("#cols").val(bits[7]);
                $("#rows").val(bits[8]);
            };

            let types = "";
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
            $("#button-email").button().click(async function() {
                $("#button-email").button("disable");
                let formdata = "mode=email&" + $("#sendemail input, #sendemail .asm-richtextarea").toPOST();
                await common.ajax_post("mailmerge", formdata);
                header.show_info(_("Messages successfully sent"));
                $("#asm-mailmerge-accordion").hide();
            });

            $("#button-copyrecipients").button({icons: { primary: "ui-icon-clipboard" }, text: true}).click(function() {
                common.copy_to_clipboard($("#recipientslist").text());
                header.show_info(_("Successfully copied to the clipboard."));
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
                let fromaddresses = [];
                let conf_org = html.decode(config.str("Organisation").replace(",", ""));
                let conf_email = config.str("EmailAddress");
                let org_email = conf_org + " <" + conf_email + ">";
                $("#em-from").val(conf_email);
                fromaddresses.push(conf_email);
                if (asm.useremail) {
                    fromaddresses.push(asm.useremail);
                    fromaddresses.push(html.decode(asm.userreal) + " <" + asm.useremail + ">");
                }
                fromaddresses = fromaddresses.concat(config.str("EmailFromAddresses").split(","));
                $("#em-from").autocomplete({source: fromaddresses});
                $("#em-from").autocomplete("widget").css("z-index", 1000);
                $("#em-from").bind("focus", function() {
                    $(this).autocomplete("search", "@");
                });
                $("#em-template").html( edit_header.template_list_options(controller.templates) );
                $("#em-template").change(function() {
                    let formdata = "mode=emailtemplate&dtid=" + $("#em-template").val();
                    header.show_loading(_("Loading..."));
                    common.ajax_post("document_gen", formdata, function(result) {
                        $("#em-body").html(result); 
                    });
                });

            }
        },

        sync: function() {

            // Default the email signature for bulk emails
            let sig = config.str("EmailSignature");
            if (sig) {
                $("#em-body").richtextarea("value", "<p>&nbsp;</p>" + sig);
            }

            // When the preview slider is chosen, load the preview data
            $("#asm-mailmerge-accordion").on("accordionactivate", function(event, ui) {
                if (ui.newHeader.attr("id") == "matchingtab" && !mailmerge.previewloaded) {
                    mailmerge.previewloaded = true;
                    header.show_loading();
                    let formdata = "mode=preview&" + $("#matching input").toPOST();
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
                if (ui.newHeader.attr("id") == "recipientstab" && !mailmerge.recipientsloaded) {
                    mailmerge.recipientsloaded = true;
                    header.show_loading();
                    let formdata = "mode=recipients&" + $("#recipients input").toPOST();
                    common.ajax_post("mailmerge", formdata).then(function(data) {
                        $("#recipientslist").html(data);
                    });
                }
            });

            // If the data doesn't have address columns, hide the label generating stuff
            if (!controller.hasaddress) {
                $("#printlabeltab").hide().next().hide();
            }

            // If the data doesn't have an email, hide the email sending stuff
            if (!controller.hasemail) {
                $("#sendemailtab").hide().next().hide();
                $("#recipientstab").hide().next().hide();
            }

            // If there are more than MailMergeMaxEmails results, hide the 
            // email section and replace it with a message explaining why.
            if (controller.numrows > config.integer("MailMergeMaxEmails")) {
                $("#sendemail").html( html.error( _("Please tighten the scope of your email campaign to {0} emails or less.").replace("{0}", config.str("MailMergeMaxEmails")) +
                    " " + _("Sending {0} emails is considered abusive and will damage the reputation of the email server.").replace("{0}", controller.numrows) ) );
            }

            // Set values for extra merge info
            $("input[name='mergeparams']").val( controller.mergeparams );
            $("input[name='mergereport']").val( controller.mergereport );
            $("input[name='mergetitle']").val( controller.mergetitle );
        },

        destroy: function() {
            common.widget_destroy("#em-body", "richtextarea");
        },

        name: "mailmerge",
        animation: "newdata",
        autofocus: "#includeheader",
        title: function() { return controller.title; }

    };

    common.module_register(mailmerge);

});
