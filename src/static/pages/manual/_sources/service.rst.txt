.. _serviceapi:

Service API
===========

ASM includes a service API that you can call from other software via HTTP. To
call the API you construct a URL to the service controller. The service
controller is /service, so if you are accessing a local ASM from your local
machine, the URL will start http://localhost:5000/service. If you are using
sheltermanager.com, the URL will start https://service.sheltermanager.com/asmservice.

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

.. rubric:: Cache time: 1 hour

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

For example, to only output animals with a species of dog, you could use
this callback::

    <script>
    function asm3_adoptable_filter(a, index, arr) {
        return a.SPECIESNAME == "Dog";
    }
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

Additional arguments are also passed to asm3_adoptable_filter containing the
index of the current element and complete list. 
Definition: asm3_adoptable_filter(item, index, arr)

Which dropdowns appear depends on the asm3_adoptable_filters string. To use
them all, include the following asm3_adoptable_filters line. The order in which
they appear in the filters line is also used to output that piece of
information below the animal's name in the list::

    <script>
    asm3_adoptable_filters = "sex breed agegroup size species";
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

Sort
^^^^

You can choose the sort order by setting an asm3_adoptable_sort variable. The default is
ANIMALNAME, but another useful value is -DAYSONSHELTER to output animals based on how
long they've been on shelter with the longest first. Preceding the sort field with a 
minus symbol - will sort in descending order. You can also use precede the sort field with
an at symbol @ to do a numeric sort rather than a string/alphanumeric sort::

    <script>
    asm3_adoptable_sort = "-@DAYSONSHELTER";
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

Limit
^^^^^

You can limit the number of animals rendered by the adoptable_js output. This
is useful if you want to only show a limited number of animals - eg: If this
call is on the home page of your website and you'd like to show some featured
animals.

For example, this will limit output to the first 3 animals in the set. Combined
with the -DAYSONSHELTER sort, it will show the 3 animals who have been on
shelter the longest::

    <script>
    asm3_adoptable_sort = "-DAYSONSHELTER";
    asm3_adoptable_limit = 3;
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

Popup iFrame
^^^^^^^^^^^^

By default, clicking on an animal thumbnail or link will load the target animalview page in a new browser tab. However, the
system can also load the page in a floating iframe so that viewing adoptable
animals does not leave your site. You can enable this behaviour by setting
asm3_adoptable_iframe = true in your script. Eg::

    <script>
    asm3_adoptable_filters = "sex breed agegroup size species";
    asm3_adoptable_iframe = true;
    asm3_adoptable_iframe_fixed = true;
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

By default, the iframe will use absolute positioning. If your page has multiple
screens of vertical height, this will cause it to scroll back to the top when
viewing an animal. Setting asm3_adoptable_iframe_fixed will use fixed
positioning instead, which keeps the position of the parent page when viewing
animals, but this has been found to be less compatible with some browsers and
iframes.

animal_view_adoptable_html
--------------------------

.. rubric:: Cache time: 2 minutes

Returns a complete HTML document that references animal_view_adoptable_js to
show a list of adoptable animals. It looks for an HTML template called
"animalviewadoptable" and falls back to a basic internal template if it does
not exist.

    http://localhost:5000/service?method=&animal_view_adoptable_html

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

Returns an extra image (see :menuselection:`Settings --> Reports --> Extra
Images`).  Pass the name of the image in the title parameter::

    http://localhost:5000/service?method=extra_image&title=splash.jpg

html_adoptable_animals
----------------------

.. rubric:: Cache time: 30 minutes

Returns a complete HTML document containing an HTML page of adoptable animals.

You can pass an HTML template name in an optional "template" parameter (leaving
it off will cause animalview to be used). It is also possible extra parameters:

* speciesid=X - only output animals of that species. In the default dataset, 
  speciesid=1 is Dogs and speciesid=2 is cats.

* animaltypeid=X - only output animals of that type. Run this query at
  the SQL interface to find out the ID numbers: SELECT * FROM animaltype

* locationid=X - only output animals in this location. Run this query at
  the SQL interface to find out the ID numbers: SELECT * FROM internallocation

The rules governing which animals are adoptable are those set under
:menuselection:`Publishing --> Set Publishing Options --> Animal Selection`.
You can view the set at :menuselection:`Publishing --> View Animals Matching
Publishing Options`
 
    http://localhost:5000/service?method=html_adoptable_animals&template=littlebox&speciesid=1
    http://localhost:5000/service?method=html_adoptable_animals

html_adopted_animals
----------------------

.. rubric:: Cache time: 30 minutes

