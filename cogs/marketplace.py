import discord #needed to interact with discord API
import random #used to select random selections from a list
import asyncio #used to wait a specified amount of time
from discord.ext import commands #used for slash commands
from discord.commands import Option #add options to slash commands

import os #used for 
import pymongo #used for mongoDB database
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


#########################MONGODB DATABASE##################################
# mongoDBpass = os.environ['mongoDBpass'] #load the mongoDB url (retreived from mongoDB upon account creation)
mongoDBpass = os.getenv('mongoDBpass')
client = pymongo.MongoClient(mongoDBpass) # Create a new client and connect to the server
games_db = client.games_db #Create the games database on mongoDB
wallets_db = client.wallets_db #Create the wallets database on mongoDB
items_db = client.items_db #Create the items database on mongoDB (to keep up with purchased items)
patrons_db = client.patrons_db #create the patrons database on mongoDB
#########################MONGODB DATABASE##################################

#this is an array of the server IDs where command testing is done
SERVER_ID = [1088118252200276071, 1117859916749742140]

class Marketplace(commands.Cog):
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
            return byname_data["byname"] #return the bot's nickname for the specified server
        else:
            return "Lord Bottington" #return Lord Bottington as the bot's nickname if none set




####################################TRADE################################  
    @discord.slash_command(
        name="exchange",
        description="Exchange collectible items with members of your guild.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def exchange(
        self,
        ctx,
        request: Option(str, name="request", description="Item to request.", choices=[
            "⬜ Pocket Square",
            "🧐 Monocle",
            "🦯 Cane",
            "🍃 Smoking Pipe",
            "🪶 Feathered Quill Pen",
            "🤵 Waistcoat",
            "🧣 Ascot Tie",
            "♟️ Chess Set",
            "🖋️ Vintage Fountain Pen",
            "🧤 Leather Gloves",
            "🧦 Striped Socks",           
            "🎭 Opera Glasses",
            "🪒 Shaving Kit",
            "💼 Leather Briefcase",
            "🥃 Silver Pocket Flask",
            "👔 Dress Shirt",
            "👖 Dress Pants",
            "👞 Wingtip Shoes",
            "🗡️ Silver Pocket Knife",
            "📓 Leather-bound Journal"
          ]
        ),
        offer: Option(str, name="offer", description="Item to offer.", choices=[
            "⬜ Pocket Square",
            "🧐 Monocle",
            "🦯 Cane",
            "🍃 Smoking Pipe",
            "🪶 Feathered Quill Pen",
            "🤵 Waistcoat",
            "🧣 Ascot Tie",
            "♟️ Chess Set",
            "🖋️ Vintage Fountain Pen",
            "🧤 Leather Gloves",
            "🧦 Striped Socks",           
            "🎭 Opera Glasses",
            "🪒 Shaving Kit",
            "💼 Leather Briefcase",
            "🥃 Silver Pocket Flask",
            "👔 Dress Shirt",
            "👖 Dress Pants",
            "👞 Wingtip Shoes",
            "🗡️ Silver Pocket Knife",
            "📓 Leather-bound Journal"
          ]
        )
    ):
        item_data = items_db[f"items_{ctx.guild.id}"]
        item_key = {"player_id": ctx.author.id}
        item_collection = item_data.find_one(item_key)

        if not item_collection:
            await ctx.respond(f"Apologies {ctx.author.mention},\n\nIt appears you do not have any items within your collection...\nConsider playing some games using my directives and gathering `🪙 Shillings`.\nYou can spend these in ***The Aristocrat's Emporium*** using `/shop` to buy items *OR* trade with others within {ctx.guild.name} to grow your collection, if you desire.\n\n*You may then display your collection for all to see!*", ephemeral=True)
            return
        else:
          
            item_descriptions = {
              "⬜ Pocket Square": "This dapper pocket square was expertly folded by Lord Reginald Sutton, a man of impeccable taste and a connoisseur of fine art.",
              "🧐 Monocle": "An elegant monocle that belonged to Sir Reginald Montgomery, a distinguished gentleman renowned for his sharp eye and impeccable taste.",
              "🦯 Cane": "This polished ebony cane, passed down through generations, once supported Sir Archibald Worthington, an esteemed nobleman and philanthropist who championed the rights of the working class.",
              "🍃 Smoking Pipe": "Crafted by the skilled hands of Master Tobacconist Giovanni Rossi, this smoking pipe bears the marks of countless contemplative evenings spent in the company of great thinkers and artists.",
              "🪶 Feathered Quill Pen": "This exquisite quill pen, adorned with vibrant peacock feathers, once belonged to Lady Victoria Sinclair, a celebrated poetess who penned verses that stirred hearts and inspired change.",
              "🤵 Waistcoat": "A finely tailored waistcoat, part of the distinguished wardrobe of Lord Archibald Kensington, an influential statesman and patron of the arts.",
              "🧣 Ascot Tie": "This luxurious silk ascot tie was worn by the dashing Duke of Wellington on the day he successfully negotiated a peace treaty between warring nations.",
              "♟️ Chess Set": "Hand-carved from fine mahogany, this exquisite chess set was a cherished possession of Professor Alfred Kingsley, a brilliant strategist and scholar of the game.",
              "🖋️ Vintage Fountain Pen": "A treasured possession of renowned author and playwright, Mr. Edward Hastings, this vintage fountain pen has inked countless pages that brought ",
              "🧤 Leather Gloves": "These supple leather gloves were worn by Captain James Hamilton, a fearless adventurer and explorer who braved treacherous terrains in search of lost civilizations.",
              "🧦 Striped Socks": "These vibrant striped socks were knitted by Miss Beatrice Pembroke, a talented seamstress, using leftover threads from her family's textile mill, bringing warmth and cheer to the feet of gentlemen while honoring her family's heritage.",
              "🎭 Opera Glasses": "These ornate opera glasses were a cherished possession of Lady Beatrice Montague, a patron of the arts who graced the grandest theaters, and witnessed the performances of legendary actors and prima ballerinas.",
              "🪒 Shaving Kit": "This meticulously crafted shaving kit belonged to Dr. Theodore Whitman, a respected physician and advocate of proper grooming habits for gentlemen.",
              "💼 Leather Briefcase": "This refined leather briefcase, entrusted to Mr. Sebastian Reynolds, a skilled lawyer and tireless advocate for justice, carries the weight of important legal documents that have shaped countless lives.",
              "🥃 Silver Pocket Flask": "Once carried by Captain William Blackwood, a fearless seafarer who sailed the seven seas, this silver pocket flask holds tales of daring escapades and exotic destinations.",
              "👔 Dress Shirt": "This fine cotton dress shirt, tailored by Madame Celeste Dupont, the most sought-after dressmaker in Paris, was worn by Monsieur Henri Beaumont, a renowned diplomat and envoy.",
              "👖 Dress Pants": "Crafted from the finest wool by Italian tailor Giovanni Russo, these dress pants epitomize elegance and were favored by Count Alessandro Conti, a charismatic aristocrat known for his impeccable style.",
              "👞 Wingtip Shoes": "These classic wingtip shoes, meticulously crafted by the legendary cobbler Antonio Ferrari, were worn by Mr. Theodore Sinclair, a charming gentleman who danced his way through grand ballrooms and won hearts with every step.",
              "🗡️ Silver Pocket Knife": "This heirloom silver pocket knife, passed down through generations, belonged to Colonel Reginald McAllister, a decorated military officer who relied on its sharp blade during his adventures in uncharted territories.",
              "📓 Leather-bound Journal": "Within the weathered pages of this leather-bound journal lie the thoughts and musings of Mr. Benjamin Hawthorne, a prolific writer and philosopher who sought to unravel the mysteries of the human mind."
            }
          
            item_values = {
                "⬜ Pocket Square": 40,
                "🧐 Monocle": 50,
                "🦯 Cane": 70,
                "🍃 Smoking Pipe": 60,
                "🪶 Feathered Quill Pen": 40,
                "🤵 Waistcoat": 100,
                "🧣 Ascot Tie": 50,
                "♟️ Chess Set": 150,
                "🖋️ Vintage Fountain Pen": 70,
                "🧤 Leather Gloves": 60,
                "🧦 Striped Socks": 60,           
                "🎭 Opera Glasses": 90,
                "🪒 Shaving Kit": 60,
                "💼 Leather Briefcase": 100,
                "🥃 Silver Pocket Flask": 70,
                "👔 Dress Shirt": 60,
                "👖 Dress Pants": 70,
                "👞 Wingtip Shoes": 90,
                "🗡️ Silver Pocket Knife": 90,
                "📓 Leather-bound Journal": 60
            }

            ### REQUEST ITEM
            # get the description of the request item
            for item_name, item_description in item_descriptions.items():
                if request == item_name:
                    request_description = item_description

          
            # get the value of the request item
            for item_name, item_value in item_values.items():
                if request == item_name:
                    request_value = item_value

          
            #### OFFER ITEM
            # get the description of the offer item
            for item_name, item_description in item_descriptions.items():
                if offer == item_name:
                    offer_description = item_description

            # get the value of the offer item
            for item_name, item_value in item_values.items():
                if offer == item_name:
                    offer_value = item_value

          
            # array of item names from mongoDB
            item_names_initiator = item_collection["items"]
            
            # user's number of collected items (on mongoDB)
            collected_items_initiator = item_collection["items_obtained"]

            # check if the initiator has the offer item
            i = 0
            for collected_item in item_names_initiator:
                if collected_item == offer:
                    offer_item_index = i
                    break
                i = i + 1

          
            # get the index for the request item
            i = 0
            for collected_item in item_names_initiator:
                if collected_item == request:
                    request_item_index = i
                    break
                i = i + 1


            #get the count of the offer item specified
            offer_count_initiator = collected_items_initiator[offer_item_index]

            #user does not have any of the specified item
            if offer_count_initiator == 0:
                await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears you do not have any `{offer}` to exchange with the members of {ctx.guild.name}.\n\nConsider buying some from **The Aristocrat's Emporium** using my `/shop` directive or try offering a different item, good sir.", ephemeral=True)
                return
            else:
                # remove 1 offer item from the item count on mongoDB (so the user cannot sell it while the offer is in progress)
                collected_items_initiator[offer_item_index] -= 1
              
                item_data.update_one(
                  item_key,
                  {"$set": {
                      "items_obtained": collected_items_initiator
                    }
                  }
                )

              
                exchange_embed = discord.Embed(title="Item Exchange", description = f"Attention members of {ctx.guild.name},\n{ctx.author.mention} has initiated an exchange for the following item.\n\nYou may utilize the buttons below to exchange items, if you desire.", color = discord.Color.from_rgb(130, 130, 130))

                exchange_embed.add_field(name="Requesting", value=f"> `{request}`\n> *{request_description}*\n> **Value:** `🪙 {request_value}`")

                exchange_embed.add_field(name="Offering", value=f"> `{offer}`\n> *{offer_description}*\n> **Value:** `🪙 {offer_value}`", inline=False)

              
                #set thumbnail to avatar url (unless they dont have one, then do not set a thumbnail)
                try:
                    exchange_embed.set_thumbnail(url=ctx.author.avatar.url)
                except:
                    pass

              
                await ctx.respond(embed = exchange_embed, view = self.ExchangeView(ctx, item_descriptions, item_values, collected_items_initiator, offer_item_index, request_item_index, request, request_description, request_value, offer, offer_description, offer_value))



    ## Select menu for help function
    class ExchangeView(discord.ui.View):
        def __init__(self, ctx, item_descriptions, item_values, collected_items_initiator, offer_item_index, request_item_index, request, request_description, request_value, offer, offer_description, offer_value):
            super().__init__(timeout=600) #set the timeout (10 minutes)
            self.ctx = ctx #intialize the context
            self.item_descriptions = item_descriptions
            self.item_values = item_values
            self.collected_items_initiator = collected_items_initiator #array of items of the initiator
            self.offer_item_index = offer_item_index #index of the offer item for the array
            self.request_item_index = request_item_index #index of the request item for the array
            self.request = request
            self.request_description = request_description
            self.request_value = request_value
            self.offer = offer
            self.offer_description = offer_description
            self.offer_value = offer_value



      
        # Handle timeout (e.g., if no trade is made within the specified timeout)
        async def on_timeout(self):
            item_data = items_db[f"items_{self.ctx.guild.id}"]
            item_key = {"player_id": self.ctx.author.id}

            # add 1 offer item back to the item count on mongoDB
            self.collected_items_initiator[self.offer_item_index] += 1
          
            item_data.update_one(
              item_key,
              {"$set": {
                  "items_obtained": self.collected_items_initiator
                }
              }
            )

          
            exchange_embed = discord.Embed(title="Item Exchange", description = f"Attention members of {self.ctx.guild.name},\nAn exchange initiated by {self.ctx.author.mention} for the following item has ended...", color = discord.Color.from_rgb(130, 130, 130))

            exchange_embed.add_field(name="Requesting", value=f"> `{self.request}`\n> *{self.request_description}*\n> **Value:** `🪙 {self.request_value}`")

            exchange_embed.add_field(name="Offering", value=f"> `{self.offer}`\n> *{self.offer_description}*\n> **Value:** `🪙 {self.offer_value}`", inline=False)

          
            #set thumbnail to avatar url (unless they dont have one, then do not set a thumbnail)
            try:
                exchange_embed.set_thumbnail(url=self.ctx.author.avatar.url)
            except:
                pass

            self.disable_all_items()
          
            try:
                await self.message.edit(embed = exchange_embed, view = None)
            except discord.errors.NotFound: #if message is deleted
                pass

            self.stop()



      

        ####### Cancel Exchange Button
        @discord.ui.button(emoji='🛑', label="Cancel Exchange", style=discord.ButtonStyle.danger)
        async def cancel_button_callback(self, button, interaction):
            await interaction.response.defer() #acknowledge the interaction
          
            #only the author can cancel the exchange
            if interaction.user.id != self.ctx.author.id:
                return

          
            item_data = items_db[f"items_{self.ctx.guild.id}"]
            item_key = {"player_id": self.ctx.author.id}

            # add 1 offer item back to the item count on mongoDB
            self.collected_items_initiator[self.offer_item_index] += 1
          
            item_data.update_one(
              item_key,
              {"$set": {
                  "items_obtained": self.collected_items_initiator
                }
              }
            )

          
            exchange_embed = discord.Embed(title="Item Exchange", description = f"Attention members of {self.ctx.guild.name},\n{self.ctx.author.mention} has cancelled an exchange for the following item...", color = discord.Color.from_rgb(130, 130, 130))

            exchange_embed.add_field(name="Requesting", value=f"> `{self.request}`\n> *{self.request_description}*\n> **Value:** `🪙 {self.request_value}`")

            exchange_embed.add_field(name="Offering", value=f"> `{self.offer}`\n> *{self.offer_description}*\n> **Value:** `🪙 {self.offer_value}`", inline=False)

          
            #set thumbnail to avatar url (unless they dont have one, then do not set a thumbnail)
            try:
                exchange_embed.set_thumbnail(url=self.ctx.author.avatar.url)
            except:
                pass

            self.disable_all_items()
          
            try:
                await self.message.edit(embed = exchange_embed, view = None)
            except discord.errors.NotFound: #if message is deleted
                pass

            self.stop()


      
        ####### Exchange Button
        @discord.ui.button(emoji='🤝', label="Exchange", style=discord.ButtonStyle.success)
        async def exchange_button_callback(self, button, interaction):
            await interaction.response.defer() #acknowledge the interaction
          
            #author cannot exchange with himself
            if interaction.user.id == self.ctx.author.id:
                return

            #get the item database of the interaction user
            giver_item_data = items_db[f"items_{self.ctx.guild.id}"]
            giver_item_key = {"player_id": interaction.user.id}
            giver_item_collection = giver_item_data.find_one(giver_item_key)

            #item data for initiator on mongoDB
            item_data = items_db[f"items_{self.ctx.guild.id}"]
            item_key = {"player_id": self.ctx.author.id}

            
            # user's number of collected items (on mongoDB)
            collected_items_giver = giver_item_collection["items_obtained"]


            #get the count of the request item specified for the giver
            request_count_giver = collected_items_giver[self.request_item_index]

            #user does not have any of the specified item
            if request_count_giver == 0:
                await interaction.followup.send(f"Apologies {interaction.user.mention},\nIt appears you do not have any `{self.request}` to exchange with **{self.ctx.author.display_name}**.\n\nConsider buying some from **The Aristocrat's Emporium** using my `/shop` directive, good sir.", ephemeral=True)
                return
            else:
  
                # add 1 offer item and remove 1 request item to the item count for the giver on mongoDB
                collected_items_giver[self.offer_item_index] += 1
                collected_items_giver[self.request_item_index] -= 1


                # remove 1 offer item and add 1 request item to the item count for the initiator on mongoDB
                self.collected_items_initiator[self.offer_item_index] -= 1
                self.collected_items_initiator[self.request_item_index] += 1

              
                #update the giver data on mongoDB
                giver_item_data.update_one(
                  giver_item_key,
                  {"$set": {
                      "items_obtained": collected_items_giver
                    }
                  }
                )

                #update the initiator's data on mongoDB
                item_data.update_one(
                  item_key,
                  {"$set": {
                      "items_obtained": self.collected_items_initiator
                    }
                  }
                )

                # update the embed (successful trade)
                exchange_embed = discord.Embed(title="Item Exchange", description = f"Attention members of {self.ctx.guild.name},\nAn exchange initiated by {self.ctx.author.mention} with {interaction.user.mention} for the following items has successfully ended...", color = discord.Color.from_rgb(130, 130, 130))
    
                exchange_embed.add_field(name="Requesting", value=f"> `{self.request}`\n> *{self.request_description}*\n> **Value:** `🪙 {self.request_value}`")
    
                exchange_embed.add_field(name="Offering", value=f"> `{self.offer}`\n> *{self.offer_description}*\n> **Value:** `🪙 {self.offer_value}`", inline=False)
    
              
                #set thumbnail to avatar url (unless they dont have one, then do not set a thumbnail)
                try:
                    exchange_embed.set_thumbnail(url=self.ctx.author.avatar.url)
                except:
                    pass
    
                self.disable_all_items()
              
                try:
                    await self.message.edit(embed = exchange_embed, view = None)
                except discord.errors.NotFound: #if message is deleted
                    pass
    
                self.stop()


