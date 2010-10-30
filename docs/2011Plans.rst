.. _2011Plans-doc:

==========================
 RandoPony Plans for 2011
==========================

:Author: Doug Latornell
:Created: 2010-09-26

This document outlines my plans for improvements and additions to the
RandoPony for 2011. Apart from getting my thoughts in order, the
purpose is to provide a solid basis for discussion of those plans with
Susan, Ross, Alex, and perhaps others.

The plan has 3 major components:

* :ref:`NewFeaturesForEventPre-Registration-section`
* :ref:`NewAppForPre-RegistrationForPopulaires-section`
* :ref:`SiteAndCodebaseMaintenance-section`


Background
==========

Event pre-registration started life as a simple app to provide an
online tool that would encourage riders to pre-register for *brevets*
to provide the brevet organizer with an estimate of the number of
riders that would ride the brevet, and their names so that control
cards and rider lists for the controls could be prepared in advance.

The brevet organizers are the ones that the event pre-registration app
was designed for. A side effect is that the riders get to see who else
is planning to ride a brevet, and links to enable them to fill out and
print the event waiver, and club membership forms.

With the night start of the spring LM400 in 2010 and the initial
emphasis that the ACP put on that event as a PBP qualification hurdle,
Susan wanted to ensure that riders for that event were qualified by
having previously ridden a 300. So, the app includes the ability to
pose a question on the registration form, and transmit the answer to
the brevet organizer by email.

Apart from providing a service to brevet organizers, the other design
goal of the pony was that it should require a minimun of
administrative attention. Adding a new brevet should take no more than
a minute or 2, and after that everything should be automatic. I'm
happy to spend time improving the pony (mainly in the fall and
winter months) but I don't want to spend a lot of time administering
it. That's why, for instance, I put the onus on the brevet organizer
to provide all of the information that the pony needs in an email to
me, and why there is no mechanism for deleting riders who decide that
they can't or don't want to ride a brevet that they have
pre-registered for.

The RandoPony caught on well in 2010 with both brevet organizers and
riders.

For the 2010 SuperWeek events Alex requested the addition of a way for
people to sign up for non-brevet events, specifically, dinners. That
was added, and subsequently a similar feature for club events like the
AGM was hacked in.

It is increasingly obvious that the way that non-brevet events were
hacked in is sub-optimal. 

* Should pre-registration for non-brevet events (AGM, Spring Social,
  dinners during Hell Week, SuperWeek, etc.) be kept in the pony?

If so, that feature needs to be refactored (see
:ref:`ImproveNon-RidingEventsImplementation-section`).

The possibility of 2 start times for 1000s was also added, and the
qualification question functionality was morphed into a more general
information question. In the context of a 1000, where the question is
used to collect the rider's planned start time, their answer is
displayed on the rider list as well as being included in the email to
the organizer.


.. _NewFeaturesForEventPre-Registration-section:

New Features for Event Pre-Registration
=======================================

Features Requested by Brevet Organizers
---------------------------------------

* Include the rider's email address in the email sent to the brevet
  organizer when a rider pre-registers (see `issue 9`_ on bitbucket).

  * That the rider's email address is *not* in that message is a
    design error that probably arose from excessive caution about
    personal information. This is trivial to fix.

.. _issue 9: https://bitbucket.org/douglatornell/randopony/issue/9

* Allow multiple brevet organizer email addresses (see `issue 7`_ on
  bitbucket).

  * A few brevets have tag-team organizers (e.g. 2010 VI summer 600,
    and LM Thanksgiving 1000). It looks fairly easy to add this
    functionality.

.. _issue 7: https://bitbucket.org/douglatornell/randopony/issue/7

* Add mechanism to provide list of rider's email addresses for an
  event (see `issue 10`_ on bitbucket).

.. _issue 10: https://bitbucket.org/douglatornell/randopony/issue/10


Make Event Waiver and Membership Form Fields Editable
-----------------------------------------------------

Alex proposed changing the event waiver form so that riders can fill
in their name, etc. in Adobe Reader before printing it instead of
having to hand-write the information after printing.

This should be easy to do by someone who has access to Adobe Acrobat
Pro (I may have at work), or via the free trial of
http://createpdf.adobe.com/

* Should we consider making the same change to the club membership
  form?

* While we're at it, should we add a field to the event waiver form
  like SIR does asking the rider to provide the number of a mobile
  phone that they will be carrying with them on the ride? 


.. _GenerateRiderListsForBrevets-section:

Generate Rider Lists for Brevets
--------------------------------

The big idea is to have the pony automatically generate a Google Docs
spreadsheet that is at least the basis of the organizer's rider list
for the brevet. The spreadsheet will include:

* Rider's first name
* Rider's last name
* Membership status declared on pre-registration form

