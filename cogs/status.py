import discord
import os
from discord.ext import commands
import pytz
import datetime
import asyncio
from discord.ext import tasks #used to start various loop tasks
from discord.commands import Option  # add options to slash commands
import pymongo #used to access mongoDB
from discord import Streaming #used for streaming

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


#########################MONGODB DATABASE##################################
# mongoDBpass = os.environ['mongoDBpass'] #load the mongoDB url (retreived from mongoDB upon account creation)
mongoDBpass = os.getenv('mongoDBpass')
client = pymongo.MongoClient(mongoDBpass) # Create a new client and connect to the server
BD_db = client.BD_db #create the birthday database on MongoDB
streaming_db = client.streaming_db #create the streaming database on MongoDB
patrons_db = client.patrons_db #create the patrons database on mongoDB
#########################MONGODB DATABASE##################################

#this is an array of the server IDs where command testing is done
SERVER_ID = [1088118252200276071, 1117859916749742140]


class Status(commands.Cog):
    # this is a special method that is called when the cog is loaded
    def __init__(self, bot):
        self.bot: commands.Bot = bot

        # birthday event (send at Midnight Central Time)
        self.timezone = pytz.timezone('US/Central')
        self.bd_time = datetime.time(hour=0, minute=0, second=0, microsecond=0, tzinfo=self.timezone)
        self.daily_bd_time = self.bd_time.strftime("%I:%M") + " AM" #set the daily bd time to ##:## AM
        self.remove_role_time = datetime.time(hour=23, minute=59, second=0, microsecond=0, tzinfo=self.timezone)
        self.daily_remove_role_time = self.remove_role_time.strftime("%I:%M") + " PM" #set the daily remove role time to ##:## AM
        self.send_bd_message.start()

  
  
    #This retrieves the current server's bot nickname from the mongoDB database
    async def get_byname(self, guild_id):
        # mongoDBpass = os.environ['mongoDBpass']
        mongoDBpass = os.getenv('mongoDBpass')
        client = pymongo.MongoClient(mongoDBpass)
        byname_db = client.byname_db

        byname_key = {"server_id": guild_id}
        byname_data = byname_db.bynames.find_one(byname_key)
        if byname_data:
            return byname_data["byname"]
        else:
            return "Lord Bottington"



