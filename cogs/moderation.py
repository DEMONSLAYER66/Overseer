import os
import discord
from discord.ext import commands
from discord.commands import Option  # add options to slash commands
import pymongo

token = os.environ['token']


#########################MONGODB DATABASE##################################
mongoDBpass = os.environ['mongoDBpass'] #load the mongoDB url (retreived from mongoDB upon account creation)
client = pymongo.MongoClient(mongoDBpass) # Create a new client and connect to the server
moderation_db = client.moderation_db #create the moderation_db on mongoDB
# server_id_db = client.server_id_db #create the server ID database on MongoDB (this shows a list of all of the active servers the bot is a part of)


# SERVER_ID = []
# server_ids = server_id_db.server_ids.find_one()["server_ids"]
# SERVER_ID = server_ids
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
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, member: Option(discord.Member, name="member", description="Member to remove from the guild."), *, reason: Option(str, name="reason", description="Reason for removing member from the guild.", required=False, default=None)):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this command.")
            return

        embed = discord.Embed(title="Member Status Update", description=f"Attention members of {ctx.guild.name},\n{member.display_name} has been ***removed (kicked)*** from this guild.", color = discord.Color.from_rgb(0, 0, 255))

        embed.add_field(name="Reason", value=reason if reason else "Not provided.")
      
        await member.kick(reason=reason if reason else "Not provided.")

        moderation_key = {"server_id": ctx.guild.id}
        moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
        if moderation_config:
            channel = await self.bot.fetch_channel(moderation_config["channel_id"])
          
            await ctx.respond(f"{ctx.author.mention}\nI have dispatched the moderation information to {channel.mention}.", ephemeral=True)
          
            await channel.send(embed=embed)
        else:
            await ctx.respond(embed=embed)
################################KICK###################################



