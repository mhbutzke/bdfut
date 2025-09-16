# Rate limit

### How does the rate limit work?&#x20;

Every default plan has 3000 API calls per entity per hour.

For example: the teams entity is used in multiple [teams endpoints](about:blank). This means that all the requests made from the team endpoints count for the same entity: [teams](about:blank).

The rate starts counting after the first request has been made. The rate limit will reset back to your original amount when an hour has passed. When your API calls are depleted, until the hour is finished, you will not be able to request data from the entity for which you surpassed the rate limit\[1] . You can however make requests to other entities that have not hit the rate-limit.

For example: If you make the first of your requests at 18:18 UTC it will be reset at 19:18.

{% hint style="info" %}
Want to learn more about entities? Check our [entities section.](../endpoints-and-entities/entities)
{% endhint %}

### What happens when I hit the rate limit?&#x20;

Once you’ve hit the rate limit, you will receive a 429 response. You can check all response codes on our [response codes page](about:blank). If you reach the limit quite often, it might be interesting to upgrade the number of API calls via [my.sportmonks](https://my.sportmonks.com/).

#### How can I find how many API requests I have left?

When you make a request, the API response includes a **rate\_limit** object in the response, this object has 3 properties:

| Property            | Meaning                                                                                 |
| ------------------- | --------------------------------------------------------------------------------------- |
| resets\_in\_seconds | The amount of seconds remaining in before your rate limits resets for the given entity. |
| remaining           | The amount of requests left in the current rate limit timeframe.                        |
| requested\_entity   | The entity that the rate limit for your current request applies on.                     |

