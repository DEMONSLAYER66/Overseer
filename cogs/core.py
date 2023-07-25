import discord #needed to interact with discord API
import os #used to import secret keys and such
from discord.ext import commands #used for slash commands
from discord.commands import Option #add options to slash commands
from discord.ext import tasks #used to start various loop tasks

import pymongo #used for database management

import json #used to read and write .json type files
import datetime #for uptime and promotions
import asyncio #used to wait for specified amounts of time

from art import * #this is used for ascii art (glyph command)

from discord.ui import Button, View #used to manually create LINK type buttons on views when sending embeds or messages

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

#########################MONGODB DATABASE################################
# mongoDBpass = os.environ['mongoDBpass'] #load the mongoDB url (retreived from mongoDB upon account creation)
mongoDBpass = os.getenv('mongoDBpass')
client = pymongo.MongoClient(mongoDBpass) # Create a new client and connect to the server
byname_db = client.byname_db #create the byname (nickname) database on MongoDB
appearance_db = client.appearance_db #create the appearance (avatar) database on MongoDB
patrons_db = client.patrons_db #create the patrons database on mongoDB
bump_db = client.bump_db #create the bump (promotion) database on MongoDB
#########################MONGODB DATABASE################################


#this is an array of the server IDs where command testing is done
SERVER_ID = [1088118252200276071, 1117859916749742140]


class Core(commands.Cog):
    # this is a special method that is called when the cog is loaded
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.check_patron_status.start() #update the patron status automatically every minute
        self.start_time = datetime.datetime.utcnow() #start time for the bot (used for uptime)


  #############################GET BOT NICKNAME############################################
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
#############################GET BOT NICKNAME############################################


  
############################# REST (SHUTDOWN) ####################################
    @commands.slash_command(
        name="rest",
        description="Permit the automaton a well-deserved rest (Automaton Owner Only)",
        # guild_ids=SERVER_ID #sync command to only specified guilds (for testing - much faster than global)
        global_command=True #sync command to all guilds the bot is in
    )
    async def rest(self, ctx):
        # Check if the command invoker is the bot owner
        if ctx.author.id == 776986646377267240:
            # current_time = datetime.datetime.utcnow()
            #
            # # Get all cooldown entries from the database (for cooldowns on promotions)
            # cooldown_data_list = bump_db.cooldowns.find()
    
            # if cooldown_data_list:
            #     for cooldown_data in cooldown_data_list:
            #         start_time = cooldown_data['start_time']
            #         elapsed_time = current_time - start_time
            #         cooldown_time = float(cooldown_data['cooldown']) #convert to float type to ensure accuracy
            #         remaining_time = max(0, cooldown_time - float(elapsed_time.total_seconds()))

            #         await ctx.send(f"start time = {start_time}\nelapsed_time = {elapsed_time}\ncooldown_time = {cooldown_time}\nremaining time = {remaining_time}")
            
            #         if remaining_time <= float(0):
            #             # Delete the cooldown time from MongoDB if the cooldown time is found and over
            #             bump_db.cooldowns.delete_one(cooldown_data)
            #         else:
            #             # Save the remaining time to the database
            #             bump_db.cooldowns.update_one({"_id": cooldown_data["_id"]}, {"$set": {"cooldown": remaining_time}})

            await ctx.respond(f"{ctx.author.mention}\nNow taking a rest sir...\n*Have a wonderful day!*", ephemeral=True)
            await self.bot.close() #shutdown bot (graceful) -- currently doesnt work with sparkedhost as they have a "restart server on crash" system in place
        else:
            await ctx.respond(f"Apologies {ctx.author.mention},\nOnly my owner is able to utilize this directive.\n\n*Have a nice day, good sir.*", ephemeral=True)
            return

################################## REST (SHUTDOWN) ####################################

    


##############################BOT UPDATES#####################################
    #this command is used to alert users of updates to the privacy policy, terms of service, or other important updates

    #### YOU HAVE TO UPDATE updates.json file in the json_files to update the field in the embed accordingly and ensure proper notification to users
  
    @discord.slash_command(
        name="updates",
        description="Retrieve the latest important update information regarding the automaton.",
        # guild_ids=SERVER_ID #sync command to only specified guilds (for testing - much faster than global)
        global_command=True #sync command to all guilds the bot is in
    )
    async def updates(self, ctx):
        byname = await self.get_byname(ctx.guild.id)

        with open("json_files/updates.json", "r") as f:
            update = json.load(f)

        bot_version = update.get("Update", {}).get("Bot Version") #get the current bot version
        update_name = update.get("Update", {}).get("Update Name") #get the name of the update
        update_description = update.get("Update", {}).get("Description") #get the description of the update

      
        #provide the link to appropriate Updates file on Github to give users notifications of updates
        github_updates_link = f"https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Updates/Version%20{bot_version}.md"
      
      
        update_embed = discord.Embed(title=f"{byname}\nUpdate Information", description=f"The following is to alert all members of {ctx.guild.name} of the updates and functionality pertaining to myself.\n\n> I have provided a link to my update information.You may visit this link by *clicking the title of this message or following the link below*.\n> Please visit this website posthaste to see vital information that may impact yourself or others.", color = discord.Color.from_rgb(130, 130, 130), url=github_updates_link)

        update_embed.add_field(name=update_name, value=update_description)

        # update_embed.add_field(name="Updates Website", value=f"[Click Here]({github_updates_link})", inline=False)
      
        update_embed.set_thumbnail(url=self.bot.user.avatar.url) #set thumbnail to bot's avatar

        UpdateInfo = discord.ui.Button(emoji='❗', label="View Update Info", url=github_updates_link, style=discord.ButtonStyle.link)
      
        view=View()
        view.add_item(UpdateInfo)

        await ctx.respond(embed=update_embed, view=view)

##############################BOT UPDATES#####################################



  

##################################BOT INFO######################################
    @discord.slash_command(
        name="automaton",
        description="Retrieve information regarding the automaton's creation.",
        # guild_ids=SERVER_ID #this updates the command in only the servers specified
        global_command=True #gives the supports slash commands {/} badge on discord and enables this command for all servers where the bot is present
    )
    async def automaton(self, ctx):
        byname = await self.get_byname(ctx.guild.id) #get the current server's nickname for the bot

        delta = datetime.datetime.utcnow() - self.start_time
        uptime_seconds = delta.total_seconds()

        # Calculate the remaining time in days, hours, minutes, and seconds
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Round the values to integers
        days = int(days)
        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)
        
        # Format the countdown string
        if days > 0:
            uptime = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
        elif hours > 0:
            uptime = f"{hours} hours, {minutes} minutes, {seconds} seconds"
        elif minutes > 0:
            uptime = f"{minutes} minutes, {seconds} seconds"
        else:
            uptime = f"{seconds} seconds"

        # bot invite link
        invite_link = "https://discord.com/api/oauth2/authorize?client_id=1092515783025889383&permissions=3557027031&scope=bot%20applications.commands"

        #get the current bot version
        with open("json_files/updates.json", "r") as f:
            update = json.load(f)

        bot_version = update.get("Update", {}).get("Bot Version") #get the current bot version
        
        #get the servers the bot is in
        bot_servers = []
        for guild in self.bot.guilds:
            bot_servers.append(guild.id)
      
      
        # Create the info embed
        embed = discord.Embed(title="Automaton Information", description=f"{ctx.author.mention},\nThe following is some general information about myself.\n\nI am here to serve you in any way I can, good sir. I am able to provide entertainment and assistance for your every need.", color=discord.Color.blurple())
    
        # Add fields to the embed with bot information
        embed.add_field(name="Original Automaton Name", value="*Lord Bottington*", inline=True)
        embed.add_field(name="Creation Date", value = "`April 3, 2023`", inline=True)
        embed.add_field(name="Version", value=f"`{bot_version}`", inline=True)  # bot's version (from updates json file)
        embed.add_field(name="Uptime", value=f"`{uptime}`", inline=False)
        embed.add_field(name=f"{ctx.guild.name}\nAutomaton Name", value=f"*{byname}*", inline=True)
        embed.add_field(name=f"{ctx.guild.name}\nAutomaton ID", value=f"`{ctx.bot.user.id}`", inline=True)
        embed.add_field(name="Guild Count", value=f"Currently present in `{len(bot_servers):,}` guild{'' if len(bot_servers) == 1 else 's'}.", inline=False)
        embed.add_field(name="❗Invite to Guild", value=f"[Click Here]({invite_link})", inline=True)
        embed.add_field(name="🎩Join Support Guild", value="[Click Here](https://discord.gg/4P6ApdPAF7)", inline=True)
        embed.add_field(name="❓General Information, Privacy Policy, and ToS", value="[Click Here](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/README.md)", inline=False)
        embed.add_field(name="↑ Vote For Me", value="[top.gg](https://top.gg/bot/1092515783025889383/vote) | [discordbotlist](https://discordbotlist.com/bots/lord-bottington/upvote)", inline=False)
        
        embed.set_thumbnail(url=self.bot.user.avatar.url) #thumbnail as bot's avatar
    
        # Set a footer with additional information
        embed.set_footer(text="Lord Bottington | Created by His Lord High Sweezness XxJSweezeyxX")
    
        # Send the embed as a response
        await ctx.respond(embed=embed, ephemeral=True)


