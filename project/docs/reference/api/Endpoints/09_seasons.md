# Seasons

**URL:** https://docs.sportmonks.com/football/endpoints-and-entities/endpoints/seasons

---

# 

\# Seasons

Gather an overview of all the historical and current seasons available within your subscription. Responses provide you details like the Season ID, Name, League ID, Year and if the Season is Active Yes or No.&#x20;

{% hint style="info" %}
Are you interested in a complete schedule? Then maybe our schedule endpoints are what you’re looking for: \[Schedule endpoint\](schedules).
{% endhint %}

Use one of our 3 season endpoints. Per endpoint, you can find the details, including base URL, parameters, includes and more.&#x20;

\* \*\*GET All Seasons:\*\* returns all the historical and active seasons that are available within your subscription.&#x20;
\* \*\*GET Season by ID:\*\* returns the single-season you’ve requested by ID.
\* \*\*GET Seasons by Search by Name:\*\* returns all seasons that match your search query.

### Include options

\[\`sport\`\](https://app.gitbook.com/o/-MJWE53IpT91aRTPjruo/s/z0kWjB5EvZvqGsozw8vP/) \[\`league\`\](../../entities/league-season-schedule-stage-and-round#league) \[\`teams\`\](../../entities/team-player-squad-coach-and-referee#team) \[\`stages\`\](../../entities/league-season-schedule-stage-and-round#stage) \[\`currentStage\`\](../../entities/league-season-schedule-stage-and-round#stage) \[\`fixtures\`\](../../entities/fixture#fixture) \[\`groups\`\](../../entities/league-season-schedule-stage-and-round#group) \[\`statistics\`\](../../entities/statistic#seasonstatistic) \[\`topscorers\`\](../../entities/standing-and-topscorer#topscorers)

### \*\*Related Entities:\*\*

Get an overview and explanation of all the fields returned in the API response. The related entities for the seasons endpoints are:

\* \[Season\](../../entities/league-season-schedule-stage-and-round#season)

{% hint style="info" %}
Remember, our historical data will be integrated into the new version of our API gradually. So, the historical data is not yet complete. However, we will be loading more historical data continuously.
{% endhint %}