The spreadsheet will be managed programmatically via the `Google Docs
API Python client library`_.

.. _Google Docs API Python client library: http://code.google.com/apis/documents/docs/1.0/developers_guide_python.html

The pre-registration form will be changed to have the rider enter
their first and last names in separate fields, and the database will
be changed to support that separation.

A field will be added to the brevet model in the database to store the
link to the spreadsheet.

The brevet organizer will have the riders' emergency contact numbers
(and ride day mobile phone number, if we add that feature) on the
event waivers.

* A read-only link to the spreadsheet with anonymous viewing access
  will be emailed to the brevet organizer when the brevet is added to
  the pony. The spreadsheet access settings will be such that only
  users with the link will be able to find or view it.

* The spreadsheet will be updated automatically as each rider
  pre-registers. Whether that happens by adding rows incrementally to
  the spreadsheet, or by re-writing the whole sheet is TBD. The latter
  option provides the possibility of keeping the sheet sorted by
  surname (for instance).

* The brevet organizer can view the spreadsheet at any time, and save
  a copy of it for their own manipulation and printing. The email they
  get when the  brevet is added to the pony, and perhaps the
  spreadsheet itself, needs to emphasis that it will continue to
  change until brevet pre-registration closes at noon on the day
  before the event starts.

* An automated mechanism to delete the spreadsheet 7 days after the
  event would be nice, otherwise this will have to be done manually. 7
  days after the event aligns the life of the spreadsheet with the
  life of the riders list page on the pony.


Automate Organizer and Webmaster Notification
---------------------------------------------

This is mostly a small tweak to further reduce the admin work on the
pony. Presently, I send an email message to the brevet organizer and
Eric with a link to the rider list page for the brevet and a request
to Eric to add it to the brevet page on randonneurs.bc.ca. With the
design described :ref:`above <GenerateRiderListsForBrevets-section>`
for the generation of rider list spreadsheets the database will have
to be queried to get the URL of the Google Docs spreadsheet, so an
admin action that does so makes sense, and it is a small step from
that to having that action generate and send the emails to the brevet
organizer and Eric.


Miscellaneous Changes
---------------------

* Is there value in sending emails when riders pre-register and there
  is no information question associated with the event? We could
  default to not sending these emails unless the brevet organizer
  requests them. That option would be added to the `Info for Brevet
  Organizers`_ page.

.. _Info for Brevet Organizers: http://randopony.sadahome.ca/register/organizer_info/

* Change pre-registration form to collect rider's first and last names
  separately so that they can be stored separately in the database and
  lists can be sorted by either. 


Features that Will Not be Added
===============================

On-line Payment for Brevets
---------------------------

Although a similar PayPal or Google Checkout mechanism to that under
consideration for Populaires could be implemented for brevets, it does
not seem to be worthwhile, and may lead to more work, rather than less
for the brevet organizers (the primary beneficiaries of the pony -
remember?!):

* Making online payment mandatory at time of pre-registration would be
  a disincentive to pre-registration for many riders who decide to
  rider some events based on weather. We don't want to loose the
  benefits of pre-registration, so payment would have to be optional,
  so brevet organizers will still have to handle money at the
  start. Most brevets do not have so many riders that the difference
  of a few online pre-payments will be that noticeable.

* Despite the fact that the event fee is only $15, there will
  inevitably be people who pre-pay then don't ride and request refunds
  from the brevet organizer. This also violates the pony's primary
  goal of making life easier for brevet organizers.

Bottom line, online payment for brevets seems to me like more trouble
than it is worth. If anyone has a compelling argument otherwise, I
invite them to write it up for discussion.


.. _NewAppForPre-RegistrationForPopulaires-section:

New App for Pre-Registration for Populaires
===========================================

Background
----------

Danelle and I had a lengthy email conversation in late 2009 about
providing on online pre-registration system for the Pacific
Populaire. After the launch of the RandoPony in early 2010 I also had
an enquiry from Dave McMurchie about using it for the Vancouver Island
Populaire.

Pre-registration for populaires is different from that for brevets in
that:

* The events are generally multi-distance (e.g. 25, 50 and 100 km).
* There can be more than one price (e.g. $15 for BC Rando members, $18
  for non-members, $10 for under 19 years old)
* There can be a factor of 10 (or greater) more riders than on a
  brevet.
* The goal of the pre-registration is to reduce the ride-day work to
  simply handing a route card to the rider, and perhaps checking their
  name off on a list.

In my mind there are 3 dimensions to such a system:

* Managing the rider's personal information
* Acceptance of the event waiver by the rider
* Handling credit card payments

The credit card payment handling is relatively straight forward and is
discussed :ref:`below <CreditCardPaymentHandling-section>`.

