/*global $, console, jQuery, */
/*global asm, asm_widget, common, config, dlgfx, edit_header, format, html, header, log, schema, tableform, validate, _, escape, unescape */

"use strict";

// This file contains composite widgets, which are mini screens
// or dialogs that can be embedded in multiple places in the system.


/**
 * Widget to show a create a payment dialog.
 * Target should be a div to contain the hidden dialog.
 */
$.fn.createpayment = asm_widget({

    _create: function(t) {
        t.append([
            '<div id="dialog-payment" style="display: none" title="' + html.title(_("Create Payment")) + '">',
            '<div>',
            '<input type="hidden" id="pm-animal" data="animal" class="asm-field" value="" />',
            '<input type="hidden" id="pm-person" data="person" class="asm-field" value="" />',
            '</div>',
            '<table width="100%">',
            '<tr>',
            '<td>', // LEFT TABLE
            '<table>',
            '<tr>',
            '<td><label for="pm-type">' + _("Type") + '</label></td>',
            '<td><select id="pm-type" data="type" class="asm-selectbox asm-field">',
            '</select></td>',
            '</tr>',
            '<tr>',
            '<td><label for="pm-method">' + _("Method") + '</label></td>',
            '<td><select id="pm-method" data="payment" class="asm-selectbox asm-field">',
            '</select></td>',
            '</tr>',
            '<tr>',
            '<td><label for="pm-due">' + _("Due") + '</label></td>',
            '<td><input id="pm-due" data="due" type="text" class="asm-textbox asm-datebox asm-field" /></td>',
            '</tr>',
            '<tr>',
            '<td><label for="pm-received">' + _("Received") + '</label></td>',
            '<td><input id="pm-received" data="received" type="text" class="asm-textbox asm-datebox asm-field" /></td>',
            '</tr>',
            '<tr>',
            '<td><label for="pm-amount">' + _("Amount") + '</label></td>',
            '<td><input id="pm-amount" data="amount" type="text" class="asm-textbox asm-currencybox asm-field" /></td>',
            '</tr>',
            '<tr>',
            '<td></td>',
            '<td><input id="pm-vat" data="vat" type="checkbox" class="asm-checkbox asm-field" /> <label for="pm-vat">' + _("Sales Tax") + '</label></td>',
            '</tr>',

            '<tr class="paymentsalestax">',
            '<td><label for="pm-vatratechoice">' + _("Tax Rate") + '</label></td>',
            '<td><select id="pm-vatratechoice" data="vatratechoice" class="asm-selectbox" /></select></td>',
            '</tr>',

            '<tr style="display: none;">',
            '<td><label for="pm-vatrate">' + _("Tax Rate %") + '</label></td>',
            '<td><input id="pm-vatrate" data="vatrate" type="text" class="asm-numberbox asm-field" /></td>',
            '</tr>',
            '<tr class="paymentsalestax">',
            '<td><label for="pm-vatamount">' + _("Tax Amount") + '</label></td>',
            '<td><input id="pm-vatamount" data="vatamount" type="text" class="asm-currencybox asm-textbox asm-field" /></td>',
            '</tr>',
            '</table>',
            '</td>',
            '<td>', // RIGHT TABLE
            '<table>',
            '<tr>',
            '<td><label for="pm-comments">' + _("Comments") + ' </label></td>',
            '<td><textarea id="pm-comments" data="comments" class="asm-textarea asm-field" rows="5"></textarea></td>',
            '</table>',
            '</td>',
            '</tr>',
            '</table>',
            '</div>'
        ].join("\n"));
        $("#pm-due, #pm-received").date();
        $("#pm-amount, #pm-vatamount").currency();
        let b = {}; 
        b[_("Create Payment")] = {
            text: _("Create Payment"),
            "class": "asm-dialog-actionbutton",
            click: function() {
                validate.reset("dialog-payment");
                if (!validate.notblank(["pm-due"])) { return; }
                let o = t.data("o");
                let formdata = "mode=create&";
                formdata += $("#dialog-payment .asm-field").toPOST();
                header.show_loading(_("Creating..."));
                common.ajax_post("donation", formdata, function(receipt) {
                    header.show_info( common.sub_arr(_("Payment {0} created for {1}"), 
                        [ receipt.split("|")[1], '<a href="person_donations?id=' + o.personid + '">' + o.personname + '</a>' ]) );
                    $("#dialog-payment").dialog("close");
                });
            }
        };
        b[_("Cancel")] = function() { $(this).dialog("close"); };
        $("#dialog-payment").dialog({
                autoOpen: false,
                resizable: false,
                modal: true,
                dialogClass: "dialogshadow",
                width: 650,
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: b
        });
        $("#pm-vat").change(function() {
            if ($(this).is(":checked")) {
                if (config.bool("VATExclusive")) {
                    $("#pm-vatamount").currency("value", common.tax_from_exclusive($("#pm-amount").currency("value"), $("#pm-vatrate").val()));
                    $("#pm-amount").currency("value", $("#pm-amount").currency("value") + $("#pm-vatamount").currency("value"));
                }
                else {
                    $("#pm-vatamount").currency("value", common.tax_from_inclusive($("#pm-amount").currency("value"), $("#pm-vatrate").val()));
                }
                $("#dialog-payment .paymentsalestax").fadeIn();
            } else {
                $("#pm-vatamount").currency("value", "0");
                $("#pm-vatrate").val("0"); 
                $("#dialog-payment .paymentsalestax").fadeOut();
            }
        });
        // NOTE: Trigger recalculating the vat on amount change - but only if the amount is inclusive of VAT
        // otherwise, the amount will keep going up with each recalculation
        $("#pm-amount").change(function() {
            if (!config.bool("VATExclusive")) { $("#pm-vat").change(); }
        });
        $("#pm-vatratechoice").change(function() {
            $("#pm-vatrate").val($("#pm-vatratechoice").val().split("|")[1]);
            $("#pm-vat").change();
        });
    },

    destroy: function(t) {
        common.widget_destroy("#dialog-payment", "dialog"); 
    },
    
    /**
     * Shows the create payment dialog.
     * title:      The dialog title (optional: Create Payment)
     * animalid:   Animal ID
     * personid:   Person ID
     * personname: Person name
     * donationtypes: The donationtypes lookup
     * paymentmethods: The paymentmethods lookup
     * chosentype: The default payment type to choose (optional, AFDefaultDonationType if not given)
     * chosenmethod: The default payment method to choose (optional, AFDefaultPaymentMethod if not given)
     * amount:     The amount of the payment (integer money expected)
     * vat:        (bool) whether we should have vat on or not
     * vatrate:    The vat rate (optional, configured amount used if not set)
     * vatamount:  The vat amount
     * comments:   Any comments for the payment
     *    Eg: show({ amount: 5000, vat: false })
     */
    show: function(t, o) {
        t.data("o", o);
        $("#dialog-payment").dialog("option", "title", o.title || _("Create Payment"));
        $("#pm-animal").val(o.animalid);
        $("#pm-person").val(o.personid);
        $("#pm-type").html( html.list_to_options(o.donationtypes, "ID", "DONATIONNAME") );
        $("#pm-type").select("removeRetiredOptions", "all");
        $("#pm-type").select("value", o.chosentype || config.integer("AFDefaultDonationType")); 
        $("#pm-method").html( html.list_to_options(o.paymentmethods, "ID", "PAYMENTNAME") );
        $("#pm-method").select("removeRetiredOptions", "all");
        $("#pm-method").select("value", o.chosenmethod || config.integer("AFDefaultPaymentMethod")); 
        $("#pm-amount").currency("value", o.amount || 0);
        $("#pm-vat").prop("checked", o.vat);
        $("#pm-vatrate").val( o.vatrate || config.number("VATRate") );
        $("#pm-vatamount").currency("value", o.vatamount || 0);
        $("#pm-comments").html( o.comments );
        $("#pm-due").date("today");
        $("#pm-vat").change();
        let vatrates = [];
        let defaulttaxrateval = "";
        $.each(o.taxrates, function(i, taxrate) {
            let optval = taxrate.ID + "|" + taxrate.TAXRATE;
            if (taxrate.ID == config.integer("AFDefaultTaxRate")) {
                defaulttaxrateval = optval;
            }
            vatrates.push({ID: optval, TAXRATENAME: taxrate.TAXRATENAME});
        });
        let vatrateoptions = html.list_to_options(vatrates, "ID", "TAXRATENAME" );
        $("#pm-vatratechoice").html(vatrateoptions);
        if (defaulttaxrateval != "") {
            $("#pm-vatratechoice").val(defaulttaxrateval);
        }
        $("#pm-vat").change();
        $("#pm-vatratechoice").change();
        $("#dialog-payment").dialog("open");
    }
});


