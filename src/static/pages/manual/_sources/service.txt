.. _serviceapi:

Service API
===========

ASM includes a service API that you can call from other software via HTTP. To
call the API you construct a URL to the service controller. The service
controller is /service, so if you are accessing a local ASM from your local
machine, the URL will start http://localhost:5000/service. If you are using
sheltermanager.com, the URL will start https://sheltermanager.com/asm/service.

If you are using sheltermanager.com, or have enabled the option
CACHE_SERVICE_RESPONSES in your sitedefs.py, please be aware that some service
call responses are cached for performance. The cache time is indicated with the
call below.

While the examples here show passing the parameters with HTTP GET requests, you
can POST the parameters too if you prefer.

The service requires the following parameters:

* account: If this is a sheltermanager.com service call, the user's account
  number. Can be omitted for other installations.

* username: A valid ASM user.

* password: A valid ASM password. From a security standpoint, it's better to
  create at least one ASM user dedicated to calling the service to assist with
  audit trails and to lock it down so an attacker with the URL cannot change
  your data or view anything you don't want them to.

* method: A service method to call

* animalid / title: An animal ID or title depending on the service method
  called.

The following method values are supported:

animal_image
------------

.. rubric:: Cache time: 1 day

Returns an animal's preferred image. Send the id of the animal::

    http://localhost:5000/service?method=animal_image&animalid=520&seq=1

An optional "seq" parameter can be included to return the animal's other
available images. seq=1 returns the preferred image (and will be assumed if
that parameter is omitted), seq=2 returns the second available image, etc. seq
is a 1-based count and can be used with the "WebsiteImageCount" property
included in animal records (which contains the number of images an animal has)
to programatically grab all the images for a particular animal.

animal_thumbnail
----------------

.. rubric:: Cache time: 1 day

Returns an animal's preferred image as a thumbnail. Send the id of the animal::
    
    http://localhost:5000/service?method=animal_thumbnail&animalid=520

The thumbnail will be sized to whatever the main application is using
(typically 150 pixels along the longest side).

animal_view
-----------

.. rubric:: Cache time: 2 minutes

Returns a webpage with information for one animal, constructed from the
animal_view HTML publishing template (editable at :menuselection:`Publishing ->
Edit HTML publishing templates`). Pass the id of the animal::

    http://localhost:5000/service?method=animal_view&animalid=520

When you use :menuselection:`Share --> Link to this animal` on an animal's record, 
it is this service call that the system redirects you to.

animal_view_adoptable_js
------------------------

.. rubric:: Cache time: 10 minutes

Returns a javascript file that when executed injects thumbnails of all
adoptable animals into the page with links to the animal_view service call. It
is most useful as the src attribute for a <script> tag.

The page must contain a div with an id attribute of "asm3-adoptables", where
the adoptable animal thumbnails are to appear. If div#asm3-adoptables cannot be
found, a popup error message will appear.

Here's an example page showing how to inject your adoptable animal list::

    <!DOCTYPE html>
    <html>
    <head>
    <title>Adoptable Animals</title>
    <style>
    .asm3-adoptable-thumbnail { border-radius: 8px; }
    </style>
    <body>
    
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

    </body>
    </html>

CSS and Styles
^^^^^^^^^^^^^^

The adoptable_js output is unstyled - just a thumbnail with a name/link below
and two lines of brief text containing some basic information about the animal.
You can style this information by adding CSS to your stylesheets for the
following classes:

* asm3-filters : The div surrounding the SELECT dropdown filters
* asm3-adoptable-list: The div surrounding all the animal thumbnails
* asm3-adoptable-item : The div surrounding each animal thumbnail
* asm3-adoptable-link : The a tag enclosing the thumbnail and animal name
* asm3-adoptable-thumbnail : The thumbnail img tag
* asm3-adoptable-name : The animal's name
* asm3-adoptable-tagline : The brief animal information

and the following elements by their id attribute:

* asm3-adoptable-iframe-overlay: The div surrounding the popup iframe (if used)
* asm3-adoptable-iframe-close: The close link at the top right of the popup
* asm3-adoptable-iframe: The popup iframe itself

Eg: To add rounded corners to the thumbnails and show the animal's name in
bold, add this to your CSS::

    .asm3-adoptable-name { font-weight: bold; }
    .asm3-adoptable-thumbnail { border-radius: 8px; }

To increase the size of the close link, add this::

    #asm3-adoptable-iframe-close { font-size: 200%; }

Translations
^^^^^^^^^^^^

It's possible to translate any of the text output by the adoptable list on the
fly. By default, it only uses text from your database values so they will match
the language of your database. 

You can add on-the-fly translation by adding a script tag with a dictionary
called asm3_adoptable_translations above the script that makes the service
call. Eg to translate some English species to French and to change the default (any
species) to all as well as the CLOSE link text::

    <script>
    asm3_adoptable_translations = {
        "Dog": "Chien",
        "Cat": "Chat",
        "Pig": "Cochon",
        "(any species)": "all",
        "CLOSE": "Return to my webpage"
    }
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>