##################################BOT INFO######################################




  
###################################PATRON#############################
    @discord.slash_command(
        name="patron",
        description="Enable patron (premium) features for your guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def patron(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may enable the patron (premium) features for ***{ctx.guild.name}***.", ephemeral=True)
            return

        # server ID for The Sweez Gang
        support_guild_id = 1088118252200276071

        patron_url = "https://www.patreon.com/LordBottington"
        patron_info_url = "https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md"
      

        patron_key = {"patron_id": ctx.author.id}
        patron_data = patrons_db.patrons
        patron_lookup = patron_data.find_one(patron_key)

    
        # If no data for the person is found
        if not patron_lookup:
            ### First, need to check if the person has any of the Automaton Patron Roles (Automatically added by the Patreon bot to the user if they have purchased it)
            # Patron role IDs
            automaton_patron_role_id = 1118164335840202803
            refined_automaton_patron_role_id = 1117467508279083139
            distinguished_automaton_patron_role_id = 1118164328575672422
    
            # Retrieve Support Guild Object
            support_guild = self.bot.get_guild(support_guild_id)

            if support_guild:
                target_patron = support_guild.get_member(ctx.author.id) #get the support guild member
                if target_patron:
                    automaton_patron_role = discord.utils.get(target_patron.roles, id=automaton_patron_role_id)
                    refined_automaton_patron_role = discord.utils.get(target_patron.roles, id=refined_automaton_patron_role_id)
                    distinguished_automaton_patron_role = discord.utils.get(target_patron.roles, id=distinguished_automaton_patron_role_id)
                    

                    #User has patron role, set the patron status to True
                    if automaton_patron_role or refined_automaton_patron_role or distinguished_automaton_patron_role:
                        if automaton_patron_role:
                            patron_role = automaton_patron_role.name
                        elif refined_automaton_patron_role:
                            patron_role = refined_automaton_patron_role.name
                        elif distinguished_automaton_patron_role:
                            patron_role = distinguished_automaton_patron_role.name

                      
                        patron_data.insert_one(
                          {
                            "server_id": ctx.guild.id,
                            "server_name": ctx.guild.name,
                            "patron_id": ctx.author.id,
                            "patron_name": ctx.author.display_name,
                            "patron_tier": patron_role,
                            "patron_status": "active" #set the patron status to active
                          }
                        )

                        patron_lookup = patron_data.find_one(patron_key)
                      
                        # Update the patron status to a string with an emoji
                        patron_status = patron_lookup["patron_status"]
                        patron_tier = patron_lookup["patron_tier"]
            
                        status_dict = {
                          "active": "🎩 Current Patron",
                          "inactive": "❌ Not Active"
                        }
            
                        tier_dict = {
                          "Automaton Patron": "🎩 Automaton Patron",
                          "Refined Automaton Patron": "🎩🎩 Refined Automaton Patron",
                          "Distinguished Automaton Patron": "🎩🎩🎩 Distinguished Automaton Patron",
                          "none": "❌ No Tier Purchased"
                        }
            
                        current_patron_status = status_dict[patron_status]
                        current_patron_tier = tier_dict[patron_tier]

                      
                        patron_embed = discord.Embed(title="Patron Features", description=f"Congratulations {ctx.author.mention},\nYou have successfully enabled my patron (premium) features for ***{ctx.guild.name}***, good sir.\n\nYou also currently hold the `{patron_role}` status in {support_guild.name}.\nPlease visit the link below to learn how to maintain these patron features!", color=discord.Color.from_rgb(130, 130, 130))

                        patron_embed.add_field(name="Patron Tier", value=f"`{current_patron_tier}`")
                      
                        patron_embed.add_field(name="Patron Status", value=f"`{current_patron_status}`")
            
                        PatronInfo = discord.ui.Button(emoji='❗', label="View Patron Info", url=patron_info_url, style=discord.ButtonStyle.link)
                      
                        view=View()
                        view.add_item(PatronInfo)
            
                        patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
                      
                        await ctx.respond(embed=patron_embed, view=view, ephemeral=True)
                      
                        return

                    # does not have the patron role in the support guild and has not created the data on mongoDB yet
                    else:
                        patron_embed = discord.Embed(title="Patron Features", description=f"Greetings {ctx.author.mention},\nPlease visit the links below to find out more information on how to begin utilizing patron (premium) features for ***{ctx.guild.name}***, good sir.", color=discord.Color.from_rgb(130, 130, 130))

                        patron_embed.add_field(name="Patron Tier", value="`❌ No Tier Purchased`")
                        patron_embed.add_field(name="Patron Status", value="`❌ Not Active`")
            
                        PatronInfo = discord.ui.Button(emoji='❗', label="View Patron Info", url=patron_info_url, style=discord.ButtonStyle.link)
                        BecomePatron = discord.ui.Button(emoji='💰', label="Become a Patron", url=patron_url, style=discord.ButtonStyle.link)
                      
                        view=View()
                        view.add_item(PatronInfo)
                        view.add_item(BecomePatron)
            
                        patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
                      
                        await ctx.respond(embed=patron_embed, view=view, ephemeral=True)

      
        # user already has patron features enabled
        else:
            # Patron role IDs
            automaton_patron_role_id = 1118164335840202803
            refined_automaton_patron_role_id = 1117467508279083139
            distinguished_automaton_patron_role_id = 1118164328575672422

            patron_guild_id = patron_lookup["server_id"]

            if patron_guild_id == "":
                patron_guild_id = ctx.guild.id

            patron_guild = self.bot.get_guild(patron_guild_id)
    
            # Retrieve Support Guild Object
            support_guild = self.bot.get_guild(support_guild_id)

            
            if ctx.guild.id != patron_guild_id:
                description = f"Apologies {ctx.author.mention},\nIt appears that you already utilizing patron (premium) features in ***{patron_guild.name}***.\n\nYou may only enable patron features for ***1*** guild at a time.\nPlease contact an administrator in the Support Guild to enable patron features for ***{ctx.guild.name}***, if you desire."
                view=None
              
            else:
                if support_guild:
                    target_patron = support_guild.get_member(ctx.author.id) #get the support guild
                    if target_patron:
                        automaton_patron_role = discord.utils.get(target_patron.roles, id=automaton_patron_role_id)
                        refined_automaton_patron_role = discord.utils.get(target_patron.roles, id=refined_automaton_patron_role_id)
                        distinguished_automaton_patron_role = discord.utils.get(target_patron.roles, id=distinguished_automaton_patron_role_id)
                        
    
                        #User has patron role, set the patron status to True
                        if automaton_patron_role or refined_automaton_patron_role or distinguished_automaton_patron_role:
                            if automaton_patron_role:
                                patron_role = automaton_patron_role.name
                            elif refined_automaton_patron_role:
                                patron_role = refined_automaton_patron_role.name
                            elif distinguished_automaton_patron_role:
                                patron_role = distinguished_automaton_patron_role.name
                        else:
                            patron_role = None
    
                        #User has patron role, set the patron status to active
                        if patron_role:
                            patron_data.update_one(
                              patron_key,
                              {"$set": {
                                "server_id": patron_guild_id,
                                "server_name": patron_guild.name,
                                "patron_tier": patron_role,
                                "patron_status": "active"
                                }
                              }
                            )

                          
                            description = f"Congratulations {ctx.author.mention},\nPatron (premium) features are enabled for ***{patron_guild.name}***, good sir.\n\nYou also currently hold the `{patron_role}` status in {support_guild.name}.\nPlease visit the link below to learn how to maintain these patron features!"
    
                            PatronInfo = discord.ui.Button(emoji='❗', label="View Patron Info", url=patron_info_url, style=discord.ButtonStyle.link)
                          
                            view=View()
                            view.add_item(PatronInfo)
                      
    
                        else:
                            description = f"Apologies {ctx.author.mention},\nIt appears that my patron (premium) features have been disabled for ***{patron_guild.name}*** as you do not currently hold a patron status in {support_guild.name}.\n\nPlease visit the links below to find out more information on how to reinstate my patron (premium) features for ***{ctx.guild.name}***, good sir."
    
                            PatronInfo = discord.ui.Button(emoji='❗', label="View Patron Info", url=patron_info_url, style=discord.ButtonStyle.link)
                            BecomePatron = discord.ui.Button(emoji='💰', label="Become a Patron", url=patron_url, style=discord.ButtonStyle.link)
                          
                            view=View()
                            view.add_item(PatronInfo)
                            view.add_item(BecomePatron)
                          
    
                            #remove the patron data from mongoDB
                            patron_data.delete_one(patron_key)

            patron_lookup = patron_data.find_one(patron_key)

            if patron_lookup:
                # Update the patron status to a string with an emoji
                patron_status = patron_lookup["patron_status"]
                patron_tier = patron_lookup["patron_tier"]
    
                status_dict = {
                  "active": "🎩 Current Patron",
                  "inactive": "❌ Not Active"
                }
    
                tier_dict = {
                  "Automaton Patron": "🎩 Automaton Patron",
                  "Refined Automaton Patron": "🎩🎩 Refined Automaton Patron",
                  "Distinguished Automaton Patron": "🎩🎩🎩 Distinguished Automaton Patron",
                  "none": "❌ No Tier Purchased"
                }
    
                current_patron_status = status_dict[patron_status]
                current_patron_tier = tier_dict[patron_tier]

            #patron data removed because the user did not pay or removed their role in the support guild
            else:
                current_patron_status = "❌ Not Active"
                current_patron_tier = "❌ No Tier Purchased"             


            # Update the patron embed
            patron_embed = discord.Embed(title="Patron Features", description=description, color=discord.Color.from_rgb(130, 130, 130))

            patron_embed.add_field(name="Patron Tier", value=f"`{current_patron_tier}`")
            patron_embed.add_field(name="Patron Status", value=f"`{current_patron_status}`")

            patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
          
            await ctx.respond(embed=patron_embed, view=view, ephemeral=True)

              

