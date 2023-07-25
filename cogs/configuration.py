import discord #needed to interact with discord API
import os #to import secret keys and such
from discord.ext import commands #used for slash commands
import asyncio #used to wait for specified amounts of time
from discord.commands import Option  # add options to slash commands

import pymongo #used for database management

import pytz #used for timezone
from datetime import datetime #used to get date formatting and such

from urllib.parse import urlparse #used to check if url is a url

import emoji #for checking if starboard reaction is an emoji or not

import re #regular expression (used for determing string characters for autopurge)

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
BD_db = client.BD_db #create the birthday database on MongoDB
streaming_db = client.streaming_db #create the streaming database on MongoDB
embeds_db = client.embeds_db #create the birthday database on MongoDB
welcome_db = client.welcome_db #create the welcomer database on MongoDB
starboard_db = client.starboard_db #create the starboard database on MongoDB
autopurge_db = client.autopurge_db #create the autopurge database on MongoDB
moderation_db = client.moderation_db #create the moderation database on MongoDB
patrons_db = client.patrons_db #create the patrons database on mongoDB
autosatire_db = client.autosatire_db #create the autosatire (automeme) database on MongoDB
bump_db = client.bump_db #create the bump (promotion) database on MongoDB
#########################MONGODB DATABASE##################################

#this is an array of the server IDs where command testing is done
SERVER_ID = [1088118252200276071, 1117859916749742140]


class Configuration(commands.Cog):
    # this is a special method that is called when the cog is loaded
    def __init__(self, bot):
        self.bot: commands.Bot = bot

      
  
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



