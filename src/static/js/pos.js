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
                ["#090909", "white"]
            ];
            this.nextbuttoncolour = 0;
            this.numpadfocus = null;
            this.activeproduct = {};
            this.activetaxrate = -1;
            this.activereceiptitem = false;
            this.payments = [];
            this.multiplier = 1;
            this.refund = false;
            this.numpadlocked = true;
            this.lastkeypress = new Date();
            this.mode = "idle";
        },

        render: function() {
            this.model();
            let s = [
                '<audio id="asmposshortbeep"><source src="static/audio/shortbeep.mp3" type="audio/mpeg"></audio>',
                '<audio id="asmposbeep"><source src="static/audio/beep.mp3" type="audio/mpeg"></audio>',
                '<audio id="asmposnope"><source src="static/audio/nope.mp3" type="audio/mpeg"></audio>',
                '<div id="posbarcodeinputoverlay">',
                    '<input readonly id="posbarcodeinput" type="text" placeholder="' + _("Waiting for barcode..") + '">',
                '</div>',
                '<div id="findreceipt"><img src="static/images/icons/edit.png"></div>',
                '<div id="findpad"><img src="static/images/icons/accounts.png"></div>',
                '<div id="mobilebalance">0.00</div>',
                '<div id="poscontainer" class="fullheight" style="background-color: #eeeeee;">',
                    '<div id="posleftpanel" style="flex: 100%;">',
                        '<div id="posmenupanel">',
                            '<h1 id="posmenutitle">' + _("ASM Point of Sale") + '</h1>',
                            '<div id="posstartbutton" class="posbuttoncontainer posmenubutton">',
                                '<div class="posbutton" style="background-color: green; color: white;">',
                                    '<div style="display: inline-block;">', 
                                        '<div class="posbuttoncontent">' + _("Start a Transaction") + '</div>',
                                    '</div>',
                                '</div>',
                            '</div>',
                            '<div id="posprintreceiptbutton" class="posbuttoncontainer posmenubutton">',
                                '<div class="posbutton" style="background-color: white; color: black;text-shadow: none;">',
                                    '<div style="display: inline-block;">', 
                                        '<div  class="posbuttoncontent">' + _("Print Receipt") + '</div>',
                                    '</div>',
                                '</div>',
                            '</div>',
                            '<div id="posfullscreenon" class="posbuttoncontainer posmenubutton">',
                                '<div class="posbutton" style="background-color: yellow; color: black;text-shadow: none;">',
                                    '<div style="display: inline-block;">', 
                                        '<div class="posbuttoncontent">' + _("Fullscreen On") + '</div>',
                                    '</div>',
                                '</div>',
                            '</div>',
                            '<div id="posleavebutton" class="posbuttoncontainer posmenubutton">',
                                '<div class="posbutton" style="background-color: blue; color: white;">',
                                    '<div style="display: inline-block;">', 
                                        '<div  class="posbuttoncontent">' + _("Leave Point of Sale") + '</div>',
                                    '</div>',
                                '</div>',
                            '</div>',
                        '</div>',
                        '<div id="postopleftpanel">',
                            '<div id="producttypes">',
                                pos.product_type_buttons(),
                            '</div>',
                            '<div id="taxrates">',
                                pos.tax_rate_buttons(),
                            '</div>',
                        '</div>',
                        '<div id="infopanel"></div>',
                    '</div>',
                    '<div id="transactionpanel">',
                        '<div id="receipt">',
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
                        '</div>',
                        '<div id="numberpad">',
                            '<div id="balancecontainer">',
                                '<div id="balancelabel">' + _("Balance") + '</div>',
                                '<div id="balance" data-balance="0">0.00</div>',
                            '</div>',
                            // '<a name="numpad">',
                            '<table>',
                            '<tr><th colspan="4" id="numpadscreen"></th></tr>',
                            '<tr><td class="numeral">7</td><td class="numeral">8</td><td class="numeral">9</td><td id="deletekey">' + _("Del") + '</td></tr>',
                            '<tr><td class="numeral">4</td><td class="numeral">5</td><td class="numeral">6</td><td id="refundkey">-</td></tr>',
                            '<tr><td class="numeral">1</td><td class="numeral">2</td><td class="numeral">3</td><td id="multiplykey">*</td></tr>',
                            '<tr><td class="numeral">0</td><td class="numeral">00</td><td colspan="2" id="enterkey" class="voidkey">' + _("Void") + '</td></tr>',
                            '<tr><td colspan="2" id="cardbutton">' + _("Card") + '</td><td colspan="2" id="cashbutton">' + _("Cash") + '</td></tr>',
                            '</table>',
                            // '</a>',
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
            if (this.nextbuttoncolour == this.buttoncolours.length) { this.nextbuttoncolour = 0; }
            return [bgcolour, fgcolour];
        },

        product_type_buttons: function() {
            let colours = pos.get_button_colours();
            var producttypes = [
                '<div class="posbuttoncontainer">',
                    '<div class="posbutton producttype" data-producttypeid="0" style="background-color: ' + colours[0] + '; color: ' + colours[1] + ';">',
                        '<div style="display: inline-block;">',
                            '<div class="posbuttoncontent">All</div>',
                        '</div>',
                    '</div>',
                '</div>'
            ];
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
                    );
            });
            return producttypes.join("\n");
        },

        tax_rate_buttons: function() {
            let colours = pos.get_button_colours();
            var taxrates = [];
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
                    );
            });
            return taxrates.join("\n");
        },

        format_price: function(price) {
            let formattedprice = (parseFloat(price) / 100.00).toFixed(2);
                // if (parseInt(price) > 100000000) {
                //     return ( parseInt(formattedprice.split(".")[0]) / 1000000 ) + "M." + formattedprice.split(".")[1];
                // } else if (parseInt(price) > 1000000) {
                //     return ( parseInt(formattedprice.split(".")[0]) / 1000 ) + "K." + formattedprice.split(".")[1];
                // }
            return formattedprice;
        },

        update_layout: function() {
            if ($(window).width() > 800 || pos.mode == "idle") {
                $("#findpad").hide();
                $("#findreceipt").hide();
                $("#mobilebalance").hide();
            } else {
                $("#findpad").show();
                $("#findreceipt").show();
                $("#mobilebalance").show();
            }
            if ($(window).width() > 800) {
                $("#receipt").show();
                $("#numberpad").show();
            } else {
                $("#receipt").hide();
                $("#numberpad").hide();
            }
        },

        update_subtotal: function(next=true) {
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
            $("#mobilebalance").text(pos.format_price(price));
            $("#transactionlog").scrollTop($("#transactionlog").height());

            $("#multiplykey").removeClass("multiply");
            pos.multiplier = 1;

            if (next) {
                pos.mode = "next";
                pos.update_mode();
            }

        },

        reset_focus: function() {
            $(".receiptitemquantity").css("border", "none");
            pos.numpadfocus = null;
            $(this).removeClass("refund");
            pos.refund = false;
        },

        complete_transaction: async function() {
            let receiptdetails = [];
            $.each($(".receiptitemcontainer"), function(i, v) {
                $(v).find(".removereceiptitem").remove();
                let productid = parseInt($(v).find(".receiptitemdescription").attr("data-productid"));
                let quantity = parseInt($(v).find(".receiptitemquantity").text());
                receiptdetails.push(
                    {
                        "productid": productid,
                        "producttypeid": parseInt($(v).find(".receiptitemdescription").attr("data-producttypeid")),
                        "description": $(v).find(".receiptitemdescription").text(),
                        "quantity": quantity,
                        "taxrate": parseFloat($(v).find(".receiptitemtax").attr("data-taxrate")),
                        "price": parseInt($(v).find(".receiptitemprice").attr("data-price"))
                    }
                );
                if (productid) {
                    $.each(controller.products, function(i, v) {
                        if (v.ID == productid) {
                            v.BALANCE += ( quantity * -1 );
                        }
                    });
                }
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
            let formdata = "mode=write&jsondata=" + JSON.stringify(receiptdetails);
            let receiptid = await common.ajax_post("pos", formdata);
            // $("#producttypes").hide();
            pos.mode = "idle";
            pos.update_mode();
            // $("#taxrates").hide();
            // $("#infopanel").hide();
            // $("#posprintreceiptbutton").show();
            // $("#transactionpanel").hide();
            // $("#posmenupanel").show();
        },

        update_mode: function() {
            console.log("mode = " + pos.mode);
            if (pos.mode == "idle") { // Waiting to begin a transaction
                $("#poscontainer").addClass("fullheight");
                $("#postopleftpanel").removeClass("fullheight");
                $("#postopleftpanel").css("height", "auto");
                $("#producttypes").hide();
                $("#taxrates").hide();
                $("#infopanel").hide();
                $("#posprintreceiptbutton").show();
                $("#transactionpanel").hide();
                $("#posmenupanel").show();
                pos.update_layout();
            } else if (pos.mode == "fresh") { // Start of transaction
                $("#poscontainer").removeClass("fullheight");
                $(".receiptitemcontainer").remove();
                $(".receiptpaymentcontainer").remove();
                $(".activeproducttype").removeClass("activeproducttype");
                $("#posmenupanel").hide();
                $("#producttypes").show();
                $("#postopleftpanel").addClass("fullheight");
                $("#infopanel").html("");
                $("#infopanel").hide();
                $("#transactionpanel").show();
                pos.numpadlocked = false;
                $("#refundkey").removeClass("refund");
                pos.refund = false;
                pos.update_layout();
            } else if (pos.mode == "productselected") {
                $("#postopleftpanel").removeClass("fullheight");
                $("#postopleftpanel").css("overflow", "auto");
                $(".activeproducttype").get(0).scrollIntoView();
                $("#postopleftpanel").css("max-height", "50vh");
                // $("#postopleftpanel").css("overflow", "hidden");
                $("#infopanel").show();
                $("#infopanel").get(0).scrollIntoView();
                if ($(window).width() <= 800) {
                    $("#numberpad").hide();
                }
            } else if (pos.mode == "priceinput") {
                $("#producttypes, #infopanel").hide();
                $("#postopleftpanel").addClass("fullheight");
                $("#taxrates").show();
            } else if (pos.mode == "multiply") {
                $("#multiplykey").addClass("multiply");
                $("#numpadscreen").text("");
                $("#producttypes").show();
                $("#postopleftpanel").addClass("fullheight");
                $("#infopanel").html("");
                $("#infopanel").hide();
            } else if (pos.mode == "next") {
                $(".activeproducttype").removeClass("activeproducttype");
                $("#producttypes").show();
                $("#postopleftpanel").addClass("fullheight");
                $("#infopanel").html("");
                $("#infopanel").hide();
            }
            // if (pos.mode != "multiply") {
            //     $("#multiplykey").removeClass("multiply");
            //     pos.multiplier = 1;
            // }
            $("#posbarcodeinput").focus();
            // console.log("Resizing");
            // pos.update_layout();
            // console.log("Resized");
        },

        sync: function() {
            $("body").css("margin", 0);
            // $("html").css("max-height", "100vh");
            $("#currentreceiptitemcontainer").hide();
            $("#asm-topline").hide();
            $("#quicklinks").hide();
            $("#linkstips").hide();
            $("#taxrates").hide();
            $("#producttypes").hide();
            $("#posprintreceiptbutton").hide();
            $("#infopanel").hide();
            
            // $("#numpadscreen").hide();
        },

        bind: function() {
            $("#posbarcodeinput").focus();
            document.getElementById("asmposbeep").volume = 0.2;
            document.getElementById("asmposshortbeep").volume = 0.2;
            document.getElementById("asmposnope").volume = 0.2;
            $(window).resize(pos.update_layout);
            pos.update_mode();
            // pos.update_layout();
            $(".producttype").click(function() {
                if (pos.activetaxrate == -1) {
                    if ($(this).hasClass("activeproducttype")) {
                        pos.mode = "next";
                        pos.update_mode();
                        return;
                    }
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
                                    '<input type="text" id="posproductsearch" class="asm-field asm-textbox" placeholder="' + _("Search") + '">',
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
                        if (producttypeid == 0 || producttypeid == v.PRODUCTTYPEID) {
                            let balance = v.BALANCE;
                            if (!v.BALANCE) {
                                balance = 0;
                            }
                            let medialink = "";
                            if (v.MEDIAID) { medialink = '<a href="image?db=' + asm.useraccount + '&mode=media&id=' + v.MEDIAID + '"><span class="asm-icon asm-icon-media"></span></a>'; }
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
                    pos.mode = "productselected";
                    pos.update_mode();
                } else {
                    let taxrate = pos.activetaxrate;
                    let refund = 1;
                    if (pos.refund) { refund = -1; }
                    let price = parseInt($("#numpadscreen").text()) * refund * pos.multiplier;
                    let taxamount = parseInt(parseFloat(price)  * taxrate);
                    if ( config.bool("VATExclusive") ) {
                        price += taxamount;
                    }
                    $("#transactionlog").append(
                        [
                            '<div class="receiptitemcontainer">',
                                '<div class="receiptitemdescription" data-productid="0" data-producttypeid="0">' + $(this).text().trim() + '<span class="removereceiptitem">X</span></div>',
                                '<div class="receiptitemquantity" data-unitprice="' + price + '">' + (pos.multiplier * refund) + '</div>',
                                '<div class="receiptitemtax" class="posprice" data-taxrate="' + taxrate + '" data-taxamount="' + taxamount + '">' + pos.format_price(taxamount) + '</div>',
                                '<div class="receiptitemprice" class="posprice" data-price="' + price + '">' + pos.format_price(price) + '</div>',
                            '</div>'
                        ].join("\n")
                    );
                    document.getElementById("asmposbeep").play();
                    $("#numpadscreen").text("");
                    pos.activetaxrate = -1;
                    pos.update_subtotal();
                }
            });
            $(".taxrate").click(function() {
                $("#producttypes, #infopanel").show();
                pos.activetaxrate = parseFloat($(this).attr("data-taxrate")) / 100.00;
                $("#taxrates").hide();
                pos.activeproduct = {};
                $(".activeproducttype").removeClass("activeproducttype");
                $("#infopanel").html("");
                $("#producttypes").show();
            });
            $("#numberpad .numeral").mousedown(function() {
                console.log("Numeral detected");
                console.log("Numpad locked = " + pos.numpadlocked);
                console.log(pos.numpadfocus);
                if (pos.numpadlocked) { return false; }
                if (pos.numpadfocus) {
                    console.log($(this).text());
                    $("#numpadscreen").text($("#numpadscreen").text() + $(this).text());
                    if ($("#numpadscreen").text()) {
                        $("#enterkey").removeClass("voidkey");
                        $("#enterkey").text(_("Enter"));
                    } else {
                        $("#enterkey").addClass("voidkey");
                        $("#enterkey").text(_("Void"));
                    }
                } else {
                    if (!$("#numpadscreen").text()) {
                        console.log("First numeral detected");
                        pos.mode = "priceinput";
                        pos.update_mode();
                    }
                    $("#numpadscreen").text($("#numpadscreen").text() + $(this).text());
                }
                // document.getElementById("asmposshortbeep").play();
            });
            $("#deletekey").mousedown(function() {
                if (pos.numpadlocked) { return false; }
                if ($("#numpadscreen").text() == "0.00") {
                    $("#numpadscreen").text("");
                } else if ($("#numpadscreen").text()) {
                    $("#numpadscreen").text($("#numpadscreen").text().slice(0, $("#numpadscreen").text().length - 1));
                }
                if (pos.numpadfocus) {
                    $("#enterkey").removeClass("voidkey");
                    $("#enterkey").text(_("Enter"));
                }
            });
            $("#enterkey").click(function() {
                if (pos.numpadlocked) { return false; }
                if (pos.numpadfocus  && !$("#enterkey").hasClass("voidkey")) {
                    console.log(pos.numpadfocus);
                    // if (pos.numpadfocus.hasClass("posprice")) {
                    //     pos.numpadfocus.text(pos.format_price(pos.numpadfocus.text()));
                    // }
                    if ( pos.numpadfocus.hasClass("receiptitemquantity") ) {
                        let quantity = parseInt($("#numpadscreen").text());
                        pos.numpadfocus.text(quantity);
                        let price = parseInt(pos.numpadfocus.attr("data-unitprice")) * quantity;
                        let taxrate = pos.numpadfocus.next().attr("data-taxrate");
                        taxrate = parseFloat(taxrate);
                        let taxamount = parseInt(parseFloat(price) * taxrate);
                        pos.numpadfocus.next().attr("data-taxamount", taxamount);
                        pos.numpadfocus.next().text(pos.format_price(taxamount));
                        pos.numpadfocus.next().next().attr("data-price", price);
                        pos.numpadfocus.next().next().text(pos.format_price(price));
                        pos.numpadfocus.css("border", "none");
                    }
                    $(".numpadtarget").removeClass("numpadtarget");
                    pos.numpadfocus = null;
                    $("#enterkey").text(_("Void"));
                    $("#enterkey").addClass("voidkey");
                    pos.update_subtotal();
                    if ( $(window).width() <= 800 ) {
                        $("#numberpad").hide();
                    }
                } else if (pos.activereceiptitem) {
                    pos.activereceiptitem.css("text-decoration", "line-through");
                    pos.activereceiptitem.attr("data-voided", "true");
                    pos.activereceiptitem = false;
                    $(".activereceiptitem").removeClass("activereceiptitem");
                    $("#enterkey").text(_("Void"));
                    $("#enterkey").addClass("voidkey");
                    pos.update_subtotal();
                    if ( $(window).width() <= 800 ) {
                        $("#numberpad").hide();
                    }
                } else {
                    if (confirm( _("No data has been written to the database and no stock has been moved. Are you sure that you want to abandon this transaction?"))) {
                        $(".receiptitemcontainer").remove();
                        $(".receiptpaymentcontainer").remove();
                        pos.update_subtotal();
                        // $("#posleftpanel").children().hide();
                        $("#producttypes").hide();
                        $("#taxrates").hide();
                        $("#infopanel").hide();
                        $("#posprintreceiptbutton").hide();
                        $("#posmenupanel").show();
                        $("#numpadscreen").text("");
                        pos.numpadlocked = true;
                        pos.activetaxrate = -1;
                        pos.mode = "idle";
                        pos.update_mode();
                    }
                }
            });
            $("#infopanel").on("keyup", "#posproductsearch", function() {
                let searchkey = $("#posproductsearch").val();
                $.each($(".productcontainer"), function(i, productcontainer) {
                    if ( $(productcontainer).find(".productinfodescription").text().toLowerCase().includes(searchkey.toLowerCase()) ) {
                        $(productcontainer).show();
                    } else {
                        $(productcontainer).hide();
                    }
                });
            });
            $("#infopanel").on("click", ".productcontainer", function() {
                let productid = $(this).attr("data-productid");
                $.each(controller.products, function(i, v) {
                    if (v.ID == productid) {
                        let taxrateid = v.TAXRATEID;
                        let taxrate = 0;
                        let refund = 1;
                        if (pos.refund) { refund = -1; }
                        $.each(controller.taxrates, function(i, v) {
                            if (v.ID == taxrateid) {
                                taxrate = parseFloat(v.TAXRATE) / 100.00;
                                return false;
                            }
                        });
                        let taxamount = parseInt(v.RETAILPRICE * taxrate * pos.multiplier * refund);
                        let price = v.RETAILPRICE * pos.multiplier * refund;
                        if ( config.bool("VATExclusive") ) {
                            price += taxamount;
                        }
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
                        pos.update_subtotal(false);
                        document.getElementById("asmposbeep").play();
                        return false;
                    }
                });

            });
            $("#transactionpanel").on("click", ".receiptitemdescription", function() {
                // if (!pos.numpadfocus) {
                pos.activereceiptitem = $(this).closest(".receiptitemcontainer");
                if (!pos.activereceiptitem) { return false; }
                if (pos.activereceiptitem.hasClass("activereceiptitem")) {
                    pos.activereceiptitem.removeClass("activereceiptitem");
                    pos.activereceiptitem = false;
                    pos.numpadfocus = false;
                    $("#numpadscreen").text("");
                    $("#enterkey").addClass("voidkey");
                    $("#enterkey").text(_("Void"));
                } else {
                    $(".activereceiptitem").removeClass("activereceiptitem");
                    pos.activereceiptitem.addClass("activereceiptitem");
                    pos.numpadfocus = pos.activereceiptitem.find(".receiptitemquantity");
                    $("#numpadscreen").text(pos.activereceiptitem.find(".receiptitemquantity").text());
                    if ( $(window).width() <= 800 ) {
                        $("#numberpad").show();
                    }
                }
                // }
            });
            $("#transactionpanel").on("click", ".paymentdescription", function() {
                if (!pos.numpadfocus) {
                    pos.activereceiptitem = $(this).closest(".receiptitemcontainer");
                    if (pos.activereceiptitem.hasClass("activereceiptitem")) {
                        pos.activereceiptitem.removeClass("activereceiptitem");
                        pos.activereceiptitem = false;
                    } else {
                        $(".activereceiptitem").removeClass("activereceiptitem");
                        pos.activereceiptitem.addClass("activereceiptitem");
                        if ( $(window).width() <= 800 ) {
                            $("#numberpad").show();
                        }
                    }
                }
            });
            // $("#transactionpanel").on("click", ".receiptitemquantity", function() {
            //     $(".activereceiptitem").removeClass("activereceiptitem");
            //     pos.activereceiptitem = false;
            //     if ( !pos.numpadfocus && !$(this).closest(".receiptitemcontainer").attr("data-voided") ) {
            //         pos.numpadfocus = $(this);
            //         pos.numpadfocus.css("border", "1px solid black");
            //         $("#enterkey").text(_("Enter"));
            //         $("#enterkey").removeClass("voidkey");
            //     }
            // });
            $("#cashbutton").on("click", function() {
                if (pos.numpadlocked) { return false; }
                let refund = 1;
                if (pos.refund) { refund = -1; }
                let paymentamount = parseInt($("#numpadscreen").text()) * refund;
                if (!paymentamount) { paymentamount = parseInt($("#balance").attr("data-balance")); }
                $("#numpadscreen").text("");
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
                if (pos.numpadlocked) { return false; }
                let refund = 1;
                if (pos.refund) { refund = -1; }
                let paymentamount = parseInt($("#numpadscreen").text()) * refund;
                if (!paymentamount) { paymentamount = parseInt($("#balance").attr("data-balance")); }
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
                if (pos.numpadlocked) { return false; }
                if (pos.mode == "multiply") {
                    pos.mode = "next";
                    pos.update_mode();
                    return false;
                }
                if ($("#numpadscreen").text()) {
                    pos.multiplier = parseInt($("#numpadscreen").text());
                    pos.mode = "multiply";
                    pos.update_mode();
                    $("#producttypes, #infopanel").show();
                    $("#taxrates").hide();
                }
            });

            $("#refundkey").click(function() {
                if (pos.numpadlocked) { return false; }
                if (pos.refund) {
                    $(this).removeClass("refund");
                    pos.refund = false;
                } else {
                    $(this).addClass("refund");
                    pos.refund = true;
                }
            });

            $("#posleavebutton").click(function() {
                location.href = "main";
            });

            $("#posstartbutton").click(function() {
                pos.mode = "fresh";
                pos.update_mode();
            });

            $("#posfullscreenon").click(function() {
                document.querySelector("body").requestFullscreen();
                $("#posfullscreenon").hide();
            });

            $("#posprintreceiptbutton").click(function() {
                let receipthtml = [
                    '<h3>' + controller.orgname + '</h3>',
                    '<p>' + controller.orgaddress + '<br>' + controller.orgpostcode + '</p>',
                    '<p>' + controller.orgtel + ' ' + controller.orgemail + '</p>',
                    '<table border="1" cellpadding="10px" style="border-collapse: collapse;">',
                    '<tr><th>' + _("Description") + '</th><th>' + _("#") + '</th><th>' + _("Tax") + '</th><th>' + _("Price") + '</th></tr>'
                ];
                $.each($(".receiptitemcontainer"), function(i, v) {
                    receipthtml.push('<tr><td>' + $(v).find(".receiptitemdescription").text() + '</td><td>' + $(v).find(".receiptitemquantity").text() + '</td><td>' + $(v).find(".receiptitemtax").text() + '</td><td>' + pos.format_price(parseInt($(v).find(".receiptitemprice").attr("data-price"))) + '</td></tr>');
                });
                receipthtml.push('<tr><td>' + _("Subtotal") + '</td><td>' + $("#subtotalquantity").text() + '</td><td>' + $("#subtotaltax").text() + '</td><td>' + $("#subtotalprice").text() + '</td></tr>');
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

            // $("#poscontainer").keypress(function() {
            //     console.log("Key press");
            // });

            $("#posproductscan").click(function() {
                // barcode.scan().then(function(scanresult) {
                //     console.log(scanresult);
                // });
                if (!pos.numpadlocked) {
                    if ( $("#posbarcodeinputoverlay").css("z-index") == -1 ) {
                        $("#posbarcodeinput").val("");
                    }
                    $("#posbarcodeinputoverlay").css("z-index", 9998);
                    $("#posbarcodeinput").css("z-index", 9999);
                }
            });
            
            $("#infopanel").on("focusout", "#posproductsearch", function() {
                $("#posbarcodeinput").focus();
            });

            $("#posbarcodeinput").focusout(function(e) {
                if (e.originalEvent.relatedTarget && e.originalEvent.relatedTarget.id == "posproductsearch") {
                    console.log(e.originalEvent.relatedTarget.id);
                    return;
                }
                $("#posbarcodeinput").focus();
            });

            $("#posproductsearch").focusout(function(e) {
                console.log("Lost focus");
                // $("#posbarcodeinput").focus();
            });

            $("#posbarcodeinput").keypress(function(e) {
                if (!pos.numpadlocked) {
                    if ( $("#posbarcodeinputoverlay").css("z-index") == -1 ) {
                        $("#posbarcodeinput").val("");
                    }
                    $("#posbarcodeinputoverlay").css("z-index", 9998);
                    $("#posbarcodeinput").css("z-index", 9999);
                    if (e.keyCode == 13) {
                        console.log("Checking for barcode");
                        $.each(controller.products, function(i, v) {
                            if (v.BARCODE == $("#posbarcodeinput").val()) {
                                console.log("Found barcode");
                                $("#producttypes").find(".posbutton").first().click();
                                let productid = v.ID;
                                console.log(productid);
                                // $(".productcontainer").find("[data-productid='" + productid + "']").click();
                                $(".productcontainer[data-productid='" + productid + "']").click(); 
                                $("#posbarcodeinput").val("");
                                $("#posbarcodeinputoverlay").css("z-index", -1);
                                $("#posbarcodeinput").css("z-index", -1);
                                document.getElementById("asmposbeep").play();
                                return false;
                            }
                            if (i == controller.products.length - 1) {
                                console.log("Nope");
                                document.getElementById("asmposnope").play();
                                $("#posbarcodeinput").val("");
                            }
                        });
                    } else {
                        $("#posbarcodeinput").val($("#posbarcodeinput").val() + e.key);
                    }
                }
            });

            $("#posbarcodeinputoverlay").click(function() {
                $("#posbarcodeinput").val("");
                $("#posbarcodeinputoverlay").css("z-index", -1);
                $("#posbarcodeinput").css("z-index", -1);
            });

            // $("#posstartbutton").on("click", function() {
            //     $("#numberpad").toggle();
            // });

            // $("#posstartbutton").on("click", function() {
            //     $("#receipt").toggle();
            // });

            $("#findpad").click(function() {
                $("#numberpad").toggle();
                // document.querySelector('#cashbutton').scrollIntoView({
                //     behavior: 'smooth'
                // });
            });
            $("#findreceipt").click(function() {
                $("#numberpad").hide();
                $("#receipt").toggle();
                document.querySelector('#receipt').scrollIntoView({
                    behavior: 'smooth'
                });
            });

            $("#postcontainer").on("touchstart", function() {
                console.log("Swiped!");
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
