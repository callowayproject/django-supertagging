.. _real_world_example:

Real World Example
==================

SuperTagging came about when The Washington Times was looking for a cheap 
alternative method of tagging its contents. The previous method was the 
process of sending the content to a similar, but paid service, and that 
service would return keywords and the content in its marked up state. The 
content then was saved into our story body field with the links in place. 
These links went to a section of our site we then called "Themes". 

The first thing we wanted to get rid of was the monthly fee we had to paid 
for the service, we ended up finding `OpenCalais <http://opencalais.com>`_, 
which gave us a free way to tag our content and also be able to easily markup 
our content with the links as before.

We now have a similar section on our site called 
`Topics <http://washingtontimes.com/topics/>`_ which is powered by 
SuperTagging, and most of our stories have the links to this section 
as before. 

This section of the documentation, we will go through all the pieces of 
SuperTagging we use here at The Washington Times.


Our current SuperTagging settings
*********************************

This first group of settings are the general settings. 

.. code-block:: python
    
    SUPERTAGGING_DEBUG = False
    SUPERTAGGING_ENABLED = True
    SUPERTAGGING_AUTO_PROCESS = True
    SUPERTAGGING_CALAIS_API_KEY = '...'
    SUPERTAGGING_USE_QUEUE = True

**Explanation**:

We have USE_QUEUE set to `True`. Together with AUTO_PROCESS set to `True`, 
the objects are saved into the `SuperTagQueue` model for later processing. 
We run the management command provided by SuperTagging every 5 minutes.
    
This next group is what we call the processing settings for SuperTagging.
    
.. code-block:: python
    
    SUPERTAGGING_PROCESS_RELATIONS = True
    SUPERTAGGING_PROCESS_TOPICS = True
    SUPERTAGGING_RESOLVE_PROPERTY_KEYS = True
    SUPERTAGGING_ONLY_NON_TAGGED_OBJECTS = False
    
    SUPERTAGGING_MIN_RELEVANCE = 200
    
    SUPERTAGGING_USE_FREEBASE = True
    
    
**Explanation**: 
    
We process pretty much all OpenCalais gives us, that includes the 
Events/Facts (relations) and Topics, which are just tags but with no 
meta data. 

We try to convert Calais ID's to tag names 
(`SUPERTAGGING_RESOLVE_PROPERTY_KEYS = True`)

We tag all objects every time they are saved 
(`SUPERTAGGING_ONLY_NON_TAGGED_OBJECTS = False`). This is so we can 
efficiently markup up the content without worry of data being stale. 

We only accept tags that have at least 200 relevance

We use Freebase to disambiguate the tag names.
    
    
Next group is the markup settings

.. code-block:: python

    SUPERTAGGING_MARKUP = True
    SUPERTAGGING_MARKUP_EXCLUDES = ['his', 'her', 'he', 'she', 'him',]
    SUPERTAGGING_MARKUP_CONTENT_CACHE_TIMEOUT = 3600
    SUPERTAGGING_MARKUP_FIELD_SUFFIX = "tagged"
    
**Explanation**: 

We markup all the objects that get processed by OpenCalais, below is an 
example of content after it has been marked up.

.. code-block:: html

    <p><a href="/topics/charles-b-rangel/">Mr. Rangel</a>, the longtime top Democrat on the House 
    <a href="/topics/ways-and-means-committee/">Ways and Means Committee</a> who stepped down under 
    pressure in March, has been under investigation by the panel for two years. At issue is a 
    plethora of subjects, including <a href="/topics/charles-b-rangel/">Mr. Rangel</a>'s ownership 
    of several rent-controlled apartments in New York; his failure to report $75,000 in earnings 
    on tax returns; and use of his official position to raise money for the 
    <a href="/topics/charles-b-rangel-center/">Charles B. Rangel Center</a> for 
    <a href="/topics/public-service/">Public Service</a> at 
    <a href="/topics/city-college-of-new-york/">City College of New York</a>.</p>


We exclude some markup values OpenCalais returns. OpenCalais returns exactly 
where, in the content sent over, the reference to the tags is. This will not 
just be the exact tag name but also references to the tag such as his, her, 
she. We found that there was just too many links in the content and needed a 
way to limit it. So combinations of `SUPERTAGGING_MIN_RELEVANCE` setting and 
`SUPERTAGGING_MARKUP_EXCLUDES` provided just that.

One of the things we did not like from the old tagging service, was that the 
links were added to the content directly. With SuperTagging the content field 
of your instance is never changed when your using the markup feature. Instead, 
another attribute is added to your instance during processing. 
`SUPERTAGGING_MARKUP_FIELD_SUFFIX` tells what the prefix for that field will 
be. For example, if we wanted to markup a field named 'content', after 
`SuperTagging` is done processing, another attribute will be available in that 
model called 'tagged_content'. This attribute will contain the content in a 
marked up state. This way, if we ever decided to change the way we markup our 
data, or change the location of where the links in the content go, we don't 
need to change the instance directly.

Vist the :ref:`markup` page for more information

This next set of settings we use is to exclude the types (entities) and 
relation types (events/facts)

