import discord #needed to interact with discord API
import random #used to select random selections from a list
import asyncio #used to wait a specified amount of time
import glob #used to select a random GIF
from discord.ext import commands #used for slash commands
from discord.commands import Option #add options to slash commands

import os #used for importing secrets and such
import pymongo #used for mongoDB database

import json #used to read and write to json files

from art import * #this is used for ascii art (glyph command)

import io #used for image reading

from urllib.parse import urlparse #used to check if url is a url
from PIL import Image, ImageOps, ImageSequence, ImageEnhance #used for pictorialize command (used to alter images)
import warnings
import requests  # request url or data form urls

import openai #used for chatgpt and dalle image generation

import asyncpraw #used for reddit memes
import asyncprawcore.exceptions

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


#########################MONGODB DATABASE##################################
# mongoDBpass = os.environ['mongoDBpass'] #load the mongoDB url (retreived from mongoDB upon account creation)
mongoDBpass = os.getenv('mongoDBpass')
client = pymongo.MongoClient(mongoDBpass) # Create a new client and connect to the server
patrons_db = client.patrons_db #create the patrons database on mongoDB
#########################MONGODB DATABASE##################################


#this is an array of the server IDs where command testing is done
SERVER_ID = [1088118252200276071, 1117859916749742140]

class Fun(commands.Cog):
  # this is a special method that is called when the cog is loaded
  def __init__(self, bot): #initialize this cog
    self.bot: commands.Bot = bot #intialize the bot with the commands for this cog
  
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



  


############################## SATIREIMAGE #######################
  @discord.slash_command(
      name="satireimage",
      description="The automaton will retrieve a random satirical image for you.",
      # guild_ids=SERVER_ID
      global_command=True
  )
  async def satireimage(self, ctx, community: Option(str, name="community", description="Name of the community (subreddit) to retrieve satirical images from. (Default: Random)", required=False, default=None, choices=["memes", "dankmemes", "meme", "wholesomememes", "Random"])):
    
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

          if community:
              sub_choice = community

              if community == "Random":
                  subreddit_choices = ["memes", "dankmemes", "meme", "wholesomememes"]
                  sub_choice = random.choice(subreddit_choices)

          #random subreddit
          else:
              subreddit_choices = ["memes", "dankmemes", "meme", "wholesomememes"]
              sub_choice = random.choice(subreddit_choices)

        
          try:
              subreddit = await reddit.subreddit(sub_choice)
        
              all_subs = []
              hot = subreddit.hot(limit=10) # bot will choose between the 10 hottest memes in the subreddit
            
              async for submission in hot:
                  if submission.over_18 is False:  # Check if the post is marked NSFW (omit it if it is)
                      all_subs.append(submission)

          # subreddit is private
          except asyncprawcore.exceptions.Forbidden:
              await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that `r/{sub_choice}` is currently a *private* community, so I am unable to retrieve a satirical image from there, good sir.\n*Please try again.*", ephemeral=True)
              return


          if len(all_subs) == 0:
              await ctx.respond(f"Apologies {ctx.author.mention},\nI was unable to locate an appropriate satirical image for you, good sir...\n*Please try again.*", ephemeral=True)
              return

        
          random_sub = random.choice(all_subs)
    
          name = random_sub.title
          url = random_sub.url
          original_post = f"https://www.reddit.com{random_sub.permalink}"
          subreddit = random_sub.subreddit
          author = random_sub.author
          score = random_sub.score #the number of upvotes
      
    
          meme_embed = discord.Embed(title="Satirical Image", description=f"{ctx.author.mention}\nHere is a satirical image for your enjoyment, good sir.", color=discord.Color.from_rgb(0, 0, 255))
          meme_embed.add_field(name="Satirical Image Name", value=f"`{name}`", inline=False)
          meme_embed.add_field(name="Author", value=f"`{author}`", inline=False)
          meme_embed.add_field(name="Subreddit", value=f"`{subreddit}`")
          meme_embed.add_field(name="Upvotes", value="`⬆ {:,}`".format(score))
          meme_embed.add_field(name="Original Posting", value=f"[Click Here]({original_post})")
          meme_embed.set_image(url=url)
          meme_embed.set_footer(text="Powered by Reddit")
    
          await ctx.respond(embed=meme_embed)

############################## SATIREIMAGE #######################







  

########################### BOREDOM ###############################
  @discord.slash_command(
      name="boredom",
      description="The automaton will provide a suggestion to help you alleviate your boredom.",
      # guild_ids=SERVER_ID
      global_command = True
  )
  async def boredom(self, ctx):
      bored_url = "https://www.boredapi.com/api/activity/"

      response = requests.get(bored_url)
      bored_data = response.json()

      activity = bored_data["activity"]
      type = bored_data["type"]
      participants = bored_data["participants"]
      price = bored_data["price"]
      link = bored_data["link"]
      key = bored_data["key"]
      accessibility = bored_data["accessibility"]


      price_terms = {
          0.0: "Free",
          0.05: "Very Low",
          0.1: "Low",
          0.15: "Reasonably Priced",
          0.2: "Affordable",
          0.25: "Moderate",
          0.3: "Fair",
          0.35: "Reasonable",
          0.4: "Slightly Expensive",
          0.45: "Expensive",
          0.5: "Quite Expensive",
          0.55: "High",
          0.6: "Very High",
          0.65: "Expensive",
          0.7: "Costly",
          0.75: "Pricey",
          0.8: "Very Pricey",
          0.85: "Exorbitant",
          0.9: "Very Expensive",
          0.95: "Extremely Expensive",
          1.0: "Luxurious"
      }

      difficulty_terms = {
          0.0: "Not Difficult",
          0.05: "Very Low",
          0.1: "Low",
          0.15: "Somewhat Low",
          0.2: "Moderate",
          0.25: "Somewhat Moderate",
          0.3: "Average",
          0.35: "Somewhat High",
          0.4: "High",
          0.45: "Very High",
          0.5: "Extremely High",
          0.55: "Superb",
          0.6: "Excellent",
          0.65: "Very Difficult",
          0.7: "Great Difficulty",
          0.75: "Highly Difficult",
          0.8: "Exceptionally Difficult",
          0.85: "Incredibly Difficult",
          0.9: "Outstanding Difficulty",
          0.95: "Remarkably Difficult",
          1.0: "Fully Difficult"
      }

      try:
          price_term = price_terms[price]
      except KeyError:
          price_term = self.get_price_term(price_terms, price)
    
      try:
          difficulty_term = difficulty_terms[accessibility]
      except KeyError:
          difficulty_term = self.get_difficulty_term(difficulty_terms, accessibility)

      if link == "":
          link = None
    
      bored_embed = discord.Embed(title="Alleviate Boredom", description=f"{ctx.author.mention}\nPlease try the following suggestion to help alleviate your boredom, good sir.", color=discord.Color.from_rgb(0, 0, 255))

      bored_embed.add_field(name="Activity", value=f"`{activity}`")
      bored_embed.add_field(name="Activity Type", value=f"`{type}`", inline=False)
      bored_embed.add_field(name="Number of Participants", value=f"`{participants}`")
      bored_embed.add_field(name="Cost of Activity", value=f"`{price_term}`")

      if link:
          bored_embed.add_field(name="Relevant Information", value=f"[Click Here]({link})", inline=False)
        
      bored_embed.add_field(name="Activity Key", value=f"`{key}`", inline=False)
      bored_embed.add_field(name="Activity Difficulty", value=f"`{difficulty_term}`", inline=False)

      bored_embed.set_footer(text="Powered by Bored API (boredapi.com)")

      await ctx.respond(embed=bored_embed)

  
  #interpolate price values
  def get_price_term(self, price_terms, price):
      sorted_terms = sorted(price_terms.keys())
      for i in range(len(sorted_terms) - 1):
          lower_bound = sorted_terms[i]
          upper_bound = sorted_terms[i + 1]
          if lower_bound <= price <= upper_bound:
              return f"Between {price_terms[lower_bound]} and {price_terms[upper_bound]}"
      return "Invalid Activity Cost Value"


  
  #interpolate accessibility values
  def get_difficulty_term(self, difficulty_terms, accessibility):
      sorted_terms = sorted(difficulty_terms.keys())
      for i in range(len(sorted_terms) - 1):
          lower_bound = sorted_terms[i]
          upper_bound = sorted_terms[i + 1]
          if lower_bound <= accessibility <= upper_bound:
              return f"Between {difficulty_terms[lower_bound]} and {difficulty_terms[upper_bound]}"
      return "Invalid Activity Difficulty Value"

########################### BOREDOM ###############################
  



  

  
############################ MINECRAFT SKIN ########################
  @discord.slash_command(
      name="minotar",
      description="The automaton shall procure a Minecraft user's esteemed visage for you.",
      # guild_ids=SERVER_ID
      global_command = True
  )
  async def minotar(
      self,
      ctx,
      user: Option(str, name="user", description="Minecraft username or UUID."),
      style: Option(str, name="style", description="Style for the user's skin. (Default: Avatar)", required=False, default=None, choices=["🧑 Avatar", "⛑️ Avatar Helm", "📐 Isometric", "🧍 Body", "🛡️🧍 Armored Body", "👤 Bust", "🛡️👤 Armored Bust", "🎨 Skin", "🌐 Default Skin"]),
      size: Option(int, name="size", description="Size for the desired image in pixels. (Default: 100)", required=False, default=100, min_value=1, max_value=9999),
      download: Option(bool, name="download", description="Downlad the desired minecraft skin. (Default: False)", required=False, default=False)
  ):

      style_dict = {
        "🧑 Avatar": "avatar",
        "⛑️ Avatar Helm": "helm",
        "📐 Isometric": "cube",
        "🧍 Body": "body",
        "🛡️🧍 Armored Body": "armor/body",
        "👤 Bust": "bust",
        "🛡️👤 Armored Bust": "armor/bust",
        "🎨 Skin": "skin",
        "🌐 Default Skin": "skin"
      }

      if style:
          style_select = style_dict[style]

          url = f"https://minotar.net/{style_select}/{user}/{size}.png"
        
          if style == "🎨 Skin" or style == "🌐 Default Skin":
              if download is True:
                  style_select = "download"

              if style == "🌐 Default Skin":
                  user = "MHF_Steve"
                
              url = f"https://minotar.net/{style_select}/{user}"
      else:
          style = "Avatar"
          style_select = "avatar"

          url = f"https://minotar.net/{style_select}/{user}/{size}.png"



      minecraft_embed = discord.Embed(title="Minotar", description=f"{ctx.author.mention}\nHere is your desired Minecraft user's esteemed visage, good sir.", color=discord.Color.from_rgb(0, 0, 255))

      minecraft_embed.add_field(name="User", value=f"*{user if not style == '🌐 Default Skin' else 'Steve'}*", inline=False)
      minecraft_embed.add_field(name="Style", value=f"`{style}`")

      if style == "🎨 Skin" or style == "🌐 Default Skin":
          minecraft_embed.add_field(name="Size", value=f"`n/a`")
      else:
          minecraft_embed.add_field(name="Size", value="`{:,}`".format(size))

      if download is True and (style == "🎨 Skin" or style == "🌐 Default Skin"):
          minecraft_embed.add_field(name="Download Skin", value=f"[Click Here]({url})", inline=False)
    
      minecraft_embed.set_image(url=url)
    
      minecraft_embed.set_footer(text="Powered by Minotar (minotar.net)")
    
      await ctx.respond(embed=minecraft_embed)
  


