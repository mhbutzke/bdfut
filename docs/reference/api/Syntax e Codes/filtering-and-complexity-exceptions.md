# Filtering and Complexity Exceptions

Whenever you make a request that is accepted and gives an error based on **filters and/or complexity** you can check the status code or name in the table below for more information. The description will show more details about how the error is created and what possible steps you can take to avoid these kind of errors.

| Status | Name                    | Description                                                                                                                                                                                                              |
| ------ | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `5004` | Query complexity        | This query (includes,filters etc) is too complex to process by the server, please check [query complexity](../request-options) for more information.                                                                     |
| `5006` | Invalid query parameter | This parameter is not allowed on the request, please remove this parameter before trying again.                                                                                                                          |
| `5010` | Inapplicable Filter     | This filter cannot be used on this request, please check if the filter is correct or remove the filter. Check [filtering](../../tutorials-and-guides/tutorials/filter-and-select-fields/filtering) for more information. |