############################### BUMP (PROMOTION) #############################
    @discord.slash_command(
        name="promotion",
        description="Configure the promotion settings for the guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def promotion(
        self,
        ctx,
        promotion_channel: Option(discord.TextChannel, name="promotion_channel", description="Channel within your guild to send promotions to."),
        invite_channel: Option(discord.TextChannel, name="invite_channel", description="Channel to invite new users to upon promotion."),
        topic: Option(str, name="topic", description="Best/primary topic to describe your guild. (Default: None)", required=False, default=None, choices=["🎮 Gaming", "🎨 Art", "🎵 Music", "😺 Anime", "😂 Memes", "📚 Books", "📱 Technology", "🍔 Food", "💪 Fitness", "⚽ Sports", "🎬 Movies", "💻 Programming", "🌍 Travel", "🐾 Pets", "📷 Photography", "✍️ Writing", "👗 Fashion", "🔬 Science", "📚 Education", "🎭 Roleplay", "🤝 Support", "🗳️ Politics", "📜 History", "🚀 Promotion", "👥 General Hangout"]),
        color: Option(str, name="color", description="Color for the guild promotion. (Default: 🔵Blue)", required=False, choices=["🔴 Red", "🟢 Green", "🔵 Blue", "🟡 Yellow", "🟣 Purple", "⚫ Black", "⚪ White"], default=None),
        custom_color: Option(str, name="custom_color", description="Custom RGB color tuple (0, 0, 0) for the guild promotion. (Patron Only)", required=False, default=None),
        guild_banner: Option(str, name="guild_banner", description="Image URL for the guild banner upon promotion. (Patron Feature)", required=False, default=None),
        remove: Option(bool, name="remove", description="Remove your guild promotion configuration from the database. (Default: False)", required=False, default=False)
    ):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

        #remove the configuration
        if remove:
            bump_key = {"server_id": ctx.guild.id}

            data = bump_db.bump_configs.find_one(bump_key)

            if data:
                invite_url = data['invite_link']

                # Delete the invite link
                try:
                    invite = await self.bot.fetch_invite(invite_url)
                    await invite.delete(reason="Removing promotion configuration")
                except discord.NotFound:
                    # Invite not found, it might have already been deleted
                    pass
                
                bump_db.bump_configs.delete_one(bump_key)
                await ctx.respond(f"{ctx.author.mention}\nI have successfully removed the promotion configuration for ***{ctx.guild.name}***, good sir.", ephemeral=True)
                return
        
        guild_description = None

        
        # Get the bot's member object
        lordbottington = ctx.guild.get_member(ctx.bot.user.id)

        # Check if the bot has create invite permissions in the current channel
        if not lordbottington.guild_permissions.create_instant_invite:
            await ctx.respond(f"Apologies {ctx.author.mention},\nI do not have permission to create invites in this guild.\n*Please change this for myself in the guild (server) settings on Discord and try again.*", ephemeral=True)
            return

        
        #define RGB guild promotion color tuples
        colors = {
            "🔴 Red": (255, 0, 0),
            "🟢 Green": (0, 255, 0),
            "🔵 Blue": (0, 0, 255),
            "🟡 Yellow": (255, 255, 0),
            "🟣 Purple": (152, 3, 252),
            "⚫ Black": (0, 0, 0),
            "⚪ White": (255, 255, 255)
        }        
    
        if color:
            if color in colors:
                r = colors[color][0]
                g = colors[color][1]
                b = colors[color][2]
        else: #set to blue if nothing selected
            r = 0
            g = 0
            b = 255
        

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
                cooldown_time = 7200 # 2 hours
                cooldown_time_str = "2 hours"
                            
            else:
                cooldown_time = 1800 # 30 min
                cooldown_time_str = "30 minutes"

        #cooldown for support guild
        else:
            cooldown_time = 1800 # 30 min
            cooldown_time_str = "30 minutes"

  

        #check for a custom color (only avaliable to refined and distinguished patrons and support guild)
        if custom_color or guild_banner:
            if ctx.guild.id != support_guild_id:
                if not refined_patron and not distinguished_patron:
                    patron_command = self.bot.get_application_command("patron")
                    promotion_command = self.bot.get_application_command("promotion")
                    
                    patron_embed = discord.Embed(title="Patron Feature", description=f"Apologies {ctx.author.mention},\nCustom embed colors and guild banners for my </{promotion_command,name}:{promotion_command.id}> directive are exclusive features available solely to `🎩🎩 Refined Automaton Patrons` and `🎩🎩🎩 Distinguished Automaton Patrons` and is not currently in use for ***{ctx.guild.name}***, good sir.\n\nPlease use my </{patron_command.name}:{patron_command.id}> directive to learn more information on enabling or upgrading patron (premium) features for ***{ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(130, 130, 130))
          
                    patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
          
                    await ctx.respond(embed=patron_embed, ephemeral=True)
                    return
                
                    

        if guild_banner:
            parsed_url = urlparse(guild_banner)
            if parsed_url.scheme in ("http", "https"): # check if item is a valid url
                if parsed_url.path.endswith((".jpg", ".png", ".jpeg", ".gif")): #only allow .jpg, .png, .jpeg, .gif files
                    banner_url = guild_banner
    
                else:
                    await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that ***{guild_banner}*** is not a valid image link.\nThis URL must be a direct link to a .JPG, .JPEG, .PNG, or .GIF image.\n*Please try again.*", ephemeral=True)
                    return
    
            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that ***{guild_banner}*** is not a valid image link.\nThis URL must be a direct link to a .JPG, .JPEG, .PNG, or .GIF image.\n*Please try again.*", ephemeral=True)
                return
        else:
            banner_url = None

        
        #check the custom color
        if custom_color:
            custom_color = self.check_custom_color(custom_color)
    
            if custom_color: #if the check is passed
                custom_r = custom_color[0]
                custom_g = custom_color[1]
                custom_b = custom_color[2]
            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\nThe custom color must be a comma-separated RGB color tuple.\n\n**For example:**\n*Black - (0, 0, 0)*\n*White: (255, 255, 255)*\n\n*Please input a valid RGB color tuple and try again.*", ephemeral=True)
                return

            #override the original color if custom color is used            
            r = custom_r
            g = custom_g
            b = custom_b

        if topic:
            topic = topic
        else:
            topic = None

        
        bump_key = {"server_id": ctx.guild.id}

        server_data = bump_db.bump_configs.find_one(bump_key)

        if server_data:
            guild_description = server_data['guild_description']
            previous_invite_channel_id = server_data['invite_channel_id']
            bumps = server_data['bumps']

            if previous_invite_channel_id != invite_channel.id:
                # Create a new invite for the invite_channel with unlimited uses (if not the same channel as the previously used one)
                invite_link = await invite_channel.create_invite(max_age=0, max_uses=0, unique=True)
            else:
                invite_link = server_data['invite_link']
                
                # check if invite is valid or not
                try:
                    await self.bot.fetch_invite(invite_link)
                except:
                    #if invalid link, create a new one
                    invite_link = await invite_channel.create_invite(max_age=0, max_uses=0, unique=True)

        else:
            bumps = 0 #no bumps yet
            invite_link = await invite_channel.create_invite(max_age=0, max_uses=0, unique=True)


        bump_modal = self.BumpModal(title="Guild Promotion Configuration", previous_description=guild_description)
        await ctx.send_modal(bump_modal)
    
        try:
            await asyncio.wait_for(bump_modal.wait(), timeout=600.0)
          
            guild_description = bump_modal.description
        except asyncio.TimeoutError:
            await ctx.respond("Good sir, it appears you have taken too long to enter your guild promotion configuration.\n*Please try again.*", ephemeral=True)
            return

        #get the app_commands related to promotion
        testpromote_app_command = self.bot.get_application_command("testpromote")
        promote_app_command = self.bot.get_application_command("promote")
        event_handler_command = self.bot.get_application_command("eventhandler")

        bump_key = {"server_id": ctx.guild.id}
        server_data = bump_db.bump_configs.find_one(bump_key)
        
        if not server_data:
            bump_db.bump_configs.insert_one(
              {
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name,
                "invite_link": str(invite_link),
                "invite_channel_id": invite_channel.id,
                "invite_channel_name": invite_channel.name,
                "guild_description": guild_description,
                "promotion_channel_id": promotion_channel.id,
                "promotion_channel_name": promotion_channel.name,
                "color": [r, g, b],
                "banner_url": banner_url,
                "bumps": bumps, #initialize the bump count to 0
                "topic": topic
              }
            )
            
            embed_description = f"{ctx.author.mention}\n\n> I have successfully *created* the guild promotion configuration for ***{ctx.guild.name}***.\n> \n> You may now utilize my </{promote_app_command.name}:{promote_app_command.id}> directive every `2 hours` to promote your guild!\n> You may also utilize </{testpromote_app_command.name}:{testpromote_app_command.id}> to see a preview of your promotion and </{event_handler_command.name}:{event_handler_command.id}> to turn reminders to promote this guild on or off, if you desire.\n> \n> *Best of luck to you in growing this esteemed community, good sir!*"
            
        else:
            bump_db.bump_configs.update_one(
              {
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name
              },
              {"$set": {
                "invite_link": str(invite_link),
                "invite_channel_id": invite_channel.id,
                "invite_channel_name": invite_channel.name,
                "guild_description": guild_description,
                "promotion_channel_id": promotion_channel.id,
                "promotion_channel_name": promotion_channel.name,
                "color": [r, g, b],
                "banner_url": banner_url,
                "bumps": bumps,
                "topic": topic
                }
              }
            )

        
            embed_description = f"{ctx.author.mention}\n\n> I have successfully *updated* the guild promotion configuration for ***{ctx.guild.name}***.\n> \n> You may now utilize my </{promote_app_command.name}:{promote_app_command.id}> directive every `{cooldown_time_str}` to promote your guild!\n> You may also utilize </{testpromote_app_command.name}:{testpromote_app_command.id}> to see a preview of your promotion and </{event_handler_command.name}:{event_handler_command.id}> to turn reminders to promote this guild on or off, if you desire.\n> \n> *Best of luck to you in growing this esteemed community, good sir!*"

        automaton_invite_link = "https://discord.com/api/oauth2/authorize?client_id=1092515783025889383&permissions=3557027031&scope=bot%20applications.commands"
        support_guild_invite = "https://discord.gg/4P6ApdPAF7"

        InviteLordBottington = discord.ui.Button(emoji='🤖', label="Add Lord Bottington", url=automaton_invite_link, style=discord.ButtonStyle.link)
        JoinSupportGuild = discord.ui.Button(emoji='🎩', label="Join 𝓣𝓱𝓮 𝓢𝔀𝓮𝓮𝔃 𝓖𝓪𝓷𝓰", url=support_guild_invite, style=discord.ButtonStyle.link)

        view=View()
        view.add_item(InviteLordBottington)
        view.add_item(JoinSupportGuild)
        
        #send the embed to the user
        promotion_embed = discord.Embed(title=f"{ctx.guild.name}\nPromotion Configuration", description = embed_description, color=discord.Color.from_rgb(r, g, b))

        promotion_embed.set_thumbnail(url=self.bot.user.avatar.url)

        await ctx.respond(embed=promotion_embed, view=view, ephemeral=True)



    #description field
    class BumpModal(discord.ui.Modal):
        def __init__(self, *args, previous_description, **kwargs):
            super().__init__(*args, **kwargs)

            self.description = previous_description

            self.add_item(discord.ui.InputText(label="Guild Description", style=discord.InputTextStyle.long, min_length=150, max_length=1000, placeholder="Enter a proper description for your guild (server).", value=previous_description))
  

        async def callback(self, interaction: discord.Interaction):
            self.description = self.children[0].value
            await interaction.response.defer() #acknowledges the interaction before calling self.stop()
            self.stop()
    
############################### BUMP (PROMOTION) #############################




    

############################### AUTOSATIRE #############################
    @discord.slash_command(
        name="autosatire",
        description="Configure the automated satirical image (meme) settings for the guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def autosatire(
        self,
        ctx,
        channel: Option(discord.TextChannel, name="channel", description="Channel to send satirical images (memes) to."),
        community: Option(str, name="community", description="Name of the community (subreddit) to retrieve satirical images from. (Default: Random)", choices=["memes", "dankmemes", "meme", "wholesomememes"]),
        remove: Option(bool, name="remove", description="Remove the autosatire configuration for the guild. (Default: False)", required=False, default=False)
    ):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

      
        satire_key = {"server_id": ctx.guild.id}

        #remove moderation config
        if remove is True:
            if not moderation_db.moderation_configs.find_one(satire_key):
                await ctx.respond(f"Apologies {ctx.author.mention},\nI was unable to locate any autosatire configurations for ***{ctx.guild.name}***.", ephemeral=True)
                return
            else:
                await ctx.respond("Now removing the autosatire configuration for this guild...", ephemeral=True)
                await asyncio.sleep(5)

                autosatire_db.autosatire_configs.delete_one(satire_key)

                await ctx.respond(f"{ctx.author.mention}\nI have removed the autosatire configuration for ***{ctx.guild.name}***.\nSatirical images will no longer be sent within this guild, good sir.", ephemeral=True)
                return

      
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

            # this checks if the subreddit is private or not
            try:
                subreddit = await reddit.subreddit(community)
          
                all_subs = []
                hot = subreddit.hot(limit=1) # bot will choose between the first hottest post in the subreddit
              
                async for submission in hot:
                    if submission.over_18 is False:  # Check if the post is marked NSFW (omit it if it is)
                        all_subs.append(submission)
    
            # subreddit is private
            except asyncprawcore.exceptions.Forbidden:
                await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that `r/{community}` is currently a *private* community, so I am unable to retrieve a satirical image from there, good sir.\n*Please try again.*", ephemeral=True)
                return
    


        #add autosatire config
        if not autosatire_db.autosatire_configs.find_one(satire_key):
            await ctx.respond(f"Good sir, there is currently no autosatire configuration for ***{ctx.guild.name}***.\n*Now creating this configuration...*", ephemeral=True)
            await asyncio.sleep(5)

          
            autosatire_db.autosatire_configs.insert_one(
              {
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name,
                "channel_id": channel.id,
                "channel_name": channel.name,
                "community": community
              }
            )

            await ctx.respond(f"{ctx.author.mention}\nI have created the autosatire configuration for ***{ctx.guild.name}***.\nSatirical images from `r/{community}` will now be sent to {channel.mention} once a day, good sir.", ephemeral=True)

        else:
            autosatire_db.autosatire_configs.update_one(
              satire_key,
              {"$set": {
                "channel_id": channel.id,
                "channel_name": channel.name,
                "community": community
                }
              }
            )

            await ctx.respond(f"{ctx.author.mention}\nI have updated the autosatire configuration for ***{ctx.guild.name}***.\nSatirical images from `r/{community}` will now be sent to {channel.mention}, good sir.", ephemeral=True)

############################### AUTOSATIRE #############################



  


############################MODERATION###################################
    @discord.slash_command(
        name="moderate",
        description="Configure the moderation for the guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def moderate(
        self,
        ctx,
        channel: Option(discord.TextChannel, name="channel", description="Channel where moderation messages will be sent for the guild."),
        remove: Option(bool, name="remove", description="Remove the moderation configuration for the guild. (Default: False)", required=False, default=False)
    ):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

        moderation_key = {"server_id": ctx.guild.id}

        #remove moderation config
        if remove is True:
            if not moderation_db.moderation_configs.find_one(moderation_key):
                await ctx.respond(f"Apologies {ctx.author.mention},\nI was unable to locate any moderation configurations for {ctx.guild.name}.", ephemeral=True)
                return
            else:
                await ctx.respond("Now removing the moderation configuration for this guild...", ephemeral=True)
                await asyncio.sleep(5)

                moderation_db.moderation_configs.delete_one(moderation_key)

                await ctx.respond(f"{ctx.author.mention}\nI have removed the moderation configuration for ***{ctx.guild.name}***. Moderation messages will now be sent in the channel where the directive is used.", ephemeral=True)
                return


        #add moderation config
        if not moderation_db.moderation_configs.find_one(moderation_key):
            await ctx.respond(f"Good sir, there is currently no moderation configuration for {ctx.guild.name}\n*Now creating this configuration...*", ephemeral=True)
            await asyncio.sleep(5)

          
            moderation_db.moderation_configs.insert_one(
              {
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name,
                "channel_id": channel.id,
                "channel_name": channel.name
              }
            )

            await ctx.respond(f"{ctx.author.mention}\nI have created this configuration for ***{ctx.guild.name}***.\nModeration messages will now be sent exclusively to {channel.mention}.", ephemeral=True)

        else:
            moderation_db.moderation_configs.update_one(
              {
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name
              },
              {"$set": {
                "channel_id": channel.id,
                "channel_name": channel.name
                }
              }
            )

            await ctx.respond(f"{ctx.author.mention}\nI have updated the moderation configuration for ***{ctx.guild.name}***.\nModeration messages will now be sent exclusively to {channel.mention}.", ephemeral=True)

  

#############################MODERATION###################################





  
#############################AUTOPURGE##################################
    @discord.slash_command(
        name="autopurge",
        description="Allow the automaton to automatically purge messages from a desired channel. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def autopurge(
        self,
        ctx,
        channel: Option(discord.TextChannel, name="channel", description="Channel to purge messages from."),
        frequency: Option(str, name="frequency", description="Frequency at which the messages will be deleted for the specified channel. (1d 1h 1m 1s)", required=False, default=None),
        messagecount: Option(int, name="messagecount", description="The maximum number of messages allowed in the specified channel.", required=False, default=None, min_value=0, max_value=100)
    ):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return
          

      
        #bot owner and those with the distinguished automaton patron (top tier) can create unlimited configurations (everyone else can make a max of 5)

        support_guild_id = 1088118252200276071

        if ctx.guild.id != support_guild_id:
            #search for a guild on mongoDB that has the Distinguished Automaton Patron tier
            patron_key = {
              "server_id": ctx.guild.id,
              "patron_tier": "Distinguished Automaton Patron"
            }
            patron_data = patrons_db.patrons
            patron_info = patron_data.find_one(patron_key)

      
            if not patron_info:
                # Count the number of autopurge configurations already created
                autopurge_count = autopurge_db[f"autopurge_config_{ctx.guild.id}"].count_documents({})
                if autopurge_count >= 5:
                    autopurgelist_command = self.bot.get_application_command("autopurgelist")
                    patron_command = self.bot.get_application_command("patron")
                    help_command = self.bot.get_application_command("help")
                    await ctx.respond(f"Apologies good sir,\nYou have reached the maximum limit of **5** autopurge configurations for ***{ctx.guild.name}***.\n\nYou may view a list of the current autopurge channel(s) using my </{autopurgelist_command.name}:{autopurgelist_command.id}> directive.\nUse my </{help_command.name}:{help_command.id}> directive and search for `autopurge` for more information on how to manage this issue, good sir.\n\nYou may also use my </{patron_command.name}:{patron_command.id}> directive to upgrade your patron status for this guild to receive *unlimited* configurations for this directive, if you wish.", ephemeral=True)
                    return

          
        if frequency:
            frequency_seconds = 0
            match = re.findall(r"(\d+)([dhms])", frequency)
            if match:
                for value, unit in match:
                    if unit == "d":
                        frequency_seconds += int(value) * 86400
                    elif unit == "h":
                        frequency_seconds += int(value) * 3600
                    elif unit == "m":
                        frequency_seconds += int(value) * 60
                    elif unit == "s":
                        frequency_seconds += int(value)

                    if frequency_seconds == 0:
                        pass
                    elif frequency_seconds < 60:
                        await ctx.respond(f"Apologies {ctx.author.mention},\nAutopurged channels must have a *frequency* of at least `60s`.\n*Please try again.*", ephemeral=True)
                        return
            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\nThe *frequency* parameter must be in the form `01d:01h:01m:01s` or a combination of this.\n*Please try again.*", ephemeral=True)
                return
    
          
            # Calculate the total frequency time in days, hours, minutes, and seconds
            days, remainder = divmod(frequency_seconds, 86400)
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
            frequency_purge_time = "0s"



        if not frequency or frequency_seconds == 0:
            frequency_seconds = None

        if not messagecount or messagecount == 0:
            messagecount = None

        if messagecount and messagecount > 100:
            await ctx.respond(f"{ctx.author.mention}\nPlease specify a message count less than or equal to ***100*** to avoid Discord rate limits, good sir...", ephemeral=True)
            return
      

        purge_key = {"purge_channel_id": channel.id}

        #delete entry if both not found and there is an entry for that channel
        if autopurge_db[f"autopurge_config_{ctx.guild.id}"].find_one(purge_key) and (not frequency_seconds and not messagecount):
            autopurge_db[f"autopurge_config_{ctx.guild.id}"].delete_one(purge_key)
          
            await ctx.respond(f"{ctx.author.mention},\nMessages will no longer be autopurged from {channel.mention}, good sir.", ephemeral=True)
            return
          
        elif not autopurge_db[f"autopurge_config_{ctx.guild.id}"].find_one(purge_key) and (not frequency_seconds and not messagecount):
            await ctx.respond(f"Apologies {ctx.author.mention},\nThere does not seem to be an entry for {channel.mention}, so I am unable to remove its autopurge configuration at this time.", ephemeral=True)
            return

        #get current time (for saving amount of time remaining)
        start_time = datetime.utcnow()

        autopurgelist_command = self.bot.get_application_command("autopurgelist")

        if not autopurge_db[f"autopurge_config_{ctx.guild.id}"].find_one(purge_key):
            await ctx.respond(f"Good sir, there are currently no autopurge configurations for {channel.mention}\n*Now creating this configuration...*", ephemeral=True)
            await asyncio.sleep(5)

          
            autopurge_db[f"autopurge_config_{ctx.guild.id}"].insert_one(
              {
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name,
                "purge_channel_id": channel.id,
                "purge_channel_name": channel.name,
                "frequency": frequency_seconds,
                "messagecount": messagecount,
                "start_time": start_time,
                "time_remaining": int(frequency_seconds) if frequency_seconds else None
              }
            )

            await ctx.respond(f"{ctx.author.mention}\n\nI have begun the purging process and set up your autopurge configuration.\n{channel.mention} will be purged every `{frequency_purge_time}` and will have a maximum message count of `{messagecount if messagecount else 0}` messages.\n\n*Please ensure that any messages you would like to keep in the future have been **pinned** to the channel.*\nYou may view your currently autopurged channels using my </{autopurgelist_command.name}:{autopurgelist_command.id}> directive, if you desire.", ephemeral=True)


            #create a loop that begins using the information given here
            await self.autopurge_task(ctx.guild.id, channel.id)

        else:
            autopurge_db[f"autopurge_config_{ctx.guild.id}"].update_one(
              {
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name,
              },
              {"$set":{
                "purge_channel_id": channel.id,
                "purge_channel_name": channel.name,
                "frequency": frequency_seconds,
                "messagecount": messagecount,
                "start_time": start_time,
                "time_remaining": int(frequency_seconds) if frequency_seconds else None
                }
              }
            )

            await ctx.respond(f"{ctx.author.mention}\n\nI have begun the purging process and updated your autopurge configuration.\n{channel.mention} will now be purged every `{frequency_purge_time}` and will have a maximum message count of `{messagecount if messagecount else 0}` messages.\n\n*Please ensure that any messages you would like to keep in the future have been **pinned** to the channel.*\nYou may view your currently autopurged channels using my </{autopurgelist_command.name}:{autopurgelist_command.id}> directive, if you desire.", ephemeral=True)

            #create a loop that begins using the information given here
            await self.autopurge_task(ctx.guild.id, channel.id)





    #This retrieves the current server's event status from the mongoDB database
    async def get_autopurge_event_status(self, guild_id):
        # mongoDBpass = os.environ['mongoDBpass']
        mongoDBpass = os.getenv('mongoDBpass')
        client = pymongo.MongoClient(mongoDBpass)
        event_handler_db = client.event_handler_db

        event_doc = event_handler_db.events.find_one({"server_id": guild_id})
        if event_doc:
            return event_doc["autopurge"]
        else:
            return "Enabled"

  

    #begin deleting messages in the channel
    async def autopurge_task(self, guild_id, purge_channel_id):
        while True:
            # print("autopurge started")
            #get the autopurge event status from mongoDB
            autopurge_status = await self.get_autopurge_event_status(guild_id)
        
        
            #Autopurge task event only runs if event status using /eventhandler is set to enabled OR if the user has not set the status using /eventhandler
            if autopurge_status == "Disabled":
                pass
            elif autopurge_status == "Enabled":
                # Retrieve autopurge configuration from database
                autopurge_key = {
                  "server_id": guild_id,
                  "purge_channel_id": purge_channel_id
                }
                autopurge_config = autopurge_db[f"autopurge_config_{guild_id}"].find_one(autopurge_key)
                if not autopurge_config:
                    # No autopurge configuration found for guild
                    return False
                    
        
                ##### PATRON FEATURE (always available in support guild)
                # server ID for The Sweez Gang
                support_guild_id = 1088118252200276071
        
                if guild_id != support_guild_id:
                    #check for the automaton patron tier
                    patron_data = patrons_db.patrons
                    patron_key = {
                      "server_id": guild_id,
                      "patron_tier": "Distinguished Automaton Patron"
                    }
                    autopurge_config_count = autopurge_db[f"autopurge_config_{guild_id}"].count_documents({})
                    distinguished_patron = patron_data.find_one(patron_key)
        
                    if not distinguished_patron and autopurge_config_count > 5:
                        delete_key = {"server_id": guild_id}
                        excess_count = autopurge_config_count - 5  # Adjust the desired count accordingly
                        autopurge_db[f"autopurge_config_{guild_id}"].delete_many(delete_key, limit=excess_count) #remove all configurations
        
                
                channel_id = autopurge_config['purge_channel_id']
                message_count = autopurge_config['messagecount']
                frequency_seconds = autopurge_config['frequency']
                time_remaining = autopurge_config['time_remaining']
                # print(channel_id)
                # print(message_count)
                # print(frequency_seconds)
            
            
                # Retrieve messages to delete from channel
                channel = self.bot.get_channel(channel_id)
                # print(channel)
            
                # Delete messages
                if message_count:
                    # print("message_count used")
                    messages = await channel.history(limit=None).flatten()
        
                    if len(messages) > message_count:
                        # retain only specified number of messages and pinned messages (from the message_count numbered message to the oldest message)
                        messages_to_delete = messages[message_count:len(messages)]
                        # print(messages_to_delete)
                        deleted_messages = await channel.purge(limit=None, check=lambda m: m in messages_to_delete and not m.pinned)
                else:
                    # print("all messages deleted")
                    # Delete all messages in the channel except for pinned messages
                    deleted_messages = await channel.purge(limit=None, check=lambda m: not m.pinned)


                #reset the time remaining to the original time and start_time to current time
                autopurge_db[f"autopurge_config_{guild_id}"].update_one(
                    autopurge_key,
                    {"$set": {
                        "start_time": datetime.utcnow(),
                        "time_remaining": int(frequency_seconds) if frequency_seconds else None
                        }
                    }
                )
            
                # Print number of messages deleted
                # print(f"Deleted {len(deleted_messages)} messages in {channel.name}")
        
                # Wait for the next autopurge cycle
                # if frequency is set, use that number, else use 60 seconds as time to check
                if frequency_seconds:
                    # print(frequency_seconds)
                    await asyncio.sleep(int(frequency_seconds))
                else:
                    # print("no frequency set")
                    await asyncio.sleep(60)




    #this is for when the bot starts up and some time is remaining on the task
    async def autopurge_startup(self, guild_id, purge_channel_id, time_remaining):
        await asyncio.sleep(int(time_remaining))
        
        #get the autopurge event status from mongoDB
        autopurge_status = await self.get_autopurge_event_status(guild_id)
    
    
        #Autopurge task event only runs if event status using /eventhandler is set to enabled OR if the user has not set the status using /eventhandler
        if autopurge_status == "Disabled":
            await self.autopurge_task(guild_id, purge_channel_id)
        elif autopurge_status == "Enabled":
            # Retrieve autopurge configuration from database
            autopurge_key = {
              "server_id": guild_id,
              "purge_channel_id": purge_channel_id
            }
            autopurge_config = autopurge_db[f"autopurge_config_{guild_id}"].find_one(autopurge_key)
            if not autopurge_config:
                # No autopurge configuration found for guild
                return
                
    
            ##### PATRON FEATURE (always available in support guild)
            # server ID for The Sweez Gang
            support_guild_id = 1088118252200276071
    
            if guild_id != support_guild_id:
                #check for the automaton patron tier
                patron_data = patrons_db.patrons
                patron_key = {
                  "server_id": guild_id,
                  "patron_tier": "Distinguished Automaton Patron"
                }
                autopurge_config_count = autopurge_db[f"autopurge_config_{guild_id}"].count_documents({})
                distinguished_patron = patron_data.find_one(patron_key)
    
                if not distinguished_patron and autopurge_config_count > 5:
                    delete_key = {"server_id": guild_id}
                    excess_count = autopurge_config_count - 5  # Adjust the desired count accordingly
                    autopurge_db[f"autopurge_config_{guild_id}"].delete_many(delete_key, limit=excess_count) #remove all configurations
    
            
            channel_id = autopurge_config['purge_channel_id']
            message_count = autopurge_config['messagecount']
            frequency_seconds = autopurge_config['frequency']
            # print(channel_id)
            # print(message_count)
            # print(frequency_seconds)
        
        
            # Retrieve messages to delete from channel
            channel = self.bot.get_channel(channel_id)
            # print(channel)
        
            # Delete messages
            if message_count:
                # print("message_count used")
                messages = await channel.history(limit=None).flatten()
    
                if len(messages) > message_count:
                    # retain only specified number of messages and pinned messages (from the message_count numbered message to the oldest message)
                    messages_to_delete = messages[message_count:len(messages)]
                    # print(messages_to_delete)
                    deleted_messages = await channel.purge(limit=None, check=lambda m: m in messages_to_delete and not m.pinned)
            else:
                # print("all messages deleted")
                # Delete all messages in the channel except for pinned messages
                deleted_messages = await channel.purge(limit=None, check=lambda m: not m.pinned)
        
            # Print number of messages deleted
            # print(f"Deleted {len(deleted_messages)} messages in {channel.name}")
    
            await self.autopurge_task(guild_id, channel_id)


##############################AUTOPURGE#################################




  

#########################BIRTHDAYS#######################################
    @discord.slash_command(
        name="birthday",
        description="Configure the settings for the automaton's birthday messages. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def birthday(
        self, 
        ctx, 
        channel: Option(discord.TextChannel, name="channel", description="Select a channel to send the birthday message.", required = False, default=None),
        role: Option(discord.Role, name="role", description="Select a role to assign to users on their birthday.", required = False, default = None),
        message: Option(str, name="message", description="Birthday message that will be sent to the specified channel. (Default: 🤖 Automaton Defined)", required = False, choices = ["🧒 User Defined", "🤖 Automaton Defined", "🚫 No Message"], default=None)
    ):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

      
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

      
            if message == "🧒 User Defined":
                if not refined_patron and not distinguished_patron:
                    patron_embed = discord.Embed(title="Patron Feature", description=f"Apologies {ctx.author.mention},\n`🧒 User Defined` birthday messages for my `/birthday` directive are an exclusive feature available solely to `🎩🎩 Refined Automaton Patrons` and `🎩🎩🎩 Distinguished Automaton Patrons` and is not currently in use for ***{ctx.guild.name}***, good sir.\n\nPlease use my `/patron` directive to learn more information on enabling or upgrading patron (premium) features for ***{ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(130, 130, 130))
          
                    patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
          
                    await ctx.respond(embed=patron_embed, ephemeral=True)
                    return


      
        # Check if the provided status is lower in hierarchy than the bot's highest role
        if role:
            bot_top_role = ctx.guild.me.top_role
            if role.position >= bot_top_role.position:
                await ctx.respond(
                    f"Regretfully, {ctx.author.mention}, I am incapable of assigning roles that hold a higher position in the hierarchy than my highest role.\nKindly proceed to the role settings for the server and place me *above* your highest role.", ephemeral=True
                )
                return

        if not channel and not role:
            await ctx.respond("Sir, you must choose either a status for me to assign or a channel to send the birthday messages.\n*Please try again.*", ephemeral=True)
            return

        if channel:
            birthday_channel_id = channel.id
            birthday_channel_name = channel.name
        else:
            birthday_channel_id = None
            birthday_channel_name = None
                                
        if role:
            birthday_role_id = role.id
            birthday_role_name = role.name
        else:
            birthday_role_id = None
            birthday_role_name = None

        messages = {
          "🧒 User Defined": "user",
          "🤖 Automaton Defined": "automaton",
          "🚫 No Message": None
        }
      
        if message:
            if message in messages:
                message = message
            else:
                await ctx.respond("Good sir, that is not a viable option for the birthday message.\n*Please try again.*", ephemeral=True)
                return
        else:
            message = "automaton"

      
        if message == "🧒 User Defined":
            modal = self.BirthdayModal(title="Birthday Message Configuration")
            await ctx.send_modal(modal)
        
            try:
                await asyncio.wait_for(modal.wait(), timeout=600.0)
              
                message = modal.message
            except asyncio.TimeoutError:
                await ctx.respond("Good sir, it appears you have taken too long to enter your birthday text configuration.\n*Please try again.*", ephemeral=True)
                return
                               
        
                                
        birthday_key = {"server_id": ctx.guild.id}
                                                             
        # Check if there's an existing document for this server
        if not BD_db.server_birthday_config_data.find_one(birthday_key):
            await ctx.respond(f"Good sir, birthday messages have not been configured for ***{ctx.guild.name}***\n*Now creating this configuration...*", ephemeral=True)
            await asyncio.sleep(5)

            BD_db.server_birthday_config_data.insert_one(
              {
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name,
                "birthday_channel_id": birthday_channel_id,
                "birthday_channel_name": birthday_channel_name,
                "birthday_role_id": birthday_role_id,
                "birthday_role_name": birthday_role_name,
                "message": message
              }
            )
          
            channel_mention = channel.mention if channel else "no channel"
            role_mention = role.mention if role else "no status"
        
            await ctx.respond(f"{ctx.author.mention},\nI have created the birthday configuration for ***{ctx.guild.name}***.\nBirthday messages and statuses will now be issued as follows on users' birthdays:\n> Birthday messages channel: **{channel_mention}**\n> Birthday status assigned: **{role_mention}**\n\n*Please ensure that I have the proper access to the above channel (`Send Messages` permissions) and that I have a higher status (role) than the desired birthday status to ensure proper functionality.*", ephemeral=True)
                                

        else:
            BD_db.server_birthday_config_data.update_one(
              {
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name
              },
              {"$set":{
                "birthday_channel_id": birthday_channel_id,
                "birthday_channel_name": birthday_channel_name,
                "birthday_role_id": birthday_role_id,
                "birthday_role_name": birthday_role_name,
                "message": message
                }
              }
            )
    
            channel_mention = channel.mention if channel else "no channel"
            role_mention = role.mention if role else "no status"
        
            await ctx.respond(f"{ctx.author.mention},\nI have updated the birthday configuration for ***{ctx.guild.name}***.\nBirthday messages and statuses will now be issued as follows on users' birthdays:\n> Birthday messages channel: **{channel_mention}**\n> Birthday status assigned: **{role_mention}**\n\n*Please ensure that I have the proper access to the above channel (`Send Messages` permissions) and that I have a higher status (role) than the desired birthday status to ensure proper functionality.*", ephemeral=True)


    #message text field
    class BirthdayModal(discord.ui.Modal):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.message = None

            self.add_item(discord.ui.InputText(label="Birthday Message", style=discord.InputTextStyle.long, placeholder="Enter message that will be sent on users' birthdays. (Use `/help birthday` for syntax info)"))
  

        async def callback(self, interaction: discord.Interaction):
            self.message = self.children[0].value
            await interaction.response.defer() #acknowledges the interaction before calling self.stop()
            self.stop()

#########################BIRTHDAYS#######################################




  

#############################STREAMING##################################
    @discord.slash_command(
        name="streaming",
        description="Configure the settings for streaming statuses and notifications. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def streaming(
        self,
        ctx,
        streamers: Option(str, name="streamers", description="Receive streaming notifications from and provide streaming status to ALL users or only ONE user.", choices=["👥 ALL", "👤 ONE"]),
        user: Option(discord.Member, name="user", description="User to receive notifications for. (Default: None)", required=False, default=None),
        stream_status: Option(discord.Role, name="stream_status", description="Status the user receives when streaming commences. (Default = None)", required=False, default=None),
        stream_channel: Option(discord.TextChannel, name="stream_channel", description="Channel the embed notifications will be sent to when user begins streaming. (Default: None)", required=False, default=None),
        message: Option(bool, name="message", description="Send a plain text message that is posted above the streaming notification. (Default: True)", required=False, default=True),
        streaming_service: Option(bool, name="streaming_service", description="Title of the streaming embed notification. (Default: OFF)", required=False, default=False),
        streamer_name: Option(bool, name="streamer_name", description="Display the username of the streamer in the embed notification. (Default: OFF)", required=False, default=False),
        stream_title: Option(bool, name="stream_title", description="Display the stream title as a click-able link for the embed notification title. (Default: OFF)", required=False, default=False),
        body: Option(bool, name="body", description="Enable the body text of the streaming embed notification. (Default: True)", required=False, default=True), 
        stream_preview: Option(bool, name="stream_preview", description="Display stream preview in notification. (Default: OFF)", required=False, default=False),
        streamer_photo: Option(bool, name="streamer_photo", description="Display user's profile picture as a thumbnail in embed notification. (Default: OFF)", required=False, default=False),
        color: Option(str, name="color", description="Select a color for the streaming embed notification. (Default: Match Streaming Service)", required=False, choices=["🔴 Red", "🟢 Green", "🍐 Lime Green", "🔵 Blue", "🟡 Yellow", "🟣 Purple", "⚫ Black", "⚪ White", "✅ Match Streaming Service"], default=None),
        custom_color: Option(str, name="custom_color", description="Custom RGB color tuple (0, 0, 0) for the streaming embed notification. (Patron Only)", required=False, default=None),
        whitelisted_status: Option(discord.Role, name="whitelisted_status", description="Status the member must have before they are granted the streaming status. (Default: None)", required=False, default=None),
        blacklisted_status: Option(discord.Role, name="blacklisted_status", description="This status will be ignored when assigning the user the streaming status. (Default: None)", required=False, default=None)
    ):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

        # #ONLY the bot owner can create more than 1 streaming configuration, otherwise cap it at 1 config.
        # if not await self.bot.is_owner(ctx.author):
        #     # Count the number of streaming configs already created
        #     embeds_count = streaming_db.stream_configs.count_documents({"server_id": ctx.guild.id})
        #     if embeds_count >= 1:
        #         await ctx.respond(f"Apologies good sir,\nYou have reached the maximum limit of **1** streaming configuration for {ctx.guild.name}.\n\nConsider editing your configuration using this directive or removing it using my `/streamlist` directive.")
        #         return


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
  

        #check for a custom color (only avaliable to refined and distinguished patrons and support guild)
        if custom_color:
            if ctx.guild.id != support_guild_id:
                if not refined_patron and not distinguished_patron:
                    patron_embed = discord.Embed(title="Patron Feature", description=f"Apologies {ctx.author.mention},\nCustom embed colors for my `/streaming` directive are an exclusive feature available solely to `🎩🎩 Refined Automaton Patrons` and `🎩🎩🎩 Distinguished Automaton Patrons` and is not currently in use for ***{ctx.guild.name}***, good sir.\n\nPlease use my `/patron` directive to learn more information on enabling or upgrading patron (premium) features for ***{ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(130, 130, 130))
          
                    patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
          
                    await ctx.respond(embed=patron_embed, ephemeral=True)
                    return


            #check the custom color
            custom_color = self.check_custom_color(custom_color)

            if custom_color: #if the check is passed
                custom_r = custom_color[0]
                custom_g = custom_color[1]
                custom_b = custom_color[2]
            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\nThe custom color must be a comma-separated RGB color tuple.\n\n**For example:**\n*Black - (0, 0, 0)*\n*White: (255, 255, 255)*\n\n*Please input a valid RGB color tuple and try again.*", ephemeral=True)
                return



      
        # Check if the provided role is lower in hierarchy than the bot's highest role
        bot_top_role = ctx.guild.me.top_role

        if stream_status is None:
            stream_status_id = None
            stream_status_name = None
        else:
            stream_status_id = stream_status.id
            stream_status_name = stream_status.name
      
            if stream_status.position >= bot_top_role.position:
                await ctx.respond(
                    f"Regretfully, {ctx.author.mention}, I am incapable of assigning roles that hold a higher position in the hierarchy than my highest role.\nKindly proceed to the role settings for the server and place me *above* your highest role.", ephemeral=True
                )
                return



        #Check which text options are set to True and send the appropriate modal
        if message or body: #embed body or message are set to True, send the text modal
            modal = self.StreamerModal(message = message, body = body, title="Streamer Text Configuration")
            await ctx.send_modal(modal)
        
            try:
                await asyncio.wait_for(modal.wait(), timeout=600.0)
              
                body = modal.body
                message = modal.message
            except asyncio.TimeoutError:
                await ctx.respond("Good sir, it appears you have taken too long to enter your streamer text configuration.\n*Please try again.*", ephemeral=True)
                return
          
        # set message to None if no message desired
        elif not message and not body:
            message = None
            body = None
      
      
        streamer_dict = {
          "👥 ALL": "all",
          "👤 ONE": "one"
        }

        if streamers is not None and streamers == "👤 ONE" and user:
            streamers = streamer_dict[streamers]

            streamer_username = user.display_name
            streamer_id = user.id

        else:
            streamers = streamer_dict[streamers]

      
        if not user:
            streamer_username = None
            streamer_id = None
            

        if not stream_channel:
            stream_channel_id = None
            stream_channel_name = None
        else:
            stream_channel_id = stream_channel.id
            stream_channel_name = stream_channel.name
            

        #define RGB color codes
        color_codes = {
            "🔴 Red": (255, 0, 0),
            "🟢 Green": (0, 255, 0),
            "🍐 Lime Green": (5, 252, 59),
            "🔵 Blue": (0, 0, 255),
            "🟡 Yellow": (255, 255, 0),
            "🟣 Purple": (152, 3, 252),
            "⚫ Black": (0, 0, 0),
            "⚪ White": (255, 255, 255),
            "✅ Match Streaming Service": (None, None, None)
        }

        if color:
            if color in color_codes:
                r = color_codes[color][0]
                g = color_codes[color][1]
                b = color_codes[color][2]
        else: #set to none if nothing selected (to match streaming status)
            r = None
            g = None
            b = None

      
        #override the default color with the custom rgb values if a custom color is used
        if custom_color:
            r = custom_r
            g = custom_g
            b = custom_b

      
        if not whitelisted_status:
            whitelisted_status_id = None
            whitelisted_status_name = None
        else:
            whitelisted_status_id = whitelisted_status.id
            whitelisted_status_name = whitelisted_status.name


        if not blacklisted_status:
            blacklisted_status_id = None
            blacklisted_status_name = None
        else:
            blacklisted_status_id = blacklisted_status.id
            blacklisted_status_name = blacklisted_status.name
      
      
        stream_key = {"server_id": ctx.guild.id}
        if not streaming_db.stream_configs.find_one(stream_key):
            await ctx.respond(f"Good sir, streaming notifications have not been configured for ***{ctx.guild.name}***.\n*Now creating this configuration...*", ephemeral=True)
            await asyncio.sleep(5)
          
            streaming_db.stream_configs.insert_one(
              {
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name,
                "streamers": streamers,
                "streamer_name": streamer_name,
                "streamer_username": streamer_username,
                "streamer_id": streamer_id,
                "stream_status_id": stream_status_id,
                "stream_status_name": stream_status_name,
                "stream_channel_id": stream_channel_id,
                "stream_channel_name": stream_channel_name,
                "message": message,
                "streaming_service": streaming_service,
                "stream_title": stream_title,
                "body": body,
                "stream_preview": stream_preview,
                "streamer_photo": streamer_photo,
                "color": [r, g, b],
                "whitelisted_status_id": whitelisted_status_id,
                "whitelisted_status_name": whitelisted_status_name,
                "blacklisted_status_id": blacklisted_status_id,
                "blacklisted_status_name": blacklisted_status_name
              }
            )

            await ctx.respond(f"{ctx.author.mention},\nI have created the streaming configuration for ***{ctx.guild.name}***.\nStreaming statuses and notifications will now be distributed accordingly.\nYou may use my `/eventstatus` directive if you wish to disable the events or statuses from deploying.\n*Happy streaming, good sir!*", ephemeral=True)
          
        else:
            streaming_db.stream_configs.update_one(
              {
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name
              },
              {"$set": {
                  "streamers": streamers,
                  "streamer_name": streamer_name,
                  "streamer_username": streamer_username,
                  "streamer_id": streamer_id,
                  "stream_status_id": stream_status_id,
                  "stream_status_name": stream_status_name,
                  "stream_channel_id": stream_channel_id,
                  "stream_channel_name": stream_channel_name,
                  "message": message,
                  "streaming_service": streaming_service,
                  "stream_title": stream_title,
                  "body": body,
                  "stream_preview": stream_preview,
                  "streamer_photo": streamer_photo,
                  "color": [r, g, b],
                  "whitelisted_status_id": whitelisted_status_id,
                  "whitelisted_status_name": whitelisted_status_name,
                  "blacklisted_status_id": blacklisted_status_id,
                  "blacklisted_status_name": blacklisted_status_name
                }
              }
            )
            await ctx.respond(f"{ctx.author.mention},\nI have updated the streaming configuration for ***{ctx.guild.name}***.\nStreaming statuses and notifications will now be distributed accordingly.\nYou may use my `/eventstatus` directive if you wish to disable the events or statuses from deploying.\n*Happy streaming, good sir!*", ephemeral=True)




    #modal that is returned for the body and message streamer notifications
    class StreamerModal(discord.ui.Modal):
        def __init__(self, message, body, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.message = message
            self.body = body

            if self.body and self.message:
                self.add_item(discord.ui.InputText(label="Streamer Message", style=discord.InputTextStyle.long, placeholder="Enter message that will appear above the stream embed. (Use `/help streaming` for syntax info)"))
                self.add_item(discord.ui.InputText(label="Embed Body Text", style=discord.InputTextStyle.long, placeholder="Enter message that will appear in the embed body. (Use `/help streaming` for syntax info)"))
            elif self.message:
                self.add_item(discord.ui.InputText(label="Streamer Message", style=discord.InputTextStyle.long, placeholder="Enter message that will appear above the stream embed. (Use `/help streaming` for syntax info)"))
            else:
                self.add_item(discord.ui.InputText(label="Embed Body Text", style=discord.InputTextStyle.long, placeholder="Enter message that will appear in the embed body. (Use `/help streaming` for syntax info)"))


  
        async def callback(self, interaction: discord.Interaction):
            if self.body and self.message:
                self.message = self.children[0].value
                self.body = self.children[1].value
                await interaction.response.defer() #acknowledges the interaction before calling self.stop()
                self.stop()
            elif self.body:
                self.body = self.children[0].value
                self.message = None
                await interaction.response.defer() #acknowledges the interaction before calling self.stop()
                self.stop()
            else:
                self.message = self.children[0].value
                self.body = None
                await interaction.response.defer() #acknowledges the interaction before calling self.stop()
                self.stop()
              
#############################STREAMING##################################



  

#################################STARBOARD################################
    #this class receives the comma separated list of text channels and returns them
    class TextChannelConverter(commands.Converter):
        async def convert(self, ctx, argument):
            channels = []
            for channel_name in argument.split(","):
                channel = await commands.TextChannelConverter().convert(ctx, channel_name.strip())
                channels.append(channel)
            return channels

    #this class receives the comma separated list of roles and returns them
    class RoleListConverter(commands.Converter):
        async def convert(self, ctx, argument):
            roles = []
            for role_name in argument.split(","):
                role = await commands.RoleConverter().convert(ctx, role_name.strip())
                roles.append(role)
            return roles

  

    @discord.slash_command(
        name="starboard",
        description="Configure the settings for the starboard messages. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def starboard(
        self,
        ctx,
        star_channel: Option(discord.TextChannel, name="star_channel", description="The channel posts will be sent to when they reach the threshold."),
        listen_channels: Option(TextChannelConverter, name="listen_channels", description="Listen for reactions in these channel(s). (Preface channel name with # and separate by commas)", is_list=True),
        threshold: Option(int, name="threshold", description="The number of reactions required for a post to be sent to the specified channel. (Default: 3)", required=False, default=3, min_value=1),
        reaction: Option(str, name="reaction", description="The reaction that will be listened for on posts. (Default: ⭐)", required=False, default=None),
        automaton_reaction: Option(bool, name="automaton_reaction", description="Automaton automatically reacts to messages in the specified channel. (Default: True)", required=False, default=True),
        ignore_author: Option(bool, name="ignore_author", description="Do no count reactions added by the message author. (Default: True)", required=False, Default=True),
        ignored_statuses: Option(RoleListConverter, name="ignored_statuses", description="Ignored statuses for starred posts. (Preface status with @ and separate by commas)", required=False, default=None, is_list=True),
        color: Option(str, name="color", description="Choose the color of the starred post's embed. (Default: ⭐ Gold)", choices=["🔴 Red", "🟢 Green", "🔵 Blue", "⭐ Gold", "🟡 Yellow", "🟣 Purple", "⚫ Black", "⚪ White"], required=False, default=None),
        custom_color: Option(str, name="custom_color", description="Custom RGB color tuple (0, 0, 0) for the starred post's embed. (Patron Only)", required=False, default=None)
    ):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

      
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
  

        #check for a custom color (only avaliable to refined and distinguished patrons and support guild)
        if custom_color:
            if ctx.guild.id != support_guild_id:
                if not refined_patron and not distinguished_patron:
                    patron_embed = discord.Embed(title="Patron Feature", description=f"Apologies {ctx.author.mention},\nCustom embed colors for my `/starboard` directive are an exclusive feature available solely to `🎩🎩 Refined Automaton Patrons` and `🎩🎩🎩 Distinguished Automaton Patrons` and is not currently in use for ***{ctx.guild.name}***, good sir.\n\nPlease use my `/patron` directive to learn more information on enabling or upgrading patron (premium) features for ***{ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(130, 130, 130))
          
                    patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
          
                    await ctx.respond(embed=patron_embed, ephemeral=True)
                    return


            #check the custom color
            custom_color = self.check_custom_color(custom_color)

            if custom_color: #if the check is passed
                custom_r = custom_color[0]
                custom_g = custom_color[1]
                custom_b = custom_color[2]
            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\nThe custom color must be a comma-separated RGB color tuple.\n\n**For example:**\n*Black - (0, 0, 0)*\n*White: (255, 255, 255)*\n\n*Please input a valid RGB color tuple and try again.*", ephemeral=True)
                return

        #default reaction
        if not reaction:
            reaction = "⭐"

        elif reaction == "⭐":
            reaction = reaction

        #custom reaction
        elif reaction and reaction != "⭐":
            if ctx.guild.id != support_guild_id:
                if not refined_patron and not distinguished_patron:
                    patron_embed = discord.Embed(title="Patron Feature", description=f"Apologies {ctx.author.mention},\nCustom reactions for my `/starboard` directive are an exclusive feature available solely to `🎩🎩 Refined Automaton Patrons` and `🎩🎩🎩 Distinguished Automaton Patrons` and is not currently in use for ***{ctx.guild.name}***, good sir.\n\nPlease use my `/patron` directive to learn more information on enabling or upgrading patron (premium) features for ***{ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(130, 130, 130))
          
                    patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
          
                    await ctx.respond(embed=patron_embed, ephemeral=True)
                    return 
      
        
            reactions = reaction.split()
            # check the reaction
            if emoji.is_emoji(reactions[0]): #regular unicode emoji
                reaction = reactions[0]
            elif (emoji.demojize(reactions[0]).startswith("<:") or emoji.demojize(reactions[0]).startswith("<a:")) and emoji.demojize(reactions[0]).endswith(">"):
                await ctx.respond(f"{ctx.author.mention}\nBe aware that your are using a **custom reaction (emoji)** from a guild.\n*Current Reaction:* **{reactions[0]}**\n\nIf this reaction is *NOT* defined in ***{ctx.guild.name}***, the automaton will not be able to automatically react to starboard messages in the specified channels (if that parameter is set to *True*).\n\nIf you would like to use that reaction, please add it to the ***{ctx.guild.name}*** iconography (emoji) list and try again, good sir.", ephemeral=True)
                
                reaction = reactions[0]
            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that you have entered an invalid reaction.\n\n**{reactions[0]}** is not a viable option for this parameter, good sir.\n\n*Please try again.*", ephemeral=True)
                return

      
      
        if listen_channels:
            listen_channels_id = [channel.id for channel in listen_channels]
            listen_channels_name = [channel.name for channel in listen_channels]

        #check to see if the star channel is in the listen channels
        if star_channel in listen_channels:
                await ctx.respond("Apologies, good sir.\nBut, the channel where I send the starred posts cannot be the same as the channels I listen for reactions on.\n*Please try again.*", ephemeral=True)
                return


        #set threshold limit to 1
        if threshold is not None:
            if not isinstance(threshold, int) or threshold < 1:
                await ctx.respond("Apologies good sir,\nThe threshold must be an **integer** that is **greater than or equal to 1**.\n*Please try again.*", ephemeral=True)
                return


        #get the array of ignored roles
        if ignored_statuses:
            ignored_statuses_id = [role.id for role in ignored_statuses]
            ignored_statuses_name = [role.name for role in ignored_statuses]
        else:
            ignored_statuses_id = None
            ignored_statuses_name = None



        # Create starboard config in database
        starboard_messages = []
        async for message in star_channel.history(limit=100):
            starboard_messages.append(message.id)

        #make the starboard messages an array of nothing (to iterate over, otherwise it will give an error)
        if not starboard_messages:
            starboard_messages = [None]

      
        #define RGB color codes
        color_codes = {
            "🔴 Red": (255, 0, 0),
            "🟢 Green": (0, 255, 0),
            "🔵 Blue": (0, 0, 255),
            "⭐ Gold": (255, 223, 0),
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
        else: #set to yellow if none is selected (to match star color)
            r = 255
            g = 223
            b = 0

      
        #override the default color with the custom rgb values if a custom color is used
        if custom_color:
            r = custom_r
            g = custom_g
            b = custom_b
      

      
        starboard_key = {"server_id": ctx.guild.id}
        if not starboard_db.starboard_configs.find_one(starboard_key):
            await ctx.respond(f"Good sir, starboard messages have not been configured for ***{ctx.guild.name}***.\n*Now creating this configuration...*", ephemeral=True)
            await asyncio.sleep(5)
      
            starboard_db.starboard_configs.insert_one(
              {
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name,
                "star_channel_id": star_channel.id,
                "star_channel_name": star_channel.name,
                "listen_channels_id": listen_channels_id,
                "listen_channels_name": listen_channels_name,
                "threshold": threshold,
                "reaction": reaction,
                "automaton_reaction": automaton_reaction,
                "ignore_author": ignore_author,
                "ignored_statuses_id": ignored_statuses_id,
                "ignored_status_name": ignored_statuses_name,
                "color": [r, g, b],
                "starboard_messages": starboard_messages
              }
            )

            await ctx.respond(f"{ctx.author.mention},\nI have created the starboard configuration for ***{ctx.guild.name}***.\nI shall now watch for posts to reach a total of **{threshold}** {reaction} reactions and post them to {star_channel.mention}, good sir.", ephemeral=True)

        else:
     
            starboard_db.starboard_configs.update_one(
              {
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name
              },
              {"$set": {
                "star_channel_id": star_channel.id,
                "star_channel_name": star_channel.name,
                "listen_channels_id": listen_channels_id,
                "listen_channels_name": listen_channels_name,
                "threshold": threshold,
                "reaction": reaction,
                "automaton_reaction": automaton_reaction,
                "ignore_author": ignore_author,
                "ignored_statuses_id": ignored_statuses_id,
                "ignored_status_name": ignored_statuses_name,
                "color": [r, g, b],
                "starboard_messages": starboard_messages
                }
              }
            )
          
            await ctx.respond(f"{ctx.author.mention},\nI have updated the starboard configuration for ***{ctx.guild.name}***.\nI shall now watch for posts to reach a total of **{threshold}** {reaction} reactions and post them to {star_channel.mention}, good sir.", ephemeral=True)

#################################STARBOARD################################







#############################WELCOME##################################
    @discord.slash_command(
        name="welcome",
        description="Configure the settings for the welcome messages. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def welcome(
            self,
            ctx,
            channel: Option(discord.TextChannel, name="channel", description="Select a channel to send the welcome message to.", required=True),
            message: Option(bool, name="message", description="Send a plain text message above the welcome image. (Default: True)", required=False, default=True),
            image_text: Option(bool, name="image_text", description="Send a message on the welcome image. (Default: True)", required=False, default=True),
            image_text_color: Option(str, name="image_text_color", description="Choose the color of the image text to make it stand out better. (Default: ⚪ White)", choices=["🔴 Red", "🟢 Green", "🔵 Blue", "🟡 Yellow", "🟣 Purple", "⚫ Black", "⚪ White"], required=False, default=None),
            custom_image_text_color: Option(str, name="custom_image_text_color", description="Custom RGB color tuple (0, 0, 0) for the image text. (Patron Only)", required=False, default=None),
            font: Option(str, name="font", description="Choose a font to use for the welcome image.", choices=["Arial", "Allura Regular", "Ariana Violeta"], required=False),
            font_size: Option(int, name="font_size", description="Size of the welcome image text font. (Default: 30)", required=False, default=30, min_value=1),
            default_backgrounds: Option(str, name="default_backgrounds", description="Default backgrounds for welcome messages. (Default: ⬛ Black Background)", required=False, default=None, choices=["⬛ Black Background", "🎩 Top Hat and Monocle", "✨ Fancy"]),
            background: Option(str, name="background", description="Custom background image URL for the welcome message.", required=False, default=None),
            default_avatars: Option(str, name="default_avatars", description="Default avatars for welcome messages. (Default: 👨 Member Avatar)", required=False, default=None, choices=["👨 Member Avatar", "🔘 Monocle", "🤵 Suit and Tie"]),
            avatar: Option(str, name="avatar", description="Custom avatar image URL for the welcome message.", required=False, default = None),
            avatar_placement: Option(str, name="avatar_placement", description="Choose the placement of the avatar and text on the background image.", choices=["Left", "Center", "Right", "Top Left", "Top Center", "Top Right", "Bottom Left", "Bottom Center", "Bottom Right"], required=False, default="Center"),
            avatar_outline_color: Option(str, name="avatar_outline_color", description="Choose the color of the avatar outline to make it stand out better. (Default: ⚪ White)", choices=["🔴 Red", "🟢 Green", "🔵 Blue", "🟡 Yellow", "🟣 Purple", "⚫ Black", "⚪ White"], required=False, default=None),
            custom_avatar_outline_color: Option(str, name="custom_avatar_outline_color", description="Custom RGB color tuple (0, 0, 0) for the avatar outline to make it stand out better. (Patron Only)", required=False, default=None),
            on_join_status: Option(discord.Role, name="on_join_status", description="Status that new members receive when joining.", required=False, default=None)
    ):
      
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return


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


        if background or avatar:
            if ctx.guild.id != support_guild_id:
                if not refined_patron and not distinguished_patron:
                    patron_embed = discord.Embed(title="Patron Feature", description=f"Apologies {ctx.author.mention},\nCustom background and avatar images for welcome messages using my `/welcome` directive are an exclusive feature available solely to `🎩🎩 Refined Automaton Patrons` and `🎩🎩🎩 Distinguished Automaton Patrons` and is not currently in use for ***{ctx.guild.name}***, good sir.\n\nPlease use my `/patron` directive to learn more information on enabling or upgrading patron (premium) features for ***{ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(130, 130, 130))
          
                    patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
          
                    await ctx.respond(embed=patron_embed, ephemeral=True)
                    return 

      
      
        #check for a custom image text (only avaliable to refined and distinguished patrons and support guild)
        if image_text is True:
            if ctx.guild.id != support_guild_id:
                if not refined_patron and not distinguished_patron:
                    patron_embed = discord.Embed(title="Patron Feature", description=f"Apologies {ctx.author.mention},\nCustom image text for welcome messages using my `/welcome` directive is an exclusive feature available solely to `🎩🎩 Refined Automaton Patrons` and `🎩🎩🎩 Distinguished Automaton Patrons` and is not currently in use for ***{ctx.guild.name}***, good sir.\n\nPlease use my `/patron` directive to learn more information on enabling or upgrading patron (premium) features for ***{ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(130, 130, 130))
          
                    patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
          
                    await ctx.respond(embed=patron_embed, ephemeral=True)
                    return


              

        #check for a custom color (only avaliable to refined and distinguished patrons and support guild)
        if custom_image_text_color or custom_avatar_outline_color:
            if ctx.guild.id != support_guild_id:
                if not refined_patron and not distinguished_patron:
                    patron_embed = discord.Embed(title="Patron Feature", description=f"Apologies {ctx.author.mention},\nCustom image text and avatar outline colors for welcome messages using my `/welcome` directive are an exclusive feature available solely to `🎩🎩 Refined Automaton Patrons` and `🎩🎩🎩 Distinguished Automaton Patrons` and is not currently in use for ***{ctx.guild.name}***, good sir.\n\nPlease use my `/patron` directive to learn more information on enabling or upgrading patron (premium) features for ***{ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(130, 130, 130))
          
                    patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
          
                    await ctx.respond(embed=patron_embed, ephemeral=True)
                    return


            #check the custom colors
            if custom_image_text_color:
                image_text_color_customized = self.check_custom_color(custom_image_text_color)

            if custom_avatar_outline_color:
                avatar_outline_color_customized = self.check_custom_color(custom_avatar_outline_color)

          
            if image_text_color_customized: #if the check is passed
                custom_image_text_r = image_text_color_customized[0]
                custom_image_text_g = image_text_color_customized[1]
                custom_image_text_b = image_text_color_customized[2]
            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\nThe custom image text color must be a comma-separated RGB color tuple.\n\n**For example:**\n*Black - (0, 0, 0)*\n*White: (255, 255, 255)*\n\n*Please input a valid RGB color tuple and try again.*", ephemeral=True)
                return

          
            if avatar_outline_color_customized: #if the check is passed
                custom_avatar_outline_r = avatar_outline_color_customized[0]
                custom_avatar_outline_g = avatar_outline_color_customized[1]
                custom_avatar_outline_b = avatar_outline_color_customized[2]
            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\nThe custom avatar outline color must be a comma-separated RGB color tuple.\n\n**For example:**\n*Black - (0, 0, 0)*\n*White: (255, 255, 255)*\n\n*Please input a valid RGB color tuple and try again.*", ephemeral=True)
                return


      
      

      
        if on_join_status:
            # Check if the provided role is lower in hierarchy than the bot's highest role
            bot_top_role = ctx.guild.me.top_role
            if on_join_status.position >= bot_top_role.position:
                await ctx.respond(
                    f"Regretfully, {ctx.author.mention}, I am incapable of assigning roles that hold a higher position in the hierarchy than my highest role.\nKindly proceed to the role settings for the server and place me *above* your highest role.", ephemeral=True
                )
                return



        #Check which text options are set to True and send the appropriate modal
        if message or image_text: #image_text or message are set to True, send the text modal
            modal = self.WelcomeModal(message = message, image_text = image_text, title="Welcome Text Configuration")
            await ctx.send_modal(modal)
        
            try:
                await asyncio.wait_for(modal.wait(), timeout=600.0)
              
                image_text = modal.image_text
                message = modal.message
            except asyncio.TimeoutError:
                await ctx.respond("Good sir, it appears you have taken too long to enter your welcome text configuration.\n*Please try again.*", ephemeral=True)
                return
          
        # set message to None if no message desired
        elif not message and not image_text:
            message = None
            image_text = None


        if not image_text:
            # change image text to a default if not the support guild and not a patron
            if ctx.guild.id != support_guild_id:
                if not refined_patron and not distinguished_patron:
                    image_text = "Welcome {member.display_name}"



        #define RGB image text color tuples
        image_text_colors = {
            "🔴 Red": (255, 0, 0),
            "🟢 Green": (0, 255, 0),
            "🔵 Blue": (0, 0, 255),
            "🟡 Yellow": (255, 255, 0),
            "🟣 Purple": (152, 3, 252),
            "⚫ Black": (0, 0, 0),
            "⚪ White": (255, 255, 255)
        }        
    
        if image_text_color is not None:
            if image_text_color in image_text_colors:
                image_text_r = image_text_colors[image_text_color][0]
                image_text_g = image_text_colors[image_text_color][1]
                image_text_b = image_text_colors[image_text_color][2]
            else:
                await ctx.respond(f"**Error**\n*{image_text_color}* is not a viable option, good sir.\n*Please try again.*", ephemeral=True)
        else: #default white
            image_text_r = 255
            image_text_g = 255
            image_text_b = 255


        #override the default image text color with the custom rgb values if a custom color is used
        if custom_image_text_color:
            image_text_r = custom_image_text_r
            image_text_g = custom_image_text_g
            image_text_b = custom_image_text_b

      
    
        #define font files
        fonts = {
          "Arial": "fonts/arial.ttf",
          "Allura Regular": "fonts/Allura-Regular.ttf",
          "Ariana Violeta": "fonts/ArianaVioleta.ttf"
        }   
    
        if font is not None:
            if font in fonts:
                font = fonts[font]
            else:
                await ctx.respond(f"**Error**\n*{font}* is not a viable option, good sir.\n*Please try again.*", ephemeral=True)
        else: #default font to arial
            font = "fonts/arial.ttf"
    


        #default backgrounds
        default_background_dict = {
          "⬛ Black Background": "https://i.imgur.com/QyT4Pho.jpg",
          "🎩 Top Hat and Monocle": "https://i.imgur.com/lIdIiqP.png",
          "✨ Fancy": "https://i.imgur.com/pOYkw1P.jpg"
        }

        if default_backgrounds:
            background_image = default_background_dict[default_backgrounds]
        else:
            background_image = "https://i.imgur.com/QyT4Pho.jpg" #black background default
            


        #overwrite with the custom background if set and check if they are a .jpg, .jpeg, .png
        if background:
            parsed_url = urlparse(background)
            if parsed_url.scheme in ("http", "https"): # check if item is a valid url
                if parsed_url.path.endswith((".jpg", ".png", ".jpeg")): #only allow .jpg, .png, .jpeg files
                    background_image = background

                else:
                    await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that ***{background}*** is not a valid image link.\nThis url must be a direct link to a .JPG, .JPEG, or .PNG image.\n*Please try again.*", ephemeral=True)
                    return

            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that ***{background}*** is not a valid image link.\nThis url must be a direct link to a .JPG, .JPEG, or .PNG image.\n*Please try again.*", ephemeral=True)
                return



        #default avatars
        default_avatar_dict = {
          "👨 Member Avatar": "{member.avatar}",
          "🔘 Monocle": "https://i.imgur.com/SQylaPJ.jpg",
          "🤵 Suit and Tie": "https://i.imgur.com/maf6EJO.jpg"
        }

        if default_avatars:
            avatar_image = default_avatar_dict[default_avatars]
        else:
            avatar_image = "{member.avatar}" #member avatar default


      

        #check to see if the user defined urls are a .jpg, .jpeg, .png
        if avatar:
            parsed_url = urlparse(avatar)
            if parsed_url.scheme in ("http", "https"): # check if item is a valid url
                if parsed_url.path.endswith((".jpg", ".png", ".jpeg")): #only allow .jpg, .png, .jpeg files
                    avatar_image = avatar

                else:
                    await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that ***{avatar}*** is not a valid image link.\nThis url must be a direct link to a .JPG, .JPEG, or .PNG image.\n*Please try again.*", ephemeral=True)
                    return

            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that ***{avatar}*** is not a valid image link.\nThis url must be a direct link to a .JPG, .JPEG, or .PNG image.\n*Please try again.*", ephemeral=True)
                return
    
    
        if avatar_placement is not None:
            placements = {
                "Left": "Left",  # align to the left of the image
                "Center": "Center",  # align to the center of the image
                "Right": "Right",  # align to the right of the image
                "Top Left": "Top Left",  # align to the Top Left of the image
                "Top Center": "Top Center",  # align to the Top Center of the image
                "Top Right": "Top Right",  # align to the Top Right of the image
                "Bottom Left": "Bottom Left",  # align to the Bottom Left of the image
                "Bottom Center": "Bottom Center",  # align to the Bottom Center of the image
                "Bottom Right": "Bottom Right"  # align to the Bottom Right of the image
            }
    
        if avatar_placement is not None:
            if avatar_placement in placements:
                avatar_placement = placements[avatar_placement]
            else:
                await ctx.respond(f"**Error**\n*{avatar_placement}* is not a viable option, good sir.\n*Please try again.*", ephemeral=True)
        else: #default font to arial
            avatar_placement = "Center"
    
        #define RGB outline color tuples
        outline_colors = {
            "🔴 Red": (255, 0, 0),
            "🟢 Green": (0, 255, 0),
            "🔵 Blue": (0, 0, 255),
            "🟡 Yellow": (255, 255, 0),
            "🟣 Purple": (152, 3, 252),
            "⚫ Black": (0, 0, 0),
            "⚪ White": (255, 255, 255)
        }
    
        if avatar_outline_color is not None:
            if avatar_outline_color in outline_colors:
                avatar_outline_r = outline_colors[avatar_outline_color][0]
                avatar_outline_g = outline_colors[avatar_outline_color][1]
                avatar_outline_b = outline_colors[avatar_outline_color][2]
        #set to white as default if none chosen
        else:
            avatar_outline_r = 255
            avatar_outline_g = 255
            avatar_outline_b = 255

      
        #override the default avatar outline color with the custom rgb values if a custom color is used
        if custom_avatar_outline_color:
            avatar_outline_r = custom_avatar_outline_r
            avatar_outline_g = custom_avatar_outline_g
            avatar_outline_b = custom_avatar_outline_b

      

        if on_join_status is not None:
            on_join_status_id = on_join_status.id
            on_join_status_name = on_join_status.name
        else:
            on_join_status_id = None
            on_join_status_name = None



        welcome_key = {"server_id": ctx.guild.id}

        #create new config if none set for server
        if not welcome_db.welcomeconfig.find_one(welcome_key):
            await ctx.respond(f"Good sir, I am unaware of any welcome configurations for ***{ctx.guild.name}***.\n*Now creating this configuration...*", ephemeral=True)
            await asyncio.sleep(5)
  
            welcome_db.welcomeconfig.insert_one(
              {
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name,
                "channel_id": channel.id,
                "channel_name": channel.name,
                "message": message,
                "image_text": image_text,
                "image_text_color": [image_text_r, image_text_g, image_text_b],
                "font": font,
                "font_size": font_size,
                "background": background_image,
                "avatar": avatar_image,
                "avatar_placement": avatar_placement,
                "avatar_outline_color": [avatar_outline_r, avatar_outline_g, avatar_outline_b],
                "on_join_status_id": on_join_status_id,
                "on_join_status_name": on_join_status_name
              }
            )         


            await ctx.respond(f"{ctx.author.mention},\nI have taken into account these configurations, good sir!\nYou may now try `/testwelcome` to view how I shall greet newcomers.", ephemeral=True)

        else:  
            welcome_db.welcomeconfig.update_one(
              {"server_id": ctx.guild.id, "server_name": ctx.guild.name},
              {"$set": {
                  "channel_id": channel.id,
                  "channel_name": channel.name,
                  "message": message,
                  "image_text": image_text,
                  "image_text_color": [image_text_r, image_text_g, image_text_b],
                  "font": font,
                  "font_size": font_size,
                  "background": background_image,
                  "avatar": avatar_image,
                  "avatar_placement": avatar_placement,
                  "avatar_outline_color": [avatar_outline_r, avatar_outline_g, avatar_outline_b],
                  "on_join_status_id": on_join_status_id,
                  "on_join_status_name": on_join_status_name
                }
              }
            )         


            await ctx.respond(f"{ctx.author.mention},\nI have updated the welcome configurations, good sir!\nYou may now try `/testwelcome` to view how I shall greet newcomers.", ephemeral=True)




    #both image_text and message text fields
    class WelcomeModal(discord.ui.Modal):
        def __init__(self, message, image_text, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.message = message
            self.image_text = image_text

            if self.image_text and self.message:
                self.add_item(discord.ui.InputText(label="Welcome Message", style=discord.InputTextStyle.long, placeholder="Enter message that will appear above the welcome image. (Use `/help welcome` for syntax info)"))
                self.add_item(discord.ui.InputText(label="Image Text", style=discord.InputTextStyle.long, placeholder="Enter message that will appear on the welcome image. (Use `/help welcome` for syntax info)", max_length=100))
            elif self.message:
                self.add_item(discord.ui.InputText(label="Welcome Message", style=discord.InputTextStyle.long, placeholder="Enter message that will appear above the welcome image. (Use `/help welcome` for syntax info)"))
            else:
                self.add_item(discord.ui.InputText(label="Image Text", style=discord.InputTextStyle.long, placeholder="Enter message that will appear on the welcome image. (Use `/help welcome` for syntax info)", max_length=100))


  
        async def callback(self, interaction: discord.Interaction):
            if self.image_text and self.message:
                self.message = self.children[0].value
                self.image_text = self.children[1].value
                await interaction.response.defer() #acknowledges the interaction before calling self.stop()
                self.stop()
            elif self.image_text:
                self.image_text = self.children[0].value
                self.message = None
                await interaction.response.defer() #acknowledges the interaction before calling self.stop()
                self.stop()
            else:
                self.message = self.children[0].value
                self.image_text = None
                await interaction.response.defer() #acknowledges the interaction before calling self.stop()
                self.stop()
              
#############################WELCOME##################################



#############################TIMED EMBEDS###################################

    #modal that is returned for the body and message streamer notifications
    class EmbedModal(discord.ui.Modal):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
    
            # if self.title or self.body or self.field_name or self.field_value:
            self.add_item(discord.ui.InputText(label="Embed Title", placeholder="Enter embed title.", style=discord.InputTextStyle.long, required=False, max_length=45))
            self.add_item(discord.ui.InputText(label="Embed Body Text", style=discord.InputTextStyle.long, placeholder="Enter message that will appear in the embed body. (Use `/help embedconfig` for syntax info)", required=False))
            self.add_item(discord.ui.InputText(label="Field Title", placeholder="Enter field title.", style=discord.InputTextStyle.long, required=False, max_length=45))
            self.add_item(discord.ui.InputText(label="Field Text", style=discord.InputTextStyle.long, placeholder="Enter text that will appear in the field of the embed. (Use `/help embedconfig` for syntax info)", required=False, max_length=1000))
    
    
        async def callback(self, interaction: discord.Interaction):
            self.title = self.children[0].value
            self.body = self.children[1].value
            self.field_name = self.children[2].value
            self.field_value = self.children[3].value
            await interaction.response.defer() #acknowledges the interaction before calling self.stop()
            self.stop()


  
    #color checker function
    def check_custom_color(self, custom_color):
        # Check if the custom_color is an RGB tuple or a hex color code
        if ',' in custom_color:
            # RGB color tuple
            try:
                rgb_values = custom_color.split(',')
                if len(rgb_values) == 3:
                    r, g, b = map(int, rgb_values)
                    # Perform additional validation if needed
                    return (r, g, b)
            except ValueError:
                pass

        return None


  
    @discord.slash_command(
        name="timedembeds",
        description="Configure the settings for the timed embed messages (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def timedembeds(
            self, 
            ctx, 
            config_name: Option(str, name="config_name", description="Name of the configuration to update or create.", required=True),
            channel: Option(discord.TextChannel, name="channel", description="Select a channel to send the timed embed message.", required=True),
            send_time: Option(str, name="send_time", description="Time to send the embed. Use the format 'YYYY-MM-DD HH:MM'.", required=True),
            intervaltype: Option(str, name="intervaltype", description = "Interval type to send the embed to the specified channel.", choices=["🔄 Repeating", "☝ One Time"]),
            interval: Option(int, name="interval", description="Interval time (in minutes) to send the message.", required=False, default = None, min_value=0),
            color: Option(str, name="color", description="Select a color for the timed embed. (Default: 🔵 Blue)", required=False, choices=["🔴 Red", "🟢 Green", "🔵 Blue", "🟡 Yellow", "🟣 Purple", "⚫ Black", "⚪ White"], default=None),
            custom_color: Option(str, name="custom_color", description="Custom RGB color tuple (0, 0, 0) for the embed message. (Patron Only)", required=False, default=None),
            thumbnail: Option(str, name="thumbnail", description="Image URL for the thumbnail.", required=False, default=None),
            image: Option(str, name="image", description="Image URL for the embed.", required=False, default=None),
            field_inline: Option(bool, name="field_inline", description="Whether the field should be inline or not.", required=False, default=False)
    ):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

        print("start")
      
      
        #bot owner and those with the distinguished automaton patron (top tier) can create unlimited configurations (everyone else can make a max of 5)
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
          
            if not distinguished_patron:
                # Count the number of timed embeds already created
                embeds_count = embeds_db[f"embeds_config_{ctx.guild.id}"].count_documents({})
              
                if embeds_count >= 5:
                    patron_embed = discord.Embed(title="Patron Feature", description=f"Apologies {ctx.author.mention},\nYou have reached the maximum limit of **5** timed embeds for ***{ctx.guild.name}***.\n\nYou currently are unable to create unlimited embeds in this guild. Therefore, consider removing a timed embed using my `/embedslist` directive.\n\nIf you would like to unlock unlimited configurations when using my `/timedembeds` directive, please use my `/patron` directive to learn more information on enabling or upgrading patron (premium) features for ***{ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(130, 130, 130))
          
                    patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
          
                    await ctx.respond(embed=patron_embed, ephemeral=True)
                    return
  
        

        #check for a custom color (only avaliable to refined and distinguished patrons and support guild)
        if custom_color:
            print("custom color")
            if ctx.guild.id != support_guild_id:
                if not refined_patron and not distinguished_patron:
                    patron_embed = discord.Embed(title="Patron Feature", description=f"Apologies {ctx.author.mention},\nCustom embed colors for my `/timedembeds` directive are an exclusive feature available solely to `🎩🎩 Refined Automaton Patrons` and `🎩🎩🎩 Distinguished Automaton Patrons` and is not currently in use for ***{ctx.guild.name}***, good sir.\n\nPlease use my `/patron` directive to learn more information on enabling or upgrading patron (premium) features for ***{ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(130, 130, 130))
          
                    patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
          
                    await ctx.respond(embed=patron_embed, ephemeral=True)
                    return


            #check the custom color
            custom_color = self.check_custom_color(custom_color)

            if custom_color: #if the check is passed
                custom_r = custom_color[0]
                custom_g = custom_color[1]
                custom_b = custom_color[2]
            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\nThe custom color must be a comma-separated RGB color tuple.\n\n**For example:**\n*Black - (0, 0, 0)*\n*White: (255, 255, 255)*\n\n*Please input a valid RGB color tuple and try again.*", ephemeral=True)
                return
      
        key = {'config_name': config_name}

        #delete config if send_time is set to 0 or None (will always need to be 0 since this is a required option at the moment)
        try:
            config_delete = int(send_time)
            print("config delete")
        except:
            config_delete = 1
            print("couldnt convert send_time")
            pass
        
        if config_delete == 0:
            if embeds_db[f"embeds_config_{ctx.guild.id}"].find_one(key):
                
                embeds_db[f"embeds_config_{ctx.guild.id}"].delete_one(key)

                await ctx.respond(f"{ctx.author.mention}\nI have successfully removed the ***{config_name}*** timed embed configuration from the registry, good sir.", ephemeral=True)
                return
            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\nI was unable to find a Timed Embed configurtion titles ***{config_name}***, good sir.\n*Please ensure the configuration is spelled correctly. The configuration name is also case sensitive.*", ephemeral=True)
                return
        else:
            pass

        #interval type
        intervaltype_dict = {
          "🔄 Repeating": "repeating",
          "☝ One Time": "onetime"
        }

        if intervaltype in intervaltype_dict:
            intervaltype = intervaltype_dict[intervaltype]
        else:
            print("not valid interval type")
            await ctx.respond(f"Apologies {ctx.author.mention},\n{intervaltype} is not a valid option for the interval type.\n*Please try again.*", ephemeral=True)
            return


        #must have an interval set for repeating messages
        if intervaltype == "repeating" and interval == None:
            print("need interval for repeating")
            await ctx.respond(f"Apologies {ctx.author.mention},\nAn interval is required for a repeating message, good sir.\n*Please try again.*", ephemeral=True)
            return


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
                print(color)
                r = color_codes[color][0]
                g = color_codes[color][1]
                b = color_codes[color][2]
            else:
                await ctx.respond(f"Apologies {ctx.author.mention}\n{color} is not a viable option for the timed embed color.\n*Please try again.*", ephemeral=True)
                return
        
        else: #default blue color
            print("default color")
            r = 0
            g = 0
            b = 255


        #override the default color with the custom rgb values if a custom color is used
        if custom_color:
            r = custom_r
            g = custom_g
            b = custom_b


        #send the embed modal to get the text configurations
        modal = self.EmbedModal(title="Embed Text Configuration")
        await ctx.send_modal(modal)
      
        try:
            await asyncio.wait_for(modal.wait(), timeout=600.0)

            title = modal.title
            body = modal.body
            field_name = modal.field_name
            field_value = modal.field_value

      
        except asyncio.TimeoutError:
            print("timed out")
            await ctx.respond("Good sir, it appears you have taken too long to enter your embed text configuration.\n*Please try again.*", ephemeral=True)
            return        

        #check to see if the user defined urls are a .jpg, .jpeg, .png, .gif
        if thumbnail:
            # print("thumbnail start")
            parsed_url = urlparse(thumbnail)
            if parsed_url.scheme in ("http", "https"): # check if item is a valid url
                if parsed_url.path.endswith((".jpg", ".png", ".jpeg", ".gif")): #only allow .jpg, .png, .jpeg, or .gif files
                    thumbnail = thumbnail

                else:
                    await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that ***{thumbnail}*** is not a valid image link.\nThis url must be a direct link to a .JPG, .JPEG, .PNG, or .GIF image.\n*Please try again.*", ephemeral=True)
                    return

            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that ***{thumbnail}*** is not a valid image link.\nThis url must be a direct link to a .JPG, .JPEG, .PNG, or .GIF image.\n*Please try again.*", ephemeral=True)
                return


        #check to see if the user defined urls are a .jpg, .jpeg, .png, .gif
        if image:
            parsed_url = urlparse(image)
            if parsed_url.scheme in ("http", "https"): # check if item is a valid url
                if parsed_url.path.endswith((".jpg", ".png", ".jpeg", ".gif")): #only allow .jpg, .png, .jpeg, or .gif files
                    image = image

                else:
                    await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that ***{image}*** is not a valid image link.\nThis url must be a direct link to a .JPG, .JPEG, .PNG, or .GIF image.\n*Please try again.*", ephemeral=True)
                    return

            else:
                await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that ***{image}*** is not a valid image link.\nThis url must be a direct link to a .JPG, .JPEG, .PNG, or .GIF image.\n*Please try again.*", ephemeral=True)
                return


        #no configurations set
        if embeds_db[f"embeds_config_{ctx.guild.id}"].count_documents({}) == 0:
            print("no docs yet")
            await ctx.respond("I am afraid that no embeds have been set as of yet.\nI am now working to create a new one for you...", ephemeral=True)
            await asyncio.sleep(5)
      

        #new configuration
        if not embeds_db[f"embeds_config_{ctx.guild.id}"].find_one(key):
            await ctx.respond(f"Good sir, there is no embed with the title:\n**{config_name}**\n*Now creating this configuration...*", ephemeral=True)
            await asyncio.sleep(5)
          

        if send_time is not None:
            print(send_time)
            try:
                tz = pytz.timezone('US/Central') # Set timezone to US/Central
            except:
                print("Could not get server timezone.")
                await ctx.respond("**Error:**\nCould not get server timezone.", ephemeral=True)
                return
            try:
                dt = datetime.strptime(send_time, '%Y-%m-%d %H:%M')
                dt = tz.localize(dt) # Localize dt to US/Central timezone

                print(dt)
                
                # Compare send_time with current time
                if dt <= datetime.now(tz):
                    print("less than current time")
                    await ctx.respond("**Error**\nsend_time must be greater than current time.", ephemeral=True)
                    return

                send_time = dt.strftime('%Y-%m-%d %H:%M') # Convert back to string in the same format
          
            except:
                print("invalid format")
                await ctx.respond("**Error:**\nInvalid send_time format. Please use the format 'YYYY-MM-DD HH:MM'.", ephemeral=True)
                return
                
            send_time = send_time
          

        #move data to mongoDB
        embed_key = {"config_name": config_name}

        embedlist_current = embeds_db[f"embeds_config_{ctx.guild.id}"].find_one(embed_key)

        if embedlist_current is None:
            await ctx.respond("Now creating this configuration for you, good sir...", ephemeral=True)
            await asyncio.sleep(5)
            
            embeds_db[f"embeds_config_{ctx.guild.id}"].insert_one(
              {
                "config_name": config_name,
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name,
                "title": title,
                "body": body,
                "channel_id": channel.id,
                "channel_name": channel.name,
                "send_time": send_time,
                "intervaltype": intervaltype,
                "interval": interval,
                "color": [r, g, b],
                "thumbnail": thumbnail,
                "image": image,
                "field_name": field_name,
                "field_value": field_value,
                "field_inline": field_inline
              }
            )

            send_time = datetime.strptime(send_time, '%Y-%m-%d %H:%M')
            send_time = send_time.strftime('%B %d, %Y %I:%M %p')
          
            await ctx.respond(f"Dearest {ctx.author.mention}\nI have configured **{config_name}** for you.\nI will now send this to {channel.mention} on `{send_time}` and repeat myself every **{interval}** minutes.\n\nYou may use `/embedslist` to view and expunge of your currently configured embeds, if you wish.", ephemeral = True)
        
        else:
            await ctx.respond("Now updating this configuration for you, good sir...", ephemeral=True)
            await asyncio.sleep(5)

          
            embeds_db[f"embeds_config_{ctx.guild.id}"].update_one(
                {"config_name": config_name},
                {"$set": {
                    "server_id": ctx.guild.id,
                    "server_name": ctx.guild.name,
                    "title": title,
                    "body": body,
                    "channel_id": channel.id,
                    "channel_name": channel.name,
                    "send_time": send_time,
                    "intervaltype": intervaltype,
                    "interval": interval,
                    "color": [r, g, b],
                    "thumbnail": thumbnail,
                    "image": image,
                    "field_name": field_name,
                    "field_value": field_value,
                    "field_inline": field_inline
                  }
                }
              )
          
            send_time = datetime.strptime(send_time, '%Y-%m-%d %H:%M')
            send_time = send_time.strftime('%B %d, %Y %I:%M %p')
          
            await ctx.respond(f"Dearest {ctx.author.mention}\nI have updated **{config_name}** for you.\nI will now send this to {channel.mention} on `{send_time}` and repeat myself every **{interval}** minutes.\n\nYou may use `/embedslist` to view and expunge of your currently configured embeds, if you wish.", ephemeral = True)

#############################TIMED EMBEDS###################################





def setup(bot):
  bot.add_cog(Configuration(bot))
