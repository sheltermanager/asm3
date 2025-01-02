Getting Started
===============

.. image:: images/login.png

On starting ASM for the first time, you will be prompted to log in to the
system. The default username is “user” with the password “letmein”. If there
are no animals in the database, ASM will remind you of these defaults in the
dialog. 

.. image:: images/home_screen.png

Once logged in, ASM's home screen will appear. Across the top, a menu bar is
used to navigate the system. 

At the top right, a keyword search box allows you to quickly locate any type of
record within ASM and the user menu shows the currently logged in user, the
locale and allows user specific actions to be taken (changing the current
user's password, logging out of the system).

The default landing page shows recently changed animals, alerts for any actions
that need to be taken, current diary tasks to be performed today, any messages
from other users and news from the ASM website. Additionally, this pane will
show a series of user-configurable quicklinks for quickly getting to different
areas of the system.

Menus and Shortcuts
-------------------

.. image:: images/menu.png

You open screens in ASM by navigating and clicking on menu items. Menu items
are laid out across the top of the screen.

Shortcut Keys
-------------

Some of the most common menu commands can be actioned by pressing combinations
of certain keys. These keys are known as shortcut keys or accelerators.
Pressing these keys is the same as navigating the menu and clicking on them
with the mouse. 

If a menu command has a shortcut key, it will be displayed at the side of it in
the menu. For example, the Add Animal option on the menu can be accessed by
pressing :kbd:`ALT+SHIFT+N` - this means you hold down the shift and alt keys
together, and tap N. It is worth learning these as you will find them much
quicker to use when you are proficient with the system. 

There are some additional shortcut keys you can use (some depend on which
browser you have):

* :kbd:`CTRL+H` will return to the home screen
* :kbd:`CTRL+S` will save the current screen (animal, person details, etc).
* :kbd:`CTRL+R` or :kbd:`F5` will reload the current screen.
* :kbd:`CTRL+W` will close the current browser tab
* :kbd:`CTRL+A` will select all items on screens that display a table with multiple
  items (eg: Foster book, Vaccination Book, etc).
* :kbd:`CTRL+LMB` (left mouse button) when clicking a link will open that link
  in a new tab.

Dates
-----

.. image:: images/dates.png

It is worth mentioning early on that Animal Shelter Manager has a keyboard user
interface for dealing with dates (as well as the more usual calendar). Every
field within the system where a date is expected, the following keyboard
shortcuts can be used: 

* :kbd:`T` Today
* :kbd:`Y` Today + 1 year
* :kbd:`M` Today + 1 month
* :kbd:`W` Today + 1 week
* :kbd:`D` Today + 1 day
* :kbd:`SHIFT + (YMWD)` Today less 1 year/month/week/day
* :kbd:`CTRL + Cursor Keys` Move the date selector around (up/down is +/- one week)
* :kbd:`CTRL + PgUp/PgDn` go forwards and backwards 1 month.

Tables
------

.. image:: images/table.png

ASM uses tables to display data throughout the application. You can sort any
table in ascending order by clicking on the column heading you wish to sort on.
If you click the column heading again, it will be sorted in descending order
instead.  Hold down shift while clicking to sort on multiple columns at the
same time.

A system setting :menuselection:`Settings --> Options --> Display --> Keep
table headers visible when scrolling` allows the table headers to float at the
top when you scroll the screen if desired. 

In addition, if you need to select any items in a table, tickboxes will appear
down the left hand side. Any actions you can take on selected items in a table
will be via buttons above the table.

The keyboard shortcut :kbd:`CTRL + A` can be used to select all items in the
currently visible table.

Initial Setup
-------------

Before doing anything else with your new ASM installation, you should now
perform the initial configuration of ASM for your shelter. The steps are as
follows: 

1. If you want to use your own animal classifications, you can use the
   :menuselection:`Settings --> Lookup Data --> Animal Types` to alter the
   standard ASM ones - ASM assumes your shelter deals with dogs and cats and
   wants to differentiate between stray, feral and abandoned animals. It also
   has an extra type for boarding, which allows you to generate separate figures
   for boarding animals. 
   After doing that, select your new defaults in the correct place on the
   :menuselection:`Settings --> Options --> Defaults` screen.

2. Go to the :menuselection:`Settings --> Options --> Details` screen and enter
   your shelter's details. You can set all of the systemwide behaviours for ASM
   and control the format of generated animal codes from the other tabs on this 
   screen as well.

3. Go to :menuselection:`Settings --> Lookup Data --> Locations` to setup your
   available shelter locations. A location can have multiple units, which you
   list in the "units" box of the location, separated by a comma. Locations can
   be anything you want - eg: a room, an area of a room, a building. Units are
   individual areas, pens or cages within that location.  For example, you
   could create a location called "Dog Block A" with units "1, 2, 3, 4, 5" to
   have 5 numbered pens.  When you use shelter view, you can have it group by
   the location or the location and unit and it will allow you to drag and drop
   animals between pens and locations to move them around. It will also 
   highlight empty pens so you can see capacity at a glance.

4. Go to :menuselection:`Settings --> Lookup Data --> Breeds` - Remove any
   unwanted breeds and species from the database that your shelter does not
   deal with.

5. Go to :menuselection:`Settings --> Reports --> Browse sheltermanager.com` and
   install some reports. The "Select Recommended" button allows you to quickly
   choose our recommended set for installation.

6. Create usernames and passwords for all your shelter staff in the
   :menuselection:`Settings --> System User Accounts` screen. Once you have
   your own username and password, delete the default “user” user. It is
   advised that everyone has their own username and password rather than
   using a shared account as it makes it easier to revoke individual permissions
   or remove the account when staff leave without disrupting everyone else.

User Settings
-------------

The user menu at the top right of the screen shows the currently logged in user.
In this menu, the user can find:

.. image:: images/user_settings.png

* Switch to Mobile Interface - Change from the desktop user interface to the 
  mobile user interface.

* Change Password - Choose a new login password.

* Change User Settings - Change settings specific to the user.

* Logout - Log out of the system.    

The option "Change User Settings" contains the following settings:

.. image:: images/change_user_settings.png
 
* Username - Current username (cannot be edited).

* Real Name - The users real name.

* Email Address - The users email address, can optionally be set as the default
  reply address when the user sends an email.

* Visual Theme - Allows the user to set different coloured themes.

* Locale - Allows the user to choose a different language/currency.

* Quicklinks - Allows the user to create links at the top of the screen to 
  quickly access the parts of the system they use the most.

* Quick Reports - This will add a dropdown menu of selected reports to the quicklinks 
  bar, reports will appear in the menu in the order they are selected here.
  
* Shelter view - Allows the user to set their own shelter view overiding the system
  default view if one is set.

* Signature - The users electronic signature to be used in document templates.

* Two-Factor Authentification (2FA) - Users can enable 2FA here using the 
  Google Authenticator app, see :ref:`Two-Factor Authentification`
  


