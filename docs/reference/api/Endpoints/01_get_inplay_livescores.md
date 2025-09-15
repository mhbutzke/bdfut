---
description: 'GET All Inplay Livescores: returns all the inplay fixtures.'
---

# GET Inplay Livescores

{% tabs %}
{% tab title="Base URL" %}
```javascript
https://api.sportmonks.com/v3/football/livescores/inplay
```
{% endtab %}

{% tab title="Example Response" %}
```json
{
    "data": {
        "id": 19146701,
        "sport_id": 1,
        "league_id": 501,
        "season_id": 23690,
        "stage_id": 77471570,
        "group_id": null,
        "aggregate_id": null,
        "round_id": 340573,
        "state_id": 5,
        "venue_id": 8909,
        "name": "Celtic vs Kilmarnock",
        "starting_at": "2024-08-04 15:30:00",
        "result_info": "Celtic won after full-time.",
        "leg": "1/1",
        "details": null,
        "length": 90,
        "placeholder": false,
        "has_odds": true,
        "has_premium_odds": true,
        "starting_at_timestamp": 1722785400
    },
```
{% endtab %}

{% tab title="Field Description" %}
| Field         | Description                                      | Type           |
| ------------- | ------------------------------------------------ | -------------- |
| id            | Refers the unique id of the fixture              | integer        |
| sport\_id     | Refers to the sport the fixture is played at     | integer        |
| league\_id    | Refers to the league the fixture is played in    | integer        |
| season\_id    | Refers to the seasons the fixture is played in   | integer        |
| stage\_id     | Refers to the stage the fixture is played in     | integer        |
| group\_id     | Refers to the group the fixture is played in     | integer / null |
| aggregate\_id | Refers to the aggregate the fixture is played at | integer / null |
| state\_id     | Refers to the state the fixture is played at     | integer        |
| round\_id     | Refers to the round the fixture is played at     | integer / null |
| state\_id     | Refers to the state the fixture is played at     | integer        |
| venue\_id     | Refers to the venue the fixture is played at     | integer / null |
| name          | Represents the name of the participants          | string / null  |
| starting\_at  | Datetime object representing the start time      | date / null    |
| result\_info  | Represents the final result info                 | string / null  |
| leg           | Represents the leg of the fixture                | string         |
| details       | Represents details about the fixture             | string / null  |
| length        | Length of the fixture (minutes)                  | integer / null |

####
{% endtab %}
{% endtabs %}

{% tabs %}
{% tab title="Query Parameters" %}
<table><thead><tr><th>Name</th><th width="232.66666666666666">Required?</th><th>Description</th></tr></thead><tbody><tr><td><code>api_token</code></td><td><p>YES </p><p>Another option is to provide the API token in the header.</p></td><td>Your unique API token. Ex. ?api_token=YOUR_TOKEN</td></tr><tr><td><code>include</code></td><td>NO</td><td>Enrich the API response with more data by using includes. Ex. &include=participants;events</td></tr><tr><td><code>select</code></td><td>NO</td><td>Select specific fields on the<a href="https://docs.sportmonks.com/football2/endpoints-and-entities/entities/fixtures"> base entity</a>. Read how to select fields in our <a href="https://docs.sportmonks.com/football2/api/request-options/selecting-fields">tutorial</a>.</td></tr><tr><td><code>sortBy</code></td><td>NO</td><td>Order by specific fields on the <a href="../../entities/fixture">base entity</a>. For more information check out <a href="../../../api/request-options/ordering-and-sorting">this</a> page.</td></tr><tr><td><code>filters</code></td><td>NO</td><td>Filter the API response on multiple related entities. There are static filters and dynamic filters.​<br><br>Please find the possibilities in the Static and Dynamic Filter tab.</td></tr><tr><td><code>locale</code></td><td>NO</td><td>Translate name fields of the API Response in your selected language. Find more information and which languages are available on our <a href="../../../api/translations-beta">translations page</a>.</td></tr></tbody></table>
{% endtab %}

{% tab title="Static Filters" %}
**Static filters** are always the same and filter in one specific way without any custom options. Each static filter is listed below and has a description of how it filters. For more information, please look at our[ Filters page](../../../api/request-options/filtering).