######################## SEND BD MESSAGE EVENT #####################
    #This retrieves the current server's birthday event status from the mongoDB database
    async def get_birthday_event_status(self, guild_id):
        # mongoDBpass = os.environ['mongoDBpass']
        mongoDBpass = os.getenv('mongoDBpass')
        client = pymongo.MongoClient(mongoDBpass)
        event_handler_db = client.event_handler_db

        event_doc = event_handler_db.events.find_one({"server_id": guild_id})
        if event_doc:
            return event_doc["birthday_messages"]
        else:
            return "Enabled"
  

  
    @tasks.loop(minutes=1)
    async def send_bd_message(self):
        # Get the time now and localize it to US/Central time
        now = datetime.datetime.now(pytz.timezone('US/Central'))

        now_time = now.strftime("%I:%M %p")
      
        if now_time == self.daily_bd_time:
            # Fetch the birthday message
            await self.get_bd_message()
        elif now_time == self.daily_remove_role_time:
            await self.remove_bd_role()


    async def remove_bd_role(self):
        # print("get bd message event started")
        #get the full list of BD configs
        bd_configs = BD_db.server_birthday_config_data.find()

        for config in bd_configs:
            bd_guild_id = config["server_id"]
            bd_role_id = config["birthday_role_id"]
          
            bd_guild = self.bot.get_guild(bd_guild_id)
              
            if bd_role_id:
                bd_role = bd_guild.get_role(bd_role_id)
    
            #find all of the collections that match today's date
            now = datetime.datetime.now(pytz.timezone('US/Central'))
          
            birthday_list = BD_db[f"birthdays_{bd_guild_id}"].find({"month": now.month, "day": now.day})
    
            for member in birthday_list:
                member_id = member['user_id']
                # print(member_id)
                try:
                    member = bd_guild.get_member(member_id) #retrieve the member object
        
                    # Assign birthday role to user (if set)
                    if bd_role:
                        try:
                            if bd_role in member.roles: # member has the role already or the user is the bot
                                await member.remove_roles(bd_role) #remove bd role
                            else:
                                # print("member does not have role yet")
                                pass
        
                        #unable to assign role
                        except:
                            # print("failed to remove role")
                            pass

                #unable to do something from above
                except:
                    pass
        
  
    
    async def get_bd_message(self):
        # print("get bd message event started")
        #get the full list of BD configs
        bd_configs = BD_db.server_birthday_config_data.find()

        for config in bd_configs:
            bd_guild_id = config["server_id"]
            bd_channel_id = config["birthday_channel_id"] #the channel to send the meme
            bd_role_id = config["birthday_role_id"]
            bd_role_name = config["birthday_role_name"]
            bd_message = config["message"]
          
            bd_guild = self.bot.get_guild(bd_guild_id)
          
            #get the birthday event status from mongoDB
            birthday_messages_status = await self.get_birthday_event_status(bd_guild_id)
          
            #birthday event only runs if event status using /eventhandler is set to enabled OR if the user has not set the status using /eventhandler
            if birthday_messages_status == "Disabled":
                pass
            if birthday_messages_status == "Enabled":

                if bd_channel_id:
                    bd_channel = self.bot.get_channel(bd_channel_id)
                  
                if bd_role_id:
                    bd_role = bd_guild.get_role(bd_role_id)

                #find all of the collections that match today's date
                now = datetime.datetime.now(pytz.timezone('US/Central'))
              
                birthday_list = BD_db[f"birthdays_{bd_guild_id}"].find({"month": now.month, "day": now.day})

                #get the bot's nickname from mongoDB
                byname = await self.get_byname(bd_guild_id)

                for member in birthday_list:
                    member_id = member['user_id']
                    # print(member_id)
                    try:
                        member = bd_guild.get_member(member_id) #retrieve the member object
    
                        # Assign birthday role to user (if set)
                        if bd_role:
                            try:
                                #dont assign role to bot
                                if member.bot:
                                    pass
                                else:
                                    await member.add_roles(bd_role) #assign bd role

                            #unable to assign role
                            except:
                                # print("failed to assign role")
                                pass

                        #send message event
                        try:
                            if bd_message: #pre-defined message
                                support_guild_id = 1088118252200276071
                                if bd_guild_id != support_guild_id:
                                    #check for the automaton patron tier and reset the birthday message to the default if the person does not have the correct tier
                                    patron_data = patrons_db.patrons
                                    refined_patron_key = {
                                      "server_id": bd_guild_id,
                                      "patron_tier": "Refined Automaton Patron"
                                    }
                                    distinguished_patron_key = {
                                      "server_id": bd_guild_id,
                                      "patron_tier": "Distinguished Automaton Patron"
                                    }
                                  
                                    refined_patron = patron_data.find_one(refined_patron_key)
                                    distinguished_patron = patron_data.find_one(distinguished_patron_key)
                                    
                                    if not refined_patron or not distinguished_patron:
                                        birthday_message = "automaton"


                              
                                if bd_message == "automaton":
                                    birthday_message = f"Dearest {member.display_name},\nHappiest of birthdays! May you be blessed with many happy returns of the occasion.\nSincerely,\n***{byname}***".format(member=member)
                        
                                else: #user defined message
                                    if bd_role:
                                        birthday_message = bd_message.replace("{birthday_role_name}", bd_role_name).replace("{birthday_role_mention}", bd_role.mention).replace("{byname}", str(byname)).format(member=member)
                                    
                                    else:
                                        birthday_message = bd_message.replace("{birthday_role_name}", "").replace("{birthday_role_mention}", "").replace("{byname}", str(byname)).format(member=member)


                                #send birthday message (send a different message if it is the bot's birthday)
                                if member.id == self.bot.user.id:
                                    bd_embed = discord.Embed(title="Day of Birth Celebration", description=f"Greetings good fellows of ***{bd_guild.name}***,\nIt appears that it is the day of my birth.\nLet us all celebrate and enjoy in the merriment!", color=discord.Color.from_rgb(130, 130, 130))

                                    bd_embed.set_thumbnail(url="https://i.imgur.com/tYenTsy.gif")
                                  
                                    await bd_channel.send(embed=bd_embed)
                                else:
                                    bd_embed = discord.Embed(title="Day of Birth Celebration", description=birthday_message, color=discord.Color.from_rgb(130, 130, 130))

                                    bd_embed.set_thumbnail(url="https://i.imgur.com/tYenTsy.gif")
                                  
                                    await bd_channel.send(f"{member.mention} ***Happiest of Birthdays!***", embed=bd_embed)
                          
                            else: #birthday message not set
                                # print("bd_message not set")
                                birthday_message = None
                          
                        except discord.Forbidden:
                            # print("couldnt send message")
                            pass

                    except:
                        # raise e
                        # print(f"member not found\n\n{e}")
                        #member not found
                        pass
                    