###################################PATRON#############################




########################CHECK PATRON STATUS TASK#######################
    # Check for updates to patron status every 60 seconds
    @tasks.loop(seconds=60)
    async def check_patron_status(self):
        if not self.bot.is_ready():
            # only run once the bot is ready
            return

        patron_url = "https://www.patreon.com/LordBottington"
        patron_info_url = "https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Patron%20(Premium)%20Features.md"
      
        # server ID for The Sweez Gang
        support_guild_id = 1088118252200276071

        # Get the support guild
        support_guild = self.bot.get_guild(support_guild_id)

        # Retrieve all the members in the support guild
        members = support_guild.members
      
        # Patron role IDs for the support guild
        automaton_patron_role_id = 1118164335840202803
        refined_automaton_patron_role_id = 1117467508279083139
        distinguished_automaton_patron_role_id = 1118164328575672422

        #get the roles from the support guild
        automaton_patron_role = support_guild.get_role(automaton_patron_role_id)
        refined_automaton_patron_role = support_guild.get_role(refined_automaton_patron_role_id)
        distinguished_automaton_patron_role = support_guild.get_role(distinguished_automaton_patron_role_id)
    
      
        patron_data = patrons_db.patrons #database of patrons on mongoDB

        # Iterate over the members in the support guild and check their roles
        for member in members:
            patron_key = {"patron_id": member.id}

            ### Automaton patron
            if automaton_patron_role in member.roles:
                patron_info = patron_data.find_one(patron_key)

                if patron_info and patron_info["patron_tier"] != automaton_patron_role.name:
                    patron_data.update_one(
                      patron_key,
                      {"$set": {
                        "patron_tier": automaton_patron_role.name,
                        "patron_status": "active"
                        }
                      }
                    )

                    patron_embed = discord.Embed(title="Patron Features", description=f"Congratulations ***{member.display_name}***,\nYour status in {support_guild.name} has been updated to `{automaton_patron_role.name}`, good sir.\n\nReturn to your desired guild and use my `/patron` directive to enable `🎩 {automaton_patron_role.name}` patron features for your guild so that you may enjoy my exclusive services I have to offer!\n\n*Please visit the link below to learn how to maintain these patron features!*", color=discord.Color.from_rgb(130, 130, 130))
    
                    PatronInfo = discord.ui.Button(emoji='❗', label="View Patron Info", url=patron_info_url, style=discord.ButtonStyle.link)
                  
                    view=View()
                    view.add_item(PatronInfo)
    
                    patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
    
                    await member.send(embed=patron_embed, view=view)
              
                  
                if not patron_info:
                    patron_data.insert_one(
                      {
                        "server_id": "",
                        "server_name": "",
                        "patron_id": member.id,
                        "patron_name": member.display_name,
                        "patron_tier": automaton_patron_role.name,
                        "patron_status": "active" #set the patron status to active
                      }
                    )

                    patron_embed = discord.Embed(title="Patron Features", description=f"Congratulations ***{member.display_name}***,\nYou have received the `{automaton_patron_role.name}` status in {support_guild.name} for becoming a patron of Lord Bottington, good sir.\n\nReturn to your desired guild and use my `/patron` directive to enable `🎩 {automaton_patron_role.name}` patron features for your guild so that you may enjoy my exclusive services I have to offer!\n\n*Please visit the link below to learn how to maintain these patron features!*", color=discord.Color.from_rgb(130, 130, 130))
    
                    PatronInfo = discord.ui.Button(emoji='❗', label="View Patron Info", url=patron_info_url, style=discord.ButtonStyle.link)
                  
                    view=View()
                    view.add_item(PatronInfo)
    
                    patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
    
                    await member.send(embed=patron_embed, view=view)

            ### Refined automaton patron
            elif refined_automaton_patron_role in member.roles:
                patron_info = patron_data.find_one(patron_key)

                if patron_info and patron_info["patron_tier"] != refined_automaton_patron_role.name:
                    patron_data.update_one(
                      patron_key,
                      {"$set": {
                        "patron_tier": refined_automaton_patron_role.name,
                        "patron_status": "active"
                        }
                      }
                    )
                  
                    patron_embed = discord.Embed(title="Patron Features", description=f"Congratulations ***{member.display_name}***,\nYour status in {support_guild.name} has been updated to `{refined_automaton_patron_role.name}`, good sir.\n\nReturn to your desired guild and use my `/patron` directive to enable `🎩🎩 {refined_automaton_patron_role.name}` patron features for your guild so that you may enjoy my exclusive services I have to offer!\n\n*Please visit the link below to learn how to maintain these patron features!*", color=discord.Color.from_rgb(130, 130, 130))
    
                    PatronInfo = discord.ui.Button(emoji='❗', label="View Patron Info", url=patron_info_url, style=discord.ButtonStyle.link)
                  
                    view=View()
                    view.add_item(PatronInfo)
    
                    patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
    
                    await member.send(embed=patron_embed, view=view)

                
                if not patron_info:
                    patron_data.insert_one(
                      {
                        "server_id": "",
                        "server_name": "",
                        "patron_id": member.id,
                        "patron_name": member.display_name,
                        "patron_tier": refined_automaton_patron_role.name,
                        "patron_status": "active" #set the patron status to active
                      }
                    )
              
                    patron_embed = discord.Embed(title="Patron Features", description=f"Congratulations ***{member.display_name}***,\nYou have received the `{refined_automaton_patron_role.name}` status in {support_guild.name} for becoming a patron of Lord Bottington, good sir.\n\nReturn to your desired guild and use my `/patron` directive to enable `🎩🎩 {refined_automaton_patron_role.name}` patron features for your guild so that you may enjoy my exclusive services I have to offer!\n\n*Please visit the link below to learn how to maintain these patron features!*", color=discord.Color.from_rgb(130, 130, 130))
    
                    PatronInfo = discord.ui.Button(emoji='❗', label="View Patron Info", url=patron_info_url, style=discord.ButtonStyle.link)
                  
                    view=View()
                    view.add_item(PatronInfo)
    
                    patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
    
                    await member.send(embed=patron_embed, view=view)
          

            ### Distinguished automaton patron
            elif distinguished_automaton_patron_role in member.roles:
                patron_info = patron_data.find_one(patron_key)

                if patron_info and patron_info["patron_tier"] != distinguished_automaton_patron_role.name:
                    patron_data.update_one(
                      patron_key,
                      {"$set": {
                        "patron_tier": distinguished_automaton_patron_role.name,
                        "patron_status": "active"
                        }
                      }
                    )

                    patron_embed = discord.Embed(title="Patron Features", description=f"Congratulations ***{member.display_name}***,\nYour status in {support_guild.name} has been updated to `{distinguished_automaton_patron_role.name}`, good sir.\n\nReturn to your desired guild and use my `/patron` directive to enable `🎩🎩🎩 {distinguished_automaton_patron_role.name}` patron features for your guild so that you may enjoy my exclusive services I have to offer!\n\n*Please visit the link below to learn how to maintain these patron features!*", color=discord.Color.from_rgb(130, 130, 130))
    
                    PatronInfo = discord.ui.Button(emoji='❗', label="View Patron Info", url=patron_info_url, style=discord.ButtonStyle.link)
                  
                    view=View()
                    view.add_item(PatronInfo)
    
                    patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
    
                    await member.send(embed=patron_embed, view=view)
              
                if not patron_info:
                    patron_data.insert_one(
                      {
                        "server_id": "",
                        "server_name": "",
                        "patron_id": member.id,
                        "patron_name": member.display_name,
                        "patron_tier": distinguished_automaton_patron_role.name,
                        "patron_status": "active" #set the patron status to active
                      }
                    )

                    patron_embed = discord.Embed(title="Patron Features", description=f"Congratulations ***{member.display_name}***,\nYou have received the `{distinguished_automaton_patron_role.name}` status in {support_guild.name} for becoming a patron of Lord Bottington, good sir.\n\nReturn to your desired guild and use my `/patron` directive to enable `🎩🎩🎩 {distinguished_automaton_patron_role.name}` patron features for your guild so that you may enjoy my exclusive services I have to offer!\n\n*Please visit the link below to learn how to maintain these patron features!*", color=discord.Color.from_rgb(130, 130, 130))
    
                    PatronInfo = discord.ui.Button(emoji='❗', label="View Patron Info", url=patron_info_url, style=discord.ButtonStyle.link)
                  
                    view=View()
                    view.add_item(PatronInfo)
    
                    patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
    
                    await member.send(embed=patron_embed, view=view)

          

            ### None of the patron roles for the member
            else:
                patron_info = patron_data.find_one(patron_key)

                # remove the patron info from the database (because they no longer have the required role)
                if patron_info:
                    patron_data.delete_one(patron_key)

                    patron_embed = discord.Embed(title="Patron Features", description=f"Apologies ***{member.display_name}***,\nIt appears that your patron status in {support_guild.name} is no longer active.\nTherefore, you will no longer be able to take advantage of Lord Bottington's patron (premium) features for your guild.\n\n*Please visit the following links to discover how to reinstate these exclusive features for your guild, good sir.*", color=discord.Color.from_rgb(130, 130, 130))
    
                    PatronInfo = discord.ui.Button(emoji='❗', label="View Patron Info", url=patron_info_url, style=discord.ButtonStyle.link)
                    BecomePatron = discord.ui.Button(emoji='💰', label="Become a Patron", url=patron_url, style=discord.ButtonStyle.link)
                  
                    view=View()
                    view.add_item(PatronInfo)
                    view.add_item(BecomePatron)
    
                    patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
    
                    await member.send(embed=patron_embed, view=view)
              

                # Otherwise, do nothing because the member does not have patron features
                else:
                    pass