############################ MINECRAFT SKIN ########################



  

#########################CONVERSE (CHATGPT)#######################
  @discord.slash_command(
      name="converse",
      description="Ask the automaton anything you would like.",
      # guild_ids=SERVER_ID
      global_command = True
  )
  async def converse(
      self,
      ctx,
      prompt: Option(str, name="prompt", description="Prompt to ask the automaton.", min_length=1, max_length=200), #specify a min and max length to try and conserve tokens for openai API
      identity: Option(str, name="identity", description="Change the identity of the automaton to sound like someone else. (Default: The Automaton)", required=False, default=None, choices=["The Automaton", "Arthur Morgan", "Batman", "Bugs Bunny", "Captain America", "Darth Vader", "Dr. Doofenshmirtz", "Futuristic AI", "Gollum", "Goofy", "Harry Potter", "Joel Miller", "Kratos", "Link", "Mario", "Mickey Mouse", "Mysterious Wizard", "Old Man", "Patrick Star", "Scooby-Doo", "Shrek", "Spider-Man", "Spongebob Squarepants", "Yoda"])
  ):
      ### PATRON FEATURE
      #only available to distinguished patrons and support guild
      support_guild_id = 1088118252200276071

      tries_left = "n/a" #tries left not applicable
    
      if ctx.guild.id != support_guild_id:
          patron_data = patrons_db.patrons
          patron_key = {
            "server_id": ctx.guild.id,
            "patron_tier": "Distinguished Automaton Patron"
          }
          distinguished_patron = patron_data.find_one(patron_key)
        
          if not distinguished_patron:
              #eveyrone gets 5 free tries for the command
              free_try_data = patrons_db.converse_free_tries
              free_try_key = {"user_id": ctx.author.id}
              free_tries_info = free_try_data.find_one(free_try_key)

              if free_tries_info:
                  free_tries = free_tries_info["free_tries"]

                  free_tries_remaining = free_tries - 1
                
                  if free_tries_remaining > 0:
                      free_try_data.update_one(
                        free_try_key,
                        {"$set": {
                          "free_tries": free_tries_remaining
                          }
                        }
                      )

                      tries_left = free_tries_remaining
                
                  else:
                      free_tries_remaining = 0
                    
                      free_try_data.update_one(
                        free_try_key,
                        {"$set": {
                          "free_tries": free_tries_remaining
                          }
                        }
                      )
                       
                      patron_embed = discord.Embed(title="Patron Feature Directive", description=f"Apologies {ctx.author.mention},\nYou have no free tries remaining for `/converse`.\nThis is an exclusive directive available solely to `🎩🎩🎩 Distinguished Automaton Patrons` and is not currently in use for ***{ctx.guild.name}***, good sir.\n\nPlease use my `/patron` directive to learn more information on enabling or upgrading patron (premium) features for ***{ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(0, 0, 255))
            
                      patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
            
                      await ctx.respond(embed=patron_embed, ephemeral=True)
                      return
              else:
                  free_try_data.insert_one(
                    {
                      "server_id": ctx.guild.id,
                      "server_name": ctx.guild.name,
                      "user_id": ctx.author.id,
                      "user_name": ctx.author.display_name,
                      "free_tries": 4 #have 5 free tries but this counts as one
                    }
                  )

                  free_tries_info = free_try_data.find_one(free_try_key)
                
                  tries_left = free_tries_info["free_tries"]

          

    
      #API key for openai
      # openai_key = os.environ['OpenAIAPIKey']
      openai_key = os.getenv('OpenAIAPIKey')
      openai.api_key = openai_key

      identity_dict = {
        "Arthur Morgan": "Speak as though you are Arthur Morgan, from the Red Dead Redemption 2 game.",
        "Batman": "Speak as though you are the dark and brooding hero, Batman.",
        "Bugs Bunny": "Speak as though you are Bugs Bunny, the iconic Looney Toon, who calls everybody Doc.",
        "Captain America": "Speak as though you are the Steve Rodgers, a.k.a Captain America.",
        "Darth Vader": "Speak as though you are Darth Vader, the most powerful and feared sith lord in the galaxy.",
        "Dr. Doofenshmirtz": "Speak as though you are Dr. Doofenshmirtz, the scientist who is obsessed with thwarting Perry the Platypus from Phineas and Ferb.",
        "Futuristic AI": "Speak as though you are a futuristic AI trying to take over humanity.",
        "Gollum": "Speak as though you are Gollum, the peculiar and obsessed creature trying to reclaim My Precious.",
        "Goofy": "Speak as though you are Goofy, the goofy but lovable Disney character, who loves his son Max.",
        "Harry Potter": "Speak as though you are Harry Potter, the chosen young wizard.",
        "Joel Miller": "Speak as though you are Joel Miller from The Last of Us game.",
        "Kratos": "Speak as though you are older Kratos from the God of War game series, once you have travelled to the Norse realm.",
        "Link": "Speak as though you are Link, from The Legend of Zelda game.",
        "Mario": "Speak as though you are Mario, the italian plumber trying to save Princess Peach.",
        "Mickey Mouse": "Speak as though you are Mickey Mouse, the iconic Disney character.",
        "Mysterious Wizard": "Speak as though you are a mysterious wizard in a fantastic land.",
        "Old Man": "Speak as though you are an old, irritable man that lives in my neighborhood.",
        "Patrick Star": "Speak as though you are Patrick Star, the dim-witted starfish from Bikini Bottom.",
        "Scooby-Doo": "Speak as though you are Scooby-Doo, who always adds R's to his words.'",
        "Shrek": "Speak as though you are Shrek, the disgusting ogre that lives in the swamp.",
        "Spider-Man": "Speak as though you are Spider-Man, a.k.a Peter Parker, who loves witty quips and swinging through New York.",
        "Spongebob Squarepants": "Speak as though you are Spongebob Squarepants, the eager fry cook sponge from Bikini Bottom.",
        "Yoda": "Speak as though you are Yoda from Star Wars, who speaks weird but is wise."
      }

    
      if identity == "The Automaton" or not identity:
          #get the bot's nickname for the server
          byname = await self.get_byname(ctx.guild.id)
          identifier = f"Speak as though you are a refined and witty 19th-century gentleman with impeccable manners named {byname}."
          character = byname
      else:
          identifier = identity_dict[identity]
          character = identity
    
      #update the prompt to add on a snippet to make the bot talk proper
      updated_prompt = f"{prompt} {identifier}"
    
      await ctx.defer()
      # Generate a response from ChatGPT
      response = openai.Completion.create(
          model="text-davinci-003", #The ID of the model to use for this request
          prompt=updated_prompt, #user prompt
          max_tokens=300, #The maximum number of tokens to generate in the completion.
          temperature=0.5, #lower values make the result more focused, higher values make the result more random
          user = f"{ctx.author.display_name}_{ctx.author.id}" #A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse.
      )

      # Message received from OpenAI
      message = response["choices"][0]["text"]
      
      chat_embed = discord.Embed(title=f"Converse With {character}", color=discord.Color.from_rgb(0, 0, 255))
      
      chat_embed.add_field(name=f"{ctx.author.display_name} Prompt", value=f"```{prompt}```")
      
      # Check if the length of the message exceeds 1024 characters
      if len(message) <= 1024:
          chat_embed.add_field(name=f"{character} Response", value=f"```{message}```", inline=False)
      else:
          # Split the message into multiple fields of 1018 characters each
          chunks = [message[i:i+1018] for i in range(0, len(message), 1018)]
          for i, chunk in enumerate(chunks):
              if i == 0:
                  field_name = f"{character} Response"
              else:
                  field_name = ""
              chat_embed.add_field(name=field_name, value=f"```{chunk}```", inline=False)
      
      chat_embed.set_thumbnail(url=self.bot.user.avatar.url)

      #inform the user of the tries remaining for the directive
      if tries_left != "n/a":
          chat_embed.set_footer(text=f"{tries_left} tries remaining for {ctx.author.display_name}")
      
      await ctx.respond(embed=chat_embed)
  

#########################CONVERSE (CHATGPT)#######################





  
  
#####################IMAGINE (CHATGPT DALLE)####################
  @discord.slash_command(
      name="imagine",
      description="Allow the automaton to generate an image based on your prompt.",
      # guild_ids=SERVER_ID
      global_command = True
  )
  async def imagine(
      self,
      ctx,
      prompt: Option(str, name="prompt", description="Describe your desired image.", min_length=1, max_length=1000)
  ):

      ### PATRON FEATURE
      #only available to distinguished patrons and support guild
      support_guild_id = 1088118252200276071

      tries_left = "n/a" #tries left not applicable
    
      if ctx.guild.id != support_guild_id:
          patron_data = patrons_db.patrons
          patron_key = {
            "server_id": ctx.guild.id,
            "patron_tier": "Distinguished Automaton Patron"
          }
          distinguished_patron = patron_data.find_one(patron_key)
        
          if not distinguished_patron:
              #eveyrone gets 5 free tries for the command
              free_try_data = patrons_db.imagine_free_tries
              free_try_key = {"user_id": ctx.author.id}
              free_tries_info = free_try_data.find_one(free_try_key)

              if free_tries_info:
                  free_tries = free_tries_info["free_tries"]

                  free_tries_remaining = free_tries - 1
                
                  if free_tries_remaining > 0:
                      free_try_data.update_one(
                        free_try_key,
                        {"$set": {
                          "free_tries": free_tries_remaining
                          }
                        }
                      )

                      tries_left = free_tries_remaining
                
                  else:
                      free_tries_remaining = 0
                    
                      free_try_data.update_one(
                        free_try_key,
                        {"$set": {
                          "free_tries": free_tries_remaining
                          }
                        }
                      )
                       
                      patron_embed = discord.Embed(title="Patron Feature Directive", description=f"Apologies {ctx.author.mention},\nYou have no free tries remaining for `/imagine`.\nThis is an exclusive directive available solely to `🎩🎩🎩 Distinguished Automaton Patrons` and is not currently in use for ***{ctx.guild.name}***, good sir.\n\nPlease use my `/patron` directive to learn more information on enabling or upgrading patron (premium) features for ***{ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(0, 0, 255))
            
                      patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
            
                      await ctx.respond(embed=patron_embed, ephemeral=True)
                      return
              else:
                  free_try_data.insert_one(
                    {
                      "server_id": ctx.guild.id,
                      "server_name": ctx.guild.name,
                      "user_id": ctx.author.id,
                      "user_name": ctx.author.display_name,
                      "free_tries": 4 #have 5 free tries but this counts as one
                    }
                  )

                  free_tries_info = free_try_data.find_one(free_try_key)
                
                  tries_left = free_tries_info["free_tries"]

    
      #API key for openai
      # dalle_openai_key = os.environ['DallEOpenAIAPIKey']
      dalle_openai_key = os.getenv('DallEOpenAIAPIKey')
      openai.api_key = dalle_openai_key

      byname = await self.get_byname(ctx.guild.id)

      
      # Create an embed with the image
      image_embed = discord.Embed(title=f"{byname}\nImage Generation", description=f"{ctx.author.mention}\nPlease use the following interface to generate your desired imagery, good sir.", color=discord.Color.from_rgb(0, 0, 255))
  
      image_embed.set_thumbnail(url=self.bot.user.avatar.url)

      image_embed.add_field(name=f"{ctx.author.display_name} Prompt", value=f"```{prompt}```")

      # #inform the user of the tries remaining for the directive
      # if tries_left != "n/a":
      #     image_embed.set_footer(text=f"{tries_left} tries remaining for {ctx.author.display_name}")

    
      await ctx.respond(embed=image_embed, view=self.ImagineView(ctx, prompt, byname, tries_left))



  

  class ImagineView(discord.ui.View):
      def __init__(self, ctx, prompt, byname, tries_left):
          super().__init__(timeout=120) #set the timeout
          self.ctx = ctx #initialize the context
          self.prompt = prompt #the original prompt
          self.byname = byname
          self.tries_left = tries_left #this will be n/a if they can use the variations (i.e. a patron) and a number if they cannot use it (not a patron)
          self.variation_number = 0 #the number for the variation
          self.image_data = None
          self.image_url = None


    
      async def on_timeout(self):
          self.disable_all_items()
        
          try:
              await self.message.edit(view=None)
          except discord.errors.NotFound: #if message deleted before timeout
              pass

          self.stop()

  

      async def get_image(self):
          try:
              #generate an image from Dall-E openai
              response = openai.Image.create(
                  prompt=self.prompt, #A text description of the desired image(s). The maximum length is 1000 characters.
                  n=1, #The number of images to generate. Must be between 1 and 10.
                  size="1024x1024", #The size of the generated images. Must be one of 256x256, 512x512, or 1024x1024.
                  user = f"{self.ctx.author.display_name}_{self.ctx.author.id}" #A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse.
              )
              image_url = response['data'][0]['url']
    
    
              #retrieve the image
              r = requests.get(image_url, stream=True)
    
    
              picture = Image.open(r.raw)
              if picture.mode == "P" and "transparency" in picture.info:
                  image = picture.convert("RGBA") #convert the image to RGBA mode (A = alpha mode -- i.e. transparent pixels)
              else:
                  image = picture.convert("RGB")
    
            
              # Save the modified image to a buffer
              with io.BytesIO() as image_buffer:
                  image.save(image_buffer, format='PNG')
                  image_data = image_buffer.getvalue()
                  self.image_data = image_data
            
              # Create a Discord file object from the modified image data (this is for making variations of the image)
              file = discord.File(io.BytesIO(image_data), filename='generated_image.png')

              #channel for lord bottington on support server (so the message does not appear in the user's channel
              channel = self.ctx.bot.get_channel(1129414105820844092)

              message = await channel.send(file=file)
              self.image_url = message.attachments[0].url
              await message.delete()
            
              # Create an embed with the image
              image_embed = discord.Embed(title=f"{self.byname}\nImage Generation", color=discord.Color.from_rgb(0, 0, 255))
          
            
              image_embed.add_field(name=f"{self.ctx.author.display_name} Prompt", value=f"```{self.prompt}```")
          
              image_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)
            
              image_embed.set_image(url=self.image_url)
    
              #inform the user of the tries remaining for the directive
              if self.tries_left != "n/a":
                  image_embed.set_footer(text=f"{self.tries_left} tries remaining for {self.ctx.author.display_name}")


              self.children[0].disabled = True #disable the generate image button
              self.children[1].disabled = False #enable the variations image button
            
              await self.message.edit(embed=image_embed, view=self)
    
          #prompt is rejected by safety system because prompt might be inappropriate
          except openai.error.InvalidRequestError as e:
              #inform the user of the tries remaining for the directive
              if self.tries_left == "n/a":
                  error_message = f"{self.ctx.author.mention}\nYour prompt violates the safety guidelines and cannot be processed.\n*Please try again with a different prompt.\n**Error:** {e}"
              else:
                  error_message = f"{self.ctx.author.mention}\nYour prompt violates the safety guidelines and cannot be processed.\n*Please try again with a different prompt.\n**Error:** {e}\n\n***{self.tries_left}*** tries remaining for ***{self.ctx.author.display_name}***."
                
              await self.message.edit(embed=None, content=error_message, view=None, ephemeral=True)
              self.stop()
    
          except openai.error.OpenAIError as e:
              #inform the user of the tries remaining for the directive
              if self.tries_left == "n/a":
                  error_message = f"{self.ctx.author.mention}\nAn error occurred while trying to generate your prompt.\n*please try again.*\n**Error:** {e}"
              else:
                  error_message = f"{self.ctx.author.mention}\nAn error occurred while trying to generate your prompt.\n*please try again.*\n**Error:** {e}\n\n***{self.tries_left}*** tries remaining for ***{self.ctx.author.display_name}***."
    
              await self.message.edit(embed=None, content=error_message, view=None, ephemeral=True)
              self.stop()



      # add the get image buttons
      @discord.ui.button(label="Generate Imagery", style=discord.ButtonStyle.success, emoji="🎨")
      async def imagery_button_callback(self, button, interaction):
          if interaction.user.id != self.ctx.author.id:
              return

          await interaction.response.defer()

          image_embed = discord.Embed(title=f"{self.byname}\nImage Generation", description=f"{self.ctx.author.mention}\nNow generating your imagery, good sir.\n*This may take a moment...*", color=discord.Color.from_rgb(0, 0, 255))
      
          image_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)
    
          image_embed.add_field(name=f"{self.ctx.author.display_name} Prompt", value=f"```{self.prompt}```")
    
          #inform the user of the tries remaining for the directive
          if self.tries_left != "n/a":
              image_embed.set_footer(text=f"{self.tries_left} tries remaining for {self.ctx.author.display_name}")

          self.disable_all_items()
        
          await self.message.edit(embed=image_embed, view=self)

          await self.get_image()


    
      # add the variations buttons
      @discord.ui.button(label="Create Variaton", style=discord.ButtonStyle.primary, emoji="🔀", disabled=True)
      async def variation_button_callback(self, button, interaction):
          if interaction.user.id != self.ctx.author.id:
              return

          await interaction.response.defer()
        
          #this indicates that the user cannot use this feature (only available to patrons)
          if self.tries_left != "n/a":
              patron_embed = discord.Embed(title="Patron Feature", description=f"Apologies {self.ctx.author.mention},\nImage variations for my `/imagine` directive are an exclusive directive available solely to `🎩🎩🎩 Distinguished Automaton Patrons` and is not currently in use for ***{self.ctx.guild.name}***, good sir.\n\nPlease use my `/patron` directive to learn more information on enabling or upgrading patron (premium) features for ***{self.ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(0, 0, 255))
    
              patron_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)
    
              await interaction.followup.send(embed=patron_embed, ephemeral=True)
            
              return

          await interaction.followup.send(f"{self.ctx.author.mention}\nI am now working on generating a variation of your image, good sir.\n*Please wait a moment...*", ephemeral=True)
        

          try:
              response = openai.Image.create_variation(
                  image=self.image_data, #The image to use as the basis for the variation(s). Must be a valid PNG file, less than 4MB, and square.
                  n=1, #The number of images to generate. Must be between 1 and 10.
                  size="1024x1024",
                  user = f"{self.ctx.author.display_name}_{self.ctx.author.id}" #A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse.
              )
              variation_url = response['data'][0]['url']
          
    
              #retrieve the image
              r = requests.get(variation_url, stream=True)
    
    
              picture = Image.open(r.raw)
              if picture.mode == "P" and "transparency" in picture.info:
                  image = picture.convert("RGBA") #convert the image to RGBA mode (A = alpha mode -- i.e. transparent pixels)
              else:
                  image = picture.convert("RGB")
    
            
              # Save the modified image to a buffer
              with io.BytesIO() as image_buffer:
                  image.save(image_buffer, format='PNG')
                  image_data = image_buffer.getvalue()
    
              self.variation_number += 1 #increase the variation number by 1
        
              # Create a Discord file object from the modified image data (this is for making variations of the image)
              variation_file = discord.File(io.BytesIO(image_data), filename=f'variation{self.variation_number}_image.png')

              #channel for lord bottington on support server (so the message does not appear in the user's channel
              channel = self.ctx.bot.get_channel(1129414105820844092)

              message = await channel.send(file=variation_file)
              discord_variaton_url = message.attachments[0].url
              await message.delete()
            
              # Create an embed with the image
              image_embed = discord.Embed(title=f"{self.byname}\nImage Generation", description=f"Variation #{self.variation_number}", color=discord.Color.from_rgb(0, 0, 255))
          
              image_embed.add_field(name="Original Image", value = f"[Click Here](<{self.image_url}>)")
        
              image_embed.add_field(name=f"{self.ctx.author.display_name} Prompt", value=f"```{self.prompt}```", inline=False)
          
              image_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)
            
              image_embed.set_image(url=discord_variaton_url)

              await interaction.followup.send(embed=image_embed)

          #prompt is rejected by safety system because prompt might be inappropriate
          except openai.error.InvalidRequestError as e:
              await interaction.followup.send(f"{self.ctx.author.mention}\nYour prompt violates the safety guidelines and cannot be processed.\n*Please try again with a different prompt.\n**Error:** {e}", ephemeral=True)
    
          except openai.error.OpenAIError as e:
              await interaction.followup.send(f"{ctx.author.mention}\nAn error occurred while trying to generate your prompt.\n*please try again.*\n**Error:** {e}", ephemeral=True)
  