######################## SEND BD MESSAGE EVENT ##################### 


  

  
  
#############################STREAMING##################################
    #This retrieves the current server's event status from the mongoDB database
    async def get_livestreams_event_status(self, guild_id):
        # mongoDBpass = os.environ['mongoDBpass']
        mongoDBpass = os.getenv('mongoDBpass')
        client = pymongo.MongoClient(mongoDBpass)
        event_handler_db = client.event_handler_db
    
        event_doc = event_handler_db.events.find_one({"server_id": guild_id})
        if event_doc:
            return event_doc["livestreams"]
        else:
            return "Enabled"


  
    #on_presence_update listener that sends notifications
    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        #ignore status updates from bots
        if after.bot or before.bot:
            return

        # Member activity status hasn't changed, return
        if before.activity == after.activity:
            return

        # print(f"Before activity: {before.activity}")
        # print(f"After activity: {after.activity}")
        # print(f"before activity streaming? {isinstance(before.activity, Streaming)}")
        # print(f"after activity streaming? {isinstance(after.activity, Streaming)}")

      
        #check if the activity after changing status is streaming
        if isinstance(after.activity, Streaming):
            # print("stream event started")
            member_server_id = after.guild.id #get the server_id of the person who is streaming
            # print(f"server id: {member_server_id}")

            #get the livestreams event status from mongoDB
            livestreams_status = await self.get_livestreams_event_status(member_server_id)            
            #livestream AFTER event only runs if event status using /eventhandler is set to enabled OR if the user has not set the status using /eventhandler
            if livestreams_status == "Disabled":
                return
            elif livestreams_status == "Enabled":
                stream_key = {"server_id": member_server_id}
                streamer_data = streaming_db.stream_configs.find_one(stream_key)
    
                #retrieve the data from mongoDB, if set
                if streamer_data:
                    streamers = streamer_data["streamers"]
                    streamer_name = streamer_data["streamer_name"]
                    streamer_username = streamer_data["streamer_username"]
                    streamer_id = streamer_data["streamer_id"]
                    stream_status_id = streamer_data["stream_status_id"]
                    stream_status_name = streamer_data["stream_status_name"]
                    stream_channel_id = streamer_data["stream_channel_id"]
                    stream_channel_name = streamer_data["stream_channel_name"]
                    message = streamer_data["message"]
                    streaming_service = streamer_data["streaming_service"]
                    stream_title = streamer_data["stream_title"]
                    body = streamer_data["body"]
                    stream_preview = streamer_data["stream_preview"]
                    streamer_photo = streamer_data["streamer_photo"]
                    color = streamer_data["color"]
                    whitelisted_status_id = streamer_data["whitelisted_status_id"]
                    whitelisted_status_name = streamer_data["whitelisted_status_name"]
                    blacklisted_status_id = streamer_data["blacklisted_status_id"]
                    blacklisted_status_name = streamer_data["blacklisted_status_name"]
                else: #if no streaming config, do nothing
                    return

                #check for the automaton patron tier and reset the configurations to the defaults
                patron_data = patrons_db.patrons
                refined_patron_key = {
                  "server_id": member_server_id,
                  "patron_tier": "Refined Automaton Patron"
                }
                distinguished_patron_key = {
                  "server_id": member_server_id,
                  "patron_tier": "Distinguished Automaton Patron"
                }
              
                refined_patron = patron_data.find_one(refined_patron_key)
                distinguished_patron = patron_data.find_one(distinguished_patron_key)
                
                if not refined_patron or not distinguished_patron:
                    color = [None, None, None] #reset color to None to match streaming service
              
        
        
                # print(f"streaming channel id: {stream_channel_id}")
                # print(f"streamer id: {streamer_id}")
    
                ####### Begin checking mongoDB data and giving and sending status and notifications if the user is streaming
                  
                #this checks if anything has been set for both the notifications and the role (if neither are set then do nothing)
                if stream_channel_id is None and stream_status_id is None:
                    # print("no channel or role set, exiting...")
                    return
    
                #Only run if a streaming id is set on mongoDB
                if stream_status_id:
                    #get all the roles of the streamer
                    statuses = [status.id for status in after.roles]
    
                    #define the streaming role
                    stream_role = after.guild.get_role(stream_status_id)
                    # print(f"stream role: {stream_role}")
          
                    # Check if the member has the blacklisted status (don't give the streaming status if so)
                    if blacklisted_status_id in statuses:
                        pass
                    
                    # Check if the member has the whitelisted status and give the streaming role if so
                    elif whitelisted_status_id in statuses:                 
                        #check to see if the activity member is the one specified and give the role if it is (this is only if the config is set to ONE USER)
                        if streamers == "one":
                            streamer = after.guild.get_member(streamer_id) #get the member object of the defined user
                            # print(f"streamer: {streamer}")
                            await streamer.add_roles(stream_role)
                            # print(f"status added: {stream_role}\nadded status id: {stream_role.id}")
                        else: #add the role to everybody if streamers is set to "all"
                            # print(f"after: {after}")
                            await after.add_roles(stream_role)
                    
                    # If neither blacklisted nor whitelisted status, and whitelist and blacklist are empty, give the streaming role
                    elif not blacklisted_status_id and not whitelisted_status_id:                 
                        #check to see if the activity member is the one specified and give the role if it is (this is only if the config is set to ONE USER)
                        if streamers == "one":
                            streamer = after.guild.get_member(streamer_id) #get the member object of the defined user
                            # print(f"streamer: {streamer}")
                            await streamer.add_roles(stream_role)
                            # print(f"status added: {stream_role}\nadded status id: {stream_role.id}")
                        else: #add the role to everybody if streamers is set to "all"
                            # print(f"after: {after}")
                            await after.add_roles(stream_role)
                            # print(f"all status added: {stream_role}\nall added status id: {stream_role.id}")
    
              
                #initialize the linked account status
                platform_status = False
    
                #loop through the streamer's activities
                for activity in after.activities:
                    if activity.type == discord.ActivityType.streaming: #only set the linked account status to true if the user is streaming
                        if "twitch.tv" in activity.url:
                            platform_status = True
                            # The person is streaming on Twitch and has their Twitch account linked
                            break
                        elif "youtube.com" in activity.url:
                            platform_status = True
                            # The person is streaming on YouTube and has their YouTube account linked
                            break
                        elif "facebook.com" in activity.url:
                            platform_status = True
                            # The person is streaming on Facebook and has their Facebook account linked
                            break
                        elif "kick.com" in activity.url:
                            platform_status = True
                            # The person is streaming on Kick and has their Kick account linked
                            break
                          
    
                # print(f"account linked? {platform_status}")
    
                #define the streaming platform
                platform = after.activity.platform
    
    
                #get the rgb color data from mongoDB
                color_data = streamer_data.get("color", None)
                # print(f"color: {color_data}")
                if color_data:
                    r, g, b = color_data
    
                    if (r and g and b): #if the color is not "Match Streaming Service" (i.e. defined)
                        color = discord.Color.from_rgb(r, g, b)
                    else:
                        if platform.lower() == "twitch": #set the embed color to match twitch (purple)
                            r = 152
                            g = 3
                            b = 252
                            color = discord.Color.from_rgb(r, g, b)
                        elif platform.lower() == "youtube": #set the embed color to match youtube (red)
                            r = 255
                            g = 0
                            b = 0
                            color = discord.Color.from_rgb(r, g, b)
                        elif platform.lower() == "kick": #set the embed color to match kick (lime green)
                            r = 5
                            g = 252
                            b = 59
                            color = discord.Color.from_rgb(r, g, b)
                        elif platform.lower() == "facebook": #set the embed color to match facebook (blue)
                            r = 0
                            g = 0
                            b = 255
                            color = discord.Color.from_rgb(r, g, b)
                        else:
                            color = discord.Color.default()
                else:
                    color = discord.Color.default()
    
    
                #display the stream title as the embed title
                if stream_title and platform_status is True:
                    if streamers == "one":
                        streamer = after.guild.get_member(streamer_id) #get the member object of the defined user
                        stream_url = streamer.activity.url
                        stream_video_title = streamer.activity.name
                    else:
                        stream_url = after.activity.url
                        stream_video_title = after.activity.name
                                        

                if body:
                    if streamers == "one":
                        body = body.format(member=streamer)
                    else:
                        body = body.format(member=after)
                else:
                    body = None
              
              
                #only send the stream embed and message if a channel is defined
                if stream_channel_id:
                    #define the embed
                    stream_embed = discord.Embed(
                      title = stream_video_title,
                      url = stream_url,
                      description = body if body else "",
                      color = color
                    )
    
    
                    if streamer_photo is True:
                        if streamers == "one": #if streamers is "one" then define the avatar url as it's discord profile pic
                            streamer = after.guild.get_member(streamer_id) #get the member object of the defined user
                            streamer_avatar_url = streamer.avatar
                        else:
                            streamer_avatar_url = after.avatar 
                        
                        stream_embed.set_thumbnail(url = streamer_avatar_url) #set the embed thumbnail to the appropriate avatar             
    
        
                    #add a field that displays the streamer's username
                    #use the defined streamer's username if streamers is "one" otherwise use the streamer's username
                    if streamer_name is True:
                        stream_embed.add_field(
                            name = "Streamer",
                            value = streamer_username if streamers == "one" else after.display_name,
                            inline = True
                        )
    
    
                    #set a field that displays the streaming service (if associated account is linked)
                    if streaming_service is True and platform_status is True:
                        if streamers == "one":
                            streamer = after.guild.get_member(streamer_id) #get the member object of the defined user
                            streaming_service = streamer.activity.platform
                            streaming_service = streaming_service.capitalize()
                        else:
                            streaming_service = after.activity.platform
                            streaming_service = streaming_service.capitalize()
                      
                        stream_embed.add_field(
                            name = "Streaming On",
                            value = streaming_service,
                            inline = True
                        )


                    if message:
                        if streamers == "one":
                            message = message.format(member=streamer)
                        else:
                            message = message.format(member=after)
                    else:
                        message = None

                    
        
                    # do not send the embed if it's empty (only send the message if defined)
                    if not (stream_embed.title or stream_embed.fields or stream_embed.description or stream_embed.thumbnail):
                        if message is not None:               
                            if stream_preview is True and platform_status is True:
                                # send the message
                                channel = self.bot.get_channel(stream_channel_id)
                                await channel.send(message)
                                await channel.send(after.activity.url)
                            elif platform_status is True:
                                # send the message
                                channel = self.bot.get_channel(stream_channel_id)
                                await channel.send(message)
                            else:
                                # send the message
                                channel = self.bot.get_channel(stream_channel_id)
                                await channel.send(message)
                        else:
                            if stream_preview is True and platform_status is True:
                                channel = self.bot.get_channel(stream_channel_id)
                                await channel.send(after.activity.url)
                            elif platform_status is True:
                                pass
                            else:
                                pass                          
                    else:  # otherwise, send the embed
                        if message:
                            if stream_preview is True and platform_status is True:
                                channel = self.bot.get_channel(stream_channel_id)
                                await channel.send(content=message, embed=stream_embed)
                                await channel.send(after.activity.url)
                            elif platform_status is True:
                                channel = self.bot.get_channel(stream_channel_id)
                                await channel.send(content=message, embed=stream_embed)
                            else:
                                channel = self.bot.get_channel(stream_channel_id)
                                await channel.send(content=message, embed=stream_embed)
                        else:
                            if stream_preview is True and platform_status is True:
                                channel = self.bot.get_channel(stream_channel_id)
                                await channel.send(embed=stream_embed)
                                await channel.send(after.activity.url)
                            elif platform_status:
                                await channel.send(embed=stream_embed)
                            else:
                                await channel.send(embed=stream_embed)
    
                    # print("notification successfully sent\n---------------------------")

        #remove the role if the status changes from streaming to not streaming
        elif isinstance(before.activity, Streaming):
            # print("remove status started")

            member_server_id = before.guild.id #get the server_id of the person who has stopped streaming
            # print(f"server id: {member_server_id}")

            #get the livestreams event status from mongoDB
            livestreams_status = await self.get_livestreams_event_status(member_server_id)

            #livestream BEFORE event only runs if event status using /eventhandler is set to enabled OR if the user has not set the status using /eventhandler
            if livestreams_status == "Disabled":
                return
            elif livestreams_status == "Enabled":
                stream_key = {"server_id": member_server_id}
                streamer_data = streaming_db.stream_configs.find_one(stream_key)
    
                #retrieve the data from mongoDB, if set
                if streamer_data:
                    streamers = streamer_data["streamers"]
                    streamer_id = streamer_data["streamer_id"]
                    stream_status_id = streamer_data["stream_status_id"]
                else: #if no streaming config, do nothing
                    return
              
                #define the streaming role
                stream_role = before.guild.get_role(stream_status_id)
                # print(f"stream role: {stream_role}")
                
                #check to see if the activity member is the one specified and remove the role if it is (this is only if the config is set to ONE USER)
                if streamers == "one":
                    streamer = before.guild.get_member(streamer_id) #get the member object of the defined user
                    # print(f"streamer: {streamer}")
                    await streamer.remove_roles(stream_role)
                    # print(f"status removed: {stream_role}\nremoved status id: {stream_role.id}")
                else: #remove the role from everybody if streamers is set to "all"
                    # print(f"before: {before}")
                    await before.remove_roles(stream_role)
                    # print(f"all status removed: {stream_role}\nall removed status id: {stream_role.id}")