########################CHECK PATRON STATUS TASK#######################

  
  

  
############################BOT JOIN AND LEAVE################################
    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        # get the guild object
        guild = self.bot.get_guild(guild.id)

        #link to README.md file on Github
        general_info_github = "https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/README.md"

        help_command = self.bot.get_application_command("help")

        first_embed = discord.Embed(title="Lord Bottington", description=f"Good day, dear members of ***{guild.name}***.\nI am **Lord Bottington**, at your service.\n\nPlease allow me to offer my assistance in any way I can.\nMay I suggest perusing my list of directives by utilizing my </{help_command.name}:{help_command.id}> directive, good sir?\n\nYou may also visit the link below to view other general information related to myself...", color=discord.Color.from_rgb(130, 130, 130), url=general_info_github)

        first_embed.set_thumbnail(url=self.bot.user.avatar.url)

        GeneralInfo = discord.ui.Button(emoji='❗', label="General Information", url=general_info_github, style=discord.ButtonStyle.link)
      
        view=View()
        view.add_item(GeneralInfo)

      
        # Loop through all channels until a good channel is found. Implemented due to removal of default channel
        # Iterate through the channels in the guild
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                try:
                    await channel.send(embed=first_embed, view=view)
                    break  # Exit the loop after sending the message
                except discord.Forbidden:
                    # Handle the case where the bot doesn't have permission to send messages in the channel
                    continue
      


#################################BOT JOIN AND LEAVE#############################



  

