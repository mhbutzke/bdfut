# Expected (xG)

**URL:** https://docs.sportmonks.com/football/endpoints-and-entities/endpoints/expected-xg.md

---

# 

\# Expected (xG)

Gather an overview of all the xG values available within your subscription via the Expected endpoints. Retrieve basic information or enrich your response.&#x20;

Use one of our 2 expected endpoints. Per endpoint, you can find the details, including base URL, parameters, includes and more.&#x20;

\* \*\*GET Expected by Team:\*\* returns all the expected data that are available within your subscription on team level.&#x20;
\* \*\*GET Expected by Player:\*\* returns all the expected data that are available within your subscription on player level.&#x20;

{% hint style="info" %}
Please note that the availability of xG values varies depending on the package you choose.&#x20;

\* The \*\*Basic xG\*\* package offers access to the xG statistics 12 hours after the match finishes.&#x20;
\* The \*\*Standard\*\* \*\*xG\*\* package offers access straight after the match has finished.&#x20;
\* The \*\*Advanced\*\* \*\*xG\*\* package offers real-time availability to all xG statistics.

\_\\\*These xG packages are only available as an add-on and are not included in any of our default plans.\_

You can find more information on our dedicated \[pricing page\](https://www.sportmonks.com/blogs/xg-pricing-explained/).&#x20;
{% endhint %}

#### Include options

\[\`type\`\](types) \[\`fixture\`\](../entities/fixture)\[\`player\`\](https://docs.sportmonks.com/football/endpoints-and-entities/entities/team-player-squad-coach-and-referee#player) \[\`team\`\](https://docs.sportmonks.com/football/endpoints-and-entities/entities/team-player-squad-coach-and-referee#team)

\*\*Related Entities:\*\*

Get an overview and explanation of all the fields returned in the API response. The related entities for the expected endpoints are:

\* \[Expected\](../entities/expected)