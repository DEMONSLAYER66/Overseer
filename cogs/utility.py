import discord #needed to interact with discord API
from discord.ext import commands #used for slash commands
from discord.commands import Option #add options to slash commands
from discord.ext import tasks #used to start various loop tasks

import os #used to import secret keys and such

import io #for picture creation
import requests #used to get data from images or websites
from PIL import Image, ImageDraw, ImageFont #used for Welcomer to draw images

import pymongo #used for database management

import re #string matching
  
import json #used to read and write .json type files
import pytz #used for timezone
import datetime
# from datetime import datetime #used to get date formatting and such
from datetime import timedelta #used for time addition and subtraction
import asyncio #used to wait for specified amounts of time
import random #used to randomize selections or choices

#for examining URLs for websites
import urllib
import urllib.parse

import asyncpraw #used for reddit memes
import asyncprawcore.exceptions
from dotenv import load_dotenv

from discord.ui import Button, View #used to manually create LINK type buttons on views when sending embeds or messages

# Load environment variables from .env
load_dotenv()


#########################MONGODB DATABASE##################################
# mongoDBpass = os.environ['mongoDBpass'] #load the mongoDB url (retreived from mongoDB upon account creation)
mongoDBpass = os.getenv('mongoDBpass')
client = pymongo.MongoClient(mongoDBpass) # Create a new client and connect to the server
embeds_db = client.embeds_db #create the birthday database on MongoDB
welcome_db = client.welcome_db #create the welcomer database on MongoDB
starboard_db = client.starboard_db #create the starboard database on MongoDB
autopurge_db = client.autopurge_db #create the autopurge database on MongoDB
patrons_db = client.patrons_db #create the patrons database on mongoDB
autosatire_db = client.autosatire_db #create the autosatire (automeme) database on MongoDB
bump_db = client.bump_db #create the bump (promotion) database on MongoDB
#########################MONGODB DATABASE##################################


#this is an array of the server IDs where command testing is done
SERVER_ID = [1088118252200276071, 1117859916749742140]



class Utility(commands.Cog):
    # this is a special method that is called when the cog is loaded
    def __init__(self, bot):
      self.bot: commands.Bot = bot
      self.send_timed_embeds.start()
      # self.subscription_notifier.start()
      with open("json_files/command_help.json", "r") as f:
        self.command_help = json.load(f)

      # autosatire event
      self.timezone = pytz.timezone('US/Central')
      self.meme_time = datetime.time(hour=9, minute=0, second=0, microsecond=0, tzinfo=self.timezone)
      self.daily_meme_time = self.meme_time.strftime("%I:%M") + " AM" #set the daily meme time to ##:## AM
      self.send_meme.start()
  

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



