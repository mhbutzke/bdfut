# team-squads

**URL:** https://docs.sportmonks.com/football/endpoints-and-entities/endpoints/team-squads

---

# Team Squads

Retrieve historical squads via our Teams Squad endpoint. You can retrieve historical squads from 2005 and onwards. The endpoint also includes player performances in the requested season.\*

You can find the details on the Team Squads endpoint, including base URL, parameters, includes, and more.

* **GET Team Squads by Team ID:** returns the current **domestic squad** from your requested team ID.
* **GET Team Squads by Team and Season ID:** returns (historical) squads from your requested team and season ID.

{% hint style="info" %}
Please check our coverage page if the league offer historical squads.
{% endhint %}

#### Include options

[`team`](../../entities/team-player-squad-coach-and-referee#team) [`player` ](../../entities/team-player-squad-coach-and-referee#player)[`position`](https://app.gitbook.com/o/-MJWE53IpT91aRTPjruo/s/z0kWjB5EvZvqGsozw8vP/)[ ](../../entities/team-player-squad-coach-and-referee#player)[`detailedPosition`](https://app.gitbook.com/o/-MJWE53IpT91aRTPjruo/s/z0kWjB5EvZvqGsozw8vP/)[ ](../../entities/team-player-squad-coach-and-referee#player)[`transfer`](../../entities/other#transfer)

#### **Related Entities:**

Get an overview and explanation of all the fields returned in the API response. The related entities for the team squads endpoint are:

* [Team Squads](../../entities/team-player-squad-coach-and-referee#team-squad)
* [PlayerStatistic](../../entities/statistic#playerstatistic)

{% hint style="info" %}
Remember, our historical data will be integrated into the new version of our API gradually. So, the historical data is not yet complete. However, we will be loading more historical data continuously.
{% endhint %}