#############################STREAMING##################################

    


  

#################################SETBIRTHDAY#################################
    #Set Birthday command
    @discord.slash_command(
        name="setbirthday",
        description="Manually input thy date of birth for the automaton to commit to memory.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def setbirthday(self, ctx, month: Option(int, name="month", description="Enter your birth month.", min_value=1, max_value=12), day: Option(int, name="day", description="Enter your birth day.", min_value=1, max_value=31)):
        # if month < 1 or month > 12 or day < 1 or day > 31:
        #     await ctx.respond("I am afraid, good fellow, that the day or month you have provided is not valid.\n*Please try again.*", ephemeral=True)
        #     return
    
        user_id = ctx.author.id
        server_id = ctx.guild.id


        # if no birthdays have been set for the guild
        if BD_db[f"birthdays_{server_id}"].count_documents({}) == 0:
            await ctx.respond(f"It appears that there are no birthdays set for ***{ctx.guild.name}***.\nNow setting this up for you...", ephemeral=True)
            await asyncio.sleep(5)

            #get the bot's nickname from mongoDB
            byname = await self.get_byname(server_id)
        
            #Lord Bottington BD (April 3, 2023)
            BD_db[f"birthdays_{server_id}"].insert_one(
              {
                "user_id": self.bot.user.id,
                "user_name": byname,
                "month": 4,
                "day": 3
              }
            )
          
            #user BD
            BD_db[f"birthdays_{server_id}"].insert_one(
              {
                "user_id": user_id,
                "user_name": ctx.author.display_name,
                "month": month,
                "day": day
              }
            )
    
            await ctx.respond(f"{ctx.author.mention},\nI have successfully set your date of birth to ***{month}/{day}***.", ephemeral=True)

        # if birthdays have been set for the guild
        else:
            key = {'user_id': user_id}
            birthday_data = BD_db[f"birthdays_{server_id}"].find_one(key)
      
            #if a user ID is found in the database, update their BD and nickname of the bot
            if birthday_data:
                await ctx.respond(f"Alas, thou hast already set a date of birth for {ctx.guild.name}.\nNow updating thy date of birth, good sir...", ephemeral=True)
                await asyncio.sleep(5)
                    
                #get the bot's nickname from mongoDB
                byname = await self.get_byname(server_id)
            
                #Lord Bottington BD (April 3, 2023)
                BD_db[f"birthdays_{server_id}"].update_one(
                  {"user_id": self.bot.user.id},
                  {"$set": {
                    "user_name": byname,
                    "month": 4,
                    "day": 3
                    }
                  }
                )
    
                #user BD
                BD_db[f"birthdays_{server_id}"].update_one(
                    {"user_id": user_id},
                    {"$set":{
                      "month": month,
                      "day": day
                      }
                    }
                )
                
                await ctx.respond(f"{ctx.author.mention},\nI have successfully updated your date of birth to ***{month}/{day}***.", ephemeral=True)
                return

            #user has not set date of birth
            else:
                #get the bot's nickname from mongoDB
                byname = await self.get_byname(server_id)
            
                #Lord Bottington BD (April 3, 2023)
                BD_db[f"birthdays_{server_id}"].update_one(
                  {"user_id": self.bot.user.id},
                  {"$set": {
                    "user_name": byname,
                    "month": 4,
                    "day": 3
                    }
                  }
                )
              
                #user BD
                BD_db[f"birthdays_{server_id}"].insert_one(
                  {
                    "user_id": user_id,
                    "user_name": ctx.author.display_name,
                    "month": month,
                    "day": day
                  }
                )
        
                await ctx.respond(f"{ctx.author.mention},\nI have successfully set your date of birth to ***{month}/{day}***.", ephemeral=True)

#################################SETBIRTHDAY#################################


  

  
  
############################## GETBIRTHDAY ################################
    @discord.slash_command(
        name="getbirthday",
        description="Allow the automaton to provide you with a user's date of birth.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def getbirthday(self, ctx, user: Option(discord.Member, name="user", description="Select a user to see the date of birth for. (Default: Self)", required=False, default=None)):
        # Check if the user is an admin
        if not ctx.author.guild_permissions.administrator:
            # Only allow access to own birthday
            if user is not None and user.id != ctx.author.id:
                await ctx.respond("Sorry, you are not allowed to access other users' birthdays. That is a privilege given only to an **administrator**.", ephemeral=True)
                return
        
        if user is None:
            user_id = ctx.author.id
        else:
            user_id = user.id
    
        key = {'user_id': user_id}
    
        if not BD_db[f"birthdays_{ctx.guild.id}"].find_one(key):
            await ctx.respond(f"Apologies, *{user.display_name}* has not set their date of birth...", ephemeral=True)
            return
    
        for users in BD_db[f"birthdays_{ctx.guild.id}"].find(key):
            month = users['month']
            day = users['day']
    
        if user is None:
            await ctx.respond(f"Dearest {ctx.author.mention},\nThy date of birth is **{month}/{day}**.", ephemeral=True)
        else:
            await ctx.respond(f"Good sir, *{user.display_name}* has a birth date of **{month}/{day}**.", ephemeral=True)

############################## GETBIRTHDAY ################################




########################BIRTHDAYLIST#####################################
    @discord.slash_command(
        name="birthdaylist",
        description="Allow the automaton to provide you a list of all dates of birth for your guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def birthdaylist(self, ctx, liststyle: Option(str, name="liststyle", description="Birthday list style. (Default: 📝 Embed)", choices=["📝 Embed", "💬 Regular"], required=False, default=None)):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may access a full list of other users' dates of birth.", ephemeral=True)
            return

      
        if not BD_db[f"birthdays_{ctx.guild.id}"].find():
            await ctx.respond(f"I am afraid that no birthdays have been set as of yet for {ctx.guild.name}.", ephemeral=True)
            return


        list_style_dict = {
          "📝 Embed": "embed",
          "💬 Regular": "regular"
        }

        if liststyle:  
            if liststyle in list_style_dict:
                liststyle = list_style_dict[liststyle]
            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\n*{liststyle}* is not a valid list style.\n*Please try again.*", ephemeral=True)
                return
        else: #set default to embed style
            liststyle = "embed"

        #embed message
        if liststyle == "embed":
            # create the birthday embed object
            BD_embed = discord.Embed(title=f"{ctx.guild.name}\n__Birthday List__", color=discord.Color.from_rgb(130, 130, 130))
        
            for member in BD_db[f"birthdays_{ctx.guild.id}"].find():
                member_name = member['user_name']
                # add a field for each member's birthday
                BD_embed.add_field(name=member_name, value=f"*{member['month']}/{member['day']}*", inline=True)
    
          
            #set thumbnail to birthday cake gif
            BD_embed.set_thumbnail(url="https://i.imgur.com/tYenTsy.gif")
              
            await ctx.respond(embed=BD_embed, ephemeral=True)

        #regular message
        elif liststyle == "regular":
            response = f"{ctx.guild.name}\n__Birthday List__\n\n"

            for member in BD_db[f"birthdays_{ctx.guild.id}"].find():
                member_name = member['user_name']
                response += f"{member_name} - *{member['month']}/{member['day']}*\n"

            # file is a birthday cake gif
            await ctx.respond(f"{response}\n[Happy Birthday All](https://i.imgur.com/tYenTsy.gif)", ephemeral=True)
          
########################BIRTHDAYLIST#####################################
    



########################## REMOVEBIRTHDAY #########################
    #Remove Birthday Command
    @discord.slash_command(
        name="removebirthday",
        description="Allow the automaton to remove a date of birth from the register.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def removebirthday(self, ctx, user: Option(discord.Member, name="user", description="Member to remove from the birthday registry. (Default: self)", required=False, default=None)):

        # Check if the user is an admin
        if not ctx.author.guild_permissions.administrator:
            # Only allow removal of own birthday
            if user is not None and user.id != ctx.author.id:
                await ctx.respond("Sorry, you are not allowed to remove other users' birthdays. That is a privilege given only to an **administrator**.", ephemeral=True)
                return


        if user is None:
            user_id = ctx.author.id
        else:
            user_id = user.id
    
        # Check if the user has set their birthday
        user_key = {'user_id': user_id}
        birthday_data = BD_db[f"birthdays_{ctx.guild.id}"].find_one(user_key)
        if not birthday_data:
            await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that {'you have' if user_id == ctx.author.id else f'**{user.display_name}** has'} yet to set a date of birth, good sir.", ephemeral=True)
            return

        #delete the birthday from mongoDB
        BD_db[f"birthdays_{ctx.guild.id}"].delete_one(user_key)

        await ctx.respond(f"{ctx.author.mention}\n{'Your date of birth' if user_id == ctx.author.id else f'The date of birth for **{user.display_name}**'} has been expunged from the records.", ephemeral=True)

########################## REMOVEBIRTHDAY #########################

def setup(bot):
  bot.add_cog(Status(bot))
