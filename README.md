## Excelobot.py
Features:
* Greetings.
* Dynamic prefixes (based on a connection to MongoDB).


Usage:
* Users with the administrator role can use **.hello** and **.goodbye** to toggle greetings.
* Greetings are sent to the system channel. If it does not exist, they are sent to the 'newcomers' and 'leavers' channels.
* Prefix command to change the prefix.

Ideas/TODOs:
* Store all user messages.
* Grant roles based on activity.
* Track users based on invitation changes - find out who invited who.
* Create charts to visualize various data (messages sent per day, leaderboard changes).
* Make charts of most used words for each user.
* Make charts to show the specific hours of when a user is usually active.

**"New ideas are hereby needed!"** - Paul Dirac.