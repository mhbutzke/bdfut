# Players

**URL:** https://docs.sportmonks.com/football/endpoints-and-entities/endpoints/players

---

# 

\# Players

Retrieve detailed player information via one of our 5 player endpoints.

You can retrieve more detailed information by using the correct includes. Per endpoint you can find the details including base URL, parameters, includes and more.

\* \*\*GET All Players:\*\* returns all the players that are accessible within your subscription.
\* \*\*GET Player by ID:\*\* returns player information from your requested player ID.
\* \*\*GET Players by Country ID:\*\* returns player information from your requested country ID.
\* \*\*GET Players Search by Name:\*\* returns all the players that match your search query.
\* \*\*GET Last Updated Players:\*\* returns all the players that have received updates in the past two hours.&#x20;

#### Include options

\[\`sport\`\](https://app.gitbook.com/o/-MJWE53IpT91aRTPjruo/s/z0kWjB5EvZvqGsozw8vP/) \[\`country\`\](https://app.gitbook.com/o/-MJWE53IpT91aRTPjruo/s/z0kWjB5EvZvqGsozw8vP/) \[\`city\`\](https://app.gitbook.com/o/-MJWE53IpT91aRTPjruo/s/z0kWjB5EvZvqGsozw8vP/) \[\`nationality\`\](https://app.gitbook.com/o/-MJWE53IpT91aRTPjruo/s/z0kWjB5EvZvqGsozw8vP/) \[\`transfers\`\](../../entities/other#transfer) \[\`pendingTransfers\`\](../../entities/other#transfer) \[\`teams\`\](../../entities/team-player-squad-coach-and-referee#team) \[\`statistics\`\](../../entities/statistic#playerstatistic) \[\`latest\`\](../../entities/fixture#fixture) \[\`position\`\](https://app.gitbook.com/o/-MJWE53IpT91aRTPjruo/s/z0kWjB5EvZvqGsozw8vP/) \[\`detailedPosition\`\](https://app.gitbook.com/o/-MJWE53IpT91aRTPjruo/s/z0kWjB5EvZvqGsozw8vP/)  \[\`lineups\`\](../../entities/fixture#lineup) \[\`trophies\`\](../../entities/other#participanttrophy) \[\`metadata\`\](../../entities/other#metadata)&#x20;

\*\*Related Entities:\*\*

Get an overview and explanation of all the fields returned in the API response. The related entities for the player endpoints are:

\* \[Player\](../../entities/team-player-squad-coach-and-referee#player)

{% hint style="info" %}
Remember, our historical data will be integrated into the new version of our API gradually. So, the historical data is not yet complete. However, we will be loading more historical data continuously.
{% endhint %}