# Events

**URL:** https://docs.sportmonks.com/football/definitions/types/events

---

# Events

## Event types

We host several events related to a fixture. Find below the event types with the description or their meaning.

<table><thead><tr><th width="81">ID</th><th>Code</th><th>Name</th><th>Description</th></tr></thead><tbody><tr><td>10</td><td>VAR</td><td><code>VAR</code></td><td>Information about VAR events like canceled goals etc</td></tr><tr><td>14</td><td>goal</td><td><code>GOAL</code></td><td>A goal is scored</td></tr><tr><td>15</td><td>owngoal</td><td><code>OWNGOAL</code></td><td>An own goal is scored</td></tr><tr><td>16</td><td>penalty</td><td><code>PENALTY</code></td><td>A penalty is scored</td></tr><tr><td>17</td><td>missed-penalty</td><td><code>MISSED\_PENALTY</code></td><td>A penalty is missed</td></tr><tr><td>18</td><td>substitution</td><td><code>SUBSTITUTION</code></td><td>A player got substituted and new player got in</td></tr><tr><td>19</td><td>yellowcard</td><td><code>YELLOWCARD</code></td><td>Yellow card is given for a player</td></tr><tr><td>20</td><td>redcard</td><td><code>REDCARD</code></td><td>Direct red card</td></tr><tr><td>21</td><td>yellowredcard</td><td><code>YELLOWREDCARD</code></td><td>Second yellow card for player resulting in a red</td></tr><tr><td>22</td><td>pen\_shootout\_miss</td><td><code>PENALTY\_SHOOTOUT\_MISS</code></td><td>Penalty in penalty shootout has been missed</td></tr><tr><td>23</td><td>pen\_shootout\_goal</td><td><code>PENALTY\_SHOOTOUT\_GOAL</code></td><td>Penalty in penalty shootout has been scored</td></tr></tbody></table>

## VAR-events types

At the moment we have the var events \`VAR\_CARD\` \`Goal Disallowed\` \`Penalty Disallowed\` \`Penalty confirmed\` \`Goal cancelled\` \`Goal confirmed\`and \`Goal under review\`.&#x20;

{% hint style="info" %}
If a var check is related to a potential goal, the event type is set to Goal under review. When the check is over, the type will be set to Goal cancelled, or the event type will be set to a goal. ​
{% endhint %}