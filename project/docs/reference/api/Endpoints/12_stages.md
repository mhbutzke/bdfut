# stages

**URL:** https://docs.sportmonks.com/football/endpoints-and-entities/endpoints/stages

---

# Stages

The stages endpoint can help you define the structure of the league. A league can have different types of stages. For example: regular season, promotion-play off, knock-outs etc. With the stages endpoint, we give you the ability to request data for a single stage or for a whole season.

Use one of our 4 stages endpoints. Per endpoint, you can find the details, including base URL, parameters, includes and more.&#x20;

* **GET All Stages:** returns all stages available within your subscription.
* **GET Stage by ID:** returns stage information from your requested stage ID.
* **GET Stages by Season ID:** returns stage information from your requested season ID.
* **GET Stages by Search by Name:** returns all stages that match your search query.

### Include options

[`league`](../../entities/league-season-schedule-stage-and-round#league) [`season`](../../entities/league-season-schedule-stage-and-round#season) [`type`](https://docs.sportmonks.com/football2/v/core/endpoints/types) [`sport`](https://app.gitbook.com/o/-MJWE53IpT91aRTPjruo/s/z0kWjB5EvZvqGsozw8vP/) [`rounds`](../../entities/league-season-schedule-stage-and-round#round) [`currentRound`](../../entities/league-season-schedule-stage-and-round#round) [`groups`](../../entities/league-season-schedule-stage-and-round#group) [`fixtures`](../../entities/fixture#fixture) [`aggregates`](../../entities/fixture#aggregate)  [`topscorers`](../../entities/standing-and-topscorer#topscorers)  [`statistics`](../entities/statistic)

### **Related Entities:**

Get an overview and explanation of all the fields returned in the API response. The related entities for the stages endpoints are:

* [Stage](../../entities/league-season-schedule-stage-and-round#stage)