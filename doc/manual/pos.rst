Point of Sale (POS) Interface
=============================

ASM provides a simple, flexible point of sale interface to allow users to accept payments 
for goods and services with automatic record keeping and stock management.

This interface was designed with touch enabled devices in mind but can also be used on a 
desktop PC.

To access this interface, follow the "Point of Sale" link under the stock menu.

The point of sale interface makes use of the following existing ASM data:

* Tax Rates - each POS sale must be associated with a tax rate, the tax rates available can be edited via the "Tax Rate" lookup.
* Product Types - POS sales may be associated with a Product Type, the product types available can be edited via the "Product Type" lookup.
* Products - Products created in ASM will be made available to the POS interface.
* Stock levels - Stock levels will be shown in POS during selection and automatically adjusted in repsonse to product sales and returns.

.. note:: Available services may be added as Product Types even though they do not represent a physical product, for example "Donation", "Paddock Hire" or "Dog Grooming".

The receipt records created by the point of sale system are recorded in your ASM 
database where they can be analysed using custom reports.

Using Mobile Devices with Small Screens
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are using the POS interface on a screen less than 800px wide, the embedded number pad and receipt are hidden unless needed. Swiping right will toggle the number pad and swiping left will toggle the receipt.

Processing a sale
-----------------

The Basics
^^^^^^^^^^

* Tap "Start a Transaction".
* Add charges for products/services/donations.
* Accept payment.
* Optionally print a receipt.

.. note:: Managed products are not moved and transaction data is not recorded in the database until the entire transaction has been completed.

Adding Charges Manually
^^^^^^^^^^^^^^^^^^^^^^^

A charge consists of a price, a tax rate and a "type". A charge can be added by:

* Inputting a price on the embedded number pad.
* Choosing a tax rate.
* Choosing a "type".

Selling Managed Products
^^^^^^^^^^^^^^^^^^^^^^^^

The price, tax rate and type of a product can retrieved from the database to speed 
up the process as well as automatically marking the product as sold within ASM.

A product can be selected manually by:

* Choosing a "type".
* Choosing a product.

Alternatively the process can be streamlined by using an external barcode scanner. Assuming 
that the product's barcode is recorded on it's product record. Simply scan the barcode and 
the product will be added to the sale.

Selling Managed Products in Bulk
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Rather than selecting or scanning a product multiple times to add multiple sales, users 
can tap the number of items required on the embedded number pad, tap the "*" button, then 
select or scan the product.

Alternatively, once an item has been added to the receipt, the user can tap on the 
receipt item and edit the quantity using the embedded number pad and confirm the 
change using the "Enter" key.

Voiding Sales
^^^^^^^^^^^^^

The "Void" key is context sensitive. If a receipt item is selected, the "Void" key will 
void that specific receipt item. If no receipt item is selected, the "Void" key will abandon 
the entire transaction and no data will be written to the database, you will be asked to confirm 
voiding the entire transaction.

Taking Payments
^^^^^^^^^^^^^^^

A payment can be taken in two ways.

Simply tapping the "Cash" or "Card" button will assume that the entire outstanding 
balance is being paid in it's entirety.

Alternatively, the amount to be paid may be entered on the embedded number pad followed by 
the "Cash" or "Card" button.

The transaction will continue until the outstanding balance reaches zero.

.. note:: This behaviour can be used to conveniently calculate the change to be given to the customer following a cash payment.

    Lets says that the customer owes 14.56 and pays with a 20.00 note. Enter "2000" on the embedded number pad and tap "Cash". 
    This will leave a balance of -5.44 - the change owed to the customer. Tap cash again and the transaction is complete, no mental arithmetic required.

Refunds
-------

Items added to the receipt when the refund button is active will subtract the value of the 
item from the transaction balance.

Tapping the "Cash" or "Card" button with the refund button active represents a payment TO 
the customer.