####################################TRADE################################




  
#########################DISPLAYCASE##################################
    @discord.slash_command(
        name="displaycase",
        description="Display your collected items for all to view.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def displaycase(self, ctx):
        item_data = items_db[f"items_{ctx.guild.id}"]
        item_key = {"player_id": ctx.author.id}
        item_collection = item_data.find_one(item_key)

        if not item_collection:
            await ctx.respond(f"Apologies {ctx.author.mention},\n\nIt appears you do not have any items within your collection...\nConsider playing some games using my directives and gathering `🪙 Shillings`.\nYou can spend these in ***The Aristocrat's Emporium*** using `/shop` to buy items *OR* trade with others within ***{ctx.guild.name}*** to grow your collection using `/exchange`, if you desire.\n\n*You may then display your collection for all to see!*", ephemeral=True)
            return

        else:  
            # array of item names from mongoDB
            item_names = item_collection["items"]
            
            # user's number of collected items (on mongoDB)
            collected_items = item_collection["items_obtained"]

            regular_items_str = [] #regular items
            exclusive_items_str = [] #exclusive items (Exclusive Gentleman Collection)
            patron_items_str = []
            regular_items_obtained = 0
            exclusive_items_obtained = 0
            patron_items_obtained = 0
            for i, item_count in enumerate(collected_items):
                if item_count > 0:
                    item_name = item_names[i]

                    #check if the item is exclusive or not
                    if i < 20:
                        regular_items_obtained += 1 #increase the amount of regular items obtained by 1
                        
                        items_str = f"`{item_name}` - `x{item_count:,}`"
                      
                        regular_items_str.append(items_str)
                    elif i >= 20 and i < 25:
                        exclusive_items_obtained += 1 #increase the amount of exclusive items obatined by 1
                      
                        items_str = f"`{item_name}` - `x{item_count:,}`"
                      
                        exclusive_items_str.append(items_str)
                    else:
                        patron_items_obtained += 1 #increase the amount of patron items obatined by 1
                      
                        items_str = f"`{item_name}` - `x{item_count:,}`"
                      
                        patron_items_str.append(items_str)


            regular_items_collected = '\n'.join(f"> {line}" for line in regular_items_str) + '\n'

            exclusive_items_collected = '\n'.join(f"> {line}" for line in exclusive_items_str) + '\n'

            patron_items_collected = '\n'.join(f"> {line}" for line in patron_items_str) + '\n'


            ### No items collected
            if regular_items_obtained == 0 and exclusive_items_obtained == 0 and patron_items_obtained == 0:
                await ctx.respond(f"Apologies {ctx.author.mention},\n\nIt appears you do not have any items within your collection...\nConsider playing some games using my directives and gathering `🪙 Shillings`.\nYou can spend these in ***The Aristocrat's Emporium*** using `/shop` to buy items *OR* trade with others within ***{ctx.guild.name}*** to grow your collection using `/exchange`, if you desire.\n\n*You may then display your collection for all to see!*", ephemeral=True)
                return
                        

          
            ##################### BADGES/AWARDS ####################
            badges_str = []
            badges_obtained = 0
            # Get one or more items from the exclusive items
            if exclusive_items_obtained > 0:
                badges_obtained += 1
                exclusive_gentleman_badge = "`🎩 Exclusive Gentleman`"
                badges_str.append(exclusive_gentleman_badge)

            #get one or more items from the patron shop
            if patron_items_obtained > 0:
                badges_obtained += 1
                automaton_patron_badge = "`💰 Automaton Patron`"
                badges_str.append(automaton_patron_badge)

            #get all the items from the regular shop
            if regular_items_obtained == 20 and exclusive_items_obtained == 5:
                badges_obtained += 1
                collector_badge = "`💎 Collector`"
                badges_str.append(collector_badge)


            wins_key = {"player_id": ctx.author.id}
            wins_data = games_db[f"winnings_{ctx.guild.id}"]
            wins = wins_data.find_one(wins_key)

            if wins:
                player_wins = wins["wins"]
                player_earnings = wins["shillings"]

                #get 250 total wins in games
                win_add = 0
                for win in player_wins:
                    win_add += win
                  
                if win_add >= 250:
                    badges_obtained += 1
                    winner_badge = "`🎮 Win Achiever`"
                    badges_str.append(winner_badge)

                #earn 5000 shillings from games
                earnings_add = 0
                for earning in player_earnings:
                    earnings_add += earning

                if earnings_add >= 5000:
                    badges_obtained += 1
                    earnings_badge = "`🪙 Master Earner`"
                    badges_str.append(earnings_badge)
          
          

            badges_collected = '\n'.join(f"> {line}" for line in badges_str) + '\n'
          
            ##################### BADGES/AWARDS ####################

            collection_embed = discord.Embed(title=f"{ctx.author.display_name}\nDisplay Case", description = f"{ctx.author.mention}\nThe following is the collection of items and awards that you have accrued within {ctx.guild.name}.", color = discord.Color.from_rgb(130, 130, 130))

          
            #set thumbnail to avatar url (unless they dont have one, then do not set a thumbnail)
            try:
                collection_embed.set_thumbnail(url=ctx.author.avatar.url)
            except:
                pass
    
            await ctx.respond(embed=collection_embed, view=self.DisplayCaseView(ctx, regular_items_collected, exclusive_items_collected, patron_items_collected, badges_collected, regular_items_obtained, exclusive_items_obtained, patron_items_obtained, badges_obtained))


    
    # select menu for display case
    class DisplayCaseView(discord.ui.View):
        def __init__(self, ctx, regular_items_collected, exclusive_items_collected, patron_items_collected, badges_collected, regular_items_obtained, exclusive_items_obtained, patron_items_obtained, badges_obtained):
            super().__init__(timeout=120) #set the timeout
            self.ctx = ctx #intialize the context
            self.regular_items_collected = regular_items_collected
            self.exclusive_items_collected = exclusive_items_collected
            self.patron_items_collected = patron_items_collected
            self.badges_collected = badges_collected
            self.regular_items_obtained = regular_items_obtained
            self.exclusive_items_obtained = exclusive_items_obtained
            self.patron_items_obtained = patron_items_obtained
            self.badges_obtained = badges_obtained


        async def on_timeout(self):
            self.disable_all_items()
          
            try:
                await self.message.edit(view = None)
            except discord.errors.NotFound: #if message is deleted
                pass

            self.stop()
        
      
        #select menu options and callback
        @discord.ui.select(
          placeholder="Choose a collection category.", 
          min_values=1, 
          max_values=1,
          options = [
            discord.SelectOption(emoji='🎖', label="Awards", description = "Awards earned for the guild."),
            discord.SelectOption(emoji='💰', label="Automaton Patron Items", description = "Collection of items from the exclusive shop. (Patrons Only Items)"),
            discord.SelectOption(emoji='🎩', label="Exclusive Gentleman Collection Items", description = "Collection of exclusive items from the shop."),
            discord.SelectOption(emoji='💸', label="Common Items", description = "Collection of common items from the shop.")
          ]
        )
        async def select_callback(self, select, interaction):
            #only author can use the select menu
            if interaction.user.id != self.ctx.author.id:
                return

            await interaction.response.defer()
            
            # Awards
            if select.values[0] == "Awards":
                if self.badges_obtained > 0:
                    field_name = f"`🎖` __Awards__ (*{self.badges_obtained}/5*)"
                    field_value = self.badges_collected
                else:
                    field_name = f"`🎖` __Awards__ (*{self.badges_obtained}/5*)"
                    field_value = "No awards collected."

                add_footer = False

            # Patron Items
            elif select.values[0] == "Automaton Patron Items":
                if self.patron_items_obtained > 0:
                    field_name = f"`💰` __Automaton Patron Items__ (*{self.patron_items_obtained}/10*)"
                    field_value = self.patron_items_collected
                else:
                    field_name = f"`💰` __Automaton Patron Items__ (*{self.patron_items_obtained}/10*)"
                    field_value = "No automaton patron items collected."

                add_footer = True

            # Exclusive Items
            elif select.values[0] == "Exclusive Gentleman Collection Items":
                if self.exclusive_items_obtained > 0:
                    field_name = f"`🎩` __Exclusive Gentleman Collection Items__ (*{self.exclusive_items_obtained}/5*)"
                    field_value = self.exclusive_items_collected
                else:
                    field_name = f"`🎩` __Exclusive Gentleman Collection Items__ (*{self.exclusive_items_obtained}/5*)"
                    field_value = "No exclusive gentleman collection items collected."

                add_footer = False

            # Common Items
            elif select.values[0] == "Common Items":
                if self.regular_items_obtained > 0:
                    field_name = f"`💸` __Common Items__ (*{self.regular_items_obtained}/20*)"
                    field_value = self.regular_items_collected
                else:
                    field_name = f"`💸` __Common Items__ (*{self.regular_items_obtained}/20*)"
                    field_value = "No common items collected."

                add_footer = False
                

            collection_embed = discord.Embed(title=f"{self.ctx.author.display_name}\nDisplay Case", color = discord.Color.from_rgb(130, 130, 130))

            collection_embed.add_field(name=field_name, value=field_value)

            try:
                collection_embed.set_thumbnail(url=self.ctx.author.avatar.url)
            except:
                pass

            if add_footer is True:
                collection_embed.set_footer(text="These are exclusive items offered to Automaton Patrons only.")

            # Enable the full collection display button
            self.children[0].disabled = False

            await self.message.edit(embed=collection_embed, view=self)
  

        ### Display full collection button
        @discord.ui.button(emoji='🎩', label="Display Full Collection", style=discord.ButtonStyle.primary, row=0)
        async def display_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            collection_embed = discord.Embed(title=f"{self.ctx.author.display_name}\nDisplay Case", description = f"{self.ctx.author.mention}\nThe following is the collection of items and awards that you have accrued within {self.ctx.guild.name}.", color = discord.Color.from_rgb(130, 130, 130))
          

            if self.badges_obtained > 0:
                collection_embed.add_field(name=f"`🎖` __Awards__ (*{self.badges_obtained}/5*)", value=self.badges_collected, inline=False)

            #patron items
            if self.patron_items_obtained > 0:
                collection_embed.add_field(name=f"`💰` __Automaton Patron Items__ (*{self.patron_items_obtained}/10*)", value=self.patron_items_collected, inline=False)
          
          
            #exclusive items
            if self.exclusive_items_obtained > 0:
                collection_embed.add_field(name=f"`🎩` __Exclusive Gentleman Collection Items__ (*{self.exclusive_items_obtained}/5*)", value=self.exclusive_items_collected, inline=False)
              
            #regular items
            collection_embed.add_field(name=f"__Common Items__ (*{self.regular_items_obtained}/20*)", value=self.regular_items_collected, inline=False)


            try:
                collection_embed.set_thumbnail(url=self.ctx.author.avatar.url)
            except:
                pass

            #Disable the button
            button.disabled = True
          
            await self.message.edit(embed=collection_embed, view=self)
  

#########################DISPLAYCASE##################################







###############################WALLET#######################################
    @discord.slash_command(
        name="earnings",
        description="Check remaining shillings for an individual within the guild.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def earnings(self, ctx, member: Option(discord.Member, name="member", description="Member to find remaining earnings for within the guild. (Default: Self)", required=False, default=None)):

        if not member:
            member = ctx.author

        #cannot look up earnings info on other members unless admin
        if member.id != ctx.author.id and not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"Apologies {ctx.author.mention},\nOnly those with administrative privileges within {ctx.guild.name} may view earnings information for other members of the guild.\n*Please try again.*", ephemeral=True)
            return

        earnings = wallets_db[f"wallets_{ctx.guild.id}"]
        earnings_key = {"player_id": member.id}
      

        guild_member = earnings.find_one(earnings_key) #find the guild member (for remaining shillings)

        if guild_member:
            wallet = guild_member["wallet"]
        else:
            wallet = 0 #no money in wallet

        #change description for embed based on who the searched member is
        if member.id == ctx.author.id:
            description = f"{ctx.author.mention}\nThe following is how many shillings you have remaining in the guild.\n*Spend them wisely, good sir.*"
        else:
            description = f"{ctx.author.mention}\nThe following is how many shillings ***{member.display_name}*** has remaining within the guild."

        #create the embed
        earnings_embed = discord.Embed(title=f"{ctx.guild.name}\nEarnings Information", description=description, color=discord.Color.from_rgb(130, 130, 130))

        earnings_embed.add_field(name="", value=f"`🪙 {wallet:,}`")

        #set thumbnail to avatar url (unless they dont have one, then do not set a thumbnail)
        try:
            earnings_embed.set_thumbnail(url=member.avatar.url)
        except:
            pass

        await ctx.respond(embed=earnings_embed)


###############################WALLET#######################################






##############################MARKET###############################
    @discord.slash_command(
        name="shop",
        description="Purchase and sell items at the marketplace.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def shop(self, ctx):
        items = {
          "⬜ Pocket Square": "This dapper pocket square was expertly folded by Lord Reginald Sutton, a man of impeccable taste and a connoisseur of fine art.",
          "🧐 Monocle": "An elegant monocle that belonged to Sir Reginald Montgomery, a distinguished gentleman renowned for his sharp eye and impeccable taste.",
          "🦯 Cane": "This polished ebony cane, passed down through generations, once supported Sir Archibald Worthington, an esteemed nobleman and philanthropist who championed the rights of the working class.",
          "🍃 Smoking Pipe": "Crafted by the skilled hands of Master Tobacconist Giovanni Rossi, this smoking pipe bears the marks of countless contemplative evenings spent in the company of great thinkers and artists.",
          "🪶 Feathered Quill Pen": "This exquisite quill pen, adorned with vibrant peacock feathers, once belonged to Lady Victoria Sinclair, a celebrated poetess who penned verses that stirred hearts and inspired change.",
          "🤵 Waistcoat": "A finely tailored waistcoat, part of the distinguished wardrobe of Lord Archibald Kensington, an influential statesman and patron of the arts.",
          "🧣 Ascot Tie": "This luxurious silk ascot tie was worn by the dashing Duke of Wellington on the day he successfully negotiated a peace treaty between warring nations.",
          "♟️ Chess Set": "Hand-carved from fine mahogany, this exquisite chess set was a cherished possession of Professor Alfred Kingsley, a brilliant strategist and scholar of the game.",
          "🖋️ Vintage Fountain Pen": "A treasured possession of renowned author and playwright, Mr. Edward Hastings, this vintage fountain pen has inked countless pages that brought ",
          "🧤 Leather Gloves": "These supple leather gloves were worn by Captain James Hamilton, a fearless adventurer and explorer who braved treacherous terrains in search of lost civilizations.",
          "🧦 Striped Socks": "These vibrant striped socks were knitted by Miss Beatrice Pembroke, a talented seamstress, using leftover threads from her family's textile mill, bringing warmth and cheer to the feet of gentlemen while honoring her family's heritage.",
          "🎭 Opera Glasses": "These ornate opera glasses were a cherished possession of Lady Beatrice Montague, a patron of the arts who graced the grandest theaters, and witnessed the performances of legendary actors and prima ballerinas.",
          "🪒 Shaving Kit": "This meticulously crafted shaving kit belonged to Dr. Theodore Whitman, a respected physician and advocate of proper grooming habits for gentlemen.",
          "💼 Leather Briefcase": "This refined leather briefcase, entrusted to Mr. Sebastian Reynolds, a skilled lawyer and tireless advocate for justice, carries the weight of important legal documents that have shaped countless lives.",
          "🥃 Silver Pocket Flask": "Once carried by Captain William Blackwood, a fearless seafarer who sailed the seven seas, this silver pocket flask holds tales of daring escapades and exotic destinations.",
          "👔 Dress Shirt": "This fine cotton dress shirt, tailored by Madame Celeste Dupont, the most sought-after dressmaker in Paris, was worn by Monsieur Henri Beaumont, a renowned diplomat and envoy.",
          "👖 Dress Pants": "Crafted from the finest wool by Italian tailor Giovanni Russo, these dress pants epitomize elegance and were favored by Count Alessandro Conti, a charismatic aristocrat known for his impeccable style.",
          "👞 Wingtip Shoes": "These classic wingtip shoes, meticulously crafted by the legendary cobbler Antonio Ferrari, were worn by Mr. Theodore Sinclair, a charming gentleman who danced his way through grand ballrooms and won hearts with every step.",
          "🗡️ Silver Pocket Knife": "This heirloom silver pocket knife, passed down through generations, belonged to Colonel Reginald McAllister, a decorated military officer who relied on its sharp blade during his adventures in uncharted territories.",
          "📓 Leather-bound Journal": "Within the weathered pages of this leather-bound journal lie the thoughts and musings of Mr. Benjamin Hawthorne, a prolific writer and philosopher who sought to unravel the mysteries of the human mind.",
          "☂️ Gentleman's Umbrella": "This sturdy and distinguished umbrella, carried by Sir Percival Worthington, offers protection from both rain and the prying eyes of society as gentlemen engage in discreet conversations.\n\nThis is part of the `🎩 Exclusive Gentleman Collection`.",
          "⌚ Pocket Watch": "A carefully constructed and well-maintained timepiece hand-crafted by skilled watchmaker Alexandre Dubois, known for his intricate engravings and precise movements.️\n\nThis is part of the `🎩 Exclusive Gentleman Collection`.",
          "🗡️ Antique Walking Stick with Hidden Sword": "Concealed within this intricately crafted antique walking stick lies a slender and deadly blade, a favored accessory of Lord Edmund Blackwood, a man of mystery who navigated the shadows of society with grace and poise.\n\nThis is part of the `🎩 Exclusive Gentleman Collection`.",
          "🧥 Smoking Jacket": "Once worn by the esteemed Sir Winston Harrington, this smoking jacket exudes an air of sophistication and serves as a reminder of evenings spent engaged in lively debates and philosophical discussions.\n\nThis is part of the `🎩 Exclusive Gentleman Collection`.",
          "🎩 Top Hat": "This top hat once graced the head of Lord Percival Harrington, a prominent figure in high society who was known for his impeccable manners and impeccable style.\n\nThis is part of the `🎩 Exclusive Gentleman Collection`.",
          "🗡️ Intricately Carved Dagger": "This exquisite dagger, adorned with intricate engravings and believed to possess mystical powers, was wielded by the legendary warrior Sir Gideon Aldrich during his heroic battles against dark forces.", ### START OF EXCLUSIVE SHOP ITEMS
          "📜 Ancient Scroll of Wisdom": "Passed down through generations, this ancient scroll contains the profound wisdom and arcane knowledge of the long-lost Order of Illumination, offering glimpses into forgotten realms of enlightenment.",
          "🖼 Masterpiece Painting": "Painted by the enigmatic artist known only as The Maestro, this masterpiece captures the essence of the human spirit, evoking a range of emotions and inspiring contemplation in all who behold it.",
          "🎻 Enchanted Violin": "Crafted by the legendary luthier, Elara Amadeus, this enchanting violin resonates with ethereal melodies and possesses the power to stir the deepest emotions within the hearts of those who play or listen.",
          "💎 Radiant Gemstone Necklace": "This dazzling necklace features a rare and radiant gemstone, known as the Starfire Diamond, said to hold within it the power to bring good fortune and illuminate even the darkest paths.",
          "⌛ Time-Worn Hourglass": "This ancient hourglass, said to be a relic from the lost city of Atlantis, holds the sands of time within its delicate frame, offering glimpses into the past and future to those who possess the wisdom to seek its secrets.",
          "📙 Spellbound Grimoire": "Bound in the tanned hide of a mythical beast, this spellbound grimoire contains ancient incantations and forbidden knowledge that can shape reality itself in the hands of a skilled magician.",
          "🧪 Elixir of Eternal Youth": "Crafted by the alchemist known as The Alabaster Rose, this elixir promises everlasting youth and vitality, but at a price that only the bravest souls are willing to pay.",
          "🔭 Celestial Telescope": "With its polished brass frame and precision lenses, this celestial telescope unlocks the secrets of the cosmos, revealing distant galaxies, majestic constellations, and the wonders of the universe.",
          "🗝 Enchanted Key to Forgotten Realms": "Forged in the heart of an ancient star, this enchanted key has the power to unlock hidden gateways to long-lost realms filled with mythical creatures, untold treasures, and unimaginable adventures."
        }

        item_values = {
            "⬜ Pocket Square": 40,
            "🧐 Monocle": 50,
            "🦯 Cane": 70,
            "🍃 Smoking Pipe": 60,
            "🪶 Feathered Quill Pen": 40,
            "🤵 Waistcoat": 100,
            "🧣 Ascot Tie": 50,
            "♟️ Chess Set": 150,
            "🖋️ Vintage Fountain Pen": 70,
            "🧤 Leather Gloves": 60,
            "🧦 Striped Socks": 60,           
            "🎭 Opera Glasses": 90,
            "🪒 Shaving Kit": 60,
            "💼 Leather Briefcase": 100,
            "🥃 Silver Pocket Flask": 70,
            "👔 Dress Shirt": 60,
            "👖 Dress Pants": 70,
            "👞 Wingtip Shoes": 90,
            "🗡️ Silver Pocket Knife": 90,
            "📓 Leather-bound Journal": 60,
            "☂️ Gentleman's Umbrella": 1000,
            "⌚ Pocket Watch": 2000,
            "🗡️ Antique Walking Stick with Hidden Sword": 2500,
            "🧥 Smoking Jacket": 3000,
            "🎩 Top Hat": 5000,
            "🗡️ Intricately Carved Dagger": 500,
            "📜 Ancient Scroll of Wisdom": 750,
            "🖼 Masterpiece Painting": 2000,
            "🎻 Enchanted Violin": 1500,
            "💎 Radiant Gemstone Necklace": 5000,
            "⌛ Time-Worn Hourglass": 1000,
            "📙 Spellbound Grimoire": 1500,
            "🧪 Elixir of Eternal Youth": 4000,
            "🔭 Celestial Telescope": 3000,
            "🗝 Enchanted Key to Forgotten Realms": 2500
        }
      

        shop_embed = discord.Embed(title="Welcome to The Aristocrat's Emporium", description=f"{ctx.author.mention}\nThis storefront sells exclusive, hand-crafted items not found anywhere else in the world.\n\n *Feel free to pefruse at your leisure and find an item worth your liking, good sir.*", color=discord.Color.from_rgb(20, 53, 219))

      
        shop_embed.set_thumbnail(url=self.bot.user.avatar.url)

        await ctx.respond(embed=shop_embed, view=self.ShopView(ctx, items, item_values))


  
    ## Select menu for help function
    class ShopView(discord.ui.View):
        def __init__(self, ctx, items, item_values):
            super().__init__(timeout=120) #set the timeout
            self.ctx = ctx #intialize the context
            self.items = items
            self.item_values = item_values
            self.current_item = None #current item selected by user
            self.current_item_description = None #current item description selected by user



        # Handle timeout (e.g., if no selections are made within the specified timeout)
        async def on_timeout(self):
            self.disable_all_items()


            shop_embed = discord.Embed(title="Welcome to The Aristocrat's Emporium", description=f"It appears that {self.ctx.author.mention} has left the storefront...\n\n*Have a wonderful day, good sir.*", color=discord.Color.from_rgb(20, 53, 219))

      
            shop_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)
          

            try:
                await self.message.edit(embed=shop_embed, view=None)
            except discord.errors.NotFound: #if message is deleted before the timeout
                pass

            self.stop()

      

        #select menu options and callback
        @discord.ui.select(
          placeholder="🪙Choose an item to purchase or sell.", 
          min_values=1, 
          max_values=1,
          options = [
            discord.SelectOption(emoji='⬜', label="Pocket Square", description = "Value: 🪙 40"),
            discord.SelectOption(emoji='🧐', label="Monocle", description = "Value: 🪙 50"),
            discord.SelectOption(emoji='🦯', label="Cane", description = "Value: 🪙 70"),
            discord.SelectOption(emoji='🍃', label="Smoking Pipe", description = "Value: 🪙 60"),
            discord.SelectOption(emoji='🪶', label="Feathered Quill Pen", description = "Value: 🪙 40"),
            discord.SelectOption(emoji='🤵', label="Waistcoat", description = "Value: 🪙 100"),
            discord.SelectOption(emoji='🧣', label="Ascot Tie", description = "Value: 🪙 50"),
            discord.SelectOption(emoji='♟️', label="Chess Set", description = "Value: 🪙 150"),
            discord.SelectOption(emoji='🖋️', label="Vintage Fountain Pen", description = "Value: 🪙 70"),
            discord.SelectOption(emoji='🧤', label="Leather Gloves", description = "Value: 🪙 60"),
            discord.SelectOption(emoji='🧦', label="Striped Socks", description = "Value: 🪙 60"),
            discord.SelectOption(emoji='🎭', label="Opera Glasses", description = "Value: 🪙 90"),
            discord.SelectOption(emoji='🪒', label="Shaving Kit", description = "Value: 🪙 60"),
            discord.SelectOption(emoji='💼', label="Leather Briefcase", description = "Value: 🪙 100"),
            discord.SelectOption(emoji='🥃', label="Silver Pocket Flask", description = "Value: 🪙 70"),
            discord.SelectOption(emoji='👔', label="Dress Shirt", description = "Value: 🪙 60"),
            discord.SelectOption(emoji='👖', label="Dress Pants", description = "Value: 🪙 70"),
            discord.SelectOption(emoji='👞', label="Wingtip Shoes", description = "Value: 🪙 90"),
            discord.SelectOption(emoji='🗡️', label="Silver Pocket Knife", description = "Value: 🪙 90"),
            discord.SelectOption(emoji='📓', label="Leather-bound Journal", description = "Value: 🪙 60"),
            discord.SelectOption(emoji='☂️', label="Gentleman's Umbrella", description = "Value: 🪙 1,000"),
            discord.SelectOption(emoji='⌚', label="Pocket Watch", description = "Value: 🪙 2,000"),
            discord.SelectOption(emoji='🗡️', label="Antique Walking Stick with Hidden Sword", description = "Value: 🪙 2,500"),
            discord.SelectOption(emoji='🧥', label="Smoking Jacket", description = "Value: 🪙 3,000"),
            discord.SelectOption(emoji='🎩', label="Top Hat", description = "Value: 🪙 5,000")
          ]
        )
        async def select_callback(self, select, interaction):
            #only author can use the select menu
            if interaction.user.id != self.ctx.author.id:
                return

            await interaction.response.defer() #acknowledge the interaction
          

            selected_option = next(option for option in select.options if option.value == select.values[0])
            emoji = selected_option.emoji #get the emoji
            item = f"{emoji} {select.values[0]}" #create the category for the commands

            #item description
            for item_name, item_description in self.items.items():
                if item_name == item:
                    item_description = item_description
                    break

            #item value
            for item_name, item_value in self.item_values.items():
                if item_name == item:
                    item_value = item_value
                    break

            shop_embed = discord.Embed(title="Welcome to The Aristocrat's Emporium", color=discord.Color.from_rgb(20, 53, 219))

            shop_embed.add_field(name=f"`{item}`", value=f"*{item_description}*")
            shop_embed.add_field(name="Value", value=f"`🪙 {item_value:,}`", inline=False)

            shop_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)

            buttons = []
            select_menus = []
            for child in self.children:
                if isinstance(child, discord.ui.Select):
                    select_menus.append(child)
                elif isinstance(child, discord.ui.Button):
                    buttons.append(child)

            select_menus[0].disabled = False
            select_menus[1].disabled = True

            #Enable the purchase and sell buttons
            buttons[1].disabled = False
            buttons[2].disabled = False

            self.current_item = item #current item selected by user
            self.current_item_description = item_description #current item description selected by user
            
            await self.message.edit(embed=shop_embed, view=self)


        #exclusive select menu options and callback
        @discord.ui.select(
          placeholder="🪙Choose an exclusive item to purchase or sell.",
          disabled=True,
          min_values=1, 
          max_values=1,
          options = [
            discord.SelectOption(emoji='🗡️', label="Intricately Carved Dagger", description = "Value: 🪙 500"),
            discord.SelectOption(emoji='📜', label="Ancient Scroll of Wisdom", description = "Value: 🪙 750"),
            discord.SelectOption(emoji='🖼', label="Masterpiece Painting", description = "Value: 🪙 2,000"),
            discord.SelectOption(emoji='🎻', label="Enchanted Violin", description = "Value: 🪙 1,500"),
            discord.SelectOption(emoji='💎', label="Radiant Gemstone Necklace", description = "Value: 🪙 5,000"),
            discord.SelectOption(emoji='⌛', label="Time-Worn Hourglass", description = "Value: 🪙 1,000"),
            discord.SelectOption(emoji='📙', label="Spellbound Grimoire", description = "Value: 🪙 1,500"),
            discord.SelectOption(emoji='🧪', label="Elixir of Eternal Youth", description = "Value: 🪙 4,000"),
            discord.SelectOption(emoji='🔭', label="Celestial Telescope", description = "Value: 🪙 3,000"),
            discord.SelectOption(emoji='🗝', label="Enchanted Key to Forgotten Realms", description = "Value: 🪙 2,500")

          ]
        )
        async def exclusive_select_callback(self, select, interaction):
            #only author can use the select menu
            if interaction.user.id != self.ctx.author.id:
                return

            await interaction.response.defer() #acknowledge the interaction
          

            selected_option = next(option for option in select.options if option.value == select.values[0])
            emoji = selected_option.emoji #get the emoji
            item = f"{emoji} {select.values[0]}" #create the category for the commands

            #item description
            for item_name, item_description in self.items.items():
                if item_name == item:
                    item_description = item_description
                    break

            #item value
            for item_name, item_value in self.item_values.items():
                if item_name == item:
                    item_value = item_value
                    break

            shop_embed = discord.Embed(title="Welcome to The Aristocrat's Emporium\n🎩 Exclusive Item Shop 🎩", color=discord.Color.from_rgb(20, 53, 219))

            shop_embed.add_field(name=f"`{item}`", value=f"*{item_description}*")
            shop_embed.add_field(name="Value", value=f"`🪙 {item_value:,}`", inline=False)

            shop_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)

            buttons = []
            select_menus = []
            for child in self.children:
                if isinstance(child, discord.ui.Select):
                    select_menus.append(child)
                elif isinstance(child, discord.ui.Button):
                    buttons.append(child)

            select_menus[0].disabled = True
            select_menus[1].disabled = False

            #Enable the purchase and sell buttons
            buttons[1].disabled = False
            buttons[2].disabled = False

            self.current_item = item #current item selected by user
            self.current_item_description = item_description #current item description selected by user
            
            await self.message.edit(embed=shop_embed, view=self)



      

        ####### Leave Button
        @discord.ui.button(emoji='🚶‍♂️', label="Leave Store", style=discord.ButtonStyle.secondary, row=0)
        async def leave_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            self.disable_all_items()

            shop_embed = discord.Embed(title="Welcome to The Aristocrat's Emporium", description=f"It appears that {self.ctx.author.mention} has left the storefront...\n\n*Have a wonderful day, good sir.*", color=discord.Color.from_rgb(20, 53, 219))

      
            shop_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)
          

            try:
                await self.message.edit(embed=shop_embed, view=None)
            except discord.errors.NotFound: #if message is deleted
                pass

            self.stop()
            
      

        
        ####### Sell Button (start with button disabled until the user selects the item to buy or sell)
        @discord.ui.button(emoji='🧾', label="Sell", style=discord.ButtonStyle.danger, disabled=True, row=0)
        async def sell_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            earnings = wallets_db[f"wallets_{self.ctx.guild.id}"]
            earnings_key = {"player_id": self.ctx.author.id}
          
    
            guild_member = earnings.find_one(earnings_key) #find the guild member (for remaining shillings)

            if guild_member:
                wallet = guild_member["wallet"]
            else:
                wallet = 0 #no money in wallet


            #item value
            for item_name, item_value in self.item_values.items():
                if item_name == self.current_item:
                    item_value = item_value
                    break


          
            #get list of item names
            items = []
            for item_name, item_cost in self.item_values.items():
                items.append(item_name)
          
            i = 0
            for item in items:
                if self.current_item == item:
                    item_obtained = i
                    break
  
                i = i + 1
  
          
  
            item_key = {"player_id": self.ctx.author.id}
            items_entry = items_db[f"items_{self.ctx.guild.id}"]
            items_data = items_entry.find_one(item_key)
  
  
            if not items_data:
                sell_message = f"Apologies {self.ctx.author.mention}\nIt appears you do not have any of the specified item to sell..."
            elif items_data["items_obtained"][item_obtained] == 0:
                sell_message = f"Apologies {self.ctx.author.mention}\nIt appears you do not have any of the specified item to sell..."
            else:
                #reduce the amount of shillings remaining in the user's wallet on MongoDB
                wallets = wallets_db[f"wallets_{self.ctx.guild.id}"]
                wallets.update_one(
                  {"player_id": self.ctx.author.id},
                  {"$inc": {"wallet": item_value}}
                )


              
                items_obtained = items_data["items_obtained"]
  
                items_obtained[item_obtained] -= 1 #decrease the item by 1
  
                items_entry.update_one(
                  item_key,
                  {"$set": {"items_obtained": items_obtained}}
                )

                sell_message = f"{self.ctx.author.mention}\nYou have successfully sold this item and have been refunded accordingly, good sir."
              

            #Disable the sell and purchase buttons and the select menu
            self.disable_all_items()

            buttons = []
            select_menus = []
            for child in self.children:
                if isinstance(child, discord.ui.Select):
                    select_menus.append(child)
                elif isinstance(child, discord.ui.Button):
                    buttons.append(child)

            if buttons[3].label == "Enter Exclusive Shop":
                title = "Welcome to The Aristocrat's Emporium"
            elif buttons[3].label == "Return to Storefront":
                title = "Welcome to The Aristocrat's Emporium\n🎩 Exclusive Item Shop 🎩"

          
            #update embed accordingly
            sell_embed = discord.Embed(title=title, color=discord.Color.from_rgb(20, 53, 219))
            sell_embed.add_field(name=f"`{self.current_item}`", value=f"*{self.current_item_description}*")
            sell_embed.add_field(name="Value", value=f"`🪙 {item_value:,}`", inline=False)
            sell_embed.add_field(name="Shop Message", value=sell_message, inline=False)
            sell_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)

            try:
                await self.message.edit(embed=sell_embed, view=self)
            except discord.errors.NotFound: #if message is deleted
                pass

            await asyncio.sleep(3) #wait for 3 seconds

            #Update the embed again without the purchase message
            self.enable_all_items()

            if buttons[3].label == "Enter Exclusive Shop":
                select_menus[0].disabled = False
                select_menus[1].disabled = True
            elif buttons[3].label == "Return to Storefront":
                select_menus[0].disabled = True
                select_menus[1].disabled = False


            #Enable the purchase and sell buttons
            buttons[1].disabled = False
            buttons[2].disabled = False

            #update embed accordingly
            shop_embed = discord.Embed(title=title, color=discord.Color.from_rgb(20, 53, 219))
            shop_embed.add_field(name=f"`{self.current_item}`", value=f"*{self.current_item_description}*")
            shop_embed.add_field(name="Value", value=f"`🪙 {item_value:,}`", inline=False)
            shop_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)

            try:
                await self.message.edit(embed=shop_embed, view=self)
            except discord.errors.NotFound: #if message is deleted
                pass
      

      

        ####### Buy Button (start with button disabled until the user selects the item to buy or sell)
        @discord.ui.button(emoji='🪙', label="Purchase", style=discord.ButtonStyle.success, disabled=True, row=0)
        async def purchase_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return


            earnings = wallets_db[f"wallets_{self.ctx.guild.id}"]
            earnings_key = {"player_id": self.ctx.author.id}
          
    
            guild_member = earnings.find_one(earnings_key) #find the guild member (for remaining shillings)

            if guild_member:
                wallet = guild_member["wallet"]
            else:
                wallet = 0 #no money in wallet


            #item value
            for item_name, item_value in self.item_values.items():
                if item_name == self.current_item:
                    item_value = item_value
                    break



            #check wallet and price of item
            if item_value > wallet: #cannot buy item
                purchase_message = f"Apologies {self.ctx.author.mention}\nIt appears you do not have enough `🪙 Shillings` to purchase this item..."

            else: #bought item
                #reduce the amount of shillings remaining in the user's wallet on MongoDB
                wallets = wallets_db[f"wallets_{self.ctx.guild.id}"]
                wallets.update_one(
                  {"player_id": self.ctx.author.id},
                  {"$inc": {"wallet": -item_value}}
                )

                #get list of item names
                items = []
                for item_name, item_cost in self.item_values.items():
                    items.append(item_name)

                i = 0
                for item in items:
                    if self.current_item == item:
                        item_obtained = i
                        break

                    i = i + 1

              

                item_key = {"player_id": self.ctx.author.id}
                items_entry = items_db[f"items_{self.ctx.guild.id}"]
                items_data = items_entry.find_one(item_key)

                no_items = [0 for _ in range(35)]

                if items_data:
                    items_obtained = items_data["items_obtained"]

                    items_obtained[item_obtained] += 1 #increase the item by 1

                    items_entry.update_one(
                      item_key,
                      {"$set": {"items_obtained": items_obtained}}
                    )

                else:
                    no_items[item_obtained] = 1
                  
                    items_entry.insert_one(
                      {
                        "server_id": self.ctx.guild.id,
                        "server_name": self.ctx.guild.name,
                        "player_id": self.ctx.author.id,
                        "player_name": self.ctx.author.display_name,
                        "items": items, #array of the names of the items
                        "items_obtained": no_items #array of the number of items the user has
                      }
                    )
              
                purchase_message = f"{self.ctx.author.mention}\nYou have successfully purchased this item, good sir."

            #Disable the sell and purchase buttons and the select menu
            self.disable_all_items()


            buttons = []
            select_menus = []
            for child in self.children:
                if isinstance(child, discord.ui.Select):
                    select_menus.append(child)
                elif isinstance(child, discord.ui.Button):
                    buttons.append(child)

            if buttons[3].label == "Enter Exclusive Shop":
                title = "Welcome to The Aristocrat's Emporium"
            elif buttons[3].label == "Return to Storefront":
                title = "Welcome to The Aristocrat's Emporium\n🎩 Exclusive Item Shop 🎩"

          
            #update embed accordingly
            purchase_embed = discord.Embed(title=title, color=discord.Color.from_rgb(20, 53, 219))
            purchase_embed.add_field(name=f"`{self.current_item}`", value=f"*{self.current_item_description}*")
            purchase_embed.add_field(name="Value", value=f"`🪙 {item_value:,}`", inline=False)
            purchase_embed.add_field(name="Shop Message", value=purchase_message, inline=False)
            purchase_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)

            try:
                await self.message.edit(embed=purchase_embed, view=self)
            except discord.errors.NotFound: #if message is deleted
                pass

            await asyncio.sleep(3) #wait for 3 seconds

            #Update the embed again without the purchase message
            self.enable_all_items()

            if buttons[3].label == "Enter Exclusive Shop":
                select_menus[0].disabled = False
                select_menus[1].disabled = True
            elif buttons[3].label == "Return to Storefront":
                select_menus[0].disabled = True
                select_menus[1].disabled = False

            #Enable the purchase and sell buttons
            buttons[1].disabled = False
            buttons[2].disabled = False
          

            #update embed accordingly
            shop_embed = discord.Embed(title=title, color=discord.Color.from_rgb(20, 53, 219))
            shop_embed.add_field(name=f"`{self.current_item}`", value=f"*{self.current_item_description}*")
            shop_embed.add_field(name="Value", value=f"`🪙 {item_value:,}`", inline=False)
            shop_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)

            try:
                await self.message.edit(embed=shop_embed, view=self)
            except discord.errors.NotFound: #if message is deleted
                pass


        ####### Exclusive Store Button
        @discord.ui.button(emoji='🎩', label="Enter Exclusive Shop", style=discord.ButtonStyle.primary, row=1)
        async def exclusive_store_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            if button.label == "Return to Storefront":
                button.emoji = '🎩'
                button.label = "Enter Exclusive Shop"

                buttons = []
                select_menus = []
                for child in self.children:
                    if isinstance(child, discord.ui.Select):
                        select_menus.append(child)
                    elif isinstance(child, discord.ui.Button):
                        buttons.append(child)

                select_menus[0].disabled = False
                select_menus[1].disabled = True

                #Disable the purchase and sell buttons
                buttons[1].disabled = True
                buttons[2].disabled = True

                shop_embed = discord.Embed(title="Welcome to The Aristocrat's Emporium", description=f"{self.ctx.author.mention}\nThis storefront sells exclusive, hand-crafted items not found anywhere else in the world.\n\n *Feel free to peruse at your leisure and find an item worth your liking, good sir.*", color=discord.Color.from_rgb(20, 53, 219))
        
              
                shop_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)

                await self.message.edit(embed=shop_embed, view=self)

          
            elif button.label == "Enter Exclusive Shop":
                ##### PATRON FEATURE (always available in support guild)
                # server ID for The Sweez Gang
                support_guild_id = 1088118252200276071
    
              
                refined_automaton_patron_key = {
                  "server_id": self.ctx.guild.id,
                  "patron_tier": "Refined Automaton Patron"
                }
    
                distinguished_automaton_patron_key = {
                  "server_id": self.ctx.guild.id,
                  "patron_tier": "Distinguished Automaton Patron"
                }
                patron_data = patrons_db.patrons
    
                refined_patron = patron_data.find_one(refined_automaton_patron_key)
                distinguished_patron = patron_data.find_one(distinguished_automaton_patron_key)
    
                if self.ctx.guild.id != support_guild_id:
                    if not refined_patron and not distinguished_patron:
                        #change button to give users a choice to return to the storefront
                        button.emoji = '🏪'
                        button.label = "Return to Storefront"
    
                        buttons = []
                        select_menus = []
                        for child in self.children:
                            if isinstance(child, discord.ui.Select):
                                select_menus.append(child)
                            elif isinstance(child, discord.ui.Button):
                                buttons.append(child)
    
                        select_menus[0].disabled = True
    
                        buttons[1].disabled = True
                        buttons[2].disabled = True
           
                      
                        patron_embed = discord.Embed(title="Patron Feature", description=f"Apologies {self.ctx.author.mention},\nThe exclusive item shop for *The Aristocrat's Emporium* is an exclusive feature available only to `Refined Automaton Patrons` and `Distinguished Automaton Patrons` and is not currently in use for ***{self.ctx.guild.name}***, good sir.\n\nPlease use my `/patron` directive to learn more information on enabling or upgrading patron (premium) features for ***{self.ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(130, 130, 130))
            
                        patron_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)
        
                        try:
                            await self.message.edit(embed=patron_embed, view=self)
                            return
                        except discord.errors.NotFound: #if message is deleted
                            return
    

                  
                buttons = []
                select_menus = []
                for child in self.children:
                    if isinstance(child, discord.ui.Select):
                        select_menus.append(child)
                    elif isinstance(child, discord.ui.Button):
                        buttons.append(child)

                select_menus[0].disabled = True
                select_menus[1].disabled = False

                #Disable the purchase and sell buttons
                buttons[1].disabled = True
                buttons[2].disabled = True

                #change button to give users a choice to return to the storefront
                button.emoji = '🏪'
                button.label = "Return to Storefront"
                
                #update embed accordingly
                shop_embed = discord.Embed(title="Welcome to The Aristocrat's Emporium\n🎩 Exclusive Item Shop 🎩", description=f"{self.ctx.author.mention}\nThe exclusive item collection offered here in this section of *The Aristocrat's Emporium* is available to only a select few individuals in the world.\n\nTake heed, good patron, for these items are of high quality and extreme value, but are *sure* to round out your lucrative item collection. You shall be the envy of all your peers with items such as these in your possession.\n\n*Feel free to peruse at your leisure and find an item worth your liking, good sir.*", color=discord.Color.from_rgb(20, 53, 219))
                shop_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)          
                
              
                await self.message.edit(embed=shop_embed, view=self)


##############################MARKET###############################





def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Marketplace(bot)) # add the cog to the bot
