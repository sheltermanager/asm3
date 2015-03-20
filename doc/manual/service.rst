Service API
===========

ASM includes a service API that you can call from other software via HTTP. To
call the API you construct a URL to the service controller. The service
controller is /service, so if you are accessing a local ASM from your local
machine, the URL will start http://localhost:5000/service. If you are using
sheltermanager.com, the URL will start https://sheltermanager.com/asm/service.
The service requires the  following parameters:

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

**animal_image**

Returns an animal's preferred image. Send the id of the animal::

    http://localhost:5000/service?method=animal_image&animalid=520

**extra_image**

Returns an extra image (see *Settings->Reports->Extra Images*). Pass the name
of the image in the title parameter::

    http://localhost:5000/service?method=extra_image&title=splash.jpg

**json_adoptable_animals | xml_adoptable_animals**

Returns a dataset containing all animals available for adoption. The method
determines whether the format returned is JSON or XML::

    http://localhost:5000/service?method=xml_adoptable_animals&username=user&password=letmein

**json_recent_adoptions | xml_recent_adoptions**

Returns a dataset containing all recently adopted animals with their new owner
information. The method name determines whether the format returned is JSON or
XML.

**html_report**

Returns an HTML document containing a report. Pass the name of the report in
the title attribute. If the report requires any parameters, you can pass those
too. VAR parameters are just their name, ASK parameters are ASKn where n is the
order within the SQL. If you run the report within the ASM frontend you will
see the parameters it requires in the address bar::

    http://localhost:5000/service?method=html_report&username=user&password=letmein&title=Detailed+Shelter+Inventory

**csv_mail**

Returns a CSV file containing a mail merge. Pass the name of the mail merge in
the title attribute and if the merge requires any parameters, you can pass
those too just like with html_report.

**json_shelter_animals | xml_shelter_animals**

Returns a dataset containing all shelter animals. The method determines whether
the format returned is JSON or XML.


