Documents
=========

Animal Shelter Manager has extensive document abilities for creating forms and
letters. The system also includes its own web-based word processor for handling
this.

To create a document for use with the system, you can manage templates under
:menuselection:`Settings --> Document Templates`. You embed keys in your document
that will be substituted with real data when a document is generated. For a
complete list of document keys, see :ref:`wordkeys`

Keys follow the format <<[Keyname]>>. For example, putting the tag
<<AnimalName>> in your document will cause it to be substituted for the
animal's name. 

.. image:: images/document_menu.png

A number of places in the system have toolbars with generate document buttons,
you can find these: 

* On the animal details screen (creates documents with animal, person and
  movement information, useful for adoption paperwork)

* On the person screen(creates documents with person information) 

* On the payments tab (creates documents with person, payment and animal
  information, useful for invoice and receipt templates)

However you choose to create the document, the process is the same. You select
your document template from the dropdown list.

.. image:: images/html_wp.png

Once you have selected the template, the document will be generated and opened
in the word processor, ready for editing and printing. If you hit the save
button in the word processor, the document will be saved to the appropriate
media tab of the animal/person you generated the document for.

You can also use the PDF button on the toolbar to generate and open a PDF of
the document. This is useful as PDFs will be consistent across different
machines running different operating systems and with different fonts
installed.

.. image:: images/html_wp_to_pdf.png

You can embed directives in your document to give some hints to the PDF engine.
These should take the form of HTML comments, embedded in <!-- and -->, and can
be inserted by going to Tools->Source Code in the document editor::

    <!-- pdf papersize a4 --> 
    
To set the papersize to a4. Other options are a3, a5 and letter::

    <!-- pdf orientation landscape --> 

To set the orientation to landscape. Portrait is the default but can be
explicitly set too.

Electronic Signatures
---------------------

.. image:: images/sign_buttons.png

ASM allows you to add an electronic signature to documents. To do this, select 
the documents you'd like to sign and use either the "Sign" or "Signing Pad"
buttons on the media tab. ASM allows you to use any generic mouse or touchscreen
hardware and mobile touchscreen devices as signing pads - you do not need
to buy expensive custom hardware.

.. image:: images/sign_dialog.png

The "Sign" button shows a signature pad on-screen and allows you to use any
mouse-style device to do the signing. This includes hardware like Wacom
drawing tablets, mice, pens and touchscreen monitors.

After signing, the signature will be attached to the document as a footer along
with the date and time the document was signed.

.. image:: images/sign_doc.png

In addition, an icon will appear next to the document on the media tab to indicate
that the document has now been signed.

.. image:: images/sign_icon.png

Signed documents are read only and cannot be edited. A cryptographic hash for the
signed document is calculated and stored separately so that any future tampering 
can be detected.

When editing your document templates, if you'd like to control the size and
location of the signature, insert an image where you'd like the signature to
appear and when the dialog requests the image source, instead of a URL, enter
"signature:placeholder" without the quotes. The document signing module will
insert the signature inside your image instead of appending a footer.

Mobile Signing
--------------

The "Signing Pad" button allows you to mark the document for signing in the mobile
interface. 

If you visit ASM's mobile interface on any mobile/tablet device, you can use the
"Signing Pad" link in the mobile interface to go into signing pad mode.

.. image:: images/sign_mobilepad.png

.. image:: images/sign_waiting.png

Once in signing pad mode, the interface waits for documents to sign. When
documents are received, they are shown on the mobile interface with a signature
pad at the bottom for the person to sign. This is useful for adoption and other
paperwork and allows you to keep contracts in a completely electronic manner
without the need for paper. You can still print off signed documents or email
them in PDF form to adopters directly.

.. image:: images/sign_mobiledoc.png


