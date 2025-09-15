# Meta description

Every request has a meta description. Let's take a look at a quick example.

<details>

<summary>Response</summary>

```javascript
   "subscription": [
    {
      "meta": [
        
      ],
      "plans": [
        {
          "plan": "Football Free Plan",
          "sport": "Football",
          "category": "Standard"
        },
        {
          "plan": "Cricket Free Plan",
          "sport": "Cricket",
          "category": "Standard"
        }
      ],
      "add_ons": [
        
      ],
      "widgets": [
        
      ]
    }
  ],
  "rate_limit": {
    "resets_in_seconds": 3600,
    "remaining": 179,
    "requested_entity": "League"
  },
  "timezone": "UTC"
}
```

</details>

It's easy to stay on top of your subscription details. You can find out what plan(s), add-ons and widgets you have, and see the timezone you're using. You'll also know when your trial ends (if you have one) and when your subscription expires. Additionally, you can see information about your rate limit. This way, you have all the information you need to manage your subscription.

In the _rate\_limit_ object, the following information is available:

* _requested\_entity:_ The requested entity for the current request&#x20;
* _remaining:_ The number of API calls remaining for the requested entity&#x20;
* _resets\_in\_seconds:_ amount of seconds left before the rate limit resets for the requested entity

{% hint style="info" %}
Check how our rate limit works in our [rate limit section.](rate-limit)
{% endhint %}