################################BAN###################################
    @discord.slash_command(
        name="banish",
        description="The automaton will banish (ban) a member from the guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    @commands.has_permissions(administrator=True)
    async def banish(self, ctx, member: Option(discord.Member, name="member", description="Member to banish from the guild."), *, reason: Option(str, name="reason", description="Reason for banishing member from the guild.", required=False, default=None)):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this command.")
            return

        embed = discord.Embed(title="Member Status Update", description=f"Attention members of {ctx.guild.name},\n{member.display_name} has been ***banished (banned)*** from this guild.", color = discord.Color.from_rgb(0, 0, 255))

        embed.add_field(name="Reason", value=reason if reason else "Not provided.")
      
        await member.ban(reason=reason if reason else "Not provided.")

        moderation_key = {"server_id": ctx.guild.id}
        moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
        if moderation_config:
            channel = await self.bot.fetch_channel(moderation_config["channel_id"])
          
            await ctx.respond(f"{ctx.author.mention}\nI have dispatched the moderation information to {channel.mention}.", ephemeral=True)
          
            await channel.send(embed=embed)
        else:
            await ctx.respond(embed=embed)
################################BAN###################################





  

###############################UNBAN###################################
    @discord.slash_command(
        name="unbanish",
        description="The automaton will unbanish (unban) a member from the guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    @commands.has_permissions(administrator=True)
    async def unbanish(self, ctx, member_name: Option(str, name="member_name", description="ID of the member to unbanish from the guild."), reason: Option(str, name="reason", description="Reason for unbanning member from the guild.", required=False, default=None)):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this command.")
            return

      
        banned_users = ctx.guild.bans()

        try:
            for ban_entry in banned_users:
                if ban_entry.user.name.lower() == member_name.lower():
                    await ctx.guild.unban(ban_entry.user)

                    embed = discord.Embed(title="Member Status Update", description=f"Attention members of {ctx.guild.name},\n{ban_entry.user.name} has been ***unbanished (unbanned)*** from this guild.", color = discord.Color.from_rgb(0, 0, 255))
    
                    embed.add_field(name="Reason", value=reason if reason else "Not provided.")
          
    
            moderation_key = {"server_id": ctx.guild.id}
            moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
            if moderation_config:
                channel = await self.bot.fetch_channel(moderation_config["channel_id"])
              
                await ctx.respond(f"{ctx.author.mention}\nI have dispatched the moderation information to {channel.mention}.", ephemeral=True)
              
                await channel.send(embed=embed)
            else:
                await ctx.respond(embed=embed)

        except:
            await ctx.respond(f"{ctx.author.mention}\nIt appears that *{member_name}* is not currently banned from {ctx.guild.name}, good sir.", ephemeral=True)
###############################UNBAN###################################




  
###############################MUTE###################################
    @discord.slash_command(
        name="silence",
        description="The automaton will silence (mute) a member within the guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    @commands.has_permissions(administrator=True)
    async def silence(self, ctx, member: Option(discord.Member, name="member", description="Member to silence within the guild."), *, reason: Option(str, name="reason", description="Reason for silencing the member within the guild.", required=False, default=None)):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this command.")
            return

      
        muted_role = discord.utils.get(ctx.guild.roles, name="Silenced")
        if muted_role is None:
            muted_role = await ctx.guild.create_role(name="Silenced")
            bot_highest_role = ctx.guild.me.top_role  # Get the bot's highest role
            position = bot_highest_role.position - 1  # Position the role right below the bot's highest role
            permissions = discord.Permissions(send_messages=False)
            await muted_role.edit(permissions=permissions, position=position)
        await member.add_roles(muted_role)

        embed = discord.Embed(title="Member Status Update", description=f"Attention members of {ctx.guild.name},\n{member.display_name} has been ***silenced (muted)*** within this guild.", color = discord.Color.from_rgb(0, 0, 255))

        embed.add_field(name="Reason", value=reason if reason else "Not provided.")

        moderation_key = {"server_id": ctx.guild.id}
        moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
        if moderation_config:
            channel = await self.bot.fetch_channel(moderation_config["channel_id"])
          
            await ctx.respond(f"{ctx.author.mention}\nI have dispatched the moderation information to {channel.mention}.", ephemeral=True)
          
            await channel.send(embed=embed)
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
    @commands.has_permissions(administrator=True)
    async def unsilence(self, ctx, member: Option(discord.Member, name="member", description="Member to unsilence within the guild."), *, reason: Option(str, name="reason", description="Reason for unsilencing the member within the guild.", required=False, default=None)):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this command.")
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

      
        embed = discord.Embed(title="Member Status Update", description=f"Attention members of {ctx.guild.name},\n{member.display_name} has been ***unsilenced (unmuted)*** within this guild.", color = discord.Color.from_rgb(0, 0, 255))

        embed.add_field(name="Reason", value=reason if reason else "Not provided.")

        moderation_key = {"server_id": ctx.guild.id}
        moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
        if moderation_config:
            channel = await self.bot.fetch_channel(moderation_config["channel_id"])
          
            await ctx.respond(f"{ctx.author.mention}\nI have dispatched the moderation information to {channel.mention}.", ephemeral=True)
          
            await channel.send(embed=embed)
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
    @commands.has_permissions(administrator=True)
    async def warn(self, ctx, member: Option(discord.Member, name="member", description="Member to warn within the guild."), *, reason: Option(str, name="reason", description="Reason for warning the member within the guild.", required=False, default=None)):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this command.")
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
            description = f"Attention members of {ctx.guild.name},\n{member.display_name} has been ***warned*** within this guild."
        else:
            description = f"Attention members of {ctx.guild.name},\n{member.display_name} has been ***warned*** within this guild and has reached the maximum number of warnings ({self.warning_threshold}). They will be banished accordingly."

      
        embed = discord.Embed(title="Member Status Update", description=description, color = discord.Color.from_rgb(0, 0, 255))

        embed.add_field(name="Warnings Remaining", value = f"{warnings_left} of {self.warning_threshold}", inline=False)
      
        embed.add_field(name="Reason", value=reason if reason else "Not provided.", inline=False)

        moderation_key = {"server_id": ctx.guild.id}
        moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
        if moderation_config:
            channel = await self.bot.fetch_channel(moderation_config["channel_id"])
          
            await ctx.respond(f"{ctx.author.mention}\nI have dispatched the moderation information to {channel.mention}.", ephemeral=True)
          
            await channel.send(embed=embed)
        else:
            await ctx.respond(embed=embed)


 ################################WARN##################################

  

  

  
###############################WARNREMOVE############################
    @discord.slash_command(
        name="warnremove",
        description="The automaton will remove a warning from a member within the guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    @commands.has_permissions(administrator=True)
    async def warnremove(self, ctx, member: Option(discord.Member, name="member", description="Member to warn within the guild."), warning_index: Option(int, name="warning_index", description="Index of the warning.", min_value=1, max_value=3)):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this command.")
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
              

                embed = discord.Embed(title="Member Status Update", description=f"Attention members of {ctx.guild.name},\nA warning has been *removed* from {member.display_name} for this guild.", color = discord.Color.from_rgb(0, 0, 255))
        
                embed.add_field(name="Warnings Remaining", value = f"{warnings_left} of {self.warning_threshold}", inline=False)
        
                moderation_key = {"server_id": ctx.guild.id}
                moderation_config = moderation_db.moderation_configs.find_one(moderation_key)
                if moderation_config:
                    channel = await self.bot.fetch_channel(moderation_config["channel_id"])
                  
                    await ctx.respond(f"{ctx.author.mention}\nI have dispatched the moderation information to {channel.mention}.", ephemeral=True)
                  
                    await channel.send(embed=embed)
                else:
                    await ctx.respond(embed=embed)
          
            else:
                await ctx.respond(f"Apologies {ctx.author.mention}\n***{warning_index}*** is not a valid warning index for {member.display_name}. This value must be a valid integer less than or equal to {num_warnings}.\n*Please try again.*", ephemeral=True)
        else:
            await ctx.respond(f"Apologies {ctx.author.mention}\nIt appears that {member.display_name} has no warnings within {ctx.guild.name}.", ephemeral=True)

###############################WARNREMOVE############################



  

##############################WARNINGLIST###############################
    @discord.slash_command(
        name="warninglist",
        description="The automaton will provide a list of warnings for a member within the guild. (Admin Only)",
        # guild_ids=SERVER_ID
        global_command = True
    )
    @commands.has_permissions(administrator=True)
    async def warninglist(self, ctx, member: Option(discord.Member, name="member", description="Member to warn within the guild.")):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"{ctx.author.mention}, I must apologize for the inconvenience, but only those with administrative privileges may use this command.")
            return      
    
        # Retrieve the warnings for the member from the database
        warnings = moderation_db[f"warnings_{ctx.guild.id}"].find_one({"member_id": member.id})

        # Check if the member has any warnings
        if warnings:
            #find the total number of warnings for the user
            num_warnings = moderation_db[f"warnings_{ctx.guild.id}"].count_documents({"member_id": member.id})

          
            # Send a message indicating the number of warnings left before a ban
            warnings_left = self.warning_threshold - num_warnings
          

            embed = discord.Embed(title=f"{ctx.guild.name}\nWarning List", description=f"The following is a list of warnings for {member.display_name} within this guild.", color = discord.Color.from_rgb(0, 0, 255))
    
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
                channel = await self.bot.fetch_channel(moderation_config["channel_id"])
              
                await ctx.respond(f"{ctx.author.mention}\nI have dispatched the moderation information to {channel.mention}.", ephemeral=True)
              
                await channel.send(embed=embed)
            else:
                await ctx.respond(embed=embed)
          
        else:
            await ctx.respond(f"Apologies {ctx.author.mention}\nIt appears that {member.display_name} has no warnings within {ctx.guild.name}.", ephemeral=True)

##############################WARNINGLIST###############################




def setup(bot):
    bot.add_cog(Moderation(bot))