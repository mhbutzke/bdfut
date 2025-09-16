# Best practices

Our API provides well-structured responses with strictly typed entities, such as statistics and lineups. This page provides best practices for using our data effectively in sports applications.

## Initial data load

Most of our endpoints support pagination, which means that you need to make multiple requests to retrieve all data. To make this process more efficient, we have added several options for fetching data and keeping it up to date.

You can use the _filters=populate_ query parameter on any endpoint to enable or disable certain features. When enabled, it disables all possible includes to avoid large responses and allows pagination with a page size of 1000 records. This significantly reduces the number of requests required to retrieve all data.

After you have retrieved all data, you can use the idAfter filter (ex. _filters=idAfter:50000)_ to keep your database in sync. This filter allows you to specify an ID, and it will only fetch records with IDs greater than the specified ID on the requested entity. You can quickly load and maintain your database using the idAfter filter combined with the populate filter.

## Reducing includes and response data

Our API uses Types extensively, often available as optional includes on most endpoints. To reduce the number of includes in your requests, we recommend storing Types in your database or cache. This way, you can determine an entity type without using an include all the time. Here's a complete list of the entities we recommend caching:

* States
* Types
* Continents
* Countries
* Regions
* Cities

Caching these entities can reduce the number of includes in your requests by up to half, saving bandwidth and improving response times.

## CORS (Cross-Origin Resource Sharing)

If you are developing your sports application in your browser, you might be running into something similar to the following error:

"_Request from origin https://your\_domain.com has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource_"

This is because you are directly integrating our API into the front-end of your application (most likely a browser). Directly integrating an API into the frontend of a web application can be risky as it can expose sensitive information, such as your Sportmonks API token, to potential security breaches.&#x20;

To avoid this, it is best practice to use a middleware, such as a backend or proxy server, to handle all communication between the frontend and the API. This middleware acts as an intermediary, making sure your API tokens are stored securely and not exposed to users. Using middleware makes it much harder for malicious actors to access sensitive information, keeping your application more secure overall.

## **Rate Limiting**

To ensure fair usage and maintain optimal performance for all users, adhere to our rate limiting policies:

* Familiarise yourself with our API rate limits and throttle your requests accordingly to avoid exceeding these limits. Exceeding the rate limits may result in temporary restrictions or suspension of access to the API.
* Implement client-side rate limiting to prevent excessive requests from overwhelming our servers. By adhering to reasonable request frequencies, you contribute to a smoother experience for all users of our API.

## **Optimised querying & filtering**

Make the most of advanced search options like filtering by certain characteristics or organising data, making it easier to find what you're looking for in big sets of data. Use caching techniques to save regularly used or complex search results. This saves time by cutting down on repetitive searches and makes your application work better overall.

1. You can store commonly accessed entities, like as teams and types in a local cache to reduce the frequency of API calls and improve response times. This allows you to quickly retrieve entities from the cache without making additional API requests.&#x20;
2. You can cache API responses to avoid redundant requests for data that does not frequently change. For instance, you can cache the responses of historical endpoints for statistics or standings.