/**
 * Widget to manage a dialog that allows sending of an email.
 * Target should be a div to contain the hidden dialog.
 */
$.fn.emailform = asm_widget({

    _create: function(t) {
        t.append([
            '<div id="dialog-email" style="display: none" title="' + html.title(_("Email person"))  + '">',
            '<table width="100%">',
            '<tr>',
            '<td><label for="em-from">' + _("From") + '</label></td>',
            '<td><input id="em-from" data="from" type="text" class="asm-doubletextbox" autocomplete="new-password" /></td>',
            '</tr>',
            '<tr>',
            '<td><label for="em-to">' + _("To") + '</label></td>',
            '<td><input id="em-to" data="to" type="text" class="asm-doubletextbox" autocomplete="new-password" /></td>',
            '</tr>',
            '<tr>',
            '<td><label for="em-cc">' + _("CC") + '</label></td>',
            '<td><input id="em-cc" data="cc" type="text" class="asm-doubletextbox" autocomplete="new-password" /></td>',
            '</tr>',
            '<tr>',
            '<td><label for="em-bcc">' + _("BCC") + '</label></td>',
            '<td><input id="em-bcc" data="bcc" type="text" class="asm-doubletextbox" autocomplete="new-password" /></td>',
            '</tr>',
            '<tr>',
            '<td><label for="em-subject">' + _("Subject") + '</label></td>',
            '<td><input id="em-subject" data="subject" type="text" class="asm-doubletextbox" /></td>',
            '</tr>',
            '<tr id="em-attachmentrow">',
            '<td><label for="em-attachments">' + _("Attachments") + '</label></td>',
            '<td><span id="em-attachments" data="attachments" type="text" class="strong"></span></td>',
            '</tr>',
            '<tr id="em-docreporow">',
            '<td><label for="em-docrepo">' + _("Document Repository") + '</label></td>',
            '<td>',
            '<select id="em-docrepo" data="docrepo" multiple="multiple" class="asm-selectmulti" title="' + _("Select") + '">',
            '</select>',
            '</td>',
            '</tr>',
            '<tr>',
            '<td></td>',
            '<td><input id="em-addtolog" data="addtolog" type="checkbox"',
            'title="' + html.title(_("Add details of this email to the log after sending")) + '" ',
            'class="asm-checkbox" /><label for="emailaddtolog">' + _("Add to log") + '</label>',
            '<select id="em-logtype" data="logtype" class="asm-selectbox">',
            '</select>',
            '</td>',
            '</tr>',
            '</table>',
            '<div id="em-body" data="body" data-margin-top="24px" data-height="300px" class="asm-richtextarea"></div>',
            '<p>',
            '<label for="em-template">' + _("Template") + '</label>',
            '<select id="em-template" class="asm-selectbox">',
            '<option value=""></option>',
            '</select>',
            '</p>',
            '</div>'
        ].join("\n"));
        if ( config.bool("AuditOnSendEmail"))
        $("#em-body").richtextarea();
        $("#em-logtype, #em-template").select();
        $("#em-docrepo").asmSelect({
            animate: true,
            sortable: true,
            removeLabel: '<strong>&times;</strong>',
            listClass: 'bsmList-custom',  
            listItemClass: 'bsmListItem-custom',
            listItemLabelClass: 'bsmListItemLabel-custom',
            removeClass: 'bsmListItemRemove-custom'
        });
        let b = {}; 
        b[_("Send")] = {
            text: _("Send"),
            "class": "asm-dialog-actionbutton",
            click: function() {
                validate.reset("dialog-email");
                if (!validate.notblank(["em-from", "em-to"])) { return; }
                if (!validate.validemail(["em-from", "em-to"])) { return; }
                if ($("#em-cc").val() != "" && !validate.validemail(["em-cc"])) { return; }
                if ($("#em-bcc").val() != "" && !validate.validemail(["em-bcc"])) { return; }
                let o = t.data("o");
                if (o.formdata) { o.formdata += "&"; }
                o.formdata += $("#dialog-email input, #dialog-email select, #dialog-email .asm-richtextarea").toPOST();
                header.show_loading(_("Sending..."));
                common.ajax_post(o.post, o.formdata, function() {
                    let recipients = $("#em-to").val();
                    if ($("#em-cc").val() != "") { recipients += ", " + $("#em-cc").val(); }
                    header.show_info(_("Message successfully sent to {0}").replace("{0}", recipients));
                    $("#dialog-email").dialog("close");
                });
            }
        };
        b[_("Cancel")] = function() { $(this).dialog("close"); };
        $("#dialog-email").dialog({
                autoOpen: false,
                resizable: false,
                modal: true,
                dialogClass: "dialogshadow",
                width: 640,
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: b
        });
        $("#em-template").change(function() {
            let o = t.data("o");
            let formdata = "mode=emailtemplate&dtid=" + $("#em-template").val();
            if (o.animalcontrolid) { formdata += "&animalcontrolid=" + o.animalcontrolid; }
            if (o.licenceid) { formdata += "&licenceid=" + o.licenceid; }
            if (o.donationids) { formdata += "&donationids=" + o.donationids; }
            if (o.personid) { formdata += "&personid=" + o.personid; }
            if (o.animalid) { formdata += "&animalid=" + o.animalid; }
            header.show_loading(_("Loading..."));
            common.ajax_post("document_gen", formdata, function(response) {
                let j = jQuery.parseJSON(response);
                let link = '<a target="blank" href="' + o.url + '">' + o.urltext + '</a>';
                if (j.BODY.indexOf("$URL") == -1 && o.url) { j.BODY = j.BODY += link; }
                if (j.BODY.indexOf("$URL") != -1 && o.url) { j.BODY = j.BODY.replace("$URL", link); }
                if (j.TO) { $("#em-to").val(j.TO); }
                if (j.SUBJECT) { $("#em-subject").val(j.SUBJECT); }
                if (j.FROM) { $("#em-from").val(j.FROM); }
                if (j.CC) { $("#em-cc").val(j.CC); }
                if (j.BCC) { $("#em-bcc").val(j.BCC); }
                $("#em-body").html(j.BODY); 
            });
        });

    },

    destroy: function(t) {
        common.widget_destroy("#em-body", "richtextarea");
        common.widget_destroy("#dialog-email", "dialog"); 
    },
    
    /**
     * Shows the email dialog.
     * title:      The dialog title (optional: Email person)
     * post:       The ajax post target
     * formdata:   The first portion of the formdata
     * name:       The name to show on the form (optional)
     * email:      The email(s) to show on the form (optional)
     * bccemail:   The bcc email(s) to show on the form (optional)
     * subject:    The default subject (optional)
     * message:    The default message (optional)
     * logtypes:   The logtypes to populate the attach as log box (optional)
     * templates:  The list of email document templates (optional)
     * personid:   A person to substitute tokens in templates for (optional)
     * animalid:   An animal to substitute tokens in templates for (optional)
     *    Eg: show({ post: "person", formdata: "mode=email&personid=52", name: "Bob Smith", email: "bob@smith.com" })
     */
    show: function(t, o) {
        t.data("o", o);
        $("#dialog-email").dialog("option", "title", o.title || _("Email person"));
        $("#dialog-email").dialog("open");
        if (o.logtypes) {
            $("#em-logtype").html( html.list_to_options(o.logtypes, "ID", "LOGTYPENAME") );
            $("#em-logtype").select("removeRetiredOptions", "all");
            $("#em-logtype").select("value", config.integer("AFDefaultLogType"));
        }
        else {
            $("#em-logtype").closest("tr").hide();
        }
        if (o.templates) {
            $("#em-template").html( edit_header.template_list_options(o.templates) );
        }
        else {
            $("#em-template").closest("tr").hide();
        }
        let fromaddresses = [], toaddresses = [];
        let conf_org = html.decode(config.str("Organisation").replace(",", ""));
        let conf_email = config.str("EmailAddress");
        let org_email = conf_org + " <" + conf_email + ">";
        let bcc_email = config.str("EmailBCC");
        $("#em-from").val(conf_email);
        fromaddresses.push(conf_email);
        fromaddresses.push(org_email);
        if (asm.useremail) {
            fromaddresses.push(asm.useremail);
            fromaddresses.push(html.decode(asm.userreal) + " <" + asm.useremail + ">");
            if (config.bool(asm.user + "_EmailDefault")) {
                $("#em-from").val(asm.useremail);
            }
        }
        if (bcc_email) {
            $("#em-bcc").val(bcc_email);
        }
        if (o.toaddresses) {
            toaddresses = toaddresses.concat(o.toaddresses);
        }
        if (o.attachments) {
            $("#em-attachments").html(o.attachments);
            $("#em-attachmentrow").show();
        }
        else {
            $("#em-attachmentrow").hide();
        }
        if (o.documentrepository) {
            $("#em-docrepo").html(html.list_to_options(o.documentrepository, "ID", "NAME"));
            $("#em-docrepo").change();
            $("#em-docreporow").show();
        }
        else {
            $("#em-docreporow").hide();
        }
        fromaddresses = fromaddresses.concat(html.decode(config.str("EmailFromAddresses")).split(","));
        toaddresses = toaddresses.concat(html.decode(config.str("EmailToAddresses")).split(","));
        const add_address = function(n, s) {
            // build a list of valid existing addresses in the textbox (n: node) so far, then add the new one (s: String)
            let existing = [], xs = String(n.val());
            $.each(xs.split(","), function(i, v) {
                if (validate.email(v) && common.trim(v) != s) { existing.push(common.trim(v)); }
            });
            existing.push(s);
            n.val(existing.join(", "));
        };
        $("#em-from").autocomplete({source: fromaddresses});
        $("#em-from").autocomplete("widget").css("z-index", 1000);
        $("#em-to").autocomplete({source: toaddresses});
        $("#em-to").autocomplete("widget").css("z-index", 1000);
        $("#em-to").on("autocompleteselect", function(event, ui) { add_address($("#em-to"), ui.item.value); return false; });
        $("#em-cc").autocomplete({source: toaddresses});
        $("#em-cc").autocomplete("widget").css("z-index", 1000);
        $("#em-cc").on("autocompleteselect", function(event, ui) { add_address($("#em-cc"), ui.item.value); return false; });
        $("#em-bcc").autocomplete({source: toaddresses});
        $("#em-bcc").autocomplete("widget").css("z-index", 1000);
        $("#em-bcc").on("autocompleteselect", function(event, ui) { add_address($("#em-bcc"), ui.item.value); return false; });
        $("#em-from, #em-to, #em-cc, #em-bcc").bind("focus", function() {
            $(this).autocomplete("search", "@");
        });
        if (o.email && o.email.indexOf(",") != -1) { 
            // If there's more than one email address, only output the comma separated emails
            $("#em-to").val(o.email); 
        }
        else if (o.email) { 
            // Otherwise, use RFC821
            $("#em-to").val(common.replace_all(html.decode(o.name), ",", "") + " <" + o.email + ">"); 
        }
        if (o.bccemail) {
            $("#em-bcc").val(o.bccemail);
        }
        let msg = "";
        if (o.message) { 
            msg = "<p>" + o.message + "</p>" + msg; 
        }
        else { 
            msg = "<p>&nbsp;</p>" + msg; 
        }
        if (o.url) {
            msg += '<p><a target="blank" href="' + o.url + '">' + o.urltext + '</a></p>';
        }
        msg += config.str("EmailSignature");
        if (msg) {
            $("#em-body").richtextarea("value", msg);
        }
        if (o.subject) {
            $("#em-subject").val(o.subject); 
        }
        if (config.bool("LogEmailByDefault")) {
            $("#em-addtolog").prop("checked", true);
        } else {
            $("#em-addtolog").prop("checked", false);
        }
        // If a default email log type has been chosen and exists in the list, select it 
        if ($("#em-logtype option[value='" + config.integer("EmailLogType") + "']").length > 0) {
            $("#em-logtype").val(config.integer("EmailLogType"));
        }
        $("#em-subject").focus();
    }
});