#####################ENABLE/DISABLE CONFIG#######################
    class ConfigView(discord.ui.View):
        def __init__(self, ctx):
            super().__init__(timeout=120) # specify the timeout here (give enough time to use help command if necessary)
            self.ctx = ctx
          
            # self.mongoDBpass = os.environ['mongoDBpass']
            self.mongoDBpass = os.getenv('mongoDBpass')
            self.client = pymongo.MongoClient(self.mongoDBpass)
            self.event_handler_db = self.client.event_handler_db
      
        @discord.ui.button(label="Begin", style=discord.ButtonStyle.success)
        async def begin_button_callback(self, button, interaction):
            self.clear_items()

            event_doc = self.event_handler_db.events.find_one({"server_id": self.ctx.guild.id})

            if event_doc is None:
                await self.ctx.respond(f"Good sir, it appears that all events are enabled and no event configurations have been set for **{self.ctx.guild.name}**.\n*I have created and updated your configuration accordingly...*", ephemeral=True)
              
                self.event_handler_db.events.insert_one(
                  {
                    "server_id": self.ctx.guild.id,
                    "server_name": self.ctx.guild.name,
                    "welcome_messages": "Enabled",
                    "birthday_messages": "Enabled",
                    "timed_embeds": "Enabled",
                    "livestreams": "Enabled",
                    "starboard": "Enabled",
                    "autopurge": "Enabled",
                    "autosatire": "Enabled",
                    "promotions_reminders": "Enabled"
                  }
                )
                event_doc = self.event_handler_db.events.find_one({"server_id": self.ctx.guild.id})


            # retrieve the values from the document
            welcome_messages = event_doc["welcome_messages"]
            birthday_messages = event_doc["birthday_messages"]
            timed_embeds = event_doc["timed_embeds"]
            livestreams = event_doc["livestreams"]
            starboard = event_doc["starboard"]
            autopurge = event_doc["autopurge"]
            autosatire = event_doc["autosatire"]
            promotions_reminders = event_doc["promotions_reminders"]
          
            #Welcome message button
            welcome_messages_button = discord.ui.Button(
              emoji="👋",
              label=f"Welcome Messages ({welcome_messages})",
              style=discord.ButtonStyle.success if welcome_messages == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"WelcomeMessages_{welcome_messages}"
            )

            #Birthday message button
            birthday_messages_button = discord.ui.Button(
              emoji="🎉",
              label=f"Birthday Messages ({birthday_messages})",
              style=discord.ButtonStyle.success if birthday_messages == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"BirthdayMessages_{birthday_messages}"
            )

            #Timed embeds button
            timed_embeds_button = discord.ui.Button(
              emoji="⏱",
              label=f"Timed Embeds ({timed_embeds})",
              style=discord.ButtonStyle.success if timed_embeds == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"TimedEmbeds_{timed_embeds}"
            )

            #Livestreams button
            livestreams_button = discord.ui.Button(
              emoji="🔴",
              label=f"Livestreams ({livestreams})",
              style=discord.ButtonStyle.success if livestreams == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"Livestreams_{livestreams}"
            )


            #Starboard button
            starboard_button = discord.ui.Button(
              emoji="⭐",
              label=f"Starboard ({starboard})",
              style=discord.ButtonStyle.success if starboard == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"Starboard_{starboard}"
            )

            #Autopurge button
            autopurge_button = discord.ui.Button(
              emoji="🗑️",
              label=f"Autopurge ({autopurge})",
              style=discord.ButtonStyle.success if autopurge == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"Autopurge_{autopurge}"
            )

            #Autosatire button
            autosatire_button = discord.ui.Button(
              emoji="😂",
              label=f"Auto-Satire ({autosatire})",
              style=discord.ButtonStyle.success if autosatire == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"Autosatire_{autosatire}"
            )

            #Promotion Message Reminders Button
            promo_messages_button = discord.ui.Button(
              emoji="🚀",
              label=f"Promotion Reminders ({promotions_reminders})",
              style=discord.ButtonStyle.success if promotions_reminders == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"PromotionReminders_{promotions_reminders}"
            )
          

            # Exit button
            exit_button = discord.ui.Button(
                emoji="🚶‍♂️",
                label="Exit",
                style=discord.ButtonStyle.danger,
                custom_id="Exit"
            )

          
            welcome_messages_button.callback = self.event_button_click
            birthday_messages_button.callback = self.event_button_click
            timed_embeds_button.callback = self.event_button_click
            livestreams_button.callback = self.event_button_click
            starboard_button.callback = self.event_button_click
            autopurge_button.callback = self.event_button_click
            autosatire_button.callback = self.event_button_click
            promo_messages_button.callback = self.event_button_click
            exit_button.callback = self.exit_interaction
          
            self.add_item(welcome_messages_button)
            self.add_item(birthday_messages_button)
            self.add_item(timed_embeds_button)
            self.add_item(livestreams_button)
            self.add_item(starboard_button)
            self.add_item(autopurge_button)
            self.add_item(autosatire_button)
            self.add_item(promo_messages_button)
            self.add_item(exit_button)
    
            await interaction.response.edit_message(content="Please select an event to enable or disable.", view=self)


      

        async def event_button_click(self, interaction):
            event_doc = self.event_handler_db.events.find_one({"server_id": self.ctx.guild.id})

            # retrieve the values from the document
            welcome_messages = event_doc["welcome_messages"]
            birthday_messages = event_doc["birthday_messages"]
            timed_embeds = event_doc["timed_embeds"]
            livestreams = event_doc["livestreams"]
            starboard = event_doc["starboard"]
            autopurge = event_doc["autopurge"]
            autosatire = event_doc["autosatire"]
            promotions_reminders = event_doc["promotions_reminders"]
          
            event_dict = {
                "WelcomeMessages": welcome_messages,
                "BirthdayMessages": birthday_messages,
                "TimedEmbeds": timed_embeds,
                "Livestreams": livestreams,
                "Starboard": starboard,
                "Autopurge": autopurge,
                "Autosatire": autosatire,
                "PromotionReminders": promotions_reminders
            }
            
            # retrieve the data from the first interaction
            custom_id = interaction.data["custom_id"]
            
            event_name, event_status = custom_id.split("_")
            
            if event_name in event_dict:
                event_dict[event_name] = "Enabled" if event_status == "Disabled" else "Disabled"
            
            self.event_handler_db.events.update_one(
                {
                    "server_id": self.ctx.guild.id,
                    "server_name": self.ctx.guild.name,
                },
                {"$set": {
                    "welcome_messages": event_dict["WelcomeMessages"],
                    "birthday_messages": event_dict["BirthdayMessages"],
                    "timed_embeds": event_dict["TimedEmbeds"],
                    "livestreams": event_dict["Livestreams"],
                    "starboard": event_dict["Starboard"],
                    "autopurge": event_dict["Autopurge"],
                    "autosatire": event_dict["Autosatire"],
                    "promotions_reminders": event_dict["PromotionReminders"]
                    }
                }
            )

            self.clear_items()

            # retrieve the values from the document
            welcome_messages = event_dict["WelcomeMessages"]
            birthday_messages = event_dict["BirthdayMessages"]
            timed_embeds = event_dict["TimedEmbeds"]
            livestreams = event_dict["Livestreams"]
            starboard = event_dict["Starboard"]
            autopurge = event_dict["Autopurge"]
            autosatire = event_dict["Autosatire"]
            promotions_reminders = event_dict["PromotionReminders"]

          
            # update the button labels based on the new values
            welcome_messages_button = discord.ui.Button(
                emoji="👋",
                label=f"Welcome Messages ({welcome_messages})",
                style=discord.ButtonStyle.success if welcome_messages == "Enabled" else discord.ButtonStyle.danger,
                custom_id=f"WelcomeMessages_{welcome_messages}"
            )
            
            birthday_messages_button = discord.ui.Button(
                emoji="🎉",
                label=f"Birthday Messages ({birthday_messages})",
                style=discord.ButtonStyle.success if birthday_messages == "Enabled" else discord.ButtonStyle.danger,
                custom_id=f"BirthdayMessages_{birthday_messages}"
            )
            
            timed_embeds_button = discord.ui.Button(
                emoji="⏱",
                label=f"Timed Embeds ({timed_embeds})",
                style=discord.ButtonStyle.success if timed_embeds == "Enabled" else discord.ButtonStyle.danger,
                custom_id=f"TimedEmbeds_{timed_embeds}"
            )

            #Livestreams button
            livestreams_button = discord.ui.Button(
              emoji="🔴",
              label=f"Livestreams ({livestreams})",
              style=discord.ButtonStyle.success if livestreams == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"Livestreams_{livestreams}"
            )


            #Starboard button
            starboard_button = discord.ui.Button(
              emoji="⭐",
              label=f"Starboard ({starboard})",
              style=discord.ButtonStyle.success if starboard == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"Starboard_{starboard}"
            )

            #Autopurge button
            autopurge_button = discord.ui.Button(
              emoji="🗑️",
              label=f"Autopurge ({autopurge})",
              style=discord.ButtonStyle.success if autopurge == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"Autopurge_{autopurge}"
            )

            #Autosatire button
            autosatire_button = discord.ui.Button(
              emoji="😂",
              label=f"Auto-Satire ({autosatire})",
              style=discord.ButtonStyle.success if autosatire == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"Autosatire_{autosatire}"
            )

            #Promotion Message Reminders Button
            promo_messages_button = discord.ui.Button(
              emoji="🚀",
              label=f"Promotion Reminders ({promotions_reminders})",
              style=discord.ButtonStyle.success if promotions_reminders == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"PromotionReminders_{promotions_reminders}"
            )
          
         
            # Exit button
            exit_button = discord.ui.Button(
                emoji="🚶‍♂️",
                label="Exit",
                style=discord.ButtonStyle.danger,
                custom_id="Exit"
            )
          
            welcome_messages_button.callback = self.event_button_second_click
            birthday_messages_button.callback = self.event_button_second_click
            timed_embeds_button.callback = self.event_button_second_click
            livestreams_button.callback = self.event_button_second_click
            starboard_button.callback = self.event_button_second_click
            autopurge_button.callback = self.event_button_second_click
            autosatire_button.callback = self.event_button_second_click
            promo_messages_button.callback = self.event_button_second_click
            exit_button.callback = self.exit_interaction
          
            self.add_item(welcome_messages_button)
            self.add_item(birthday_messages_button)
            self.add_item(timed_embeds_button)
            self.add_item(livestreams_button)
            self.add_item(starboard_button)
            self.add_item(autopurge_button)
            self.add_item(autosatire_button)
            self.add_item(promo_messages_button)
            self.add_item(exit_button)
          
            await interaction.response.edit_message(content="Please select an event to enable or disable.", view=self)



      
        async def event_button_second_click(self, interaction):
            event_doc = self.event_handler_db.events.find_one({"server_id": self.ctx.guild.id})

            # retrieve the values from the document
            welcome_messages = event_doc["welcome_messages"]
            birthday_messages = event_doc["birthday_messages"]
            timed_embeds = event_doc["timed_embeds"]
            livestreams = event_doc["livestreams"]
            starboard = event_doc["starboard"]
            autopurge = event_doc["autopurge"]
            autosatire = event_doc["autosatire"]
            promotions_reminders = event_doc["promotions_reminders"]
          
            event_dict = {
                "WelcomeMessages": welcome_messages,
                "BirthdayMessages": birthday_messages,
                "TimedEmbeds": timed_embeds,
                "Livestreams": livestreams,
                "Starboard": starboard,
                "Autopurge": autopurge,
                "Autosatire": autosatire,
                "PromotionReminders": promotions_reminders
            }
            
            # retrieve the data from the first interaction
            custom_id = interaction.data["custom_id"]
            
            event_name, event_status = custom_id.split("_")
            
            if event_name in event_dict:
                event_dict[event_name] = "Enabled" if event_status == "Disabled" else "Disabled"
            
            self.event_handler_db.events.update_one(
                {
                    "server_id": self.ctx.guild.id,
                    "server_name": self.ctx.guild.name,
                },
                {"$set": {
                    "welcome_messages": event_dict["WelcomeMessages"],
                    "birthday_messages": event_dict["BirthdayMessages"],
                    "timed_embeds": event_dict["TimedEmbeds"],
                    "livestreams": event_dict["Livestreams"],
                    "starboard": event_dict["Starboard"],
                    "autopurge": event_dict["Autopurge"],
                    "autosatire": event_dict["Autosatire"],
                    "promotions_reminders": event_dict["PromotionReminders"],
                    }
                }
            )

            self.clear_items()

            # retrieve the values from the document
            welcome_messages = event_dict["WelcomeMessages"]
            birthday_messages = event_dict["BirthdayMessages"]
            timed_embeds = event_dict["TimedEmbeds"]
            livestreams = event_dict["Livestreams"]
            starboard = event_dict["Starboard"]
            autopurge = event_dict["Autopurge"]
            autosatire = event_dict["Autosatire"]
            promotions_reminders = event_dict["PromotionReminders"]
          
          
            # update the button labels based on the new values
            welcome_messages_button = discord.ui.Button(
                emoji="👋",
                label=f"Welcome Messages ({welcome_messages})",
                style=discord.ButtonStyle.success if welcome_messages == "Enabled" else discord.ButtonStyle.danger,
                custom_id=f"WelcomeMessages_{welcome_messages}"
            )
            
            birthday_messages_button = discord.ui.Button(
                emoji="🎉",
                label=f"Birthday Messages ({birthday_messages})",
                style=discord.ButtonStyle.success if birthday_messages == "Enabled" else discord.ButtonStyle.danger,
                custom_id=f"BirthdayMessages_{birthday_messages}"
            )
            
            timed_embeds_button = discord.ui.Button(
                emoji="⏱",
                label=f"Timed Embeds ({timed_embeds})",
                style=discord.ButtonStyle.success if timed_embeds == "Enabled" else discord.ButtonStyle.danger,
                custom_id=f"TimedEmbeds_{timed_embeds}"
            )

            #Livestreams button
            livestreams_button = discord.ui.Button(
              emoji="🔴",
              label=f"Livestreams ({livestreams})",
              style=discord.ButtonStyle.success if livestreams == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"Livestreams_{livestreams}"
            )

            #Starboard button
            starboard_button = discord.ui.Button(
              emoji="⭐",
              label=f"Starboard ({starboard})",
              style=discord.ButtonStyle.success if starboard == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"Starboard_{starboard}"
            )

            #Autopurge button
            autopurge_button = discord.ui.Button(
              emoji="🗑️",
              label=f"Autopurge ({autopurge})",
              style=discord.ButtonStyle.success if autopurge == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"Autopurge_{autopurge}"
            )

            #Autosatire button
            autosatire_button = discord.ui.Button(
              emoji="😂",
              label=f"Auto-Satire ({autosatire})",
              style=discord.ButtonStyle.success if autosatire == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"Autosatire_{autosatire}"
            )

            #Promotion Message Reminders Button
            promo_messages_button = discord.ui.Button(
              emoji="🚀",
              label=f"Promotion Reminders ({promotions_reminders})",
              style=discord.ButtonStyle.success if promotions_reminders == "Enabled" else discord.ButtonStyle.danger,
              custom_id=f"PromotionReminders_{promotions_reminders}"
            )
          
            # Exit button
            exit_button = discord.ui.Button(
                emoji="🚶‍♂️",
                label="Exit",
                style=discord.ButtonStyle.danger,
                custom_id="Exit"
            )
          
            welcome_messages_button.callback = self.event_button_click
            birthday_messages_button.callback = self.event_button_click
            timed_embeds_button.callback = self.event_button_click
            livestreams_button.callback = self.event_button_click
            starboard_button.callback = self.event_button_click
            autopurge_button.callback = self.event_button_click
            autosatire_button.callback = self.event_button_click
            promo_messages_button.callback = self.event_button_click
            exit_button.callback = self.exit_interaction
          
            self.add_item(welcome_messages_button)
            self.add_item(birthday_messages_button)
            self.add_item(timed_embeds_button)
            self.add_item(livestreams_button)
            self.add_item(starboard_button)
            self.add_item(autopurge_button)
            self.add_item(autosatire_button)
            self.add_item(promo_messages_button)
            self.add_item(exit_button)
          
            await interaction.response.edit_message(content="Please select an event to enable or disable.", view=self)

        async def exit_interaction(self, interaction):
            await self.message.edit(content="Now storing your event settings...", view=None)
            await asyncio.sleep(5)
              
            await self.message.edit(content=f"{interaction.user.mention}\nI have stored your event settings.", view=None)
            self.stop()
      
      
        #create the exit button
        @discord.ui.button(emoji="🚶‍♂️", label="Exit", style=discord.ButtonStyle.danger)
        async def initial_exit_callback(self, button, interaction):
            await self.message.edit(content="Now storing your event settings...", view=None)
            await asyncio.sleep(5)
          
            await self.message.edit(content=f"{interaction.user.mention}\nI have stored your event settings.", view=None)
            self.stop()

        #Timeout message
        async def on_timeout(self):
            for child in self.children:
                child.disabled = True
              
            await self.message.edit(content="Apologies good sir, it seems you have taken an ample amount of time to respond.\nNow storing your current event settings...", view=self)
            await asyncio.sleep(5)

            try:
                await self.message.edit(content="I have stored your current event settings...", view=None)
            except discord.errors.NotFound: #if message deleted before timeout
                pass
              
            self.stop()
      

    @discord.slash_command(
        name="eventhandler",
        description="Configure the automaton's usage and directives. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command=True
    )
    # @commands.has_permissions(administrator=True)
    async def eventhandler(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.")
            return
      
        view = self.ConfigView(ctx)
        await ctx.respond(f"{ctx.author.mention},\nPlease configure the events that I will perform in {ctx.guild.name} using the following prompts.\n\nBy default, all events are **ENABLED**.\nHowever, It is important to note that, when *disabled*, even if these events are configured using their corresponding directives, the events themselves will **not be performed**.\n*I have this functionality so as to give full customization to those that I serve.*", view=view, ephemeral=True)
#####################ENABLE/DISABLE CONFIG#######################




###########################HELP################################
    @discord.slash_command(
        name="help",
        description="Receive a list of OR assistance with the automaton's directives -- organized by category.", 
        # guild_ids=SERVER_ID
        global_command=True
    )
    async def help(self, ctx, directive: Option(str, name="directive", description="Directive to receive assistance with.", required=False, default=None)):
        #get command help longer descriptions
        with open("json_files/command_help.json", "r") as f:
            self.command_help = json.load(f)

        #get the bot's nickname from mongoDB
        byname = await self.get_byname(ctx.guild.id)

        #full list of directives found on Github
        github_full_directives_list = "https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/Full%20Directive%20List.md"


        #dictionary of Cog names (with emojis)
        category_dict = {
          "🌐 Core": "Core",
          "⚙️ Configuration": "Configuration",
          "🎉 Fun": "Fun",
          "🎮 Games": "Games",
          "🛡️ Moderation": "Moderation",
          "📊 Status": "Status",
          "🔧 Utility": "Utility",
          "💰 Marketplace": "Marketplace"
        }

        #dictionary of Cog descriptions
        category_description_dict = {
          "🌐 Core": f"This category is for directives related to general information for *{byname}* or to assist you in changing the functionality or appearance of *{byname}*.",
          "⚙️ Configuration": f"This category is for directives related to configuring the functionality of the various automated directives of *{byname}*.\n\nAll directives within this category are for users who have *administrative privileges* within your guild, as they alter your guild in some way.",
          "🎉 Fun": "This category is for directives related to providing members of your guild with entertainment.",
          "🎮 Games": f"This category is for directives related to providing members of your guild with entertainment through challenging games.\n\nMembers of your guild may face each other *OR* myself (*{byname}*) in the following games with varying degrees of difficulty.\n\nEach member has the chance to earn `🪙 Shillings` to spend on various items in the shop and show off to others in your guild!\n\nI will also keep up with the top ***10*** winners and earners for each of the games within your guild, which you may view using my `/toptalent` directive, if you desire.",
          "🛡️ Moderation": "This category is for directives related to providing you the ability to moderate your guild and its members.\n\nAll directives within this category are for users who have *administrative privileges* within your guild, as they alter your guild or its members in some way.\n\nNotifications for the following directives will be sent to the channel specified when using the `/moderation` directive.",
          "📊 Status": "This category is for directives related to updating your status or information within the guild in order to receive specific statuses or information related to this.",
          "🔧 Utility": "This category is for directives related to performing various utility actions for your guild, such as helping facilitate gift giving (giveaways) or managing the iconography (emojis) for your guild.",
          "💰 Marketplace": "This category is for directives related to buying and selling items within the guild.\n\nMembers may use their `🪙 Shillings` earned from winning games to purchase and sell items.\nThey may then trade with others or display their winnings using these directives."
        }


        #get the list of commands and application commands
        commands = []
        for cmd in self.bot.commands:
            commands.append(cmd.name)
        
        for app_command in self.bot.application_commands:
            commands.append(app_command.name)

        #list of commands
        command_names_list = commands


        #organize by Cog
        cog_names_list = [cog.qualified_name for cog in self.bot.cogs.values()]
        cog_dict = {name: {'commands': [], 'app_commands': []} for name in cog_names_list}
        uncategorized_commands = []


        for command in self.bot.commands:
            if command.cog and command.name in command_names_list:
                cog_dict[command.cog.qualified_name]['commands'].append(command.name)
            else:
                uncategorized_commands.append(command.name)
  
        for app_command in self.bot.application_commands:
            if app_command.cog and app_command.name in command_names_list:
                cog_dict[app_command.cog.qualified_name]['app_commands'].append(app_command)


        #if a directive is specified
        if directive:
            if directive in command_names_list and directive in self.bot.commands:
                command = self.bot.get_command(directive)

                help_embed = discord.Embed(title=f"__**Directives for {byname}**__", color = discord.Color.from_rgb(130, 130, 130), url=github_full_directives_list)
              
                help_embed.add_field(name=command.name, value=command.help if command.help else "No description available.")

                await ctx.respond(embed=help_embed, ephemeral=True)
              
                return
              
            else:
                await self.directive_help(ctx, directive, byname, github_full_directives_list, command_names_list)
    
                return


        #help embed
        help_embed = discord.Embed(title=f"__**Directives for {byname}**__", description=f"{ctx.author.mention}\nSelect a category to view the directives for by utilizing the select menu below, good sir.", color = discord.Color.from_rgb(130, 130, 130), url=github_full_directives_list)

        # bot invite link
        invite_link = "https://discord.com/api/oauth2/authorize?client_id=1092515783025889383&permissions=3557027031&scope=bot%20applications.commands"

        help_embed.add_field(name="", value=f"Please use the link provided in the title *OR* [Click Here]({github_full_directives_list}) for a full list of directives for *{byname}*, good sir.\n\nYou may also utilize `/help directive-name` for an in-depth analysis of a specific directive, if you desire.", inline=False)
        
        help_embed.add_field(name="❗Invite to Guild", value=f"[Click Here]({invite_link})", inline=True)
        help_embed.add_field(name="🎩Join Support Guild", value="[Click Here](https://discord.gg/4P6ApdPAF7)", inline=True)
        help_embed.add_field(name="❓General Information, Privacy Policy, and ToS", value="[Click Here](https://github.com/xxjsweezeyxx/Lord-Bottington/blob/main/README.md)", inline=False)
        help_embed.add_field(name="↑ Vote For Me", value="[top.gg](https://top.gg/bot/1092515783025889383/vote) | [discordbotlist](https://discordbotlist.com/bots/lord-bottington/upvote)", inline=False)
        
        help_embed.set_thumbnail(url=self.bot.user.avatar.url) #make the thumbnail the bot's avatar

        #only admins can post the help for everyone to view
        if not ctx.author.guild_permissions.administrator:
            hide_status = True
        else:
            hide_status = False
      
        await ctx.respond(embed=help_embed, view=self.HelpView(ctx, byname, github_full_directives_list, category_dict, category_description_dict, cog_dict), ephemeral=hide_status)




  

    # send an embed with the specific help for the directive and cool effects
    async def directive_help(self, ctx, directive, byname, full_directives_list, command_names_list):
      

        app_command_names_list = [x.name for x in self.bot.application_commands]
        if directive in app_command_names_list and directive in command_names_list:
            hide_status=True #make message ephemeral (hidden)
            app_command = self.bot.get_application_command(directive)

            help_embed = discord.Embed(title=f"__**Directives for {byname}**__", color = discord.Color.from_rgb(130, 130, 130), url=f"{full_directives_list}#{app_command.name.lower()}")

          
            ##########add cool effects to the help commands###################
            if app_command.name.lower() == "pictorialize":
                #This is the pictorialize name in emojis
                iconify_app_command = ":slight_smile::regional_indicator_p::regional_indicator_i::regional_indicator_c::regional_indicator_t::regional_indicator_o::regional_indicator_r::regional_indicator_i::regional_indicator_a::regional_indicator_l::regional_indicator_i::regional_indicator_z::regional_indicator_e::open_mouth:\n:grinning::regional_indicator_h::regional_indicator_e::regional_indicator_l::regional_indicator_p::stuck_out_tongue:"
                #thumbnail set to top hat emoji gif (goodsir emoji)
                help_embed.set_thumbnail(url="https://i.imgur.com/pfRNFyk.gif")
                help_embed.set_image(url="https://i.imgur.com/p2RygwY.png")
                await ctx.respond(f"{iconify_app_command}", ephemeral=True)
            
            
            #set the thumbnail to a spinning star gif
            elif app_command.name.lower() == "starboard":
                help_embed.set_thumbnail(url="https://i.imgur.com/l6kTLDv.gif")
            
            #set the thumbnail to a video game controller gif
            elif app_command.name.lower() == "streaming" or app_command.name.lower() == "playerinfo":
                help_embed.set_thumbnail(url="https://i.imgur.com/YBuzl2j.gif")
            
            #welcome gif as thumbnail
            elif app_command.name.lower() == "welcome" or app_command.name.lower() == "testwelcome":
                help_embed.set_thumbnail(url="https://i.imgur.com/XkBGmax.gif")
            
            elif app_command.name.lower() == "birthday" or app_command.name.lower() == "setbirthday" or app_command.name.lower() == "getbirthday" or app_command.name.lower() == "birthdaylist" or app_command.name.lower() == "removebirthday":
                help_embed.set_thumbnail(url="https://i.imgur.com/tYenTsy.gif")
            
            
            #set the thumbnail to a weather gif
            elif app_command.name.lower() == "weather":
                help_embed.set_thumbnail(url="https://i.imgur.com/0bVfhYI.gif")
            
            
            #set the thumbnail to a gift gif
            elif app_command.name.lower() == "giftgiving":
                help_embed.set_thumbnail(url="https://i.imgur.com/EdJvsIt.gif")
            
            #set thumbnail to emoji guy raising top hat
            elif app_command.name.lower() == "iconography":
                help_embed.set_thumbnail(url="https://i.imgur.com/UHfZkeT.gif")
            
            #set thumbnail to trash gif
            elif app_command.name.lower() == "purge" or app_command.name.lower() == "autopurge" or app_command.name.lower() == "autopurgelist":
                help_embed.set_thumbnail(url="https://i.imgur.com/0Os7c99.gif")
            
            #set thumbnail to timer gif
            elif app_command.name.lower() == "timedembeds":
                help_embed.set_thumbnail(url="https://i.imgur.com/FzUsO01.gif")
            
            
            # set thumbnail to ascii uncle sam and send glyph help in ascii art above help command
            elif app_command.name.lower() == "glyph":
                ascii_text = text2art("Glyph Help", font = "larry3d")
                help_embed.set_thumbnail(url="https://i.imgur.com/rVtl3zz.gif")
                help_embed.set_image(url="https://i.imgur.com/qql6oKh.png")
                await ctx.respond(f"```{ascii_text}```", ephemeral=True)
            
            # set thumbnail to dice roll gif
            elif app_command.name.lower() == "roll":
                help_embed.set_thumbnail(url="https://i.imgur.com/XQxn8Bh.gif")   
            
            # set thumbnail to rock paper scissors gif
            elif app_command.name.lower() == "rps":
                help_embed.set_thumbnail(url="https://i.imgur.com/ExzGCb4.gif")
            
            # set thumbnail to connect four GIF
            elif app_command.name.lower() == "connectfour":
                help_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")
            
            # set thumbnail to tictactoe gif
            elif app_command.name.lower() == "tictactoe":
                help_embed.set_thumbnail(url="https://i.imgur.com/G34stnX.gif")
            
            # set thumbnail to wumpus PNG
            elif app_command.name.lower() == "wumpus":
                help_embed.set_thumbnail(url="https://i.imgur.com/0DdDso7.png")
            
            # set thumbnail to rainbow PNG
            elif app_command.name.lower() == "mastermind":
                help_embed.set_thumbnail(url="https://i.imgur.com/Ce6Y2Ee.gif")
            
            # set thumbnail to crystal ball GIF
            elif app_command.name.lower() == "crystalball":
                help_embed.set_thumbnail(url="https://i.imgur.com/oW25bhm.gif")
            
            # set thumbnail to battleship GIF
            elif app_command.name.lower() == "battleship":
                help_embed.set_thumbnail(url="https://i.imgur.com/WVTMctu.gif")

            # set thumbnail to money GIF
            elif app_command.name.lower() == "shop" or app_command.name.lower() == "earnings":
                help_embed.set_thumbnail(url="https://i.imgur.com/ydqcPtI.gif")

            #set to avatar picture of Steve
            elif app_command.name.lower() == "minotar":
                help_embed.set_thumbnail(url="https://i.imgur.com/x21wIDt.png")

            elif app_command.name.lower() == "autosatire" or app_command.name.lower() == "satireimage":
                help_embed.set_thumbnail(url="https://i.imgur.com/UMsxnFb.gif")

            #set the thumbnail to the bot's avatar
            else:
                help_embed.set_thumbnail(url=self.bot.user.avatar.url)
            
            ##########add cool effects to the help commands###################
            
            
            #short description
            if app_command.description:
                command_description=app_command.description
            else:
                command_description="No description available for this directive."
            
            #check to see if a longer description is available from .json file
            if self.command_help.get(directive, {}).get("long_description_contd2"):
                command_long_description = self.command_help[directive]["long_description"]
                command_long_description_contd = self.command_help[directive]["long_description_contd"]
                command_long_description_contd2 = self.command_help[directive]["long_description_contd2"]                  
            
                help_embed.add_field(
                    name = f"</{app_command.name}:{app_command.id}>",
                    value=f"> {command_description}"
                )
            
                help_embed.add_field(
                    name="",
                    value=f"{command_long_description}",
                    inline=False
                )       
              
                help_embed.add_field(
                    name="",
                    value=f"{command_long_description_contd}",
                    inline=False
                )
            
                help_embed.add_field(
                    name="",
                    value=f"{command_long_description_contd2}",
                    inline=False
                )
            
              
            elif self.command_help.get(directive, {}).get("long_description_contd"):
                command_long_description = self.command_help[directive]["long_description"]
                command_long_description_contd = self.command_help[directive]["long_description_contd"]
                          
              
                help_embed.add_field(
                    name = f"</{app_command.name}:{app_command.id}>",
                    value=f"> {command_description}"
                )
            
                help_embed.add_field(
                    name="",
                    value=f"{command_long_description}",
                    inline=False
                )       
              
                help_embed.add_field(
                    name="",
                    value=f"{command_long_description_contd}",
                    inline=False
                )       
            
            
            elif self.command_help.get(directive, {}).get("long_description"):
                command_long_description = self.command_help[directive]["long_description"]
            
              
                help_embed.add_field(
                    name=f"</{app_command.name}:{app_command.id}>",
                    value=f"> {command_description}"
                )
            
                help_embed.add_field(
                    name="",
                    value=f"{command_long_description}",
                    inline=False
                )
            
            
            else:
                help_embed.add_field(
                    name=f"</{app_command.name}:{app_command.id}>",
                    value=f"> {command_description}"
                )
        
        elif directive in app_command_names_list and directive not in command_names_list:
            help_embed = discord.Embed(title=f"__**Directives for {byname}**__", color = discord.Color.from_rgb(130, 130, 130), url=f"{full_directives_list}")

            help_embed.set_thumbnail(url=self.bot.user.avatar.url)
          
            help_embed.add_field(
                name="Help Error",
                value=f"Apologies good sir,\nIt appears that the **{directive}** directive is restricted for you.\n*Please try again or contact an administrator if more help is required.*")                
        
        else:
            help_embed = discord.Embed(title=f"__**Directives for {byname}**__", color = discord.Color.from_rgb(130, 130, 130), url=f"{full_directives_list}")

            help_embed.set_thumbnail(url=self.bot.user.avatar.url)
          
            help_embed.add_field(
                name="Help Error",
                value=f"Apologies good sir,\nIt appears that I could not locate a directive entitled **{directive}**.\n*Please try again.*")
        
        
        await ctx.respond(embed=help_embed, ephemeral=True)


  
    ## Select menu for help function
    class HelpView(discord.ui.View):
        def __init__(self, ctx, byname, full_directives_list, category_dict, category_description_dict, cog_dict):
            super().__init__(timeout=120) #set the timeout
            self.ctx = ctx #intialize the context
            self.byname = byname
            self.full_directives_list = full_directives_list #Github full directives list link
            self.category_dict = category_dict
            self.category_description_dict = category_description_dict
            self.cog_dict = cog_dict

        # Handle timeout (e.g., if no selections are made within the specified timeout)
        async def on_timeout(self):
            self.disable_all_items()

            try:
                await self.message.edit(view=None)
            except discord.errors.NotFound: #if message is deleted before the timeout
                pass

            self.stop()


        #select menu options and callback
        @discord.ui.select(
          placeholder="Choose a directive category.",
          min_values=1,
          max_values=1,
          options = [
            discord.SelectOption(emoji='🌐', label="Core", description="Basic directives."),
            discord.SelectOption(emoji='⚙️', label="Configuration", description="Automaton configuration directives."),
            discord.SelectOption(emoji='🎉', label="Fun", description="Entertaining directives."),
            discord.SelectOption(emoji='🎮', label="Games", description="Interactive and challenging directives."),
            discord.SelectOption(emoji='🛡️', label="Moderation", description="Moderation directives for the guild."),
            discord.SelectOption(emoji='📊', label="Status", description="Status related directives."),
            discord.SelectOption(emoji='🔧', label="Utility", description="Helpful directives."),
            discord.SelectOption(emoji='💰', label="Marketplace", description="Directives for buying and selling items.")
          ]  
        )
        async def select_callback(self, select, interaction):
            #only author can use the select menu
            if interaction.user.id != self.ctx.author.id:
                return

            await interaction.response.defer() #acknowledge the interaction

            #loop through the selections and find the matching emoji to pair up with the Cog name
            selected_option = next(option for option in select.options if option.value == select.values[0])
            emoji = selected_option.emoji #get the emoji
            category = f"{emoji} {select.values[0]}" #create the category for the commands
          
            category_name = self.category_dict[category]
            category_description = self.category_description_dict[category]

            #help embed
            help_embed = discord.Embed(title=f"__**Directives for {self.byname}**__", description=f"`{category}`\n{category_description}", color = discord.Color.from_rgb(130, 130, 130), url=f"{self.full_directives_list}#{category_name.lower()}")
    
            commands_list = self.cog_dict[category_name]['commands']
            app_commands_list = self.cog_dict[category_name]['app_commands']
            if commands_list or app_commands_list:
                for command in app_commands_list:
                    help_embed.add_field(name=f"</{command.name}:{command.id}>", value=f"[Directive Help]({self.full_directives_list}#{command.name.lower()})")
                    #f"[/{command}]({self.full_directives_list}#{command.lower()})"
    
    
            help_embed.add_field(name="", value=f"Please use the links provided for each directive for specific help *OR* [Click Here]({self.full_directives_list}#{category_name.lower()}) for a list of directives within this category, good sir.\n\nYou may also utilize `/help directive-name` for an in-depth analysis of a specific directive, if you desire.", inline=False)
            help_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url) #make the thumbnail the bot's avatar
    
          
            await self.message.edit(embed=help_embed, view=self)
  