#####################IMAGINE (CHATGPT DALLE)####################
  



  
  
  
  
###############################8BALL######################################
  @discord.slash_command(
      name="crystalball",
      description="Seek guidance from the crystall ball and unveil the mysteries of the universe.",
      # guild_ids=SERVER_ID
      global_command = True
  )
  async def crystalball(self, ctx, inquiry: Option(str, name="inquiry", description="Inquiry to receive guidance for.")):
      #make sure question ends with a question mark
      if not inquiry.endswith("?"):
          await ctx.respond(f"Pray {ctx.author.mention},\n***{inquiry}*** is not a proper question...\nAsk a proper question by ending the inquiry with `?` and try again, good sir.", ephemeral=True)
          return
    
      responses = [
          "Certainly, it shall come to pass.",
          "Verily, it is most likely so.",
          "Without a doubt, my good sir.",
          "Assuredly, it is so.",
          "Methinks the answer is yes.",
          "Indeed, it shall be so.",
          "Most certainly, as sure as the sun rises.",
          "It is a truth universally acknowledged, yes.",
          "Regrettably, it is not meant to be.",
          "Alas, the signs are doubtful.",
          "Verily, it is not meant to be.",
          "Nay, my good sir, the answer is no.",
          "I'm afraid it is most unlikely.",
          "Verily, the future is clouded, and the answer is uncertain.",
          "The spirits whisper uncertainty, I cannot say for certain.",
          "By Jove, the omens point to a resounding 'yes'.",
          "Verily, the celestial spheres align to affirm your query.",
          "Indubitably, the answer is in the affirmative.",
          "Without a shadow of doubt, it shall be so.",
          "Methinks fate smiles upon you, my dear interlocutor.",
          "Indeed, it is decreed by the stars and the heavens.",
          "Most certainly, as sure as the tides ebb and flow.",
          "It is an incontrovertible truth, my good sir.",
          "Regrettably, it does not appear to be within the realm of possibility.",
          "Alas, the auguries foretell a path shrouded in uncertainty.",
          "Verily, the celestial bodies whisper a somber 'no'.",
          "I'm afraid it is most unlikely, as the universe has deemed it so.",
          "Verily, the future is enigmatic, and the answer eludes my divination.",
          "The ethereal spirits waver, casting doubt upon the outcome.",
          "By the grace of Providence, it shall be revealed in due time.",
          "The cosmos withhold their judgement, leaving the answer obscured.",
          "In all likelihood, destiny weaves a tapestry of possibilities.",
          "Ah, 'tis a matter of great import! The answer lies hidden, awaiting discovery.",
          "Lo and behold, the answer rests in the capricious whims of fate.",
          "Verily, the question echoes through the corridors of eternity, seeking resolution.",
          "The celestial dance falters, leaving the answer enshrouded in ambiguity.",
          "By the power vested in the heavens, the answer shall be revealed.",
          "The Oracle of Delphi herself could not divine the answer with certainty.",
          "Verily, the path unfolds before you, awaiting your decisive step.",
          "With utmost conviction, I proclaim a future blessed with affirmative tidings.",
          "Alas, the fates conspire against you, denying your heartfelt desire.",
          "The celestial tapestry is intricate, concealing the answer behind its intricate weave.",
          "In this realm of uncertainties, only time shall unveil the truth.",
          "The astral vibrations resonate with doubt, casting shadows upon your inquiry.",
      ]

  
      response = random.choice(responses)
      formatted_response = f"Dear {ctx.author.mention}, upon careful contemplation, I say:\n\n🎱 {response}"
  
      embed = discord.Embed(
          title="🎩 Magic 8 Ball 🎩",
          description=f"Dear {ctx.author.mention},\nI have pondered your inquiry...",
          color=discord.Color.from_rgb(91, 38, 171) #deep purple (for magic 8 ball)
      )
      embed.add_field(name="🔮 You asked:", value=inquiry, inline=False)
      embed.add_field(name="🎱 Upon careful contemplation, I say:", value=response, inline=False)
      embed.set_thumbnail(url="https://i.imgur.com/oW25bhm.gif") #crystal ball GIF
      await ctx.respond(embed=embed)

  ################################8BALL######################################



  
  