/**
 * Widget to allow entry of one or more payments.
 * Relies on controller.accounts, controller.paymentmethods and controller.donationtypes
 * target should be a container div.
 * This is mainly used by Financial->Receive payment, and the Move-> screens 
 * to add payments at the same time as a movement.
 */
$.fn.payments = asm_widget({

    options: {
        controller: null,
    },

    _create: function(t, options) {
        let self = this;
        // If the user does not have permission to add payments, do nothing
        if (!common.has_permission("oaod")) { return; }
        let o = { controller: options.controller, count: 0, giftaid: false };
        t.data("o", o);
        t.append([
            html.content_header(_("Payment"), true),
            '<table class="asm-table-layout">',
            '<thead>',
            '<tr>',
            '<th>' + _("Type") + '</th>',
            '<th class="overridedates">' + _("Due") + '</th>',
            '<th class="overridedates">' + _("Received") + '</th>',
            '<th>' + _("Method") + '</th>',
            '<th>' + _("Check No") + '</th>',
            '<th class="quantities">' + _("Quantity") + '</th>',
            '<th class="quantities">' + _("Unit Price") + '</th>',
            '<th>' + _("Amount") + '</th>',
            '<th class="overrideaccount">' + _("Deposit Account") + '</th>',
            '<th class="giftaid">' + _("Gift Aid") + '</th>',
            '<th class="vat">' + _("Sales Tax") + '</th>',
            '<th>' + _("Comments") + '</th>',
            '</tr>',
            '</thead>',
            '<tbody id="paymentlines">',
            '</tbody>',
            '<tfoot id="paymenttotals">',
            '<tr>',
            '<td colspan="3"><button class="takepayment">' + _("Take another payment") + '</button>',
            '<a class="takepayment" href="#">' + _("Take another payment") + '</a></td>',
            '<td class="overridedates"></td>',
            '<td class="overridedates"></td>',
            //'<td></td>',
            //'<td></td>',
            '<td class="quantities"></td>',
            '<td class="quantities"></td>',
            '<td class="rightalign strong" id="totalamount"></td>',
            '<td class="overrideaccount"></td>',
            '<td class="giftaid"></td>',
            '<td class="vat rightalign strong" id="totalvat"></td>',
            '<td></td>',
            '</tr>',
            '</tfoot>',
            '</table>',
            html.content_footer()
        ].join("\n"));
        self.add_payment(t);
        $("button.takepayment")
            .button({ icons: { primary: "ui-icon-circle-plus" }, text: false })
            .click(function() {
            self.add_payment(t);
        });
        t.find("a.takepayment").click(function() {
            self.add_payment(t);
            return false;
        });
    },

    add_payment: function(t) {
        let o = t.data("o");
        let h = [
            '<tr>',
            '<td>',
            '<select id="donationtype{i}" data="donationtype{i}" class="asm-selectbox asm-halfselectbox">',
            html.list_to_options(o.controller.donationtypes, "ID", "DONATIONNAME"),
            '</select>',
            '</td>',
            '<td class="overridedates">',
            '<input id="due{i}" data="due{i}" class="asm-datebox asm-textbox asm-halftextbox" />',
            '</td>',
            '<td class="overridedates">',
            '<input id="received{i}" data="received{i}" class="asm-datebox asm-textbox asm-halftextbox" />',
            '</td>',
            '<td>',
            '<select id="payment{i}" data="payment{i}" class="asm-halfselectbox">',
            html.list_to_options(o.controller.paymentmethods, "ID", "PAYMENTNAME"),
            '</select>',
            '</td>',
            '<td>',
            '<input id="chequenumber{i}" data="chequenumber{i}" class="asm-textbox asm-halftextbox" />',
            '</td>',
            '<td class="quantities">',
            '<input id="quantity{i}" data="quantity{i}" class="rightalign asm-numberbox asm-textbox asm-halftextbox" value="1" />',
            '</td>',
            '<td class="quantities">',
            '<input id="unitprice{i}" data="unitprice{i}" class="rightalign unitprice asm-currencybox asm-textbox asm-halftextbox" value="0" />',
            '</td>',
            '<td>',
            '<input id="amount{i}" data="amount{i}" class="rightalign amount asm-currencybox asm-textbox asm-halftextbox" />',
            '</td>',
            '<td class="overrideaccount">',
            '<select id="destaccount{i}" data="destaccount{i}" class="asm-selectbox asm-halfselectbox">',
            html.list_to_options(o.controller.accounts, "ID", "CODE"),
            '</select>',
            '</td>',
            '<td class="giftaid centered">',
            '<input id="giftaid{i}" data="giftaid{i}" type="checkbox" class="asm-checkbox"',
            (o.giftaid ? ' checked="checked"' : '') + ' />',
            '</td>',
            '<td class="vat centered nowrap">',
            '<input id="vat{i}" data="vat{i}" type="checkbox" class="asm-checkbox" />',
            '<span id="vatboxes{i}" style="display: none">',
            '<select id="vatratechoice{i}" data="vatratechoice{i}" class="asm-selectbox asm-halfselectbox">',
            html.list_to_options(o.controller.taxrates, "ID", "TAXRATENAME"),
            '</select>',
            '<input id="vatrate{i}" data="vatrate{i}" class="rightalign asm-textbox asm-halftextbox asm-numberbox" value="0" style="display: none;" />',
            '<input id="vatamount{i}" data="vatamount{i}" class="rightalign vatamount asm-textbox asm-halftextbox asm-currencybox" value="0" />',
            '</span>',
            '</td>',
            '<td>',
            '<input id="comments{i}" data="comments{i}" class="asm-textbox" />',
            '</td>',
            '</tr>'
        ];
        // Construct and add our new payment fields to the DOM
        o.count += 1;
        let i = o.count, self = this;
        t.find("#paymentlines").append(common.substitute(h.join("\n"), {
            i: o.count
        }));
        // Remove any retired payment types and methods
        $("#donationtype" + i).select("removeRetiredOptions", "all");
        $("#payment" + i).select("removeRetiredOptions", "all");
        // Change the default amount when the payment type changes
        $("#donationtype" + i).change(function() {
            let dc = common.get_field(o.controller.donationtypes, $("#donationtype" + i).select("value"), "DEFAULTCOST");
            let dv = common.get_field(o.controller.donationtypes, $("#donationtype" + i).select("value"), "ISVAT");
            $("#quantity" + i).val("1");
            $("#unitprice" + i).currency("value", dc);
            $("#amount" + i).currency("value", dc);
            $("#vatratechoice" + i).val(config.number("AFDefaultTaxRate")); // triggers change
            $("#vat" + i).prop("checked", dv == 1);
            $("#vat" + i).change();
            self.update_totals(t);
        });
        // Recalculate when quantity or unit price changes
        $("#quantity" + i + ", #unitprice" + i).change(function() {
            let q = $("#quantity" + i).val(), u = $("#unitprice" + i).currency("value");
            $("#amount" + i).currency("value", q * u);
            self.update_totals(t);
        });
        // Recalculate when amount or VAT changes
        $("#amount" + i).change(function() {
            self.update_totals(t);
        });
        // Recalculate vat when taxrate select is changed
        $("#vatratechoice" + i).change(function() {
            let taxrate = 0.0;
            taxrate = common.get_field(o.controller.taxrates, $("#vatratechoice" + i).val(), "TAXRATE");
            $("#vatrate" + i).val(taxrate);
            self.update_vat(t, i, true);
            self.update_totals(t);
        });
        // Clicking the VAT checkbox enables and disables the rate/amount fields with defaults
        $("#vat" + i).change(function() {
            if ($(this).is(":checked")) {
                $("#vatratechoice" + i).val(config.number("AFDefaultTaxRate"));
                $("#vatratechoice" + i).change();
                $("#vatboxes" + i).fadeIn();
            }
            else {
                $("#vatrate" + i + ", #vatamount" + i).val("0");
                $("#vatboxes" + i).fadeOut();
            }
            self.update_totals(t);
        });
        // Set the default for our new payment type
        $("#donationtype" + i).val(config.str("AFDefaultDonationType")).change();
        $("#donationtype" + i).change();
        // Payment method
        $("#payment" + i).val(config.str("AFDefaultPaymentMethod"));
        // If we're creating accounting transactions and the override
        // option is set, allow override of the destination account
        if (config.bool("CreateDonationTrx") && config.bool("DonationTrxOverride")) {
            $(".overrideaccount").show();
            // Set it to the default account
            $("#destaccount" + i).val(config.str("DonationTargetAccount"));
        }
        else {
            $(".overrideaccount").hide();
        }
        // Gift aid only applies to the UK
        if (asm.locale != "en_GB") { $(".giftaid").hide(); }
        // Disable vat/tax if the option is off necessary
        if (!config.bool("VATEnabled")) { $(".vat").hide(); }
        // Disable quantity/unit price if the option is off
        if (!config.bool("DonationQuantities")) { $(".quantities").hide(); }
        // Disable dates if the option is off
        if (!config.bool("DonationDateOverride")) { 
            $(".overridedates").hide(); 
        }
        else {
            // Set due or received date to today if the date override is on
            if (config.bool("MovementDonationsDefaultDue")) {
                $("#due" + i).val(format.date(new Date()));
            }
            else {
                $("#received" + i).val(format.date(new Date()));
            }
            // Make sure the dates are turned into picker widgets
            $("#due" + i).date();
            $("#received" + i).date();
        }
    },

    set_giftaid: function(t, b) {
        let o = t.data("o");
        o.giftaid = b;
    },

    update_totals: function(t) {
        let totalamt = 0, totalvat = 0, totalall = 0;
        $(".amount").each(function() {
            totalamt += $(this).currency("value");
        });
        $(".vatamount").each(function() {
            totalvat += $(this).currency("value");
        });
        $("#totalamount").html(format.currency(totalamt));
        $("#totalvat").html(format.currency(totalvat));
    },

    update_vat: function(t, i, update_amount) {
        // Calculates the vatamount field. If update_amount is true, and vatexclusive is off, adds the vat to the amount
        if (config.bool("VATExclusive")) {
            $("#vatamount" + i).currency("value", 
                common.tax_from_exclusive($("#amount" + i).currency("value"), format.to_float($("#vatrate" + i).val())));
            if (update_amount === undefined || update_amount === true) {
                $("#amount" + i).currency("value", $("#amount" + i).currency("value") + $("#vatamount" + i).currency("value"));
            }
        }
        else {
            $("#vatamount" + i).currency("value", 
                common.tax_from_inclusive($("#amount" + i).currency("value"), format.to_float($("#vatrate" + i).val())));
        }
    },

});