Event waiver acceptance is a legal issue. Anecdotally we know that
this issue has apparently been solved by any number of sites that
handle online event registration. We need to ensure that whatever
click-through mechanism we implement is as legally binding on the
rider, and is acceptable to our insurer as their written signature on
the present event waiver is so that we do not open the club, the
executive members, or me to any liability that we do not currently
have.

The discussion with Danelle ended because she had an apparently
non-negotiable requirement that we collect rider's full address and
telephone number and send it to her in an email message as each rider
signed up. Doing so would be poor, if not illegal, management of
personal information because plain text email messages are totally
unsecured and their content can be read, duplicated, and re-transmitted
by anyone with access to any of the servers that they pass through
between the sender and the recipient. I offerred Danelle the option of
sending this information via encrypted email, which she would take
responsibility for decrypting, and received no response.

I believe that a component can be added to the RandoPony to handle
pre-registration for the Pacific Populaire, and other populaires
(Canada Day, Vancouver Island). I'll describe my present thoughts on
implementing such a system below. The alternative for the club to
consider is the use of an event registration service such as
`karelo.com`_, `zone4.ca`_, `eventsonline.ca`_, or
`cyclecomponentnetwork.com`_.

.. _karelo.com: http://karelo.com/
.. _zone4.ca: http://zone4.ca/
.. _eventsonline.ca: http://eventsonline.ca/
.. _cyclecomponentnetwork.com: http://www.cyclecomponentnetwork.com/


.. _Rider'sPersonalInformationManagement-section:

Rider's Personal Information Management
---------------------------------------

The 2 components of this are:

* Collect only the information that we need
* Always transmit the information securely (via HTTPS)


Personal Information That We Need
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

I believe that the personal information that we need for populaire
riders is:

* First name
* Last name
* Whether rider is a member of BC Randonneurs
* Emergency contact phone number
* Phone number of mobile phone they are carrying on the ride
* Acceptance of event waiver
* Whether rider is over or under 19 years of age

The justification I have heard for collecting the rider's address is
that it may be needed to send them their pin if we run out. However,
it is unreasonable to collect, store and transmit electronically
hundreds of addresses on the small possibility that a few will be
needed for that purpose. The running out of pins issue can be managed
in other ways:

* The combination of a pre-registration system and previous years
  event participation numbers should allow the organizers to order
  close to the correct number of pins.
* Populaire pins are undated so left-overs from pervious years can be
  used when the current year's run out. Most riders have no idea about
  the colour rotation scheme that is used.
* As is already done, club members are not given pins at the finish if
  there is going to be a shortage because they can be given theirs
  later from a 2nd order.
* If the pins do run out the late finishing riders can be asked to
  write their name and address on an envelop so that their pin can be
  mailed to them when available.

If there are other compelling use cases for collection of populaire
rider addresses and home phone numbers, I would appreciate if they
could be written up for discussion.


Transmission Via HTTPS
~~~~~~~~~~~~~~~~~~~~~~

* Add an SSL certificate to the randopony.sadahome.ca domain so that
  data entered by the rider on the pre-registration form is
  transmitted via HTTPS from their browser to the Randopony server.

  * There are a variety of price points for SSL certificates, ranging
    from ~$25/yr to ~$325/yr. I need to do some research to figure out
    the differences and determine which is appropriate; hopefully
    something near the lower end of the price range.

* Deliver data to populaire organizers by way of Google Docs
  spreadsheets. Google Docs uses HTTPS, so the data is transmitted via
  HTTPS from Google's servers to the organizer's browser.

  * Populaire organizers will be required to have a Google Docs
    account (free) which they will sign in to in order to access the
    spreadsheets generated by RandoPony. Note that this is a higher
    level of security and authentication than will be required for
    brevet organizers to access their event spreadsheet. This is
    because the populaire spreadsheet will contain more personal
    information than the brevet ones.

* Manage the Google Docs spreadsheets from RandoPony programmatically
  via the `Google Docs API Python client library`_ so that data is
  transmitted from the RandoPony server to the Google servers via
  HTTPS. 


.. _WaiverAcceptanceHandling-section:

Waiver Acceptance Handling
--------------------------

My preference would be to have a paid legal opinion from a lawyer
familiar with web technology and liability in the context of our
events. I would like to be present for the discussion with that lawyer
so that I can be sure that I understand directly the requirements for:

* the presentation of the waiver
* the action required of the user to accept it
* the storage of that acceptance 


.. _CreditCardPaymentHandling-section:

Credit Card Payment Handling
----------------------------

Credit card payment handling will be delegated to a 3rd party service
because that is the only mechanism that makes economic sense given the
relatively low number and "spiky" timing of transactions for
populaires; i.e. a few hundred transactions (at most) clustered in 1
or 2 months for each event, with no overlap between the 2 big events
(PacPop and Canada Day).

