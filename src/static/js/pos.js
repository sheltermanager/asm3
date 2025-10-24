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
                ["red", "white"],                
                ["orange", "black"],
                ["pink", "black"],
                ["green", "white"],
                ["grey", "white"],
                ["blue", "white"],
                ["purple", "white"],
                ["black", "white"]
            ];
            this.nextbuttoncolour = 0;
            this.numpadfocus;
            this.activeproduct = {};
            this.payments = [];
            this.multiplier = 1;
            this.refund = false;
            this.numpadlocked = true;
        },

        render: function() {
            this.model();
            let s = [
                '<div id="poscontainer" style="background-color: #eeeeee; width: 100vw; height: 100vh;">',
                    '<div id="posleftpanel" style="flex: 100%;">',
                        // '<div id="findproductpanel" style="vertical-align: middle; padding: 10px; padding-bottom: 0;">',
                        //     '<input type="text" style="font-size: 150%; padding: 10px; margin-right: 5px;" placeholder="' + _("Search key..") + '">',
                        //     '<button style="font-size: 150%; padding: 10px; vertical-align: top; height: 100%;">' + _("Search") + '</button>',
                        // '</div>',
                        '<div id="producttypes">',
                            pos.product_type_buttons(),
                        '</div>',
                        '<div id="taxrates">',
                            pos.tax_rate_buttons(),
                        '</div>',
                        '<div id="infopanel"></div>',
                        '<div id="posmenupanel">',
                            '<h1 id="posmenutitle">' + _("ASM Point of Sale") + '</h1>',
                            '<div id="posstartbutton" class="posbuttoncontainer posmenubutton">',
                                '<div class="posbutton" style="background-color: green; color: white;">',
                                    '<div style="display: inline-block;">', 
                                        '<div  class="posbuttoncontent">' + _("Start a Transaction") + '</div>',
                                    '</div>',
                                '</div>',
                            '</div>',
                            '<div id="posprintreceiptbutton" class="posbuttoncontainer posmenubutton">',
                                '<div class="posbutton" style="background-color: white; color: black;">',
                                    '<div style="display: inline-block;">', 
                                        '<div  class="posbuttoncontent">' + _("Print Receipt") + '</div>',
                                    '</div>',
                                '</div>',
                            '</div>',
                            '<div id="posasmmenubutton" class="posbuttoncontainer posmenubutton">',
                                '<div class="posbutton" style="background-color: blue; color: white;">',
                                    '<div style="display: inline-block;">', 
                                        '<div  class="posbuttoncontent">' + _("ASM Menu") + '</div>',
                                    '</div>',
                                '</div>',
                            '</div>',
                        '</div>',
                    '</div>',
                    '<div id="transactionpanel">',
                        '<div id="transactionlog" style="overflow: auto;">',
                            '<div id="transactionsheader">',
                                '<div id="transactiondescriptionheader">' + _("Description") + '</div>',
                                '<div id="transactionquantityheader">' + _("#") + '</div>',
                                '<div id="transactiontaxheader">' + _("Tax") + '</div>',
                                '<div id="transactionpriceheader">' + _("Price") + '</div>',
                            '</div>',
                            '<hr>',
                        '</div>',
                        '<hr>',
                        '<div id="subtotal">',
                            '<div id="subtotaldescription">' + _("Subtotal") + '</div>',
                            '<div id="subtotalquantity">0</div>',
                            '<div id="subtotaltax">0.00</div>',
                            '<div id="subtotalprice">0.00</div>',
                        '</div>',
                        '<hr>',
                        '<div id="payments">',
                        '</div>',
                        '<div id="numberpad">',
                            '<div id="balancecontainer">',
                                '<div id="balancelabel">' + _("Balance") + '</div>',
                                '<div id="balance" data-balance="0">0.00</div>',
                            '</div>',
                            '<table>',
                            '<tr><th colspan="4" id="numpadscreen"></th></tr>',
                            '<tr><td class="numeral">7</td><td class="numeral">8</td><td class="numeral">9</td><td id="deletekey">' + _("Del") + '</td></tr>',
                            '<tr><td class="numeral">4</td><td class="numeral">5</td><td class="numeral">6</td><td id="refundkey">-</td></tr>',
                            '<tr><td class="numeral">1</td><td class="numeral">2</td><td class="numeral">3</td><td id="multiplykey">*</td></tr>',
                            '<tr><td class="numeral">0</td><td class="numeral">00</td><td colspan="2" id="enterkey" class="voidkey">' + _("Void") + '</td></tr>',
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
                                    '<div style="display: inline-block;">',
                                        '<div class="posbuttoncontent">' + v.PRODUCTTYPENAME + '</div>',
                                    '</div>',
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
                                    '<div style="display: inline-block;">',
                                        '<div class="posbuttoncontent">' + v.TAXRATENAME + '</div>',
                                    '</div>',
                                '</div>',
                            '</div>'
                        ].join("\n")
                    )
            });
            return taxrates.join("\n");
        },

        format_price: function(price) {
            return (parseFloat(price) / 100.00).toFixed(2);
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
                    price = price + parseInt($(v).attr("data-price"));
                }
            });
            $.each($(".receiptitemtax"), function(i, v) {
                if ( !$(v).closest(".receiptitemcontainer").attr("data-voided") ) {
                    tax = tax + parseInt($(v).attr("data-taxamount"));
                }
            });
            $("#subtotalquantity").text(quantity);
            $("#subtotaltax").text(pos.format_price(tax));
            $("#subtotalprice").text(pos.format_price(price));
            $.each($(".paymentprice"), function(i, v) {
                if ( !$(v).closest(".receiptpaymentcontainer").attr("data-voided") ) {
                    price = price - parseInt($(v).attr("data-price"));
                }
            });
            $("#balance").attr("data-balance", price);
            $("#balance").text(pos.format_price(price));
            $("#transactionlog").scrollTop($("#transactionlog").height());
        },

        reset_focus: function() {
            $(".receiptitemquantity").css("border", "none");
            pos.numpadfocus = null;
        },

        complete_transaction: async function() {
            // alert(_("Transaction Complete"));
            let receiptdetails = [];
            $.each($(".receiptitemcontainer"), function(i, v) {
                $(v).find(".removereceiptitem").remove();
                receiptdetails.push(
                    {
                        "productid": parseInt($(v).find(".receiptitemdescription").attr("data-productid")),
                        "producttypeid": parseInt($(v).find(".receiptitemdescription").attr("data-producttypeid")),
                        "description": $(v).find(".receiptitemdescription").text(),
                        "quantity": parseInt($(v).find(".receiptitemquantity").text()),
                        "taxrate": parseFloat($(v).find(".receiptitemtax").attr("data-taxrate")),
                        "price": parseInt($(v).find(".receiptitemprice").attr("data-price"))
                    }
                );
            });
            $.each($(".receiptpaymentcontainer"), function(i, v) {
                $(v).find(".removereceiptitem").remove();   
                receiptdetails.push(
                    {
                        "productid": 0,
                        "producttypeid": 0,
                        "description": $(v).find(".paymentdescription").text(),
                        "quantity": 1,
                        "taxrate": 0,
                        "price": parseInt($(v).find(".paymentprice").attr("data-price")) * -1
                    }
                );
            });
            console.log(receiptdetails);
            let formdata = "mode=write&jsondata=" + JSON.stringify(receiptdetails);
            let receiptid = await common.ajax_post("pos", formdata);
            console.log(receiptid);
            $("#posleftpanel").children().hide();
            $("#posprintreceiptbutton").show();
            $("#posmenupanel").show();
        },

        sync: function() {
            $("body").css("margin", 0);
            $("html").css("max-height", "100vh");
            $("#currentreceiptitemcontainer").hide();
            $("#asm-topline").hide();
            $("#quicklinks").hide();
            $("#linkstips").hide();
            $("#taxrates").hide();
            $("#producttypes").hide();
            $("#posprintreceiptbutton").hide();
            // $("#numpadscreen").hide();
        },

        bind: function() {
            $(".producttype").click(function() {
                $("#currentreceiptitemdescription").text($(this).text());
                $("#infopanel").html("");
                let producttypeid = $(this).attr("data-producttypeid");
                $("#infopanel").attr("data-producttypeid", producttypeid);
                $(".producttype").removeClass("activeproducttype");
                $(this).addClass("activeproducttype");
                let products = [
                    [
                        '<div id="productsheader">',
                            '<div class="productinfodescription">',
                                _("Product Name"),
                            '</div>',
                            '<div class="productinfounit">',
                                _("Unit"),
                            '</div>',
                            '<div class="productinfoprice">',
                                _("Price"),
                            '</div>',
                            '<div class="productinfobalance">',
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
                                    '<div class="productinfodescription">',
                                        v.PRODUCTNAME,
                                        medialink,
                                    '</div>',
                                    '<div class="productinfounit">',
                                        v.UNIT,
                                    '</div>',
                                    '<div class="productinfoprice">',
                                        pos.format_price(v.RETAILPRICE),
                                    '</div>',
                                    '<div class="productinfobalance">',
                                        balance,
                                    '</div>',
                                '</div>',
                            ].join("\n"));
                    }
                });
                $("#infopanel").html(products);
                $("#infopanel").scrollTop(0);
            });
            $(".taxrate").click(function() {
                let taxrate = parseFloat($(this).attr("data-taxrate")) / 100.00;
                let refund = 1;
                if (pos.refund) { refund = -1 };
                let price = parseInt($("#numpadscreen").text()) * refund;
                let taxamount = parseInt(parseFloat(price)  * taxrate);
                $("#transactionlog").append(
                    [
                        '<div class="receiptitemcontainer">',
                            '<div class="receiptitemdescription" data-productid="0" data-producttypeid="0">' + $(this).text().trim() + '<span class="removereceiptitem">X</span></div>',
                            '<div class="receiptitemquantity" data-unitprice="' + price + '">1</div>',
                            '<div class="receiptitemtax" class="posprice" data-taxrate="' + taxrate + '" data-taxamount="' + taxamount + '">' + pos.format_price(taxamount) + '</div>',
                            '<div class="receiptitemprice" class="posprice" data-price="' + price + '">' + pos.format_price(price) + '</div>',
                        '</div>'
                    ].join("\n")
                );
                $("#numpadscreen").text("");
                // $("#numpadscreen").hide();
                $("#producttypes, #infopanel").show();
                $("#taxrates").hide();
                pos.update_subtotal();
                $("#infopanel").scrollTop(0);
            });

            $("#currentreceiptitemcontainer div").click(function() {
                pos.numpadfocus = $(this);
                $(".numpadtarget").removeClass("numpadtarget");
                pos.numpadfocus.addClass("numpadtarget");
                if ( pos.numpadfocus.hasClass("posprice") && pos.numpadfocus.text() == "0.00") { pos.numpadfocus.text("") };
                $("#enterkey").text(_("Enter"));
                $("#enterkey").removeClass("voidkey");
            });
            $("#numberpad .numeral").click(function() {
                if (pos.numpadlocked) { return false };
                if (pos.numpadfocus) {
                    pos.numpadfocus.text(pos.numpadfocus.text() + $(this).text());
                } else {
                    if (!$("#numpadscreen").text()) {
                        // $("#numpadscreen").show();
                        $("#producttypes, #infopanel").hide();
                        $("#taxrates").show();
                    }
                    $("#numpadscreen").text($("#numpadscreen").text() + $(this).text());
                }
            });
            $("#deletekey").click(function() {
                if (pos.numpadlocked) { return false };
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
                        // $("#numpadscreen").hide();
                    }
                }
            });
            $("#enterkey").click(function() {
                if (pos.numpadlocked) { return false };
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
                    $("#enterkey").text(_("Void"));
                    $("#enterkey").addClass("voidkey");
                    pos.update_subtotal();
                } else {
                    if (confirm( _("No data has been written to the database and no stock has been moved. Are you sure that you want to abandon this transaction?"))) {
                        $(".receiptitemcontainer").remove();
                        $(".receiptpaymentcontainer").remove();
                        pos.update_subtotal();
                        $("#posleftpanel").children().hide();
                        $("#posprintreceiptbutton").hide();
                        $("#posmenupanel").show();
                    }
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
                        let taxamount = parseInt(v.RETAILPRICE * taxrate * pos.multiplier * refund);
                        let price = v.RETAILPRICE * pos.multiplier * refund;
                        pos.activeproduct = v;
                        $("#transactionlog").append(
                            [
                                '<div class="receiptitemcontainer">',
                                    '<div class="receiptitemdescription" data-productid="' + productid + '" data-producttypeid="' + $("#infopanel").attr("data-producttypeid") + '">' + v.PRODUCTNAME + '<span class="removereceiptitem">X</span></div>',
                                    '<div class="receiptitemquantity" data-unitprice="' + v.RETAILPRICE + '">' + ( pos.multiplier * refund ) + '</div>',
                                    '<div class="receiptitemtax" class="posprice" data-taxrate="' + taxrate + '" data-taxamount="' + taxamount + '">' + pos.format_price(taxamount) + '</div>',
                                    '<div class="receiptitemprice" class="posprice" data-price="' + price + '">' + pos.format_price(price) + '</div>',
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
                    $("#enterkey").text(_("Enter"));
                    $("#enterkey").removeClass("voidkey");
                }
            });
            $("#transactionpanel").on("click", ".removereceiptitem", function() {
                let receiptitem = $(this).closest(".receiptitemcontainer");
                if ( $(this).closest("div").hasClass("paymentdescription") ) {
                        receiptitem = $(this).closest(".receiptpaymentcontainer");
                }
                // let receiptitem = $(this).closest(".receiptitemcontainer");
                console.log(receiptitem);
                receiptitem.find(".receiptitemquantity").css("border", "none");
                receiptitem.css("text-decoration", "line-through");
                receiptitem.attr("data-voided", "true");
                $(this).remove();
                pos.numpadfocus = null;
                pos.update_subtotal();
            });
            $("#cashbutton").on("click", function() {
                if (pos.numpadlocked) { return false };
                let refund = 1;
                if (pos.refund) { refund = -1 };
                let paymentamount = parseInt($("#numpadscreen").text()) * refund;
                if (!paymentamount) { paymentamount = parseInt($("#balance").attr("data-balance")) };
                $("#numpadscreen").text("");
                // $("#numpadscreen").hide();
                $("#payments").append(
                    [
                        '<div class="receiptpaymentcontainer">',
                            '<div class="paymentdescription">' + _("Cash") + '<span class="removereceiptitem">X</span></div>',
                            '<div class="paymentprice" data-price="' + paymentamount + '">' + pos.format_price(paymentamount) + '</div>',
                        '</div>'
                    ].join("\n")
                );
                pos.update_subtotal();
                $("#producttypes, #infopanel").show();
                $("#taxrates").hide();
                if ( $("#balance").attr("data-balance") == 0 ) {
                    pos.numpadlocked = true;
                    pos.complete_transaction();
                }
            });

            $("#cardbutton").on("click", function() {
                if (pos.numpadlocked) { return false };
                let refund = 1;
                if (pos.refund) { refund = -1 };
                let paymentamount = parseInt($("#numpadscreen").text()) * refund;
                if (!paymentamount) { paymentamount = parseInt($("#balance").attr("data-balance")) };
                $("#numpadscreen").text("");
                // $("#numpadscreen").hide();
                $("#payments").append(
                    [
                        '<div class="receiptpaymentcontainer">',
                            '<div class="paymentdescription">' + _("Card") + '<span class="removereceiptitem">X</span></div>',
                            '<div class="paymentprice" data-price="' + paymentamount + '">' + pos.format_price(paymentamount) + '</div>',
                        '</div>'
                    ].join("\n")
                );
                pos.update_subtotal();
                $("#producttypes, #infopanel").show();
                $("#taxrates").hide();
                if ( $("#balance").attr("data-balance") == 0 ) {
                    pos.numpadlocked = true;
                    pos.complete_transaction();
                }
            });

            $("#multiplykey").click(function() {
                if (pos.numpadlocked) { return false };
                if ($("#numpadscreen").text()) {
                    pos.multiplier = parseInt($("#numpadscreen").text());
                    $("#producttypes, #infopanel").show();
                    $("#taxrates").hide();
                }
            });

            $("#refundkey").click(function() {
                if (pos.numpadlocked) { return false };
                if (pos.refund) {
                    $(this).removeClass("refund");
                    pos.refund = false;
                } else {
                    $(this).addClass("refund");
                    pos.refund = true;
                }
            });

            $("#posasmmenubutton").click(function() {
                $("#asm-topline").toggle();
            });

            $("#posstartbutton").click(function() {
                $(".receiptitemcontainer").remove();
                $(".receiptpaymentcontainer").remove();
                pos.update_subtotal();
                pos.activeproduct = {};
                $(".activeproducttype").removeClass("activeproducttype");
                $("#posmenupanel").hide();
                $("#producttypes").show();
                $("#infopanel").html("");
                $("#infopanel").show();
                pos.numpadlocked = false;
            });

            $("#posprintreceiptbutton").click(function() {
                let receipthtml = [
                    '<h3>' + controller.orgname + '</h3>',
                    '<p>' + controller.orgaddress + '<br>' + controller.orgpostcode + '</p>',
                    '<p>' + controller.orgtel + ' ' + controller.orgemail + '</p>',
                    '<table border="1" cellpadding="10px" style="border-collapse: collapse;">',
                    '<tr><th>' + _("Description") + '</th><th>' + _("#") + '</th><th>' + _("Tax") + '</th><th>' + _("Price") + '</th></tr>'
                ]
                $.each($(".receiptitemcontainer"), function(i, v) {
                    receipthtml.push('<tr><td>' + $(v).find(".receiptitemdescription").text() + '</td><td>' + $(v).find(".receiptitemquantity").text() + '</td><td>' + $(v).find(".receiptitemtax").text() + '</td><td>' + pos.format_price(parseInt($(v).find(".receiptitemprice").attr("data-price"))) + '</td></tr>');
                });
                $.each($(".receiptpaymentcontainer"), function(i, v) {
                    receipthtml.push('<tr><td colspan="3">' + $(v).find(".paymentdescription").text() + '</td><td>' + pos.format_price(parseInt($(v).find(".paymentprice").attr("data-price"))) + '</td></tr>');
                });
                receipthtml.push('</table>');
                let now = new Date();
                receipthtml.push('<p>' + asm.user + ' ' + now + '</p>');
                let newwindow = window.open("");
                newwindow.document.write(receipthtml.join("\n"));
                newwindow.print();
                newwindow.close();
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
