import os #used for loading secrets (tokens, codes, passwords, etc.)
import discord
import random
from discord.ext import tasks

import pymongo

from discord.ext import commands #used for slash commands
# from discord.commands import Option #add options to slash commands

#This checks if the person running the code has a token for discord API or not
try:
    #Important variables (tokens, codes, passwords, files, etc.)
    token = os.environ['token']
except KeyError:
    print("Apologies good sir, but it appears that you require a Discord API key to access my features.\n\nPlease visit the following link to learn how to do such things:\n\nhttps://discord.com/developers/docs/getting-started")
    exit()
    

#set up the bot's prefix command and intents
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.remove_command('help')




#ON READY EVENT LISTENER
@bot.event
async def on_ready():
  #begin changing Lord Bottington's activities
  change_activity.start()

  #let user of bot know that bot is ready in Console
  print(f"Be advised, {bot.user.name} hath loaded with a ping of {int(bot.latency*100)}, good sirs.")
  print(f"{bot.user.name} is ready to do thy bidding...")
  print("--------------------")


  #initialize the mongoDB database and get the server IDs for the autopurge command to initiate
  mongoDBpass = os.environ['mongoDBpass'] #load the mongoDB url (retreived from mongoDB upon account creation)
  client = pymongo.MongoClient(mongoDBpass) # Create a new client and connect to the server
  autopurge_db = client.autopurge_db #create the autpourge database on mongoDB
  # server_id_db = client.server_id_db #create the server ID database on MongoDB (this shows a list of all of the active servers the bot is a part of)
  
  
  # SERVER_ID = []
  # server_ids = server_id_db.server_ids.find_one()["server_ids"] #find the current server list
  # SERVER_ID = server_ids #save the server_ids as SERVER_ID (array)

  server_ids = []
  for guild in bot.guilds:
      server_ids.append(guild.id)

  #start the autopurge task
  configuration_cog = bot.get_cog('Configuration') #get the configuration cog
  for server_id in server_ids: #for every active server, create a loop task for autopurge
      # Retrieve autopurge configurations from database
      autopurge_config = autopurge_db[f"autopurge_config_{server_id}"].find()
      if autopurge_config:
          for config in autopurge_config:
              purge_channel_id = config["purge_channel_id"]

              #create the autopurge task loop
              await bot.loop.create_task(configuration_cog.autopurge_task(server_id, purge_channel_id))



#get list of cogs
cogfiles = [
  f"cogs.{filename[:-3]}" for filename in os.listdir("./cogs/") if filename.endswith(".py")
]

#load all cogs
for cogfile in cogfiles:
  try:
    bot.load_extension(cogfile)
  except Exception as err:
    print(err)


##Change Lord Bottington's activities##
# Change bots custom status every 10 minutes
@tasks.loop(minutes=10)
async def change_activity():
  with open("text_files/activities.txt", "r") as f:
      activities_full = f.read().splitlines()
    
  activity = random.choice(activities_full)
  current_activity = discord.Activity(type=discord.ActivityType.watching,
                   name = activity)
  await bot.change_presence(activity=current_activity)
##END Change Lord Bottington's activities##



token = os.environ['token']
bot.run(token)