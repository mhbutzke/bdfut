# Error codes

Whenever you receive an unexpected response, or are experiencing unexpected behaviour, you should check the request's HTTP response code and reference it with the table below. The following are all possible HTTP response codes for any request made to the API:

| Code                             | Description                                                                                                                                                                                                                                |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **`200: OK`**                    | Request succeeded                                                                                                                                                                                                                          |
| **`400: Bad Request`**           | It seems that some part of the request is malformed. The exact reason is returned in the response. This error is also show when making requests with invalid filters.                                                                      |
| **`401: Unauthorized`**          | The request is not authenticated.                                                                                                                                                                                                          |
| **`403: Forbidden`**             | Not authorized. Indicates you're attempting to access a feed that is not accessible from your plan.                                                                                                                                        |
| **`429: Too Many Requests`**     | Too many requests. In order to make the API as responsive as possible, you have an hourly request limit. The limit for your current subscription can be found in any successful response. Check the "meta" section to find out your limit. |
| **`500: Internal Server Error`** | An internal error has occurred and has been logged for further inspection. Please email support if you are receiving this error.                                                                                                           |

