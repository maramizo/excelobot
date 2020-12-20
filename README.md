## Excelobot.py
Features:
* Greetings.
* Dynamic prefixes (based on a connection to MongoDB).
* Store a week's worth of user messages upon boot.
* Display user message count on command.


Usage:
* Users with the administrator role can use **.hello** and **.goodbye** to toggle greetings.
* Greetings are sent to the system channel. If it does not exist, they are sent to the 'newcomers' and 'leavers' channels.
* Prefix command to change the prefix.

Ideas/TODOs:
* Grant roles based on activity.
* Track users based on invitation changes - find out who invited who.
* Create charts to visualize various data (messages sent per day, leaderboard changes).
* Make charts of most used words for each user.
* Make charts to show the specific hours of when a user is usually active.
* Create a web-interface for the bot to visualize the data.

Hierarchy explanation:
* Extensions - contains all the cogs and bot loaded extensions, grouped by functionality.
* Model - contains different models used by classes.
* Shared - contains classes that are loaded into the bot itself.
* Tasks - contains automated tasks that are expected to run regardless of commands (some may need to be initialized or set to run in the first place, though).

**"New ideas are hereby needed!"** - Paul Dirac.