Filters
^^^^^^^

You can also add a filter callback, which allows you to implement your own
filter based on other elements in the page. The callback receives the complete
animal record and must return true if the record is to be included in the list
of thumbnails.

For example, to only output animals with an animal type of dog, you could use
this callback::

    <script>
    function asm3_adoptable_filter(a) {
        return a.ANIMALTYPENAME == "D (Dog)";
    }
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

Which dropdowns appear depends on the asm3_adoptable_filters string. To use
them all, include the following asm3_adoptable_filters line. The order in which
they appear in the filters line is also used to output that piece of
information below the animal's name in the list::

    <script>
    asm3_adoptable_filters = "sex breed agegroup size species";
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

Extra Content
^^^^^^^^^^^^^

It's also possible to add an extra content callback, which adoptable_js calls
for every animal it outputs. For example, to add the animal's bio below the
thumbnail and basic info::

    <script>
    asm3_adoptable_filters = "sex breed agegroup size species";
    asm3_adoptable_extra = function(a) {
        return a.WEBSITEMEDIANOTES;
    }
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

You could set .asm3-adoptable-tagline to display: none and then use an extra
content callback to output and format any data from the animal's record in the
way you want and override the default behaviour.

Popup iFrame
^^^^^^^^^^^^

By default, clicking on an animal thumbnail or link will load the target animalview page in a new browser tab. However, the
system can also load the page in a floating iframe so that viewing adoptable
animals does not leave your site. You can enable this behaviour by setting
asm3_adoptable_iframe = true in your script. Eg::

    <script>
    asm3_adoptable_filters = "sex breed agegroup size species";
    asm3_adoptable_iframe = true;
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

Some positioning styles for the iframe have to be supplied programatically and
cannot be set by CSS (everything else can be), but there are a couple of
javascript variables you can set for them instead. 

Eg: To fix the iframe height at 2000 pixels and use a gray background instead
of the default of white::

    <script>
    asm3_adoptable_filters = "sex breed agegroup size species";
    asm3_adoptable_iframe = true;
    asm3_adoptable_iframe_height = "2000px";
    asm3_adoptable_iframe_bgcolor = "#888";
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

csv_mail and csv_report
-----------------------

.. rubric:: Cache time: 10 minutes

Returns a CSV file containing a mail merge or report. Pass the name of the mail
merge/report in the title attribute and if the merge requires any parameters,
you can pass those too just like with html_report::

    http://localhost:5000/service?method=csv_report&username=user&password=letmein&title=Detailed+Shelter+Inventory

extra_image
-----------

.. rubric:: Cache time: 1 day

Returns an extra image (see :menuselection:`Settings->Reports->Extra Images`).
Pass the name of the image in the title parameter::

    http://localhost:5000/service?method=extra_image&title=splash.jpg

html_report
-----------

.. rubric:: Cache time: 10 minutes

Returns an HTML document containing a report. Pass the name of the report in
the title attribute. If the report requires any parameters, you can pass those
too. VAR parameters are just their name, ASK parameters are ASKn where n is the
order within the SQL. If you run the report within the ASM frontend you will
see the parameters it requires in the address bar::

    http://localhost:5000/service?method=html_report&username=user&password=letmein&title=Detailed+Shelter+Inventory

json_adoptable_animal and xml_adoptable_animal
----------------------------------------------

.. rubric:: Cache time: 1 hour

Returns a dataset containing a single animal record from the list of animals
available for adoption. The method determines whether the format returned is
JSON or XML::

    http://localhost:5000/service?method=xml_adoptable_animal&animalid=123&username=user&password=letmein

.. note:: If the animal with animalid is not adoptable, an empty result set will be returned.

json_adoptable_animals and xml_adoptable_animals
------------------------------------------------

.. rubric:: Cache time: 1 hour 

Returns a dataset containing all animals available for adoption. The method
determines whether the format returned is JSON or XML::

    http://localhost:5000/service?method=xml_adoptable_animals&username=user&password=letmein

json_recent_adoptions and xml_recent_adoptions
----------------------------------------------

.. rubric:: Cache time: 1 hour 

Returns a dataset containing all recently adopted animals with their new owner
information. The method name determines whether the format returned is JSON or
XML::
    
    http://localhost:5000/service?method=xml_recent_adoptions&username=user&password=letmein

json_shelter_animals and xml_shelter_animals
--------------------------------------------

.. rubric:: Cache time: 1 hour 

Returns a dataset containing all shelter animals. The method determines whether
the format returned is JSON or XML::

    http://localhost:5000/service?method=xml_shelter_animals&username=user&password=letmein

rss_timeline
------------

.. rubric:: Cache time: 1 hour 

Returns an RSS feed of the timeline for use with feed aggregators::
    
    http://localhost:5000/service?method=rss_timeline&username=user&password=letmein


