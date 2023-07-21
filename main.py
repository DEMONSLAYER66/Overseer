import os #used for loading secrets (tokens, codes, passwords, etc.)
import discord #needed to interact with discord API
import random #used for choosing random selections from lists
from discord.ext import tasks #used to start various loop tasks
from discord.ext import commands #used for slash commands
import pymongo #used for database management
from dotenv import load_dotenv


#This checks if the person running the code has a token for discord API or not
try:
    # Load environment variables from .env
    load_dotenv()
  
    #Important variables (tokens, codes, passwords, files, etc.)
    token = os.getenv('token')
except:
    print("Apologies good sir, but it appears that you require a Discord API key to access my features.\n\nPlease visit the following link to learn how to do such things:\n\nhttps://discord.com/developers/docs/getting-started")
    exit()
    

#set up the bot's prefix command and intents
bot = commands.Bot(intents=discord.Intents.all())
bot.remove_command('help')


#ON READY EVENT LISTENER
@bot.event
async def on_ready():
  #begin changing Lord Bottington's activities
  if not change_activity.is_running():
      change_activity.start()

  #let user of bot know that bot is ready in Console
  print(f"Be advised, {bot.user.name} hath loaded with a ping of {int(bot.latency*100)}, good sirs.")
  print(f"{bot.user.name} is ready to do thy bidding...")
  print("--------------------")


  #initialize the mongoDB database and get the server IDs for the autopurge command to initiate
  # mongoDBpass = os.environ['mongoDBpass'] #load the mongoDB url (retreived from mongoDB upon account creation)
  mongoDBpass = os.getenv('mongoDBpass')
  client = pymongo.MongoClient(mongoDBpass) # Create a new client and connect to the server
  autopurge_db = client.autopurge_db #create the autpourge database on mongoDB
  bump_db = client.bump_db #create the bump (promotion) database on MongoDB

      current_time = datetime.datetime.utcnow()

      # Get all cooldown entries from the database (for cooldowns on promotions)
      cooldown_data_list = bump_db.cooldowns.find()

      if cooldown_data_list:
          for cooldown_data in cooldown_data_list:
              cooldown_time = cooldown_data['cooldown']

              # Update the 'send_time' field in the MongoDB collection
              bump_db.cooldowns.update_one(
                  {'_id': cooldown_data['_id']},  # Use the _id field to identify the document
                  {'$set': {'send_time': current_time}}
              )
              
              utility_cog = bot.get_cog('Utility') #get the utility cog
              utility_cog.send_reminder(cooldown_time)



    

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
              bot.loop.create_task(configuration_cog.autopurge_task(server_id, purge_channel_id))



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


################## CHANGE BOT ACTIVITIES ON DISCORD ################
# Change bots custom status every 10 minutes
@tasks.loop(minutes=10)
async def change_activity():
  with open("text_files/activities.txt", "r") as f:
      activities_full = f.read().splitlines()
    
  activity = random.choice(activities_full)
  current_activity = discord.Activity(type=discord.ActivityType.watching,
                   name = activity)
  await bot.change_presence(activity=current_activity)
################## CHANGE BOT ACTIVITIES ON DISCORD ################


# run the bot using the discord API key
try:
    bot.run(token)
except TypeError:
    print("Apologies good sir, but it appears that you require a Discord API key to access my features.\n\nPlease visit the following link to learn how to do such things:\n\nhttps://discord.com/developers/docs/getting-started")
    exit()
