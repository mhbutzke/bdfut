# Predictions

**URL:** https://docs.sportmonks.com/football/endpoints-and-entities/endpoints/predictions

---

# Predictions | API 3.0

Enrich your applications with detailed predictions. Our Predictions API offers predictions on various markets, such as the winner, correct scores, over/under, and both teams to score (BTTS). These predictions are all available here, produced with our **machine learning** techniques and models.

Not all fixtures contain sufficient data for reliable predictions. To determine if a fixture is suitable for prediction, use the `metadata` include to check its `"predictable"` status.

Use one of our 3 probabilities endpoints. Per endpoint, you can find the details, including base URL, parameters, includes and more.

*   **GET Probabilities:** returns all probabilities available within your subscription.
    
*   **GET Performance by League ID:** returns the performance of our Predictions Model for your requested league ID.
    
*   **GET Probabilities by Fixture ID:** returns all the predictions available for your requested fixture ID.
    

All probabilities are available 21 days before the match starts.

Sportmonks also detects **Value Bets** for you. The Value Bet API is processing thousands of historical odds data and market trends to find value opportunities, compared to bookmakers\' odds.

Use one of our 2 value bets endpoints. Per endpoint, you can find the details, including base URL, parameters, includes and more.

*   **GET Value Bets:** returns all value bets available within your subscription.
    
*   **GET Value Bets by Fixture ID:** returns all the value bets available for your requested fixture ID.
    

Please note that not every match has value bets.

#### 

Include options

#### 

**Related Entities:**

Get an overview and explanation of all the fields returned in the API response. The related entities for the predictions are:

Last updated 3 months ago

Was this helpful?