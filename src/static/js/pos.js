/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const pos = {

        model: function() {
            const dialog = {};
            const table = {};
            const buttons = [];
            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;
            this.buttoncolours = [
                ['#e7e7e7', '#515151'],
                ['#b6cff5', '#103b79'],
                ['#e3d7ff', '#472893'],
                ['#98d7e4', '#78203d'],
                ['#f2b2a8', '#8b1900'],
                ['#c2c2c2', '#fafafa']
            ];
            this.nextbuttoncolour = 0;
            this.numpadfocus;
            this.activeproduct = {};
            this.payments = [];
            this.multiplier = 1;
            this.refund = false;
        },

        render: function() {
            this.model();
            let s = [
                '<div id="poscontainer" style="background-color: #eeeeee; width: 100vw; height: 100vh;">',
                    '<div style="flex: 100%;">',
                        // '<div id="findproductpanel" style="vertical-align: middle; padding: 10px; padding-bottom: 0;">',
                        //     '<input type="text" style="font-size: 150%; padding: 10px; margin-right: 5px;" placeholder="' + _("Search key..") + '">',
                        //     '<button style="font-size: 150%; padding: 10px; vertical-align: top; height: 100%;">' + _("Search") + '</button>',
                        // '</div>',
                        '<div id="producttypes" style="padding: 10px; padding-bottom: 0px;">',
                            pos.product_type_buttons(),
                        '</div>',
                        '<div id="taxrates" style="padding: 10px; padding-bottom: 0px;">',
                            pos.tax_rate_buttons(),
                        '</div>',
                        '<div id="infopanel"></div>',
                    '</div>',
                    '<div id="transactionpanel" style="background-color: #ffffff; max-width: 600px; min-width: 600px; height: 100vh; max-height: 100vh; border: 1px; position: relative;">',
                        '<div id="transactionlog" style="overflow: auto;">',
                            '<div id="transactionsheader">',
                                '<div id="transactiondescriptionheader">' + _("Description") + '</div>',
                                '<div id="transactionquantityheader">' + _("#") + '</div>',
                                '<div id="transactiontaxheader">' + _("Tax") + '</div>',
                                '<div id="transactionpriceheader">' + _("Price") + '</div>',
                            '</div>',
                            '<hr>',
                            '<div id="currentreceiptitemcontainer">',
                                '<div id="currentreceiptitemdescription"></div>',
                                '<div id="currentreceiptitemquantity">1</div>',
                                '<div id="currentreceiptitemtax" class="posprice">0.00</div>',
                                '<div id="currentreceiptitemprice" class="posprice">0.00</div>',
                            '</div>',
                        '</div>',
                        '<hr>',
                        '<div id="subtotal">',
                            '<div id="subtotaldescription">' + _("Subtotal") + '</div>',
                            '<div id="subtotalquantity">0</div>',
                            '<div id="subtotaltax">0.00</div>',
                            '<div id="subtotalprice">0.00</div>',
                        '</div>',
                        '<div id="payments">',
                        '</div>',
                        '<div id="numberpad">',
                            '<div id="balancecontainer">',
                                '<div id="balancelabel">' + _("Balance") + '</div>',
                                '<div id="balance">0.00</div>',
                            '</div>',
                            '<table style="width: 100%; height: 700px;">',
                            '<tr><th colspan="4" id="numpadscreen"></th></tr>',
                            '<tr><td class="numeral">7</td><td class="numeral">8</td><td class="numeral">9</td><td id="deletekey">' + _("Del") + '</td></tr>',
                            '<tr><td class="numeral">4</td><td class="numeral">5</td><td class="numeral">6</td><td id="refundkey">-</td></tr>',
                            '<tr><td class="numeral">1</td><td class="numeral">2</td><td class="numeral">3</td><td id="multiplykey">*</td></tr>',
                            '<tr><td class="numeral">0</td><td class="numeral">00</td><td colspan="2" id="enterkey">Enter</td></tr>',
                            '<tr><td colspan="2" id="cardbutton">' + _("Card") + '</td><td colspan="2" id="cashbutton">' + _("Cash") + '</td></tr>',
                            '</table>',
                        '</div>',
                    '</div>',
                    
                '</div>'
            ].join("\n");
            
            return s;
        },

        get_button_colours: function() {
            let bgcolour = this.buttoncolours[this.nextbuttoncolour][0];
            let fgcolour = this.buttoncolours[this.nextbuttoncolour][1];
            this.nextbuttoncolour++;
            if (this.nextbuttoncolour == this.buttoncolours.length) { this.nextbuttoncolour = 0 };
            return [bgcolour, fgcolour];
        },

        product_type_buttons: function() {
            let colours = pos.get_button_colours();
            var producttypes = []
            $.each(controller.producttypes, function(i, v) {
                    colours = pos.get_button_colours();
                    producttypes.push(
                        [
                            '<div class="posbuttoncontainer">',
                                '<div class="posbutton producttype" data-producttypeid="' + v.ID + '" style="background-color: ' + colours[0] + '; color: ' + colours[1] + ';">',
                                    v.PRODUCTTYPENAME,
                                '</div>',
                            '</div>'
                        ].join("\n")
                    )
            });
            return producttypes.join("\n");
        },

        tax_rate_buttons: function() {
            let colours = pos.get_button_colours();
            var taxrates = []
            $.each(controller.taxrates, function(i, v) {
                    colours = pos.get_button_colours();
                    taxrates.push(
                        [
                            '<div class="posbuttoncontainer">',
                                '<div class="posbutton taxrate" data-taxrateid="' + v.ID + '" data-taxrate="' + v.TAXRATE + '" style="background-color: ' + colours[0] + '; color: ' + colours[1] + ';">',
                                    v.TAXRATENAME,
                                '</div>',
                            '</div>'
                        ].join("\n")
                    )
            });
            return taxrates.join("\n");
        },

        format_price: function(price) {
            let founddecimalpoint = false;
            let digitsafterdecimalpoint = 0;
            if (!price) { return "0.00" };
            for (let c = 0; c < price.length; c++) {
                if (price.charAt(c) == ".") {
                    if (!founddecimalpoint) {
                        founddecimalpoint = true
                    } else {
                        return "0.00";
                    }
                } else {
                    if (founddecimalpoint) {
                        digitsafterdecimalpoint++;
                    }
                }
            }
            if (digitsafterdecimalpoint > 2) {
                return "0.00";
            }
            let formattedprice = price;
            if (!founddecimalpoint) {
                formattedprice = parseFloat(formattedprice) / 100.00;
                formattedprice = formattedprice.toFixed(2);
            } else  {
                while (digitsafterdecimalpoint < 2) {
                    formattedprice = formattedprice + "0";
                    digitsafterdecimalpoint++;
                }
            }
            return formattedprice;
        },

        update_subtotal: function() {
            let quantity = 0;
            let price = 0.00;
            let tax = 0.00;
            $.each($(".receiptitemquantity"), function(i, v) {
                if ( !$(v).closest(".receiptitemcontainer").attr("data-voided") ) {
                    quantity = quantity + parseInt($(v).text());
                }
            });
            $.each($(".receiptitemprice"), function(i, v) {
                if ( !$(v).closest(".receiptitemcontainer").attr("data-voided") ) {
                    price = price + parseFloat($(v).text());
                }
            });
            $.each($(".receiptitemtax"), function(i, v) {
                if ( !$(v).closest(".receiptitemcontainer").attr("data-voided") ) {
                    tax = tax + parseFloat($(v).text());
                }
            });
            $("#subtotalquantity").text(quantity);
            $("#subtotaltax").text(tax.toFixed(2));
            $("#subtotalprice").text(price.toFixed(2));
            $.each($(".paymentprice"), function(i, v) {
                if ( !$(v).closest(".receiptitemcontainer").attr("data-voided") ) {
                    price = price - parseFloat($(v).text());
                }
            });
            $("#balance").text(price.toFixed(2));
            $("#transactionlog").scrollTop($("#transactionlog").height());
        },

        reset_focus: function() {
            $(".receiptitemquantity").css("border", "none");
            pos.numpadfocus = null;
        },

        complete_transaction: function() {
            alert(_("Transaction Complete"));
        },

        sync: function() {
            $("body").css("margin", 0);
            $("html").css("max-height", "100vh");
            $("#currentreceiptitemcontainer").hide();
            $("#asm-topline").hide();
            $("#quicklinks").hide();
            $("#linkstips").hide();
            $("#taxrates").hide();
        },

        bind: function() {
            $(".producttype").click(function() {
                $("#currentreceiptitemdescription").text($(this).text());
                $("#infopanel").html("");
                let producttypeid = $(this).attr("data-producttypeid");
                let products = [
                    [
                        '<div id="productsheader">',
                            '<div style="flex: 70%">',
                                _("Product Name"),
                            '</div>',
                            '<div style="flex: 10%">',
                                _("Unit"),
                            '</div>',
                            '<div style="flex: 10%">',
                                _("Price"),
                            '</div>',
                            '<div style="flex: 10%">',
                                _("Stock"),
                            '</div>',
                        '</div>'
                    ].join("\n")
                ];
                $.each(controller.products, function(i, v) {
                    if (producttypeid == v.PRODUCTTYPEID) {
                        let balance = v.BALANCE;
                        if (!v.BALANCE) {
                            balance = 0;
                        }
                        let medialink = "";
                        if (v.MEDIAID) { medialink = '<a href="image?db=' + asm.useraccount + '&mode=media&id=' + v.MEDIAID + '"><span class="asm-icon asm-icon-media"></span></a>' };
                        products.push(
                            [
                                '<div class="productcontainer" data-productid="' + v.ID + '">',
                                    '<div style="flex: 70%">',
                                        v.PRODUCTNAME,
                                        medialink,
                                    '</div>',
                                    '<div style="flex: 10%">',
                                        v.UNIT,
                                    '</div>',
                                    '<div style="flex: 10%">',
                                        pos.format_price(v.RETAILPRICE),
                                    '</div>',
                                    '<div style="flex: 10%">',
                                        balance,
                                    '</div>',
                                '</div>',
                            ].join("\n"));
                    }
                });
                $("#infopanel").html(products);
            });
            $(".taxrate").click(function() {
                let taxrate = parseFloat($(this).attr("data-taxrate")) / 100.00;
                let refund = 1;
                if (pos.refund) { refund = -1 };
                let price = parseInt($("#numpadscreen").text()) * refund;
                let taxamount = parseFloat(price)  * taxrate;
                $("#transactionlog").append(
                    [
                        '<div class="receiptitemcontainer">',
                            '<div class="receiptitemdescription">' + $(this).text() + '&nbsp;<span class="removereceiptitem">X</span></div>',
                            '<div class="receiptitemquantity" data-unitprice="' + price + '">1</div>',
                            '<div class="receiptitemtax" class="posprice" data-taxrate="' + $(this).attr("data-taxrate") + '">' + pos.format_price(taxamount) + '</div>',
                            '<div class="receiptitemprice" class="posprice">' + pos.format_price(price) + '</div>',
                        '</div>'
                    ].join("\n")
                );
                $("#numpadscreen").text("");
                $("#producttypes, #infopanel").show();
                $("#taxrates").hide();
                pos.update_subtotal();
            });

            $("#currentreceiptitemcontainer div").click(function() {
                pos.numpadfocus = $(this);
                $(".numpadtarget").removeClass("numpadtarget");
                pos.numpadfocus.addClass("numpadtarget");
                if ( pos.numpadfocus.hasClass("posprice") && pos.numpadfocus.text() == "0.00") { pos.numpadfocus.text("") };
            });
            $("#numberpad .numeral").click(function() {
                if (pos.numpadfocus) {
                    pos.numpadfocus.text(pos.numpadfocus.text() + $(this).text());
                } else {
                    if (!$("#numpadscreen").text()) {
                        $("#producttypes, #infopanel").hide();
                        $("#taxrates").show();
                    }
                    $("#numpadscreen").text($("#numpadscreen").text() + $(this).text());
                }
            });
            $("#deletekey").click(function() {
                if (pos.numpadfocus) {
                    if (pos.numpadfocus.text() == "0.00") {
                        pos.numpadfocus.text("");
                    } else if (pos.numpadfocus.text()) {
                        pos.numpadfocus.text(pos.numpadfocus.text().slice(0, pos.numpadfocus.text().length - 1));
                    }
                } else {
                    $("#numpadscreen").text($("#numpadscreen").text().slice(0, $("#numpadscreen").text().length - 1));
                    if (!$("#numpadscreen").text()) {
                        $("#producttypes, #infopanel").show();
                        $("#taxrates").hide();
                    }
                }
            });
            $("#enterkey").click(function() {
                if (pos.numpadfocus) {
                    if (pos.numpadfocus.hasClass("posprice")) {
                        pos.numpadfocus.text(pos.format_price(pos.numpadfocus.text()));
                    }
                    if (pos.numpadfocus.hasClass("receiptitemquantity")) {
                        let quantity = parseInt(pos.numpadfocus.text());
                        pos.numpadfocus.text(quantity);
                        let price = parseInt(pos.numpadfocus.attr("data-unitprice")) * quantity;
                        let taxrate = pos.numpadfocus.next().attr("data-taxrate");
                        taxrate = parseFloat(taxrate);
                        let taxamount = parseFloat(price) * taxrate;
                        pos.numpadfocus.next().text(pos.format_price(taxamount));
                        pos.numpadfocus.next().next().text(pos.format_price(price));
                        pos.numpadfocus.css("border", "none");
                    }
                    $(".numpadtarget").removeClass("numpadtarget");
                    pos.numpadfocus = null;
                    pos.update_subtotal();
                }
            });
            $("#infopanel").on("click", ".productcontainer", function() {
                let productid = $(this).attr("data-productid");
                $.each(controller.products, function(i, v) {
                    if (v.ID == productid) {
                        let taxrateid = v.TAXRATEID;
                        let taxrate = 0;
                        let refund = 1;
                        if (pos.refund) { refund = -1 };
                        $.each(controller.taxrates, function(i, v) {
                            if (v.ID == taxrateid) {
                                taxrate = parseFloat(v.TAXRATE) / 100.00;
                                return false;
                            }
                        });
                        let taxamount = parseFloat(v.RETAILPRICE) * taxrate;
                        pos.activeproduct = v;
                        $("#transactionlog").append(
                            [
                                '<div class="receiptitemcontainer">',
                                    '<div class="receiptitemdescription">' + v.PRODUCTNAME + '&nbsp;<span class="removereceiptitem">X</span></div>',
                                    '<div class="receiptitemquantity" data-unitprice="' + v.RETAILPRICE + '">' + ( pos.multiplier * refund ) + '</div>',
                                    '<div class="receiptitemtax" class="posprice" data-taxrate="' + taxrate + '">' + pos.format_price(taxamount * pos.multiplier * refund) + '</div>',
                                    '<div class="receiptitemprice" class="posprice">' + pos.format_price(v.RETAILPRICE * pos.multiplier * refund) + '</div>',
                                '</div>'
                            ].join("\n")
                        );
                        pos.multiplier = 1;
                        $("#numpadscreen").text("");
                        pos.update_subtotal();
                        return false;
                    }
                });

            });
            $("#transactionpanel").on("click", ".receiptitemdescription", function() {
                $(this).find(".removereceiptitem").toggle();
            });
            $("#transactionpanel").on("click", ".paymentdescription", function() {
                $(this).find(".removereceiptitem").toggle();
            });
            $("#transactionpanel").on("click", ".receiptitemquantity", function() {
                if ( !pos.numpadfocus && !$(this).closest(".receiptitemcontainer").attr("data-voided") ) {
                    pos.numpadfocus = $(this);
                    pos.numpadfocus.css("border", "1px solid black");
                }
            });
            $("#transactionpanel").on("click", ".removereceiptitem", function() {
                let receiptitem = $(this).closest(".receiptitemcontainer");
                receiptitem.find(".receiptitemquantity").css("border", "none");
                receiptitem.css("text-decoration", "line-through");
                receiptitem.attr("data-voided", "true");
                $(this).remove();
                pos.numpadfocus = null;
                pos.update_subtotal();
            });
            $("#cashbutton").on("click", function() {
                let paymentamount = $("#numpadscreen").text();
                if (!paymentamount) { paymentamount = $("#balance").text() };
                $("#numpadscreen").text("");
                $("#payments").append(
                    [
                        '<hr>',
                        '<div class="receiptitemcontainer">',
                            '<div class="paymentdescription">' + _("Cash") + '&nbsp;<span class="removereceiptitem">X</span></div>',
                            '<div class="paymentprice">' + pos.format_price(paymentamount) + '</div>',
                        '</div>'
                    ].join("\n")
                );
                pos.update_subtotal();
                $("#producttypes, #infopanel").show();
                $("#taxrates").hide();
                if ($("#balance").text() == "0.00") {
                    pos.complete_transaction();
                }
            });

            $("#cardbutton").on("click", function() {
                let paymentamount = $("#numpadscreen").text();
                if (!paymentamount) { paymentamount = $("#balance").text() };
                $("#numpadscreen").text("");
                $("#payments").append(
                    [
                        '<hr>',
                        '<div class="receiptitemcontainer">',
                            '<div class="paymentdescription">' + _("Card") + '&nbsp;<span class="removereceiptitem">X</span></div>',
                            '<div class="paymentprice">' + pos.format_price(paymentamount) + '</div>',
                        '</div>'
                    ].join("\n")
                );
                pos.update_subtotal();
                $("#producttypes, #infopanel").show();
                $("#taxrates").hide();
                if ($("#balance").text() == "0.00") {
                    pos.complete_transaction();
                }
            });

            $("#multiplykey").click(function() {
                if ($("#numpadscreen").text()) {
                    pos.multiplier = parseInt($("#numpadscreen").text());
                    $("#producttypes, #infopanel").show();
                    $("#taxrates").hide();
                }
            });

            $("#refundkey").click(function() {
                if (pos.refund) {
                    $(this).removeClass("refund");
                    pos.refund = false;
                } else {
                    $(this).addClass("refund");
                    pos.refund = true;
                }
            });
        },

        destroy: function() {
        },

        name: "pos",
        animation: "formtab",
        title: function() {
            return _("POS");
        },
        routes: {
            "pos": function() { common.module_loadandstart("pos", "pos"); }
        }

    };

    common.module_register(pos);

});
