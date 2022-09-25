/*global $, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const accounts_trx = {

        render: function() {
            return [
                '<div id="dialog-edit" style="display: none" title="' + html.title(_("Edit transaction")) + '">',
                '<input type="hidden" id="trxid" />',
                '<table width="100%">',
                '<tr>',
                '<td><label for="description">' + _("Description") + '</label></td>',
                '<td><input id="description" data="description" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="trxdate">' + _("Date") + '</label></td>',
                '<td><input id="trxdate" data="trxdate" class="asm-textbox asm-datebox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="reconciled">' + _("Reconciled") + '</label></td>',
                '<td><select id="reconciled" data="reconciled" class="asm-selectbox">',
                '<option value="0">' + _("Not reconciled") + '</option>',
                '<option value="1">' + _("Reconciled") + '</option>',
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Account") + '</td>',
                '<td><span id="thisaccount">' + controller.accountcode + '</span></td>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="otheraccount">' + _("Other Account") + '</label></td>',
                '<td><input id="otheraccount" data="otheraccount" class="asm-textbox" /></td>',
                '</tr>',
                '<tr id="paymentrow">',
                '<td><label for="person">' + _("Payment From") + '</label></td>',
                '<td>',
                '<a id="personlink" class="asm-embed-name" href="#"></a> ' + html.icon("right"),
                '<a id="animallink" class="asm-embed-name" href="#"></a>',
                '[<span id="receiptno"></span>]',
                '</td>',
                '</tr>',
                '<tr id="costrow">',
                '<td><label for="costanimallink">' + _("Cost For") + '</label></td>',
                '<td>',
                '<a id="costanimallink" class="asm-embed-name" href="#"></a>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="deposit">' + _("Credit") + '</label></td>',
                '<td><input id="deposit" data="deposit" class="asm-textbox asm-currencybox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="withdrawal">' + _("Debit") + '</label></td>',
                '<td><input id="withdrawal" data="withdrawal" class="asm-textbox asm-currencybox" /></td>',
                '</tr>',
                '</table>',
                '</div>',
                html.content_header(_("Transactions") + " - " + controller.accountcode),
                '<input type="hidden" id="accountid" data="accountid" value="' + controller.accountid + '" />',
                '<table width="100%">',
                '<tr>',
                '<td>' + _("Show transactions from") + '</td>',
                '<td><input id="fromdate" data="fromdate" type="text" class="asm-textbox asm-datebox" /></td>',
                '<td>' + _("to") + '</td>',
                '<td><input id="todate" data="todate" type="text" class="asm-textbox asm-datebox" /></td>',
                '<td>' + _("Reconciled") + '</td>',
                '<td><select id="recfilter" data="recfilter" class="asm-selectbox">',
                '<option value="0">' + _("Both") + '</option>',
                '<option value="1">' + _("Reconciled") + '</option>',
                '<option value="2">' + _("Not Reconciled") + '</option>',
                '</select></td>',
                '<td><button id="button-refresh">' + html.icon("refresh") + ' ' + _("Refresh") + '</button></td>',
                '</tr>',
                '</table>',
                tableform.buttons_render([
                    { id: "delete", text: _("Delete"), icon: "delete" },
                    { id: "reconcile", text: _("Reconcile"), icon: "transactions" }
                ]),
                '<table id="table-trx" width="100%">',
                '<thead>',
                '<tr>',
                '<th class="left">' + _("Date") + '</th>',
                '<th class="left">' + _("R") + '</th>',
                '<th class="left">' + _("Description") + '</th>',
                '<th class="left">' + _("Account") + '</th>',
                '<th class="right">' + _("Credit") + '</th>',
                '<th class="right">' + _("Debit") + '</th>',
                '<th class="right">' + _("Balance") + '</th>',
                '</tr>',
                '</thead>',
                '<tbody>',
                this.render_tablebody(),
                '<tr>',
                '<td class="newrow left"><input id="newtrxdate" data="trxdate" type="text" class="asm-halftextbox asm-datebox" />',
                '<input id="newaccountid" data="accountid" type="hidden" value="' + controller.accountid + '" />',
                '</td>',
                '<td class="newrow left"><input id="newreconciled" data="reconciled" type="checkbox" class="asm-checkbox" /></td>',
                '<td class="newrow left"><input id="newdesc" data="description" type="text" class="asm-textbox" /></td>',
                '<td class="newrow left"><input id="newacc" data="otheraccount" class="asm-textbox" /></td>',
                '<td class="newrow right"><input id="newdeposit" data="deposit" type="text" class="asm-halftextbox asm-currencybox" /></td>',
                '<td class="newrow right"><input id="newwithdrawal" data="withdrawal" type="text" class="asm-halftextbox asm-currencybox" /></td>',
                '<td class="newrow right"><button id="button-add">' + html.icon("new") + ' ' + _("Add") + '</button></td>',
                '</tr>',
                '</tbody>',
                '</table>',
                html.content_footer(),
                '<div id="spacer" style="height: 100px"></div>'
            ].join("\n");
        },

        render_tablebody: function() {
            let h = [],
                tdc = "even",
                futuredrawn = false,
                reconciled = "",
                desc = "";
            $.each(controller.rows, function(i, t) {
                tdc = (tdc == "even" ? "odd" : "even");
                if (format.date_js(t.TRXDATE) > new Date() && !futuredrawn) {
                    tdc += " future";
                    futuredrawn = true;
                }
                if (t.RECONCILED == 1) {
                    reconciled = _("R");
                }
                else {
                    reconciled = "";
                }
                desc = "";
                if (t.PERSONNAME) {
                    desc += html.person_link(t.PERSONID, t.PERSONNAME);
                }
                if (t.DONATIONANIMALID) {
                    desc += " " + html.icon("right") + " " + 
                        '<a href="animal?id=' + t.DONATIONANIMALID + '">' +
                        t.DONATIONANIMALCODE + " - " + 
                        t.DONATIONANIMALNAME + '</a>';
                }
                if (t.DONATIONRECEIPTNUMBER) {
                    desc += " [" + t.DONATIONRECEIPTNUMBER + "]";
                }
                desc = html.truncate(t.DESCRIPTION) + " " + desc;
                h.push("<tr>");
                h.push('<td class="' + tdc + ' left">');
                h.push('<span style="white-space: nowrap">');
                h.push('<input type="checkbox" data="' + t.ID + '" title="' + _('Select') + '" />');
                h.push('<a href="#" class="trx-edit-link asm-embed-name" data-id="' + t.ID + '">' + format.date(t.TRXDATE) + '</a>');
                h.push('</span>');
                h.push('</td>');
                h.push('<td class="' + tdc + ' left">' + reconciled + '</td>');
                h.push('<td class="' + tdc + ' left">' + desc + '</td>');
                h.push('<td class="' + tdc + ' left">' + t.OTHERACCOUNTCODE + '</td>');
                h.push('<td class="right ' + tdc + '">' + format.currency(t.DEPOSIT) + '</td>');
                h.push('<td class="right ' + tdc + '">' + format.currency(t.WITHDRAWAL) + '</td>');
                h.push('<td class="right ' + tdc + '">' + format.currency(t.BALANCE) + '</td>');
                h.push('</tr>');
            });
            return h.join("\n");
        },

        reload: function() {
            common.route_reload();
        },

        bind: function() {
            const validate_account = function(selector) {
                // Returns true if the value of $(selector) is a valid account code
                let v = $(selector).val(),
                    codes = html.decode(controller.codes).split("|"),
                    validcode;
                $.each(codes, function(i, c) {
                    if (c == v) {
                        validcode = v;
                        return false;
                    }
                });
                if (validcode) {
                    return true;
                }
                $(selector).focus();
                header.show_error(String(_("Account code '{0}' is not valid.").replace("{0}", v)));
                return false;
            };

            $("#table-trx input:checkbox").change(function() {
                if ($("#table-trx input:checked").length > 0) {
                    $("#button-delete").button("option", "disabled", false); 
                    $("#button-reconcile").button("option", "disabled", false); 
                }
                else {
                    $("#button-delete").button("option", "disabled", true); 
                    $("#button-reconcile").button("option", "disabled", true); 
                }
                if ($(this).is(":checked")) {
                    $(this).closest("tr").find("td").addClass("highlight");
                }
                else {
                    $(this).closest("tr").find("td").removeClass("highlight");
                }
            });

            validate.indicator(["trxdate", "otheraccount", "description", "deposit", "withdrawal"]);

            let editbuttons = { };
            editbuttons[_("Save")] = async function() {
                validate.reset();
                if (!validate_account("#otheraccount")) { return; }
                if (!validate.notblank([ "trxdate", "otheraccount", "description", "deposit", "withdrawal" ])) { return; }
                let formdata = "mode=update&trxid=" + $("#trxid").val() + "&accountid=" + controller.accountid + "&" +
                    $("#dialog-edit input, #dialog-edit select").toPOST();
                $("#dialog-edit").disable_dialog_buttons();
                try {
                    await common.ajax_post("accounts_trx", formdata);
                    accounts_trx.reload();
                }
                finally {
                    $("#dialog-edit").dialog("close");
                }
            };
            editbuttons[_("Cancel")] = function() {
                $("#dialog-edit").dialog("close");
            };

            $("#dialog-edit").dialog({
                autoOpen: false,
                modal: true,
                width: 550,
                dialogClass: "dialogshadow",
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: editbuttons
            });

            $("#button-reconcile").button({disabled: true}).click(async function() {
                $("#button-reconcile").button("disable");
                let formdata = "mode=reconcile&ids=" + $("#table-trx input").tableCheckedData();
                await common.ajax_post("accounts_trx", formdata);
                accounts_trx.reload();
            });

            $("#button-refresh").button().click(function() {
                common.route("accounts_trx?" + $("#fromdate, #todate, #recfilter, #accountid").toPOST());
            });

            $("#button-add").button().click(async function() {
                if (!validate_account("#newacc")) { return; }
                if (!validate.notblank([ "newtrxdate", "newdesc", "newacc" ])) { return; }
                $("#button-add").button("disable");
                let formdata = "mode=create&accountid=" + controller.accountid + "&" +
                    $("#table-trx input, #table-trx select").toPOST();
                await common.ajax_post("accounts_trx", formdata);
                accounts_trx.reload();
            });

            $("#button-delete").button({disabled: true}).click(async function() {
                await tableform.delete_dialog();
                let formdata = "mode=delete&ids=" + $("#table-trx input").tableCheckedData();
                await common.ajax_post("accounts_trx", formdata);
                accounts_trx.reload();
            });

            // Allow CTRL+A to select all transactions
            Mousetrap.bind("ctrl+a", function() {
                $("#table-trx input[type='checkbox']").prop("checked", true);
                $("#button-delete").button("option", "disabled", false); 
                $("#button-reconcile").button("option", "disabled", false); 
                return false;
            });

            $(".trx-edit-link").click(function() {
                if (accounts_trx.readonly) { return false; }
                const row = common.get_row(controller.rows, $(this).attr("data-id"));
                validate.reset("dialog-edit");
                $("#trxid").val(row.ID);
                $("#trxdate").val(format.date(row.TRXDATE));
                $("#description").val(html.decode(row.DESCRIPTION));
                $("#reconciled").select("value", row.RECONCILED);
                $("#otheraccount").val(html.decode(row.OTHERACCOUNTCODE));
                if (!row.PERSONNAME) {
                    $("#paymentrow").hide();
                }
                else {
                    $("#personlink").html(row.PERSONNAME);
                    $("#personlink").prop("href", "person_donations?id=" + row.PERSONID);
                    $("#animallink").html(row.DONATIONANIMALCODE + " " + row.DONATIONANIMALNAME);
                    $("#animallink").prop("href", "animal_donations?id=" + row.DONATIONANIMALID);
                    $("#receiptno").html(row.DONATIONRECEIPTNUMBER);
                    $("#paymentrow").show();
                }
                if (!row.COSTANIMALNAME) {
                    $("#costrow").hide();
                }
                else {
                    $("#costanimallink").html(row.COSTANIMALCODE + " " + row.COSTANIMALNAME);
                    $("#costanimallink").prop("href", "animal_costs?id=" + row.COSTANIMALID);
                    $("#costrow").show();
                }
                common.inject_target();
                $("#deposit").val(format.currency(row.DEPOSIT));
                $("#withdrawal").val(format.currency(row.WITHDRAWAL));
                $("#dialog-edit").dialog("open");
                $("#description").focus();
                return false; // prevents # href
            });

        },

        readonly: false,

        sync: function() {

            // When first loaded, scroll to the bottom of the page and make the
            // new description active
            setTimeout(function() {
                $("html, body").animate({scrollTop: $(document).height()});
                $("#newdesc").focus();
            }, 1000);

            // Set the filter at the top to match our current view
            $("#recfilter").select("value", controller.recfilter);
            $("#fromdate").val(controller.fromdate);
            $("#todate").val(controller.todate);

            // Default values for the new row
            $("#newtrxdate").datepicker("setDate", new Date());
            $("#newacc").autocomplete({ source: html.decode(controller.codes).split("|") });
            $("#otheraccount").autocomplete({ source: html.decode(controller.codes).split("|") });

            // If this account has edit roles set and our user is
            // not a superuser and not in one of those roles then
            // hide the add row and prevent editing the transactions
            if (controller.accounteditroles && !asm.superuser && !common.array_overlap(controller.accounteditroles.split("|"), asm.roleids.split("|"))) {
                accounts_trx.readonly = true;
                $(".newrow").hide();
                $("#asm-content .asm-toolbar").hide();
            }
        },

        destroy: function() {
            common.widget_destroy("#dialog-edit");
            tableform.dialog_destroy();
        },

        name: "accounts_trx",
        animation: "book",
        title: function() { return controller.accountcode; },

        routes: {
            "accounts_trx": function() {
                common.module_loadandstart("accounts_trx", "accounts_trx?" + this.rawqs);
            }
        }


    };

    common.module_register(accounts_trx);

});