I have briefly investigated 3 credit card transaction services:

* `PayPal Canada`_
* `Google Checkout`_
* `Amazon Payments`_

.. _PayPal Canada: https://www.paypal.ca/
.. _Google Checkout: https://checkout.google.com/sell/
.. _Amazon Payments: https://payments.amazon.com/

All have the same base tranactions fee: 2.9% + $0.30. For the PapPop
fees structure that translates to:

* $0.82 on the $18 non-member fee
* $0.74 on the $15 member fee
* $0.59 on the $10 under-19 fee

The primary difference among those services is that PayPal does not
require the user to have an account in order to make a payment while
the other 2 do. So, in the interest of keeping the barrier to people
using the online payment system low, PayPal looks like the best choice.


Populaires App Components and Workflow
--------------------------------------

#. I use the RandoPony admin interface to
   create an event object instance for the populaire
   event. Information required:

   * Event (PacPop, VanIsPop, CanadaDayPop, etc.)
   * Distance(s)
   * Date
   * Start/Finish location
   * Start time (need to handle time range for Canada Day)
   * Organizer email address(es)
   * Link to event page on randonneurs.bc.ca (optional?)
   * Fee for BC Rando member
   * Fee for non-member
   * Fee for under 19 year old
   * Date on which pre-registration for the populaire closes

#. When the RandoPony event page is ready to go live the I use admin
   interface functions to:

   * Initialize the Google Docs spreadsheet for the event and store
     its URL in the event object instance in the database.

   * Send an email message to the organizer that contains:
   
     * the URL of the RandoPony event page
     * the URL of the Google Docs spreadsheet for the event 

   * Send an email message to Eric that contains:
   
     * the URL of the RandoPony event page

#. When a rider pre-registers for the populaire:

   * RandoPony presents a form to collect:

     * First name
     * Last name
     * Whether rider is a member of BC Randonneurs
     * Emergency contact phone number
     * Phone number of mobile phone they are carrying on the ride
     * Whether rider is over or under 19 years of age

   * RandoPony present a form that shows the event waiver and collects
     the rider's acceptance of it. Pre-registration process aborts if
     the rider does not accept the waiver.

   * RandoPony stores The rider's pre-registration information is
     stored in the database, pending payment confirmation.

   * RandoPony passes the rider to the credit card transaction service
     to collect payment for their registration.

#. When RandoPony receives confirmation that the credit card
   transaction was successful:

   * The rider's database entry is updated to indicate payment confirmed
   * A confirmation email is sent to the address the rider provided
   * The Google Docs spreadsheet for the event is updated with the
     rider's information

#. At any time after creation of the event object instance the
   organizer can sign-in to Google Docs to:

   * View the event spreadsheet
   * Save a copy to manipulate as they wish in Google Docs
   * Download a copy in various formats (Excel, OpenOffice, etc.) to
     manipulate as they wish
   * Print directly from Google Docs

   .. note::

      Only the original spreadsheet will be updated as riders register,
      not Google Docs or downloaded copies. So, organizers should wait
      until after the pre-registration closure date to do any heavy
      duty manipulation of the spreadsheet.

#. When appropriate the club treasurer signs into the PayPal account
   and transfers the accumulated funds to the club bank account.


Google Docs Spreadsheet Content
-------------------------------

The Google Docs spreadsheet for a populaire will contain 2 sheets:

* The summary riders list. This sheet contains minimal personal
  information so that it can be widely distributed by the organizer
  for use at the registration tables and controls.
* The detailed riders list. This sheet contains the collected contact
  information for the riders and is intended for the organizer use.

Summary Riders List Columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Rider Number
* First Name
* Last Name
* Distance they plan to ride


Detailed Riders List Columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Rider Number
* First Name
* Last Name
* Distance they plan to ride
* Emergency contact phone number
* Phone number of mobile phone they are carrying on the ride
* Whether rider is over or under 19 years of age
* BC Randonneurs membership status


.. _SiteAndCodebaseMaintenance-section:

Site and Codebase Maintenance
=============================

This is a collection of notes and tasks for my reference. I don't
expect discussion or comment on these from anyone else.

Add Documentation About Pony Capabilities
-----------------------------------------

What the pony does by default, and what it is optionally capable of
has grown beyond what can/should be explained on the `Info for Brevet
Organizers`_ page. Additional documentation pages need to be provided.


.. _ImproveNon-RidingEventsImplementation-section:

Improve Non-Riding Events Implementation
----------------------------------------

Still thinking about this.


Miscellaneous Issues
--------------------

* Fix `issue 8`_ on bitbucket.

.. _issue 8: http://bitbucket.org/douglatornell/randopony/issue/8