############################ PROMOTE #########################
    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, commands.CommandOnCooldown):
            promote_app_command = self.bot.get_application_command("promote")
            
            # Calculate the total cooldown time in days, hours, minutes, and seconds
            days, remainder = divmod(int(error.retry_after), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            # Format the frequency string
            if days > 0:
                cooldown_time = f"{days:02d}d:{hours:02d}h:{minutes:02d}m:{seconds:02d}s"
            elif hours > 0:
                cooldown_time = f"{hours:02d}h:{minutes:02d}m:{seconds:02d}s"
            elif minutes > 0:
                cooldown_time = f"{minutes:02d}m:{seconds:02d}s"
            else:
                cooldown_time = f"{seconds}s"

            cooldown_embed = discord.Embed(title=f"{ctx.guild.name}\nPromotion Cooldown", description=f"> Apologies good sir, it appears that my </{promote_app_command.name}:{promote_app_command.id}> directive is not ready to use at the moment...\n> Please try again in `{cooldown_time}`.\n> \n> *I apologize for the inconvenience, good sir.*", color=discord.Color.from_rgb(130, 130, 130))

            cooldown_embed.set_thumbnail(url=self.bot.user.avatar.url)

            await ctx.respond(f"{ctx.author.mention}", embed=cooldown_embed, ephemeral=True)


  
    @discord.slash_command(
        name="promote",
        description="Promote this guild.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.cooldown(1, 7200, commands.BucketType.guild)
    async def promote(self, ctx):
        # check if a cooldown is active for the guild
        cooldown_data = bump_db.cooldowns.find_one({"server_id": ctx.guild.id})

        if cooldown_data:
            current_time = datetime.datetime.utcnow()
            start_time = cooldown_data['start_time']
            elapsed_time = current_time - start_time
            cooldown_time = int(cooldown_data['cooldown'])
            remaining_time = max(0, cooldown_time - int(elapsed_time.total_seconds()))

            promote_app_command = self.bot.get_application_command("promote")
            
            # Calculate the total cooldown time in days, hours, minutes, and seconds
            days, remainder = divmod(int(remaining_time), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            # Format the frequency string
            if days > 0:
                cooldown_time = f"{days:02d}d:{hours:02d}h:{minutes:02d}m:{seconds:02d}s"
            elif hours > 0:
                cooldown_time = f"{hours:02d}h:{minutes:02d}m:{seconds:02d}s"
            elif minutes > 0:
                cooldown_time = f"{minutes:02d}m:{seconds:02d}s"
            else:
                cooldown_time = f"{seconds}s"

            cooldown_embed = discord.Embed(title=f"{ctx.guild.name}\nPromotion Cooldown", description=f"> Apologies good sir, it appears that my </{promote_app_command.name}:{promote_app_command.id}> directive is not ready to use at the moment...\n> Please try again in `{cooldown_time}`.\n> \n> *I apologize for the inconvenience, good sir.*", color=discord.Color.from_rgb(130, 130, 130))

            cooldown_embed.set_thumbnail(url=self.bot.user.avatar.url)

            await ctx.respond(f"{ctx.author.mention}", embed=cooldown_embed, ephemeral=True)
            return


        #begin promote command
        await ctx.defer() #acknowledge the interaction

        #get the promotion application command
        promotion_app_command = self.bot.get_application_command("promotion")

        bump_key = {"server_id": ctx.guild.id}
        server_data = bump_db.bump_configs.find_one(bump_key)

        if not server_data:
            no_data_description = f"Apologies {ctx.author.mention},\nIt appears that a guild promotion configuration has not been set up for ***{ctx.guild.name}***, good sir.\n\nYou may utilize my </{promotion_app_command.name}:{promotion_app_command.id}> directive to configure this for your guild, if you desire."
            no_data_embed = discord.Embed(title=f"{ctx.guild.name}\nPromotion Error", description = no_data_description, color=discord.Color.from_rgb(130, 130, 130))

            no_data_embed.set_thumbnail(url=self.bot.user.avatar.url)

            await ctx.respond(embed=no_data_embed, ephemeral=True)
            return

        else:
            initial_embed = discord.Embed(title=f"{ctx.guild.name}\nPromotion", description = "Your guild has been added to the promotion roster and will be promoted momentarily, good sir.\nPlease be patient while I process this request for you...", color=discord.Color.from_rgb(130, 130, 130))

            initial_embed.set_thumbnail(url=self.bot.user.avatar.url)

            initial_message = await ctx.respond(embed=initial_embed, ephemeral=True) #send an initial embed to interact with the response
          
            #update the mongoDB database and retrieve info
            bump_key = {"server_id": ctx.guild.id}
          
            #increase the number of bumps for the server by 1 on mongodb
            bump_db.bump_configs.update_one(
              bump_key,
              {"$inc": {
                "bumps": 1
                }
              }
            )

            #increase the total number of bumps for the bot by 1
            if not bump_db.total_bumps.find_one({"automaton": "Lord Bottington"}):
                bump_db.total_bumps.insert_one(
                  {
                    "automaton": "Lord Bottington",
                    "total_bumps": 1
                  }
                )
            else:
                bump_db.total_bumps.update_one(
                  {"automaton": "Lord Bottington"},
                  {"$inc": {
                    "total_bumps": 1
                    }
                  }
                )

            bump_key = {"server_id": ctx.guild.id}
            server_data = bump_db.bump_configs.find_one(bump_key)
          
            automaton_invite_link = "https://discord.com/api/oauth2/authorize?client_id=1092515783025889383&permissions=3557027031&scope=bot%20applications.commands"
            support_guild_invite = "https://discord.gg/4P6ApdPAF7"
            invite_link = server_data['invite_link']
            guild_description = server_data['guild_description']
            original_promotion_channel = await self.bot.fetch_channel(server_data['promotion_channel_id'])
            color = server_data['color'] #array of (r, g, b)
            banner_url = server_data['banner_url']
            bumps = server_data['bumps']
            guild_created_at = ctx.guild.created_at.strftime('%B %d, %Y')
            topic = server_data['topic']
          

            #PATRON FEATURE
            # server ID for The Sweez Gang
            support_guild_id = 1088118252200276071
    
            if ctx.guild.id != support_guild_id:
                #search for a guild on mongoDB that has the Distinguished Automaton Patron tier
                distinguished_patron_key = {
                  "server_id": ctx.guild.id,
                  "patron_tier": "Distinguished Automaton Patron"
                }
                refined_patron_key = {
                  "server_id": ctx.guild.id,
                  "patron_tier": "Refined Automaton Patron"
                }
                patron_data = patrons_db.patrons
                refined_patron = patron_data.find_one(refined_patron_key)
                distinguished_patron = patron_data.find_one(distinguished_patron_key)
      
                if not refined_patron and not distinguished_patron:
                    banner_url = None # no banner
                    color = [0, 0, 255] # default color
                    cooldown_time = 7200 # 2 hours
                    cooldown_time_str = "2 hours"
                    patron = False

                else:
                    cooldown_time = 1800 # 30 min
                    cooldown_time_str = "30 minutes"
                    patron = True

            #cooldown for support guild
            else:
                cooldown_time = 1800 # 30 min
                cooldown_time_str = "30 minutes"
                patron = None


            test_embed =  discord.Embed(title=f"{ctx.guild.name}", description = guild_description, color=discord.Color.from_rgb(color[0], color[1], color[2]))

            test_embed.add_field(name="❗Guild Topic", value=f"`{topic}`", inline=True)
            test_embed.add_field(name="🕒Guild Creation", value=f"`{guild_created_at}`", inline=True)
            test_embed.add_field(name="👑 Owner", value=f"`{str(ctx.guild.owner.display_name)}`")
            test_embed.add_field(name="🚀Promotions", value=f"`{bumps:,}`", inline=True)
            test_embed.add_field(name="👨Member Count", value=f"`{ctx.guild.member_count:,}`", inline=True)
            test_embed.add_field(name="💎Boost Tier", value=f"`{ctx.guild.premium_subscription_count:,}`", inline=True)
            test_embed.add_field(name="🤣Iconography", value=f"`{len(ctx.guild.emojis):,}/{ctx.guild.emoji_limit:,}`", inline=True)

            if patron and patron is True:
                test_embed.add_field(name="🎩Patron Guild", value="", inline=True)

            try:
                test_embed.set_thumbnail(url=ctx.guild.icon.url)
            except:
                pass

            if banner_url:
                test_embed.set_image(url=banner_url)

            try:
                test_embed.set_footer(text=f"Promoter: {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
            except:
                test_embed.set_footer(text=f"Promoter: {ctx.author.display_name}") #no avatar set

            InviteButton = discord.ui.Button(emoji='✅', label="Join Guild", url=invite_link, style=discord.ButtonStyle.link)
            InviteLordBottington = discord.ui.Button(emoji='🤖', label="Add Lord Bottington", url=automaton_invite_link, style=discord.ButtonStyle.link)
            JoinSupportGuild = discord.ui.Button(emoji='🎩', label="Join 𝓣𝓱𝓮 𝓢𝔀𝓮𝓮𝔃 𝓖𝓪𝓷𝓰", url=support_guild_invite, style=discord.ButtonStyle.link)

            view=View()
            view.add_item(InviteButton)
            view.add_item(InviteLordBottington)
            view.add_item(JoinSupportGuild)

            # Fetch all promotion channel IDs from the MongoDB collection
            promotion_channel_ids = bump_db.bump_configs.distinct("promotion_channel_id")
            
            # Iterate through each promotion channel ID
            message_sent_to = 0
            for promotion_channel_id in promotion_channel_ids:
                # Fetch the promotion channel from the ID
                promotion_channel = await self.bot.fetch_channel(promotion_channel_id)


                if original_promotion_channel.id == promotion_channel.id:
                    try:
                        promotion_message = await promotion_channel.send(invite_link, embed=test_embed, view=view)
                    except (discord.errors.HTTPException, discord.errors.Forbidden) as e:
                        await ctx.respond(f"Apologies {ctx.author.mention},\nI was unable to send the promotion message to your specified promotion channel with ID ***{promotion_channel_id}*** as I may not have the required permissions to do so...\n*For future reference, please ensure my permissions for this channel are set to `Send Messages` and `Manage Messages` permissions to be able to send the promotion there, sir.*\n\nError: `{e}`", ephemeral=True)
                        continue

              
               # Check if the promotion channel exists and is a TextChannel
                elif promotion_channel and isinstance(promotion_channel, discord.TextChannel):
                    try:
                        # Send the embed to the promotion channel
                        await promotion_channel.send(invite_link, embed=test_embed, view=view)
                        message_sent_to += 1 #add one to the sent invites list
                    except (discord.errors.HTTPException, discord.errors.Forbidden) as e:
                        # await ctx.respond(f"Apologies {ctx.author.mention},\nI was unable to send the promotion message to the specified channel with ID ***{promotion_channel.id}*** as I may not have the required permissions to do so.\n*Please check my permissions for this channel and ensure I have the `Send Messages` and `Manage Messages` permissions and try again.*\n\nError: `{e}`", ephemeral=True)
                        continue


            bot_data = bump_db.total_bumps.find_one({"automaton": "Lord Bottington"}) #the total number of bumps for the bot
            total_bumps = bot_data['total_bumps']

            # guild_count = bump_db.bump_configs.count_documents({}) #the amount of servers that have configured their promo channel

            # other_guilds = guild_count - 1 #do not count current guild
          
            info_embed = discord.Embed(title=f"{ctx.guild.name}\nSuccessful Promotion", description=f"**🎩Congratulations!🎩**\nThis guild has been **successfully promoted** to `{message_sent_to:,}` other guilds.\n\nYou may view the posting for your guild in {original_promotion_channel.mention} by [clicking here]({promotion_message.jump_url}).\n\nYou may *promote* this guild again in `{cooldown_time_str}`, if you so desire.\n\nI would also like to inform you that since my creation, I have received a grand total of 🚀`{total_bumps:,}` promotions.\nI do appreciate your support and look forward to serving you even more!\n\n*Best of luck in growing your esteemed community, good sir!*", color=discord.Color.from_rgb(color[0], color[1], color[2]))

            info_embed.add_field(name=f"🚀Guild Promotions", value=f"`{bumps:,}`")

            info_embed.set_thumbnail(url=self.bot.user.avatar.url)

            info_view=View()
            info_view.add_item(InviteLordBottington)
            info_view.add_item(JoinSupportGuild)

            #delete the initial embed telling the user that their bot is queued
            try:
                await initial_message.delete()
            except:
                pass
            
            await ctx.send(embed=info_embed, view=info_view)

            #add the cooldown data to mongodb
            bump_db.cooldowns.insert_one(
              {
                "server_id": ctx.guild.id,
                "promoter_id": ctx.author.id,
                "promotion_channel_id": ctx.channel.id,
                "cooldown": int(cooldown_time), #convert to int type to ensure accuracy
                "start_time": datetime.datetime.utcnow()
              }
            )
              
            await self.send_reminder(cooldown_time, ctx.guild.id)



    async def send_reminder(self, cooldown, guild_id):
        await asyncio.sleep(int(cooldown))

        #delete the cooldown data from mongodb
        cooldown_key = {"server_id": guild_id}
        cooldown_data = bump_db.cooldowns.find_one(cooldown_key)

        if cooldown_data:
            #delete the cooldown time on mongodb if the cooldown time is is found
            bump_db.cooldowns.delete_one(cooldown_key)


        #get the promotion event status from mongoDB
        promotions_status = await self.get_promotions_event_status(guild_id)

        #Promotion Reminders event only runs if event status using /eventhandler is set to enabled OR if the user has not set the status using /eventhandler
        if promotions_status == "Disabled":
            pass
        elif promotions_status == "Enabled":
            try:
                author = self.bot.get_user(cooldown_data['promoter_id'])
                guild = self.bot.get_guild(cooldown_data['server_id'])
                channel = self.bot.get_channel(cooldown_data['promotion_channel_id'])
            except:
                return
      
            promote_app_command = self.bot.get_application_command("promote")
            eventhandler_command = self.bot.get_application_command("eventhandler")
          
            reminder_embed = discord.Embed(
                title=f"{guild.name}\nPromotion Reminder",
                description=f"Attention members of {guild.name},\nThe promotion cooldown has **ended** for this guild...\n\nYou may once again use the </{promote_app_command.name}:{promote_app_command.id}> directive!\n\nYou may also utilize </{eventhandler_command.name}:{eventhandler_command.id}> in order to turn promotion reminders on or off.\n\n*Best of luck in promoting and growing this esteemed community, good fellows!*",
                color=discord.Color.from_rgb(130, 130, 130)
            )
            reminder_embed.set_thumbnail(url=self.bot.user.avatar.url)
    
            try:
                await channel.send(f"{author.mention} ***Promotion Reminder***", embed=reminder_embed)
            except:
                return


    #This retrieves the current server's event status from the mongoDB database
    async def get_promotions_event_status(self, guild_id):
        # mongoDBpass = os.environ['mongoDBpass']
        mongoDBpass = os.getenv('mongoDBpass')
        client = pymongo.MongoClient(mongoDBpass)
        event_handler_db = client.event_handler_db

        event_doc = event_handler_db.events.find_one({"server_id": guild_id})
        if event_doc:
            return event_doc["promotions_reminders"]
        else:
            return "Enabled"


    # when the bot goes offline (either manually or randomly)
    @commands.Cog.listener()
    async def on_disconnect(self):
        #### Promotions
        current_time = datetime.datetime.utcnow()
      
        # Get all cooldown entries from the database
        cooldown_data_list = bump_db.cooldowns.find()

        if cooldown_data_list:
            for cooldown_data in cooldown_data_list:
                start_time = cooldown_data['start_time']
                elapsed_time = current_time - start_time
                cooldown_time = int(cooldown_data['cooldown'])
                remaining_time = max(0, cooldown_time - int(elapsed_time.total_seconds()))
        
                if remaining_time <= 0:
                    # Delete the cooldown time from MongoDB if the cooldown time is found and over
                    bump_db.cooldowns.delete_one({"_id": cooldown_data["_id"]})
                else:
                    # Save the remaining time to the database
                    bump_db.cooldowns.update_one({"_id": cooldown_data["_id"]}, {"$set": {"cooldown": remaining_time}})


        #### Autopurge
        server_ids = []
        for guild in self.bot.guilds:
            server_ids.append(guild.id)
      
        #start the autopurge task
        configuration_cog = self.bot.get_cog('Configuration') #get the configuration cog
        current_time = datetime.datetime.utcnow()
        for server_id in server_ids:
            # Retrieve autopurge configurations from database
            autopurge_config = autopurge_db[f"autopurge_config_{server_id}"].find()
            if autopurge_config:
                for config in autopurge_config:
                    time_remaining = config['time_remaining']
                    if time_remaining:
                        start_time = config['start_time']
                        elapsed_time = current_time - start_time
                        time_left = int(time_remaining) #convert to int type
                        remaining_time = max(0, time_left - int(elapsed_time.total_seconds()))

                        #save time_remaining to database even if 0 time left
                        autopurge_db[f"autopurge_config_{server_id}"].update_one({"_id": config["_id"]}, {"$set": {"time_remaining": remaining_time}})

  

############################# PROMOTE #########################



  

############################# TEST PROMOTION #########################
    @discord.slash_command(
        name="testpromote",
        description="Test the promotion for this guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def testpromote(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return
          
        #get the promotion application command
        promotion_app_command = self.bot.get_application_command("promotion")

        bump_key = {"server_id": ctx.guild.id}
        server_data = bump_db.bump_configs.find_one(bump_key)

        if not server_data:
            no_data_description = f"Apologies {ctx.author.mention},\nIt appears that a guild promotion configuration has not been set up for ***{ctx.guild.name}***, good sir.\n\nYou may utilize my </{promotion_app_command.name}:{promotion_app_command.id}> directive to configure this for your guild, if you desire."
            no_data_embed = discord.Embed(title=f"{ctx.guild.name}\nPromotion Configuration", description = no_data_description, color=discord.Color.from_rgb(130, 130, 130))

            no_data_embed.set_thumbnail(url=self.bot.user.avatar.url)

            await ctx.respond(embed=no_data_embed, ephemeral=True)
            return

        else:
            automaton_invite_link = "https://discord.com/api/oauth2/authorize?client_id=1092515783025889383&permissions=3557027031&scope=bot%20applications.commands"
            support_guild_invite = "https://discord.gg/4P6ApdPAF7"
            invite_link = server_data['invite_link']
            guild_description = server_data['guild_description']
            promotion_channel = await self.bot.fetch_channel(server_data['promotion_channel_id'])
            color = server_data['color'] #array of (r, g, b)
            banner_url = server_data['banner_url']
            bumps = server_data['bumps']
            guild_created_at = ctx.guild.created_at.strftime('%B %d, %Y')
            topic = server_data['topic']

            test_embed =  discord.Embed(title=f"{ctx.guild.name}", description = guild_description, color=discord.Color.from_rgb(color[0], color[1], color[2]))

            test_embed.add_field(name="❗Guild Topic", value=f"`{topic}`", inline=True)
            test_embed.add_field(name="🕒Guild Creation", value=f"`{guild_created_at}`", inline=True)
            test_embed.add_field(name="👑 Owner", value=f"`{str(ctx.guild.owner.display_name)}`")
            test_embed.add_field(name="🚀Promotions", value=f"`{bumps:,}`", inline=True)
            test_embed.add_field(name="👨Member Count", value=f"`{ctx.guild.member_count:,}`", inline=True)
            test_embed.add_field(name="💎Boost Tier", value=f"`{ctx.guild.premium_subscription_count:,}`", inline=True)
            test_embed.add_field(name="🤣Iconography", value=f"`{len(ctx.guild.emojis):,}/{ctx.guild.emoji_limit:,}`", inline=True)
            test_embed.add_field(name="# Promotion Channel", value=promotion_channel.mention, inline=False)

            try:
                test_embed.set_thumbnail(url=ctx.guild.icon.url)
            except:
                pass

            if banner_url:
                test_embed.set_image(url=banner_url)

            try:
                test_embed.set_footer(text=f"Promoter: {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
            except:
                test_embed.set_footer(text=f"Promoter: {ctx.author.display_name}") #no avatar set

            InviteButton = discord.ui.Button(emoji='✅', label="Join Guild", url=invite_link, style=discord.ButtonStyle.link)
            InviteLordBottington = discord.ui.Button(emoji='🤖', label="Add Lord Bottington", url=automaton_invite_link, style=discord.ButtonStyle.link)
            JoinSupportGuild = discord.ui.Button(emoji='🎩', label="Join 𝓣𝓱𝓮 𝓢𝔀𝓮𝓮𝔃 𝓖𝓪𝓷𝓰", url=support_guild_invite, style=discord.ButtonStyle.link)

            view=View()
            view.add_item(InviteButton)
            view.add_item(InviteLordBottington)
            view.add_item(JoinSupportGuild)

            await ctx.respond(invite_link, embed=test_embed, view=view, ephemeral=True)


############################# TEST PROMOTION #########################



  

  
############################# AUTOSATIRE EVENT #########################
    #This retrieves the current server's event status from the mongoDB database
    async def get_autosatire_event_status(self, guild_id):
        # mongoDBpass = os.environ['mongoDBpass']
        mongoDBpass = os.getenv('mongoDBpass')
        client = pymongo.MongoClient(mongoDBpass)
        event_handler_db = client.event_handler_db

        event_doc = event_handler_db.events.find_one({"server_id": guild_id})
        if event_doc:
            return event_doc["autosatire"]
        else:
            return "Enabled"


  
    @tasks.loop(minutes=1)
    async def send_meme(self):
        # Get the time now and localize it to US/Central time
        now = datetime.datetime.now(pytz.timezone('US/Central'))

        now_time = now.strftime("%I:%M %p")
      
        if now_time == self.daily_meme_time:
            # Fetch the meme
            await self.get_random_meme()

  
    
    async def get_random_meme(self):
        #get the full list of autosatire configs
        autosatire_configs = autosatire_db.autosatire_configs.find()

        for config in autosatire_configs:
            satire_guild_id = config["server_id"]
            channel_id = config["channel_id"] #the channel to send the meme
            community = config["community"] #the desired subreddit
          
            autosatire_channel = self.bot.get_channel(channel_id)
            autosatire_guild = self.bot.get_guild(satire_guild_id)

            #get the autosatire event status from mongoDB
            autosatire_status = await self.get_autosatire_event_status(satire_guild_id)

            #Autosatire task event only runs if event status using /eventhandler is set to enabled OR if the user has not set the status using /eventhandler
            if autosatire_status == "Disabled":
                continue
            elif autosatire_status == "Enabled":
              
                # Reddit_API = os.environ['RedditAPI']
                # Client_ID = os.environ['RedditClientID']
                Reddit_API = os.getenv('RedditAPI')
                Client_ID = os.getenv('RedditClientID')
          
                ### By using async with asyncpraw.Reddit(...) as reddit, the client session will be automatically closed once the code execution leaves the with block, ensuring that the session and connector are properly closed.
                async with asyncpraw.Reddit(
                    client_id=Client_ID,
                    client_secret=Reddit_API,
                    user_agent="Lord Bottington Reddit Application Meme Finder"
                ) as reddit:
          
                    try:
                        subreddit = await reddit.subreddit(community)
                  
                        all_subs = []
                        hot = subreddit.hot(limit=20) # bot will choose between the 20 hottest memes in the subreddit
                      
                        async for submission in hot:
                            if submission.over_18 is False:  # Check if the post is marked NSFW (omit it if it is)
                                all_subs.append(submission)
          
                    # subreddit is private
                    except asyncprawcore.exceptions.Forbidden:
                        error_embed = discord.Embed(title="Auto-Satire Error", description=f"Apologies members of ***{autosatire_guild.name}***,\nIt appears that `r/{community}` is currently a *private* community, so I am unable to retrieve a satirical image from there.\n\n*Please contact an administrator of your guild to use my `/autosatire` directive to update this.*", color=discord.Color.from_rgb(130, 130, 130))
                      
                        error_embed.set_thumbnail(url=self.bot.user.avatar.url)
    
                        await autosatire_channel.send(embed=error_embed)
                        return
          
          
                    if len(all_subs) == 0:
                        error_embed = discord.Embed(title="Auto-Satire Error", description=f"Apologies members of ***{autosatire_guild.name}***,\nIt appears that I was unable to find an appropriate satirical image from `r/{community}`.\n\n*I will try again tomorrow...", color=discord.Color.from_rgb(130, 130, 130))
                      
                        error_embed.set_thumbnail(url=self.bot.user.avatar.url)
    
                        await autosatire_channel.send(embed=error_embed)
                        return
          
                  
                    random_sub = random.choice(all_subs)
              
                    name = random_sub.title
                    url = random_sub.url
                    original_post = f"https://www.reddit.com{random_sub.permalink}"
                    subreddit = random_sub.subreddit
                    author = random_sub.author
                    score = random_sub.score #the number of upvotes
                
              
                    meme_embed = discord.Embed(title="Auto-Satirical Imagery", description=f"Attention members of ***{autosatire_guild.name}***.\nHere is a satirical image for your enjoyment.", color=discord.Color.from_rgb(130, 130, 130))
                    meme_embed.add_field(name="Satirical Image Name", value=f"`{name}`", inline=False)
                    meme_embed.add_field(name="Author", value=f"`{author}`", inline=False)
                    meme_embed.add_field(name="Subreddit", value=f"`{subreddit}`")
                    meme_embed.add_field(name="Upvotes", value="`⬆ {:,}`".format(score))
                    meme_embed.add_field(name="Original Posting", value=f"[Click Here]({original_post})")
                    meme_embed.set_image(url=url)
                    meme_embed.set_footer(text="Powered by Reddit")
              
                    await autosatire_channel.send(embed=meme_embed)
      

############################# AUTOSATIRE EVENT #########################



  
  
  
  
############################### DEFINE (PROPER) ##############################
    @discord.slash_command(
        name="defineproper",
        description="The automaton will define a term for you in its proper form.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def defineproper(self, ctx, term: Option(str, name="term", description="Term to define.")):
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}"
        response = requests.get(url)
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            # Get the first entry from the response
            entry = data[0]
            
            # Extract relevant information from the entry
            term = entry.get("word")
            phonetics = entry.get("phonetics")
            meanings = entry.get("meanings")
            
            # Create an embed to display the information
            embed = discord.Embed(title="Proper Definition", description=f"{ctx.author.mention}\nHere is the proper definition for the term you requested, good sir.", color=discord.Color.from_rgb(130, 130, 130))
    
            embed.add_field(name="Term", value=f"`{term}`", inline=False)
            
            # Add phonetics to the embed
            for i, phonetic in enumerate(phonetics):
                text = phonetic.get("text")
                audio = phonetic.get("audio")
                embed.add_field(name=f"Phonetic {i+1}", value=f"`{text}`", inline=True)
                if audio:
                    embed.add_field(name=f"Pronunciation {i+1}", value=f"[Click Here]({audio})", inline=True)
            
            # Add meanings to the embed
            for i, meaning in enumerate(meanings):
                part_of_speech = meaning.get("partOfSpeech")
                definitions = meaning.get("definitions")
                
                # Create separate fields for each part of speech
                embed.add_field(name=f"Part of Speech {i+1}", value=f"`{part_of_speech}`", inline=False)
                
                # Create a string to hold all definitions, examples, synonyms, and antonyms for the part of speech
                part_of_speech_info = ""
                
                # Add definitions to the part of speech info
                for x, definition in enumerate(definitions):
                    definition_text = definition.get("definition")
                    example = definition.get("example")
                    synonyms = definition.get("synonyms")
                    antonyms = definition.get("antonyms")
                    
                    part_of_speech_info += f"\n**Definition {x+1}:** `{definition_text}`"
                    
                    if example:
                        part_of_speech_info += f"\n**Example {x+1}:** `{example}`"
                    
                    if synonyms:
                        part_of_speech_info += f"\n**Synonyms {x+1}:** {', '.join(synonyms)}"
                    
                    if antonyms:
                        part_of_speech_info += f"\n**Antonyms {x+1}:** {', '.join(antonyms)}"
                
                # Add the part of speech info as a single field
                embed.add_field(name="Definitions", value=part_of_speech_info, inline=False)
    
            embed.set_footer(text="Powered by Free Dictionary")
            
            await ctx.respond(embed=embed)
        else:
            await ctx.respond(f"Apologies {ctx.author.mention},\nI was unable to locate a proper definition for ***{term}***, good sir.\n*Please try again.*", ephemeral=True)

          
############################### DEFINE (PROPER) ##############################
  





  
############################### DEFINE (URBAN) ##############################
    @discord.slash_command(
        name="defineimproper",
        description="The automaton will define a term for you in its improper (slang/urban) form.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def defineimproper(self, ctx, term: Option(str, name="term", description="Slang term to define."), censor: Option(bool, name="censor", description="Censor the resulting definition. (Default: True)", required=False, default=True)):
        # get the definition from Urban Dictionary
        try:
            with urllib.request.urlopen(f"https://api.urbandictionary.com/v0/define?term={term}") as url:
                data = json.loads(url.read().decode())
        except Exception:
            return await ctx.respond(f"Apologies {ctx.author.mention}\nI have received invalid data from my definition source, good sir.\nIt is possible that the source might not be functioning properly at the moment...\n\n*Please try again later.*", ephemeral=True)
    
        if not data:
            return await ctx.respond(f"Apologies {ctx.author.mention},\nI believe the definition source is not functioning.\n\n*Please try again later, good sir.*", ephemeral=True)
    
        if not len(data["list"]):
            return await ctx.respond(f"Apologies {ctx.author.mention},\nI was unable to locate a term with the name ***{term}***, good sir.\n\n*Please try again.*", ephemeral=True)
    
        results = data["list"]
        top_result = results[0]

        slang_term = top_result['word']
        definition = top_result["definition"]
        example = top_result['example']
        author = top_result['author']

        definition = definition.replace('[', "").replace("]", "")
        example = example.replace('[', "").replace("]", "")

        # Censor the term, definition, author name, and example
        if censor is True:
            with open("text_files/banned_words.txt", "r") as file:
                banned_words = [word.strip().lower() for word in file.readlines()]

            for banned_word in banned_words:
                censored_word = "*" * len(banned_word)
                # Add word boundaries to banned_word using regex
                banned_word_regex = fr"\b{re.escape(banned_word.lower())}\b"
                
                slang_term = re.sub(banned_word_regex, censored_word, slang_term.lower(), flags=re.IGNORECASE)
                definition = re.sub(banned_word_regex, censored_word, definition.lower(), flags=re.IGNORECASE)
                example = re.sub(banned_word_regex, censored_word, example.lower(), flags=re.IGNORECASE)
                author = re.sub(banned_word_regex, censored_word, author.lower(), flags=re.IGNORECASE)

      
        if len(definition) >= 1000:
            definition = definition[:1000]
            definition = definition.rsplit(" ", 1)[0]
            definition += "..."

        if len(example) >= 1000:
            example = example[:1000]
            example = example.rsplit(" ", 1)[0]
            example += "..."

      
        em = discord.Embed(title="Improper Definition", description=f"{ctx.author.mention}\nHere is the improper definition for the term you requested, good sir.", color=discord.Color.from_rgb(130, 130, 130))

        em.add_field(name="Term", value=f"`{slang_term}`")
      
        formatted_definition = "*{}*".format(definition)
      
        em.add_field(name="Definition", value=formatted_definition, inline=False)

        em.add_field(name="Author", value=f"`{author}`", inline=False)
        em.add_field(name="Example", value=f"*{example}*", inline=False)
        em.add_field(name="Thumbs Up", value=f"`👍 {top_result['thumbs_up']}`")
        em.add_field(name="Thumbs Down", value=f"`👎 {top_result['thumbs_down']}`")
        
        em.set_footer(text="Powered by Urban Dictionary")
        
        await ctx.respond(embed=em)
############################### DEFINE (URBAN) ##############################


  
  


################################# SEARCH (LMGTFY)###############################  
    @discord.slash_command(
        name="search",
        description="The automaton will demonstrate how to find something on the internet.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def search(self, ctx, search_terms: Option(str, name="search_terms", description="Search terms to find on the web.")):

        # Check for inappropriate searches
        with open("text_files/banned_words.txt", "r") as file:
            banned_words = [word.strip().lower() for word in file.readlines()]
    
        # Convert search_terms to lowercase for case-insensitive comparison
        search_terms_lower = search_terms.lower()
    
        for banned_word in banned_words:
            # Add word boundaries to banned_word using regex
            banned_word_regex = fr"\b{re.escape(banned_word.lower())}\b"

            flagged_term = re.search(banned_word_regex, search_terms_lower, flags=re.IGNORECASE)
          
            if flagged_term:
                # Inappropriate phrase found, stop further processing
                return await ctx.respond(f"Apologies {ctx.author.mention},\nI am unable to complete your search as it contains inappropriate terms, good sir.\n*Please try again.*\n\nFlagged term: `{flagged_term.group()}`", ephemeral=True)

      
        #the original search terms
        text = search_terms
      
        mentions = re.findall(r"<@!?(\d+)>", search_terms)
        for mention in mentions:
            user = self.bot.get_user(int(mention))
            if user:
                if not user.bot:
                    text = text.replace(f"<@{mention}>", user.display_name)
                else:
                    text = text.replace(f"<@{mention}>", user.name)
            else:
                member = ctx.guild.get_member(int(mention))
                if not member.bot:
                    text = text.replace(f"<@{mention}>", member.display_name)
                else:
                    text = text.replace(f"<@{mention}>", member.name)
                
                  
        channel_mentions = re.findall(r"<#(\d+)>", search_terms)
        for channel_mention in channel_mentions:
            channel = self.bot.get_channel(int(channel_mention))
            if channel:
                text = text.replace(f"<#{channel_mention}>", channel.name)
              
        role_mentions = re.findall(r"<@&(\d+)>", search_terms)
        for role_mention in role_mentions:
            role_id = int(role_mention)
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            if role:
                text = text.replace(f"<@&{role_mention}>", role.name)
      
        formatted_text = urllib.parse.quote_plus(text)
      
        formatted_text = formatted_text.replace("@everyone", "everyone")
        formatted_text = formatted_text.replace("@here", "here")
      
        result = "https://lmgtfy.app/?q={}&s=g".format(formatted_text)

        lmgtfy_embed = discord.Embed(title="Search Results", description=f"{ctx.author.mention}\nLet me demonstrate how to find such things on the internet for you, good sir.", color=discord.Color.from_rgb(130, 130, 130))
        lmgtfy_embed.add_field(name="Search Term", value=f"```{text}```")
        lmgtfy_embed.add_field(name="Demonstration", value=f"[Click Here]({result})", inline=False)

        lmgtfy_embed.set_thumbnail(url=self.bot.user.avatar.url)

        await ctx.respond(embed=lmgtfy_embed)
################################# SEARCH (LMGTFY)###############################



  

  
#######################################PLAY########################################
    #the following games list uses the game's headers pictures from STEAM (if available on steam, otherwise, use imgur to host the images)
    games_list = {
        "Apex Legends": {
            "title": "Apex Legends",
            "url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1172470/header.jpg?t=1684341161"
        },
        "Overwatch 2": {
            "title": "Overwatch 2",
            "url": "https://i.imgur.com/pczOhNY.jpg"
        },
        "Valorant": {
            "title": "Valorant",
            "url": "https://i.imgur.com/Ekfte4n.jpg"
        },
        "CS:GO": {
            "title": "Counter-Strike: Global Offensive",
            "url": "https://cdn.cloudflare.steamstatic.com/steam/apps/730/header.jpg?t=1668125812"
        },
        "Rainbow Six Siege": {
            "title": "Tom Clancy's Rainbow Six Siege",
            "url": "https://cdn.cloudflare.steamstatic.com/steam/apps/359550/header.jpg?t=1683930161"
        },
        "COD: MW2": {
            "title": "Call of Duty: Modern Warfare II",
            "url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1938090/header.jpg?t=1686759791"
        },
        "Fortnite": {
            "title": "Fortnite",
            "url": "https://i.imgur.com/bTU3Z5q.jpg"
        },
        "Minecraft": {
            "title": "Minecraft",
            "url": "https://i.imgur.com/tFPFec8.jpg"
        },
        "GTA Online": {
            "title": "Grand Theft Auto Online",
            "url": "https://cdn.cloudflare.steamstatic.com/steam/apps/271590/header.jpg?t=1678296348"
        },
        "Red Dead Online": {
            "title": "Red Dead Online",
            "url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1404210/header.jpg?t=1656615218"
        },
        "Dead by Daylight": {
            "title": "Dead by Daylight",
            "url": "https://cdn.cloudflare.steamstatic.com/steam/apps/381210/header.jpg?t=1683120711"
        },
        "Among Us": {
            "title": "Among Us",
            "url": "https://cdn.cloudflare.steamstatic.com/steam/apps/945360/header.jpg?t=1684189647"
        },
        "Other": {
            "title": None,
            "url": None
        }
    }
    
    class ReadyOrNotView(discord.ui.View):
        def __init__(self, ctx, bot, players, platform, game, other_game):
            super().__init__(timeout=3600) #used to initialize the timeout (if needed)
            self.ctx = ctx #initialize the context
            self.bot = bot #intialize bot
            self.game = Utility.games_list[game]
            self.players = players
            self.platform = platform
            self.other_game = other_game
            self.joined_users = []
            self.tentative_users = []
            self.declined_users = []



        #timeout function
        async def on_timeout(self):
            self.disable_all_items()
            embed = self.create_embed(self.ctx)
          
            try:
                await self.message.edit(embed=embed, view=None)
            except discord.errors.NotFound: #if message deleted before timeout
                pass

            self.stop()
      

    
    
        def convert_user_list_to_str(self, user_list, default_str="None"):
            if len(user_list):
                return "\n".join(user_list)
            return default_str
    
        def create_embed(self, ctx):
            remaining_users = self.players - len(self.joined_users)

            
            desc = f"Good fellows of {self.ctx.guild.name},\n\n***{self.ctx.author.display_name}*** is looking to play a game with some other individuals.\nCare to join in their endeavors, good sir?"
            embed = discord.Embed(title="Join Together in Play", description=desc, color=discord.Color.from_rgb(130, 130, 130))
    
            if self.game['url']:
                embed.set_image(url=self.game['url'])

            #set thumbnail to author's avatar
            try:
                embed.set_thumbnail(url=self.ctx.author.avatar.url)
            except:
                pass #if no avatar set, skip the thumbnail


            embed.add_field(inline=False, name="Game", value=f"*{self.game['title'] if self.game['title'] else self.other_game}*")
            embed.add_field(inline=False, name="Desired Game Platform", value=self.platform)
            embed.add_field(inline=False, name="Number of Players Needed", value=f"*{remaining_users}*")
          
            embed.add_field(inline=True, name="✅ Joined", value=f"*{self.convert_user_list_to_str(self.joined_users)}*")
            embed.add_field(inline=True, name="❌ Declined", value=f"*{self.convert_user_list_to_str(self.declined_users)}*")
            embed.add_field(inline=True, name="🤔 Tentative", value=f"*{self.convert_user_list_to_str(self.tentative_users)}*")
    
            return embed
    
        def check_players_full(self):
            if len(self.joined_users) >= self.players:
                return True
            return False
    
    
        # def disable_all_buttons(self):
        #     for child in self.children:
        #         child.disabled = True
              
      
        async def update_message(self, ctx):
            embed = self.create_embed(self.ctx)
            
            if self.check_players_full():
                self.stop()
                await self.message.edit(view=None, embed=embed)
            else:
                await self.message.edit(view=self, embed=embed)

      
        @discord.ui.button(label="Join", style=discord.ButtonStyle.green, emoji="👍")
        async def join_button(self, button: discord.ui.Button, interaction: discord.Interaction):
            if interaction.user == self.ctx.author: #author cannot use the buttons
                await interaction.response.defer()
                return
          
            await interaction.response.defer()
            
            if interaction.user.display_name not in self.joined_users:
                self.joined_users.append(interaction.user.display_name)
            # remove from declined and from tentative if inside
            if interaction.user.display_name in self.tentative_users:
                self.tentative_users.remove(interaction.user.display_name)
            if interaction.user.display_name in self.declined_users:
                self.declined_users.remove(interaction.user.display_name)
        
            await self.update_message(self.ctx)
        
        @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, emoji="👎")
        async def decline_button(self, button: discord.ui.Button, interaction: discord.Interaction):
            if interaction.user == self.ctx.author: #author cannot use the buttons
                await interaction.response.defer()
                return

          
            await interaction.response.defer()
        
            if interaction.user.display_name not in self.declined_users:
                self.declined_users.append(interaction.user.display_name)
            # remove from joined and from tentative if inside
            if interaction.user.display_name in self.tentative_users:
                self.tentative_users.remove(interaction.user.display_name)
            if interaction.user.display_name in self.joined_users:
                self.joined_users.remove(interaction.user.display_name)
        
            await self.update_message(self.ctx)
        
        @discord.ui.button(label="Maybe", style=discord.ButtonStyle.blurple, emoji="🤔")
        async def tentative_button(self, button: discord.ui.Button, interaction: discord.Interaction):
            if interaction.user == self.ctx.author: #author cannot use the buttons
                await interaction.response.defer()
                return

          
            await interaction.response.defer()
        
            if interaction.user.display_name not in self.tentative_users:
                self.tentative_users.append(interaction.user.display_name)
            # remove from declined and from joined if inside
            if interaction.user.display_name in self.joined_users:
                self.joined_users.remove(interaction.user.display_name)
            if interaction.user.display_name in self.declined_users:
                self.declined_users.remove(interaction.user.display_name)
        
            await self.update_message(self.ctx)
    

    
    @discord.slash_command(
        name="play",
        description="The automaton will help you reach out to other like-minded players in search of game companions.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def play(
          self,
          ctx,
          game: Option(str, name="game", description="Name of game you would like to play.", choices=["Apex Legends", "Overwatch 2", "Valorant", "CS:GO", "Rainbow Six Siege", "COD: MW2", "Fortnite", "Minecraft", "GTA Online", "Red Dead Online", "Dead by Daylight", "Among Us", "Other"]), 
          players: Option(int, name="players", description="Number of players. (Default: 3; Min: 1, Max: 20)", required=False, default=3, min_value=1, max_value=20),
          platform: Option(str, name="platform", description="Desired game platform.", required=False, default="Any", choices=["🎮 Console", "💻 PC", "📱 Mobile", "🕹 Any"]),
          other_game: Option(str, name="other_game", description="Name of game (if not listed in original choices. (Default: a game)", required=False, default=None)
          ):

            #other game title only works if Other is selected
            if game == "Other":
                if other_game:
                    other_game = other_game
                elif other_game is None or other_game == "":
                    other_game = "a game"
            else:
                pass
            
            view = self.ReadyOrNotView(ctx, self.bot, players, platform, game, other_game)


            
            desc = f"Good fellows of {ctx.guild.name},\n\n***{ctx.author.display_name}*** is looking to play a game with some other individuals.\nCare to join in their endeavors, good sir?"
            embed = discord.Embed(title="Join Together in Play", description=desc, color=discord.Color.from_rgb(130, 130, 130))
    
            if self.games_list[game]['url']:
                embed.set_image(url=self.games_list[game]['url'])

            #set thumbnail to author's avatar
            try:
                embed.set_thumbnail(url=ctx.author.avatar.url)
            except:
                pass #if no avatar set, skip the thumbnail


            embed.add_field(inline=False, name="Game", value=f"*{self.games_list[game]['title'] if self.games_list[game]['title'] else other_game}*")
            embed.add_field(inline=False, name="Desired Game Platform", value=platform)
            embed.add_field(inline=False, name="Number of Players Needed", value=f"*{players}*")
          
            embed.add_field(inline=True, name="✅ Joined", value="*None*")
            embed.add_field(inline=True, name="❌ Declined", value="*None*")
            embed.add_field(inline=True, name="🤔 Tentative", value="*None*")

            await ctx.respond(embed=embed, view=view)
  
            
#######################################PLAY########################################




  

###################################EMBEDDER################################
    # regular text input modal for embeds
    class EmbedderModal(discord.ui.Modal):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
    
            # if self.title or self.body or self.field_name or self.field_value:
            self.add_item(discord.ui.InputText(label="Embed Title", placeholder="Enter embed title.", style=discord.InputTextStyle.long, required=False, max_length=45))
            self.add_item(discord.ui.InputText(label="Embed Body Text", style=discord.InputTextStyle.long, placeholder="Enter message that will appear in the embed body.", required=False))
            self.add_item(discord.ui.InputText(label="Field Title", placeholder="Enter field title.", style=discord.InputTextStyle.long, required=False, max_length=45))
            self.add_item(discord.ui.InputText(label="Field Text", style=discord.InputTextStyle.long, placeholder="Enter text that will appear in the field of the embed.", required=False, max_length=1000))
            self.add_item(discord.ui.InputText(label="Footer Text", style=discord.InputTextStyle.long, placeholder="Enter text that will appear in the footer of the embed.", required=False, max_length=2000))
    
    
        async def callback(self, interaction: discord.Interaction):
            self.title = self.children[0].value
            self.body = self.children[1].value
            self.field_name = self.children[2].value
            self.field_value = self.children[3].value
            self.footer = self.children[4].value
            await interaction.response.defer() #acknowledges the interaction before calling self.stop()
            self.stop()

  
  
  
    @discord.slash_command(
        name="embedder",
        description="Send embedded messages to a channel. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def embedder(
            self, 
            ctx, 
            channel: Option(discord.TextChannel, name="channel", description="Select a channel to send the embed message. (Default: Directive Channel)", required=False, default=None),
            color: Option(str, name="color", description="Select a color for the timed embed. (Default: 🔵 Blue)", required=False, choices=["🔴 Red", "🟢 Green", "🔵 Blue", "🟡 Yellow", "🟣 Purple", "⚫ Black", "⚪ White"], default=None),
            thumbnail: Option(discord.Attachment, name="thumbnail", description="URL of the thumbnail image.", required=False, default=None),
            image: Option(discord.Attachment, name="image", description="URL of the embed image.", required=False, default=None)
    ):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return
    
        if channel:
            channel = channel
        else:
            channel = ctx.channel

      
        #define RGB color codes
        color_codes = {
            "🔴 Red": (255, 0, 0),
            "🟢 Green": (0, 255, 0),
            "🔵 Blue": (0, 0, 255),
            "🟡 Yellow": (255, 255, 0),
            "🟣 Purple": (152, 3, 252),
            "⚫ Black": (0, 0, 0),
            "⚪ White": (255, 255, 255)
        }
    
        if color is not None:
            if color in color_codes:
                r = color_codes[color][0]
                g = color_codes[color][1]
                b = color_codes[color][2]
            else:
                await ctx.respond(f"Apologies {ctx.author.mention}\n{color} is not a viable option for the timed embed color.\n*Please try again.*", ephemeral=True)
                return
        
        else: #default blue color
            r = 0
            g = 0
            b = 255


        #check to see if the user defined urls are a .jpg, .jpeg, .png, or .gif
        if thumbnail:
            picture_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            file_extension = os.path.splitext(thumbnail.filename)[1].lower()
    
            if file_extension in picture_extensions:
                thumbnail = thumbnail.url
            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that *{thumbnail.filename}* is not a valid picture file. This file must be a JPG, JPEG, PNG, or GIF.\n*Please try again.*", ephemeral=True)
                return
    
    
        if image:
            picture_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            file_extension = os.path.splitext(image.filename)[1].lower()
    
            if file_extension in picture_extensions:
                image = image.url
            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that *{image.filename}* is not a valid picture file. This file must be a JPG, JPEG, PNG, or GIF.\n*Please try again.*", ephemeral=True)
                return
      

      
    
        #send the embed modal to get the text configurations
        modal = self.EmbedderModal(title="Embed Text Configuration")
        await ctx.send_modal(modal)
      
        try:
            await asyncio.wait_for(modal.wait(), timeout=600.0)
    
            title = modal.title
            body = modal.body
            field_name = modal.field_name
            field_value = modal.field_value
            footer = modal.footer

            #if all fields are blank
            if not title and not body and not field_name and not field_value and not footer:
                await ctx.respond(f"Apologies {ctx.author.mention},\nAt least one of the fields needs to be filled in.\n*Please try again.*", ephemeral=True)
                return

            
        except asyncio.TimeoutError:
            await ctx.respond("Good sir, it appears you have taken too long to enter your embed text configuration.\n*Please try again.*", ephemeral=True)
            return

      

        #begin creating the embed object
        embed = discord.Embed(
          title=title if title else "",
          description=body if body else "",
          color=discord.Color.from_rgb(r, g, b)
        )

        #set the author
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)

        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

        if image:
            embed.set_image(url=image)

        if field_name and field_value:
            embed.add_field(name=field_name, value=field_value)
        elif field_name and not field_value:
            embed.add_field(name=field_name, value="\u200b")
        elif field_value:
            embed.add_field(name="\u200b", value=field_value)
      
        if footer:
            embed.set_footer(text=footer)


        await ctx.respond(f"{ctx.author.mention}\nI have dispatched your embed to {channel.mention}, good sir.", ephemeral=True)

        await channel.send(embed=embed)

        
#####################################EMBEDDER################################








  

####################################AUTOPURGE LIST##############################
    @discord.slash_command(
        name="autopurgelist",
        description="Receive a list of currently autopurged channels for the guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def autopurgelist(self, ctx):
      
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

        if not autopurge_db[f"autopurge_config_{ctx.guild.id}"].find() or autopurge_db[f"autopurge_config_{ctx.guild.id}"].count_documents({}) == 0:
            autopurge_command = self.bot.get_application_command("autopurge")
            await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that no channels in {ctx.guild.name} are being autopurged at the moment.\nConsider using my </{autopurge_command.name}:{autopurge_command.id}> directive to configure these, good sir.", ephemeral=True)
            return

        else:
            autopurge_embed = discord.Embed(title=f"{ctx.guild.name}\n__Autopurge List__", description = "The following is a list of the current channels being autopurged and their respective frequencies and message counts.", color = discord.Color.from_rgb(130, 130, 130))

            i = 1
            for config in autopurge_db[f"autopurge_config_{ctx.guild.id}"].find():
                purge_channel_id = config['purge_channel_id']
                purge_channel = self.bot.get_channel(purge_channel_id)
                frequency = config['frequency']
                messagecount = config['messagecount']
                time_remaining = config['time_remaining']


                if frequency:
                    # Calculate the total frequency time in days, hours, minutes, and seconds
                    days, remainder = divmod(frequency, 86400)
                    hours, remainder = divmod(remainder, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    
                    # Format the frequency string
                    if days > 0:
                        frequency_purge_time = f"{days:02d}d:{hours:02d}h:{minutes:02d}m:{seconds:02d}s"
                    elif hours > 0:
                        frequency_purge_time = f"{hours:02d}h:{minutes:02d}m:{seconds:02d}s"
                    elif minutes > 0:
                        frequency_purge_time = f"{minutes:02d}m:{seconds:02d}s"
                    else:
                        frequency_purge_time = f"{seconds}s"

                else:
                    frequency_purge_time = "n/a"
                    frequency = "None"


                if not messagecount:
                    messagecount = "No"

              
                if time_remaining:
                    current_time = datetime.datetime.utcnow()
                    start_time = config['start_time']
                    elapsed_time = current_time - start_time
                    time_left = float(time_remaining) #convert to float type
                    remaining_time = max(0, time_left - float(elapsed_time.total_seconds()))
                  
                    # Calculate the total time remaining in days, hours, minutes, and seconds
                    days, remainder = divmod(int(remaining_time), 86400)
                    hours, remainder = divmod(remainder, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    
                    # Format the frequency string
                    if days > 0:
                        time_left = f"{days:02d}d:{hours:02d}h:{minutes:02d}m:{seconds:02d}s"
                    elif hours > 0:
                        time_left = f"{hours:02d}h:{minutes:02d}m:{seconds:02d}s"
                    elif minutes > 0:
                        time_left = f"{minutes:02d}m:{seconds:02d}s"
                    else:
                        time_left = f"{seconds}s"

                    time_rem_string = f"> Time Remaining Until Next Autopurge: `{time_left}`"

              
                autopurge_embed.add_field(name = f"Purge Channel {i}", value = f"> Channel: {purge_channel.mention}\n> Frequency: `{frequency_purge_time}`\n> Message Count: `{messagecount} messages`\n{time_rem_string if time_remaining else ''}", inline = True)
                i = i + 1


            #trash can gif
            autopurge_embed.set_thumbnail(url="https://i.imgur.com/0Os7c99.gif")

            await ctx.respond(embed = autopurge_embed, ephemeral=True)

#####################################AUTOPURGE LIST##############################



  

#########################################PURGE##################################
    @discord.slash_command(
        name="purge",
        description="Purge messages from a desired channel. (Manage Messages Privileges)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(manage_messages=True) #must have manage messages permissons
    async def purge(self, ctx, messagecount: Option(int, name="messagecount", description="Number of messages that will be deleted from the specified channel.", min_value=1, max_value=100)):
      
        #user must have manage messages privileges
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those that are permitted to *manage messages* in this guild may use this directive, good sir.", ephemeral=True)
            return

        # Get the bot's member object
        lordbottington = ctx.guild.get_member(ctx.bot.user.id)

        # Check if the bot has manage_messages permission in the current channel
        if not lordbottington.guild_permissions.manage_messages:
            await ctx.respond(f"Apologies {ctx.author.mention},\nI do not have permission to delete messages in this guild.\n*Please change this in the guild settings and try again.*", ephemeral=True)
            return
      
    
        if messagecount == 0:
            await ctx.respond(f"Apologies {ctx.author.mention},\nI am unable to delete ***0*** messages.\n*Please try again.*", ephemeral=True)
            return
        elif messagecount > 100:
            await ctx.respond(f"{ctx.author.mention}\nPlease specify a message count less than or equal to ***100*** to avoid Discord rate limits, good sir...", ephemeral=True)
            return
        else:
            await ctx.respond(f"Attempting to delete *{messagecount}* message{'s' if messagecount > 1 else ''} from {ctx.channel.mention}...", ephemeral=True)
            await asyncio.sleep(5)
    
            deleted = await ctx.channel.purge(limit=messagecount)
            deleted_count = len(deleted)
    
            #if there were no messages in the channel
            if deleted_count == 0:
                await ctx.respond(f"Apologies {ctx.author.mention},\nThere were no messages to delete in {ctx.channel.mention}.", ephemeral=True)
                return
            else:  
                await ctx.respond(f"{ctx.author.mention}\nI have successfully removed ***{deleted_count}*** message{'s' if deleted_count > 1 else ''} from {ctx.channel.mention}, good sir.", ephemeral=True)

#########################################PURGE##################################




  


  
#################################EMOJIS#######################################
    class IconView(discord.ui.View):
        def __init__(self, ctx, bot, iconlinks):
            super().__init__(timeout=120) #used to initialize the timeout (if needed)
            self.ctx = ctx #initialize the context
            self.bot = bot #intialize bot
            self.iconlinks = iconlinks

      
        #timeout function
        async def on_timeout(self):
            self.disable_all_items()
          
            try:
                await self.message.edit(view=None)
            except discord.errors.NotFound: #if message deleted before timeout
                pass
  
            self.stop()


        #insert the add icon button
        @discord.ui.button(label="Add Iconography", style=discord.ButtonStyle.success, emoji="😀")
        async def add_icon_button_callback(self, button, interaction):
            #only allow author or administrator to add icons
            if await self.bot.is_owner(self.ctx.author) or self.ctx.author.guild_permissions.administrator:

                await interaction.response.defer() #acknowledge the interaction and tell the bot to wait for a response
              

                #wait for the user file input (timeout after 30 seconds)
                try:
                    #disable the add and remove icon buttons when done waiting
                    for child in self.children: #leave cancel button alone
                        if child.label == "Cancel":
                            pass
                        else:
                            child.disabled = True

                    await self.message.edit(content=f"{interaction.user.mention}\nPlease submit a file directly into the chat box which you would like to add as an icon.", view=self)

                  
                    file = await self.bot.wait_for("message", check=lambda m: m.author == interaction.user and m.channel == self.ctx.channel, timeout=120.0)
                except asyncio.TimeoutError:
                    try:#check if the list has not been cancelled
                        await self.ctx.channel.fetch_message(self.message.id)

                        #re-enable the add and remove icon buttons when timed out
                        for child in self.children: #leave cancel button alone
                            if child.label == "Cancel":
                                pass
                            else:
                                child.disabled = False

                        await self.message.edit(content="", view=self) #update the changes of the enable buttons in the view

                      
                        await self.ctx.respond(f"Apologies {interaction.user.mention},\nIt appears you took to long to submit a file.\n*Please try again.*", ephemeral=True)
                        return
                  
                    except discord.NotFound:
                        # The icon list has been cancelled
                        return


                #retrieve the file name
                try:
                    file_name = file.attachments[0].filename #file name of the first attachment
                except IndexError: #no file was attached
                    await self.ctx.respond(f"Apologies {interaction.user.mention},\nThe message must contain a picture file (JPG, JPEG, PNG, GIF).\n*Please try again.*", ephemeral=True)

                    #re-enable the add and remove icon buttons when timed out
                    for child in self.children: #leave cancel button alone
                        if child.label == "Cancel":
                            pass
                        else:
                            child.disabled = False

                    await self.message.edit(content="", view=self) #update the changes of the enable buttons in the view
                  
                    await file.delete() #delete the user's message
                    return
    
                file_name = file_name.split('.') #split the file name into name and extension
                
                file_extension = file_name[1] #file extension

                #check if the file is a picture file
                if file_extension in ["jpg", "jpeg", "png", "gif"]:
                    file_name=file_name[0] #file name
                    await file.delete()
                else:
                    await self.ctx.respond(f"Apologies {interaction.user.mention},\nThe file must be a picture file (JPG, JPEG, PNG, GIF).\n*Please try again.*", ephemeral=True)

                    #re-enable the add and remove icon buttons when timed out
                    for child in self.children: #leave cancel button alone
                        if child.label == "Cancel":
                            pass
                        else:
                            child.disabled = False

                    await self.message.edit(content="", view=self) #update the changes of the enable buttons in the view
                  
                    await file.delete()
                    return
    
              
                # Add the emoji to the server
                try:
                    await self.ctx.guild.create_custom_emoji(name=file_name, image=await file.attachments[0].read())
    
                    #edit the embed to reflect the new emoji addition
                    try:
                        icons = self.ctx.guild.emojis #retrieve the server emojis
                    
                        static_icons = []
                        animated_icons = []
                        for icon in icons:
                            if icon.animated: #animated emojis
                                if self.iconlinks:
                                    animated_icons.append(f"{icon} - [{icon.name}]({icon.url})")
                                else:
                                    animated_icons.append(f"{icon} - {icon.name}")
                            else: #static emojis
                                if self.iconlinks:
                                    static_icons.append(f"{icon} - [{icon.name}]({icon.url})")
                                else:
                                    static_icons.append(f"{icon} - {icon.name}")
            
                        # get the total number of static and animated icons
                        total_static_icons = len(static_icons)
                        total_animated_icons = len(animated_icons)
                      
                        
                        # split the icon lists into smaller lists of 25 elements or less (to save space and prevent character limit error from occurring)
                        static_icon_lists = [static_icons[i:i+15] for i in range(0, len(static_icons), 15)]
                        animated_icon_lists = [animated_icons[i:i+15] for i in range(0, len(animated_icons), 15)]


                        if self.iconlinks:
                            embed_description = f"> The following lists contain the custom iconography defined for this guild and are organized by static and animated icons.\n> You may use use the links (icon names) next to each icon in the list to navigate directly to the image for download, if you desire.\n> \n> *Total static icons:* ***{total_static_icons}***\n> *Total animated icons:* ***{total_animated_icons}***"
                        else:
                            embed_description = f"> The following lists contain the custom iconography defined for this guild and are organized by static and animated icons.\n> *Total static icons:* ***{total_static_icons}***\n> *Total animated icons:* ***{total_animated_icons}***"

                      
                        #remake the embed with the new updates
                        icon_embed = discord.Embed(title=f"{self.ctx.guild.name}\nIconography", description=embed_description, color=discord.Color.from_rgb(130, 130, 130))
                        
                        # add each static icon list as a separate field in the embed
                        for i, icon_list in enumerate(static_icon_lists):
                            icon_embed.add_field(name=f"Static Icons {i+1}", value="\n".join(icon_list), inline=False)
                        
                        # add each animated icon list as a separate field in the embed
                        for i, icon_list in enumerate(animated_icon_lists):
                            icon_embed.add_field(name=f"Animated Icons {i+1}", value="\n".join(icon_list), inline=False)
                        
                        # set thumbnail to emoji guy raising tophat
                        icon_embed.set_thumbnail(url="https://i.imgur.com/pfRNFyk.gif")
    
                        # update the message that appears over the embed to notify the user of additon
                        embed_message = f"***{file_name}*** has been successfully added to the iconography list!"
    
    
                        # check if the user has the necessary permissions to edit the embed sent to everybody
                        if await self.bot.is_owner(self.ctx.author) or self.ctx.author.guild_permissions.administrator:
                            #edit the embed to reflect the addition

                            #re-enable the add and remove icon buttons when timed out
                            for child in self.children: #leave cancel button alone
                                if child.label == "Cancel":
                                    pass
                                else:
                                    child.disabled = False

                          
                            await self.message.edit(content=embed_message, embed=icon_embed, view=self)
                
                    except Exception as e: #error handling
                        await self.ctx.respond(f"Apologies {interaction.user.mention},\nI was unable to retrieve the iconography for {self.ctx.guild.name}.", ephemeral=True)
                        print(f"An iconography error occurred: {e}")

                        #re-enable the add and remove icon buttons when timed out
                        for child in self.children: #leave cancel button alone
                            if child.label == "Cancel":
                                pass
                            else:
                                child.disabled = False

                        await self.message.edit(content="", view=self) #update the changes of the enable buttons in the view
                      
                        return

                except discord.HTTPException: #name was too long or wrong syntax
                    await self.ctx.respond(f"Apologies {interaction.user.mention},\nThe file name does not have the correct syntax.\nPlease consider shortening the name to 2 words or less with no spaces, removing unnecessary characters, or removing spaces and *try again*.\n\nUse the following documentation for more information on this issue:\n[Icon Syntax Documentation](<https://discord.com/blog/beginners-guide-to-custom-emojis#:~:text=Any%20emoji%20uploaded%20to%20your,go%20ahead%20and%20compress%20it.>)", ephemeral=True) #add <> around link to prevent preview from showing

                    #re-enable the add and remove icon buttons when timed out
                    for child in self.children: #leave cancel button alone
                        if child.label == "Cancel":
                            pass
                        else:
                            child.disabled = False

                    await self.message.edit(content="", view=self) #update the changes of the enable buttons in the view
                  

              
                except Exception as e: #error handling
                    await self.ctx.respond(f"Apologies {interaction.user.mention},\nI was unable to add that icon.\n*Please try again.*", ephemeral=True)
                    print(f"An add icon error occurred: {e}")

                    #re-enable the add and remove icon buttons when timed out
                    for child in self.children: #leave cancel button alone
                        if child.label == "Cancel":
                            pass
                        else:
                            child.disabled = False

                    await self.message.edit(content="", view=self) #update the changes of the enable buttons in the view
          
      
            else: #user did not have necessary permissions to use button
                await interaction.response.send_message(content=f"Apologies {interaction.user.mention},\nOnly the person who initiated this directive or an administrator is permitted add an icon.", ephemeral=True)



        #add remove emoji button
        @discord.ui.button(label="Remove Iconography", style=discord.ButtonStyle.danger, emoji="❌")
        async def remove_icon_button_callback(self, button, interaction):      
            # only allow author or administrator to remove icons
            if await self.bot.is_owner(self.ctx.author) or self.ctx.author.guild_permissions.administrator:
      
                await interaction.response.defer() #acknowledge the interaction and tell the bot to wait for a response
                    

                #begin waiting for an emoji name from the user (timeout after 30 seconds)
                try:
                    #disable the add and remove icon buttons when done waiting
                    for child in self.children: #leave cancel button alone
                        if child.label == "Cancel":
                            pass
                        else:
                            child.disabled = True

                    await self.message.edit(content=f"{interaction.user.mention}\nPlease enter the name of the icon you would like to remove directly into the chat box below:", view=self) #update the changes of the disable buttons in the view
                  
                    message = await self.bot.wait_for("message", check=lambda m: m.author == interaction.user and m.channel == self.ctx.channel, timeout=120.0)

                except asyncio.TimeoutError:
                    try: #check if the list has not been cancelled
                        await self.ctx.channel.fetch_message(self.message.id)

                        #re-enable the add and remove icon buttons when timed out
                        for child in self.children: #leave cancel button alone
                            if child.label == "Cancel":
                                pass
                            else:
                                child.disabled = False

                        await self.message.edit(content="", view=self) #update the changes of the enable buttons in the view
                      
                        await self.ctx.respond(f"Apologies {interaction.user.mention},\nIt appears you took too long to enter the icon name.\n*Please try again.*", ephemeral=True)
                        return
                  
                    except discord.NotFound:
                        # The icon list has been cancelled
                        return

                #attempt to retrieve the message content
                try:
                    icon_name = message.content

                    await message.delete() #delete the user message
                except Exception:
                    await self.ctx.respond(f"Apologies {interaction.user.mention},\nThe message must contain a valid icon name.\n*Please try again.*", ephemeral=True)
                    # print(f"Delete icon error: {e}")


                    #re-enable the add and remove icon buttons when done waiting
                    for child in self.children: #leave cancel button alone
                        if child.label == "Cancel":
                            pass
                        else:
                            child.disabled = False

                    await self.message.edit(content="", view=self) #update the changes of the enable buttons in the view
                  
                    await message.delete()
                    return

                #retrieve the emoji list and delete the emoji
                try:
                    # get the emoji object from the server
                    found_match = False
                    for icon in self.ctx.guild.emojis:
                        if icon.name.lower() == icon_name.lower(): #check if the name is valid
                            found_match = True
                            # delete the emoji
                            await icon.delete()

                            #begin updating the embed to reflect the removal
                            try:
                                icons = self.ctx.guild.emojis
                            
                                static_icons = []
                                animated_icons = []
                                for icon in icons:
                                    if icon.animated: #animated emojis
                                        if self.iconlinks:
                                            animated_icons.append(f"{icon} - [{icon.name}]({icon.url})")
                                        else:
                                            animated_icons.append(f"{icon} - {icon.name}")
                                    else: #static emojis
                                        if self.iconlinks:
                                            static_icons.append(f"{icon} - [{icon.name}]({icon.url})")
                                        else:
                                            static_icons.append(f"{icon} - {icon.name}")
                    
                                # get the total number of static and animated icons
                                total_static_icons = len(static_icons)
                                total_animated_icons = len(animated_icons)
                              
                                
                                # split the icon lists into smaller lists of 25 elements or less
                                static_icon_lists = [static_icons[i:i+25] for i in range(0, len(static_icons), 25)]
                                animated_icon_lists = [animated_icons[i:i+25] for i in range(0, len(animated_icons), 25)]


                                if self.iconlinks:
                                    embed_description = f"> The following lists contain the custom iconography defined for this guild and are organized by static and animated icons.\n> You may use use the links (icon names) next to each icon in the list to navigate directly to the image for download, if you desire.\n> \n> *Total static icons:* ***{total_static_icons}***\n> *Total animated icons:* ***{total_animated_icons}***"
                                else:
                                    embed_description = f"> The following lists contain the custom iconography defined for this guild and are organized by static and animated icons.\n> *Total static icons:* ***{total_static_icons}***\n> *Total animated icons:* ***{total_animated_icons}***"

                              
                                #create the updated embed that reflects the removal
                                icon_embed = discord.Embed(title=f"{self.ctx.guild.name}\nIconography", description=embed_description, color=discord.Color.from_rgb(130, 130, 130))
                                
                                # add each static icon list as a separate field in the embed
                                for i, icon_list in enumerate(static_icon_lists):
                                    icon_embed.add_field(name=f"Static Icons {i+1}", value="\n".join(icon_list), inline=False)
                                
                                # add each animated icon list as a separate field in the embed
                                for i, icon_list in enumerate(animated_icon_lists):
                                    icon_embed.add_field(name=f"Animated Icons {i+1}", value="\n".join(icon_list), inline=False)
                                
                                # set thumbnail to emoji guy raising tophat
                                icon_embed.set_thumbnail(url="https://i.imgur.com/pfRNFyk.gif")
            
                                #change the message that appears above the embed to reflect the removal
                                embed_message = f"***{icon_name}*** has been successfully removed from the iconography list!"
            
            
                                # check if the user has the necessary permissions to edit the embed sent to everybody
                                if await self.bot.is_owner(self.ctx.author) or self.ctx.author.guild_permissions.administrator:
                                    await self.message.edit(content=embed_message, embed=icon_embed, view=self)

                                    #re-enable the add and remove icon buttons when done waiting
                                    for child in self.children: #leave cancel button alone
                                        if child.label == "Cancel":
                                            pass
                                        else:
                                            child.disabled = False

                                    await self.message.edit(view=self) #update the changes of the enable buttons in the view
                        
                            except Exception as e: #error handling
                                await self.ctx.respond(f"Apologies {interaction.user.mention},\nI was unable to retrieve the iconography for {self.ctx.guild.name}.", ephemeral=True)


                                #re-enable the add and remove icon buttons when timed out
                                for child in self.children: #leave cancel button alone
                                    if child.label == "Cancel":
                                        pass
                                    else:
                                        child.disabled = False
        
                                await self.message.edit(content="", view=self) #update the changes of the enable buttons in the view

                              
                                print(f"An iconography error occurred: {e}")
                                return
                          
                            # let the user know the emoji was removed
                            await self.message.edit(content=f"***{icon_name}*** has been successfully removed from the iconography list, good sir.")
                            break

                      
                    if found_match is False: #icon name not found
                        await self.ctx.respond(f"Apologies {interaction.user.mention},\nThe message must contain a valid icon name.\n*Please try again.*", ephemeral=True)
                        #re-enable the add and remove icon buttons when done waiting
                        for child in self.children: #leave cancel button alone
                            if child.label == "Cancel":
                                pass
                            else:
                                child.disabled = False
    
                        await self.message.edit(content="", view=self) #update the changes of the enable buttons in the view
                        return





              
                except Exception as e: #error handling
                    await self.ctx.respond(f"Apologies {interaction.user.mention},\nI was unable to remove that icon.\n*Please try again.*", ephemeral=True)
                    print(f"A remove icon error occurred: {e}")

                    #re-enable the add and remove icon buttons when done waiting
                    for child in self.children: #leave cancel button alone
                        if child.label == "Cancel":
                            pass
                        else:
                            child.disabled = False

                    await self.message.edit(content = "", view=self) #update the changes of the enable buttons in the view

          
            else: #user did not have permissions to use the button
                await interaction.response.send_message(content=f"Apologies {interaction.user.mention},\nOnly the person who initiated this directive or an administrator is permitted add an icon.", ephemeral=True)



      
        #add a way to close the message
        @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="🚫")
        async def cancel_button_callback(self, button, interaction):

            #only allow author or admin to close the message
            if await self.bot.is_owner(self.ctx.author) or self.ctx.author.guild_permissions.administrator:
                await self.message.edit(content="Now storing your iconography, good sir...", embed=None, view=None) #remove view and embed and only show message content
                await asyncio.sleep(5)
                
                self.stop() #disable the buttons
                await self.message.delete() #delete the message
            else: #user did not have permissions to use the button
                await interaction.response.send_message(content=f"Apologies {interaction.user.mention},\nOnly the person who initiated this directive or an administrator is permitted to close this interaction.", ephemeral=True)




    #initiates the emoji embed and settings
    @discord.slash_command(
        name="iconography",
        description="Receive a list of this guild's iconography.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def iconography(self, ctx, iconlinks: Option(bool, name="iconlinks", description="Provide the links for each icon to provide download capability. (Default: True)", required=False, default=True)):
        #retrieve the emojis
        try:
            icons = ctx.guild.emojis
            if not icons:
                await ctx.respond(f"Apologies {ctx.author.mention},\n{ctx.guild.name} has no custom iconography.", ephemeral=True)
                return
        
            static_icons = []
            animated_icons = []
            for icon in icons:
                if icon.animated: #animated emojis
                    if iconlinks:
                        animated_icons.append(f"{icon} - [{icon.name}]({icon.url})")
                    else:
                        animated_icons.append(f"{icon} - {icon.name}")
                else: #static emojis
                    if iconlinks:
                        static_icons.append(f"{icon} - [{icon.name}]({icon.url})")
                    else:
                        static_icons.append(f"{icon} - {icon.name}")

            # get the total number of static and animated icons
            total_static_icons = len(static_icons)
            total_animated_icons = len(animated_icons)

            if iconlinks:
                embed_description = f"> The following lists contain the custom iconography defined for this guild and are organized by static and animated icons.\n> You may use use the links (icon names) next to each icon in the list to navigate directly to the image for download, if you desire.\n> \n> *Total static icons:* ***{total_static_icons}***\n> *Total animated icons:* ***{total_animated_icons}***"
            else:
                embed_description = f"> The following lists contain the custom iconography defined for this guild and are organized by static and animated icons.\n> *Total static icons:* ***{total_static_icons}***\n> *Total animated icons:* ***{total_animated_icons}***"

            
            
            # split the icon lists into smaller lists of 25 elements or less
            static_icon_lists = [static_icons[i:i+25] for i in range(0, len(static_icons), 25)]
            animated_icon_lists = [animated_icons[i:i+25] for i in range(0, len(animated_icons), 25)]
            
            icon_embed = discord.Embed(title=f"{ctx.guild.name}\nIconography", description=embed_description, color=discord.Color.from_rgb(130, 130, 130))
            
            # add each static icon list as a separate field in the embed
            for i, icon_list in enumerate(static_icon_lists):
                icon_embed.add_field(name=f"Static Icons {i+1}", value="\n".join(icon_list), inline=False)
            
            # add each animated icon list as a separate field in the embed
            for i, icon_list in enumerate(animated_icon_lists):
                icon_embed.add_field(name=f"Animated Icons {i+1}", value="\n".join(icon_list), inline=False)
            
            # set thumbnail to emoji guy raising tophat
            icon_embed.set_thumbnail(url="https://i.imgur.com/pfRNFyk.gif")

            #define the button view class and pass in context, the bot object, and the current iconlinks setting
            view = self.IconView(ctx, self.bot, iconlinks)
          
            # check if the user has the necessary permissions to send the embed to everybody
            if await self.bot.is_owner(ctx.author) or ctx.author.guild_permissions.administrator:
                await ctx.respond(embed=icon_embed, view=view) #send embed to everyone with buttons included
            else:
                await ctx.respond(embed=icon_embed, ephemeral=True) #only self can see the message
    
        except Exception as e: #error handling
            await ctx.respond(f"Apologies {ctx.author.mention},\nI was unable to retrieve the iconography for {ctx.guild.name}.", ephemeral=True)
            print(f"An iconography error occurred: {e}")
            return

#################################EMOJIS#######################################


  


##################################GIVEAWAYS###################################
    class GiveawayView(discord.ui.View):
        def __init__(self, ctx, bot, prize, duration, winners, color_r, color_g, color_b, participation, image):
            super().__init__() #used to initialize the timeout (if needed)
            self.ctx = ctx #initialize the context
            self.duration = duration #initialize the duration of the giveaway
            self.prize = prize #initialize the prize
            self.winners = winners #initialize the number of winners
            self.timer = None
            self.participants = [] #initialize the participant list
            self.color_r = color_r #initialize the embed red color
            self.color_g = color_g #initialize the embed green color
            self.color_b = color_b #initialize the embed blue color
            self.bot = bot #initialize the bot user
            self.participation = participation #initialize the participation (whether the member count needs to be reached or not)
            self.image = image #initialize the image file attachment

        #don't do anything when the timeout is reached
        async def on_timeout(self):
            pass
          
      
        #create the giveaway button
        @discord.ui.button(label="Join prize drawing", style=discord.ButtonStyle.primary, emoji="🎁")
        async def giveawaybutton_callback(self, button, interaction): #when the button is clicked
            #perform a check on the interaction (returns true if all checks are passed)
            interaction_message = await self.join_giveaway_check(interaction)

            if interaction_message is True:
                #add user to the list
                self.participants.append(interaction.user.display_name)
                await interaction.response.send_message(f"Congratulations {interaction.user.mention}!\nYou have been entered into the prize drawing for *{self.prize}*.", ephemeral=True)
            else:
                pass


        #create the END giveaway button
        @discord.ui.button(label="End Prize Drawing", style=discord.ButtonStyle.secondary, emoji="🛑")
        async def end_giveawaybutton_callback(self, button, interaction):
            # Check if the user who clicked the button is the author of the original message or an administrator
            if interaction.user == self.ctx.author or interaction.user.guild_permissions.administrator:
                self.duration = 0
                await self.giveaway_end()
            else:
                await interaction.response.send_message(f"Apologies {interaction.user.mention},\nOnly the individual who initiated the prize drawing or an administrator may end the prize drawing, good sir.", ephemeral=True)




      
        #check if the following are true for the giveaway
        async def join_giveaway_check(self, interaction):
            #author and bots cannot enter the giveaway
            if interaction.user == self.ctx.author or interaction.user.bot:
                await interaction.response.send_message(f"Apologies {interaction.user.mention},\nYou initiated this prize drawing.\nOnly participants may join the prize drawing for *{self.prize}*.", ephemeral=True)
                return False

            #cannot enter giveaway more than once
            elif interaction.user.display_name in self.participants:
                await interaction.response.send_message(f"Apologies {interaction.user.mention},\nYou have already joined the prize drawing for *{self.prize}*.", ephemeral=True)
                return False

            #user pass all checks, enter giveaway
            return True




      
      
        #start the countdown timer for the giveaway
        async def start_timer(self):
            while self.duration >= 0:        
                # Calculate the remaining time in days, hours, minutes, and seconds
                days, remainder = divmod(self.duration, 86400)
                hours, remainder = divmod(remainder, 3600)
                minutes, seconds = divmod(remainder, 60)
        
                # Format the countdown string
                if days > 0:
                    countdown = f"{days:02d}d:{hours:02d}h:{minutes:02d}m:{seconds:02d}s"
                elif hours > 0:
                    countdown = f"{hours:02d}h:{minutes:02d}m:{seconds:02d}s"
                elif minutes > 0:
                    countdown = f"{minutes:02d}m:{seconds:02d}s"
                else:
                    countdown = f"{seconds}s"


                #update the description of the embed depending on if winner count needs to be reached or not
                if self.participation is False:
                    participation_message = f"A prize drawing has begun!\nPlease find the details attached below and utilize the join button to participate, if you desire...\n\nIf the number of participants *does not exceed* the winner count ({self.winners}), the prize will be awarded to all participants."
                else:
                    participation_message = f"A prize drawing has begun!\nPlease find the details attached below and utilize the join button to participate, if you desire...\n\nThe number of participants must reach the winner count ({self.winners}) for the prize to be awarded."

              
                # Modify the embed with the remaining time
                giveaway_embed = discord.Embed(title="__Prize Drawing__", description=participation_message, color=discord.Color.from_rgb(self.color_r, self.color_g, self.color_b))
                giveaway_embed.add_field(name="Ending In", value=f"`{countdown}`", inline = False)
                giveaway_embed.add_field(name="Number of Winners", value=self.winners, inline=False)
                giveaway_embed.add_field(name="Prize", value=self.prize, inline=False)
                giveaway_embed.set_footer(text=f"Initiated by: {self.ctx.author.display_name}")
              
                #set thumbnail to avatar url (unless they dont have one, then set it to bot's url)
                try:
                    giveaway_embed.set_thumbnail(url=self.ctx.author.avatar.url)
                except:
                    giveaway_embed.set_thumbnail(url=self.bot.user.avatar.url)

                if self.image:
                    giveaway_embed.set_image(url=self.image.url)
              
                await self.message.edit(embed=giveaway_embed, view=self)
        
                await asyncio.sleep(1)
                self.duration -= 1

            #await the end giveaway command
            await self.giveaway_end()

        
      
        #Timeout message (when giveaway ends)
        async def giveaway_end(self):
            for child in self.children: #disable all buttons
                child.disabled = True


            # Select the winner(s)
            if self.participation is True: #the member count must be reached
                if len(self.participants) < self.winners:
                    winner_list = []
                    winner_message = f"It appears that there were not enough participants to select {self.winners} winner(s).\nUnfortunately, nobody has received *{self.prize}*..."
                else:
                    winner_list = random.sample(self.participants, self.winners)
                    winner_mention_list = [f"<@{self.ctx.guild.get_member_named(name).id}>" for name in winner_list]
                    winner_message = "Congratulations are in order for the following prestigious individual(s):\n" + "\n".join(winner_mention_list)

            else: #the member count does not have to be reached
                if len(self.participants) == 0:
                    winner_list = []
                    winner_message = f"It appears that there were no participants for the prize drawing.\nUnfortunately, nobody has received *{self.prize}*..."
                else:
                    if len(self.participants) < self.winners:
                        winner_list = self.participants
                    else:
                        winner_list = random.sample(self.participants, self.winners)

                  
                    winner_mention_list = [f"<@{self.ctx.guild.get_member_named(name).id}>" for name in winner_list]
                    winner_message = "Congratulations are in order for the following prestigious individuals:\n" + "\n".join(winner_mention_list)             



            # Get the time now and localize it to US/Central time
            target_tz = pytz.timezone('US/Central')
            now = datetime.datetime.now()
            time = now.astimezone(target_tz)
            end_time = time.strftime("%A %B %d, %Y %I:%M:%S %p %Z")


            #send the winner list and embed
            giveaway_embed = discord.Embed(title="__Prize Drawing__", description="A prize drawing has ended!\nNow selecting the winner(s)...", color=discord.Color.from_rgb(self.color_r, self.color_g, self.color_b))
            giveaway_embed.add_field(name="Ending In", value="`COMPLETE`", inline = False)
            giveaway_embed.add_field(name="Number of Winners", value=self.winners, inline=False)
            giveaway_embed.add_field(name="Prize", value=self.prize, inline=False)
            giveaway_embed.set_footer(text=f"Initiated by: {self.ctx.author.display_name}")
          
            #set thumbnail avatar url (unless they dont have one, then set it to bot's url)
            try:
                giveaway_embed.set_thumbnail(url=self.ctx.author.avatar.url)
            except:
                giveaway_embed.set_thumbnail(url=self.bot.user.avatar.url)

            if self.image:
                giveaway_embed.set_image(url=self.image.url)
          
            await self.message.edit(embed=giveaway_embed, view=None)
          
            await asyncio.sleep(5)


            #set the winner embed with information
            winner_embed = discord.Embed(title="__Prize Drawing Winner(s)__", description = "Thank you all for participating in this prize drawing. The winner(s) are listed above and the award information may be found below.\n*Enjoy!*", color=discord.Color.from_rgb(self.color_r, self.color_g, self.color_b))
            winner_embed.add_field(name = "Ended", value=f"`{end_time}`", inline=False)
            winner_embed.add_field(name="Number of Winners", value=len(winner_list) if len(winner_list)>0 else "None", inline = False)
            winner_embed.add_field(name="Prize", value=f"{self.prize}", inline = False)
            winner_embed.set_footer(text=f"Initiated by: {self.ctx.author.display_name}")

            #set thumbnail to exquisite emoji
            winner_embed.set_thumbnail(url="https://i.imgur.com/UHfZkeT.gif")

            if self.image:
                winner_embed.set_image(url=self.image.url)
          
            await self.message.edit(content=winner_message, embed=winner_embed, view=None)

            self.stop()



    #giftgiving command to initiate the giveaways
    @discord.slash_command(
        name="giftgiving",
        description="Permit the automaton to arrange a prize drawing for an item of your preference. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def giftgiving(
        self, 
        ctx,
        *, prize: Option(str, name="prize", description="Prize being gifted to the user(s)."),
        duration: Option(str, name="duration", description="How long the prize drawing will last. (Example: 1d, 1h, 1m, 1s)"),
        winners: Option(int, name="winners", description="The amount of people who will be receiving the prize.", min_value=1, max_value=20),
        participation: Option(bool, name = "participation", description="Winner count (winners) must be reached to award prize to active participants. (Default: True)", required=False, default = True),
        color: Option(str, name="color", description="Select a color for the prize drawing embed. (Default: 🔵 Blue)", required=False, choices=["🔴 Red", "🟢 Green", "🔵 Blue", "🟡 Yellow", "🟣 Purple", "⚫ Black", "⚪ White"], default=None),
        image: Option(discord.Attachment, name="image", dewscription="Image for the prize drawing. (Default: None)", required=False, default=None)
    ):

        #only allow admins to initiate giveaways
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

        #winner count must be between 1 and 20 total
        if winners < 1:
            await ctx.respond(f"Apologies {ctx.author.mention},\You must have at least one winner for this prize drawing.\n*Please try again.*", ephemeral=True)
            return
        elif winners > 20:
            await ctx.respond(f"Apologies {ctx.author.mention},\You may not have more than 20 participants in this prize drawing.\n*Please try again.*", ephemeral=True)
            return
        

        #define RGB image text color tuples
        colors = {
            "🔴 Red": (255, 0, 0),
            "🟢 Green": (0, 255, 0),
            "🔵 Blue": (0, 0, 255),
            "🟡 Yellow": (255, 255, 0),
            "🟣 Purple": (152, 3, 252),
            "⚫ Black": (0, 0, 0),
            "⚪ White": (255, 255, 255)
        }        
    
        if color is not None:
            if color in colors:
                color_r = colors[color][0]
                color_g = colors[color][1]
                color_b = colors[color][2]
            else:
                await ctx.respond(f"**Error**\n*{color}* is not a viable option, good sir.\n*Please try again.*", ephemeral=True)
        else: #default blue
            color_r = 0
            color_g = 0
            color_b = 255


        # Parse the duration string to calculate the total duration in seconds
        duration_seconds = 0
        match = re.findall(r"(\d+)([dhms])", duration)
        if match:
            for value, unit in match:
                if unit == "d":
                    duration_seconds += int(value) * 86400
                elif unit == "h":
                    duration_seconds += int(value) * 3600
                elif unit == "m":
                    duration_seconds += int(value) * 60
                elif unit == "s":
                    duration_seconds += int(value)



        #if the duration is not input correctly or the duration is input as 0s
        if duration_seconds == 0:
            await ctx.respond(f"Apologies {ctx.author.mention},\nThe prize drawing duration must be greater than 0 seconds.\n\n__Note:__ You must insert a time string after the time integer (i.e. 1d = 1 day, 1h = 1 minute, 1m = 1 minute, 1s = 1 second).\n*Please try again.*", ephemeral=True)
            return
      
        # Calculate the remaining time in days, hours, minutes, and seconds
        days, remainder = divmod(duration_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Format the countdown string
        if days > 0:
            countdown = f"{days:02d}d:{hours:02d}h:{minutes:02d}m:{seconds:02d}s"
        elif hours > 0:
            countdown = f"{hours:02d}h:{minutes:02d}m:{seconds:02d}s"
        elif minutes > 0:
            countdown = f"{minutes:02d}m:{seconds:02d}s"
        else:
            countdown = f"{seconds}s"


        #update the description of the embed depending on if winner count needs to be reached or not
        if participation is False:
            participation_message = f"A prize drawing has begun!\nPlease find the details attached below and utilize the join button to participate, if you desire...\n\nIf the number of participants *does not exceed* the winner count ({winners}), the prize will be awarded to all participants."
        else:
            participation_message = f"A prize drawing has begun!\nPlease find the details attached below and utilize the join button to participate, if you desire...\n\nThe number of participants must reach the winner count ({winners}) for the prize to be awarded."

      

        giveaway_embed = discord.Embed(title="__Prize Drawing__", description = participation_message, color=discord.Color.from_rgb(color_r, color_g, color_b))
        giveaway_embed.add_field(name="Ending In", value=f"`{countdown}`", inline = False)
        giveaway_embed.add_field(name="Number of Winners", value=winners, inline = False)
        giveaway_embed.add_field(name="Prize", value=prize, inline = False)
        giveaway_embed.set_footer(text=f"Initiated by: {ctx.author.display_name}")

        #set thumbnail avatar url (unless they dont have one, then set it to bot's url)
        try:
            giveaway_embed.set_thumbnail(url=ctx.author.avatar.url)
        except:
            giveaway_embed.set_thumbnail(url=self.bot.user.avatar.url)


        if image:
            picture_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            file_extension = os.path.splitext(image.filename)[1].lower()

            if file_extension in picture_extensions:
                giveaway_embed.set_image(url=image.url)
            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that *{image.filename}* is not a valid picture file. This file must be a JPG, JPEG, PNG, or GIF.\n*Pleae try again.*", ephemeral=True)
                return

        #define the view of the embed message (to add buttons)
        view = self.GiveawayView(ctx, self.bot, prize, duration_seconds, winners, color_r, color_g, color_b, participation, image)
        await ctx.respond(embed=giveaway_embed, view = view) #send embed with button view
        await view.start_timer() #start the countdown timer (defined in the GiveawayView Class)

##################################GIVEAWAYS###################################










  

###############################WEATHER#################################


############### free plan API usage = 1,000,000 calls per month

    # https://www.weatherapi.com/
    @discord.slash_command(
        name="weather",
        description="Allow the automaton to retrieve the weather data for your location of choice.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def weather(self, ctx, *, city: Option(str, name="city", description="City to receive weather data for. (Can include location's state)"), visible: Option(bool, name="visible", description="Make weather information visible to everyone. (Default: False - to provide location privacy)", required=False, default=False)):

        ##### PATRON FEATURE (always available in support guild)
        # server ID for The Sweez Gang
        support_guild_id = 1088118252200276071

        if ctx.guild.id != support_guild_id:
            if not patrons_db.patrons.find_one({"server_id": ctx.guild.id}):
                patron_embed = discord.Embed(title="Patron Feature Directive", description=f"Apologies {ctx.author.mention},\n`/weather` is an exclusive feature available solely to patrons and is not currently in use for ***{ctx.guild.name}***, good sir.\n\nPlease use my `/patron` directive to learn more information on enabling patron (premium) features for ***{ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(130, 130, 130))
    
                patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
    
                await ctx.respond(embed=patron_embed, ephemeral=True)
                return


      
        # weather_api_key = os.environ['WeatherAPIKey']
        weather_api_key = os.getenv('WeatherAPIKey')
        current_url = "http://api.weatherapi.com/v1/current.json"
        params = {
          "key": weather_api_key,
          "q": city
        }

        try:
            # make the request to the weather API
            response = requests.get(current_url, params=params)
            
            if not response.ok:
                await ctx.respond(f"Apologies {ctx.author.mention},\nI was unable to retrieve the weather data for **{city}**.\n*Please try again.*", ephemeral=True)
                return
        
            data = response.json()
            # print(json.dumps(data, indent=4))
    
            #colors for different weather conditons from weatherapi
            color_dict = {
                "Sunny": (255, 255, 0), # yellow
                "Clear": (0, 0, 139), #dark shade of blue (midnight blue)
                "Partly cloudy": (255, 255, 128), # light yellow
                "Cloudy": (192, 192, 192), # light gray
                "Overcast": (128, 128, 128), # dark gray
                "Mist": (211, 211, 211), # light gray
                "Patchy rain possible": (135, 206, 250), # light blue
                "Patchy snow possible": (192, 192, 192), # light gray
                "Patchy sleet possible": (192, 192, 192), # light gray
                "Patchy freezing drizzle possible": (135, 206, 250), # light blue
                "Thundery outbreaks possible": (255, 255, 0), # yellow
                "Blowing snow": (255, 250, 250), # snow white
                "Blizzard": (255, 250, 250), # snow white
                "Fog": (192, 192, 192), # light gray
                "Freezing fog": (192, 192, 192), # light gray
                "Patchy light drizzle": (135, 206, 250), # light blue
                "Light drizzle": (135, 206, 250), # light blue
                "Freezing drizzle": (192, 192, 192), # light gray
                "Heavy freezing drizzle": (192, 192, 192), # light gray
                "Patchy light rain": (135, 206, 250), # light blue
                "Light rain": (135, 206, 250), # light blue
                "Moderate rain at times": (0, 191, 255), # sky blue
                "Moderate rain": (0, 191, 255), # sky blue
                "Heavy rain at times": (25, 25, 112), # midnight blue
                "Heavy rain": (25, 25, 112), # midnight blue
                "Light freezing rain": (192, 192, 192), # light gray
                "Moderate or heavy freezing rain": (192, 192, 192), # light gray
                "Light sleet": (192, 192, 192), # light gray
                "Moderate or heavy sleet": (192, 192, 192), # light gray
                "Patchy light snow": (211, 211, 211), # light gray
                "Light snow": (211, 211, 211), # light gray
                "Patchy moderate snow": (255, 250, 250), # snow white
                "Moderate snow": (255, 250, 250), # snow white
                "Patchy heavy snow": (255, 250, 250), # snow white
                "Heavy snow": (255, 250, 250), # snow white
                "Ice pellets": (192, 192, 192), # light gray
                "Light rain shower": (135, 206, 250), # light blue
                "Moderate or heavy rain shower": (0, 191, 255), # sky blue
                "Torrential rain shower": (25, 25, 112), # midnight blue
                "Light sleet showers": (192, 192, 192), # light gray
                "Moderate or heavy sleet showers": (192, 192, 192), # light gray
                "Light snow showers": (211, 211, 211), # light gray
                "Moderate or heavy snow showers": (255, 250, 250), # snow white
                "Light showers of ice pellets": (192, 192, 192), # light gray
                "Moderate or heavy showers of ice pellets": (192, 192, 192), # light gray
                "Patchy light rain with thunder": (255, 255, 0), # yellow
                "Moderate or heavy rain with thunder": (255, 255, 0), # yellow
                "Patchy light snow with thunder": (211, 211, 211), # light gray
                "Moderate or heavy snow with thunder": (255, 250, 250) # snow white
                }
    
            condition = data['current']['condition']['text']
            if condition in color_dict:
                weather_color = color_dict[condition]
            else:
                weather_color = discord.Color.blurple().to_rgb()
    
          
            # create a fancy embed with the weather data
            embed = discord.Embed(title=f"Current Weather\n{data['location']['name']}, {data['location']['region']}", color=discord.Color.from_rgb(*weather_color))
            embed.add_field(name="Temperature", value=f"{data['current']['temp_f']}°F\n({data['current']['temp_c']}°C)")
            embed.add_field(name="Feels Like", value=f"{data['current']['feelslike_f']}°F\n({data['current']['feelslike_c']}°C)")
            embed.add_field(name="Condition", value=data['current']['condition']['text'])
            embed.add_field(name="Precipitation", value=f"{data['current']['precip_in']} in\n({data['current']['precip_mm']} mm)")
            embed.add_field(name="Wind Speed", value=f"{data['current']['wind_mph']} mph {data['current']['wind_dir']}\n({data['current']['wind_kph']} kph {data['current']['wind_dir']})")
            embed.add_field(name="Pressure", value=f"{data['current']['pressure_mb']} mb\n({data['current']['pressure_in']} inHg)")
            embed.add_field(name="Humidity", value=f"{data['current']['humidity']}%")
            embed.add_field(name="UV Index", value=f"{data['current']['uv']}")
            embed.add_field(name="Cloud Cover", value=f"{data['current']['cloud']}%")
            embed.add_field(name="Visibility", value=f"{data['current']['vis_miles']} miles\n({data['current']['vis_km']} km)")
            embed.add_field(name="Wind Gusts", value=f"{data['current']['gust_mph']} mph\n({data['current']['gust_kph']} km/h)")
            embed.set_thumbnail(url=f"https:{data['current']['condition']['icon']}") #the url always starts with // for some reason, so add https:
    
            date_time = data['current']['last_updated'] #last updated time
            timezone = pytz.timezone(data['location']['tz_id']) #timezone
            timezone_abbr = timezone.localize(datetime.datetime.now()).strftime('%Z')
            date_time = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M')
            date_time = date_time.strftime('%B %d, %Y %I:%M %p')
            embed.add_field(name="Last Updated", value=f"`{date_time} {timezone_abbr}`")
            embed.set_footer(text="Powered by Weather API (weatherapi.com)")
    
            weather_message = f"{ctx.author.mention}, here is your weather information for *{data['location']['name']}, {data['location']['region']}:*"
    
            if visible:
                await ctx.respond(weather_message, embed=embed, ephemeral=False)
            else:
                await ctx.respond(weather_message, embed=embed, ephemeral=True)

        except Exception as e:
            await ctx.respond(f"Apologies {ctx.author.mention},\nI was unable to retrieve your weather information due to an error.\n*Please try again.*", ephemeral=True)
            print(f"Weather error: {e}")
            return
            

#################################WEATHER#################################    



  

################################SPOILERS###################################
    @discord.slash_command(
        name="conceal",
        description="Conceal a message to allow others a chance to avoid content spoilers. (Attachments optional)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def conceal(self, ctx):
        # Get the most recent message by the user
        async for message in ctx.channel.history(limit=1):
            if message.author == ctx.author:
                # Add spoiler tags to the message content, including any attachments or embedded content
                if message.content:
                    spoiler_message = f"||{message.content}"
                else:
                    spoiler_message = "||"
                
                spoiler_images = []
                spoiler_videos = []
                spoiler_files = []
                for attachment in message.attachments:
                    if attachment.content_type.startswith("image"):
                        # If the attachment is an image, add it to the list of spoiler images
                        spoiler_image = await attachment.to_file(spoiler=True)
                        spoiler_images.append(spoiler_image)
                    elif attachment.content_type.startswith("video"):
                        # If the attachment is a video, add it to the list of spoiler videos
                        spoiler_video = await attachment.to_file(spoiler=True)
                        spoiler_videos.append(spoiler_video)
                    else:
                        # If the attachment is not an image or video, add a link to it
                        spoiler_message += f"\n[{attachment.filename}]({attachment.url})"
                        spoiler_file = attachment
                        spoiler_files.append(spoiler_file)

                # if message.embed:
                #     await ctx.respond(f"Apologies {ctx.author.mention},\nConcealment warnings only work for regular messages and their attachments at the moment, not embedded messages.\n*Please consider sending your content without the embed.*", ephemeral=True)
                #     return
              
                
                spoiler_message += "||"
              
                if (spoiler_images or spoiler_videos) and spoiler_files:
                    # Send the edited message with spoiler images and videos
                    await ctx.respond(f"The following has been concealed by {ctx.author.mention} to avoid content spoilers, be wary good fellows:\n{spoiler_message}", files=[*spoiler_images, *spoiler_videos])
                elif (spoiler_images or spoiler_videos) and not spoiler_files:
                    # Send the edited message with spoiler images and videos
                    await ctx.respond(f"The following has been concealed by {ctx.author.mention} to avoid content spoilers, be wary good fellows:", files=[*spoiler_images, *spoiler_videos])
                else:
                    # Send the edited message without spoiler images or videos
                    await ctx.respond(f"The following has been concealed by {ctx.author.mention} to avoid content spoilers:\n{spoiler_message}")

                # Delete the original message
                await message.delete()
                return
    
        # If no recent message by the user was found
        await ctx.respond(f"Dearest {ctx.author.mention},\nIt appears you have not sent any messages recently.\n*Please try again.*\n\n*Note that my `/conceal` directive only works if it is used in direct succession of the message you would like to conceal.*", ephemeral=True)


################################SPOILERS###################################


  

# #################################STARBOARD################################

    #This retrieves the current server's event status from the mongoDB database
    async def get_starboard_event_status(self, guild_id):
        # mongoDBpass = os.environ['mongoDBpass']
        mongoDBpass = os.getenv('mongoDBpass')
        client = pymongo.MongoClient(mongoDBpass)
        event_handler_db = client.event_handler_db

        event_doc = event_handler_db.events.find_one({"server_id": guild_id})
        if event_doc:
            return event_doc["starboard"]
        else:
            return "Enabled"
          
  

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            # Message is not associated with a guild (private message)
            return
      
        if message.flags.ephemeral:
            # print("message is ephemeral")
            return True
          
        message_server = message.guild.id
        # print(message_server)

        #get the starboard event status from mongoDB
        starboard_status = await self.get_starboard_event_status(message_server)
        # print(message_server)


        #Starboard on_message event only runs if event status using /eventhandler is set to enabled OR if the user has not set the status using /eventhandler
        if starboard_status == "Disabled":
            return
        elif starboard_status == "Enabled":
            # Ignore bot messages
            # if message.author.bot:
            #     return
            
            # Get the starboard configuration for the current server
            server_config = starboard_db.starboard_configs.find_one({"server_id": message_server})
            if not server_config:
                return
        
            # Ignore messages in channels that are not being listened to
            if message.channel.id not in server_config["listen_channels_id"]:
                return
            
            # Ignore messages that are already in the starboard
            if server_config["starboard_messages"]:
                if message.id in server_config["starboard_messages"]:
                    return
            
            # Ignore messages where the author has an ignored status
            if server_config["ignored_statuses_id"]:
                for role in message.author.roles:
                    if role.id in server_config["ignored_statuses_id"]:
                        return
    
            
            # Automaton reacts if setting is enabled
            if server_config["automaton_reaction"]:
                #check for the automaton patron tier and reset the configurations to the defaults
                patron_data = patrons_db.patrons
                refined_patron_key = {
                  "server_id": message_server,
                  "patron_tier": "Refined Automaton Patron"
                }
                distinguished_patron_key = {
                  "server_id": message_server,
                  "patron_tier": "Distinguished Automaton Patron"
                }
              
                refined_patron = patron_data.find_one(refined_patron_key)
                distinguished_patron = patron_data.find_one(distinguished_patron_key)
                
                if not refined_patron or not distinguished_patron:
                    reaction = "⭐"
                else:
                    reaction = server_config["reaction"]


                try:
                    await message.add_reaction(reaction)
                except Exception:
                    pass
    
    
          
            await self.listen_for_reactions(message, server_config)
      


    #listen for additional reactions to the message
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        reaction_server = reaction.message.guild.id

        #get the starboard event status from mongoDB
        starboard_status = await self.get_starboard_event_status(reaction_server)  

        #Starboard on_reaction_add event only runs if event status using /eventhandler is set to enabled OR if the user has not set the status using /eventhandler
        if starboard_status == "Disabled":
            return
        elif starboard_status == "Enabled":
            #get the starboard data from mongoDB
            server_config = starboard_db.starboard_configs.find_one({"server_id": reaction_server})
    
            #if the starboard data is not found
            if not server_config:
                # print("server config not found")
                return
    
            #get the list of listening channel IDs
            listen_channels = server_config["listen_channels_id"]

          
            #PATRON FEATURE
            # server ID for The Sweez Gang
            support_guild_id = 1088118252200276071
    
            if reaction_server != support_guild_id:
                #check for the automaton patron tier and reset the configurations to the defaults
                patron_data = patrons_db.patrons
                refined_patron_key = {
                  "server_id": reaction_server,
                  "patron_tier": "Refined Automaton Patron"
                }
                distinguished_patron_key = {
                  "server_id": reaction_server,
                  "patron_tier": "Distinguished Automaton Patron"
                }
              
                refined_patron = patron_data.find_one(refined_patron_key)
                distinguished_patron = patron_data.find_one(distinguished_patron_key)
                
                if not refined_patron or not distinguished_patron:
                    starboard_db.starboard_configs.update_one(
                      {"server_id": reaction_server},
                      {"$set": {
                        "color": [255, 223, 0],
                        "reaction": "⭐"
                        }
                      }
                    )
              
            server_config = starboard_db.starboard_configs.find_one({"server_id": reaction_server})

          
            #if the channel the reaction is added on is not in the listening channels OR
            #if the user adding the reaction is a bot OR
            #if the reaction emoji added is not the same as the defined on on mongoDB
            if reaction.message.channel.id not in listen_channels or user.bot or reaction.emoji != server_config["reaction"]:
                # print(server_config["reaction"])
                # print(f"reaction emoji: {reaction.emoji}")
                # print(f"message channel id: {reaction.message.channel.id}")
                # star_channel_id = server_config["star_channel_id"]
                # print(listen_channels)
                # print(user.bot)
                # print("did not pass criteria")
                return
    
            #await the listen for reactions function below
            await self.listen_for_reactions(reaction.message, server_config)


  
    #listen for reaction event used to add the initial reactions, check additional reactions and send the starboard embeds to the specified star channel
    async def listen_for_reactions(self, message, server_config):
        # print("listening started")
        def check(reaction, user):
            return (
                reaction.emoji == server_config["reaction"]
                and not user.bot
                and reaction.message.id == message.id
            )
          
        # print("listener check passed")


        # Count the author's reaction if the author is not ignored
        if not server_config["ignore_author"]:
            reactions = sum([1 for r in message.reactions if not r.me and not r.bot])
            # print(f"author not ignored: {reactions}")
        else:
            reactions = 0
            # print(f"author ignored: {reactions}")
      
        # Get the updated number of reactions on the message
        updated_message = None
        async for message_in_history in message.channel.history(limit=200):
            if message_in_history.id == message.id:
                updated_message = message_in_history
                # print(f"Updated message: {updated_message}")
                break
        
        if not updated_message:
            # print("Message not found")
            return
  
        
        # Add the reactions to the count
        for reaction in updated_message.reactions:
            if reaction.emoji == server_config["reaction"]:
                reactions += reaction.count
                # print(f"updated reaction count: {reactions}")
                break
    
        # Update the starboard message with the updated number of reactions
        if reactions and reactions >= server_config["threshold"]:
            reaction = server_config["reaction"]
            threshold = server_config["threshold"]
            # print(f"threshold passed: threshold = {threshold}, reactions = {reactions}")
            starboard_channel = await self.bot.fetch_channel(server_config["star_channel_id"])
            # print(f"starboard_channel: {starboard_channel}")
            async for starboard_message in starboard_channel.history(limit=200):
                if starboard_message.embeds and starboard_message.embeds[0].url == message.jump_url:
                    # print("starboard embed check passed")
                    starboard_db.starboard_configs.update_one(
                        {"server_id": message.guild.id, "starboard_messages": message.id},
                        {"$set": {"starboard_messages.$": updated_message.id}}
                    )
                    # print("mongoDB updated with message id")
                    # Update the footer with the new reaction count
                    embed = starboard_message.embeds[0]
                    embed.set_footer(text=f"Maximum Reactions: {reaction} {reactions}")
                    await starboard_message.edit(embed=embed)
                    # print("embed sent")
                    break
            else:
                # If there is no existing starboard embed, create a new one
                starboard_db.starboard_configs.update_one(
                    {"server_id": message.guild.id},
                    {"$push": {"starboard_messages": message.id}}
                )
                # print("mongoDB updated with message id")
                
                if message.embeds:
                    # Get the existing embed from the message
                    existing_embed = message.embeds[0]

                    await starboard_channel.send(embed=existing_embed) #send original embed

                    author_avatar = message.author.avatar
                    embed = discord.Embed(
                        title = "Original Posting (click here)",
                        url = message.jump_url,
                        description="⬆️See embedded message above.⬆️",
                        timestamp=message.created_at,
                        color=discord.Color.from_rgb(*server_config["color"]),
                    )
                    embed.set_author(
                        name=message.author.display_name,
                        icon_url=author_avatar,
                    )
    
                    embed.set_footer(text=f"Maximum Reactions: {reaction} {reactions}")
                    if message.attachments:
                        attachment = message.attachments[0]
                        if attachment.url.lower().endswith(("png", "jpeg", "jpg", "gif", "webp")):
                            embed.set_image(url=attachment.url)
                        else:
                            embed.add_field(name="Attachment", value=f"[{attachment.filename}]({attachment.url})", inline=False)

                else:
                    author_avatar = message.author.avatar
                    embed = discord.Embed(
                        title = "Original Posting (click here)",
                        url = message.jump_url,
                        description=message.content,
                        timestamp=message.created_at,
                        color=discord.Color.from_rgb(*server_config["color"]),
                    )
                    embed.set_author(
                        name=message.author.display_name,
                        icon_url=author_avatar,
                    )
    
                    embed.set_footer(text=f"Maximum Reactions: {reaction} {reactions}")
                    if message.attachments:
                        attachment = message.attachments[0]
                        if attachment.url.lower().endswith(("png", "jpeg", "jpg", "gif", "webp")):
                            embed.set_image(url=attachment.url)
                        else:
                            embed.add_field(name="Attachment", value=f"[{attachment.filename}]({attachment.url})", inline=False)
                await starboard_channel.send(embed=embed)
                # print("embed sent")



    #remove the starboard message from mongoDB if deleted
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.flags.ephemeral:
            # print("message is ephemeral")
            return True
          
        message_server = message.guild.id

        #get the starboard event status from mongoDB
        starboard_status = await self.get_starboard_event_status(message_server)


        #Starboard on_message_delete event only runs if event status using /eventhandler is set to enabled OR if the user has not set the status using /eventhandler
        if starboard_status == "Disabled":
            return
        elif starboard_status == "Enabled":
            # Check if the deleted message is in the starboard_messages array
            starboard_message = starboard_db.starboard_configs.find_one({"server_id": message_server, "starboard_messages": message.id})
            if starboard_message:
                # Remove the deleted message from the starboard_messages array
                starboard_db.starboard_configs.update_one(
                    {"server_id": message.guild.id},
                    {"$pull": {"starboard_messages": message.id}}
                )

  

#################################STARBOARD################################









  
  
###############################WELCOMER#################################
  
    #This retrieves the current server's event status from the mongoDB database
    async def get_welcome_event_status(self, guild_id):
        # mongoDBpass = os.environ['mongoDBpass']
        mongoDBpass = os.getenv('mongoDBpass')
        client = pymongo.MongoClient(mongoDBpass)
        event_handler_db = client.event_handler_db

        event_doc = event_handler_db.events.find_one({"server_id": guild_id})
        if event_doc:
            return event_doc["welcome_messages"]
        else:
            return "Enabled"


  

    #welcome new members event listener
    @commands.Cog.listener()
    async def on_member_join(self, member):
    		#do not welcome bots
        if member.bot:
            return
      
        member_server_id = member.guild.id #retrieve the server ID of where the member is being welcomed

        #get the welcome event status from mongoDB
        welcome_messages_status = await self.get_welcome_event_status(member_server_id)

        #welcome event only runs if event status using /eventhandler is set to enabled OR if the user has not set the status using /eventhandler
        if welcome_messages_status == "Disabled":
            return
        elif welcome_messages_status == "Enabled":
            welcome_key = {"server_id": member_server_id} #key to search through mongoDB with to find the appropriate welcome configuration
          
            #find the welcome config for the server
            welcome_data = welcome_db.welcomeconfig.find_one(welcome_key)
    
            if welcome_data:
                #retrieve required data from the database
                channel_id = welcome_data['channel_id']
                message = welcome_data['message']
                image_text = welcome_data['image_text']
                image_text_color = welcome_data['image_text_color']
                font = welcome_data['font']
                font_size = welcome_data['font_size']
                background = welcome_data['background']
                avatar = welcome_data['avatar']
                avatar_placement = welcome_data['avatar_placement']
                avatar_outline_color = welcome_data['avatar_outline_color']
                on_join_status_id = welcome_data['on_join_status_id']
                on_join_status_name = welcome_data['on_join_status_name']


                # server ID for The Sweez Gang
                support_guild_id = 1088118252200276071

                if member.guild.id != support_guild_id:
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
                        image_text = "Welcome {member.display_name}"
                        image_text_color = [255, 255, 255]
                        background = "https://i.imgur.com/QyT4Pho.jpg"
                        avatar = "{member.avatar}"
                        avatar_outline_color = [255, 255, 255]
              

                #get the bot's nickname from mongoDB
                byname = await self.get_byname(member_server_id)
              
                
                channel = self.bot.get_channel(channel_id)
                if channel is None:
                    return
                    
                message = welcome_data.get('message')
                if message:
                    #add one to the member count
                    member_count = len([m for m in member.guild.members if not m.bot]) + 1
                    message = message.replace("{member_count}", str(member_count))

                  
                    #add the byname of the bot if used
                    message = message.replace("{byname}", str(byname))

                    #add the on_join_status if used
                    if on_join_status_id:
                        message = message.replace("{on_join_status}", str(on_join_status_name))

                        on_join_status_mention = member.guild.get_role(on_join_status_id)
                        message = message.replace("{on_join_status_mention}", on_join_status_mention.mention)
                    else:
                        message = message.replace("{on_join_status}", "")
                        message = message.replace("{on_join_status_mention}", "")
                  
                    message = message.format(member=member)
                else:
                    message = None
                    
                image_text = welcome_data.get('image_text')
                if image_text:
                    #add one to the member count
                    member_count = len([m for m in member.guild.members if not m.bot]) + 1
                    image_text = image_text.replace("{member_count}", str(member_count))

                    #add the byname of the bot if used
                    image_text = image_text.replace("{byname}", str(byname))

                    #add the on_join_status if used
                    if on_join_status_id:
                        image_text = image_text.replace("{on_join_status}", str(on_join_status_name))
                    else:
                        image_text = image_text.replace("{on_join_status}", "")
                  
                    image_text = image_text.format(member=member)
                else:
                    image_text = None
                
                font_path = welcome_data.get('font')
                font_size = welcome_data.get('font_size')
                font = ImageFont.truetype(font_path, font_size)
      
                # print(channel)
                # print(message)
                # print(image_text)
                # print(image_text_color)
                # print(font)
                # print(background)
                # print(avatar)
                # print(avatar_placement)
                # print(avatar_outline_color)
                # print(on_join_status_id)
                # print(on_join_status_name)
    
                # Define the options for avatar placement
                avatar_placements = ['Top Right', 'Top Left', 'Bottom Right', 'Bottom Left', 'Bottom Center', 'Top Center', 'Left', 'Right', 'Center']
    
                if avatar_placement not in avatar_placements:
                    raise ValueError('Invalid avatar placement option')
                    
                # Download the background image
                response = requests.get(background)
                background_image = Image.open(io.BytesIO(response.content))
    
    
                # Calculate the maximum width and total height of the lines
                text_width = 0
                text_height = 0

                if image_text:
                    #split the lines
                    lines = image_text.split('\n')
    
                    line_widths = []
                    for line in lines:
                        line_width, line_height = font.getsize(line)
                        line_widths.append(line_width)  # append each line's width to the array
                        if line_width > text_width:
                            text_width = line_width
                        text_height += line_height
    
                # Resize the background image to fit the avatar and text
                background_width, background_height = background_image.size
                avatar_size = font_size * 3
                avatar_x = background_width // 2 - avatar_size // 2
                avatar_y = background_height // 2 - avatar_size // 2
                avatar_image = Image.new('RGBA', (avatar_size, avatar_size), (255, 255, 255, 0))
                  
                # Download the avatar image (if one is set), else set it to the monacle image
                if avatar is not None:
                    try:
                        avatar_response = requests.get(avatar.format(member=member))
                    except:
                        avatar_response = requests.get("https://i.imgur.com/SQylaPJ.jpg")

                if avatar_response.status_code == 200:
                    avatar_content = io.BytesIO(avatar_response.content)
                    avatar_image = Image.open(avatar_content)
                    avatar_image = avatar_image.convert('RGBA')
                    avatar_image = avatar_image.resize((avatar_size, avatar_size), resample=Image.LANCZOS)
                    
                    # Create a circular mask
                    mask = Image.new('L', (avatar_size, avatar_size), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
                    del draw
                
                    # Apply the mask to the avatar image
                    avatar_image.putalpha(mask)
                
                    # Add a white circle outline to the avatar image
                    draw = ImageDraw.Draw(avatar_image)
    
                    #Find the avatar outline color choice (if necessary)
                    if avatar_outline_color:
                        r = avatar_outline_color[0]
                        g = avatar_outline_color[1]
                        b = avatar_outline_color[2]
    
                      
                    draw.ellipse((0, 0, avatar_size, avatar_size), fill=None, outline=(r, g, b, 255), width=5)
                    del draw
                    
                if avatar_placement == 'Top Right':
                    background_image.paste(avatar_image, (background_width - avatar_size - 20, 20), avatar_image)
                    text_x = background_width - avatar_size - text_width - 30
                    text_y = 20
                    align = "right"
                elif avatar_placement == 'Top Left':
                    background_image.paste(avatar_image, (20, 20), avatar_image)
                    text_x = avatar_size + 30
                    text_y = 20
                    align = "left"
                elif avatar_placement == 'Bottom Right':
                    background_image.paste(avatar_image, (background_width - avatar_size - 20, background_height - avatar_size - 20), avatar_image)
                    text_x = background_width - avatar_size - text_width - 30
                    text_y = background_height - text_height - 20
                    align = "right"
                elif avatar_placement == 'Bottom Left':
                    background_image.paste(avatar_image, (20, background_height - avatar_size - 20), avatar_image)
                    text_x = avatar_size + 30
                    text_y = background_height - text_height - 20
                    align = "left"
                elif avatar_placement == 'Bottom Center':
                    background_image.paste(avatar_image, (background_width // 2 - avatar_size // 2, background_height - avatar_size - 20), avatar_image)
                    text_x = background_width // 2 - text_width // 2
                    text_y = background_height - avatar_size - text_height - 30
                    align = "center"
                elif avatar_placement == 'Top Center':
                    background_image.paste(avatar_image, (background_width // 2 - avatar_size // 2, 20), avatar_image)
                    text_x = background_width // 2 - text_width // 2
                    text_y = avatar_size + 25
                    align = "center"
                elif avatar_placement == 'Left':
                    background_image.paste(avatar_image, (20, background_height // 2 - avatar_size // 2), avatar_image)
                    text_x = avatar_size + 30
                    text_y = background_height // 2 - text_height // 2
                    align = "left"
                elif avatar_placement == 'Right':
                    background_image.paste(avatar_image, (background_width - avatar_size - 20, background_height // 2 - avatar_size // 2), avatar_image)
                    text_x = background_width - text_width - avatar_size - 30
                    text_y = background_height // 2 - text_height // 2
                    align = "right"
                elif avatar_placement == 'Center':
                    background_image.paste(avatar_image, (background_width // 2 - avatar_size // 2, background_height // 2 - avatar_size // 2), avatar_image)
                    text_x = background_width // 2 - text_width // 2
                    text_y = background_height // 2 + avatar_size // 2 + 5
                    align = "center"
    
    
                #Find the avatar outline color choice (if necessary)
                if image_text_color:
                    r = image_text_color[0]
                    g = image_text_color[1]
                    b = image_text_color[2]
                  
                # Draw the message on the image
                draw = ImageDraw.Draw(background_image)
                if image_text:
                    if align == "right":
                        # Align the lines to the right
                        for i, line in enumerate(lines):
                            draw_x = text_x + text_width - line_widths[i]
                            draw_y = text_y + i * line_height
                            draw.text((draw_x, draw_y), line, font=font, fill=(r, g, b, 255))
                    elif align == "center":
                        # Draw each line with centered alignment
                        for i, line in enumerate(lines):
                            line_width, line_height = font.getsize(line)
                            draw_x = text_x + (text_width - line_width) // 2
                            draw_y = text_y + i * line_height
                            draw.text((draw_x, draw_y), line, font=font, fill=(r, g, b, 255))
                    #align to the left
                    else:
                        draw.text((text_x, text_y), image_text, font=font, fill=(r, g, b, 255))
                    
                # Save the final image as a byte array
                image_byte_array = io.BytesIO()
                background_image.save(image_byte_array, format='PNG')
                image_byte_array.seek(0)
    
                #give member a role when they join (if set by user)
                if on_join_status_id:
                    await member.add_roles(discord.Object(id=on_join_status_id))
                
                # Send the welcome message and image to the channel
                if message:
                    await channel.send(message, file=discord.File(image_byte_array, filename='welcome.png'))
                else:
                    await channel.send(file=discord.File(image_byte_array, filename='welcome.png'))
         


    @discord.slash_command(
        name="testwelcome",
        description="Test how the automaton welcomes newcomers. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def testwelcome(self, ctx, user: Option(discord.Member, name="user", description="Choose a user to welcome.", required=False)):
        #only allow admins to test welcome
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

      
        member_server_id = ctx.guild.id #retrieve the server ID of where the member is being welcomed
        welcome_key = {"server_id": member_server_id} #key to search through mongoDB with to find the appropriate welcome configuration
      
        #find the welcome config for the server
        welcome_data = welcome_db.welcomeconfig.find_one(welcome_key)


        if welcome_data is None:
            await ctx.respond(f"Apologies, {ctx.user.mention}\nThe welcome configuration has not been set up for **{ctx.guild.name}**.\nPlease use my `/welcome` directive to configure this so that I may begin greeting newcomers!", ephemeral = True)
        else:
            if user is None:
              user = ctx.author


            #get the welcome event status from mongoDB
            welcome_messages_status = await self.get_welcome_event_status(member_server_id)

            if welcome_messages_status == "Enabled":
                await ctx.respond(f"{ctx.author.mention},\nI have dispatched the welcome message to the intended destination.", ephemeral=True)
                await self.on_member_join(user)
            elif welcome_messages_status == "Disabled":
                await ctx.respond(f"{ctx.author.mention},\nIt appears that welcome messages have been disabled for {ctx.guild.name}.\nYou may use my `/eventhandler` directive to update this, if you wish.", ephemeral=True)


###############################WELCOMER#################################





  

###########################TIMED EMBEDS###################################

    #This retrieves the current server's event status from the mongoDB database
    async def get_timed_embeds_event_status(self, guild_id):
        # mongoDBpass = os.environ['mongoDBpass']
        mongoDBpass = os.getenv('mongoDBpass')
        client = pymongo.MongoClient(mongoDBpass)
        event_handler_db = client.event_handler_db

        event_doc = event_handler_db.events.find_one({"server_id": guild_id})
        if event_doc:
            return event_doc["timed_embeds"]
        else:
            return "Enabled"

  

    # Send timed embeds (check every 60 seconds)
    @tasks.loop(seconds=60)
    async def send_timed_embeds(self):
        tz = pytz.timezone('US/Central') # Set timezone to US/Central
      
        for server_data in embeds_db.list_collection_names():
            server_id = server_data.split("_")[2]

            #retrieve timed embeds status from mongoDB (use int() to convert the str server_id to an integer because you cannot compare a string with an integer)
            timed_embeds_status = await self.get_timed_embeds_event_status(int(server_id))

            #timed embeds only run if event status using /eventhandler is set to enabled OR if the user has not set the status using /eventhandler
            if timed_embeds_status == "Disabled":
                continue
            elif timed_embeds_status == "Enabled":
                for config_data in embeds_db[f"embeds_config_{server_id}"].find():
                    send_time = datetime.datetime.strptime(config_data['send_time'], '%Y-%m-%d %H:%M') 
                    send_time = tz.localize(send_time) # Localize send_time to US/Central timezone
                    send_time = send_time.strftime('%Y-%m-%d %H:%M')
                    dt = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M') #localize time to US/Central timezone
                  
                    #only send message if time now is equal to send_time down to the minute (localized to US/Central timezone)
                    if dt == send_time:
                        channel = self.bot.get_channel(config_data['channel_id'])
                        if channel is None:
                            # print(f"Error: Channel with ID {config_data['channel_id']} not found for server {server_id}.")
                            continue
        
                        color_data = config_data['color']
                        if color_data:
                            r = color_data[0]
                            g = color_data[1]
                            b = color_data[2]
                        else:
                            r = 0
                            g = 0
                            b = 255

                      
                        #check for the automaton patron tier and reset the configurations to the defaults
                        patron_data = patrons_db.patrons
                        refined_patron_key = {
                          "server_id": server_id,
                          "patron_tier": "Refined Automaton Patron"
                        }
                        distinguished_patron_key = {
                          "server_id": server_id,
                          "patron_tier": "Distinguished Automaton Patron"
                        }
                      
                        refined_patron = patron_data.find_one(refined_patron_key)
                        distinguished_patron = patron_data.find_one(distinguished_patron_key)
                        embeds_count = embeds_db[f"embeds_config_{server_id}"].count_documents({})


                        #delete all excess timed embed configs
                        if not distinguished_patron and embeds_count > 5:
                            excess_count = embeds_count - 5  # Adjust the desired count accordingly
                            embeds_db[f"embeds_config_{server_id}"].delete_many({"server_id": server_id}, limit=excess_count)
                          
                        if not refined_patron or not distinguished_patron:
                            r = 0
                            g = 0
                            b = 255

                      

                        title = config_data.get('title')
                        body = config_data.get('body')
                        field_name = config_data.get('field_name')
                        field_value = config_data.get('field_value')


                        embed = discord.Embed(
                            title=title,
                            description=body,
                            color=discord.Color.from_rgb(r, g, b)
                        )
        
                        if config_data.get('thumbnail'):
                            embed.set_thumbnail(url=config_data['thumbnail'])
        
                        if config_data.get('image'):
                            embed.set_image(url=config_data['image'])

    
                        embed.add_field(name=field_name, value=field_value, inline=config_data['field_inline'])
        
                        await channel.send(embed=embed)
        
                        interval = config_data.get('interval', 0)
                        intervaltype = config_data.get('intervaltype')

                        #add interval to new time to continue sending
                        if interval and intervaltype == "repeating":
                            send_time = datetime.datetime.strptime(send_time, '%Y-%m-%d %H:%M')
                            new_send_time = (send_time + timedelta(minutes=interval)).strftime('%Y-%m-%d %H:%M')
                            embeds_db[f"embeds_config_{server_id}"].update_one({"_id": config_data["_id"]}, {"$set": {"send_time": new_send_time}})

                        #dont add interval to new time to stop sending after it is sent
                        elif interval and intervaltype == "onetime":
                            pass



    #embeds list
    @discord.slash_command(
        name="embedslist",
        description="List all the timed embeds created so far. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def embedslist(self, ctx):
        #only allow admins to retrieve embeds list
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

      
        embeds_data = list(embeds_db[f"embeds_config_{ctx.guild.id}"].find())
        # embed_count = len(embeds_data)

        if not embeds_data:
            await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that there are no timed embed configurations for {ctx.guild.name}. Consider using my `/timedembeds` directive to set these up.", ephemeral=True)
            return
      
        tz = pytz.timezone('US/Central') # Set timezone to US/Central


        #get the timed embed event status from mongoDB
        timed_embeds_status = await self.get_timed_embeds_event_status(ctx.guild.id)

      
        embed = discord.Embed(title=f"{ctx.guild.name}\n__Timed Embeds List__", description = f"The following is a list of timed embeds. It is advisable to *remove* or *edit* all timed embeds which are prior to the current time (`{datetime.datetime.now(tz).strftime('%B %d, %Y %I:%M %p %Z')}`)\n{f'Timed embeds are currently **disabled** for {ctx.guild.name}. However, you may update this using my `/eventhandler` directive, if you wish.' if timed_embeds_status == 'Disabled' else ''}", color=discord.Color.from_rgb(130, 130, 130))
        for i, config_data in enumerate(embeds_data):
            channel = self.bot.get_channel(config_data['channel_id'])
          
            send_time = config_data['send_time']
            send_time = datetime.datetime.strptime(send_time, '%Y-%m-%d %H:%M')
            send_time = send_time.strftime('%B %d, %Y %I:%M %p')

            intervaltype = config_data['intervaltype']
            interval = config_data['interval']

            #interval type
            intervaltype_dict = {
              "repeating": "🔄 Repeating",
              "onetime": "☝ One Time"
            }
    
            if intervaltype in intervaltype_dict:
                intervaltype = intervaltype_dict[intervaltype]
          
          
            value = f"Channel: {channel.mention}\nSend Time: `{send_time}`\nInterval Type: *{intervaltype}*\nInterval: {f'`{interval} minutes`' if intervaltype == '🔄 Repeating' else '*n/a*'}"
            embed.add_field(name=f"{i+1}. {config_data['config_name']}", value=value, inline=True)

      
        #set thumbnail to timer gif
        embed.set_thumbnail(url="https://i.imgur.com/FzUsO01.gif")
        
        await ctx.respond(embed=embed, ephemeral=True)

#############################TIMED EMBEDS###################################




def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Utility(bot)) # add the cog to the bot
