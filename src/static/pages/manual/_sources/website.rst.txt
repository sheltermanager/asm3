.. _websiteintegration:

Appendix: Integrating with Your Website
=======================================

ASM offers a number of methods of integrating your adoptable animal data with
your website.

Javascript Include
------------------

The animal_view_adoptable_js method of ASM's :ref:`serviceapi`
can generate a list of adoptable animal thumbnails for embedding straight into
a div container on a page of your website. 

Clicking on the thumbnails will call the animal_view method of the Service API
for the animal. You can edit the HTML of how that page looks and what
information appears on it by editing the animal_view template under
:menuselection:`Publishing --> Edit HTML publishing templates`

The code snippet required to embed the adoptable animal list in a page on your
website looks like this::
    
    <div id="asm3-adoptables" />
    <script src="https://service.sheltermanager.com/asmservice?method=animal_view_adoptable_js&account=ACCOUNT"></script>

This example is for sheltermanager.com, substitute your own URL in the script
src if you are hosting ASM yourself. Also, if you are using sheltermanager.com,
change ACCOUNT in the src for your sheltermanager.com account.

Wordpress
^^^^^^^^^

To embed your adoptable animals in a Wordpress page, edit the page and add the
javascript include snippet shown above where you'd like your adoptable animals
to appear on the page:

.. image:: images/wordpress_1.png

.. image:: images/wordpress_2.png

Wix
^^^

To embed your adoptable animals in a Wix page, add a content box within the
page where you would like the animals to appear. Make the box as wide as it
needs to be.

.. image:: images/wix_content_box.png

Next, publish your site so that the page is live. Visit the page and use
the browser inspect tool on the content box to find its id attribute. In
the example below, the id is "comp-m8xapztd"

.. image:: images/wix_box_id.png

Now, go to the main settings for your Wix site and pick "Custom Code" from
the bottom of the list.

.. image:: images/wix_settings.png

Click the "Add Custom Code" button. Enter the code snippet below, changing
ACCOUNT for your sheltermanager account number and filling in the id
attribute of your container box::

    <script>
    asm3_adoptable_div_id = "comp-m8xapztd";
    asm3_adoptable_delay = 2000;
    </script>
    <script src="https://service.sheltermanager.com/asmservice?method=animal_view_adoptable_js&account=ACCOUNT"></script>

Finally, choose the page you want to add the custom code to (this will be your
adoptable animals page) and choose "Head" for the "Place code in"
option.

.. image:: images/wix_add_code.png

Further options for animal_view_adoptable.js as documented in the :ref:`serviceapi`
section of the manual can be specified in the custom code snippet if needed.

Dynamic HTML Page 
-----------------

ASM can generate dynamic pages of your adoptable animals on demand with the
service API. The HTML templates are those used by the regular HTML publisher.

For example, to embed a dynamic page of adoptable animals in an iframe on your
website for a sheltermanager.com account::

    <iframe src="https://service.sheltermanager.com/asmservice?account=ACCOUNT&method=html_adoptable_animals" width="100%" height="600px"></iframe>

Static HTML Pages (Publisher)
-----------------------------

ASM can generate a set of static pages from your data with its 
:ref:`htmlftppublisher`. You can configure it under
:menuselection:`Publishing --> Set Publishing Options --> HTML/FTP Publisher`.

The HTML/FTP publisher constructs the static pages using HTML templates, which
you can create under :menuselection:`Publishing --> Edit HTML publishing
templates` and outputs the pages to a folder of your choice, sending them on to
an FTP server of your choice.

Once the site has been created, you can either link directly to it, or embed it
on your website with an iframe tag.

.. warning:: The HTML publisher is no longer available for sheltermanager.com users, use the dynamic HTML page service call outlined above instead.

Service API Data Calls
----------------------

Finally, you can use ASM's Service API to retrieve the adoptable animal
information and images programatically yourself and use that information to
construct a site in any way you wish. 

More information can be found in the section on the :ref:`serviceapi`