###########################HELP################################ 




  



#############################PING###############################
    #ping the bot to see its latency
    @discord.slash_command(
        name = "ping",
        description="Inquire of the latency of the automaton.",
        # guild_ids=SERVER_ID
        global_command=True
    )
    async def ping(self, ctx):
        byname = await self.get_byname(ctx.guild.id)
      
        ping = round(self.bot.latency * 1000)
        ping_embed = discord.Embed(title=f"{byname}\nLatency", description=f"Pardon me, {ctx.author.mention}, but my current latency is `{ping} milliseconds`.\n\n*I do hope that satisfies your query, good sir.*", color=discord.Color.from_rgb(130, 130, 130))

        ping_embed.set_thumbnail(url=self.bot.user.avatar.url)
      
        await ctx.respond(embed=ping_embed, ephemeral=True)
#############################PING###############################




  
################################NICKNAME##########################
    #Change bot's nickname
    @discord.slash_command(
        name="byname",
        description="Change the byname (nickname) of the automaton. (Admin only)",
        # guild_ids=SERVER_ID
        global_command=True
    )
    # @commands.has_permissions(administrator=True)
    async def byname(self, ctx, byname: Option(str, name="byname", description="Set a byname (nickname) for the automaton. (No entry sets the default of Lord Bottington)", required=False, default=None)):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return
      
      
        ##### PATRON FEATURE (always available in support guild)
        # server ID for The Sweez Gang
        support_guild_id = 1088118252200276071

        if ctx.guild.id != support_guild_id:
            if not patrons_db.patrons.find_one({"server_id": ctx.guild.id}):
                patron_embed = discord.Embed(title="Patron Feature Directive", description=f"Apologies {ctx.author.mention},\n`/byname` is an exclusive feature available solely to patrons and is not currently in use for ***{ctx.guild.name}***, good sir.\n\nPlease use my `/patron` directive to learn more information on enabling patron (premium) features for ***{ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(130, 130, 130))
    
                patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
    
                await ctx.respond(embed=patron_embed, ephemeral=True)
                return

  
        if byname is None:
            byname = "Lord Bottington"
            await ctx.guild.me.edit(nick=None)
        else:
            byname = byname
            await ctx.guild.me.edit(nick = byname)

        byname_key = {"server_id": ctx.guild.id}
        if not byname_db.bynames.find_one(byname_key):
            await ctx.respond(f"Good sir, I am unaware of any changes to my byname as of yet within **{ctx.guild.name}**\n*Now changing this for you...*", ephemeral=True)
            await asyncio.sleep(5)

            #update the mongoDB database with the nickname
            byname_db.bynames.insert_one(
              {
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name,
                "byname": byname
              }
            )
          
            await ctx.respond(f"{ctx.author.mention},\nI have taken into account your byname suggestion!\n**{byname}** is ready to serve ***{ctx.guild.name}***.", ephemeral=True)

        else:
            if byname != "Lord Bottington":
                byname_db.bynames.update_one(
                  {
                    "server_id": ctx.guild.id,
                    "server_name": ctx.guild.name
                  },
                  {"$set": {"byname": byname}}
                )
            else:
                byname_db.bynames.delete_one({"server_id": ctx.guild.id})

            await ctx.respond(f"{ctx.author.mention},\nI have updated my byname!\n**{byname}** is ready to serve ***{ctx.guild.name}***.", ephemeral=True)
          
################################NICKNAME##########################



def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Core(bot)) # add the cog to the bot