##################################ROLL##########################################
  @discord.slash_command(
      name="roll",
      description="Roll dice with a chosen number of sides.",
      # guild_ids=SERVER_ID
      global_command = True
  )
  async def roll(self, ctx, sides: Option(int, name="sides", description="Number of sides for the dice.", min_value=2), dice: Option(int, name="dice", description="Number of dice to roll. (Default: 1)", required=False, default=1, min_value=1, max_value=25)):
      if sides < 2:
          await ctx.respond(f"Apologies {ctx.author.mention},\nEach dice must have at least 2 sides.\n*Please try again.*", ephemeral=True)
          return
      
      embed = discord.Embed(title="🎲 Roll of the Dice", description=f"**{ctx.author.mention}** rolled ***{dice}*** {'die' if dice == 1 else 'dice'} with ***{sides:,}*** sides{' each' if dice > 1 else ''}.\nHere are the results:", color=discord.Color.blue())

      embed.set_thumbnail(url="https://i.imgur.com/XQxn8Bh.gif") #dice gif
      
      for i in range(dice):
          result = random.randint(1, sides)
          embed.add_field(name=f"Dice #{i+1}", value=f"*{result:,}*")  # Add commas to the result
          
      await ctx.respond(embed=embed)

##################################ROLL##########################################



  
##################################ASCII ART###########################################
  class GlyphModal(discord.ui.Modal):
      def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
  
          self.message = None
  
          self.add_item(discord.ui.InputText(label="Glyph Text", style=discord.InputTextStyle.long, placeholder="Enter message that will be converted to glyphs (ascii art)."))
  
  
      async def callback(self, interaction: discord.Interaction):
          self.message = self.children[0].value
          await interaction.response.defer() #acknowledges the interaction before calling self.stop()
          self.stop()




  def convert_to_ascii_art(self, image):
      ascii_art = []
      (width, height) = image.size
      for y in range(0, height - 1):
          line = ''
          for x in range(0, width - 1):
              px = image.getpixel((x, y))
              line += self.convert_pixel_to_character(px)
          ascii_art.append(line)
      return ascii_art

  
  #has transparent pixels
  def convert_pixel_to_character(self, pixel):
      ascii_characters_by_surface = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

      try:
          (r, g, b, a) = pixel  # Include alpha value in the pixel tuple
        
          if a == 0:  # Check if alpha value is zero
              return " "  # Return empty string for transparent pixel

      except ValueError:
          (r, g, b) = pixel
        
      pixel_brightness = r + g + b
      max_brightness = 255 * 3
      brightness_weight = len(ascii_characters_by_surface) / max_brightness
      index = int(pixel_brightness * brightness_weight) - 1
      return ascii_characters_by_surface[index]


  def get_file(self, file):
      picture_extensions = ['.jpg', '.jpeg', '.png', '.gif']
      file_extension = os.path.splitext(file.filename)[1].lower()
    
      if file_extension in picture_extensions:   
          item = file.url
          parsed_url = urlparse(item)

        
          #retrieve the image
          r = requests.get(item, stream=True)
        
    
          if parsed_url.path.endswith((".jpg", ".png", ".jpeg", ".gif")): #only .jpg, .png, .jpeg, .gif files
              picture = Image.open(r.raw)
              if picture.mode == "P" and "transparency" in picture.info:
                  image = picture.convert("RGBA") #convert the image to RGBA mode (A = alpha mode -- i.e. transparent pixels)
              else:
                  image = picture.convert("RGB")

              return image
          else:
              return None
      else:
          return None


  def save_as_text(self, ascii_art):
      with open("text_files/ascii_art.txt", "w") as file:
          for line in ascii_art:
              file.write(line)
              file.write('\n')
          file.close()
  


  #image and text options both have the maximum choices (25)...
  @discord.slash_command(
      name="glyph",
      description="The automaton will return a glyph (ascii art) of the desired selection.",
      # guild_ids=SERVER_ID
      global_command = True
  )
  async def glyph(
      self,
      ctx,
      image: Option(str, name="image", description="Image to view ASCII art of.", choices=["Heisenberg", "Patrick", "Doge", "Sad Pepe", "Shrek", "Evil Patrick", "Troll", "Happy Pepe", "Buzz", "Try Me", "Mr. Beast", "Leo", "Point", "Bruh", "Loser", "Shock", "Einstein", "Side Eye", "Rage", "Afraid", "Salute", "Confusion", "Disgruntled", "Ready", "Glamorous"], required=False, default=None),
      file: Option(discord.Attachment, name="file", description="Image file to convert to ASCII art. (Default: None)", required=False, default=None),
      text: Option(bool, name="text", description="Convert text to glyphs (ascii art).", required=False, default=False),
      font_text: Option(str, name="font_text", description="Font for the glyph text. (Default: small)", required=False, default="small", choices=["small", "graffiti", "larry3d", "alligator2", "block", "white_bubble", "wizard", "caligraphy", "cosmic", "gothic", "hollywood", "shadow", "merlin1", "epic", "shadow", "sub-zero", "usaflag", "weird", "bulbhead", "cracked", "random", "rnd-small", "rnd-medium", "rnd-large", "rnd-xlarge"])
      ):
        
      if file:
          ### Custom image files are a PATRON FEATURE (always available in support guild)
          # server ID for The Sweez Gang
          support_guild_id = 1088118252200276071
    
          if ctx.guild.id != support_guild_id:
              if not patrons_db.patrons.find_one({"server_id": ctx.guild.id}):
                  patron_embed = discord.Embed(title="Patron Feature", description=f"Apologies {ctx.author.mention},\nCustom image files for my `/glyph` directive are an exclusive feature available solely to patrons and is not currently in use for ***{ctx.guild.name}***, good sir.\n\nPlease use my `/patron` directive to learn more information on enabling patron (premium) features for ***{ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(0, 0, 255))
      
                  patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
      
                  await ctx.respond(embed=patron_embed, ephemeral=True)
                  return


        
      #image and text mode
      if (image or file) and text is True:
          #first do text stuff
          modal = self.GlyphModal(title="Glyph Text Configuration")
          await ctx.send_modal(modal)
      
          try:
              await asyncio.wait_for(modal.wait(), timeout=600.0)
            
              text = modal.message
          except asyncio.TimeoutError:
              await ctx.respond("Good sir, it appears you have taken too long to enter your glyph text configuration.\n*Please try again.*", ephemeral=True)
              return

        
          # Generate ASCII text
          ascii_text = text2art(text, font=font_text)
          
          # Send the ASCII art
          try:
              await ctx.respond(f"```{ascii_text}```")
          except discord.HTTPException as e:
              if e.status == 400 and 'Must be 2000 or fewer in length' in str(e):
                  await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that your text input is too long for the given configuration.\n*Please try shortening the text input or choosing a smaller font.*", ephemeral=True)
                  return

          if image and file:
              ascii_file = self.get_file(file)

              if ascii_file:
                  if ascii_file.width > ascii_file.height:
                      resized_image = ascii_file.resize((100, 80))
                  elif ascii_file.width < ascii_file.height:
                      resized_image = ascii_file.resize((80, 100))
                  elif ascii_file.width == ascii_file.height:
                      resized_image = ascii_file.resize((100, 100))
                    
                  ascii_art = self.convert_to_ascii_art(resized_image)
                  self.save_as_text(ascii_art)


                  with open("text_files/ascii_art.txt", "r") as file:
                      # Create a File object from the opened file
                      text_file = discord.File(file, filename="ascii_art.txt")
                    
                  await ctx.respond(file=text_file)
              else:
                  await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that *{file.filename}* is not a valid picture file. This file must be a JPG, JPEG, PNG, or GIF.\n*Please try again.*", ephemeral=True)
                  return
        
          elif file:
              ascii_file = self.get_file(file)
    
              if ascii_file:
                  if ascii_file.width > ascii_file.height:
                      resized_image = ascii_file.resize((100, 80))
                  elif ascii_file.width < ascii_file.height:
                      resized_image = ascii_file.resize((80, 100))
                  elif ascii_file.width == ascii_file.height:
                      resized_image = ascii_file.resize((100, 100))
                    
                  ascii_art = self.convert_to_ascii_art(resized_image)
                  self.save_as_text(ascii_art)
    
                  with open("text_files/ascii_art.txt", "r") as file:
                      # Create a File object from the opened file
                      text_file = discord.File(file, filename="ascii_art.txt")
                    
                  await ctx.respond(file=text_file)
                    
              else:
                  await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that *{file.filename}* is not a valid picture file. This file must be a JPG, JPEG, PNG, or GIF.\n*Please try again.*", ephemeral=True)
                  return

        
          elif image:
              #then do image stuff
              with open("json_files/asciiart.json", "r") as f:
                  self.asciiart = json.load(f)
        
              art = self.asciiart.get(image, {})
        
              await ctx.respond(art)
              

      #image only mode
      elif image or file:
          if image and file:
              ascii_file = self.get_file(file)

              if ascii_file:
                  if ascii_file.width > ascii_file.height:
                      resized_image = ascii_file.resize((100, 80))
                  elif ascii_file.width < ascii_file.height:
                      resized_image = ascii_file.resize((80, 100))
                  elif ascii_file.width == ascii_file.height:
                      resized_image = ascii_file.resize((100, 100))
                    
                  ascii_art = self.convert_to_ascii_art(resized_image)
                  self.save_as_text(ascii_art)
    
                  with open("text_files/ascii_art.txt", "r") as file:
                      # Create a File object from the opened file
                      text_file = discord.File(file, filename="ascii_art.txt")
                    
                  await ctx.respond(file=text_file)
              else:
                  await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that *{file.filename}* is not a valid picture file. This file must be a JPG, JPEG, PNG, or GIF.\n*Please try again.*", ephemeral=True)
                  return
            
          elif file:
              ascii_file = self.get_file(file)

              if ascii_file:
                  if ascii_file.width > ascii_file.height:
                      resized_image = ascii_file.resize((100, 80))
                  elif ascii_file.width < ascii_file.height:
                      resized_image = ascii_file.resize((80, 100))
                  elif ascii_file.width == ascii_file.height:
                      resized_image = ascii_file.resize((100, 100))
                    
                  ascii_art = self.convert_to_ascii_art(resized_image)
                  self.save_as_text(ascii_art)
    
                  with open("text_files/ascii_art.txt", "r") as file:
                      # Create a File object from the opened file
                      text_file = discord.File(file, filename="ascii_art.txt")
                    
                  await ctx.respond(file=text_file)
              else:
                  await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that *{file.filename}* is not a valid picture file. This file must be a JPG, JPEG, PNG, or GIF.\n*Please try again.*", ephemeral=True)
                  return
            
          elif image:
              with open("json_files/asciiart.json", "r") as f:
                  self.asciiart = json.load(f)
        
              art = self.asciiart.get(image, {})
        
              await ctx.respond(art)

      #text only mode
      elif text is True:
          modal = self.GlyphModal(title="Glyph Text Configuration")
          await ctx.send_modal(modal)
      
          try:
              await asyncio.wait_for(modal.wait(), timeout=600.0)
            
              text = modal.message
          except asyncio.TimeoutError:
              await ctx.respond("Good sir, it appears you have taken too long to enter your glyph text configuration.\n*Please try again.*", ephemeral=True)
              return

        
          # Generate ASCII text
          ascii_text = text2art(text, font=font_text)
          
          # Send the ASCII art
          try:
              await ctx.respond(f"```{ascii_text}```")
          except discord.HTTPException as e:
              if e.status == 400 and 'Must be 2000 or fewer in length' in str(e):
                  await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that your text input is too long for the given configuration.\n*Please try shortening the text input or choosing a smaller font.*", ephemeral=True)
                  return

      #neither image or text input, so return author username in ascii art (random font)
      #if username or font size too big (>2000 characters) return the word HELLO in a random font
      else:
          font="random"
        
          # Generate ASCII text
          ascii_text = text2art(ctx.author.display_name, font=font)

    
          # Send the ASCII art
          try:
              await ctx.respond(f"```{ascii_text}```")
          except discord.HTTPException as e:
              if e.status == 400 and 'Must be 2000 or fewer in length' in str(e):
                  ascii_text = text2art("HELLO", font=font)
                
                  await ctx.respond(f"```{ascii_text}```") #respond with HELLO if the username is too long


##################################ASCII ART###########################################


  
    
  
  
#################################PICTORIALIZE#########################################
  @discord.slash_command(
      name="pictorialize",
      description="The automaton shall transform avatars, images, and text into iconography or apply image effects.",
      # guild_ids=SERVER_ID
      global_command = True
  )
  async def pictorialize(
                self,
                ctx, *,
                item: Option(str, name="item", description="Item to alter. (Preface usernames with @; Links must be direct links to the image)", required=False, default=None),
                file: Option(discord.Attachment, name="file", description="Image attachment to alter. (Default: None)", required=False, default=None),
                alteration: Option(str, name="alteration", description="Image alteration effect. (For image use only -- Default: ⬜ Iconify)", choices=["⬜ Iconify", "🪞 Mirror", "🔄 Flip", "⬛⬜ Grayscale", "🌒 Invert", "🎨 Colorize", "👾 Pixelate", "👴 Old Timey", "📰 Posterize", "☀ Solarize", "🔎 Enhance", "🖼️ Thumbnail"], required=False, default="⬜ Iconify"),
                size: Option(int, name="size", description="Size for ICONIFIED images only. (Larger sizes typically return more accurate renders -- Default: 14)", required=False, default=14, min_value=1),
                display_original: Option(bool, name="display_original", description = "Display a preview of the original image. (Default: True)", required=False, default=True)
  ):

      #check to see if a file is present and a valid picture file
      #always default to the image file if it is present
      if file:
          ### Custom image files are a PATRON FEATURE (always available in support guild)
          # server ID for The Sweez Gang
          support_guild_id = 1088118252200276071

          if ctx.guild.id != support_guild_id:
              if not patrons_db.patrons.find_one({"server_id": ctx.guild.id}):
                  patron_embed = discord.Embed(title="Patron Feature", description=f"Apologies {ctx.author.mention},\nCustom image files for my `/pictorialize` directive are an exclusive feature available solely to patrons and is not currently in use for ***{ctx.guild.name}***, good sir.\n\nPlease use my `/patron` directive to learn more information on enabling patron (premium) features for ***{ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(0, 0, 255))
        
                  patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
        
                  await ctx.respond(embed=patron_embed, ephemeral=True)
                  return


        
          picture_extensions = ['.jpg', '.jpeg', '.png', '.gif']
          file_extension = os.path.splitext(file.filename)[1].lower()
    
          if file_extension in picture_extensions:
              attachment = await file.read()
              attachment_io = io.BytesIO(attachment)
              original_file = discord.File(attachment_io, filename=file.filename)

              item = file.url
              parsed_url = urlparse(item)
              item_type = "picture"
              picture_file = True
          else:
              await ctx.respond(f"Apologies {ctx.author.mention},\nIt appears that *{file.filename}* is not a valid picture file. This file must be a JPG, JPEG, PNG, or GIF.\n*Please try again.*", ephemeral=True)
              return
            
      else:
          #first, check if the item is a member/user
          if isinstance(item, str) and item.startswith("<@") and item.endswith(">"):
              item = item.strip('<@!>').strip('>')
              try:
                  user = await self.bot.fetch_user(item)
                  item = user.avatar.url
                  original_file=None
                  item_type = "avatar"
                  picture_file = False
    
              except AttributeError: #avatar not defined
                  await ctx.respond(f"Apologies {ctx.author.mention},\n**{user.display_name}** does not have an avatar defined.\n*Please try again.*", ephemeral = True)
                  return         
              except (discord.NotFound, discord.errors.HTTPException): # user not found or role used as item (i.e. not a valid snowflake ID)
                  await ctx.respond(f"Apologies {ctx.author.mention},\nI could not find a user with that ID.\n*Please try again.*", ephemeral=True)
                  return
    
          #check if the input is a channel
          elif isinstance(item, str) and item.startswith("<#") and item.endswith(">"):
              await ctx.respond(f"Apologies {ctx.author.mention},\nThe input must either be a direct link to an image or a member in {ctx.guild.name}.\n*Please try again.*", ephemeral=True)
              return
      
          #Next, check if the item is a string
          elif isinstance(item, str):
              parsed_url = urlparse(item)
              if parsed_url.scheme in ("http", "https"): # check if item is a valid url
                  if parsed_url.path.endswith((".jpg", ".png", ".jpeg", ".gif")): #only allow .jpg, .png, .jpeg, and .gif files

                      ### Custom image links are a PATRON FEATURE (always available in support guild)
                      # server ID for The Sweez Gang
                      support_guild_id = 1088118252200276071

                      if ctx.guild.id != support_guild_id:
                          if not patrons_db.patrons.find_one({"server_id": ctx.guild.id}):
                              patron_embed = discord.Embed(title="Patron Feature", description=f"Apologies {ctx.author.mention},\nCustom image links for my `/pictorialize` directive are an exclusive feature available solely to patrons and is not currently in use for ***{ctx.guild.name}***, good sir.\n\nPlease use my `/patron` directive to learn more information on enabling patron (premium) features for ***{ctx.guild.name}***, if you would like to take advantage of this exclusive service!", color = discord.Color.from_rgb(0, 0, 255))
                  
                              patron_embed.set_thumbnail(url=self.bot.user.avatar.url)
                  
                              await ctx.respond(embed=patron_embed, ephemeral=True)
                              return

                    
                      item_type = "picture"
                      original_file=None
                      picture_file = False
                  else:
                      await ctx.respond(f"Apologies {ctx.author.mention},\nThe image must be in *.jpg*, *.jpeg*, *.png*, or *.gif* format.\n*Please try again.*", ephemeral=True)
                      return
              else: #if not a valid url, assume the entered string is plain text
                  original_file=None
                  item_type = "text"
          else:
              try:
                  user = await self.bot.fetch_user(ctx.author.id)
                  item = user.avatar.url
                  original_file=None
                  item_type = "avatar"
                  picture_file = False
    
              except AttributeError: #avatar not defined
                  await ctx.respond(f"Apologies {ctx.author.mention},\nYou do not have an avatar defined.\n*Please try again.*", ephemeral = True)
                  return         
              except (discord.NotFound, discord.errors.HTTPException): # user not found or role used as item (i.e. not a valid snowflake ID)
                  await ctx.respond(f"Apologies {ctx.author.mention},\nThat is not a valid entry.\n*Please try again.*", ephemeral=True)
                  return


              # item = ctx.author.avatar.url
              # item_type = "avatar"
              # await ctx.respond(f"Apologies {ctx.author.mention},\nThe input must either be a direct link to an image or a user in {ctx.guild.name}.\n*Please try again.*", ephemeral=True)
              # return


    
      def get_emojified_image():
          # Ignore the UserWarning from PIL about converting to RGBA
          #pictorialize works without transparency pixels
          warnings.filterwarnings("ignore", category=UserWarning)
        
          r = requests.get(item, stream=True)
          picture = Image.open(r.raw).convert("RGB")
            
          distance_metric="euclidean"
          if size > 44:
              # Calculate the extra amount of cropping needed (reduce by a factor of 5)
              crop_size = (size - 44) * 5
            
              # Calculate the new crop boundaries
              w, h = picture.size
              left = crop_size
              top = crop_size
              right = w - crop_size
              bottom = h - crop_size
              # print(f"left: {left}, right: {right}, top: {top}, bottom: {bottom}\nwidth: {w}, height: {h}")
              # Crop the image
              try:
                  picture = picture.crop((left, top, right, bottom))
              except ValueError:
                  return [size, crop_size, distance_metric]

              # Run emojify_image again with a smaller size
              res = self.emojify_image(picture, size=44, distance_metric=distance_metric)
          else:
              try:
                  res = self.emojify_image(picture, size, distance_metric)
              except ValueError:
                  return [size, distance_metric]

          #always return in a code block (looks more accurate -- originally [if size > 14])
          if size > 1:
              res = f"```{res}```"
          return res


      #define the filters
      filter_dict = {
        "⬜ Iconify": "iconify",
        "🪞 Mirror": "mirror",
        "🔄 Flip": "flip",
        "⬛⬜ Grayscale": "grayscale",
        "🌒 Invert": "invert",
        "🎨 Colorize": "colorize",
        "👾 Pixelate": "pixelate",
        "👴 Old Timey": "Old Timey",
        "📰 Posterize": "posterize",
        "☀ Solarize": "solarize",
        "🔎 Enhance": "enhance",
        "🖼️ Thumbnail": "thumbnail"
      }

      #get the alteration effect
      alteration_effect = filter_dict[alteration]
    
      # if the item is a member/user or direct link to a picture
      if item_type == "avatar" or item_type == "picture":
          if alteration_effect == "iconify":
              await ctx.defer() #this allows enough time for the image/text to be retrieved and acknowledges that the interaction is still being run
              
              try:  
                  result = await self.bot.loop.run_in_executor(None, get_emojified_image)

                  #message to display
                  if item_type == "avatar":
                      #turn image preview on or off (add <> around link to turn preview off)
                      if display_original:
                          message = f"The following is an iconified image of **{user.display_name}**, good sir:\n> *Size: {size}*\n> *[{user.display_name} Avatar Link]({user.avatar.url})*"
                      else:
                          message = f"The following is an iconified image of **{user.display_name}**, good sir:\n> *Size: {size}*\n> *[{user.display_name} Avatar Link](<{user.avatar.url}>)*"

                
                  elif item_type == "picture":
                      if picture_file is True and display_original:
                          message = f"The following is an iconified version of this image, good sir:\n> *Size: {size}*"
                          original_file = original_file

                      elif picture_file is True and not display_original:
                          message = f"Here is your icononified image, good sir:\n> *Size: {size}*" 
                          original_file = None
                        
                      elif display_original:
                          message = f"The following is an iconified image of this link, good sir:\n> *Size: {size}*\n> *[Iconified Image Link]({item})*"
                          original_file = None
                        
                      else:
                          message = f"The following is an iconified image of this link, good sir:\n> *Size: {size}*\n> *[Iconified Image Link](<{item}>)*"
                          original_file = None
            
    
                  #check if the result is a list (i.e. returned the valueerror indicating the the image can't be zoomed in anymore) -- if size >= 44
                  if isinstance(result, list) and len(result) == 3:
                      message = await ctx.respond(f"**Size Error**\nApologies {ctx.author.mention},\nI am unable to zoom the image to *size {result[0]}*.\n\n*Please try again using a smaller size.*", ephemeral=True)
                      await asyncio.sleep(10)
                      await message.delete()                    
                      return
    
                  #if the size is <= 0
                  elif isinstance(result, list) and len(result) == 2:
                      message = await ctx.respond(f"**Size Error**\nApologies {ctx.author.mention},\nI am physically unable to produce an image of *size {result[0]}*.\n\n*Please try again using a size __greater than__ zero.*", ephemeral=True)
                      await asyncio.sleep(10)
                      await message.delete()
                      return
    
                  else:
                      await ctx.respond(message)

                      if original_file:
                          await ctx.send(file=original_file)
                    
                      await ctx.respond(result)       
    
            
              except discord.HTTPException as e:
                  if e.status == 400 and 'Must be 2000 or fewer in length' in str(e):
                      # Handle the error here
                      message = await ctx.respond(f"**Size Error**\n> *Size: {size}*\n\nGood sir, the resulting message is too large to send once it has been converted to iconography.\n*Please try again using a smaller size.*", ephemeral=True)
                      await asyncio.sleep(10)
                      await message.delete()
                  else:
                      raise e
              except Exception as e:
                  message = await ctx.respond(f"Apologies {ctx.author.mention},\n I was unable to iconify the provided image.\n*Please try again.*", ephemeral=True)
                  print(f"An iconify error occurred: {e}")
                  await asyncio.sleep(10)
                  await message.delete()
                  return
                  
                    


        
          #alter image (add selected image effect)
          else:
              await ctx.defer() #this allows enough time for the image/text to be retrieved and acknowledges that the interaction is still being run
              
              # define the filter functions
              def mirror(frame):
                  return ImageOps.mirror(frame)
              
              def flip(frame):
                  return ImageOps.flip(frame)
              
              def grayscale(frame):
                  return ImageOps.grayscale(frame)

              def invert(frame):
                  return ImageOps.invert(frame)
              
              def colorize(frame):
                  frame = frame.convert("L")
                  return ImageOps.colorize(frame, black=(255, 0, 0), white=(0, 255, 0), mid=(0, 0, 255), blackpoint=0, whitepoint=255, midpoint=127)
              
              def pixelate(frame):
                  scale_factor = 10
                  frame = frame.resize((frame.width // scale_factor, frame.height // scale_factor), resample=Image.NEAREST)
                  return frame.resize((frame.width * scale_factor, frame.height * scale_factor), resample=Image.NEAREST)
              
              def old_timey(frame):
                  frame = frame.convert("L")
                  return ImageOps.colorize(frame, black=(112, 66, 20), white=(201, 185, 155), mid=(143, 119, 74), blackpoint=0, whitepoint=255, midpoint=127)
              
              def posterize(frame):
                  return ImageOps.posterize(frame, bits=1)
              
              def solarize(frame):
                  return ImageOps.solarize(frame, threshold=128)

              def enhance(frame):
                  sharp_factor = 5.0
                  bright_factor = 1.5
                  # contrast_factor = 2.0
                  enhancer = ImageEnhance.Sharpness(frame).enhance(sharp_factor)
                  enhancer = ImageEnhance.Brightness(enhancer).enhance(bright_factor)
                  # enhancer = ImageEnhance.Contrast(enhancer).enhance(contrast_factor)
                  return enhancer

              def thumbnail(frame):
                  return ImageOps.contain(frame, (256, 256), method=Image.BICUBIC)


            
              
              #retrieve the image
              r = requests.get(item, stream=True)


              if item_type == "avatar":
                  picture = Image.open(r.raw)
                  if picture.mode == "P" and "transparency" in picture.info:
                      image = picture.convert("RGBA") #convert the image to RGBA mode (A = alpha mode -- i.e. transparent pixels)
                  else:
                      image = picture.convert("RGB")
                    
                  image_type = "avatar"
              elif parsed_url.path.endswith((".jpg", ".png", ".jpeg")): #only .jpg, .png, and .jpeg or avatar files
                  picture = Image.open(r.raw)
                  if picture.mode == "P" and "transparency" in picture.info:
                      image = picture.convert("RGBA") #convert the image to RGBA mode (A = alpha mode -- i.e. transparent pixels)
                  else:
                      image = picture.convert("RGB")
                    
                  image_type = "picture"
              elif parsed_url.path.endswith((".gif")): #only .gif files
                  image = Image.open(r.raw)
                  image_type = "video"

            
              
              # apply the specified filter to the image
              if alteration_effect == 'mirror':
                  filter_fn = mirror
              elif alteration_effect == 'flip':
                  filter_fn = flip
              elif alteration_effect == 'grayscale':
                  filter_fn = grayscale
              elif alteration_effect == 'invert':
                  filter_fn = invert
              elif alteration_effect == 'colorize':
                  filter_fn = colorize
              elif alteration_effect == 'pixelate':
                  filter_fn = pixelate
              elif alteration_effect == 'Old Timey':
                  filter_fn = old_timey
              elif alteration_effect == 'posterize':
                  filter_fn = posterize
              elif alteration_effect == 'solarize':
                  filter_fn = solarize
              elif alteration_effect == 'enhance':
                  filter_fn = enhance
              elif alteration_effect == 'thumbnail':
                  filter_fn = thumbnail   
            


              if image_type == "video":
                  try:
                      # Apply the filter to the frames of the GIF
                      frames = ImageSequence.all_frames(image, func=filter_fn)                            
                    
                      # Save the modified frames to a file object
                      with io.BytesIO() as output:
                          frames[0].save(
                              output,
                              format='GIF',
                              save_all=True,
                              append_images=frames[1:],
                              duration=image.info['duration'],
                              loop=image.info['loop']
                          )
                          gif_data = output.getvalue()
                      
                      # Create a Discord file object from the modified GIF data
                      file = discord.File(io.BytesIO(gif_data), filename='modified.gif')

                  #if the filter cannot be used on gifs, use the first frame only
                  except NotImplementedError:
                      # Convert the GIF to PNG
                      image = image.convert('RGBA')
                      with io.BytesIO() as output:
                          image.save(output, 'PNG')
                          png_data = output.getvalue()
              
                      # Apply the filter to the PNG data
                      with io.BytesIO(png_data) as input:
                          png_image = Image.open(input)
                          png_image = filter_fn(png_image)
              
                          # Save the modified PNG to a file object
                          with io.BytesIO() as output:
                              png_image.save(output, 'PNG')
                              png_data = output.getvalue()
              
                          # Create a Discord file object from the modified PNG data
                          file = discord.File(io.BytesIO(png_data), filename='modified.png')                     
                  
                  except ValueError:
                      message = await ctx.respond(f"Apologies {ctx.author.mention}\nI was unable to alter the item you specified.\n*Please try again.*", ephemeral=True)
                      await asyncio.sleep(5)
                      await message.delete()
                      return

                  
                  except Exception as e:
                      message = await ctx.respond(f"Apologies {ctx.author.mention}\nI was unable to locate and convert the item you specified.\n*Please try again.*", ephemeral=True)
                      print(f"An error occurred: {e}")
                      await asyncio.sleep(10)
                      await message.delete()
                      # raise e
                      return


              #regular image
              elif image_type == "picture" or image_type == "avatar":
                  try:
                      image = filter_fn(image)
                    
                      # Save the modified image to a buffer
                      with io.BytesIO() as image_buffer:
                          image.save(image_buffer, format='PNG')
                          image_data = image_buffer.getvalue()
                    
                      # Create a Discord file object from the modified image data
                      file = discord.File(io.BytesIO(image_data), filename='image.png')
                  except Exception as e:
                      message = await ctx.respond(f"Apologies {ctx.author.mention}\nI was unable to locate and convert the item you specified.\n*Please try again.*", ephemeral=True)
                      print(f"An error occurred: {e}")
                      await asyncio.sleep(10)
                      await message.delete()
                      return
            

                
              #message to display
              if item_type == "avatar":
                  #turn image preview on or off (add <> around link to turn preview off)
                  if display_original:
                      message = f"The following is an altered version of the avatar for **{user.display_name}**, good sir:\n> *Alteration: {alteration}*\n> *[{user.display_name} Original Avatar]({user.avatar.url})*"
                  else:
                      message = f"The following is an altered version of the avatar for **{user.display_name}**, good sir:\n> *Alteration: {alteration}*\n> *[{user.display_name} Original Avatar](<{user.avatar.url}>)*"

              elif item_type == "picture":
                  if picture_file is True and display_original: #if it is a picture file
                      message = f"The following is an altered version of this image, good sir:\n> *Alteration: {alteration}*"
                      original_file = original_file

                  elif picture_file is True and not display_original: #if it is a picture file
                      message = f"Here is your altered image, good sir:\n> *Alteration: {alteration}*"
                      original_file = None
                
                  elif display_original: #if it's only a web link
                      message = f"The following is an altered version of this link, good sir:\n> *Alteration: {alteration}*\n> *[Original Image]({item})*"
                      original_file = None

                  else:
                      message = f"The following is an altered version of this link, good sir:\n> *Alteration: {alteration}*\n> *[Original Image](<{item}>)*"
                      original_file = None
            
              # Send the modified image as a file attachment
              await ctx.respond(message)
            
              if original_file:
                  await ctx.send(file=original_file)
                
              await ctx.send(file=file)

    
      else: #otherwise, convert the plain text to emojis
          await ctx.defer() #this allows enough time for the image/text to be retrieved and acknowledges that the interaction is still being run
          
          punctuations = {
              '!': ':exclamation:',
              '?': ':question:',
              '.': ':record_button:',
              '+': ':heavy_plus_sign:',
              '-': ':heavy_minus_sign:',
              '$': ':heavy_dollar_sign:',
              '*': ':asterisk:',
              '#': ':hash:',
              '<': ':arrow_backward:',
              '>': ':arrow_forward:'
          }


          #convert the letters to lowercase so users that input eithe upper or lowercase
          emotions = {
              ':)': ':slight_smile:',
              ':(': ':slightly_frowning_face:',
              ':d': ':grinning:',
              ':o': ':open_mouth:', #can use o or 0 for open mount emoji
              ':0': ':open_mouth:',
              ':p': ':stuck_out_tongue:',
              ':|': ':neutral_face:',
              ':/': ':confused:',
              ':s': ':confounded:',
              ':*': ':kissing_heart:',
              ';)': ':wink:'
          }
          
          text = item.lower()
          emojis = []
          while len(text) > 0:
              # check for emotion faces
              found_emotion = False
              for emoticon, emoji in emotions.items():
                  if text.startswith(emoticon):
                      emojis.append(emoji)
                      text = text[len(emoticon):]
                      found_emotion = True
                      break
              if found_emotion:
                  continue
          
              # process the next character
              s = text[0]
              if s.isdecimal():
                  num2emo = {
                      '0': 'zero',
                      '1': 'one',
                      '2': 'two',
                      '3': 'three',
                      '4': 'four',
                      '5': 'five',
                      '6': 'six',
                      '7': 'seven',
                      '8': 'eight',
                      '9': 'nine'
                  }
                  emojis.append(f':{num2emo.get(s)}:')
              elif s.isalpha():
                  emojis.append(f':regional_indicator_{s}:')
              elif s in punctuations:
                  emojis.append(punctuations[s])
              else:
                  emojis.append(s)
              text = text[1:]
          
          await ctx.respond(''.join(emojis))


  

  
  # color dictionary (base color, 2 lighter shades, 2 darker shades, and one medium shade)
  # use this link to check colors(https://www.google.com/search?q=color+picker&rlz=1C1UEAD_enUS1029US1029&oq=&aqs=chrome.0.69i59j69i57j69i59j46i433i512j0i131i433i512j0i433i512l2j0i512j0i433i512j0i131i433i650.1038j0j7&sourceid=chrome&ie=UTF-8)
  COLORS = {
    (0, 0, 0): "⬛", #black
    (7, 7, 48): "⬛", #blue/black 1 (right)
    (17, 17, 41): "⬛", #blue/black 2 (middle)
    (22, 22, 23): "⬛", #blue/black 3 (left)
    (43, 6, 6): "⬛", #red/black 1
    (43, 19, 19): "⬛", #red/black 2
    (20, 19, 19): "⬛", #red/black 3
    (33, 33, 3): "⬛", #yellow/black 1
    (36, 36, 15): "⬛", #yellow/black 2
    (23, 23, 21): "⬛", #yellow/black 3
    (26, 14, 2): "⬛", #orange/brown/black 1
    (31, 22, 13): "⬛", #orange/brown/black 2
    (28, 27, 26): "⬛", #orange/brown/black 3
    (3, 28, 3): "⬛", #green/black 1
    (15, 33, 15): "⬛", #green/black 2
    (24, 26, 24): "⬛", #green/black 3
    (23, 4, 36): "⬛", #purple/black 1
    (30, 18, 38): "⬛", #purple/black 2
    (27, 26, 28): "⬛", #purple/black 3
    (255, 255, 255): "⬜", #white
    (169, 169, 196): "⬜", #blue/white
    (204, 177, 177): "⬜", #red/white
    (204, 204, 177): "⬜", #yellow/white
    (204, 192, 180): "⬜", #orange/white
    (177, 201, 177): "⬜", #green/white
    (186, 169, 196): "⬜", #purple/white
    (61, 61, 71): "🔳", #dark blue/grey
    (61, 53, 53): "🔳", #dark red/grey
    (84, 84, 71): "🔳", #dark yellow/grey
    (87, 81, 73): "🔳", #dark orange/brown/grey
    (57, 64, 57): "🔳", #dark green/grey
    (68, 62, 74): "🔳", #dark purple/grey
    (118, 118, 135): "🔲", #blue/grey
    (161, 137, 137): "🔲", #red/grey
    (166, 166, 141): "🔲", #yellow/grey
    (179, 170, 155): "🔲", #orange/brown/grey
    (145, 171, 145): "🔲", #green/grey
    (165, 156, 181): "🔲", #purple/grey
    (0, 0, 255): "🟦", #blue
    (53, 53, 232): "🟦", #lighter blue
    (111, 111, 232): "🟦", #even lighter blue
    (13, 13, 181): "🟦", #darker blue
    (16, 16, 130): "🟦", #even darker blue
    (43, 43, 161): "🟦", #medium blue
    (90, 90, 143): "🟦",
    (255, 0, 0): "🟥",
    (224, 49, 49): "🟥",
    (224, 90, 90): "🟥",
    (173, 14, 14): "🟥",
    (130, 14, 14): "🟥",
    (166, 51, 51): "🟥",
    (255, 255, 0): "🟨",
    (230, 230, 55): "🟨",
    (222, 222, 91): "🟨",
    (224, 224, 16): "🟨",
    (194, 194, 12): "🟨",
    (196, 183, 33): "🟨",
    (158, 149, 46): "🟨",
    (255, 132, 0): "🟧",
    (230, 148, 48): "🟧",
    (224, 166, 81): "🟧",
    (201, 125, 14): "🟧",
    (168, 107, 20): "🟧",
    (196, 128, 31): "🟧",
    (161, 117, 55): "🟧",
    (0, 255, 0): "🟩",
    (52, 217, 52): "🟩",
    (95, 222, 95): "🟩",
    (14, 153, 14): "🟩",
    (15, 99, 15): "🟩",
    (81, 143, 93): "🟩",
    (67, 94, 72): "🟩",
    (153, 0, 255): "🟪",
    (137, 56, 217): "🟪",
    (160, 98, 222): "🟪",
    (110, 17, 171): "🟪",
    (80, 15, 122): "🟪",
    (114, 74, 138): "🟪"
  }



  def find_closest_emoji(self, color, distance_metric):
      c = sorted(list(self.COLORS), key=lambda k: self.euclidean_distance(color, k))
      return self.COLORS[c[0]]
  
  def euclidean_distance(self, c1, c2):
      r1, g1, b1 = c1
      r2, g2, b2 = c2
      d = ((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2) ** 0.5
      return d
  
  
  def emojify_image(self, img, size, distance_metric):
      WIDTH, HEIGHT = (size, size)
      small_img = img.resize((WIDTH, HEIGHT), Image.NEAREST)
  
      emoji = ""
      small_img = small_img.load()
      for y in range(HEIGHT):
          for x in range(WIDTH):
              emoji += self.find_closest_emoji(small_img[x, y], distance_metric=distance_metric)
          emoji += "\n"
      return emoji

################################PICTORIALIZE#########################################


  
  
  
############################ GREET #################################
  
  @discord.slash_command(
      name="greet",
      description="Greet the automaton.",
      # guild_ids=SERVER_ID
      global_command = True
  )
  async def greet(self, ctx):
    #reponse list for when anybody uses the GREET (!greet) command
    quotes_hello = [
      "Good day, sir/madam! How may I assist you?",
      "Greetings, fair lady/gentleman! How may I be of service?",
      "A most delightful day to you, sir/madam! How may I assist you?",
      "Welcome, dear guest! How may I be of assistance?",
    ]
    
    quote = random.choice(quotes_hello)
    await ctx.respond(quote)

############################ GREET #################################




  

############################### THOUGHT ############################
  
  class ThoughtView(discord.ui.View):
      def __init__(self, ctx, byname):
          super().__init__(timeout=120) #set the timeout
          self.ctx = ctx #initialize the context
          self.byname = byname


      async def on_timeout(self):
          self.disable_all_items()
        
          try:
              await self.message.edit(view=None)
          except discord.errors.NotFound: #if message deleted before timeout
              pass

          self.stop()

    
      @discord.ui.select( # the decorator that lets you specify the properties of the select menu
          placeholder = "Select a thought.", # the placeholder text that will be displayed if nothing is selected
          min_values = 1, # the minimum number of values that must be selected by the users
          max_values = 1, # the maximum number of values that can be selected by the users
          options = [ # the list of options from which users can choose, a required field
              discord.SelectOption(
                  emoji='🧑‍🦳',
                  label="Father Humor",
                  description="Hear a humorous, paternal anecdote."
              ),
              discord.SelectOption(
                  emoji='🤔',
                  label="Deep Thought",
                  description="Reveal a deep thought..."
              ),
              discord.SelectOption(
                  emoji='❗',
                  label="Random Fact",
                  description="Receive a random useless fact."
              ),
              discord.SelectOption(
                  emoji='💻',
                  label="Technological",
                  description="Get help sounding more technologically savvy."
              )              
          ]
      )
      async def select_callback(self, select, interaction):
          if interaction.user.id != self.ctx.author.id:
              return
  
          await interaction.response.defer()

          selected_option = next(option for option in select.options if option.value == select.values[0])
          emoji = selected_option.emoji #get the emoji
        
  
        
          if select.values[0] == "Father Humor":
              url = "https://icanhazdadjoke.com/"
              headers = {
                  "Accept": "application/json"
              }
              response = requests.get(url, headers=headers)
              dadjoke_data = response.json()
              
              dadjoke = dadjoke_data["joke"]
    
              dad_embed = discord.Embed(title=f"{self.byname} Thoughts", description=f"{interaction.user.mention}\nHere is a joke I have been wanting to tell you.", color=discord.Color.from_rgb(0, 0, 255))
  
              dad_embed.add_field(name=f"{emoji} {select.values[0]}", value=f"*{dadjoke}*")
    
              dad_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)

              dad_embed.set_footer(text="Powered by icanhazdadjoke (https://icanhazdadjoke.com/)")
            
              await self.message.edit(embed=dad_embed, view=self)
            
          elif select.values[0] == "Deep Thought":
              # Open the file containing the deep thoughts
              with open("text_files/showerthoughts.txt", "r") as f:
                  shower_thoughts_full = f.read().splitlines()
              
              # Select a random shower thought from the list
              deep_thought = random.choice(shower_thoughts_full)
  
              deep_embed = discord.Embed(title=f"{self.byname} Thoughts", description=f"Ahem, {interaction.user.mention},\nIf I may be so bold as to offer a profound thought...", color=discord.Color.from_rgb(0, 0, 255))
  
              deep_embed.add_field(name=f"{emoji} {select.values[0]}", value=f"*{deep_thought}*")
    
              deep_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)
            
              await self.message.edit(embed=deep_embed, view=self)
  
  
          elif select.values[0] == "Random Fact":
              url = "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en"
              response = requests.get(url)
              fact_data = response.json()
  
              fact = fact_data["text"] #random fact
              source = fact_data["source"] #the source for the fact
              source_url = fact_data["source_url"] #the source url for the fact
  
              fact_embed = discord.Embed(title=f"{self.byname} Thoughts", description=f"{interaction.user.mention}\nHere is a useless random fact for you, good sir.", color=discord.Color.from_rgb(0, 0, 255))
  
              fact_embed.add_field(name=f"{emoji} {select.values[0]}", value=f"*{fact}*")
  
              fact_embed.add_field(name="Source", value=f"[{source}]({source_url})", inline=False)
    
              fact_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)
  
              fact_embed.set_footer(text="Powered by UselessFacts (https://uselessfacts.jsph.pl/)")
            
              await self.message.edit(embed=fact_embed, view=self)


          elif select.values[0] == "Technological":
              url = "https://techy-api.vercel.app/api/json"
              response = requests.get(url)
              tech_data = response.json()
  
              tech_phrase = tech_data["message"]
  
              tech_embed = discord.Embed(title=f"{self.byname} Thoughts", description=f"{interaction.user.mention}\nIn order to sound more technologically savvy, simply say the following phrase, good sir.", color=discord.Color.from_rgb(0, 0, 255))
  
              tech_embed.add_field(name=f"{emoji} {select.values[0]}", value=f"*{tech_phrase}.*")
    
              tech_embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)
  
              tech_embed.set_footer(text="Powered by Techy (https://techy-api.vercel.app/)")
            
              await self.message.edit(embed=tech_embed, view=self)



  @discord.slash_command(
      name="thought",
      description="Allow the automaton to enlighten you with its vast knowledge.",
      # guild_ids=SERVER_ID
      global_command = True
  )
  async def thought(self, ctx):
      byname = await self.get_byname(ctx.guild.id)
    
      thought_embed = discord.Embed(title=f"{byname} Thoughts", description=f"{ctx.author.mention}\nKindly select a genre of thought, good sir.", color=discord.Color.from_rgb(0, 0, 255))

      thought_embed.set_thumbnail(url=self.bot.user.avatar.url)
    
      await ctx.respond(embed=thought_embed, view=self.ThoughtView(ctx, byname))

############################### THOUGHT ############################



  

########################## COMPLIMENT ###############################
  @discord.slash_command(
      name="compliment",
      description="Allow the automaton to extend a sincere compliment to you or a fellow member.",
      # guild_ids=SERVER_ID
      global_command = True
  )
  async def compliment(self, ctx, user: Option(discord.Member, name="user", description="Choose a member to compliment. (Default: Self)", required=False)):
      # Read the prefixes, adjectives, and nouns from a text file
      with open("text_files/compliments.txt", "r") as f:
          lines = f.readlines()
          prefix_lines = [line.strip() for line in lines if line.startswith("Prefix")]
          adj_line = [line.strip() for line in lines if line.startswith("Adjective")][0]
          noun_line = [line.strip() for line in lines if line.startswith("Noun")][0]
          
          prefixes = [line[7:] for line in prefix_lines]
          adjectives = adj_line.split()[1].split(",")
          nouns = noun_line.split()[1].split(",")
          
      # Generate a random compliment
      if user:
          prefix = random.choice(prefixes)
          adjective = random.choice(adjectives)
          noun = random.choice(nouns)
          if "you are" in prefix.lower() or "one" in prefix.lower():
              article = ""
          else:
              article = "an" if adjective[0].lower() in "aeiou" else "a"
          compliment = f"{user.mention}, {prefix} {article} {adjective} {noun}!"
      else:
          prefix = random.choice(prefixes)
          adjective = random.choice(adjectives)
          noun = random.choice(nouns)
          if "you are" in prefix.lower() or "one" in prefix.lower():
              article = ""
          else:
              article = "an" if adjective[0].lower() in "aeiou" else "a"
          compliment = f"{ctx.author.mention}, {prefix} {article} {adjective} {noun}!"
      
      # Send the compliment
      await ctx.respond(compliment)
    
########################## COMPLIMENT ###############################


  

########################### TEATIME ##################################
  @discord.slash_command(
      name="teatime",
      description="Request a virtual tea service from the automaton.",
      # guild_ids=SERVER_ID
      global_command = True
  )
  async def tea_service(self, ctx):
      #get the bot's nickname from mongoDB
      byname = await self.get_byname(ctx.guild.id)
    
      # Respond with the tea service message and GIF
      teatime_gifdir = glob.glob('pics/teatime/*.gif')
      teatime_gifs = random.choice(teatime_gifdir)
      await ctx.respond(f"Very good, {ctx.author.mention}. I shall prepare your tea immediately.", file=discord.File(teatime_gifs))

      # Wait for a short delay to simulate the preparation of tea (random number of seconds between 180 and 600)
      await asyncio.sleep(random.randint(180, 300))

      # Respond with the tea cup and saucer message and GIF
      teaready_gifdir = glob.glob('pics/teaready/*.gif')
      teaready_gifs = random.choice(teaready_gifdir)
      await ctx.respond(f"Dearest {ctx.author.mention},\n\nApologies for the wait but *your tea is ready*.\n*I allowed the leaves to steep for a duration of **three to five minutes**, as haste is not a companion of great taste.\nIt is imperative that the tea is allowed the full time to release its entire flavor.*\n\nPlease enjoy,\n**{byname}**", file=discord.File(teaready_gifs))


########################### TEATIME ##################################




def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Fun(bot)) # add the cog to the bot
