# forsen-twitter-bot
@BotForsen

### What?
Bot that tweets when [Forsen](https://www.twitch.tv/forsen) is on a promising Minecraft speedrun (timer is above 15 minutes).

### Why?
Because some people are unable to check the stream 24/7 but don't want to miss the record-setting run.

### How?
(Script is being hosted on a Heroku server)
 - Script receives notifications via the Twitch [webhooks API](https://dev.twitch.tv/docs/api/webhooks-reference)  about changes to Forsen's stream
 - If Forsen starts playing Minecraft, the script starts running
 - Once every 20 seconds, the bot takes a screenshot of the stream
 - Bot finds the speedrunning timer in the screenshot
 - If the timer is above 15 minutes, bot posts a tweet
 - If Forsen is fighting the Ender Dragon, bot post a special tweet

### Want to contribute?
Create a pull request!


### Q's?
Send them to forsenbot@gmail.com