Returns a complete HTML document containing an HTML page of recently adopted
animals.

You can pass an HTML template name in an optional "template" parameter (leaving
it off will cause animalview to be used). It is also possible to pass
speciesid=X or animaltypeid=X parameters to only output animals of that species
and type. In the default dataset, speciesid=1 is Dogs and speciesid=2 is cats.

You can also pass a "days" parameter to indicate how far you would like to
go back. If you do not set it, the default is animals adopted in the last 30
days.
 
    http://localhost:5000/service?method=html_adopted_animals&template=littlebox&speciesid=1&days=60
    http://localhost:5000/service?method=html_adopted_animals

html_deceased_animals
----------------------

.. rubric:: Cache time: 30 minutes

Returns a complete HTML document containing an HTML page of recently deceased 
animals.

You can pass an HTML template name in an optional "template" parameter (leaving
it off will cause animalview to be used). It is also possible to pass
speciesid=X or animaltypeid=X parameters to only output animals of that species
and type. In the default dataset, speciesid=1 is Dogs and speciesid=2 is cats.

You can also pass a "days" parameter to indicate how far you would like to
go back. If you do not set it, the default is animals deceased in the last 30
days.
 
    http://localhost:5000/service?method=html_deceased_animals&template=littlebox&speciesid=1&days=60
    http://localhost:5000/service?method=html_deceased_animals

html_flagged_animals
----------------------

.. rubric:: Cache time: 30 minutes

Returns a complete HTML document containing an HTML page of shelter animals
that have a particular flag.

You can pass an HTML template name in an optional "template" parameter (leaving
it off will cause animalview to be used). It is also possible to pass
speciesid=X or animaltypeid=X parameters to only output animals of that species
and type. In the default dataset, speciesid=1 is Dogs and speciesid=2 is cats.

A "flag" parameter must be passed to specify the flag you want the returned
animals to have. If no flag is set, an error is returned. An "allanimals=1"
parameter can optionally be passed if you'd like all animals to be included,
not just shelter animals.

    http://localhost:5000/service?method=html_flagged_animals&template=littlebox&speciesid=1&allanimals=1&flag=Needs+Foster
    http://localhost:5000/service?method=html_flagged_animals&flag=At+Risk


html_held_animals
----------------------

.. rubric:: Cache time: 30 minutes

Returns a complete HTML document containing an HTML page of current held animals.

You can pass an HTML template name in an optional "template" parameter (leaving
it off will cause animalview to be used). It is also possible to pass
speciesid=X or animaltypeid=X parameters to only output animals of that species
and type. In the default dataset, speciesid=1 is Dogs and speciesid=2 is cats.

    http://localhost:5000/service?method=html_deceased_animals&template=littlebox&speciesid=1
    http://localhost:5000/service?method=html_deceased_animals


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

json_lost_animals, xml_lost_animals, json_found_animals, xml_found_animals
--------------------------------------------------------------------------

.. rubric:: Cache time: 1 hour 

Returns a dataset containing all lost or found animals reported in the last 90
days that are still active.  The method determines whether the format returned
is JSON or XML::

    http://localhost:5000/service?method=xml_found_animals&username=user&password=letmein

json_recent_adoptions and xml_recent_adoptions
----------------------------------------------

.. rubric:: Cache time: 1 hour 

Returns a dataset containing all recently adopted animals with their new owner
information. The method name determines whether the format returned is JSON or
XML::
    
    http://localhost:5000/service?method=xml_recent_adoptions&username=user&password=letmein

json_recent_changes and xml_recent_changes
--------------------------------------------

.. rubric:: Cache time: 1 hour 

Returns a dataset containing all animals who have been modified in the last
month. The method determines whether the format returned is JSON or XML::

    http://localhost:5000/service?method=xml_recent_changes&username=user&password=letmein


json_shelter_animals and xml_shelter_animals
--------------------------------------------

.. rubric:: Cache time: 1 hour 

Returns a dataset containing all animals currently in the care of the shelter.
The method determines whether the format returned is JSON or XML::

    http://localhost:5000/service?method=xml_shelter_animals&username=user&password=letmein

By default, any personal or sensitive data (such as names and contact
information of fosterers and surrenders) will be stripped from the results. If
you wish them to be included, pass an extra sensitive=1 parameter::

    http://localhost:5000/service?method=xml_shelter_animals&username=user&password=letmein&sensitive=1

rss_timeline
------------

.. rubric:: Cache time: 1 hour 

Returns an RSS feed of the timeline for use with feed aggregators::
    
    http://localhost:5000/service?method=rss_timeline&username=user&password=letmein


