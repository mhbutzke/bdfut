# Demo response files

Next to the responses in our [tutorials](../tutorials-and-guides/tutorials) and [how-to guides](../tutorials-and-guides), we have generated some example files for you to download. The example JSON files will help you build your implementation. Click on the button to download the example files.

## **Fixtures**

### **Match and player statistics, lineups and events**

#### **CL final 2023/2024 season:** Borussia Dortmund **- Real Madrid**&#x20;

Request with the all match and player statistics, events and full line-up.

```javascript
https://api.sportmonks.com/v3/football/fixtures/19101794?api_token=YOUR_TOKEN&include=statistics.type;lineups.details.type;events.type
```

{% file src="https://3469464275-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F9zsNGu3HAzSnl5DWBD3Y%2Fuploads%2FiqKrMUSDtHJ5nmKoODDP%2FCL_final_23_24_stats_events_lineups.json?alt=media&token=7b0411c5-6c1f-4bbd-a976-86fbabb1bd8c" %}
Borussia Dortmund - Real Madrid: Match stats
{% endfile %}

{% hint style="danger" %}
Including `.type` is not recommended as an include on any endpoint. Types are used throughout the entire API. We recommend retrieving all types from the types endpoint and storing them in your database or other data structure. Only include the type if no other option is available or when testing the API.
{% endhint %}

### **Pre-match odds from bet365**

#### **CL final 2023/2024 season: Borussia Dortmund - Real Madrid**&#x20;

Request to retrieve pre-match odds for the 2023/2024 CL final.&#x20;

```javascript
https://api.sportmonks.com/v3/football/fixtures/19101794?api_token=YOUR_TOKEN&include=odds&filters=bookmakers:23
```

{% file src="https://3469464275-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F9zsNGu3HAzSnl5DWBD3Y%2Fuploads%2FsQwOGRXW36XxNWIiKBAl%2FCL_final_odds.json?alt=media&token=6ca3ac33-bc37-4d3a-b20d-0eebbc7a2dc3" %}
Borussia Dortmund - Real Madrid: odds
{% endfile %}

## **Team**

### **Team season statistics**

#### **CL 2023/2024 season: Borussia Dortmund team statistics**

Request to retrieve the season statistics of Borussia Dortmund for the CL 2023/2024 season.&#x20;

```javascript
https://api.sportmonks.com/v3/football/teams/68?api_token=YOUR_TOKEN&include=statistics.details.type&filters=teamStatisticSeasons:21638
```

{% file src="https://3469464275-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F9zsNGu3HAzSnl5DWBD3Y%2Fuploads%2FIQoLc9W60gyEonBhqexK%2Fborussia_dortmund_CL_stats.json?alt=media&token=787415c5-46d8-43b2-8e8b-c46b00a97cbc" %}
Borussia Dortmund season stats
{% endfile %}

{% hint style="danger" %}
Including `.type` is not recommended as an include on any endpoint. Types are used throughout the entire API. We recommend retrieving all types from the types endpoint and storing them in your database or other data structure. Only include the type if no other option is available or when testing the API.
{% endhint %}

### **Team season squads and statistics**

#### **CL 2023/2024 season: Real Madrid squad**

Request to retrieve the squad and statistics of Real Madrid for the CL 2023/2024 season.&#x20;

```javascript
https://api.sportmonks.com/v3/football/squads/seasons/21638/teams/3468?api_token=YOUR_TOKEN&include=player;details.type
```

{% file src="https://3469464275-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F9zsNGu3HAzSnl5DWBD3Y%2Fuploads%2FPhxe4tfWSYzioe3lX2On%2FReal_Madrid_CL_season_stats.json?alt=media&token=b70c0de6-e0f6-423b-a578-ee909b942460" %}
Real Madrid season squad
{% endfile %}

{% hint style="danger" %}
Including `.type` is not recommended as an include on any endpoint. Types are used throughout the entire API. We recommend retrieving all types from the types endpoint and storing them in your database or other data structure. Only include the type if no other option is available or when testing the API.
{% endhint %}

## **Player**

### **Player season statistics**

#### **CL 2023/2024 season: Kylian Mbappé statistics**

Request to retrieve the statistics of Kylian Mbappé for the CL 2023/2024 season.&#x20;

```javascript
https://api.sportmonks.com/v3/football/players/96611?api_token=YOUR_TOKEN&include=statistics.details.type&filters=playerStatisticSeasons:21638
```

{% file src="https://3469464275-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F9zsNGu3HAzSnl5DWBD3Y%2Fuploads%2FlTWPfckda36DBw7gReFT%2FMbappe_season_CL%20stats.json?alt=media&token=0843e94d-bf89-41a3-b5e9-95c2794f44a7" %}
Mbappé CL season stats
{% endfile %}

{% hint style="danger" %}
Including `.type` is not recommended as an include on any endpoint. Types are used throughout the entire API. We recommend retrieving all types from the types endpoint and storing them in your database or other data structure. Only include the type if no other option is available or when testing the API.
{% endhint %}

## **Standings**

### **Domestic Cup Standings**

#### **English Premier League 2023/2024 season standings**

Request to retrieve the standings of the English Premier League 2023/2024 season.

```javascript
https://api.sportmonks.com/v3/football/standings/seasons/21646?api_token=YOUR_TOKEN&include=participant;rule;details.type
```

{% file src="https://3469464275-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F9zsNGu3HAzSnl5DWBD3Y%2Fuploads%2FbddFFeDf3hjWPw35H1Gm%2FEPL_standings.json?alt=media&token=0f5f0953-8680-4cf0-8945-7e86ab670bde" %}
EPL season standings
{% endfile %}

{% hint style="danger" %}
Including `.type` is not recommended as an include on any endpoint. Types are used throughout the entire API. We recommend retrieving all types from the types endpoint and storing them in your database or other data structure. Only include the type if no other option is available or when testing the API.
{% endhint %}

### **International Cup Standings**

#### **World Cup 2022 group season standings**

Request to retrieve the group standings of the World Cup 2022.

```javascript
https://api.sportmonks.com/v3/football/standings/seasons/18017?api_token=YOUR_TOKEN&include=participant;rule;details.type
```

{% file src="https://3469464275-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F9zsNGu3HAzSnl5DWBD3Y%2Fuploads%2FF3tD1PpcxlPI8W6m3iBI%2FWorld_cup_group_standings_2022.json?alt=media&token=4002fbc4-cd21-48a7-8690-59cf0a45a92d" %}
World Cup group standings
{% endfile %}

{% hint style="danger" %}
Including `.type` is not recommended as an include on any endpoint. Types are used throughout the entire API. We recommend retrieving all types from the types endpoint and storing them in your database or other data structure. Only include the type if no other option is available or when testing the API.
{% endhint %}
