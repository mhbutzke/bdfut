# Teams

**URL:** https://docs.sportmonks.com/football/endpoints-and-entities/endpoints/teams.md

---

# 

\# Teams

Retrieve detailed team information via one of our 5 team endpoints.&#x20;

With the team endpoints, you can retrieve basic information like logos, names etc. Interested in detailed information?

You can retrieve more detailed information by using the correct includes. Per endpoint you can find the details including base URL, parameters, includes and more.

\* \*\*GET All Teams:\*\* returns all the teams that are accessible within your subscription.
\* \*\*GET Team by ID:\*\* returns the single team you’ve requested by ID.
\* \*\*GET Team by Country ID:\*\* returns all the teams from your requested country ID.
\* \*\*GET Team by Season ID:\*\* returns all the teams from your requested season ID.
\* \*\*GET Team Search by Name:\*\* returns all the teams that match your search query.

### Include options

\[\`sport\`\](https://app.gitbook.com/o/-MJWE53IpT91aRTPjruo/s/z0kWjB5EvZvqGsozw8vP/) \[\`country\`\](https://app.gitbook.com/o/-MJWE53IpT91aRTPjruo/s/z0kWjB5EvZvqGsozw8vP/) \[\`venue\`\](../../entities/other#venue) \[\`coaches\`\](../../entities/team-player-squad-coach-and-referee#coach) \[\`rivals\`\](../../entities/other#rival) \[\`players\`\](../../entities/team-player-squad-coach-and-referee#player) \[\`latest\`\](../../entities/fixture#fixture) \[\`upcoming\`\](../../entities/fixture#fixture) \[\`seasons\`\](../../entities/league-season-schedule-stage-and-round#season) \[\`activeSeasons\`\](../../entities/league-season-schedule-stage-and-round#season) \[\`sidelined\`\](../../entities/team-player-squad-coach-and-referee#sidelined) \[\`sidelinedHistory\`\](../../entities/team-player-squad-coach-and-referee#sidelined) \[\`statistics\`\](../../entities/statistic#teamstatistic) \[\`trophies\`\](../../entities/other#participanttrophy) \[\`socials\`\](../../entities/other#social)

### \*\*Related Entities:\*\*

Get an overview and explanation of all the fields returned in the API response. The related entities for the teams endpoints are:

\* \[Team\](../../entities/team-player-squad-coach-and-referee#team)

{% hint style="info" %}
Remember, our historical data will be integrated into the new version of our API gradually. So, the historical data is not yet complete. However, we will be loading more historical data continuously.
{% endhint %}