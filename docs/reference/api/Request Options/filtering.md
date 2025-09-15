# Filtering

## Filter your request

### Filter on includes&#x20;

Next to selecting specific fields on the base entity or includes, it’s possible to filter your request.

Filters are improved in API 3 to give even more possibilities to get the data the way you need it. Each endpoint has two types of filters, static and dynamic filters. You can combine any dynamic filter with any static filter or use a multitude.

**Static filters** are always the same and filter in one specific way without any custom options.&#x20;

The **dynamic filters** are based on entities and includes. Each dynamic filter uses an entity to filter on and one entity to apply the filter to. Below is an example with an explanation of how filters are set up.

{% hint style="info" %}
https://api.sportmonks.com/v3/football/fixtures?api\_token=YOUR\_TOKEN\&include=statistics\&filters=statisticTypes:42,49
{% endhint %}

<figure><img src="https://3469464275-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F9zsNGu3HAzSnl5DWBD3Y%2Fuploads%2FRuVSLwxBRoff4O7Pbb2S%2FFiltering.png?alt=media&#x26;token=1db20a7b-d532-4972-9cbb-91b78a969fb6" alt=""><figcaption></figcaption></figure>

1. The include or base Entity you want to filter, this entity defines what you are filtering and what results are modified. In this case, you want to filter statistics. This is always a **singular** version of the entity.
2. The Entities you expect to receive when filtering. In this case, you want to receive all the statistics that have a specific type. This is always a **plural** version of the entity.
3. The ID's you want to filter on for the 2nd part, in this case types. You can separate the ID's by using a comma.

**You can find more information in our Filtering Tutorial:**

{% content-ref url="../../tutorials-and-guides/tutorials/filter-and-select-fields/filtering" %}
[filtering](../../tutorials-and-guides/tutorials/filter-and-select-fields/filtering)
{% endcontent-ref %}
