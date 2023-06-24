# Lord Bottington's Full Directive List

The following is a full register of directives (commands) for Lord Bottington. Directives are separated by functionality and usage.

As more directives are added or updated, changes will be reflected here or in the latest version of [Lord Bottington's Updates](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Updates/Version%201.0.md). You may access this information by using my [`/updates`](#updates) directive within your guild on Discord, if you desire.

***Last Updated:*** `June 24, 2023`

## General Information
Each directive must be in the form `/directive-name` for proper functionality within Discord.

It is also important to note that not all directives are available to all members, meaning they require *administrative privileges for your guild*, as some can potentially contain private information (birthday information, etc.) or alter your guild functionality entirely. **Please use and assign the following directives accordingly.** 

Please do not hesitate to contact myself (*XxJSweezeyxX*) or [Join the Support Guild](https://discord.gg/4P6ApdPAF7) and contact an administrator or myself there for assistance with directives or to notify us of any bugs or updates that need to be made.

For Lord Bottington's features to work, please make sure that the following permissions are granted to the automaton within your guild.
> [See Lord Bottington's Required Permissions](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Discord%20Permissions.md)

___
<h2 align="center">
  <href=#directive-categories>Directive Categories</a>
</h2>

<p align="center">
  <a href=#core>🌐Core</a>
   ・ 
  <a href=#configuration>⚙️Configuration</a>
   ・ 
  <a href=#fun>🎉Fun</a>
   ・ 
  <a href=#games>🎮Games</a>
   ・ 
  <a href=#moderation>🛡️Moderation</a>
   ・ 
  <a href=#status>📊Status</a>
   ・ 
  <a href=#utility>🔧Utility</a>
   ・ 
  <a href=#marketplace>💰Marketplace</a>
</p>

## Core

This category is for directives related to general information for *Lord Bottington* or to assist you in changing the functionality or appearance of *Lord Bottington*.

### `/automaton`

  ![Lord Bottingtonhttps://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/b0d19df2-9425-407f-92ee-7654186c797d)

  - Retrieve information regarding the automaton's creation.
  - This is general information regarding Lord Bottington, including, but not limited to: Current nickname, uptime, invite link for Lord Bottington and for the Support guild, etc...
### `/byname`
  - [`🎩 Patron Feature`https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md)
  - Change the byname (nickname) of the automaton. (Admin only)
  - If you have administrative privileges within your guild, you may update the byname of Lord Bottington to whatever you desire.
  - This byname shall be stored in the database and used throughout *your guild only*. If no byname is set, the original name for the automaton shall be used (*Lord Bottington*).
  - *Please note that your byname must follow Lord Bottington's ToS, otherwise action shall be taken to remove this from use.*
### `/eventhandler`
  - Configure the automaton's usage and directives. (Admin Only)
  - If you have administrative privileges within your guild, you may update the functionality of the various automated capabilities of Lord Bottington within your guild for the directives within the [⚙️Configuration](#configuration) category.
    > - i.e. turn welcome messages on or off -- if configured, etc...
  - These settings will be stored in the database and used within your guild.
  - Please note that all automated functions of Lord Bottington are **enabled** by default. If this directive has not been used before and an automated function of Lord Bottington is configured, such as welcome messages, the automated function will still be used unless turned off using this directive or the configuration for the automated function has been deleted from the database.
### `/help`
  - Receive a list of OR assistance with the automaton's directives -- organized by category.
  - You will receive a short description and list of directives for the specified category.
  - You may utilize the select menu below the message to change the category and view all of my directives.
  - Take note that you may view a list of directives for the respective directive category by utilizing the link in the title or in the bottom of the description.
  - You may also find specific help for a directive, here on Github, by using the links provided as each directive name.
  - You may also use `/help directive-name` to receive information related directly to the specified directive, which will be sent ephemerally (only you can see the message) to prevent spamming.
### `/patron`
  - Enable patron (premium) features for your guild. (Admin Only)
  - When employed, this directive will allow you to enable patron features for your guild.
  - If you already have patron features enabled for your guild, and you use this directive in a different guild, you will be notified of your current patron status and patron tier for the guild you have enabled patron (premium) features in.
  - Please visit the following links to learn more information on how to obtain and maintain patron features for your guild, good sir!
    > - [❗ View Patron Info](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md)
    > - [💰 Become a Patron](https://www.patreon.com/LordBottington)
### `/ping`
  - Inquire of the latency of the automaton.
### `/updates`
  - Retrieve the latest important update information regarding the automaton.
  - This directive will return a link to the latest [Updates File](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Updates/Version%201.0.md) contained here on Github to inform users of any important information or updates.

<p align="center">
  <a href=#--directive-categories>⬆ Back to Directive Categories</a>
</p>

## Configuration

This category is for directives related to configuring the functionality of the various automated directives of Lord Bottington.

You may toggle the use of each of the events within this category by utilizing my [`/eventhandler`](#eventhandler) directive.

*All directives within this category are for users who have administrative privileges within your guild, as they alter your guild in some way.*

### `/autopurge`

  ![delete](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/48e88a42-adc2-41a1-82d5-5cc15b954430)

  - Allow the automaton to automatically purge messages from a desired channel. (Admin Only)
  - You are limited to ***5*** configurations, otherwise unlimited configurations are a [`🎩 Patron Feature`](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md).
  - When employed, this directive will delete messages in the specified channel(s) according to the input *frequency* and *messagecount*.
  - *Frequency:* This parameter controls the frequency at which the messages in the channel will be deleted and must be input as a string followed by the date character that represents the time interval, separated by spaces. If only frequency is set, *ALL* messages in the channel will be deleted at the time interval specified.
    > *Examples:* *1d 1h 1m 1s* would set the autopurge frequency to *1 day*, *1 hour*, *1 minute*, and *1 second*.n*120m* would set the duration to *2 hours*.
  - *Message Count:* This number represents the maximum number of messages in the channel before the oldest is deleted.\n> If only messagecount is set, the oldest messages will be deleted and checked for every 60 seconds.
  - *If both frequency and messagecount are set, the frequency at which the oldest messages will be retained for will be set by the frequency parameter.*
  - *Configuration Deletion:* In order to delete a configuration, simply input the desired channel into the *channel* parameter and set both the *frequency* and *messagecount* parameters to either ***0*** or leave them both blank. This will indicate that the configuration is *no longer needed* and remove it from use within your guild.
### `/autosatire`

  ![laughing](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/c3316f06-01fd-4540-89b1-221c42f6c757)

  - Configure the automated satirical image (meme) settings for the guild. (Admin Only)
  - When employed, this directive will ***automatically*** retrieve a satirical image (meme) and its respective data from a selected popular subreddit to a channel of your choice.
  - All automatically retrieved satirical imagery is sent to your desired channel at `9:00:00 AM US/Central` time.
  - The information and images are provided by [Reddit](https://www.reddit.com/) and its various meme subreddits.
  - Post author and other information regarding the retrieved post will be displayed for you.
  - Please note that if no satirical images are found in your current search, it *could* mean that no appropriate images were found *OR* the subreddit has switched to *private*.
  - **Simply try a different community until you are successful in setting a channel.**
  - It is also important to note that inappropriate and tastless images are mitigated to the best of my ability according to their *NSFW* tags.
  - *Please enjoy an automatically generated good and entertaining laugh with your guild, good sir.*
  - [Asyncpraw](https://asyncpraw.readthedocs.io/en/stable/index.html) used to retrieve the satirical images.
### `/birthday`

  ![cake](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/9e3ea4c8-fa89-4200-aa91-e35f034cfd8c)

  - Configure the settings for the automaton's birthday messages. (Admin Only)
  - Certain customization options are [`🎩 Patron Features`](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md).
  - Using this directive, birthday messages and status that are sent to users may be modified using a custom message or an automaton defined message to wish users a happy birthday.
  - However, all image and text configurations must follow Lord Bottington's ToS, otherwise action will be taken to remove your configuration from use.
  - Lord Bottington **must have a higher status in your guild** than the status that is used for birthday messages, if used, as Lord Bottington cannot assign statuses to members that are higher than the automaton.
  - All birthday messages are sent to the proper channels and statuses are distributed and removed accordingly at `12:00:00 AM US/Central` to provide users a full day of their birthday celebration.
  - *However, if the user does not set their birthday **before** midnight of the actual day, the automaton will be unable to distribute the birthday message and status accordingly.*
  - *Markdown Syntax:* The following variables may be used in the birthday message to display the respective information.
    > *[General Markdown Syntax](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-)*
    > + `{member.mention}` - Mention joining user
    > + `{member.display_name}` - User's display name
    > + `{birthday_role_name}` - Birthday status name (if set)
    > + `{birthday_role_mention}` - Mention birthday status (if set)
    > + `{member.guild.name}` - Server Name
    > + `{byname}` - Byname (nickname) of the automaton
### `/moderate`
  - Configure the moderation message settings for the guild. (Admin Only)
  - This directive will allow the user to change where moderation messages are sent to within the guild, such as when a user is banished (banned) or removed (kicked), as well as the warning list for the specified user (if they have any).
  - If no channel is set or the channel is removed from the database, the messages will be sent to the same channel where the directive was used.
### `/starboard`

  ![star_spin](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/ec127386-601c-40f9-815b-7cf88868c33f)

  - Configure the settings for the starboard messages. (Admin Only)
  - Certain customization options are [`🎩 Patron Features`](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md).
  - You may configure such things as what channel the starboard messages are sent to, how many reactions the message must have (threshold), what channel the messages are sent to when the threshold is met, etc...
  - The threshold minimum is set to 1, to prevent spamming of the starboard messages.
  - The channel where starboard messages are sent can NOT be the same as the channels where reactions are listened for.
  - *It is also important to note that messages by automatons will be not be ignored and automatic reactions will be added to their messages. So, be aware that this might cause spamming of reactions on automaton messages if many are sent within the channel that is specified.*
### `/streaming`

  ![platform-icons](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/2552365b-4c97-4a03-8604-3f3f111fdda8)

  - Configure the settings for streaming statuses and notifications. (Admin Only)
  - Certain customization options are [`🎩 Patron Features`](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md).
  - You may configure whether members within your guild receive a special status, where notifications with the streaming information is sent in your guild, various message configurations for the notifications, etc...
  - However, all image and text configurations must follow Lord Bottington's ToS, otherwise action will be taken to remove your configuration from use.
  - Lord Bottington **must have a higher status in your guild** than the status that is used for streaming notifications, if used, as Lord Bottington cannot assign statuses to members that are higher than the automaton.
  - Features for streaming notifications will **ONLY** work if the specified users have their streaming platform (Twitch, YouTube, etc...) linked to their Discord account and **STREAMING MODE IS ENABLED**.
  - *The following links should provide the information needed to allow my streaming notifications to succeed, good sir:*
    > + [Discord Linked Roles](https://support.discord.com/hc/en-us/articles/10388356626711-Connections-Linked-Roles-Admins)
    > + [Link Twitch Account to Discord](https://support.discord.com/hc/en-us/articles/212112068-Twitch-Integration-FAQ)
    > + [Enable Streamer Mode](https://support.discord.com/hc/en-us/articles/218485407-Streamer-Mode-101)
  - *Markdown Syntax:* The following variables may be used in the message and embed body strings to display the respective information.
    > *[General Markdown Syntax](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-):*
    > + `{member.display_name}` - Streamer display name
    > + `{member.guild.name}` - Streaming server
    > 
    > *Streaming Message Only:*
    > + `{member.mention}` - Mention the streamer
### `/timedembeds`

  ![timer](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/f2ac1969-9eb0-441c-9aeb-d038c2768e19)

  - Configure the settings for the timed embed messages (Admin Only)
  - Certain customization options as well as unlimited configurations are [`🎩 Patron Features`](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md).
  - You may configure the settings for when timed embeds are sent to specified channels and the text and images within this embed to notify your members of different things.
  - However, all image and text configurations must follow Lord Bottington's ToS, otherwise action will be taken to remove your configuration from use.
  - *General Usage*
    > + Upon use, the `/timedembeds` directive will prompt you in a separate text box for an embed title, body, field name, or field value *after* you have submitted your initial configurations.
    > + Timed embeds may be sent on a recurring basis or once at a specified time using the *intervaltype* parameter.
    > + Thumbnail and image files must be a **direct link** to an image of the JPG, JPEG, PNG, or GIF formats for proper functionality.
    > + You may use an image hosting site like IMGUR for this, if you desire.
    > + Any text box not filled in within the `Embeds Text Configuration` will be taken as not desired, and will *not* appear in the timed embed.
    > + **Note:** Each server is allowed a maximum of 5 timed embed messages for use. Use them wisely, good sir.
    > + Please use `/embedslist` to view your timed embed configurations.
  - *Configuration Removal*
    > - In order to remove a configuration from use, simply input the configuration name and set the *interval* parameter to ***0***. This will indicate that the configuration is no longer needed.
    > It is advisable to remove all embed configurations that have already past or are no longer needed to clear up space.
  - *Markdown Syntax:* The following is a list of syntax parameters you may employ for use in the timed embeds.
    > - [General Markdown Syntax](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-)
### `/welcome`

  ![welcome](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/23122277-0e0e-43c1-be56-79476beaad47)

  - Configure the settings for the welcome messages. (Admin Only)
  - Certain customization options are [`🎩 Patron Features`](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md).
  - You may configure whether members within your guild receive a greeting from myself upon joining. You may configure such things as the background image, user avatar picture, message and image text, etc...
  - However, all image and text configurations must follow Lord Bottington's ToS, otherwise action will be taken to remove your configuration from use.
  - Background images and avatar images must be a **direct link** to a file of the JPG, JPEG, or PNG file format for proper functionality.
  - You may use an image hosting site like IMGUR for this, if you desire.
  - *Markdown Syntax:* The following variables may be used in the welcome message and image text strings to display the respective information.
    > *[General Markdown Syntax](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-):*
    >   - `{member.display_name}` - User's display name
    >   - `{member.guild.name}` - Server Name
    >   - `{member_count}` - Joining user's number for the server
    >   - `{on_join_status}` - Status given to new members upon joining (if set)
    >   - `{byname}` - Byname (nickname) of the automaton
    >   
    > *Welcome Message Only:*
    >   - `{member.mention}` - Mention joining user
    >   - `{on_join_status_mention}` - Mention the status given to users upon joining

<p align="center">
  <a href=#--directive-categories>⬆ Back to Directive Categories</a>
</p>

## Status

This category is for directives related to updating your status or information within the guild in order to receive specific statuses or information related to this.

  ![cake](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/dedb3705-9314-489e-9184-85f4715a3bae)

### `/birthdaylist`
  - Allow the automaton to provide you a list of all dates of birth for your guild. (Admin Only)
  - If you administrative privileges with your guild, you may retrieve a list of the birthdays (*day/month*) for the server as an embed or plain text message, sent ephemerally (only you may see it), as this contains sensitive user information.
### `/getbirthday`
  - Allow the automaton to provide you with a user's date of birth.
  - You may retrieve your OWN birthday from the database if it has been set.
  - If you have administrative privileges within your guild, you may retrieve any user's birthday within your own guild, otherwise, you may only retrieve your own.
### `/removebirthday`
  - Allow the automaton to remove a date of birth from the register.
  - You may remove your OWN birthday from the database.
  - If you have administrative privileges within your guild, you may remove any user's birthday from the guild, otherwise you may only remove your own.
### `/setbirthday`
  - Manually input thy date of birth for the automaton to commit to memory.
  - Set your birthday for the automaton to wish you the happiest of birthdays and receive a special status for the entire day, if configured using `/birthday`.

<p align="center">
  <a href=#--directive-categories>⬆ Back to Directive Categories</a>
</p>

## Utility

This category is for directives related to performing various utility actions for your guild, such as helping facilitate gift giving (giveaways) or managing the iconography (emojis) for your guild.

### `/autopurgelist`

  ![delete](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/375bb29c-486e-4b00-805e-042f585b84cc)

  - Receive a list of currently autopurged channels for the guild. (Admin Only)
  - If you have administrative privileges within your guild, you may retrieve this list in order to help you determine the channel(s) that I am automatically purging for your guild.
### `/conceal`
  - Conceal a message to allow others a chance to avoid content spoilers. (Attachments optional)
  - Will conceal the content of a regular message or a link with its preview (i.e. YouTube link, etc...), including any attachments added.
  - The directive must be used **directly** after the message that is to be concealed within the same channel to work.
  - Any files that are **NOT** an *image* (.jpg, .png, .gif, etc...) or *video* (.mp4, .mov, etc...) will be added as a concealed, direct link to the file and the original message shall be removed from view.
### `/defineimproper`
  - The automaton will define a term for you in its improper (slang/urban) form.
  - When employed, the automaton will return the definition for a desired term from [Urban Dictionary](https://www.urbandictionary.com/) as well as other related information and examples.
  - *Please note that definition results are **censored** by default, but may be uncensored, if desired.*
  - Take care to use this directive wisely and follow Lord Bottington's TOS, good sir.
### `/defineproper`
  - The automaton will define a term for you in its proper form.
  - When employed, the automaton will return the definition for a desired term provided by [Free Dictionary](https://dictionaryapi.dev/) as well as other related information and examples.
  - Take care to use this directive wisely and follow Lord Bottington's TOS, good sir.
### `/embedder`
  - Send embedded messages to a channel. (Admin Only)
  - If you have administrative privileges within your guild, you may configure and send these messages with your own desired text and images.
  - However, all image and text configurations must follow Lord Bottington's ToS, otherwise action will be taken to disable your usage of this directive within your guild.
### `/embedslist`
  - List all the timed embeds created so far. (Admin Only)
  - If you have *administrative privileges* within your guild, you may retrieve this list in order to help you determine the information about the embeds that are currently being sent using my [`/timedembeds`](#timedembeds) directive within your guild.
### `/giftgiving`

  ![gift](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/4ddfd1f5-4a88-4b2c-9b5a-9b48fdecf192)

  - Permit the automaton to arrange a prize drawing for an item of your preference. (Admin Only)
  - If you have administrative privileges within your guild, you may configure and send an interactive message for members of your guild to join a giveaway, with your own text and image configurations.
  - However, all image and text configurations must follow Lord Bottington's ToS, otherwise action will be taken to disable your usage of this directive within your guild.
  - *Beginning the Prize Drawing*
    > - *Prize:* The prize you would like to give may be input as a string of characters and may include iconography (emojis).
    > - *Duration:* A duration must be set for the length of the the prize drawing as integers followed by the date character that represents the time interval, separated by spaces.
      > - Examples: *1d 1h 1m 1s* would set the total duration of the prize drawing to *1 day*, *1 hour*, *1 minute*, and *1 second*. *72h* would set the duration to *3 days*.
    > - *Winner Count:* The number of winners must be an integer between 1 and 20. Therefore, at least one winner must be chosen for the prize drawing and *up to* 20 individuals may also receive the prize. If the number of participants is greater than this value, a random number of participants equal to this *winners* value will be chosen. This maximum value is set to prevent spamming.
   - *Participation:* The participation parameter may be set to *TRUE* if you prefer the number of participants to reach the winner count before a winner is chosen. If this parameter is set to *FALSE*, the prize will be distributed to all participants, regardless of the winner count. In both situations, if there are *no* participants, a winner will not be chosen. By default, this value is set to *TRUE*.
   - *Color:* Furthermore, you may choose a color for the prize drawing embed, to further customize the experience. By default, the embed color will be *🔵 Blue*.
   - *Image:* An image may be sent in the embed to provide you with the option to display an image for the prize you are giving. *This must be a JPG, JPEG, PNG or GIF file.
   -  Once these parameters have been set, you may send the embed to begin the prize drawing and commence the countdown.
   -  *Avatar photograph will be displayed as the thumbnail (if one is found).*
   -  *Participating in the Prize Drawing:*
      > - Users who would like to participate in the prize drawing may utilize the `🎁 Join Prize Drawing` button.
      > - The individual who initated the prize drawing may *not* join the drawing and everyone may only enter into each drawing *once*.
   - *Ending Prize Drawing and Choosing Winner(s):*
     > - Once the countdown has ended, a winner will be selected based on the parameters set when the prize drawing was initiated.
     > - However, at any time, the individual who initiated the prize drawing *OR* an administrator may utilize the `🛑 End Prize Drawing` button to stop the countdown and select the winner(s).
     > - The prize drawing embed will reflect the number of winners and the time the prize drawing ended, localized to *US/Central Time*.
     > - Furthermore, a message will be sent above the embed mentioning the winner(s), if any were selected.
### `/iconography`
  
  ![goodsir](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/1a7bc378-8cda-4b83-b2dd-1755519e4df3)

  - Receive a list of the guild's iconography.
  - When employed, this directive will return an embed containing all of the static and animated iconography (emojis) for the guild in which it was used.
  - If desired, direct links to the icons can be added next to each icon to allow the icons to be downloaded by setting the `iconlinks` option to *TRUE* and are turned *ON* by default.
  - Those with administrative permissions will be able to post the list for all to see, while those without will be able to post the list only visible to themselves (in order to prevent spamming).
  - Furthermore, administrators may utilize the following buttons, once the list has been posted:
     > - `😀 Add Iconography` - Permits the addition of an icon to the guild.
     > - `❌ Remove Iconography` - Permits the removal of an icon from the guild.
     > - `🚫 Cancel` - Removes the icon list from view.
   - It is also important to note that when adding an icon using the `😀 Add Iconography` button, you must submit a *picture* file when prompted (i.e. *.jpg*, *.jpeg*, *.png*, or *.gif* - *.gif* files will be added as *animated* icons while the rest will be added as static icons).
   - Submitted files must follow a certain naming syntax. If you are having trouble, try shortening the file name to 2 words or less and submitting again.
   - The following documentation might be of use to you as well: [Icon Syntax Documentation](<https://discord.com/blog/beginners-guide-to-custom-emojis#:~:text=Any%20emoji%20uploaded%20to%20your,go%20ahead%20and%20compress%20it.>)
   - Furthermore, when using the `❌ Remove Iconography` button, you must enter the icon name *directly* into the chat box on Discord when prompted.
   - *I hope this serves you well in your endeavors, good sir.*
### `/play`

  ![controller](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/6d5d4f49-cc13-4631-acb0-acb53a46e1ce)

  - The automaton will help you reach out to other like-minded players in search of game companions.
  - This directive will send an interactive message for members of your guild to interact with and join, think about, or deny playing with you, if they desire.
  - Several games are pre-defined to choose from but any game can be input into the *other_game* parameter to send the embed without an image.
  - If the game is chosen from the pre-defined list, an image of the game will be sent in the embed.
### `/purge`

  ![delete](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/5c0b12ca-1662-4aba-b5ca-5ed4d3f0f4be)

  - Purge messages from a desired channel. (Manage Messages Privileges)
  - This directive allows users to remove a certain number of messages from a specified channel.
  - Users can only remove up to ***100*** messages at a time to avoid rate-limiting.
  - This directive will remove the *most recent* messages up to the value specified.
  - *Please note that this directive requires that the user AND automaton have the **manage messages** permissions for the guild (administrators have this permission).*
  - Refer to the following documentation to grant these permissions: [Discord Server Permissions](<https://support.discord.com/hc/en-us/articles/206029707-Setting-Up-Permissions-FAQ#h_01FFTVYFNVY8GHKTHCFBXMBGAZ>)
### `/search`
  - The automaton will demonstrate how to find something on the internet.
  - When emplyed, a link demonstrating how to find your desired search terms on Google will be returned.
  - *Please note that search terms must pass a check for inappropriate terms, good sir. Otherwise, the search demonstration will not move forward.*
  - Take care to use this directive wisely and follow Lord Bottington's TOS, good sir.
### `/testwelcome`

  ![welcome](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/ef0e0ebc-63bd-4a29-bf6c-6b1136e4a2fd)

  - Test how the automaton welcomes newcomers. (Admin Only)
  - If you have administrative privileges within your guild, you may test how the welcome message configuration that is set up using the `/welcome` directive looks.
  - You may tag another member of the guild or yourself.
  - This is useful when trying to configure the welcome messages to see a preview of how I will greet new members to the guild.
### `/weather`

  ![weather](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/a6566707-61be-4492-a250-9d35ce00ae7d)

  - [`🎩 Patron Feature`](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md)
  - Allow the automaton to retrieve the weather data for your location of choice.
  - Input a city name to receive the weather information for the specified location. You may also include the state, if you desire, to narrow down your search results.
  - This information is provided by [Weather API](https://www.weatherapi.com/).
  - The information will include data on the *current* day and time the directive is used.
  - Information related to the *temperature*, *condition*, *precipitation*, *wind speed*, and much more will de displayed for you, with an embed color that matches the condition.
  - Please note that the embed can be sent publicly or privately, so as to keep the location information private for you, if you wish. This will be set to *ON* by default and can be changed.
  - It is also important to note that the weather information will *not* be retrieved if the location is unable to be found or the amount of times the directive is used *exceeds* a certain amount, so please employ this directive sparingly.

<p align="center">
  <a href=#--directive-categories>⬆ Back to Directive Categories</a>
</p>

## Moderation

This category is for directives related to providing you the ability to moderate your guild and its members.

*All directives within this category are for users who have administrative privileges within your guild, as they alter your guild or its members in some way.*

Notifications for the following directives will be sent to the channel specified when using the [`/moderate`](#moderate) directive.

### `/banish`
  - The automaton will banish (ban) a member from the guild. (Admin Only)
  - If you have administrative privileges within your guild, you may use this directive to ban a member from your guild and provide a reason, if desired.
### `/remove`
  - The automaton will remove (kick) a member from the guild. (Admin Only)
  - If you have administrative privileges within your guild, you may use this directive to kick a member from your guild and provide a reason, if desired.
### `/silence`
  - The automaton will silence (mute) a member within the guild. (Admin Only)
  - If you have administrative privileges within your guild, you may use this directive to mute a member from your guild and provide a reason, if desired.
  - This directive works by creating a status (role) with the name **Silenced**, giving this status a position that is *directly below* my own within your guild, and assigning it to the desired user. This status will have no privileges in your guild.
### `/unbanish`
  - The automaton will unbanish (unban) a member from the guild. (Admin Only)
  - If you have administrative privileges within your guild, you may use this directive to unban a member from your guild and provide a reason, if desired.
### `/unsilence`
  - The automaton will unsilence (unmute) a member within the guild. (Admin Only)
  - If you have administrative privileges within your guild, you may use this directive to unmute a member from your guild and provide a reason, if desired.
  - This directive works by removing the status (role) with the name **Silenced** that is created when using the `/silence` command, if it has been used in your guild before.
### `/warn`
  - The automaton will warn a member within the guild. (Admin Only)
  - If you have administrative privileges within your guild, you may add a singular warning to a specified user within your guild and store this information in the database.
  - Each user within your guild has a maximum of ***3*** warnings. Once this has been reached, the guild will be notified and it will be up to your discretion as to remove the member from the guild or remove a warning for the user, if desired.
### `/warninglist`
  - The automaton will provide a list of warnings for a member within the guild. (Admin Only)
  - If you have administrative privileges within your guild, you may use this directive to retrieve the list of warnings for a specified user within your guild.
### `/warnremove`
  - The automaton will remove a warning from a member within the guild. (Admin Only)
  - If you have administrative privileges within your guild, you may use this directive to remove a warning from a member within your guild by providing the index for the warning.
  - You may see the index of the warning by using my `/warninglist` directive.

<p align="center">
  <a href=#--directive-categories>⬆ Back to Directive Categories</a>
</p>

## Fun

This category is for directives related to providing members of your guild with entertainment.

### `/boredom`
  - The automaton will provide a suggestion to help you alleviate your boredom.
  - When employed, the automaton will provide you with an activity and related information to alleviate your boredom.
  - Information regarding this activity includes the type of activity, the number of recommended participants, and much more.
  - This information is provided by [The Bored API](https://www.boredapi.com/).
  - *I hope I am able to alleviate your boredom, good sir.*
### `/compliment`
  - Allow the automaton to extend a sincere compliment to you or a fellow member.
### `/converse`
  - [`🎩 Patron Feature`](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md)
  - Ask the automaton anything you would like.
  - When employed, this directive will allow you to converse with the automaton and ask any question your heart desires.
  - This directive utilizes ChatGPT integration to allow fluid conversation capabilities.
  - *Identity*
    > - You may also choose an *identity* for the automaton to speak as.
    > - There is a wide range of characters the automaton can imitiate, ranging from video game and movie characters to other general characters.
    > - The default for this parameter (i.e. The Automaton) allows you to converse with Lord Bottington and his gentlemanly personality.
    > - If you have [`🎩 Patron Features`](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md) for your guild, you may use the `/byname` directive to change the automaton's name to something else and converse with the automaton using your own custom byname (nickname).
  - *Free Tries*
    > - Each person receives ***5*** free tries for this directive in order to give the capability to test out the functionality.
    > - Past this, you will have to look into upgrading to patron (premium) features to allow full use of this directive!
  - *I look forward to conversing with you, good sir!*
### `/crystalball`

  ![crystalball](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/8f07c6e8-e2ef-4e08-8847-f547d09d4807)

  - Seek guidance from the crystall ball and unveil the mysteries of the universe.
  - Using this directive will grant you access to answers previously unknown...🔮
  - *Please note that inquiries must end with a question mark `?` to ensure proper functionality.*
### `/glyph`

  ![ascii-unclesam](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/e5534743-b099-4b13-a035-e470c312548f)

  - The automaton will return a glyph (ascii art) of the desired selection.
  - When employed, this directive will return a glyph image (ascii art) of either an image (default selection or custom image file) *OR* a text string.
    > - Custom images will be returned as a *.txt* file entitled ***ascii_art.txt***.
    > - *Please note that custom images are a [`🎩 Patron Feature`](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md) only.*
  - If a text string is desired for conversion, you must set the *text* parameter to True.
  - You may also select a font for the text conversion. (Default font: small)
  - If the font has *rnd* or *random* in the name, that indicates a random selection from the respective font library.
  - If no image or text has been input to the directive, the directive author's username will be returned as a glyph in a random font.
  - However, if the username is too long or the random font is too large, the text string *HELLO* will be returned in a random font instead.
  - Refer to the following documentation for more information on textual conversions: [ASCII Art Library for Python](<https://pypi.org/project/art/>)
  - Refer to the following link for default images source: [ASCII Art](https://emojicombos.com/funny-ascii-art)
### `/greet`
  - Greet the automaton.
### `/imagine`
  - [`🎩 Patron Feature`](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md)
  - Allow the automaton to generate an image based on your prompt.
  - When employed, this directive will allow you to generate an image from a prompt.
  - This directive utilizes OpenAI Dall-E integration to allow image generation.
  - The automaton will generate an image closest to your description.
  - It is important to note that the more descriptive you are in your prompt, the closer the generated image will be to your description.
  - You may also generate variations of your original generated image using the `🔀 Create Variation` button, if you desire.
  - *Free Tries*
    > - Each person receives ***5*** free tries for this directive in order to give the capability to test out the functionality.
    > - Past this, you will have to look into upgrading to patron (premium) features to allow full use of this directive!
  - *I look forward to seeing your creativity, good sir!*
### `/minotar`

  ![steve](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/e4ea79cd-adb3-47d1-9c09-a2bd92c124c5)

  - The automaton shall procure a Minecraft user's esteemed visage for you.
  - User avatar and skin images are retirieved using [Minotar](https://minotar.net/).
  - The *user* parameter must be a ***Minecraft*** user name *OR* a Universally Unique Identifier (UUID).
  - You may find a user's UUID or username by [clicking here](https://minecraftuuid.com/).
  - You may select from several diffent styles of images ranging from the user's `🧑 Avatar` to their `🎨 Skin`.
  - You may also download the skins by setting the *download* parameter to `TRUE`.
    > - You will receive a link that, when used, will redirect to a download link for the desired user's skin such as the following:
    > - [Download Default Skin](https://minotar.net/download/MHF_Steve)
### `/pictorialize`

  ![goodsir](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/d9ffd112-b9a8-4d2f-a6a8-4c0df74f8071)

  - The automaton shall transform avatars, images, and text into iconography or apply image effects.
  - *Image Alteration 🖼*
    > - Images or user avatars may be altered using an entertaining effect, if desired. See note in *Iconify Alteration* for image link and username input syntax.
    > - Some effects are currently not supported for video formatted files, such as *.gif* files. In those cases, the initial frame of the file shall be returned with the desired alteration.
    > - The *display_original* option may be used to show the original image, for comparison purposes. This setting will be turned *ON* by default.
    > 
    > *The following effects may be applied to the images:*
    > - `Iconify` - Render in iconographic form (see below)
    > - `Mirror` - Reflect
    > - `Flip` - Turn over
    > - `Grayscale` - Render in grayscale
    > - `Invert` - Invert colors
    > - `Colorize` - Add different colors
    > - `Pixelate` - Render in mosaic form
    > - `Old Timey` - Give an old-timey feel
    > - `Posterize` - Posterize into fewer tones
    > - `Solarize` - Create a solarized effect.
    > - `Enhance` - Sharpen and brighten.
    > - `Thumbnail` - Resize to *256x256*.
  - *Iconify Alteration ⬜*
    > - The automaton works to obtain the pixels from an image (avatar url or user defined imagery) and convert them to the closest icon ⬜🟥🟩⬛.
    > - While not 100% accurate, the directive works best for *simpler* image designs.
    > - The default size begins at ***14***, but you may increase this to enhance the detail of the output image until the Discord-enforced character message limit is reached. Once reached, sizes larger than ***2000*** characters will zoom in on the picture to show even more enhanced detail, while sacrificing the outer edges of the image.
    > - *Maximum size value varies depending on the submission.*
    > - You may test this by copying and pasting this link as the directive item, good sir: [Example Link (Among Us)](https://i.imgur.com/VIX8Yyh.png)
    > - *Note:* User names must be prefaced with '@' and links must be *direct links* to the images (beginning with *http://* or *https://* and ending with .jpg, .jpeg, .png, or .gif - *.gif files will use the initial frame of the file*).
  - *File Input*
    > - Custom files and links are a [`🎩 Patron Feature`](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md).
    > - Either a direct link to an image or a file attachment may be used.
    > - If both are input, the file attachment will be used instead.
    > - However, if neither are input, the avatar of the directive author will be used.
  - *Plain Text Strings*
    > - The automaton is also able to convert *plain text strings* to their respective icons, if desired.
    > - The following iconography is defined and may be used in your string. However, it is important to note that there can be *no space* between the two string characters, and they may not be located next to other character strings (most of the time).
      > - `:)`:smile: `:(`:slightly_frowning_face: `:D`:grinning: `:O`:open_mouth: `:P`:stuck_out_tongue:
      > - `:|`:neutral_face: `:/`:confused: `:s`:confounded: `:*`:kissing_heart: `;)`:wink:
      > 
      > - *Note:* If a punctuation or letter is not defined when trying to convert a plain text string to emoticons, it will simply remain a regular character.
### `/roll`

  ![dice](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/c26f490a-a2ab-46a8-820e-615da2a4b6c2)

  - Roll dice with a chosen number of sides.
  - When employed, this directive allows you to roll a specified number of dice each with a set number of sides.
  - *Limitations*
    > - You may only have up to ***25*** total dice rolled at one time.
    > - Each die must have at least ***2*** sides each, to ensure a proper roll.
    > - Furthermore, each die can have up to ***999,999,999,999,999*** sides. Surely you will never need more...
### `/satireimage`

  ![laughing](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/63f066b2-a922-44c8-8b65-f82436f39276)

  - When employed, this directive will return a randomly selected satirical image (meme) from a random or selected popular subreddit and provide information relating to the image.
  - The information and images are provided by [Reddit](https://www.reddit.com/) from its various meme subreddits.
  - Post author and other information regarding the retrieved post is also displayed for you.
  - Please note that if no satirical images are found in your current search, it *could* mean that no appropriate images were found *OR* the subreddit has switched to *private*.
    > - Simply try again until a satirical image is returned.
  - It is also important to note that inappropriate and tastless images are mitigated to the best of my ability according to their *NSFW* tags.
  - *Please enjoy a good and entertaining laugh with your guild, good sir.*
  - [Asyncpraw](https://asyncpraw.readthedocs.io/en/stable/index.html) used to retrieve the satirical images.
### `/teatime`
  - Request a virtual tea service from the automaton.
### `/thought`
  - Allow the automaton to enlighten you with its vast knowledge.
  - Lord Bottington has several categories of thought that he is well-versed in and can provide to you.
    > - `🧑‍🦳 Father Humor` - Hear a humorous, paternal anecdote. (Paternal anecdotes provided by [icanhazdadjoke](https://icanhazdadjoke.com/))
    > - `🤔 Deep Thought` - Reveal a deep thought...
    > - `❗ Random Fact` - Receive a random useless fact. (Random facts provided by [UselessFacts](https://uselessfacts.jsph.pl/))
    > - `💻 Technological` - Get help sounding more technologically savvy. (Technological phrases provided by [Techy](https://techy-api.vercel.app/))

<p align="center">
  <a href=#--directive-categories>⬆ Back to Directive Categories</a>
</p>

## Games

This category is for directives related to providing members of your guild with entertainment through challenging games.

Members of your guild may face each other *OR* myself in the following games with varying degrees of difficulty. Each member has the chance to earn `🪙 Shillings` to spend on various items in the shop and show off to others in your guild!

I will also keep up with the top **10** winners and earners for each of the games within your guild, which you may view using my `/toptalent` directive, if you desire.

### `/battleship`

  ![battleship](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/d209335d-6aa1-432f-bd68-d424ac43328a)

  - Challenge the automaton or another member of the guild to a game of Battleship.
  - You may challenge another member *OR* the automaton to an exciting game of Battleship using this directive.
  - Simply preface the desired member's username with `@` in the *player2* parameter and the game will commence.
  - *Please note that the game will end if there is no interaction with the interface after **2 minutes** to ensure efficiency on the automaton's end.*
  - The game ends when either user **🏳 Surrenders** or **Sinks** all of their opponent's vessels in their fleet.
  - Each fleet contains the following vessels and are represented by the corresponding colors and lengths:
    > - `🟨 Destroyer (2)`
    > - `🟩 Submarine (3)`
    > - `🟪 Cruiser (3)`
    > - `🟧 Battleship (4)`
    > - `⬛ Carrier (5)`
  - On your turn, simply select the desired coordinates and `💥 Fire` at your opponent's fleet. you will be notified if you have `⚪ Missed!` or `🔴 Hit!` one of your opponent's vessels.
  - You will also be notified when any of your vessels in your fleet have been sunk, as well as your remaining vessels in your fleet.
  - You may view your fleet layout for the game using the `🔎 View Fleet` button. *This will only be visible to yourself.*
  - It is also important to note that when facing the automaton (`@Lord Bottington` or whatever the byname/nickname is for the guild) you may select a difficulty for the round.
  - Depending upon your difficulty level, you will earn `🪙 Shillings` for your wins to spend on various items in the shop, which are noted below:
    > - `🟩 Easy` (🪙x2)
    > - `🟨 Medium` (🪙x5)
    > - `🟥 Hard` *OR* `another member of your guild` (🪙x10)
  - *Choose wisely and have fun, good sir!*
### `/connectfour`

  ![connectfour](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/d4a7d96d-345d-4197-ab9f-fc4dcea61178)

  - Challenge the automaton or another member of the guild to a game of Connect Four.
  - You may challenge another member *OR* the automaton to an exciting game of Connect FOur using this directive.
  - Simply preface the desired member's username with `@` in the *player2* parameter and the game will commence.
  - *Please note that the game will end if there is no interaction with the interface after **2 minutes** to ensure efficiency on the automaton's end.*
  - You may also choose which symbol you desire to be for the duration of the game (Player 2 will be the opposite symbol for the round).
  - It is also important to note that when facing the automaton (`@Lord Bottington` or whatever the byname/nickname is for the guild) you may select a difficulty for the round.
  - Depending upon your difficulty level, you will earn `🪙 Shillings` for your wins to spend on various items in the shop, which are noted below:
    > - `🟩 Easy` (🪙x2)
    > - `🟨 Medium` (🪙x5)
    > - `🟥 Hard` *OR* `another member of your guild` (🪙x10)
  - *Choose wisely and have fun, good sir!*
### `/mastermind`
  
  ![mastermind](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/8e062063-4070-42b6-a89d-30efb6629644)

  - Decipher the secret code of the automaton.
  - *Introduction*
    > Welcome, dear player, to the enigmatic realm of Mastermind, a test of wit and cunning. Your noble quest is to decipher the secret code crafted by a most cunning mastermind. You shall engage in a battle of intellect and deduction.
  - *The Code*
    > The mastermind, in his ingenuity, has fashioned a hidden code consisting of a sequence of colored pegs. These pegs can be of different hues, each representing a distinct color. Alas, the exact sequence eludes your grasp.
  - *The Challenge*
    > Your task, dear player, is to uncover the secret code within a limited number of attempts. Each attempt shall be made by crafting your own sequence of colored pegs, striving to match the hidden code, with a desired difficulty *(Easy -> Hard)* that increases the number of required pegs to match.
  - *The Clues*
    > The mastermind shall not make your endeavor an easy one. After each attempt, he shall provide you with vital clues. The clues manifest as a series of small pegs in two distinct colors: white`🔲` and black`🔳`
      > - *Black Pegs:* A black peg`🔳` signifies the presence of a correct color within your attempt but in an *incorrect* position. It indicates that a peg of the chosen color exists in the hidden code, albeit not in the spot you placed it.
      > - *White Pegs:* Ah, the white pegs`🔲`, the pinnacle of success. These resplendent gems signify the presence of both a correct color and its precise position within your attempt. They herald your triumph and inch you closer to victory...
  - *Deductive Reasoning*
    > Armed with the clues, you must employ your astute deductive reasoning to refine your subsequent attempts. Discard incorrect colors and adjust their positions, for the secrets of the code shall only be revealed through careful analysis and strategic thinking.
  - *The Ultimate Challenge*
    > In the face of adversity, remember that the number of attempts granted to you is finite ***(10)*** . With each valiant endeavor, the mastermind shall assess your progress and reveal his cunning nature through the clues he bestows. Seek to decipher the code within the allotted attempts and emerge as the **true victor**.
  - Depending upon your difficulty level, you will earn `🪙 Shillings` for your wins to spend on various items in the shop, which are noted below:
    > - `🟩 Easy` (🪙x2)
    > - `🟨 Medium` (🪙x5)
    > - `🟥 Hard` (🪙x10)
  - *Let the pursuit of unraveling the hidden code commence!*
### `/playerinfo`
  - Check game related information for a member within the guild.
  - When employed, this directive will return information regarding the game playing information for a user within the guild.
  - This information includes the player's favorite game, wins & earnings for each game, etc...
  - It is also important to note that only those with *administrative privileges* within your guild may access other users game information.
  - However, those without these privileges may still view their own game information within the guild.
### `/rps`

  ![rps](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/4802c8d6-3931-4460-9674-e61eecdb4e5d)

  - Challenge the automaton or another member of the guild to a game of rock, paper, scissors.
  - You may challenge another member *OR* the automaton to an exciting game of rock, paper, scissors using this directive.
  - Simply preface the desired member's username with `@` in the *player2* parameter and the game will commence.
  - *Please note that the game will end if there is no interaction with the interface after **2 minutes** to ensure efficiency on the automaton's end.*
  - You will earn 5 `🪙 Shillings` for every round won to spend on various items in the shop.
  - *Choose wisely and have fun, good sir!*
### `/tictactoe`

  ![tictactoe](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/1d0ef6d0-9a0b-4584-950f-02f54b265c90)

  - Challenge the automaton or another member of the guild to a game of tic-tac-toe.
  - You may challenge another member *OR* the automaton to an exciting game of tic-tac-toe using this directive.
  - Simply preface the desired member's username with `@` in the *player2* parameter and the game will commence.
  - *Please note that the game will end if there is no interaction with the interface after **2 minutes** to ensure efficiency on the automaton's end.*
  - You may also choose which symbol you desire to be for the duration of the game (Player 2 will be the opposite symbol for the round -- ❌ or ⭕).
  - It is also important to note that when facing the automaton (`@Lord Bottington` or whatever the byname/nickname is for the guild) you may select a difficulty for the round.
  - Depending upon your difficulty level, you will earn `🪙 Shillings` for your wins to spend on various items in the shop, which are noted below:
    > - `🟩 Easy` (🪙x2)
    > - `🟨 Medium` (🪙x5)
    > - `🟥 Hard` *OR* `another member of your guild` (🪙x10)
  - *Choose wisely and have fun, good sir!*
### `/toptalent`
  - Receive information on the top talent for games played within the guild.
  - When employed, this directive will return information regarding the **Top 10** `🏆 Winners` and `🪙 Earners` within your guild.
  - You may use the select menu under the list to view the top winners and earners for the various games.
  - The top 3 winners and earners are denoted by `🥇 Gold`, `🥈 Silver`, and `🥉 Bronze` medals, respectively. All other top winners and earners are denoted by `🔷`.
  - *Have fun and challenge others in your guild to be the top winner and earner, good sir!*
### `/wumpus`

  ![wumpus](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/f5efd449-e2a5-409a-8bb2-e0f048c211cd)

  - Go on a hunt to find and conquer the dreaded Wumpus👹.
  - Greetings, esteemed ladies and gentlemen! Allow me to present to you the thrilling diversion known as ***Hunt the Wumpus***.
  - In this parlour game of cunning and wit, you shall find yourself embarking upon a perilous quest within the depths of a treacherous cave system.
  - Your noble objective is to track down and vanquish the elusive Wumpus👹, a fearsome creature lurking amidst the labyrinthine tunnels. But take heed, for the caves hold other perils. Bottomless pits⚫ lie concealed, eager to claim any who stumble upon them. And lo, be wary of the mischievous bats🦇 that dwell within these shadows, ever ready to whisk you away to unknown recesses.

  - As you traverse the dimly lit passages, your senses shall guide you. Listen closely, for distant murmurs shall reveal the presence of the Wumpus👹 or the chilling drafts wafting from sinister chasms⚫. Cunning strategy is required to deduce the Wumpus'👹 whereabouts and strike true.

  - With careful steps and a steady hand, navigate through the interconnected rooms. Make your choices wisely, deciding which paths to tread and when to unleash your arrow🏹, seeking to pierce the heart of the mighty Wumpus👹. But remember, a single misstep can be your undoing, consigning you to the inky abyss.
  - Should you succeed in your noble quest, emerging from the cave triumphant and unscathed, the accolades🏆 shall be yours to claim.
  - Depending upon your danger level, you will earn `🪙 Shillings` for your wins to spend on various items in the shop, which are noted below:
    > - `🟩 Safe` (🪙x5)
    > - `🟨 Challenging` (🪙x10)
    > - `🟥 Dangerous` (🪙x25)
    > - `👹 Perilous` (🪙x50)
  - May fortune favor the courageous as they engage in the timeless pursuit of the Wumpus👹!
  - *You may use the various reaction buttons located beneath the game board to partake in this perilous journey.*

<p align="center">
  <a href=#--directive-categories>⬆ Back to Directive Categories</a>
</p>

## Marketplace

This category is for directives related to buying and selling items within the guild.

Members may use their `🪙 Shillings` earned from winning games to purchase and sell items.

They may then trade with others or display their winnings using these directives.

  ![money](https://github.com/xxjsweezeyxx/Lord-Bottington/assets/133728652/4321c109-47f2-4291-9661-a37d9162db47)

### `/displaycase`
  - Display your collected items for all to view.
  - When employed, this directive will display your collected items for your guild.
  - Items are separated by *Common Items*, *Exclusive Items*, and [*`🎩 Patron Items`*](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md).
  - There are a certain amount of items for each category that may be collected and are indicated in the display case when displayed.
  - Within your display case, you will also see your `🎖 Awards` section. Each award has different conditions that must be met and maintained in order to collect.
  - Awards (***5***)
    > - `🎩 Exclusive Gentleman` - Have at least ***1*** of all the items (***5***) in the `🎩 Exclusive Gentleman Collection` in your display case.
    > - `💰 Automaton Patron` - Have at least ***1*** of all the items (***10***) in the `💰 Automaton Patron Collection` in your display case.
    > - `💎 Collector` - Have at least ***1*** of all the common and exclusive items (***25***) in *The Aristocrat's Emporium* in your display case. (does not include the patron items in the Exclusive Shop)
    > - `🎮 Win Achiever` - Achieve ***250*** total wins playing games in your guild.
    > - `🪙 Master Earner` - Collect a total of ***5,000*** `🪙 Shillings` playing games in your guild.
  - These awards are subject to change, depending on their requirements and your current collection within your guild.
  - *Have fun trading and collecting, good sir!*
### `/earnings`
  - Check remaining shillings and other game information for an individual within the guild.
  - When employed, this directive will return information regarding the remaining earnings (`🪙 Shillings`) for a user within the guild.
  - These earnings may be spent in the shop on various items and will increase or decrease depending on the items they are spent on in the shop.
  - It is also important to note that only those with *administrative privileges* within your guild may access other users' remaining earnings information.
  - However, those without these privileges may still view their own remaining earnings within the guild.
### `/exchange`
  - Exchange collectible items with members of your guild.
  - When employed, this directive will allow you to request an item in exchange for an item of your own collection.
  - This will help you grow your collection even further than before!
  - *Only common items are available to trade with others.*
  - Those items that are part of the `🎩 Exclusive Gentleman Collection` and `💰 Automaton Patron Collection` must be bought directly from **The Aristocrat's Emporium** using my `/shop` directive.
  - You must have the item to offer to be able to complete the exchange.
  - *Have fun trading and collecting, good sir!*
### `/shop`
  - Purchase and sell items at the marketplace.
  - *Welcome to **The Aristocrat's Emporium***
  - The official shop for *Lord Bottington.*
  - This storefront sells exclusive, hand-crafted items not found anywhere else in the world. *Feel free to peruse at your leisure and find an item worth your liking, good sir.
  - Certain items offered in ***The Aristocrat's Emporium*** are [*`🎩 Patron Items`*](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md).
  - *Purchasing and Selling*
    > - Members may purchase *OR* sell items for `🪙 Shillings` that are earned by winning games against myself or others within the guild.
    > - When items are sold, the member will be refunded the appropriate amount.
    > - Items purchased from this store can be used to show off to other members and promote properness and showmanship within the guild.
    > - Utilize the `🧾 Sell` and `🪙 Purchase` buttons in the message to perform shop actions and the select menu to change the desired item for the shop.
  - *Items*
    > - The items sold and purchased here range from general proper items to exclusive and expensive items that will make you a more proper gentleman overall.
    > - Once purchased, certain items allow the member to be a part of the `🎩 Exclusive Gentleman Collection`, a highly esteemed and respectable community of individuals within your guild.
    > - Members who have any of these exclusive items shall be distinguished when displaying their items using my `/displaycase` directive to show off their item collection!
  - *May your shopping experience at **The Aristocrat's Emporium** be pleasant and well, good sir.*

<p align="center">
  <a href=#--directive-categories>⬆ Back to Directive Categories</a>
</p>

___
***This is the end of my Full Directives List.***

Thank you for your time and attention.

Sincerely,

***Lord Bottington***
