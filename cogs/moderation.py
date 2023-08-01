import os #used to import secret keys and such
import discord #needed to interact with discord API
from discord.ext import commands #used for slash commands
from discord.commands import Option  # add options to slash commands
import pymongo #used for database management
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env
load_dotenv()


#########################MONGODB DATABASE##################################
# mongoDBpass = os.environ['mongoDBpass'] #load the mongoDB url (retreived from mongoDB upon account creation)
mongoDBpass = os.getenv('mongoDBpass')
client = pymongo.MongoClient(mongoDBpass) # Create a new client and connect to the server
moderation_db = client.moderation_db #create the moderation_db on mongoDB
#########################MONGODB DATABASE##################################

#this is an array of the server IDs where command testing is done
SERVER_ID = [1088118252200276071, 1117859916749742140]


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warning_threshold = 3  # Number of warnings before a ban


################################KICK###################################
    @discord.slash_command(
        name="remove",
        description="The automaton will remove (kick) a member from the guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def remove(self, ctx, member: Option(discord.Member, name="member", description="Member to remove from the guild."), *, reason: Option(str, name="reason", description="Reason for removing member from the guild.", required=False, default=None)):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

        if member == self.bot.user:
            await ctx.respond(f"Apologies {ctx.author.mention},\nI am unable to `remove (kick)` myself from ***{ctx.guild.name}***.\n*Please try again.*", ephemeral=True)
            return

        moderation_key = {"server_id": member.guild.id}
        moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
        if moderation_config:
            channel = self.bot.get_channel(moderation_config["channel_id"])
          
            await ctx.respond(f"{ctx.author.mention}\nI have dispatched the moderation information to {channel.mention}.\n\n*Please note that if no message is sent, you may need to update my access to {channel.mention} for future moderation messages, good sir.*", ephemeral=True)
        else:
            await ctx.respond(f"{ctx.author.mention}\nI have `removed (kicked)` **{member.display_name}** from the guild for you, good sir.", ephemeral=True)
      
        await member.kick(reason=reason if reason else "Not provided.")



    #when users are kicked
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        try:
            async for entry in member.guild.audit_logs(action=discord.AuditLogAction.kick, limit=1):
                if entry.target == member:
                    reason = entry.reason
    
                    embed = discord.Embed(title="Member Status Update", description=f"Attention members of ***{member.guild.name}***,\n**{member.display_name}** has been `removed (kicked)` from this guild.", color = discord.Color.from_rgb(130, 130, 130))
            
                    embed.add_field(name="Reason", value=reason if reason else "Not provided.")
    
                    #set thumbnail to author's avatar
                    try:
                        embed.set_thumbnail(url=member.avatar.url)
                    except:
                        pass #if no avatar set, skip the thumbnail
                    
    
          
                    moderation_key = {"server_id": member.guild.id}
                    moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
                    if moderation_config:
                        channel = self.bot.get_channel(moderation_config["channel_id"])
    
                        try:
                            await channel.send(embed=embed)
                        except: #if the bot does not have access or any other errors occur
                            pass
                    else:
                        pass

        #possibly missing required permissions
        except:
            pass
            

  
################################KICK###################################



  

################################BAN###################################
    @discord.slash_command(
        name="banish",
        description="The automaton will banish (ban) a member from the guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def banish(self, ctx, member: Option(discord.Member, name="member", description="Member to banish from the guild."), *, reason: Option(str, name="reason", description="Reason for banishing member from the guild.", required=False, default=None)):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

        if member == self.bot.user:
            await ctx.respond(f"Apologies {ctx.author.mention},\nI am unable to `banish (ban)` myself from ***{ctx.guild.name}***.\n*Please try again.*", ephemeral=True)
            return

        moderation_key = {"server_id": member.guild.id}
        moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
        if moderation_config:
            channel = self.bot.get_channel(moderation_config["channel_id"])
          
            await ctx.respond(f"{ctx.author.mention}\nI have dispatched the moderation information to {channel.mention}.\n\n*Please note that if no message is sent, you may need to update my access to {channel.mention} for future moderation messages, good sir.*", ephemeral=True)
        else:
            await ctx.respond(f"{ctx.author.mention}\nI have `banished (banned)` **{member.display_name}** from the guild for you, good sir.", ephemeral=True)

      
      
        await member.ban(reason=reason if reason else "Not provided.")



    #when users are banned
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        try:
            async for entry in guild.audit_logs(action=discord.AuditLogAction.ban):
                if entry.target == user:
                    reason = entry.reason
    
                    embed = discord.Embed(title="Member Status Update", description=f"Attention members of ***{guild.name}***,\n**{user.display_name}** has been `banished (banned)` from this guild.", color = discord.Color.from_rgb(130, 130, 130))
            
                    embed.add_field(name="Reason", value=reason if reason else "Not provided.")
    
                    #set thumbnail to author's avatar
                    try:
                        embed.set_thumbnail(url=user.avatar.url)
                    except:
                        pass #if no avatar set, skip the thumbnail
                    
    
          
            moderation_key = {"server_id": guild.id}
            moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
            if moderation_config:
                channel = self.bot.get_channel(moderation_config["channel_id"])
              
                try:
                    await channel.send(embed=embed)
                except: #if the bot does not have access or any other errors occur
                    pass
            else:
                pass

        #possibly missing required permissions
        except:
            pass

  
################################BAN###################################





  

###############################UNBAN###################################
    @discord.slash_command(
        name="unbanish",
        description="The automaton will unbanish (unban) a member from the guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def unbanish(self, ctx, member_id: Option(str, name="member_id", description="ID of the member to unbanish from the guild. (Will remove all user's previous warnings)"), reason: Option(str, name="reason", description="Reason for unbanning member from the guild.", required=False, default=None)):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

      
        banned_users = await ctx.guild.bans().flatten()

        user = await self.bot.fetch_user(member_id)

        if user == self.bot.user:
            await ctx.respond(f"Apologies {ctx.author.mention},\nI am unable to `unbanish (unban)` myself from ***{ctx.guild.name}***.\n*Please try again.*", ephemeral=True)
            return

        try:
            for ban_entry in banned_users:
                if ban_entry.user.name == user.display_name:

                    moderation_key = {"server_id": ctx.guild.id}
                    moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
                    if moderation_config:
                        channel = self.bot.get_channel(moderation_config["channel_id"])
                      
                        await ctx.respond(f"{ctx.author.mention}\nI have dispatched the moderation information to {channel.mention}.\n\n*Please note that if no message is sent, you may need to update my access to {channel.mention} for future moderation messages, good sir.*", ephemeral=True)
                    else:
                        await ctx.respond(f"{ctx.author.mention}\nI have `unbanished (unbanned)` **{user.display_name}** from the guild for you, good sir.", ephemeral=True)

                  
                    await ctx.guild.unban(ban_entry.user)


                    # Find all entries in the database that match the user.id
                    warning_entries = moderation_db[f"warnings_{ctx.guild.id}"].find({"member_id": user.id})
            
                    # Delete the matching entries from the database
                    for warning in warning_entries:
                        moderation_db[f"warnings_{ctx.guild.id}"].delete_one({"_id": warning["_id"]})

        

        except:
            await ctx.respond(f"{ctx.author.mention}\nIt appears that **{user.display_name} (ID: {member_id})** is not currently banned from ***{ctx.guild.name}***, good sir.\n*Please try again.*", ephemeral=True)



    #when users are unbanned
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        try:
            async for entry in guild.audit_logs(action=discord.AuditLogAction.unban):
                if entry.target == user:
                    reason = entry.reason
    
                    embed = discord.Embed(title="Member Status Update", description=f"Attention members of ***{guild.name}***,\n**{user.display_name}** has been `unbanished (unbanned)` from this guild.", color = discord.Color.from_rgb(130, 130, 130))
            
                    embed.add_field(name="Reason", value=reason if reason else "Not provided.")
    
                    #set thumbnail to author's avatar
                    try:
                        embed.set_thumbnail(url=user.avatar.url)
                    except:
                        pass #if no avatar set, skip the thumbnail
                    
    
          
            moderation_key = {"server_id": guild.id}
            moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
            if moderation_config:
                channel = self.bot.get_channel(moderation_config["channel_id"])
              
                try:
                    await channel.send(embed=embed)
                except: #if the bot does not have access or any other errors occur
                    pass
            else:
                pass

        #possibly missing required permissions
        except:
            pass
###############################UNBAN###################################




  
###############################MUTE###################################
    @discord.slash_command(
        name="silence",
        description="The automaton will silence (mute) a member within the guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def silence(self, ctx, member: Option(discord.Member, name="member", description="Member to silence within the guild."), *, reason: Option(str, name="reason", description="Reason for silencing the member within the guild.", required=False, default=None)):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

        if member == self.bot.user:
            await ctx.respond(f"Apologies {ctx.author.mention},\nI am unable to `silence (mute)` myself in ***{ctx.guild.name}***.\n*Please try again.*", ephemeral=True)
            return

      
        muted_role = discord.utils.get(ctx.guild.roles, name="Silenced")
        if muted_role is None:
            muted_role = await ctx.guild.create_role(name="Silenced")
            bot_highest_role = ctx.guild.me.top_role  # Get the bot's highest role
            position = bot_highest_role.position - 1  # Position the role right below the bot's highest role
            permissions = discord.Permissions(send_messages=False)
            await muted_role.edit(permissions=permissions, position=position)
        await member.add_roles(muted_role)

        embed = discord.Embed(title="Member Status Update", description=f"Attention members of {ctx.guild.name},\n{member.display_name} has been `silenced (muted)` within this guild.", color = discord.Color.from_rgb(130, 130, 130))

        embed.add_field(name="Reason", value=reason if reason else "Not provided.")

        #set thumbnail to author's avatar
        try:
            embed.set_thumbnail(url=member.avatar.url)
        except:
            pass #if no avatar set, skip the thumbnail

        moderation_key = {"server_id": ctx.guild.id}
        moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
        if moderation_config:
            channel = self.bot.get_channel(moderation_config["channel_id"])
          
            await ctx.respond(f"{ctx.author.mention}\nI have dispatched the moderation information to {channel.mention}.", ephemeral=True)
          
            try:
                await channel.send(embed=embed)
            except: #if the bot does not have access or any other errors occur
                await ctx.respond(f"Apologies {ctx.author.mention},\nI was unable to send the moderation message to {channel.mention}, good sir.\n*Please update my access to this channel, if necessary, and try again.*", ephemeral=True)
        else:
            await ctx.respond(embed=embed)
  
###############################MUTE###################################




  
###############################UNMUTE###################################
    @discord.slash_command(
        name="unsilence",
        description="The automaton will unsilence (unmute) a member within the guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def unsilence(self, ctx, member: Option(discord.Member, name="member", description="Member to unsilence within the guild."), *, reason: Option(str, name="reason", description="Reason for unsilencing the member within the guild.", required=False, default=None)):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

        if member == self.bot.user:
            await ctx.respond(f"Apologies {ctx.author.mention},\nI am unable to `unsilence (unmute)` myself from ***{ctx.guild.name}***.\n*Please try again.*", ephemeral=True)
            return

      
        muted_role = discord.utils.get(ctx.guild.roles, name="Silenced")
        if muted_role is None:
            await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears there is no *Silenced* status for {ctx.guild.name}.\nPlease use my `/silence` directive to silence a user and create this status for the guild.", ephemeral=True)
            return
      
        try:
            await member.remove_roles(muted_role)
        except:
            await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that {member.display_name} has not been silenced within {ctx.guild.name}.", ephemeral=True)
            return

      
        embed = discord.Embed(title="Member Status Update", description=f"Attention members of ***{ctx.guild.name}***,\n**{member.display_name}** has been `unsilenced (unmuted)` within this guild.", color = discord.Color.from_rgb(130, 130, 130))

        embed.add_field(name="Reason", value=reason if reason else "Not provided.")

        #set thumbnail to author's avatar
        try:
            embed.set_thumbnail(url=member.avatar.url)
        except:
            pass #if no avatar set, skip the thumbnail

        moderation_key = {"server_id": ctx.guild.id}
        moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
        if moderation_config:
            channel = self.bot.get_channel(moderation_config["channel_id"])
          
            await ctx.respond(f"{ctx.author.mention}\nI have dispatched the moderation information to {channel.mention}.", ephemeral=True)
          
            try:
                await channel.send(embed=embed)
            except: #if the bot does not have access or any other errors occur
                await ctx.respond(f"Apologies {ctx.author.mention},\nI was unable to send the moderation message to {channel.mention}, good sir.\n*Please update my access to this channel, if necessary, and try again.*", ephemeral=True)
        else:
            await ctx.respond(embed=embed)
###############################UNMUTE###################################




  

###############################WARN##################################
    @discord.slash_command(
        name="warn",
        description="The automaton will warn a member within the guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def warn(self, ctx, member: Option(discord.Member, name="member", description="Member to warn within the guild."), *, reason: Option(str, name="reason", description="Reason for warning the member within the guild.", required=False, default=None)):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

        if member == self.bot.user:
            await ctx.respond(f"Apologies {ctx.author.mention},\nI am unable to `warn` myself in ***{ctx.guild.name}***.\n*Please try again.*", ephemeral=True)
            return

        warning_number = moderation_db[f"warnings_{ctx.guild.id}"].count_documents({"member_id": member.id})

        #cannot add more than 3 warnings
        if warning_number >= 3:
            await ctx.respond(f"Apologies {ctx.author.mention},\n{member.display_name} has already reached the maximum number of warnings for {ctx.guild.name} ({self.warning_threshold}).\nConsider using my `/warnremove` directive to remove a warning for this member.", ephemeral=True)
            return
      
        
        moderation_db[f"warnings_{ctx.guild.id}"].insert_one(
          {
            "warning_number": warning_number + 1,
            "server_id": ctx.guild.id,
            "server_name": ctx.guild.name,
            "member_id": member.id,
            "member_name": member.display_name,
            "reason": reason
          }
        )

        # Retrieve the warnings for the member from the database
        num_warnings = moderation_db[f"warnings_{ctx.guild.id}"].count_documents({"member_id": member.id})

        # Send a message indicating the number of warnings left before a ban
        warnings_left = self.warning_threshold - num_warnings

        if warnings_left > 0:
            threshold_reached = False
            description = f"Attention members of ***{ctx.guild.name}***,\n**{member.display_name}** has been `warned` within this guild."
        else:
            threshold_reached = True
            description = f"Attention members of {ctx.guild.name},\n{member.display_name} has been `warned` within this guild and has reached the maximum number of warnings ({self.warning_threshold}).\n\nTheir banishment shall be swift."

      
        embed = discord.Embed(title="Member Status Update", description=description, color = discord.Color.from_rgb(130, 130, 130))

        embed.add_field(name="Warnings Remaining", value = f"{warnings_left} of {self.warning_threshold}", inline=False)
      
        embed.add_field(name="Reason", value=reason if reason else "Not provided.", inline=False)

        #set thumbnail to author's avatar
        try:
            embed.set_thumbnail(url=member.avatar.url)
        except:
            pass #if no avatar set, skip the thumbnail

        moderation_key = {"server_id": ctx.guild.id}
        moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
        if moderation_config:
            channel = self.bot.get_channel(moderation_config["channel_id"])
          
            await ctx.respond(f"{ctx.author.mention}\nI have dispatched the moderation information to {channel.mention}.", ephemeral=True)
            await asyncio.sleep(1)
          
            try:
                await channel.send(embed=embed)
            except: #if the bot does not have access or any other errors occur
                banish_embed = discord.Embed(title="Banishment Error", description=f"Apologies {ctx.author.mention},\nI was unable to send the moderation message to {channel.mention}, good sir.\n*For future reference, please update my access to this channel by permitting me the `Send Messages` permission in order to view moderation notifications in this channel.*", color=discord.Color.from_rgb(130, 130, 130))

                banish_embed.set_thumbnail(url=self.bot.user.avatar.url)
                
                await ctx.respond(embed=banish_embed, ephemeral=True)

            autobanish = moderation_config["autobanish"]
            if threshold_reached is True:
                if autobanish is True:
                    
                    try:
                        await member.ban(reason=reason if reason else "Not provided.")
                    except:
                        banish_embed = discord.Embed(title="Banishment Error", description=f"Apologies {ctx.author.mention},\nI was unable to automatically banish **{member.display_name}**, good sir.\n*For future reference, please permit me the `Ban Members` permission in order to automatically ban members from this guild.*", color=discord.Color.from_rgb(130, 130, 130))
        
                        banish_embed.set_thumbnail(url=self.bot.user.avatar.url)
                        
                        await ctx.respond(embed=banish_embed, ephemeral=True)
                else:
                    banish_command = self.bot.get_application_command("banish")
                    unbanish_command = self.bot.get_application_command("unbanish")
                    warnremove_command = self.bot.get_application_command("warnremove")
                    
                    banish_embed = discord.Embed(title="Banishment Reminder", description=f"{ctx.author.mention}\n{member.display_name} has reached the maximum number of warnings for ***{ctx.guild.name}***, good sir.\n\nIt is advisable to utilize my </{banish_command.name}:{banish_command.id}> directive to permanently banish them from this guild.\n\nYou may also utilize my </{warnremove_command.name}:{warnremove_command.id}> directive to remove a warning from this user or you may utilize my </{unbanish_command.name}:{unbanish_command.id}> directive to unbanish them in the future, if you so desire.\n*Please note that using my </{unbanish_command.name}:{unbanish_command.id}> directive will remove all previous warnings from the user for your guild.", color=discord.Color.from_rgb(130, 130, 130))
    
                    banish_embed.set_thumbnail(url=self.bot.user.avatar.url)
                    
                    await channel.send(embed=banish_embed)
            else:
                pass
        
        else:
            await ctx.respond(embed=embed)

            await asyncio.sleep(1)

            if threshold_reached is True:
                banish_command = self.bot.get_application_command("banish")
                unbanish_command = self.bot.get_application_command("unbanish")
                warnremove_command = self.bot.get_application_command("warnremove")
                
                banish_embed = discord.Embed(title="Banishment Reminder", description=f"{ctx.author.mention}\n{member.display_name} has reached the maximum number of warnings for ***{ctx.guild.name}***, good sir.\n\nIt is advisable to utilize my </{banish_command.name}:{banish_command.id}> directive to permanently banish them from this guild.\n\nYou may also utilize my </{warnremove_command.name}:{warnremove_command.id}> directive to remove a warning from this user or you may utilize my </{unbanish_command.name}:{unbanish_command.id}> directive to unbanish them in the future, if you so desire.\n*Please note that using my </{unbanish_command.name}:{unbanish_command.id}> directive will remove all previous warnings from the user for your guild.", color=discord.Color.from_rgb(130, 130, 130))
        
                banish_embed.set_thumbnail(url=self.bot.user.avatar.url)
                
                await ctx.respond(embed=banish_embed)

 ################################WARN##################################

  

  

  
###############################WARNREMOVE############################
    @discord.slash_command(
        name="warnremove",
        description="The automaton will remove a warning from a member within the guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def warnremove(self, ctx, member: Option(discord.Member, name="member", description="Member to warn within the guild."), warning_index: Option(int, name="warning_index", description="Index of the warning.", min_value=1, max_value=3)):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return

        if member == self.bot.user:
            await ctx.respond(f"Apologies {ctx.author.mention},\nI am unable to `remove a warning` from myself in ***{ctx.guild.name}***.\n*Please try again.*", ephemeral=True)
            return

      
        # Retrieve the warnings for the member from the database
        warnings = moderation_db[f"warnings_{ctx.guild.id}"].find_one({"member_id": member.id})
      
        # Check if the member has any warnings
        if warnings:
            #find the total number of warnings for the user
            num_warnings = moderation_db[f"warnings_{ctx.guild.id}"].count_documents({"member_id": member.id})

  
            # Check if the warn_index is valid
            if warning_index > 0 and warning_index <= num_warnings:
                # Remove the warning from the database
                moderation_db[f"warnings_{ctx.guild.id}"].delete_one({"member_id": member.id, "warning_number": warning_index})


                # Update the remaining warnings' warning_number field
                for warning in moderation_db[f"warnings_{ctx.guild.id}"].find({"member_id": member.id, "warning_number": {"$gt": warning_index}}):
                    moderation_db[f"warnings_{ctx.guild.id}"].update_one({"_id": warning["_id"]}, {"$inc": {"warning_number": -1}})
              

                #count number of warnings after deletion
                num_warnings = moderation_db[f"warnings_{ctx.guild.id}"].count_documents({"member_id": member.id})
              
                # Send a message indicating the number of warnings left before a ban
                warnings_left = self.warning_threshold - num_warnings
              

                embed = discord.Embed(title="Member Status Update", description=f"Attention members of {ctx.guild.name},\nA warning has been *removed* from {member.display_name} for this guild.", color = discord.Color.from_rgb(130, 130, 130))
        
                embed.add_field(name="Warnings Remaining", value = f"{warnings_left} of {self.warning_threshold}", inline=False)

                #set thumbnail to author's avatar
                try:
                    embed.set_thumbnail(url=member.avatar.url)
                except:
                    pass #if no avatar set, skip the thumbnail
        
                moderation_key = {"server_id": ctx.guild.id}
                moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
                if moderation_config:
                    channel = self.bot.get_channel(moderation_config["channel_id"])
                  
                    await ctx.respond(f"{ctx.author.mention}\nI have dispatched the moderation information to {channel.mention}.", ephemeral=True)
                  
                    try:
                        await channel.send(embed=embed)
                    except: #if the bot does not have access or any other errors occur
                        await ctx.respond(f"Apologies {ctx.author.mention},\nI was unable to send the moderation message to {channel.mention}, good sir.\n*Please update my access to this channel, if necessary, and try again.*", ephemeral=True)
                else:
                    await ctx.respond(embed=embed)
          
            else:
                await ctx.respond(f"Apologies {ctx.author.mention}\n***{warning_index}*** is not a valid warning index for **{member.display_name}**. This value must be a valid integer less than or equal to {num_warnings}.\n*Please try again.*", ephemeral=True)
        else:
            await ctx.respond(f"Apologies {ctx.author.mention}\nIt appears that **{member.display_name}** has no warnings within ***{ctx.guild.name}***.", ephemeral=True)

###############################WARNREMOVE############################



  

##############################WARNINGLIST###############################
    @discord.slash_command(
        name="warninglist",
        description="The automaton will provide a list of warnings for a member within the guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    # @commands.has_permissions(administrator=True)
    async def warninglist(self, ctx, member: Option(discord.Member, name="member", description="Member to get warnings for within the guild.")):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this directive, good sir.", ephemeral=True)
            return   

        if member == self.bot.user:
            await ctx.respond(f"Apologies {ctx.author.mention},\nI am unable to retrieve a list of warnings for myself from ***{ctx.guild.name}***.\n*Please try again.*", ephemeral=True)
            return
    
        # Retrieve the warnings for the member from the database
        warnings = moderation_db[f"warnings_{ctx.guild.id}"].find_one({"member_id": member.id})

        # Check if the member has any warnings
        if warnings:
            #find the total number of warnings for the user
            num_warnings = moderation_db[f"warnings_{ctx.guild.id}"].count_documents({"member_id": member.id})

          
            # Send a message indicating the number of warnings left before a ban
            warnings_left = self.warning_threshold - num_warnings
          

            embed = discord.Embed(title=f"{ctx.guild.name}\nWarning List", description=f"The following is a list of warnings for {member.display_name} within this guild.", color = discord.Color.from_rgb(130, 130, 130))
    
            embed.add_field(name="Warnings Remaining", value = f"{warnings_left} of {self.warning_threshold}", inline=False)

            for reason in moderation_db[f"warnings_{ctx.guild.id}"].find({"member_id": member.id}):
                embed.add_field(name=f"Warning {reason['warning_number']}", value=reason['reason'], inline=False)

            #member avatar as thumbnail
            try:
                embed.set_thumbnail(url=member.avatar.url)
            except:
                pass

          
            moderation_key = {"server_id": ctx.guild.id}
            moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
            if moderation_config:
                channel = self.bot.get_channel(moderation_config["channel_id"])
              
                await ctx.respond(f"{ctx.author.mention}\nI have dispatched the moderation information to {channel.mention}.", ephemeral=True)
              
                try:
                    await channel.send(embed=embed)
                except: #if the bot does not have access or any other errors occur
                    pass
            else:
                await ctx.respond(embed=embed)
          
        else:
            await ctx.respond(f"Apologies {ctx.author.mention}\nIt appears that {member.display_name} has no warnings within {ctx.guild.name}.", ephemeral=True)

##############################WARNINGLIST###############################




def setup(bot):
    bot.add_cog(Moderation(bot))