<table><thead><tr><th width="165">Static Filters</th><th width="114">Available on Entity</th><th width="197">Description</th><th width="274">Example</th></tr></thead><tbody><tr><td><code>ParticipantSearch</code></td><td>Fixture</td><td>Filter on the matches of specific participants.</td><td><code>&include=participants&filters=participantSearch:Celtic</code></td></tr><tr><td><code>todayDate</code></td><td>Fixture</td><td>Filter all fixtures to find only the fixtures of today.</td><td><code>&filters=todayDate</code></td></tr><tr><td><code>venues</code></td><td>Fixture</td><td>Find all fixtures that are played in a specific venue.</td><td><code>&include=venue&filters=venues:venueIDs</code><br><br><code>&include=venue&filters=venues:10,12</code></td></tr><tr><td><code>IsDeleted</code></td><td>Fixture</td><td>Filter on deleted fixtures only. This filter helps to keep your database in sync.</td><td><code>&filters=IsDeleted</code></td></tr><tr><td><code>markets</code></td><td>Odds</td><td>Filter the odds on a selection of markets separated by a comma. </td><td><code>&include=odds&filters=markets:marketIDs</code><br><br><code>&include=odds&filters=markets:12,14</code></td></tr><tr><td><code>bookmakers</code></td><td>Odds</td><td>Filter the odds on a selection of bookmakers separated by a comma. (e.g: 2,14). </td><td><code>&include=odds&filters=bookmakers:bookmakerIDs</code><br><br><code>&include=odds&filters=bookmakers:2,14</code></td></tr><tr><td><code>WinningOdds</code></td><td>Odds</td><td>Filter all winning odds.</td><td><code>&include=odds&filters=WinningOdds</code></td></tr></tbody></table>
{% endtab %}

{% tab title="Dynamic Filters" %}
The **dynamic filters** are based on entities and includes. Each dynamic filter uses an entity to filter on and one entity to apply the filter on. Below are examples with explanations of how filters are set up. For more information, please look at our [Filters page.](../../../api/request-options/filtering)

{% hint style="info" %}
Using an include? Check their respective filters on their entity page. For example if you use `&include=participants` you can apply [team-related filters](../../../entities/team-player-squad-coach-and-referee#team).&#x20;
{% endhint %}

<table><thead><tr><th width="143">Dynamic Filters</th><th>Available on Entity</th><th>Description</th><th width="191">Examples</th></tr></thead><tbody><tr><td><code>types</code></td><td>Statistics, Events, Lineup, and way more.<br><br>Check this <a href="https://docs.sportmonks.com/football2/v/core/endpoints/filters/get-all-entity-filters">endpoint</a> for all possibilities.</td><td>Filter the Types on a selection of Fixture statistics separated by a comma. <br><br><br><br>Filter on the specific events you want to show.</td><td><code>&include=statistics&filters=statisticTypes:TypeIDs</code><br><br><code>&include=statistics&filters=statisticTypes:42,49</code><br><br><code>&include=events&filters=eventTypes:14</code></td></tr><tr><td><code>states</code></td><td>Fixtures<br><br>Check this <a href="https://docs.sportmonks.com/football2/v/core/endpoints/filters/get-all-entity-filters">endpoint</a> for all possibilities.</td><td>Filter the states of fixtures separated by a comma. <br></td><td><code>&include=state&filters=fixtureStates:StateIDs</code><br><br><code>&include=state&filters=fixtureStates:1,5</code></td></tr></tbody></table>
{% endtab %}
{% endtabs %}

### **Filters**

More information on how to use filters can be found on our tutorials on how to [filter](../../../api/request-options/filtering). If you want more information on which filters to use you can check out the following [endpoint]():

```
https://api.sportmonks.com/v3/my/filters/entity?api_token=YOUR_TOKEN
```

### Pagination

NO

### Include depth

You can use a total of `3` nested includes on this endpoint

### Include options

**Related Entities:**

Get an overview and explanation of all the fields returned in the API response. The related entities for the livescores endpoints are:

### Postman

We also offer detailed postman documentation with examples and a complete up-to-date version of all our endpoints. Below is a button that lets your fork the collection or import it.

### Code Example

Ruby

Python

PHP

Java

Node.js

Go

```ruby
require "uri"
require "net/http"

url = URI("https://api.sportmonks.com/v3/football/livescores/inplay?api_token=YOUR_TOKEN")

https = Net::HTTP.new(url.host, url.port)
https.use_ssl = true

request = Net::HTTP::Get.new(url)

response = https.request(request)
puts response.read_body
```

Last updated 1 month ago

Was this helpful?