.. code-block:: python

    SUPERTAGGING_TAG_TYPE_EXCLUSIONS = [
        'Anniversary', 
        'City', 
        #'Company', 
        'Continent', 
        #'Country', 
        'Currency', 
        'EmailAddress', 
        'EntertainmentAwardEvent', 
        'Facility', 
        'FaxNumber', 
        #'Holiday', 
        'IndustryTerm', 
        'MarketIndex', 
        'MedicalCondition', 
        'MedicalTreatment', 
        'Movie', 
        'MusicAlbum', 
        'MusicGroup', 
        'NaturalFeature', 
        'OperatingSystem', 
        #'Organization', 
        #'Person', 
        'PhoneNumber', 
        'PoliticalEvent', 
        'Position', 
        'Product', 
        'ProgrammingLanguage', 
        'ProvinceOrState', 
        'PublishedMedium', 
        #'RadioProgram', 
        'RadioStation', 
        'Region', 
        #'SportsEvent', 
        #'SportsGame', 
        #'SportsLeague', 
        'Technology', 
        #'TVShow', 
        'TVStation', 
        'URL',
    ]
    
    SUPERTAGGING_REL_TYPE_EXCLUSIONS = [
       #'Acquisition',  
       'Alliance', 
       'AnalystEarningsEstimate', 
       'AnalystRecommendation', 
       #'Arrest', 
       #'Bankruptcy', 
       'BonusSharesIssuance', 
       #'BusinessRelation', 
       'Buybacks', 
       'CompanyAccountingChange', 
       #'CompanyAffiliates', 
       'CompanyCompetitor', 
       'CompanyCustomer', 
       'CompanyEarningsAnnouncement', 
       'CompanyEarningsGuidance', 
       #'CompanyEmployeesNumber', 
       'CompanyExpansion', 
       'CompanyForceMajeure', 
       #'CompanyFounded', 
       'CompanyInvestment', 
       'CompanyLaborIssues', 
       'CompanyLayoffs', 
       'CompanyLegalIssues', 
       'CompanyListingChange', 
       'CompanyLocation', 
       'CompanyMeeting', 
       'CompanyNameChange', 
       'CompanyProduct', 
       'CompanyReorganization', 
       'CompanyRestatement', 
       'CompanyTechnology', 
       #'CompanyTicker', 
       'CompanyUsingProduct', 
       'ConferenceCall', 
       #'Conviction', 
       'CreditRating', 
       'DebtFinancing', 
       'DelayedFiling', 
       'DiplomaticRelations', 
       'Dividend', 
       'EmploymentChange', 
       #'EmploymentRelation', 
       'EnvironmentalIssue', 
       'Extinction', 
       #'FamilyRelation', 
       'FDAPhase', 
       'Indictment', 
       'IPO', 
       'JointVenture', 
       'ManMadeDisaster', 
       'Merger', 
       'MovieRelease', 
       'MusicAlbumRelease', 
       'NaturalDisaster', 
       'PatentFiling', 
       'PatentIssuance', 
       #'PersonAttributes', 
       #'PersonCareer', 
       'PersonCommunication', 
       #'PersonEducation', 
       'PersonEmailAddress', 
       'PersonRelation', 
       'PersonTravel', 
       'PoliticalEndorsement', 
       #'PoliticalRelationship', 
       'PollsResult', 
       'ProductIssues', 
       'ProductRecall', 
       'ProductRelease', 
       #'Quotation', 
       'SecondaryIssuance', 
       'StockSplit', 
       'Trial', 
       'VotingResult', 
    ]
    
The ones that are commented out are the ones we do want. So so make sense of 
these to lists we only want the following:

* **Tag Types (Entities)**
    * Company
    * Country
    * Holiday
    * Organization
    * Person
    * RadioProgram 
    * SportsEvent 
    * SportsGame 
    * SportsLeague 
    * TVShow
* **Relation Types (Events/Facts)**
    * Acquisition  
    * Arrest
    * Bankruptcy
    * BusinessRelation 
    * CompanyAffiliates
    * CompanyEmployeesNumber 
    * CompanyFounded 
    * CompanyTicker 
    * Conviction
    * EmploymentRelation 
    * FamilyRelation 
    * PersonAttributes 
    * PersonCareer
    * PersonEducation
    * PoliticalRelationship
    * Quotation

This last section is the models we tag.

.. code-block:: python

    SUPERTAGGING_MODULES = {
       'stories.story': 
            {'fields':(
                {'name': 'body', 
                 'process_type':'TEXT/HTML'},),
            },
        'massmedia.image':
            {'fields':(
                {'name': 'caption'},)
            },
    }
    
**Explanation**: 

This we very basic, since we only tag one field for both our stories and 
images. One thing that will change in the future for The Washington Times, 
will be that we will only tag stories with particular set of origins. 
For example, we currently have the following origins for our stories:

.. code-block:: python

    STORY_ORIGIN_CHOICES = (
        (0, 'Unknown'),
        (1, 'Admin'),
        (2, 'SaxoTech Editorial'),
        (3, 'SaxoTech Online'),
        (4, 'AP News'),
        (5, 'Bernini'),
        (6, 'AP NetNews'),
    )
    
Some of these origins are not used anymore, and we will want to limit which 
ones we do tag, so eventually the `SUPERTAGGING_MODULES` will look like this:

.. code-block:: python

    SUPERTAGGING_MODULES = {
       'stories.story': 
            {'fields':(
                {'name': 'body', 
                 'process_type':'TEXT/HTML'},),
             'match_kwargs': {'origin__in': [1,2,3,5]}
            },
        'massmedia.image':
            {'fields':(
                {'name': 'caption'},)
            },
    }
    
If this was our current setup, we would not tag stories that had an origin 
of (0) Unknown, (4) AP News or (6) AP NetNews.

Showcasing what SuperTagging does
*********************************

**TODO**

Running the process
*******************

Last thing is to run the cron job every 5 minutes to process the Queued
objects.

.. code-block:: console

  */5 *   *   *   *    /path/to/virtualenv/bin/python /path/to/project/manage.py st_process_queue>/dev/null 2>&1
