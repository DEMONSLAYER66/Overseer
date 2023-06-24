import discord #needed to interact with discord API
import random #used to select random selections from a list
import asyncio #used to wait a specified amount of time
from discord.ext import commands #used for slash commands
from discord.commands import Option #add options to slash commands

import os #used for 
import pymongo #used for mongoDB database

#########################MONGODB DATABASE##################################
mongoDBpass = os.environ['mongoDBpass'] #load the mongoDB url (retreived from mongoDB upon account creation)
client = pymongo.MongoClient(mongoDBpass) # Create a new client and connect to the server
games_db = client.games_db #Create the games database on mongoDB
wallets_db = client.wallets_db #Create the wallets database on mongoDB
#########################MONGODB DATABASE##################################


#this is an array of the server IDs where command testing is done
SERVER_ID = [1088118252200276071, 1117859916749742140]


class Games(commands.Cog):
    # this is a special method that is called when the cog is loaded
    def __init__(self, bot): #initialize this cog
      self.bot: commands.Bot = bot #intialize the bot with the commands for this cog


    #This retrieves the current server's bot nickname from the mongoDB database
    async def get_byname(self, guild_id):
        mongoDBpass = os.environ['mongoDBpass']
        client = pymongo.MongoClient(mongoDBpass)
        byname_db = client.byname_db
  
        byname_key = {"server_id": guild_id}
        byname_data = byname_db.bynames.find_one(byname_key)
        if byname_data:
            return byname_data["byname"] #return the bot's nickname for the specified server
        else:
            return "Lord Bottington" #return Lord Bottington as the bot's nickname if none set



  

###############################PLAYERINFO#######################################
    @discord.slash_command(
        name="playerinfo",
        description="Check game related information for a member within the guild.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def playerinfo(self, ctx, member: Option(discord.Member, name="member", description="Member to find game information for within the guild. (Default: Self)", required=False, default=None)):

        if not member:
            member = ctx.author

        #cannot look up earnings info on other members unless admin
        if member.id != ctx.author.id and not ctx.author.guild_permissions.administrator:
            await ctx.respond(f"Apologies {ctx.author.mention},\nOnly those with administrative privileges within {ctx.guild.name} may view game information for other members of the guild.\n*Please try again.*", ephemeral=True)
            return

        games = games_db[f"winnings_{ctx.guild.id}"] #the database to look in
        games_key = {"player_id": member.id} #search parameter

        games_data = games.find_one(games_key)

        if games_data:
            game_names = games_data["games"]
            game_wins = list(map(int, games_data["wins"]))

            # Find the maximum value and its index
            max_value = max(game_wins)
            max_index = game_wins.index(max_value)

            favorite_game = game_names[max_index]

            wins = games_data["wins"]
            earnings = games_data["shillings"]
        else:
            favorite_game = None
            wins = [0 for _ in range(6)] #6 total games, but no data found, so 0 wins for them all
            earnings = [0 for _ in range(6)]

      
        game_dict = {
          "battleship": "🚤 Battleship 💥",
          "connectfour": "🔴 Connect Four 🟡",
          "mastermind": "🌈 Mastermind",
          "rps": "🪨 Rock, 📄 Paper, ✂ Scissors",
          "tictactoe": "❌ Tic-Tac-Toe ⭕",
          "wumpus": "👹 Hunt the Wumpus"
        }

      
        #if a favorite game is found, convert the name of the game to a string with emojis
        if favorite_game:
            fav_game = game_dict[favorite_game]


        #change description for embed based on who the searched member is
        if member.id == ctx.author.id:
            description = f"{ctx.author.mention}\nThe following is information regarding your game playing within the guild."
        else:
            description = f"{ctx.author.mention}\nThe following is information regarding game playing within the guild for ***{member.display_name}***."

        #create the embed
        earnings_embed = discord.Embed(title=f"{ctx.guild.name}\nPlayer Information", description=description, color=discord.Color.from_rgb(0, 0, 255))


        #add favorite game field (if found)
        if favorite_game:
            earnings_embed.add_field(name="Favorite Game", value=f"`{fav_game}`", inline=False)
        else:
            earnings_embed.add_field(name="Favorite Game", value=f"`Not Applicable`", inline=False)

  
      
        #add the winnings and earnings for each game
        for i, item in enumerate(game_names):
            game_name = game_dict[item] #change the game name to a string with emojis from game_dict
            win = wins[i]
            earning = earnings[i]

            earnings_embed.add_field(name=f"`{game_name}`", value=f"Wins: `🏆 {win:,}`\nTotal Earnings: `🪙 {earning:,}`", inline=False)
      

        #set thumbnail to avatar url (unless they dont have one, then do not set a thumbnail)
        try:
            earnings_embed.set_thumbnail(url=member.avatar.url)
        except:
            pass

        await ctx.respond(embed=earnings_embed)



###############################PLAYERINFO#######################################

  

  

  
#################################LEADERBOARD################################
    @discord.slash_command(
        name="toptalent",
        description="Receive information on the top talent for games played within the guild.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def toptalent(self, ctx, game: Option(str, name = "game", description="Game to see the top talent for within the guild.", choices=["🪨 Rock, 📄 Paper, ✂ Scissors", "❌ Tic-Tac-Toe ⭕", "🔴 Connect Four 🟡", "👹 Hunt the Wumpus", "🌈 Mastermind", "🚤 Battleship 💥"])):

        game_dict = {
          "🪨 Rock, 📄 Paper, ✂ Scissors": "rps",
          "❌ Tic-Tac-Toe ⭕": "tictactoe",
          "🔴 Connect Four 🟡": "connectfour",
          "👹 Hunt the Wumpus": "wumpus",
          "🌈 Mastermind": "mastermind",
          "🚤 Battleship 💥": "battleship"
        }

        game_GIF_dict = {
          "🪨 Rock, 📄 Paper, ✂ Scissors": "https://i.imgur.com/ExzGCb4.gif",
          "❌ Tic-Tac-Toe ⭕": "https://i.imgur.com/G34stnX.gif",
          "🔴 Connect Four 🟡": "https://i.imgur.com/qChYW1N.gif",
          "👹 Hunt the Wumpus": "https://i.imgur.com/0DdDso7.png",
          "🌈 Mastermind": "https://i.imgur.com/Ce6Y2Ee.gif",
          "🚤 Battleship 💥": "https://i.imgur.com/WVTMctu.gif"
        }


        # Retrieve all player records
        guild_wins = games_db[f"winnings_{ctx.guild.id}"]
        win_records = guild_wins.find()
        earn_records = guild_wins.find()

        games = ["🚤 Battleship 💥", "🔴 Connect Four 🟡", "🌈 Mastermind", "🪨 Rock, 📄 Paper, ✂ Scissors", "❌ Tic-Tac-Toe ⭕", "👹 Hunt the Wumpus"]

        i = 0
        for game_name in games:
            if game == game_name:
                game_index = i
                break

            i = i + 1


        # Filter players with non-zero wins
        filtered_winners = [p for p in win_records if p["wins"][game_index] > 0]
        
        # Sort the filtered player records based on the number of wins in descending order
        sorted_winners = sorted(filtered_winners, key=lambda x: x["wins"][game_index], reverse=True)
        
        # Filter players with non-zero shillings
        filtered_earners = [p for p in earn_records if p["shillings"][game_index] > 0]
        
        # Sort the filtered player records based on the number of shillings in descending order
        sorted_earners = sorted(filtered_earners, key=lambda x: x["shillings"][game_index], reverse=True)

        # Select the top 10 players with the highest number of wins
        top_10_winners = sorted_winners[:10]

        # Select the top 10 players with the highest number of shillings
        top_10_earners = sorted_earners[:10]

      
        medal_emojis = ["🥇", "🥈", "🥉"]
      
        # Win leaders
        win_leaders = []
        for i, winner in enumerate(top_10_winners):
            winner_name = winner["player_name"]
            wins = winner["wins"][game_index]
            medal = medal_emojis[i] if i < 3 else "🔷"
            win_str = f"{medal} {winner_name} `{wins:,}`"
            win_leaders.append(win_str)

        top_winners = '\n'.join(f"> {line}" for line in win_leaders) + '\n'


        # Earning leaders
        earn_leaders = []
        for i, earner in enumerate(top_10_earners):
            earner_name = earner["player_name"]
            shillings = earner["shillings"][game_index]
            medal = medal_emojis[i] if i < 3 else "🔷"
            earn_str = f"{medal} {earner_name} `{shillings:,}`"
            earn_leaders.append(earn_str)

        top_earners = '\n'.join(f"> {line}" for line in earn_leaders) + '\n'

      
      
        leaderboard_embed = discord.Embed(title=f"{ctx.guild.name}\nTop Talent", description = f"`{game}`", color = discord.Color.from_rgb(0, 0, 255))

              
        leaderboard_embed.add_field(name="🏆 Top Wins", value=top_winners)
        leaderboard_embed.add_field(name="🪙 Top Earnings", value=top_earners)

        leaderboard_embed.set_thumbnail(url=game_GIF_dict[game])
      
        await ctx.respond(embed=leaderboard_embed, view=self.TopTalentView(ctx, game_dict, game_GIF_dict))


  

    ## Select menu for leaderboards
    class TopTalentView(discord.ui.View):
        def __init__(self, ctx, game_dict, game_GIF_dict):
            super().__init__(timeout=120) #set the timeout
            self.ctx = ctx #intialize the context
            self.game_dict = game_dict
            self.game_GIF_dict = game_GIF_dict

        # Handle timeout (e.g., if no selections are made within the specified timeout)
        async def on_timeout(self):
            self.disable_all_items()

            try:
                await self.message.edit(view=None)
            except discord.errors.NotFound: #if message is deleted before the timeout
                pass

            self.stop()

      
        @discord.ui.select(
          placeholder="🏆🪙Choose a game.", 
          min_values=1, 
          max_values=1,
          options = [
            discord.SelectOption(label="🪨 Rock, 📄 Paper, ✂ Scissors"),
            discord.SelectOption(label="❌ Tic-Tac-Toe ⭕"),
            discord.SelectOption(label="🔴 Connect Four 🟡"),
            discord.SelectOption(label="👹 Hunt the Wumpus"),
            discord.SelectOption(label="🌈 Mastermind"),
            discord.SelectOption(label="🚤 Battleship 💥")
          ]
        )
        async def select_callback(self, select, interaction):
            await interaction.response.defer()

            game = select.values[0]
    
            # Retrieve all player records
            guild_wins = games_db[f"winnings_{self.ctx.guild.id}"]
            win_records = guild_wins.find()
            earn_records = guild_wins.find()
    
            games = ["🚤 Battleship 💥", "🔴 Connect Four 🟡", "🌈 Mastermind", "🪨 Rock, 📄 Paper, ✂ Scissors", "❌ Tic-Tac-Toe ⭕", "👹 Hunt the Wumpus"]
    
            i = 0
            for game_name in games:
                if game == game_name:
                    game_index = i
                    break
    
                i = i + 1
    
    
            # Filter players with non-zero wins
            filtered_winners = [p for p in win_records if p["wins"][game_index] > 0]
            
            # Sort the filtered player records based on the number of wins in descending order
            sorted_winners = sorted(filtered_winners, key=lambda x: x["wins"][game_index], reverse=True)
            
            # Filter players with non-zero shillings
            filtered_earners = [p for p in earn_records if p["shillings"][game_index] > 0]
            
            # Sort the filtered player records based on the number of shillings in descending order
            sorted_earners = sorted(filtered_earners, key=lambda x: x["shillings"][game_index], reverse=True)
    
            # Select the top 10 players with the highest number of wins
            top_10_winners = sorted_winners[:10]
    
            # Select the top 10 players with the highest number of shillings
            top_10_earners = sorted_earners[:10]
    
          
            medal_emojis = ["🥇", "🥈", "🥉"]
          
            # Win leaders
            win_leaders = []
            for i, winner in enumerate(top_10_winners):
                winner_name = winner["player_name"]
                wins = winner["wins"][game_index]
                medal = medal_emojis[i] if i < 3 else "🔷"
                win_str = f"{medal} {winner_name} `{wins:,}`"
                win_leaders.append(win_str)
    
            top_winners = '\n'.join(f"> {line}" for line in win_leaders) + '\n'
    
    
            # Earning leaders
            earn_leaders = []
            for i, earner in enumerate(top_10_earners):
                earner_name = earner["player_name"]
                shillings = earner["shillings"][game_index]
                medal = medal_emojis[i] if i < 3 else "🔷"
                earn_str = f"{medal} {earner_name} `{shillings:,}`"
                earn_leaders.append(earn_str)
    
            top_earners = '\n'.join(f"> {line}" for line in earn_leaders) + '\n'
            
          
            leaderboard_embed = discord.Embed(title=f"{self.ctx.guild.name}\nTop Talent", description = f"`{game}`", color = discord.Color.from_rgb(0, 0, 255))
    
                  
            leaderboard_embed.add_field(name="🏆 Top Wins", value=top_winners)
            leaderboard_embed.add_field(name="🪙 Top Earnings", value=top_earners)
    
            leaderboard_embed.set_thumbnail(url=self.game_GIF_dict[game])
          
            await self.message.edit(embed=leaderboard_embed, view=self)


#################################LEADERBOARD################################




  


#############################BATTLESHIP####################################
    # Helper function to check for overlapping positions
    def can_place_ship(self, board, ship, row, col, orientation):
        ship_size = len(ship)
        if orientation == 'horizontal':
            for i in range(ship_size):
                if row >= len(board) or col >= len(board[0]) or board[row][col] != ' ':
                    return False
                col += 1
        elif orientation == 'vertical':
            for i in range(ship_size):
                if row >= len(board) or col >= len(board[0]) or board[row][col] != ' ':
                    return False
                row += 1
        return True

  
    @discord.slash_command(
        name="battleship",
        description="Challenge the automaton or another member of the guild to a game of Battleship.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def battleship(self, ctx, player2: Option(discord.Member, name="player2", description="Opponent for the game."), difficulty: Option(str, name="difficulty", description="Difficulty setting when facing the automaton. (Default: 🟡 Medium)", required=False, default=None, choices=["🟢 Easy", "🟡 Medium", "🔴 Hard"])):
    
        #check the member that is used
        #cannot play against self
        if player2.id == ctx.author.id:
            await ctx.respond(f"Apologies {ctx.author.mention},\nYou are unable to play against yourself in Battleship.\n*Please try again using a different member of {ctx.guild.name}.*", ephemeral=True)
            return
    
        #play against Lord Bottington
        elif player2.id == self.bot.user.id:
            player2_bot = True
          
        #cannot play against a bot that is not Lord Bottington
        elif player2.bot:
            await ctx.respond(f"Apologies {ctx.author.mention},\nYou cannot play against *{player2.display_name}* in Battleship. You may only face myself or another member of {ctx.guild.name}.\n*Please try again.*", ephemeral=True)
            return
    
        else:
            player2_bot = False

        #difficulty
        difficulty_dict = {
          "🟢 Easy": "easy",
          "🟡 Medium": "medium",
          "🔴 Hard": "hard"
        }
    
        if difficulty:
            bot_difficulty = difficulty_dict[difficulty]
        else:
            difficulty = "🟡 Medium"
            bot_difficulty = "medium"  

        # Blank board
        blank_board = [['🟦' for _ in range(10)] for _ in range(10)]
        
        letters = [':regional_indicator_a:', ':regional_indicator_b:', ':regional_indicator_c:', ':regional_indicator_d:', ':regional_indicator_e:', ':regional_indicator_f:', ':regional_indicator_g:', ':regional_indicator_h:', ':regional_indicator_i:', ':regional_indicator_j:']
        numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

        #ships: Destroyer (🟨🟨), Submarine (🟩🟩🟩), Cruiser (🟪🟪🟪), Battleship (🟧🟧🟧🟧), Carrier (⬛⬛⬛⬛⬛)
        ships = ['🟨🟨', '🟩🟩🟩', '🟪🟪🟪', '🟧🟧🟧🟧', '⬛⬛⬛⬛⬛']
        
        # Create a modified board for both players
        player1_board = [[' ' for _ in range(11)] for _ in range(11)]
        player2_board = [[' ' for _ in range(11)] for _ in range(11)]
        blank_board1_modified = [[' ' for _ in range(11)] for _ in range(11)]
        blank_board2_modified = [[' ' for _ in range(11)] for _ in range(11)]

        # Place the ships randomly on player 1's board
        for ship in ships:
            ship_size = len(ship)
            placed = False

            #place ships on player 1's board
            while not placed:
                row = random.randint(1, 10)
                col = random.randint(1, 10)
                orientation = random.choice(['horizontal', 'vertical'])
        
                if self.can_place_ship(player1_board, ship, row, col, orientation):
                    if orientation == 'horizontal':
                        for i in range(ship_size):
                            player1_board[row][col + i] = ship[i]
                    elif orientation == 'vertical':
                        for i in range(ship_size):
                            player1_board[row + i][col] = ship[i]
                    placed = True

        # Place the ships randomly on player 2's board
        for ship in ships:
            ship_size = len(ship)
            placed = False

            #place ships on player 2's board
            while not placed:
                row = random.randint(1, 10)
                col = random.randint(1, 10)
                orientation = random.choice(['horizontal', 'vertical'])
        
                if self.can_place_ship(player2_board, ship, row, col, orientation):
                    if orientation == 'horizontal':
                        for i in range(ship_size):
                            player2_board[row][col + i] = ship[i]
                    elif orientation == 'vertical':
                        for i in range(ship_size):
                            player2_board[row + i][col] = ship[i]
                    placed = True
      

        #add an emoji to the top left of the boards
        player1_board[0][0] = '🔲'
        player2_board[0][0] = '🔲'
        blank_board1_modified[0][0] = '🔲'
        blank_board2_modified[0][0] = '🔲'


        # Add letters column above the modified boards
        for i in range(1, 11):
            player1_board[0][i] = letters[i - 1]
            player2_board[0][i] = letters[i - 1]
            blank_board1_modified[0][i] = letters[i - 1]
            blank_board2_modified[0][i] = letters[i - 1]
        
        # Add numbers column on the left to the modified boards
        for i in range(1, 11):
            player1_board[i][0] = numbers[i - 1]
            player2_board[i][0] = numbers[i - 1]
            blank_board1_modified[i][0] = numbers[i - 1]
            blank_board2_modified[i][0] = numbers[i - 1]
        
        # Fill the rest of the modified boards with the blank board
        for i in range(1, 11):
            for j in range(1, 11):
                if player1_board[i][j] == ' ':
                    player1_board[i][j] = blank_board[i - 1][j - 1]
                  
                if player2_board[i][j] == ' ':
                    player2_board[i][j] = blank_board[i - 1][j - 1]

                blank_board1_modified[i][j] = blank_board[i - 1][i - j]
                blank_board2_modified[i][j] = blank_board[i - 1][i - j]
                  
        
        # Convert the modified boards to a string
        blank_board1_str = '\n'.join([''.join(row) for row in blank_board1_modified])
        blank_board2_str = '\n'.join([''.join(row) for row in blank_board2_modified])
      
        battleship_embed = discord.Embed(title="Battleship", description=f"Attention members of {ctx.guild.name}\nA game of Battleship has commenced.\nSelect the desired row and column using the position buttons below and then `💥Fire` upon your opponent's fleet.", color=discord.Color.from_rgb(0, 0, 255))

        battleship_embed.add_field(name="Player 1", value=ctx.author.mention)
        battleship_embed.add_field(name="Player 2", value=player2.mention)

        if player2_bot is True:
            battleship_embed.add_field(name="Difficulty", value=difficulty)

        battleship_embed.add_field(name="Player 1 Vessels Remaining", value = "`🚤 5`")
        battleship_embed.add_field(name="Player 2 Vessels Remaining", value = "`🚤 5`")

        battleship_embed.add_field(name="Player 1 Board", value=blank_board1_str, inline=False)
        battleship_embed.add_field(name="Player 2 Board", value=blank_board2_str, inline=False)

        battleship_embed.add_field(name="Hit Status", value="`n/a`", inline=False)
        
        battleship_embed.set_footer(text=f"Current Turn: 1️⃣{ctx.author.display_name}")
        battleship_embed.set_thumbnail(url="https://i.imgur.com/WVTMctu.gif") #battleship GIF

        await ctx.respond(embed=battleship_embed, view=self.PlacementView(ctx, difficulty, bot_difficulty, player1_board, player2_board, blank_board1_modified, blank_board2_modified, ctx.author, player2, player2_bot))




    #Place Buttons
    class PlacementView(discord.ui.View):
        def __init__(self, ctx, difficulty, bot_difficulty, player1_board, player2_board, blank_board1, blank_board2, player1, player2, player2_bot):
            super().__init__(timeout=120) #set the timeout
            self.ctx = ctx #intialize the context
            self.difficulty = difficulty
            self.bot_difficulty = bot_difficulty
            self.player1_board = player1_board
            self.player2_board = player2_board
            self.player1_blank_board = blank_board1
            self.player2_blank_board = blank_board2
            self.player1 = player1
            self.player2 = player2
            self.current_turn = player1
            self.player2_bot = player2_bot
            self.player1_ships_remaining = 5
            self.player2_ships_remaining = 5
            self.row = 0  #row for choosing location
            self.column = 0 #column for choosing location
            self.bot_boat = ""

      
        #switch the turns
        def toggle_turn(self):
            if self.current_turn == self.player1:
                self.current_turn = self.player2
            else:
                self.current_turn = self.player1
      

      
        # Handle timeout (e.g., if no moves are made within the specified timeout)
        async def on_timeout(self):
            player1_board = '\n'.join([''.join(row) for row in self.player1_board])
            player2_board = '\n'.join([''.join(row) for row in self.player2_board])
          
            battleship_embed = discord.Embed(title="Battleship", description=f"Attention members of {self.ctx.guild.name}\nA game of Battleship has ended...\nIt appears that {self.current_turn.mention} did not respond in time.", color=discord.Color.from_rgb(0, 0, 255))
    
            battleship_embed.add_field(name="Player 1", value=self.player1.mention)
            battleship_embed.add_field(name="Player 2", value=self.player2.mention)          
    
            if self.player2_bot is True:
                battleship_embed.add_field(name="Difficulty", value=self.difficulty)
    
            battleship_embed.add_field(name="Player 1 Vessels Remaining", value = f"`🚤 {self.player1_ships_remaining}`")
            battleship_embed.add_field(name="Player 2 Vessels Remaining", value = f"`🚤 {self.player2_ships_remaining}`")

            #for the boards, Player 1 Board always has to come first in the embed
            battleship_embed.add_field(name="Player 1 Board", value=player1_board, inline=False)
            battleship_embed.add_field(name="Player 2 Board", value=player2_board, inline=False)

            battleship_embed.add_field(name="Hit Status", value="`n/a`", inline=False)
            
            battleship_embed.set_thumbnail(url="https://i.imgur.com/WVTMctu.gif") #battleship GIF

            for child in self.children:
                child.disabled = True

            try:
                await self.message.edit(embed=battleship_embed, view=None)
            except discord.errors.NotFound: #if message deleted before timeout
                pass

            self.stop()


        #update winnings data
        def update_wins(self, winner, game_played):
            if winner and not winner.bot:
                #increase currency (🪙shillings) based on difficulty of game
                if self.bot_difficulty == "easy":
                    shillings = 2
                elif self.bot_difficulty == "medium":
                    shillings = 5
                elif self.bot_difficulty == "hard":
                    shillings = 10
                elif not self.player2.bot: #when facing regular player
                    shillings = 10

                games = ["battleship", "connectfour", "mastermind", "rps", "tictactoe", "wumpus"]

                i = 0
                for game in games:
                    if game_played == game:
                        game_index = i
                        break

                    i = i + 1

                no_wins = [0 for _ in range(6)] #blank array of wins
                no_shillings = [0 for _ in range(6)] #blank array of shillings
              
                #update the number of wins for connectfour for the winner
                guild_wins = games_db[f"winnings_{self.ctx.guild.id}"]
                game_key = {"player_id": winner.id}
    
                player_record = guild_wins.find_one(game_key)
              
                if player_record is None:
                    no_wins[game_index] = 1
                    no_shillings[game_index] = shillings
                  
                    guild_wins.insert_one(
                      {
                        "server_id": self.ctx.guild.id,
                        "server_name": self.ctx.guild.name,
                        "player_name": winner.display_name,
                        "player_id": winner.id,
                        "games": games,
                        "wins": no_wins,
                        "shillings": no_shillings
                      }
                    )
                else:
                    wins_obtained = player_record["wins"]
                    shillings_obtained = player_record["shillings"]

                    wins_obtained[game_index] += 1
                    shillings_obtained[game_index] += shillings
                  
                    guild_wins.update_one(
                        game_key,
                        {"$set": {
                          "wins": wins_obtained,
                          "shillings": shillings_obtained
                          }
                        }
                    )


                #wallets for the guild
                guild_wallets = wallets_db[f"wallets_{self.ctx.guild.id}"]
                wallet_key = {"player_id": winner.id}
              
                wallet_record = guild_wallets.find_one(wallet_key)

                if wallet_record is None:
                    guild_wallets.insert_one(
                      {
                        "server_id": self.ctx.guild.id,
                        "server_name": self.ctx.guild.name,
                        "player_name": winner.display_name,
                        "player_id": winner.id,
                        "wallet": shillings
                      }
                    )
              
                else:
                    guild_wallets.update_one(
                        wallet_key,
                        {"$inc": {
                          "wallet": shillings
                          }
                        }
                    )

      

        #update embed to display the winner
        async def winner(self, winner, loser):
            game_played = "battleship"
            self.update_wins(winner, game_played) #update winnings on database based on player faced and difficulty of game when facing bot
          
            player1_board = '\n'.join([''.join(row) for row in self.player1_board])
            player2_board = '\n'.join([''.join(row) for row in self.player2_board])
          
            battleship_embed = discord.Embed(title="Battleship", description=f"Attention members of {self.ctx.guild.name}\nA game of Battleship has ended...\n:trophy:{winner.mention} has defeated {loser.mention} on the high seas!", color=discord.Color.from_rgb(0, 0, 255))
    
            battleship_embed.add_field(name="Player 1", value=self.player1.mention)
            battleship_embed.add_field(name="Player 2", value=self.player2.mention)          
    
            if self.player2_bot is True:
                battleship_embed.add_field(name="Difficulty", value=self.difficulty)
    
            battleship_embed.add_field(name="Player 1 Vessels Remaining", value = f"`🚤 {self.player1_ships_remaining}`")
            battleship_embed.add_field(name="Player 2 Vessels Remaining", value = f"`🚤 {self.player2_ships_remaining}`")

            #for the boards, Player 1 Board always has to come first in the embed
            battleship_embed.add_field(name="Player 1 Board", value=player1_board, inline=False)
            battleship_embed.add_field(name="Player 2 Board", value=player2_board, inline=False)

            battleship_embed.add_field(name="Hit Status", value="`n/a`", inline=False)
          
            battleship_embed.set_thumbnail(url="https://i.imgur.com/WVTMctu.gif") #battleship GIF

            for child in self.children:
                child.disabled = True
            
            await self.message.edit(embed=battleship_embed, view=None)

            self.stop()


      

        #bot's move
        async def bot_move(self):
            #Boat Dict
            boat_dict = {
              "🟨": "🟨 Destroyer (2)",
              "🟩": "🟩 Submarine (3)",
              "🟪": "🟪 Cruiser (3)",
              "🟧": "🟧 Battleship (4)",
              "⬛": "⬛ Carrier (5)"
            }


            #if the bot has hit a boat before
            if self.bot_boat != "":
                if self.bot_difficulty == "easy":
                    if random.random() < 0.50:  # 50% chance of making a random move
                        bot_row = random.randint(1, 10)
                        bot_col = random.randint(1, 10)
                    else:
                        for row_index, row in enumerate(self.player1_board):
                            if self.bot_boat in row:
                                bot_row = row_index
                                bot_col = row.index(self.bot_boat)
                                break
                          
                elif self.bot_difficulty == "medium":
                    if random.random() < 0.25:  # 25% chance of making a random move
                        bot_row = random.randint(1, 10)
                        bot_col = random.randint(1, 10)
                    else:
                        for row_index, row in enumerate(self.player1_board):
                            if self.bot_boat in row:
                                bot_row = row_index
                                bot_col = row.index(self.bot_boat)
                                break

                elif self.bot_difficulty == "hard": #no chance of random move, just find the next available boat type row and column
                    for row_index, row in enumerate(self.player1_board):
                        if self.bot_boat in row:
                            bot_row = row_index
                            bot_col = row.index(self.bot_boat)
                            break

            else:
                # otherwise, loop through until the bot finds a random space not used
                space_empty = False
                while space_empty is False:
                    bot_row = random.randint(1, 10)
                    bot_col = random.randint(1, 10)
    
                    if self.player1_board[bot_row][bot_col] == "⚪" or self.player1_board[bot_row][bot_col] == "🔴":
                        space_empty = False
                  
                    else:
                        space_empty = True


            ### Check the hit for the bot
            # Miss
            if self.player1_board[bot_row][bot_col] == "🟦":
                self.player1_board[bot_row][bot_col] = "⚪"
                self.player1_blank_board[bot_row][bot_col] = "⚪"
                hit_status = "`⚪ Missed!`"

            # Hit
            elif (self.player1_board[bot_row][bot_col] == "🟨" or self.player1_board[bot_row][bot_col] == "🟩" or self.player1_board[bot_row][bot_col] == "🟪" or self.player1_board[bot_row][bot_col] == "🟧" or self.player1_board[bot_row][bot_col] == "⬛"):
                boat_type = self.player1_board[bot_row][bot_col]

                if self.bot_boat == "":
                    self.bot_boat = boat_type
                      

                self.player1_board[bot_row][bot_col] = "🔴"
                self.player1_blank_board[bot_row][bot_col] = "🔴"

                # Check if the boat has been sunk
                if not any(boat_type in row for row in self.player1_board): #boat sunk
                    hit_status = f"Sunk the `{boat_dict[boat_type]}` for {self.player1.mention}'s fleet!"
                    self.bot_boat = ""
                    self.player1_ships_remaining -= 1 #reduce player 1's number of ships by 1
                  
                    #update the embed to display the winner (if necessary)
                    #Winner = player 2, loser = player 1
                    if self.player1_ships_remaining == 0:
                        await self.winner(self.player2, self.player1)
                        return
              
                else:
                    hit_status = "`🔴 Hit!`"
          
            # Space already used
            else:
                return
              

            player1_board = '\n'.join([''.join(row) for row in self.player1_blank_board])
            player2_board = '\n'.join([''.join(row) for row in self.player2_blank_board])
    
              
            self.toggle_turn() #change the turn back to player
              
            battleship_embed = discord.Embed(title="Battleship", description=f"Attention members of {self.ctx.guild.name}\nA game of Battleship has commenced.\nSelect the desired row and column using the position buttons below and then `💥Fire` upon your opponent's fleet.", color=discord.Color.from_rgb(0, 0, 255))
    
            battleship_embed.add_field(name="Player 1", value=self.player1.mention)
            battleship_embed.add_field(name="Player 2", value=self.player2.mention)          
    
            if self.player2_bot is True:
                battleship_embed.add_field(name="Difficulty", value=self.difficulty)
    
            battleship_embed.add_field(name="Player 1 Vessels Remaining", value = f"`🚤 {self.player1_ships_remaining}`")
            battleship_embed.add_field(name="Player 2 Vessels Remaining", value = f"`🚤 {self.player2_ships_remaining}`")
    
            #for the boards, Player 1 Board always has to come first in the embed
            battleship_embed.add_field(name="Player 1 Board", value=player1_board, inline=False)
            battleship_embed.add_field(name="Player 2 Board", value=player2_board, inline=False)

            battleship_embed.add_field(name="Hit Status", value=hit_status, inline=False)
          
            battleship_embed.set_footer(text=f"Current Turn: {'1️⃣' if self.current_turn.id == self.player1.id else '2️⃣'}{self.current_turn.display_name}")
            battleship_embed.set_thumbnail(url="https://i.imgur.com/WVTMctu.gif") #battleship GIF
    
            await self.message.edit(embed=battleship_embed, view=self)
    

      

      

        #### Player Move
        async def fire(self):
            #Boat Dict
            boat_dict = {
              "🟨": "🟨 Destroyer (2)",
              "🟩": "🟩 Submarine (3)",
              "🟪": "🟪 Cruiser (3)",
              "🟧": "🟧 Battleship (4)",
              "⬛": "⬛ Carrier (5)"
            }

            ####check the current turn and if the shot already was used

            ## PLAYER 1's TURN
            if self.current_turn.id == self.player1.id:
                # Miss
                if self.player2_board[self.row][self.column] == "🟦":
                    self.player2_board[self.row][self.column] = "⚪"
                    self.player2_blank_board[self.row][self.column] = "⚪"
                    hit_status = "`⚪ Missed!`"
    
                # Hit
                elif self.player2_board[self.row][self.column] == "🟨" or self.player2_board[self.row][self.column] == "🟩" or self.player2_board[self.row][self.column] == "🟪" or self.player2_board[self.row][self.column] == "🟧" or self.player2_board[self.row][self.column] == "⬛":
                    boat_type = self.player2_board[self.row][self.column]
                  
                    self.player2_board[self.row][self.column] = "🔴"
                    self.player2_blank_board[self.row][self.column] = "🔴"

                    # Check if the boat has been sunk
                    if not any(boat_type in row for row in self.player2_board): #boat sunk
                        hit_status = f"Sunk the `{boat_dict[boat_type]}` for {self.player2.mention}'s fleet!"
                        self.player2_ships_remaining -= 1 #reduce player 2's number of ships by 1

                        #update the embed to display the winner (if necessary)
                        #Winner = player 1, loser = player 2
                        if self.player2_ships_remaining == 0:
                            await self.winner(self.player1, self.player2)
                            return
                      
                    else:
                        hit_status = "`🔴 Hit!`"
    
                # Space already used
                else:
                    return

            ## PLAYER 2's TURN
            else:
                # Miss
                if self.player1_board[self.row][self.column] == "🟦":
                    self.player1_board[self.row][self.column] = "⚪"
                    self.player1_blank_board[self.row][self.column] = "⚪"
                    hit_status = "`⚪ Missed!`"
    
                # Hit
                elif self.player1_board[self.row][self.column] == "🟨" or self.player1_board[self.row][self.column] == "🟩" or self.player1_board[self.row][self.column] == "🟪" or self.player1_board[self.row][self.column] == "🟧" or self.player1_board[self.row][self.column] == "⬛":
                    boat_type = self.player1_board[self.row][self.column]
                  
                    self.player1_board[self.row][self.column] = "🔴"
                    self.player1_blank_board[self.row][self.column] = "🔴"

                    # Check if the boat has been sunk
                    if not any(boat_type in row for row in self.player1_board): #boat sunk
                        hit_status = f"Sunk the `{boat_dict[boat_type]}` for {self.player1.mention}'s fleet!"
                        self.player1_ships_remaining -= 1 #reduce player 1's number of ships by 1
                      
                        #update the embed to display the winner (if necessary)
                        #Winner = player 2, loser = player 1
                        if self.player1_ships_remaining == 0:
                            await self.winner(self.player2, self.player1)
                            return
                  
                    else:
                        hit_status = "`🔴 Hit!`"
              
                # Space already used
                else:
                    return
                  

            player1_board = '\n'.join([''.join(row) for row in self.player1_blank_board])
            player2_board = '\n'.join([''.join(row) for row in self.player2_blank_board])

          
            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index < 20:
                    child.style = discord.ButtonStyle.primary

            #reset the row and column and fire button
            self.row = 0
            self.column = 0
            self.children[-1].disabled = True #fire button is the last button

            self.toggle_turn()
              
            battleship_embed = discord.Embed(title="Battleship", description=f"Attention members of {self.ctx.guild.name}\nA game of Battleship has commenced.\nSelect the desired row and column using the position buttons below and then `💥Fire` upon your opponent's fleet.", color=discord.Color.from_rgb(0, 0, 255))
    
            battleship_embed.add_field(name="Player 1", value=self.player1.mention)
            battleship_embed.add_field(name="Player 2", value=self.player2.mention)          
    
            if self.player2_bot is True:
                battleship_embed.add_field(name="Difficulty", value=self.difficulty)
    
            battleship_embed.add_field(name="Player 1 Vessels Remaining", value = f"`🚤 {self.player1_ships_remaining}`")
            battleship_embed.add_field(name="Player 2 Vessels Remaining", value = f"`🚤 {self.player2_ships_remaining}`")

            #for the boards, Player 1 Board always has to come first in the embed
            battleship_embed.add_field(name="Player 1 Board", value=player1_board, inline=False)
            battleship_embed.add_field(name="Player 2 Board", value=player2_board, inline=False)

            battleship_embed.add_field(name="Hit Status", value=hit_status, inline=False)
          
            battleship_embed.set_footer(text=f"Current Turn: {'1️⃣' if self.current_turn.id == self.player1.id else '2️⃣'}{self.current_turn.display_name}")
            battleship_embed.set_thumbnail(url="https://i.imgur.com/WVTMctu.gif") #battleship GIF
    
            await self.message.edit(embed=battleship_embed, view=self)




      
        ############### LETTERS ###############

        ####### 'A' Button
        @discord.ui.button(label="A", row=0, style=discord.ButtonStyle.primary)
        async def A_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index < 10:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.column = 1

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color
          

        ####### 'B' Button
        @discord.ui.button(label="B", row=0, style=discord.ButtonStyle.primary)
        async def B_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index < 10:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.column = 2

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color
              

        ####### 'C' Button
        @discord.ui.button(label="C", row=0, style=discord.ButtonStyle.primary)
        async def C_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index < 10:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.column = 3

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color

        ####### 'D' Button
        @discord.ui.button(label="D", row=0, style=discord.ButtonStyle.primary)
        async def D_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index < 10:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.column = 4

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color

        ####### 'E' Button
        @discord.ui.button(label="E", row=0, style=discord.ButtonStyle.primary)
        async def E_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index < 10:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.column = 5

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color

        ####### 'F' Button
        @discord.ui.button(label="F", row=1, style=discord.ButtonStyle.primary)
        async def F_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index < 10:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.column = 6

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color

        ####### 'G' Button
        @discord.ui.button(label="G", row=1, style=discord.ButtonStyle.primary)
        async def G_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index < 10:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.column = 7

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color

        ####### 'H' Button
        @discord.ui.button(label="H", row=1, style=discord.ButtonStyle.primary)
        async def H_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index < 10:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.column = 8

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color

        ####### 'I' Button
        @discord.ui.button(label="I", row=1, style=discord.ButtonStyle.primary)
        async def I_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index < 10:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.column = 9

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color

        ####### 'J' Button
        @discord.ui.button(label="J", row=1, style=discord.ButtonStyle.primary)
        async def J_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index < 10:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.column = 10

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color


      
        ############### NUMBERS ###############
      
        ####### '1' Button
        @discord.ui.button(emoji="1️⃣", row=2, style=discord.ButtonStyle.primary)
        async def button1_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index >= 10 and index < 20:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.row = 1

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color

        ####### '2' Button
        @discord.ui.button(emoji="2️⃣", row=2, style=discord.ButtonStyle.primary)
        async def button2_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index >= 10 and index < 20:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.row = 2

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color

        ####### '3' Button
        @discord.ui.button(emoji="3️⃣", row=2, style=discord.ButtonStyle.primary)
        async def button3_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index >= 10 and index < 20:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.row = 3

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color

        ####### '4' Button
        @discord.ui.button(emoji="4️⃣", row=2, style=discord.ButtonStyle.primary)
        async def button4_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index >= 10 and index < 20:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.row = 4

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color

        ####### '5' Button
        @discord.ui.button(emoji="5️⃣", row=2, style=discord.ButtonStyle.primary)
        async def button5_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index >= 10 and index < 20:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.row = 5

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color

        ####### '6' Button
        @discord.ui.button(emoji="6️⃣", row=3, style=discord.ButtonStyle.primary)
        async def button6_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index >= 10 and index < 20:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.row = 6

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color

        ####### '7' Button
        @discord.ui.button(emoji="7️⃣", row=3, style=discord.ButtonStyle.primary)
        async def button7_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index >= 10 and index < 20:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.row = 7

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color

        ####### '8' Button
        @discord.ui.button(emoji="8️⃣", row=3, style=discord.ButtonStyle.primary)
        async def button8_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index >= 10 and index < 20:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.row = 8

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color

        ####### '9' Button
        @discord.ui.button(emoji="9️⃣", row=3, style=discord.ButtonStyle.primary)
        async def button9_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index >= 10 and index < 20:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.row = 9

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color

        ####### '10' Button
        @discord.ui.button(emoji="🔟", row=3, style=discord.ButtonStyle.primary)
        async def button10_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            for index, child in enumerate(self.children): #change all the position buttons back to primary style
                if index >= 10 and index < 20:
                    child.style = discord.ButtonStyle.primary
        
            button.style = discord.ButtonStyle.success #change the selection to green color

            self.row = 10

            #only enable the fire button when the user has selected a row and column
            if self.row != 0 and self.column != 0:
                self.children[-1].disabled = False

            await self.message.edit(view=self) #update the embed with the button color


        #################### OTHER BUTTONS ####################
        ####### End Game Button
        @discord.ui.button(emoji="🏳", label="Surrender", row=4, style=discord.ButtonStyle.danger)
        async def end_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            #decide winner and loser
            if interaction.user.id == self.player1.id:
                winner = self.player2
                loser = self.player1
            else:
                winner = self.player1
                loser = self.player2

          
          
            player1_board = '\n'.join([''.join(row) for row in self.player1_board])
            player2_board = '\n'.join([''.join(row) for row in self.player2_board])
          
            battleship_embed = discord.Embed(title="Battleship", description=f"Attention members of {self.ctx.guild.name}\nA game of Battleship has ended...\n{loser.mention} has **🏳 Surrendered** to {winner.mention}.", color=discord.Color.from_rgb(0, 0, 255))
    
            battleship_embed.add_field(name="Player 1", value=self.player1.mention)
            battleship_embed.add_field(name="Player 2", value=self.player2.mention)          
    
            if self.player2_bot is True:
                battleship_embed.add_field(name="Difficulty", value=self.difficulty)
    
            battleship_embed.add_field(name="Player 1 Vessels Remaining", value = f"`🚤 {self.player1_ships_remaining}`")
            battleship_embed.add_field(name="Player 2 Vessels Remaining", value = f"`🚤 {self.player2_ships_remaining}`")

            #for the boards, Player 1 Board always has to come first in the embed
            battleship_embed.add_field(name="Player 1 Board", value=player1_board, inline=False)
            battleship_embed.add_field(name="Player 2 Board", value=player2_board, inline=False)

            battleship_embed.add_field(name="Hit Status", value="`n/a`", inline=False)
          
            battleship_embed.set_thumbnail(url="https://i.imgur.com/WVTMctu.gif") #battleship GIF

            for child in self.children:
                child.disabled = True
            
            await self.message.edit(embed=battleship_embed, view=None)

            self.stop()


        ####### View Own Board Button
        @discord.ui.button(emoji="🔎", label="View Fleet", row=4, style=discord.ButtonStyle.secondary)
        async def viewboard_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id not in [self.player1.id, self.player2.id]:
                return

            #choose the correct board
            if interaction.user.id == self.player1.id:
                board = self.player1_board
                user = self.player1
                opponent = self.player2
            else:
                board = self.player2_board
                user = self.player2
                opponent = self.player1

            board_str = '\n'.join([''.join(row) for row in board])

            # Send the board as a message only to the user who clicked the button
            await interaction.followup.send(f"**Battleship**\n\n{user.mention},\nHere is your fleet for your battle on the high seas against *{opponent.display_name}*, captain:\n\n{board_str}", ephemeral=True)




        ####### Fire Button
        @discord.ui.button(emoji="💥", label="Fire", row=4, style=discord.ButtonStyle.success, disabled=True) #start with Fire button disabled (until the user selects both positions)
        async def fire_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.current_turn.id:
                return

            await self.fire()

            #Make bot move after player's turn (if used)
            if self.player2_bot is True:
                await asyncio.sleep(4) #simulate loading
                await self.bot_move()


#############################BATTLESHIP####################################




  




###############################MASTERMIND###################################
    @discord.slash_command(
        name="mastermind",
        description="Decipher the secret code of the automaton.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def mastermind(self, ctx, difficulty: Option(str, name="difficulty", description="Difficulty of the code. (Default: 🟡 Medium)", required=False, default=None, choices=["🟢 Easy", "🟡 Medium", "🔴 Hard"])):


        #difficulty
        difficulty_dict = {
          "🟢 Easy": "easy",
          "🟡 Medium": "medium",
          "🔴 Hard": "hard"
        }
    
        if difficulty:
            bot_difficulty = difficulty_dict[difficulty]
        else:
            difficulty = "🟡 Medium"
            bot_difficulty = "medium"

        #increase the number of characters you have to guess as the difficulty goes up
        if bot_difficulty == "easy":
            characters = 4
        elif bot_difficulty == "medium":
            characters = 5
        elif bot_difficulty == "hard":
            characters = 6
      
        #create guesses string
        guesses = [['🔳' for _ in range(characters)] for _ in range(10)]
        guesses_string = '\n'.join([''.join(row) for row in guesses])

        #create answers string (to tell the user how many they got correct)
        correct_guesses = [['🔳' for _ in range(characters)] for _ in range(10)]
        correct_guesses_string = '\n'.join([''.join(row) for row in correct_guesses])

        #create blank answer string
        answer_blank = ['🔳' for _ in range(characters)]
        answer_blank_string = ''.join(answer_blank)

        #create the actual answer
        colors = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "⬛", "⬜"]

        answer = random.choices(colors, k=characters)
        answer_string = ''.join(answer)

        attempts = 10 #the number of attempts the user gets
      
        mm_embed = discord.Embed(title="Mastermind", description=f"Attention members of {ctx.guild.name}\nA game of Mastermind has commenced.\n{ctx.author.mention} must decipher my secret...", color = discord.Color.from_rgb(0, 0, 255))
        mm_embed.add_field(name="Difficulty", value=difficulty, inline=True)
        mm_embed.add_field(name="Secret Code", value=f"```{answer_blank_string}```", inline=False)
        mm_embed.add_field(name="Guesses", value=f"```{guesses_string}```", inline=True)
        mm_embed.add_field(name="Number Correct", value=f"```{correct_guesses_string}```", inline=True)
        mm_embed.set_thumbnail(url="https://i.imgur.com/Ce6Y2Ee.gif") #rainbow GIF

        await ctx.respond(embed=mm_embed, view=self.MMView(ctx, difficulty, bot_difficulty, attempts, characters, guesses, guesses_string, correct_guesses, correct_guesses_string, answer_blank, answer_blank_string, answer, answer_string))
    


  
    #mastermind buttons
    class MMView(discord.ui.View):
        def __init__(self, ctx, difficulty, bot_difficulty, attempts, characters, guesses, guesses_string, correct_guesses, correct_guesses_string, answer_blank, answer_blank_string, answer, answer_string):
            super().__init__(timeout=120) #set the timeout
            self.ctx = ctx #intialize the context
            self.difficulty = difficulty
            self.bot_difficulty = bot_difficulty
            self.attempts = attempts
            self.total_clicks = characters
            self.clicks = characters #the number of clicks the user gets for the difficulty
            self.children[9].disabled = True #start with the undo move button disabled
            self.guesses = [] #initialize a blank guessing array
            self.guess_row = attempts - 1 #initialize the row for updating the embed
            self.guess_column = 0 #initialize the column for updating the embed

            #guess arrays
            self.guesses_array = guesses
            self.guesses_string = guesses_string
            self.correct_guesses = correct_guesses
            self.correct_guesses_string = correct_guesses_string
            self.answer_blank = answer_blank
            self.answer_blank_string = answer_blank_string #blank answer string
            self.answer = answer #answer
            self.answer_string = answer_string #answer string
            
      
        #guessing function
        async def guessing(self, emoji, undo_clicked):
            #update list
            if undo_clicked is True:
                self.guess_column -= 1 #decrease the column by 1 (needs to be done before to update the embed accordingly)
                self.guesses_array[self.guess_row][self.guess_column] = "🔳"
                guesses = '\n'.join([''.join(row) for row in self.guesses_array])

                correct_guesses = '\n'.join([''.join(row) for row in self.correct_guesses])
              
                self.guesses.pop() #remove the last entry in the guesses array
                self.clicks += 1 #increase the number of clicks remaining
            else:
                self.guesses_array[self.guess_row][self.guess_column] = emoji.name
                guesses = '\n'.join([''.join(row) for row in self.guesses_array])

                correct_guesses = '\n'.join([''.join(row) for row in self.correct_guesses])
                          
              
                self.guesses.append(emoji.name)
                self.guess_column += 1 #increase the column by 1
                self.clicks -= 1 #reduce the number of clicks remaining

            #enable/disable buttons
            if self.clicks == self.total_clicks:
                for index, child in enumerate(self.children): #enable color buttons
                    if index < 8:
                        child.disabled = False
              
                self.children[9].disabled = True #undo move button disabled
              
            elif self.clicks == 0:
                for index, child in enumerate(self.children): #only disable the color buttons
                    if index < 8:
                        child.disabled = True

                self.children[9].disabled = False #undo move button enabled
    
            else:
                for index, child in enumerate(self.children): #enable the color buttons
                    if index < 8:
                        child.disabled = False
              
                self.children[9].disabled = False #undo move button enabled
          

          
            mm_embed = discord.Embed(title="Mastermind", description=f"Attention members of {self.ctx.guild.name}\nA game of Mastermind has commenced.\n{self.ctx.author.mention} must decipher my secret...", color = discord.Color.from_rgb(0, 0, 255))
            mm_embed.add_field(name="Difficulty", value=self.difficulty, inline=True)
            mm_embed.add_field(name="Secret Code", value=f"```{self.answer_blank_string}```", inline=False)
            mm_embed.add_field(name="Guesses", value=f"```{guesses}```", inline=True)
            mm_embed.add_field(name="Number Correct", value=f"```{correct_guesses}```", inline=True)
            mm_embed.set_thumbnail(url="https://i.imgur.com/Ce6Y2Ee.gif") #rainbow GIF

          
            await self.message.edit(embed = mm_embed, view=self) #update the embed
        


        #update winnings data
        def update_wins(self, winner, game_played):
            if winner and not winner.bot:
                #increase currency (🪙shillings) based on difficulty of game
                if self.bot_difficulty == "easy":
                    shillings = 2
                elif self.bot_difficulty == "medium":
                    shillings = 5
                elif self.bot_difficulty == "hard":
                    shillings = 10
                    
              
                games = ["battleship", "connectfour", "mastermind", "rps", "tictactoe", "wumpus"]

                i = 0
                for game in games:
                    if game_played == game:
                        game_index = i
                        break

                    i = i + 1

                no_wins = [0 for _ in range(6)] #blank array of wins
                no_shillings = [0 for _ in range(6)] #blank array of shillings
              
                #update the number of wins for connectfour for the winner
                guild_wins = games_db[f"winnings_{self.ctx.guild.id}"]
                game_key = {"player_id": winner.id}
    
                player_record = guild_wins.find_one(game_key)
              
                if player_record is None:
                    no_wins[game_index] = 1
                    no_shillings[game_index] = shillings
                  
                    guild_wins.insert_one(
                      {
                        "server_id": self.ctx.guild.id,
                        "server_name": self.ctx.guild.name,
                        "player_name": winner.display_name,
                        "player_id": winner.id,
                        "games": games,
                        "wins": no_wins,
                        "shillings": no_shillings
                      }
                    )
                else:
                    wins_obtained = player_record["wins"]
                    shillings_obtained = player_record["shillings"]

                    wins_obtained[game_index] += 1
                    shillings_obtained[game_index] += shillings
                  
                    guild_wins.update_one(
                        game_key,
                        {"$set": {
                          "wins": wins_obtained,
                          "shillings": shillings_obtained
                          }
                        }
                    )


                #wallets for the guild
                guild_wallets = wallets_db[f"wallets_{self.ctx.guild.id}"]
                wallet_key = {"player_id": winner.id}
              
                wallet_record = guild_wallets.find_one(wallet_key)

                if wallet_record is None:
                    guild_wallets.insert_one(
                      {
                        "server_id": self.ctx.guild.id,
                        "server_name": self.ctx.guild.name,
                        "player_name": winner.display_name,
                        "player_id": winner.id,
                        "wallet": shillings
                      }
                    )
              
                else:
                    guild_wallets.update_one(
                        wallet_key,
                        {"$inc": {
                          "wallet": shillings
                          }
                        }
                    )


      

        #check answer
        async def check_answer(self, guess):
            # Update the correct answer string for the corresponding row
            for i in range(len(self.answer)):
                if self.guesses[i] == self.answer[i]:
                    self.correct_guesses[self.guess_row][i] = "🔲"

          
            if guess == self.answer_string:
                win = True
                description = f"Attention members of {self.ctx.guild.name}\nCongratulations to {self.ctx.author.mention} :trophy:\n\nThey have successfully deciphered my secret code!\nMay you be honored amongst your peers for this achievement..."
                game_played = "mastermind"
                self.update_wins(self.ctx.author, game_played) #update winnings on database based on difficulty
                view = None
                answer = self.answer_string
                guesses = '\n'.join([''.join(row) for row in self.guesses_array])
                correct_guesses = '\n'.join([''.join(row) for row in self.correct_guesses])

            elif self.guesses_array[0][self.total_clicks-1] != "🔳": #check top right block
                win = False
                description = f"Attention members of {self.ctx.guild.name}\nA game of Mastermind has ended.\n\n{self.ctx.author.mention} was unable to decipher my secret code...\nWhom shall I stump next?	🤔"
                view=None
                answer = self.answer_string
                guesses = '\n'.join([''.join(row) for row in self.guesses_array])
                correct_guesses = '\n'.join([''.join(row) for row in self.correct_guesses])
          
            else:
                win = False #incorrect answer
                self.clicks = self.total_clicks #reset the clicks
                self.guess_column = 0 #reset the column to 0
                self.guess_row -= 1 #decrease the row by 1
                self.guesses = [] #reset the guesses to a blank string so the user can try again

                description = f"Attention members of {self.ctx.guild.name}\nA game of Mastermind has commenced.\n{self.ctx.author.mention} must decipher my secret..."

                for index, child in enumerate(self.children): #enable the color buttons
                    if index < 8:
                        child.disabled = False
              
                self.children[9].disabled = True #undo move button disabled

                view = self
                answer = self.answer_blank_string
                guesses = '\n'.join([''.join(row) for row in self.guesses_array])
                correct_guesses = '\n'.join([''.join(row) for row in self.correct_guesses])
                

            mm_embed = discord.Embed(title="Mastermind", description=description, color = discord.Color.from_rgb(0, 0, 255))
            mm_embed.add_field(name="Difficulty", value=self.difficulty, inline=True)
            mm_embed.add_field(name="Secret Code", value=f"```{answer}```", inline=False)
            mm_embed.add_field(name="Guesses", value=f"```{guesses}```", inline=True)
            mm_embed.add_field(name="Number Correct", value=f"```{correct_guesses}```", inline=True)
            mm_embed.set_thumbnail(url="https://i.imgur.com/Ce6Y2Ee.gif") #rainbow GIF

            await self.message.edit(embed = mm_embed, view = view)
            return win
            

        # Handle timeout (e.g., if no moves are made within the specified timeout)
        async def on_timeout(self):
            description = f"Attention members of {self.ctx.guild.name}\nA game of Mastermind has ended.\n\n{self.ctx.author.mention} has given up trying to decipher my secret code...\nWhom shall I stump next?	🤔"
            view=None
            answer = self.answer_string
            guesses = '\n'.join([''.join(row) for row in self.guesses_array])
            correct_guesses = '\n'.join([''.join(row) for row in self.correct_guesses])

          
            mm_embed = discord.Embed(title="Mastermind", description=description, color = discord.Color.from_rgb(0, 0, 255))
            mm_embed.add_field(name="Difficulty", value=self.difficulty, inline=True)
            mm_embed.add_field(name="Secret Code", value=f"```{answer}```", inline=False)
            mm_embed.add_field(name="Guesses", value=f"```{guesses}```", inline=True)
            mm_embed.add_field(name="Number Correct", value=f"```{correct_guesses}```", inline=True)
            mm_embed.set_thumbnail(url="https://i.imgur.com/Ce6Y2Ee.gif") #rainbow GIF

            for child in self.children:
                child.disabled = True

            try:
                await self.message.edit(embed = mm_embed, view = view)
            except discord.errors.NotFound: #if message deleted before timeout
                pass
          
            self.stop()
      
      

        ####### Red Color Button
        @discord.ui.button(label="Red", emoji="🟥", row=0, style=discord.ButtonStyle.primary)
        async def red_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            undo_clicked = False
            await self.guessing(button.emoji, undo_clicked)
      

        ####### Orange Color Button
        @discord.ui.button(label="Orange", emoji="🟧", row=0, style=discord.ButtonStyle.primary)
        async def orange_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            undo_clicked = False
            await self.guessing(button.emoji, undo_clicked)

      

        ####### Yellow Color Button
        @discord.ui.button(label="Yellow", emoji="🟨", row=0, style=discord.ButtonStyle.primary)
        async def yellow_button_callback(self, button, interaction):
            await interaction.response.defer()
          
            if interaction.user.id != self.ctx.author.id:
                return

            undo_clicked = False
            await self.guessing(button.emoji, undo_clicked)

      

        ####### Green Color Button
        @discord.ui.button(label="Green", emoji="🟩", row=0, style=discord.ButtonStyle.primary)
        async def green_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            undo_clicked = False
            await self.guessing(button.emoji, undo_clicked)


        ####### Blue Color Button
        @discord.ui.button(label="Blue", emoji="🟦", row=1, style=discord.ButtonStyle.primary)
        async def blue_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            undo_clicked = False
            await self.guessing(button.emoji, undo_clicked)

      

        ####### Purple Color Button
        @discord.ui.button(label="Purple", emoji="🟪", row=1, style=discord.ButtonStyle.primary)
        async def purple_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            undo_clicked = False
            await self.guessing(button.emoji, undo_clicked)

        ####### Brown Color Button
        @discord.ui.button(label="Black", emoji="⬛", row=1, style=discord.ButtonStyle.primary)
        async def black_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            undo_clicked = False
            await self.guessing(button.emoji, undo_clicked)

        ####### White Color Button
        @discord.ui.button(label="White", emoji="⬜", row=1, style=discord.ButtonStyle.primary)
        async def white_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            undo_clicked = False
            await self.guessing(button.emoji, undo_clicked)


        ####### End Game
        @discord.ui.button(label = "End Game", emoji="🛑", row=2, style=discord.ButtonStyle.secondary)
        async def end_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            description = f"Attention members of {self.ctx.guild.name}\nA game of Mastermind has ended.\n\n{self.ctx.author.mention} has given up trying to decipher my secret code...\nWhom shall I stump next?	🤔"
            view=None
            answer = self.answer_string
            guesses = '\n'.join([''.join(row) for row in self.guesses_array])
            correct_guesses = '\n'.join([''.join(row) for row in self.correct_guesses])

          
            mm_embed = discord.Embed(title="Mastermind", description=description, color = discord.Color.from_rgb(0, 0, 255))
            mm_embed.add_field(name="Difficulty", value=self.difficulty, inline=True)
            mm_embed.add_field(name="Secret Code", value=f"```{answer}```", inline=False)
            mm_embed.add_field(name="Guesses", value=f"```{guesses}```", inline=True)
            mm_embed.add_field(name="Number Correct", value=f"```{correct_guesses}```", inline=True)
            mm_embed.set_thumbnail(url="https://i.imgur.com/Ce6Y2Ee.gif") #rainbow GIF

            for child in self.children:
                child.disabled = True

            await self.message.edit(embed = mm_embed, view = view)
          
            self.stop()


        ####### Undo Guess
        @discord.ui.button(label = "Undo", emoji="🔄", row=2, style=discord.ButtonStyle.secondary)
        async def undo_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            undo_clicked = True
            await self.guessing(None, undo_clicked)
      
      
        ####### Submit Guess
        @discord.ui.button(label = "Submit", emoji="✅", row=2, style=discord.ButtonStyle.success)
        async def submit_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return
          
            
            if len(self.guesses) != self.total_clicks: #not enough guesses in the string
                return
            else:
                guess = ''.join(self.guesses)
                check_win = await self.check_answer(guess)

                if check_win is True:
                    for child in self.children:
                        child.disabled = True

                    self.stop()


################################MASTERMIND###################################

  



  
  
################################WUMPUS######################################
    @discord.slash_command(
        name="wumpus",
        description="Go on a hunt to find and conquer the dreaded Wumpus.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def wumpus(self, ctx, danger_level: Option(str, name="danger_level", description="How perilous the cave system will be for the hunt. (Default: 🟨 Challenging)", required=False, default=None, choices=["🟩 Safe", "🟨 Challenging", "🟥 Dangerous", "👹 Perilous"])):
      
        # Initialize the map array.
        
        world = [['🔲' for _ in range(10)] for _ in range(7)]
        
        # Hide the wumpus (w).
        row = random.randint(1, 5)
        col = random.randint(1, 8)
        world[row][col] = 'w'

        danger_dict = {
          "🟩 Safe": "safe",
          "🟨 Challenging": "challenging",
          "🟥 Dangerous": "dangerous",
          "👹 Perilous": "perilous"
        }

        if danger_level:
            danger = danger_dict[danger_level]
        elif danger_level is None:
            danger_level = "🟨 Challenging"
            danger = "challenging"

        #increase the number of obstacles generated based on difficulty
        if danger == "safe":
            obstacle_count = 2

        elif danger == "challenging":
            obstacle_count = 3

        elif danger == "dangerous":
            obstacle_count = 4

        elif danger == "perilous":
            obstacle_count = 6

        #hide the pits (p)
        for p in range(obstacle_count):
            while True:
                row = random.randint(1, 5)
                col = random.randint(1, 8)
                if world[row][col] == '🔲':
                    world[row][col] = 'p'
                    break

        #hide the bats (b)
        for b in range(obstacle_count):
            while True:
                row = random.randint(1, 5)
                col = random.randint(1, 8)
                if world[row][col] == '🔲':
                    world[row][col] = 'b'
                    break

        #place user in a safe spot
        needit = True
        while needit:
          row = random.randint(1, 5)
          col = random.randint(1, 8)
          if world[row][col] == '🔲':
            userRow = row
            userCol = col
            needit = False
      
        
        # Initialize variables
        arrows = 2
        alive = True

        #printBoard shows the hidden cave system
        def printBoard(r, c):
          out = []
          w = [['🔲' for _ in range(10)] for _ in range(7)]
          w[r][c] = '💂🏻‍♂️'
          for i in w:
            out.append(''.join(i[1:-1]))
          return '```' + '\n'.join(out[1:-1]) + '```'

        #endBoard shows the generated cave system
        def endBoard(r, c):
          out = []
          world[r][c] = '💀'
          for i in world:
            out.append(''.join(i[1:-1]))
          return '```' + '\n'.join(out[1:-1]).replace('w', '👹').replace('b', '🦇').replace('p', '⚫') + '```' #wumpus emoji in place of monster emoji
    
  
    
        brdmsg_embed = discord.Embed(title="Hunt for the Wumpus", description=f"{ctx.author.mention} has begun searching for the Wumpus.\nGood luck...", color=discord.Color.from_rgb(0, 0, 255))
    
        brdmsg_embed.add_field(name="Status", value=":grinning: `Now Loading...`", inline=False)
        brdmsg_embed.add_field(name="Arrows Remaining", value=f":bow_and_arrow: `{arrows}`", inline=True)
        brdmsg_embed.add_field(name="Danger Level", value=f"`{danger_level}`", inline=True)
        brdmsg_embed.add_field(name="", value=printBoard(userRow, userCol), inline=False)
    
        brdmsg_embed.set_thumbnail(url="https://i.imgur.com/0DdDso7.png") #wumpus PNG
      
        # brd_msg
        await ctx.respond(embed=brdmsg_embed, view=self.WumpusView(ctx, arrows, alive, world, userRow, userCol, danger_level, danger)) #update the initial board and now loading... status
      
  
    #Wumpus Buttons
    class WumpusView(discord.ui.View):
        def __init__(self, ctx, arrows, alive, world, userRow, userCol, danger_level, danger):
            super().__init__(timeout=10) #set the timeout
            self.ctx = ctx #intialize the context
            self.arrows = arrows
            self.alive = alive
            self.world = world
            self.userRow = userRow
            self.userCol = userCol
            self.danger_level = danger_level
            self.danger = danger

            asyncio.create_task(self.check_status()) #initialize the status based on initial location


        #printBoard shows the hidden cave system
        def printBoard(self, r, c):
          out = []
          w = [['🔲' for _ in range(10)] for _ in range(7)]
          w[r][c] = '💂🏻‍♂️'
          for i in w:
            out.append(''.join(i[1:-1]))
          return '```' + '\n'.join(out[1:-1]) + '```'


        #endBoard shows the generated cave system
        def endBoard(self, r, c):
          out = []
          self.world[r][c] = '💀'
          for i in self.world:
            out.append(''.join(i[1:-1]))
          return '```' + '\n'.join(out[1:-1]).replace('w', '👹').replace('b', '🦇').replace('p', '⚫') + '```'

      
        #endBoard shows the hidden cave system with the Wumpus dead
        def winnerBoard(self, r, c):
          out = []
          self.world[r][c] = '💂🏻‍♂️'
          for i in self.world:
            out.append(''.join(i[1:-1]))
          return '```' + '\n'.join(out[1:-1]).replace('w', '💀').replace('b', '🦇').replace('p', '⚫') + '```'


        #endBoard shows the hidden cave system with the user running
        def fledBoard(self, r, c):
          out = []
          self.world[r][c] = '🏃'
          for i in self.world:
            out.append(''.join(i[1:-1]))
          return '```' + '\n'.join(out[1:-1]).replace('w', '👹').replace('b', '🦇').replace('p', '⚫') + '```'


        #loading status
        async def surroundings(self):
            surroundings_embed = discord.Embed(title="Hunt for the Wumpus", description=f"{self.ctx.author.mention} has begun searching for the Wumpus.\nGood luck...", color=discord.Color.from_rgb(0, 0, 255))
      
            surroundings_embed.add_field(name="Status", value=":grinning: `Checking Surroundings...`", inline=False)
            surroundings_embed.add_field(name="Arrows Remaining", value=f":bow_and_arrow: `{self.arrows}`", inline=True)
            surroundings_embed.add_field(name="Danger Level", value=f"`{self.danger_level}`", inline=True)
            surroundings_embed.add_field(name="", value=self.printBoard(self.userRow, self.userCol), inline=False)
            surroundings_embed.set_thumbnail(url="https://i.imgur.com/0DdDso7.png") #wumpus PNG
            await self.message.edit(embed=surroundings_embed, view=self)
      

      
        # check user location and update status
        async def check_status(self):
            await asyncio.sleep(1) #mimic loading

            ####Game Over Statuses
            # If wumpus then user dies.
            if self.world[self.userRow][self.userCol] == 'w':
                description=f"{self.ctx.author.mention} stumbled upon an angry Wumpus and has become its dinner..."
                status = "👹 `Eaten`"
                board = self.endBoard(self.userRow, self.userCol)
                view=None
                gameover = True

            # If pit then user dies.
            elif self.world[self.userRow][self.userCol] == 'p':
                description=f'{self.ctx.author.mention} screams as they fall to their untimely death...'
                status = ":skull: `Deceased`"
                board = self.endBoard(self.userRow, self.userCol)
                view=None
                gameover = True

            # If bat then hyperspace.
            elif self.world[self.userRow][self.userCol] == 'b':
                description=f'{self.ctx.author.mention} was taken by a bat high into the sky never to be seen again...'
                status = ":bat: `Taken`"
                board = self.endBoard(self.userRow, self.userCol)
                view=None
                gameover = True


            ####Regular Statuses
            # Tells user if he is near the wumpus
            elif self.world[self.userRow - 1][self.userCol] == 'w' or self.world[self.userRow + 1][self.userCol] == 'w' or self.world[self.userRow][self.userCol - 1] == 'w' or \
                self.world[self.userRow][self.userCol + 1] == 'w':
                description = f"{self.ctx.author.mention} has begun searching for the Wumpus.\nGood luck..."
                status = ':nauseated_face:  `I smell a Wumpus near...`'
                board = self.printBoard(self.userRow, self.userCol) #regular board
                view=self
                gameover = False
          
            # Tells user if he is near a pit
            elif self.world[self.userRow - 1][self.userCol] == 'p' or self.world[self.userRow + 1][self.userCol] == 'p' or self.world[self.userRow][self.userCol - 1] == 'p' or \
                self.world[self.userRow][self.userCol + 1] == 'p':
                description = f"{self.ctx.author.mention} has begun searching for the Wumpus.\nGood luck..."
                status = ':dizzy_face:  `I feel a draft...`'
                board = self.printBoard(self.userRow, self.userCol) #regular board
                view=self
                gameover = False
          
            # Tell the user if he is near a bat
            elif self.world[self.userRow - 1][self.userCol] == 'b' or self.world[self.userRow + 1][self.userCol] == 'b' or self.world[self.userRow][self.userCol - 1] == 'b' or \
                self.world[self.userRow][self.userCol + 1] == 'b':
                description = f"{self.ctx.author.mention} has begun searching for the Wumpus.\nGood luck..."
                status =':rolling_eyes:  `I hear wings flapping...`'
                board = self.printBoard(self.userRow, self.userCol) #regular board
                view=self
                gameover = False
    
            #safe status (not a game over)
            else:
                description = f"{self.ctx.author.mention} has begun searching for the Wumpus.\nGood luck..."
                status =':grinning:  `Nothing suspicious here.`'
                board = self.printBoard(self.userRow, self.userCol) #regular board
                view=self
                gameover = False
      
      
            #Update Status according to user position
            status_embed = discord.Embed(title="Hunt for the Wumpus", description=description, color=discord.Color.from_rgb(0, 0, 255))
            status_embed.add_field(name="Status", value=status, inline=False)
            status_embed.add_field(name="Arrows Remaining", value=f":bow_and_arrow: `{self.arrows}`", inline=True)
            status_embed.add_field(name="Danger Level", value=f"`{self.danger_level}`", inline=True)
            status_embed.add_field(name="", value=board, inline=False)
            status_embed.set_thumbnail(url="https://i.imgur.com/0DdDso7.png") #wumpus PNG

            try:
                await self.message.edit(embed=status_embed, view=view)
            except AttributeError:
                pass

            return gameover



        #update winnings data
        def update_wins(self, winner, game_played):
            if winner and not winner.bot:
                #increase currency (🪙shillings) based on difficulty of game
                if self.danger == "safe":
                    shillings = 5
                elif self.danger == "challenging":
                    shillings = 10
                elif self.danger == "dangerous":
                    shillings = 25
                elif self.danger == "perilous":
                    shillings = 50
                    
              
                games = ["battleship", "connectfour", "mastermind", "rps", "tictactoe", "wumpus"]

                i = 0
                for game in games:
                    if game_played == game:
                        game_index = i
                        break

                    i = i + 1

                no_wins = [0 for _ in range(6)] #blank array of wins
                no_shillings = [0 for _ in range(6)] #blank array of shillings
              
                #update the number of wins for connectfour for the winner
                guild_wins = games_db[f"winnings_{self.ctx.guild.id}"]
                game_key = {"player_id": winner.id}
    
                player_record = guild_wins.find_one(game_key)
              
                if player_record is None:
                    no_wins[game_index] = 1
                    no_shillings[game_index] = shillings
                  
                    guild_wins.insert_one(
                      {
                        "server_id": self.ctx.guild.id,
                        "server_name": self.ctx.guild.name,
                        "player_name": winner.display_name,
                        "player_id": winner.id,
                        "games": games,
                        "wins": no_wins,
                        "shillings": no_shillings
                      }
                    )
                else:
                    wins_obtained = player_record["wins"]
                    shillings_obtained = player_record["shillings"]

                    wins_obtained[game_index] += 1
                    shillings_obtained[game_index] += shillings
                  
                    guild_wins.update_one(
                        game_key,
                        {"$set": {
                          "wins": wins_obtained,
                          "shillings": shillings_obtained
                          }
                        }
                    )


                #wallets for the guild
                guild_wallets = wallets_db[f"wallets_{self.ctx.guild.id}"]
                wallet_key = {"player_id": winner.id}
              
                wallet_record = guild_wallets.find_one(wallet_key)

                if wallet_record is None:
                    guild_wallets.insert_one(
                      {
                        "server_id": self.ctx.guild.id,
                        "server_name": self.ctx.guild.name,
                        "player_name": winner.display_name,
                        "player_id": winner.id,
                        "wallet": shillings
                      }
                    )
              
                else:
                    guild_wallets.update_one(
                        wallet_key,
                        {"$inc": {
                          "wallet": shillings
                          }
                        }
                    )


      
      
        # check arrow location
        async def check_arrow(self, arrowRow, arrowCol):
            # Check what is in the spaces that he fired into.
            lookup = self.world[arrowRow][arrowCol]

            if self.arrows > 0:
                #hit wumpus, victory
                if lookup == 'w':
                    status = ":trophy: `Victor`"
                    description = f'{self.ctx.author.mention} has slain the dreaded Wumpus and will be honored for all of eternity...'
                    board = self.winnerBoard(self.userRow, self.userCol)
                    game_played = "wumpus"
                    self.update_wins(self.ctx.author, game_played) #update the winnings for the game in the database
                    view = None
                    gameover = True
    
                #missed
                else:
                    status = ':bow_and_arrow: `Missed!`'
                    description = f"{self.ctx.author.mention} must decide where to shoot quickly..."
                    board = self.printBoard(self.userRow, self.userCol)
                    view = self
                    gameover = False


            #check if out of arrows and the user has not hit anything
            else:
                status = ":skull: `Deceased`"
                description = f'{self.ctx.author.mention} ran out of arrows and was slain by the dreaded Wumpus with no way to defend themself...'
                board = self.endBoard(self.userRow, self.userCol)
                view = None
                gameover = True


              
            arrowmsg_embed = discord.Embed(title="Hunt for the Wumpus", description=description, color=discord.Color.from_rgb(0, 0, 255))
  
            arrowmsg_embed.add_field(name="Status", value=status, inline=False)
            arrowmsg_embed.add_field(name="Arrows Remaining", value=f":bow_and_arrow: `{self.arrows}`", inline=True)
            arrowmsg_embed.add_field(name="Danger Level", value=f"`{self.danger_level}`", inline=True)
            arrowmsg_embed.add_field(name="", value=board, inline=False)
            arrowmsg_embed.set_thumbnail(url="https://i.imgur.com/0DdDso7.png") #wumpus PNG

            if gameover is True:
                for child in self.children:
                    child.disabled = True

                await self.message.edit(embed=arrowmsg_embed, view=view)
              
                self.stop()
            else:
                self.children[4].disabled = False #Enable the shoot button after using an arrow button for shooting direction (if missed)
              
                await self.message.edit(embed=arrowmsg_embed, view=view)

                #Change labels to shoot
                self.children[0].label = "Move Forward"
                self.children[1].label = "Move Backward"
                self.children[2].label = "Move Left"
                self.children[3].label = "Move Right"

                await self.check_status() #check status again
      

      
      

        # Handle timeout (e.g., if no moves are made within the specified timeout)
        async def on_timeout(self):
            for child in self.children: #disable all the buttons
                child.disabled = True

            endmsg_embed = discord.Embed(title="Hunt for the Wumpus", description=f"{self.ctx.author.mention} lost their way in the unending cave, never to be seen again...", color=discord.Color.from_rgb(0, 0, 255))
  
            endmsg_embed.add_field(name="Status", value=":skull: `Lost`", inline=False)
            endmsg_embed.add_field(name="Arrows Remaining", value=f":bow_and_arrow: `{self.arrows}`", inline=True)
            endmsg_embed.add_field(name="Danger Level", value=f"`{self.danger_level}`", inline=True)
            endmsg_embed.add_field(name="", value=self.endBoard(self.userRow, self.userCol), inline=False)
            endmsg_embed.set_thumbnail(url="https://i.imgur.com/0DdDso7.png") #wumpus PNG

            try:
                await self.message.edit(embed=endmsg_embed, view=None)
            except discord.errors.NotFound: #if message deleted before timeout
                pass

            self.stop()


        ####### Up Button
        @discord.ui.button(label="Move Forward", emoji="⬆", row=0, style=discord.ButtonStyle.primary)
        async def forward_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            #if shoot button is used
            if self.children[4].disabled is True:
                self.arrows -= 1 #remove 1 arrow

                arrowRow = self.userRow - 1
                arrowCol = self.userCol
            
                # Do not allow the arrow to fly off the face of the Earth
                if arrowRow == 0:
                    arrowRow = 1
                if arrowRow == 6:
                    arrowRow = 5
                if arrowCol == 0:
                    arrowCol = 1
                if arrowCol == 9:
                    arrowCol = 8

                await self.check_arrow(arrowRow, arrowCol)

            else:
                self.userRow -= 1
              
                # Do not allow user to walk off the face of the Earth.
                if self.userRow == 0:
                    self.userRow = 1
                elif self.userRow == 6:
                    self.userRow = 5
              
                if self.userCol == 9:
                    self.userCol = 8
                elif self.userCol == 0:
                    self.userCol = 1
    
                #loading status
                if self.alive:
                    await self.surroundings()
    
              
                status = await self.check_status() #update the user status based on location (this returns a True or false value based on location)
    
                #if dead, end interaction (retrieved from check_status function)
                if status is True:
                    for child in self.children:
                        child.disabled = True
    
                    self.stop()

      

        ####### Down Button
        @discord.ui.button(label="Move Backward", emoji="⬇", row=0, style=discord.ButtonStyle.primary)
        async def back_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return


            #if shoot button is used
            if self.children[4].disabled is True:
                self.arrows -= 1 #remove 1 arrow
              
                arrowRow = self.userRow + 1
                arrowCol = self.userCol
            
                # Do not allow the arrow to fly off the face of the Earth
                if arrowRow == 0:
                    arrowRow = 1
                if arrowRow == 6:
                    arrowRow = 5
                if arrowCol == 0:
                    arrowCol = 1
                if arrowCol == 9:
                    arrowCol = 8

                await self.check_arrow(arrowRow, arrowCol)
            else:
                self.userRow += 1
              
                # Do not allow user to walk off the face of the Earth.
                if self.userRow == 0:
                    self.userRow = 1
                elif self.userRow == 6:
                    self.userRow = 5
              
                if self.userCol == 9:
                    self.userCol = 8
                elif self.userCol == 0:
                    self.userCol = 1
    
                #loading status
                if self.alive:
                    await self.surroundings()
    
              
                status = await self.check_status() #update the user status based on location (this returns a True or false value based on location)
    
                #if dead, end interaction (retrieved from check_status function)
                if status is True:
                    for child in self.children:
                        child.disabled = True
    
                    self.stop()
      
      
      
      
        ####### Left Button
        @discord.ui.button(label="Move Left", emoji="⬅", row=1, style=discord.ButtonStyle.primary)
        async def left_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            #if shoot button is used
            if self.children[4].disabled is True:
                self.arrows -= 1 #remove 1 arrow
              
                arrowRow = self.userRow
                arrowCol = self.userCol - 1
            
                # Do not allow the arrow to fly off the face of the Earth
                if arrowRow == 0:
                    arrowRow = 1
                if arrowRow == 6:
                    arrowRow = 5
                if arrowCol == 0:
                    arrowCol = 1
                if arrowCol == 9:
                    arrowCol = 8

                await self.check_arrow(arrowRow, arrowCol)
            else:
                self.userCol -= 1
              
                # Do not allow user to walk off the face of the Earth.
                if self.userRow == 0:
                    self.userRow = 1
                elif self.userRow == 6:
                    self.userRow = 5
              
                if self.userCol == 9:
                    self.userCol = 8
                elif self.userCol == 0:
                    self.userCol = 1
    
                #loading status
                if self.alive:
                    await self.surroundings()
    
                status = await self.check_status() #update the user status based on location (this returns a True or false value based on location)
    
                #if dead, end interaction (retrieved from check_status function)
                if status is True:
                    for child in self.children:
                        child.disabled = True
    
                    self.stop()



      
        ####### Right Button
        @discord.ui.button(label="Move Right", emoji="➡", row=1, style=discord.ButtonStyle.primary)
        async def right_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            #if shoot button is used
            if self.children[4].disabled is True:
                self.arrows -= 1 #remove 1 arrow
              
                arrowRow = self.userRow
                arrowCol = self.userCol + 1
            
                # Do not allow the arrow to fly off the face of the Earth
                if arrowRow == 0:
                    arrowRow = 1
                if arrowRow == 6:
                    arrowRow = 5
                if arrowCol == 0:
                    arrowCol = 1
                if arrowCol == 9:
                    arrowCol = 8

                await self.check_arrow(arrowRow, arrowCol)
            else:
                self.userCol += 1
              
                # Do not allow user to walk off the face of the Earth.
                if self.userRow == 0:
                    self.userRow = 1
                elif self.userRow == 6:
                    self.userRow = 5
              
                if self.userCol == 9:
                    self.userCol = 8
                elif self.userCol == 0:
                    self.userCol = 1
    
                #loading status
                if self.alive:
                    await self.surroundings()
    
                status = await self.check_status() #update the user status based on location (this returns a True or false value based on location)
    
                #if dead, end interaction (retrieved from check_status function)
                if status is True:
                    for child in self.children:
                        child.disabled = True
    
                    self.stop()
      

        ####### Shoot Button
        @discord.ui.button(label="Shoot", emoji="🏹", row=2, style=discord.ButtonStyle.secondary)
        async def shoot_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            button.disabled = True #disable the button (until one of the arrow buttons is used)

          
            shootmsg_embed = discord.Embed(title="Hunt for the Wumpus", description=f"{self.ctx.author.mention} must decide where to shoot quickly...", color=discord.Color.from_rgb(0, 0, 255))
            shootmsg_embed.add_field(name="Status", value=":bow_and_arrow: `Shooting`", inline=False)
            shootmsg_embed.add_field(name="Arrows Remaining", value=f":bow_and_arrow: `{self.arrows}`", inline=True)
            shootmsg_embed.add_field(name="Danger Level", value=f"`{self.danger_level}`", inline=True)
            shootmsg_embed.add_field(name="", value=self.printBoard(self.userRow, self.userCol), inline=False)
            shootmsg_embed.set_thumbnail(url="https://i.imgur.com/0DdDso7.png") #wumpus PNG

            #Change labels to shoot
            self.children[0].label = "Shoot Forward"
            self.children[1].label = "Shoot Backward"
            self.children[2].label = "Shoot Left"
            self.children[3].label = "Shoot Right"
          
            await self.message.edit(embed=shootmsg_embed, view=self)
      


      
        ####### Flee Button
        @discord.ui.button(label="Flee", emoji="🏃", row=2, style=discord.ButtonStyle.danger)
        async def flee_button_callback(self, button, interaction):
            await interaction.response.defer()

            if interaction.user.id != self.ctx.author.id:
                return

            for child in self.children: #disable all the buttons
                child.disabled = True
          
            endmsg_embed = discord.Embed(title="Hunt for the Wumpus", description=f'{self.ctx.author.mention} stopped searching for the dreaded Wumpus...\nShall someone ever slay this dreaded beast? 👹', color=discord.Color.from_rgb(0, 0, 255))
    
            endmsg_embed.add_field(name="Status", value=":dash: `Fled`", inline=False)
            endmsg_embed.add_field(name="Arrows Remaining", value=f":bow_and_arrow: `{self.arrows}`", inline=True)
            endmsg_embed.add_field(name="Danger Level", value=f"`{self.danger_level}`", inline=True)
            endmsg_embed.add_field(name="", value=self.fledBoard(self.userRow, self.userCol), inline=False)
            endmsg_embed.set_thumbnail(url="https://i.imgur.com/0DdDso7.png") #wumpus PNG
          
            await self.message.edit(embed=endmsg_embed, view=None)

            self.stop()

  
  
####################################WUMPUS#########################################




  


##################################CONNECTFOUR#####################################
    @discord.slash_command(
        name="connectfour",
        description="Challenge the automaton or another member of the guild to a game of Connect Four.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def connectfour(self, ctx, player2: Option(discord.Member, name="player2", description="Opponent for the game."), symbol: Option(str, name="symbol", description="Symbol you would like to use for the game. (Default: 🔴)", choices=["🔴", "🟡"], required=False, default="🔴"), difficulty: Option(str, name="difficulty", description="Difficulty setting when facing the automaton. (Default: 🟨 Medium)", required=False, default=None, choices=["🟩 Easy", "🟨 Medium", "🟥 Hard"])):
    
        #check the member that is used
        #cannot play against self
        if player2.id == ctx.author.id:
            await ctx.respond(f"Apologies {ctx.author.mention},\nYou are unable to play against yourself in Connect Four.\n*Please try again using a different member of {ctx.guild.name}.*", ephemeral=True)
            return
    
        #play against Lord Bottington
        elif player2.id == self.bot.user.id:
            player2_bot = True
          
        #cannot play against a bot that is not Lord Bottington
        elif player2.bot:
            await ctx.respond(f"Apologies {ctx.author.mention},\nYou cannot play against *{player2.display_name}* in Connect Four. You may only face myself or another member of {ctx.guild.name}.\n*Please try again.*", ephemeral=True)
            return
    
        else:
            player2_bot = False
    
        symbols = ["🔴", "🟡"]
      
        player1emoji = symbol
        player2emoji = next(emoji for emoji in symbols if emoji != symbol) #assign the other symbol to player 2
    
        #difficulty
        difficulty_dict = {
          "🟩 Easy": "easy",
          "🟨 Medium": "medium",
          "🟥 Hard": "hard"
        }
    
        if difficulty:
            bot_difficulty = difficulty_dict[difficulty]
        else:
            difficulty = "🟨 Medium"
            bot_difficulty = "medium"
    
      
        c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {ctx.guild.name}\nA game of Connect Four has commenced.\nSelect the desired column using the corresponding button.", color = discord.Color.from_rgb(0, 0, 255))
    
        if player2_bot is True:
            c4_embed.add_field(name="Difficulty", value=difficulty, inline=False)
      
        c4_embed.add_field(name=f"{player1emoji} Player 1", value=ctx.author.mention)
        c4_embed.add_field(name=f"{player2emoji} Player 2", value=player2.mention)
    
        c4_embed.add_field(name="", value="```1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n⚪⚪⚪⚪⚪⚪⚪\n⚪⚪⚪⚪⚪⚪⚪\n⚪⚪⚪⚪⚪⚪⚪\n⚪⚪⚪⚪⚪⚪⚪\n⚪⚪⚪⚪⚪⚪⚪\n⚪⚪⚪⚪⚪⚪⚪```", inline=False)
    
        c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif") #c4 GIF
    
        c4_embed.set_footer(text=f"Current Turn: {player1emoji} {ctx.author.display_name}")
    
        await ctx.respond(embed=c4_embed, view=self.C4View(ctx, player1emoji, player2emoji, ctx.author.id, player2.id, player2_bot, ctx.author, player2, difficulty, bot_difficulty))
    
    
    
    
    
    class C4View(discord.ui.View):
        def __init__(self, ctx, player1emoji, player2emoji, player1id, player2id, player2_bot, player1, player2, difficulty, bot_difficulty):
            super().__init__(timeout=120) #set the timeout
            self.ctx = ctx #intialize the context
            self.player1emoji = player1emoji #initialize player 1 emoji
            self.player2emoji = player2emoji #initialize player 2 emoji
            self.board = [['⚪'] * 7 for _ in range(6)]  # Initialize the Connect Four board
            self.player1id = player1id #initialize player 1's ID
            self.player2id = player2id #initialize player 2's ID
            self.current_turn = self.player1id #initialize the current turn (player 1 goes first)
            self.player2_bot = player2_bot #check if player 2 is a bot
            self.player1 = player1 #initialize the player 1 object (for mentions)
            self.player2 = player2 #initialize the player 2 object (for mentions)
            self.difficulty = difficulty #initialize the difficulty (with emojis)
            self.bot_difficulty = bot_difficulty #initialize the difficulty (without emojis)
    
            #initialize the button clicks to 0
            self.button1clicks = 0
            self.button2clicks = 0
            self.button3clicks = 0
            self.button4clicks = 0
            self.button5clicks = 0
            self.button6clicks = 0
            self.button7clicks = 0
            
      
        #function to switch the player's turn
        def toggle_turn(self):
            if self.current_turn == self.player1id:
                self.current_turn = self.player2id  # Switch to player 2's turn
            else:
                self.current_turn = self.player1id  # Switch to player 1's turn
    
    
        # Handle timeout (e.g., if no moves are made within the specified timeout)
        async def on_timeout(self):
            for child in self.children: #disable all the buttons
                child.disabled = True
    
            # Update the embed
            c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {self.ctx.guild.name}\nA game of Connect Four has ended...\nOne or more of the players did not interact in time.", color=discord.Color.from_rgb(0, 0, 255))
    
            if self.player2_bot is True:
                c4_embed.add_field(name="Difficulty", value=self.difficulty, inline=False)
          
            c4_embed.add_field(name=f"{self.player1emoji} Player 1", value=self.player1.mention)
            c4_embed.add_field(name=f"{self.player2emoji} Player 2", value=self.player2.mention)
            c4_embed.add_field(name="", value=self.format_board(self.board), inline=False)
            c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")  # c4 GIF

            try:
                await self.message.edit(embed=c4_embed, view=None)
            except discord.errors.NotFound: #if message deleted before timeout
                pass
          
            self.stop() #stop accepting button clicks
    
    
        async def make_bot_move(self, interaction):
            # Bot's turn and player 2 is a bot
            available_columns = [col for col in range(7) if self.board[0][col] == '⚪']
    
            #Easy Mode
            if self.bot_difficulty == "easy":
                if random.random() < 0.5:  # 50% chance of making a random move
                    column = random.choice(available_columns)
    
                else:
                    column = self.find_blocking_move(available_columns)
                    if column is None:
                        column = self.find_winning_move(available_columns)
                    if column is None:
                        column = random.choice(available_columns)
      
            #Medium Mode
            elif self.bot_difficulty == "medium":
                if random.random() < 0.25:  # 25% chance of making a random move
                    column = random.choice(available_columns)
    
                else:
                    column = self.find_blocking_move(available_columns)
                    if column is None:
                        column = self.find_winning_move(available_columns)
                    if column is None:
                        column = random.choice(available_columns)
      
            #Hard Mode (no chance of random moves)
            elif self.bot_difficulty == "hard":
                column = self.find_blocking_move(available_columns)
                if column is None:
                    column = self.find_winning_move(available_columns)
                if column is None:
                    column = random.choice(available_columns)
      
    
          
            emoji = self.player2emoji #get the correct emoji
      
            if column == 0:
                self.button1clicks += 1
    
                if self.button1clicks == 6: #column is full, disable button
                    self.children[column].disabled = True
            elif column == 1:
                self.button2clicks += 1
    
                if self.button2clicks == 6: #column is full, disable button
                    self.children[column].disabled = True
            elif column == 2:
                self.button3clicks += 1
    
                if self.button3clicks == 6: #column is full, disable button
                    self.children[column].disabled = True
            elif column == 3:
                self.button4clicks += 1
    
                if self.button4clicks == 6: #column is full, disable button
                    self.children[column].disabled = True
            elif column == 4:
                self.button5clicks += 1
    
                if self.button5clicks == 6: #column is full, disable button
                    self.children[column].disabled = True
            elif column == 5:
                self.button6clicks += 1
    
                if self.button6clicks == 6: #column is full, disable button
                    self.children[column].disabled = True
            elif column == 6:
                self.button7clicks += 1
    
                if self.button7clicks == 6: #column is full, disable button
                    self.children[column].disabled = True
    
          
        
            # Update the board
            for row in range(5, -1, -1):
                if self.board[row][column] == '⚪':
                    self.board[row][column] = emoji
                    break
        
            # Check for a winner
            winning_symbol = self.check_winner(self.board)
            if winning_symbol:
                for child in self.children: #disable the buttons
                    child.disabled = True
              
                #check what the winning symbol is and assign a player object to it (for mentions)
                if winning_symbol == self.player1emoji:
                    winner = self.player1
                else:
                    winner = self.player2
      
                #check for a tie
                if winning_symbol == "tie":
                    winner_message = "It is a tie!\nUnfortunately, nobody won this round."
                else:
                    winner_message = f"{winning_symbol} {winner.mention} won this round.\nCongratulations, good sir!"
              
                # Update the winner embed
                c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {self.ctx.guild.name}\nA game of Connect Four has ended...\n\n{winner_message}", color=discord.Color.from_rgb(0, 0, 255))
    
                if self.player2_bot is True:
                    c4_embed.add_field(name="Difficulty", value=self.difficulty, inline=False)
              
                c4_embed.add_field(name=f"{self.player1emoji} Player 1", value=self.player1.mention)
                c4_embed.add_field(name=f"{self.player2emoji} Player 2", value=self.player2.mention)
                c4_embed.add_field(name="", value=self.format_board(self.board), inline=False)
                c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")  # c4 GIF
            
                await self.message.edit(embed=c4_embed, view=None)
      
                self.stop() #stop accepting interactions
                return
          
          
            self.toggle_turn() #toggle the turn
        
            # Update the embed
            c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {self.ctx.guild.name}\nA game of Connect Four has commenced.\nSelect the desired column using the corresponding button.", color=discord.Color.from_rgb(0, 0, 255))
    
            if self.player2_bot is True:
                c4_embed.add_field(name="Difficulty", value=self.difficulty, inline=False)
          
            c4_embed.add_field(name=f"{self.player1emoji} Player 1", value=self.player1.mention)
            c4_embed.add_field(name=f"{self.player2emoji} Player 2", value=self.player2.mention)
            c4_embed.add_field(name="", value=self.format_board(self.board), inline=False)
            c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")  # c4 GIF
          
            if self.current_turn == self.player1id:
                footer = f"Current Turn: {self.player1emoji} {self.player1.display_name}"
            else:
                footer = f"Current Turn: {self.player2emoji} {self.player2.display_name}"
          
            c4_embed.set_footer(text=footer)
        
            await self.message.edit(embed=c4_embed, view=self)
    
      
        #Winning Move
        def find_winning_move(self, columns):
            for column in range(7):
                temp_board = [row[:] for row in self.board]
                for row in range(5, -1, -1):
                    if temp_board[row][column] == '⚪':
                        temp_board[row][column] = self.player2emoji
                        if self.check_winner(temp_board) == self.player2emoji:
                            return column
                        break
            return None
          
    
        #Blocking Move
        def find_blocking_move(self, columns):
            for column in range(7):
                temp_board = [row[:] for row in self.board]
                for row in range(5, -1, -1):
                    if temp_board[row][column] == '⚪':
                        temp_board[row][column] = self.player1emoji
                        if self.check_winner(temp_board) == self.player1emoji:
                            return column
                        break
            return None
    
      
      
      
        def check_winner(self, board):
            # Check for horizontal wins
            for row in range(6):
                for col in range(4):
                    if (
                        board[row][col] != '⚪' and
                        board[row][col] == board[row][col+1] == board[row][col+2] == board[row][col+3]
                    ):
                        return board[row][col]  # Return the winning symbol
        
            # Check for vertical wins
            for row in range(3):
                for col in range(7):
                    if (
                        board[row][col] != '⚪' and
                        board[row][col] == board[row+1][col] == board[row+2][col] == board[row+3][col]
                    ):
                        return board[row][col]  # Return the winning symbol
        
            # Check for diagonal wins (top-left to bottom-right)
            for row in range(3):
                for col in range(4):
                    if (
                        board[row][col] != '⚪' and
                        board[row][col] == board[row+1][col+1] == board[row+2][col+2] == board[row+3][col+3]
                    ):
                        return board[row][col]  # Return the winning symbol
        
            # Check for diagonal wins (bottom-left to top-right)
            for row in range(3, 6):
                for col in range(4):
                    if (
                        board[row][col] != '⚪' and
                        board[row][col] == board[row-1][col+1] == board[row-2][col+2] == board[row-3][col+3]
                    ):
                        return board[row][col]  # Return the winning symbol
    
            # Check for a tie (all positions filled)
            if all(board[row][col] != '⚪' for row in range(6) for col in range(7)):
                return 'tie'  # Return 'Tie' if all positions are filled
    
        
            return None  # No winner
    
    
      
        def format_board(self, board):
            # Convert the board into a formatted string
            formatted = ""
            for row in board:
                formatted += "".join(row) + "\n"
    
            formatted = f"```1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n{formatted}```"
            return formatted



      
        def update_wins(self, winner, game_played):
            #only update winnings data if there is not a tie and the winner is not Lord Bottington
            if winner and not winner.bot:
                #increase currency (🪙shillings) based on who the player is facing and the difficulty when facing Lord Bottington
                if self.player2.bot and self.bot_difficulty == "easy":
                    shillings = 2
                elif self.player2.bot and self.bot_difficulty == "medium":
                    shillings = 5
                elif self.player2.bot and self.bot_difficulty == "hard":
                    shillings = 10
                elif not self.player2.bot: #when facing regular player
                    shillings = 10

                print(shillings)
              
                games = ["battleship", "connectfour", "mastermind", "rps", "tictactoe", "wumpus"]

                i = 0
                for game in games:
                    if game_played == game:
                        game_index = i
                        break

                    i = i + 1

                no_wins = [0 for _ in range(6)] #blank array of wins
                no_shillings = [0 for _ in range(6)] #blank array of shillings
              
                #update the number of wins for connectfour for the winner
                guild_wins = games_db[f"winnings_{self.ctx.guild.id}"]
                game_key = {"player_id": winner.id}
    
                player_record = guild_wins.find_one(game_key)
              
                if player_record is None:
                    no_wins[game_index] = 1
                    no_shillings[game_index] = shillings
                  
                    guild_wins.insert_one(
                      {
                        "server_id": self.ctx.guild.id,
                        "server_name": self.ctx.guild.name,
                        "player_name": winner.display_name,
                        "player_id": winner.id,
                        "games": games,
                        "wins": no_wins,
                        "shillings": no_shillings
                      }
                    )
                else:
                    wins_obtained = player_record["wins"]
                    shillings_obtained = player_record["shillings"]

                    wins_obtained[game_index] += 1
                    shillings_obtained[game_index] += shillings
                  
                    guild_wins.update_one(
                        game_key,
                        {"$set": {
                          "wins": wins_obtained,
                          "shillings": shillings_obtained
                          }
                        }
                    )
                  

                #wallets for the guild
                guild_wallets = wallets_db[f"wallets_{self.ctx.guild.id}"]
                wallet_key = {"player_id": winner.id}
              
                wallet_record = guild_wallets.find_one(wallet_key)

                if wallet_record is None:
                    guild_wallets.insert_one(
                      {
                        "server_id": self.ctx.guild.id,
                        "server_name": self.ctx.guild.name,
                        "player_name": winner.display_name,
                        "player_id": winner.id,
                        "wallet": shillings
                      }
                    )
              
                else:
                    guild_wallets.update_one(
                        wallet_key,
                        {"$inc": {
                          "wallet": shillings
                          }
                        }
                    )


      
    
        ###### First column button
        @discord.ui.button(emoji="1️⃣", style=discord.ButtonStyle.primary)
        async def first_button_callback(self, button, interaction):
            await interaction.response.defer()
        
            if self.current_turn != interaction.user.id:
                return
        
            # Get the correct emoji for the interaction
            if interaction.user.id == self.player1id:
                emoji = self.player1emoji
            else:
                emoji = self.player2emoji
    
          
            self.button1clicks += 1  # Increment the click count for button 1
          
            if self.button1clicks == 6: #column is full, disable button
                button.disabled = True
    
          
            column = 0  # Update this based on the button clicked
        
            # Update the board
            for row in range(5, -1, -1):
                if self.board[row][column] == '⚪':
                    self.board[row][column] = emoji
                    break
        
            # Check for a winner
            winning_symbol = self.check_winner(self.board)
            if winning_symbol:
                for child in self.children: #disable the buttons
                    child.disabled = True
              
                #check what the winning symbol is and assign a player object to it (for mentions)
                if winning_symbol == self.player1emoji:
                    winner = self.player1
                else:
                    winner = self.player2

                game_played = "connectfour"
                self.update_wins(winner, game_played) #update the games_db with wins and shillings
              
                #check for a tie
                if winning_symbol == "tie":
                    winner_message = "It is a tie!\nUnfortunately, nobody won this round."
                else:
                    winner_message = f"{winning_symbol} {winner.mention} won this round.\nCongratulations, good sir!"
              
                # Update the winner embed
                c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {self.ctx.guild.name}\nA game of Connect Four has ended...\n\n{winner_message}", color=discord.Color.from_rgb(0, 0, 255))
    
                if self.player2_bot is True:
                    c4_embed.add_field(name="Difficulty", value=self.difficulty, inline=False)
              
                c4_embed.add_field(name=f"{self.player1emoji} Player 1", value=self.player1.mention)
                c4_embed.add_field(name=f"{self.player2emoji} Player 2", value=self.player2.mention)
                c4_embed.add_field(name="", value=self.format_board(self.board), inline=False)
                c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")  # c4 GIF
            
                await self.message.edit(embed=c4_embed, view=None)
    
                self.stop() #stop accepting interactions
                return
          
          
            self.toggle_turn() #toggle the turn
    
        
            # Update the embed
            c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {self.ctx.guild.name}\nA game of Connect Four has commenced.\nSelect the desired column using the corresponding button.", color=discord.Color.from_rgb(0, 0, 255))
    
            if self.player2_bot is True:
                c4_embed.add_field(name="Difficulty", value=self.difficulty, inline=False)
          
            c4_embed.add_field(name=f"{self.player1emoji} Player 1", value=self.player1.mention)
            c4_embed.add_field(name=f"{self.player2emoji} Player 2", value=self.player2.mention)
            c4_embed.add_field(name="", value=self.format_board(self.board), inline=False)
            c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")  # c4 GIF
          
            if self.current_turn == self.player1id:
                footer = f"Current Turn: {self.player1emoji} {self.player1.display_name}"
            else:
                footer = f"Current Turn: {self.player2emoji} {self.player2.display_name}"
          
            c4_embed.set_footer(text=footer)
        
            await self.message.edit(embed=c4_embed, view=self)
    
            # Make the bot move (if set)
            if self.player2_bot is True:
                await asyncio.sleep(2)
                await self.make_bot_move(interaction)
    
            
    
        ####### second column button
        @discord.ui.button(emoji="2️⃣", style=discord.ButtonStyle.primary)
        async def second_button_callback(self, button, interaction):
            await interaction.response.defer()
        
            if self.current_turn != interaction.user.id:
                return
        
            # Get the correct emoji for the interaction
            if interaction.user.id == self.player1id:
                emoji = self.player1emoji
            else:
                emoji = self.player2emoji
    
          
            self.button2clicks += 1  # Increment the click count for button 1
          
            if self.button2clicks == 6: #column is full, disable button
                button.disabled = True
    
          
            column = 1  # Update this based on the button clicked
        
            # Update the board
            for row in range(5, -1, -1):
                if self.board[row][column] == '⚪':
                    self.board[row][column] = emoji
                    break
        
            # Check for a winner
            winning_symbol = self.check_winner(self.board)
            if winning_symbol:
                for child in self.children: #disable the buttons
                    child.disabled = True
              
                #check what the winning symbol is and assign a player object to it (for mentions)
                if winning_symbol == self.player1emoji:
                    winner = self.player1
                else:
                    winner = self.player2
                  
                #check for a tie
                if winning_symbol == "tie":
                    winner_message = "It is a tie!\nUnfortunately, nobody won this round."
                else:
                    winner_message = f"{winning_symbol} {winner.mention} won this round.\nCongratulations, good sir!"
              
                # Update the winner embed
                c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {self.ctx.guild.name}\nA game of Connect Four has ended...\n\n{winner_message}", color=discord.Color.from_rgb(0, 0, 255))
    
                if self.player2_bot is True:
                    c4_embed.add_field(name="Difficulty", value=self.difficulty, inline=False)
              
                c4_embed.add_field(name=f"{self.player1emoji} Player 1", value=self.player1.mention)
                c4_embed.add_field(name=f"{self.player2emoji} Player 2", value=self.player2.mention)
                c4_embed.add_field(name="", value=self.format_board(self.board), inline=False)
                c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")  # c4 GIF
            
                await self.message.edit(embed=c4_embed, view=None)
    
                self.stop() #stop accepting interactions
                return
          
                
            
            self.toggle_turn() #toggle the turn
        
            # Update the embed
            c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {self.ctx.guild.name}\nA game of Connect Four has commenced.\nSelect the desired column using the corresponding button.", color=discord.Color.from_rgb(0, 0, 255))
    
            if self.player2_bot is True:
                c4_embed.add_field(name="Difficulty", value=self.difficulty, inline=False)
          
            c4_embed.add_field(name=f"{self.player1emoji} Player 1", value=self.player1.mention)
            c4_embed.add_field(name=f"{self.player2emoji} Player 2", value=self.player2.mention)
            c4_embed.add_field(name="", value=self.format_board(self.board), inline=False)
            c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")  # c4 GIF
    
            if self.current_turn == self.player1id:
                footer = f"Current Turn: {self.player1emoji} {self.player1.display_name}"
            else:
                footer = f"Current Turn: {self.player2emoji} {self.player2.display_name}"
          
            c4_embed.set_footer(text=footer)
        
            await self.message.edit(embed=c4_embed, view=self)
    
            # Make the bot move (if set)
            if self.player2_bot is True:
                await asyncio.sleep(2)
                await self.make_bot_move(interaction)
          
    
        ###### third column button
        @discord.ui.button(emoji="3️⃣", style=discord.ButtonStyle.primary)
        async def third_button_callback(self, button, interaction):
            await interaction.response.defer()
        
            if self.current_turn != interaction.user.id:
                return
        
            # Get the correct emoji for the interaction
            if interaction.user.id == self.player1id:
                emoji = self.player1emoji
            else:
                emoji = self.player2emoji
    
          
            self.button3clicks += 1  # Increment the click count for button 1
          
            if self.button3clicks == 6: #column is full, disable button
                button.disabled = True
    
          
            column = 2  # Update this based on the button clicked
        
            # Update the board
            for row in range(5, -1, -1):
                if self.board[row][column] == '⚪':
                    self.board[row][column] = emoji
                    break
        
            # Check for a winner
            winning_symbol = self.check_winner(self.board)
            if winning_symbol:
                for child in self.children: #disable the buttons
                    child.disabled = True
              
                #check what the winning symbol is and assign a player object to it (for mentions)
                if winning_symbol == self.player1emoji:
                    winner = self.player1
                else:
                    winner = self.player2
    
                #check for a tie
                if winning_symbol == "tie":
                    winner_message = "It is a tie!\nUnfortunately, nobody won this round."
                else:
                    winner_message = f"{winning_symbol} {winner.mention} won this round.\nCongratulations, good sir!"
              
                # Update the winner embed
                c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {self.ctx.guild.name}\nA game of Connect Four has ended...\n\n{winner_message}", color=discord.Color.from_rgb(0, 0, 255))
    
                if self.player2_bot is True:
                    c4_embed.add_field(name="Difficulty", value=self.difficulty, inline=False)
              
                c4_embed.add_field(name=f"{self.player1emoji} Player 1", value=self.player1.mention)
                c4_embed.add_field(name=f"{self.player2emoji} Player 2", value=self.player2.mention)
                c4_embed.add_field(name="", value=self.format_board(self.board), inline=False)
                c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")  # c4 GIF
            
                await self.message.edit(embed=c4_embed, view=None)
    
                self.stop() #stop accepting interactions
                return
          
                
            
            self.toggle_turn() #toggle the turn
        
            # Update the embed
            c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {self.ctx.guild.name}\nA game of Connect Four has commenced.\nSelect the desired column using the corresponding button.", color=discord.Color.from_rgb(0, 0, 255))
    
            if self.player2_bot is True:
                c4_embed.add_field(name="Difficulty", value=self.difficulty, inline=False)
          
            c4_embed.add_field(name=f"{self.player1emoji} Player 1", value=self.player1.mention)
            c4_embed.add_field(name=f"{self.player2emoji} Player 2", value=self.player2.mention)
            c4_embed.add_field(name="", value=self.format_board(self.board), inline=False)
            c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")  # c4 GIF
    
            if self.current_turn == self.player1id:
                footer = f"Current Turn: {self.player1emoji} {self.player1.display_name}"
            else:
                footer = f"Current Turn: {self.player2emoji} {self.player2.display_name}"
          
            c4_embed.set_footer(text=footer)
        
            await self.message.edit(embed=c4_embed, view=self)
    
            # Make the bot move (if set)
            if self.player2_bot is True:
                await asyncio.sleep(2)
                await self.make_bot_move(interaction)
    
    
      
        ###### fourth column button
        @discord.ui.button(emoji="4️⃣", style=discord.ButtonStyle.primary)
        async def fourth_button_callback(self, button, interaction):
            await interaction.response.defer()
        
            if self.current_turn != interaction.user.id:
                return
        
            # Get the correct emoji for the interaction
            if interaction.user.id == self.player1id:
                emoji = self.player1emoji
            else:
                emoji = self.player2emoji
    
          
            self.button4clicks += 1  # Increment the click count for button 1
          
            if self.button4clicks == 6: #column is full, disable button
                button.disabled = True
    
          
            column = 3  # Update this based on the button clicked
        
            # Update the board
            for row in range(5, -1, -1):
                if self.board[row][column] == '⚪':
                    self.board[row][column] = emoji
                    break
        
            # Check for a winner
            winning_symbol = self.check_winner(self.board)
            if winning_symbol:
                for child in self.children: #disable the buttons
                    child.disabled = True
              
                #check what the winning symbol is and assign a player object to it (for mentions)
                if winning_symbol == self.player1emoji:
                    winner = self.player1
                else:
                    winner = self.player2
    
                #check for a tie
                if winning_symbol == "tie":
                    winner_message = "It is a tie!\nUnfortunately, nobody won this round."
                else:
                    winner_message = f"{winning_symbol} {winner.mention} won this round.\nCongratulations, good sir!"
              
                # Update the winner embed
                c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {self.ctx.guild.name}\nA game of Connect Four has ended...\n\n{winner_message}", color=discord.Color.from_rgb(0, 0, 255))
    
                if self.player2_bot is True:
                    c4_embed.add_field(name="Difficulty", value=self.difficulty, inline=False)
              
                c4_embed.add_field(name=f"{self.player1emoji} Player 1", value=self.player1.mention)
                c4_embed.add_field(name=f"{self.player2emoji} Player 2", value=self.player2.mention)
                c4_embed.add_field(name="", value=self.format_board(self.board), inline=False)
                c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")  # c4 GIF
            
                await self.message.edit(embed=c4_embed, view=None)
    
                self.stop() #stop accepting interactions
                return
          
                
            
            self.toggle_turn() #toggle the turn
        
            # Update the embed
            c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {self.ctx.guild.name}\nA game of Connect Four has commenced.\nSelect the desired column using the corresponding button.", color=discord.Color.from_rgb(0, 0, 255))
    
            if self.player2_bot is True:
                c4_embed.add_field(name="Difficulty", value=self.difficulty, inline=False)
          
            c4_embed.add_field(name=f"{self.player1emoji} Player 1", value=self.player1.mention)
            c4_embed.add_field(name=f"{self.player2emoji} Player 2", value=self.player2.mention)
            c4_embed.add_field(name="", value=self.format_board(self.board), inline=False)
            c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")  # c4 GIF
    
    
            if self.current_turn == self.player1id:
                footer = f"Current Turn: {self.player1emoji} {self.player1.display_name}"
            else:
                footer = f"Current Turn: {self.player2emoji} {self.player2.display_name}"
          
            c4_embed.set_footer(text=footer)
        
            await self.message.edit(embed=c4_embed, view=self)
    
            # Make the bot move (if set)
            if self.player2_bot is True:
                await asyncio.sleep(2)
                await self.make_bot_move(interaction)
    
    
    
      
        ###### fifth column button
        @discord.ui.button(emoji="5️⃣", style=discord.ButtonStyle.primary)
        async def fifth_button_callback(self, button, interaction):
            await interaction.response.defer()
        
            if self.current_turn != interaction.user.id:
                return
        
            # Get the correct emoji for the interaction
            if interaction.user.id == self.player1id:
                emoji = self.player1emoji
            else:
                emoji = self.player2emoji
    
          
            self.button5clicks += 1  # Increment the click count for button 1
          
            if self.button5clicks == 6: #column is full, disable button
                button.disabled = True
    
          
            column = 4  # Update this based on the button clicked
        
            # Update the board
            for row in range(5, -1, -1):
                if self.board[row][column] == '⚪':
                    self.board[row][column] = emoji
                    break
        
            # Check for a winner
            winning_symbol = self.check_winner(self.board)
            if winning_symbol:
                for child in self.children: #disable the buttons
                    child.disabled = True
              
                #check what the winning symbol is and assign a player object to it (for mentions)
                if winning_symbol == self.player1emoji:
                    winner = self.player1
                else:
                    winner = self.player2
    
                #check for a tie
                if winning_symbol == "tie":
                    winner_message = "It is a tie!\nUnfortunately, nobody won this round."
                else:
                    winner_message = f"{winning_symbol} {winner.mention} won this round.\nCongratulations, good sir!"
              
                # Update the winner embed
                c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {self.ctx.guild.name}\nA game of Connect Four has ended...\n\n{winner_message}", color=discord.Color.from_rgb(0, 0, 255))
    
                if self.player2_bot is True:
                    c4_embed.add_field(name="Difficulty", value=self.difficulty, inline=False)
              
                c4_embed.add_field(name=f"{self.player1emoji} Player 1", value=self.player1.mention)
                c4_embed.add_field(name=f"{self.player2emoji} Player 2", value=self.player2.mention)
                c4_embed.add_field(name="", value=self.format_board(self.board), inline=False)
                c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")  # c4 GIF
            
                await self.message.edit(embed=c4_embed, view=None)
    
                self.stop() #stop accepting interactions
                return
          
                
            
            self.toggle_turn() #toggle the turn
        
            # Update the embed
            c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {self.ctx.guild.name}\nA game of Connect Four has commenced.\nSelect the desired column using the corresponding button.", color=discord.Color.from_rgb(0, 0, 255))
    
            if self.player2_bot is True:
                c4_embed.add_field(name="Difficulty", value=self.difficulty, inline=False)
          
            c4_embed.add_field(name=f"{self.player1emoji} Player 1", value=self.player1.mention)
            c4_embed.add_field(name=f"{self.player2emoji} Player 2", value=self.player2.mention)
            c4_embed.add_field(name="", value=self.format_board(self.board), inline=False)
            c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")  # c4 GIF
    
    
            if self.current_turn == self.player1id:
                footer = f"Current Turn: {self.player1emoji} {self.player1.display_name}"
            else:
                footer = f"Current Turn: {self.player2emoji} {self.player2.display_name}"
          
            c4_embed.set_footer(text=footer)
        
            await self.message.edit(embed=c4_embed, view=self)
    
            # Make the bot move (if set)
            if self.player2_bot is True:
                await asyncio.sleep(2)
                await self.make_bot_move(interaction)
    
    
    
        ###### sixth column button
        @discord.ui.button(emoji="6️⃣", style=discord.ButtonStyle.primary)
        async def sixth_button_callback(self, button, interaction):
            await interaction.response.defer()
        
            if self.current_turn != interaction.user.id:
                return
        
            # Get the correct emoji for the interaction
            if interaction.user.id == self.player1id:
                emoji = self.player1emoji
            else:
                emoji = self.player2emoji
    
          
            self.button6clicks += 1  # Increment the click count for button 1
          
            if self.button6clicks == 6: #column is full, disable button
                button.disabled = True
    
          
            column = 5  # Update this based on the button clicked
        
            # Update the board
            for row in range(5, -1, -1):
                if self.board[row][column] == '⚪':
                    self.board[row][column] = emoji
                    break
        
            # Check for a winner
            winning_symbol = self.check_winner(self.board)
            if winning_symbol:
                for child in self.children: #disable the buttons
                    child.disabled = True
              
                #check what the winning symbol is and assign a player object to it (for mentions)
                if winning_symbol == self.player1emoji:
                    winner = self.player1
                else:
                    winner = self.player2
    
                #check for a tie
                if winning_symbol == "tie":
                    winner_message = "It is a tie!\nUnfortunately, nobody won this round."
                else:
                    winner_message = f"{winning_symbol} {winner.mention} won this round.\nCongratulations, good sir!"
              
                # Update the winner embed
                c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {self.ctx.guild.name}\nA game of Connect Four has ended...\n\n{winner_message}", color=discord.Color.from_rgb(0, 0, 255))
    
                if self.player2_bot is True:
                    c4_embed.add_field(name="Difficulty", value=self.difficulty, inline=False)
              
                c4_embed.add_field(name=f"{self.player1emoji} Player 1", value=self.player1.mention)
                c4_embed.add_field(name=f"{self.player2emoji} Player 2", value=self.player2.mention)
                c4_embed.add_field(name="", value=self.format_board(self.board), inline=False)
                c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")  # c4 GIF
            
                await self.message.edit(embed=c4_embed, view=None)
    
                self.stop() #stop accepting interactions
                return
          
                
            
            self.toggle_turn() #toggle the turn
        
            # Update the embed
            c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {self.ctx.guild.name}\nA game of Connect Four has commenced.\nSelect the desired column using the corresponding button.", color=discord.Color.from_rgb(0, 0, 255))
    
            if self.player2_bot is True:
                c4_embed.add_field(name="Difficulty", value=self.difficulty, inline=False)
          
            c4_embed.add_field(name=f"{self.player1emoji} Player 1", value=self.player1.mention)
            c4_embed.add_field(name=f"{self.player2emoji} Player 2", value=self.player2.mention)
            c4_embed.add_field(name="", value=self.format_board(self.board), inline=False)
            c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")  # c4 GIF
    
            if self.current_turn == self.player1id:
                footer = f"Current Turn: {self.player1emoji} {self.player1.display_name}"
            else:
                footer = f"Current Turn: {self.player2emoji} {self.player2.display_name}"
          
            c4_embed.set_footer(text=footer)
        
            await self.message.edit(embed=c4_embed, view=self)
    
            # Make the bot move (if set)
            if self.player2_bot is True:
                await asyncio.sleep(2)
                await self.make_bot_move(interaction)
    
    
    
    
        ###### seventh column button
        @discord.ui.button(emoji="7️⃣", style=discord.ButtonStyle.primary)
        async def seventh_button_callback(self, button, interaction):
            await interaction.response.defer()
        
            if self.current_turn != interaction.user.id:
                return
        
            # Get the correct emoji for the interaction
            if interaction.user.id == self.player1id:
                emoji = self.player1emoji
            else:
                emoji = self.player2emoji
    
          
            self.button7clicks += 1  # Increment the click count for button 1
          
            if self.button7clicks == 6: #column is full, disable button
                button.disabled = True
    
          
            column = 6  # Update this based on the button clicked
        
            # Update the board
            for row in range(5, -1, -1):
                if self.board[row][column] == '⚪':
                    self.board[row][column] = emoji
                    break
        
            # Check for a winner
            winning_symbol = self.check_winner(self.board)
            if winning_symbol:
                for child in self.children: #disable the buttons
                    child.disabled = True
              
                #check what the winning symbol is and assign a player object to it (for mentions)
                if winning_symbol == self.player1emoji:
                    winner = self.player1
                else:
                    winner = self.player2
    
                #check for a tie
                if winning_symbol == "tie":
                    winner_message = "It is a tie!\nUnfortunately, nobody won this round."
                else:
                    winner_message = f"{winning_symbol} {winner.mention} won this round.\nCongratulations, good sir!"
              
                # Update the winner embed
                c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {self.ctx.guild.name}\nA game of Connect Four has ended...\n\n{winner_message}", color=discord.Color.from_rgb(0, 0, 255))
    
                if self.player2_bot is True:
                    c4_embed.add_field(name="Difficulty", value=self.difficulty, inline=False)
              
                c4_embed.add_field(name=f"{self.player1emoji} Player 1", value=self.player1.mention)
                c4_embed.add_field(name=f"{self.player2emoji} Player 2", value=self.player2.mention)
                c4_embed.add_field(name="", value=self.format_board(self.board), inline=False)
                c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")  # c4 GIF
            
                await self.message.edit(embed=c4_embed, view=None)
    
                self.stop() #stop accepting interactions
                return
          
                
            
            self.toggle_turn() #toggle the turn
        
            # Update the embed
            c4_embed = discord.Embed(title="Connect Four", description=f"Attention members of {self.ctx.guild.name}\nA game of Connect Four has commenced.\nSelect the desired column using the corresponding button.", color=discord.Color.from_rgb(0, 0, 255))
    
            if self.player2_bot is True:
                c4_embed.add_field(name="Difficulty", value=self.difficulty, inline=False)
          
            c4_embed.add_field(name=f"{self.player1emoji} Player 1", value=self.player1.mention)
            c4_embed.add_field(name=f"{self.player2emoji} Player 2", value=self.player2.mention)
            c4_embed.add_field(name="", value=self.format_board(self.board), inline=False)
            c4_embed.set_thumbnail(url="https://i.imgur.com/qChYW1N.gif")  # c4 GIF
    
            if self.current_turn == self.player1id:
                footer = f"Current Turn: {self.player1emoji} {self.player1.display_name}"
            else:
                footer = f"Current Turn: {self.player2emoji} {self.player2.display_name}"
          
            c4_embed.set_footer(text=footer)
        
            await self.message.edit(embed=c4_embed, view=self)
    
            # Make the bot move (if set)
            if self.player2_bot is True:
                await asyncio.sleep(2)
                await self.make_bot_move(interaction)

##################################CONNECTFOUR#####################################






##############################TICTACTOE################################  
    @discord.slash_command(
        name="tictactoe",
        description="Challenge the automaton or another member of the guild to a game of tic-tac-toe.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def tictactoe(self, ctx, player2: Option(discord.Member, name="player2", description="Opponent for the gmae."), symbol: Option(str, name="symbol", description="Symbol you would like to use for the game. (Default: ❌)", choices=["❌", "⭕"], required=False, default="❌"), difficulty: Option(str, name="difficulty", description="Difficulty setting when facing the automaton. (Default: 🟨 Medium)", required=False, default=None, choices=["🟩 Easy", "🟨 Medium", "🟥 Hard"])):
    
        #check the member that is used
        #cannot play against self
        if player2.id == ctx.author.id:
            await ctx.respond(f"Apologies {ctx.author.mention},\nYou are unable to play against yourself in tic-tac-toe.\n*Please try again using a different member of {ctx.guild.name}.*", ephemeral=True)
            return
    
        #play against Lord Bottington
        elif player2.id == self.bot.user.id:
            #define the bot difficulty dictionary
            difficulty_dict = {
              "🟩 Easy": "easy",
              "🟨 Medium": "medium",
              "🟥 Hard": "hard"
            }
    
            if difficulty:
                if difficulty in difficulty_dict:
                    bot_difficulty = difficulty_dict[difficulty] #set the bot difficulty
            else:
                difficulty = "🟨 Medium" #emoji string difficulty
                bot_difficulty = "medium" #bot difficulty as lowercase string
          
            player2_bot = True
    
        #cannot play against a bot that is not Lord Bottington
        elif player2.bot:
            await ctx.respond(f"Apologies {ctx.author.mention},\nYou cannot play against *{player2.display_name}* in tic-tac-toe. You may only face myself or another member of {ctx.guild.name}.\n*Please try again.*", ephemeral=True)
            return
    
        else:
            difficulty = None
            bot_difficulty = None
            player2_bot = False
            
        
        symbols = ["❌", "⭕"] #symbols that are used
      
        # Assign the chosen character to player 1
        player1emoji = symbol
      
        # Assign the other character to player 2
        player2emoji = next(emoji for emoji in symbols if emoji != symbol)
    
        #send the response with the buttons defined below
        await ctx.respond(f"__***Tic Tac Toe***__\n{f'*Difficulty:* {difficulty}' if player2_bot is True else ''}\n*Player 1:*\n {player1emoji} {ctx.author.mention}\n *Player 2:*\n {player2emoji} {player2.mention}\n\nPress the button corresponding to your desired play position below.\nCurrent Turn: {player1emoji} {ctx.author.display_name}", view=self.TTTView(ctx, player1emoji, player2emoji, ctx.author.id, player2.id, player2_bot, difficulty, bot_difficulty, ctx.author, player2))
    
    
    
    
    class TTTView(discord.ui.View):
        def __init__(self, ctx, player1emoji, player2emoji, player1id, player2id, player2_bot, difficulty, bot_difficulty, player1, player2):
            super().__init__(timeout=120) # specify the timeout here
            self.ctx = ctx
            self.player1emoji = player1emoji
            self.player2emoji = player2emoji
            self.board = [None] * 9 #initialize the tictactoe board to a 3x3
            self.player1id = player1id #author ID
            self.player2id = player2id #other player ID
            self.current_turn = self.player1id #author always starts the game
            self.player2_bot = player2_bot #check if player 2 is the bot
            self.difficulty = difficulty #emoji user chosen difficulty (if facing bot)
            self.bot_difficulty = bot_difficulty #initialize the bot difficulty (if facing bot)
            self.player1 = player1
            self.player2 = player2
    
        #check for a winner
        #if all the symbols that are returned are the same in the positions indicated in winning_combinations, return True else return False
        def check_win(self, symbol):
            winning_combinations = [
                [0, 1, 2], [3, 4, 5], [6, 7, 8],  # horizontal
                [0, 3, 6], [1, 4, 7], [2, 5, 8],  # vertical
                [0, 4, 8], [2, 4, 6]  # diagonal
            ]
       
            for combo in winning_combinations:
                if all(self.board[i] == symbol for i in combo): #if all the symbols are the same for the winning combo
                    return True
            return False
    
    
        #check for a tie in the game
        def check_tie(self):
            # Check if all positions on the board are filled
            if all(position is not None for position in self.board):
                return True
            return False
    
    
      
        # Handle timeout (e.g., if no moves are made within the specified timeout)
        async def on_timeout(self):
            for child in self.children: #disable all the buttons
                child.disabled = True

            try:
                await self.message.edit("__***Tic-Tac-Toe***__\nIt appears that one or more of the players has not responded in time.\nThe game has officially ended...", view=self)
            except discord.errors.NotFound: #if message deleted before timeout
                pass
          
            self.stop() #stop accepting button clicks
    
    
      
        #function to switch the player's turn
        def toggle_turn(self):
            if self.current_turn == self.player1id:
                self.current_turn = self.player2id  # Switch to player 2's turn
            else:
                self.current_turn = self.player1id  # Switch to player 1's turn
    
    
    
        # bot's move
        async def bot_make_move(self):
            available_positions = [i for i in range(9) if self.board[i] is None]
    
            #Easy mode (only choose random position from available positions)
            if self.bot_difficulty == "easy":
                if random.random() < 0.5:  # 50% chance of making a random move
                    position = random.choice(available_positions)
                else:
                    # Check if there is any winning move for the player
                    winning_move = self.find_winning_move(self.player2emoji)
                    if winning_move is not None:
                        position = winning_move
                    else:
                        # Check if there is any winning move for the bot
                        winning_move = self.find_winning_move(self.player1emoji)
                        if winning_move is not None:
                            position = winning_move
                        else:
                            # If no winning move for either player, choose a random available position
                            position = random.choice(available_positions)
    
          
    
            #Medium Mode - default (only block player, otherwise find random position)
            elif self.bot_difficulty == "medium":
                if random.random() < 0.25:  # 25% chance of making a random move
                    position = random.choice(available_positions)
                else:
                    # Check if there is any winning move for the player
                    winning_move = self.find_winning_move(self.player2emoji)
                    if winning_move is not None:
                        position = winning_move
                    else:
                        # Check if there is any winning move for the bot
                        winning_move = self.find_winning_move(self.player1emoji)
                        if winning_move is not None:
                            position = winning_move
                        else:
                            # If no winning move for either player, choose a random available position
                            position = random.choice(available_positions)
    
              #Hard Mode (block player, look for winning moves, and if all else fails, look for random spot); no chance of radnom choice
            elif self.bot_difficulty == "hard":
                # Check if there is any winning move for the player
                winning_move = self.find_winning_move(self.player2emoji)
                if winning_move is not None:
                    position = winning_move
                else:
                    # Check if there is any winning move for the bot
                    winning_move = self.find_winning_move(self.player1emoji)
                    if winning_move is not None:
                        position = winning_move
                    else:
                        # If no winning move for either player, choose a random available position
                        position = random.choice(available_positions)
          
    
          
            button = self.children[position]
            button.disabled = True
            button.emoji = self.player2emoji
            self.board[position] = button.emoji
            check_win = self.check_win(button.emoji)
            await asyncio.sleep(2)  # Allow time to add emoji and disable button
          
            if check_win:
                for child in self.children:
                    child.disabled = True
    
              
                winner = self.ctx.author if button.emoji == self.player1emoji else self.ctx.guild.get_member(self.player2id)
                await self.message.edit(content=f"__***Tic-Tac-Toe***__\n*Difficulty:* {self.difficulty}\n{button.emoji} {winner.mention} wins this round...\n*{'Congratulations, good sir!*' if winner.id != self.player2id else 'That was quite exciting, good sir!*'}", view=self)
                self.stop()
            elif self.check_tie():
                for child in self.children:
                    child.disabled = True
                await self.message.edit(content=f"__***Tic-Tac-Toe***__\n*Difficulty:* {self.difficulty}\nIt's a tie!\nThe game has officially ended with no winner...", view=self)
                self.stop()
            else:
                self.toggle_turn() #switch turns
      
                if self.current_turn == self.player1id:
                    turn = f"{self.player1emoji} {self.player1.display_name}"
                else:
                    turn = f"{self.player2emoji} {self.player2.display_name}"
                
                message = f"__***Tic Tac Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n*Player 1:*\n {self.player1emoji} {self.ctx.author.mention}\n *Player 2:*\n {self.player2emoji} {self.player2.mention}\n\nPress the button corresponding to your desired play position below.\nCurrent Turn: {turn}"
              
                await self.message.edit(content=message, view=self) # edit the message's view
        
    
    
        def find_winning_move(self, player_emoji):
            array = self.board
          
            updated_array = []
            for item in array:
                if isinstance(item, discord.PartialEmoji):
                    updated_array.append(item.name)
                else:
                    updated_array.append(item)
    
            # Check rows
            for i in range(0, 7, 3):
                if updated_array[i] == updated_array[i + 1] == player_emoji and updated_array[i + 2] is None:
                    return i + 2
                elif updated_array[i] == updated_array[i + 2] == player_emoji and updated_array[i + 1] is None:
                    return i + 1
                elif updated_array[i + 1] == updated_array[i + 2] == player_emoji and updated_array[i] is None:
                    return i
        
            # Check columns
            for i in range(3):
                if updated_array[i] == updated_array[i + 3] == player_emoji and updated_array[i + 6] is None:
                    return i + 6
                elif updated_array[i] == updated_array[i + 6] == player_emoji and updated_array[i + 3] is None:
                    return i + 3
                elif updated_array[i + 3] == updated_array[i + 6] == player_emoji and updated_array[i] is None:
                    return i
        
            # Check diagonals
            if updated_array[0] == updated_array[4] == player_emoji and updated_array[8] is None:
                return 8
            elif updated_array[0] == updated_array[8] == player_emoji and updated_array[4] is None:
                return 4
            elif updated_array[4] == updated_array[8] == player_emoji and updated_array[0] is None:
                return 0
        
            if updated_array[2] == updated_array[4] == player_emoji and updated_array[6] is None:
                return 6
            elif updated_array[2] == updated_array[6] == player_emoji and updated_array[4] is None:
                return 4
            elif updated_array[4] == updated_array[6] == player_emoji and updated_array[2] is None:
                return 2
        
            return None


      

        def update_wins(self, winner, game_played):
            #only update winnings data if there is not a tie and the winner is not Lord Bottington
            if winner and not winner.bot:
                #increase currency (🪙shillings) based on who the player is facing and the difficulty when facing Lord Bottington
                if self.player2.bot and self.bot_difficulty == "easy":
                    shillings = 2
                elif self.player2.bot and self.bot_difficulty == "medium":
                    shillings = 5
                elif self.player2.bot and self.bot_difficulty == "hard":
                    shillings = 10
                elif not self.player2.bot: #when facing regular player
                    shillings = 10
                    
              
                games = ["battleship", "connectfour", "mastermind", "rps", "tictactoe", "wumpus"]

                i = 0
                for game in games:
                    if game_played == game:
                        game_index = i
                        break

                    i = i + 1

                no_wins = [0 for _ in range(6)] #blank array of wins
                no_shillings = [0 for _ in range(6)] #blank array of shillings
              
                #update the number of wins for connectfour for the winner
                guild_wins = games_db[f"winnings_{self.ctx.guild.id}"]
                game_key = {"player_id": winner.id}
    
                player_record = guild_wins.find_one(game_key)
              
                if player_record is None:
                    no_wins[game_index] = 1
                    no_shillings[game_index] = shillings
                  
                    guild_wins.insert_one(
                      {
                        "server_id": self.ctx.guild.id,
                        "server_name": self.ctx.guild.name,
                        "player_name": winner.display_name,
                        "player_id": winner.id,
                        "games": games,
                        "wins": no_wins,
                        "shillings": no_shillings
                      }
                    )
                else:
                    wins_obtained = player_record["wins"]
                    shillings_obtained = player_record["shillings"]

                    wins_obtained[game_index] += 1
                    shillings_obtained[game_index] += shillings
                  
                    guild_wins.update_one(
                        game_key,
                        {"$set": {
                          "wins": wins_obtained,
                          "shillings": shillings_obtained
                          }
                        }
                    )

              
                #wallets for the guild
                guild_wallets = wallets_db[f"wallets_{self.ctx.guild.id}"]
                wallet_key = {"player_id": winner.id}
              
                wallet_record = guild_wallets.find_one(wallet_key)

                if wallet_record is None:
                    guild_wallets.insert_one(
                      {
                        "server_id": self.ctx.guild.id,
                        "server_name": self.ctx.guild.name,
                        "player_name": winner.display_name,
                        "player_id": winner.id,
                        "wallet": shillings
                      }
                    )
              
                else:
                    guild_wallets.update_one(
                        wallet_key,
                        {"$inc": {
                          "wallet": shillings
                          }
                        }
                    )
                    
                  
    
        #first button
        @discord.ui.button(row=0, emoji="1️⃣", style=discord.ButtonStyle.primary)
        async def first_button_callback(self, button, interaction):
            #if the current turn is not equal to the interaction user
            if self.current_turn != interaction.user.id:
                await interaction.response.defer() #acknowledge the interaction
                return
    
            #otherwise, perform the interaction
            else:
                button.disabled = True #disable the button from further use
                button.emoji = self.player1emoji if interaction.user.id == self.ctx.author.id else self.player2emoji #set the emoji to the correct one for the user
      
                position = 0  # The position of the button on the board
                self.board[position] = button.emoji #replace the position on the board from None to the position number
                check_win = self.check_win(button.emoji) #check if this interaction is a winner
      
                if check_win is True: #if there is a winner
                    for child in self.children: #disable all the buttons
                        child.disabled = True
                      
                    await interaction.response.edit_message(content = f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n{button.emoji} {interaction.user.mention} wins this round...\n*Congratulations, good sir!*", view=self)

                    #Update the winner database on mongoDB
                    game_played = "tictactoe"
                    self.update_wins(interaction.user, game_played)
                  
                    self.stop() #stop accepting interactions
    
                elif self.check_tie(): #check for a tie
                    for child in self.children: #disable all buttons
                        child.disabled = True
    
                    await interaction.response.edit_message(content=f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\nIt appears there is a tie!\nThe game has officially ended with no winner...", view=self)
                    self.stop() #stop accepting interactions
              
                else:
                    self.toggle_turn() #switch turns
    
                    if self.current_turn == self.player1id:
                        turn = f"{self.player1emoji} {self.player1.display_name}"
                    else:
                        turn = f"{self.player2emoji} {self.player2.display_name}"
                    
                    message = f"__***Tic Tac Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n*Player 1:*\n {self.player1emoji} {self.ctx.author.mention}\n *Player 2:*\n {self.player2emoji} {self.player2.mention}\n\nPress the button corresponding to your desired play position below.\nCurrent Turn: {turn}"
                  
                    await interaction.response.edit_message(content=message, view=self) # edit the message's view
    
                    if self.player2_bot is True:
                        await self.bot_make_move()
                    
            
        #second button
        @discord.ui.button(row=0, emoji="2️⃣", style=discord.ButtonStyle.primary)
        async def second_button_callback(self, button, interaction):
            if self.current_turn != interaction.user.id:
                await interaction.response.defer()
                return
            else:
                button.disabled = True
                button.emoji = self.player1emoji if interaction.user.id == self.ctx.author.id else self.player2emoji
      
                position = 1  # The position of the button on the board
                self.board[position] = button.emoji
                check_win = self.check_win(button.emoji)
      
                if check_win is True:
                    for child in self.children:
                        child.disabled = True
                      
                    await interaction.response.edit_message(content = f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n{button.emoji} {interaction.user.mention} wins this round...\n*Congratulations, good sir!*", view=self)

                    #Update the winner database on mongoDB
                    game_played = "tictactoe"
                    self.update_wins(interaction.user, game_played)
                  
                    self.stop()
    
                elif self.check_tie(): #check for a tie
                    for child in self.children: #disable all buttons
                        child.disabled = True
    
                    await interaction.response.edit_message(content=f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\nIt appears there is a tie!\nThe game has officially ended with no winner...", view=self)
                    self.stop() #stop accepting interactions
    
              
                else:
                    self.toggle_turn() #switch turns
    
                    if self.current_turn == self.player1id:
                        turn = f"{self.player1emoji} {self.player1.display_name}"
                    else:
                        turn = f"{self.player2emoji} {self.player2.display_name}"
                    
                    message = f"__***Tic Tac Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n*Player 1:*\n {self.player1emoji} {self.ctx.author.mention}\n *Player 2:*\n {self.player2emoji} {self.player2.mention}\n\nPress the button corresponding to your desired play position below.\nCurrent Turn: {turn}"
                  
                    await interaction.response.edit_message(content=message, view=self) # edit the message's view
    
                  
                    if self.player2_bot is True:
                        await self.bot_make_move()
    
        #third button
        @discord.ui.button(row=0, emoji="3️⃣", style=discord.ButtonStyle.primary)
        async def third_button_callback(self, button, interaction):
            if self.current_turn != interaction.user.id:
                await interaction.response.defer()
                return
            else:
                button.disabled = True
                button.emoji = self.player1emoji if interaction.user.id == self.ctx.author.id else self.player2emoji
      
                position = 2  # The position of the button on the board
                self.board[position] = button.emoji
                check_win = self.check_win(button.emoji)
      
                if check_win is True:
                    for child in self.children:
                        child.disabled = True
                      
                    await interaction.response.edit_message(content = f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n{button.emoji} {interaction.user.mention} wins this round...\n*Congratulations, good sir!*", view=self)

                    #Update the winner database on mongoDB
                    game_played = "tictactoe"
                    self.update_wins(interaction.user, game_played)
                  
                    self.stop()
    
                elif self.check_tie(): #check for a tie
                    for child in self.children: #disable all buttons
                        child.disabled = True
    
                    await interaction.response.edit_message(content=f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\nIt appears there is a tie!\nThe game has officially ended with no winner...", view=self)
                    self.stop() #stop accepting interactions
              
                else:
                    self.toggle_turn() #switch turns
    
                    if self.current_turn == self.player1id:
                        turn = f"{self.player1emoji} {self.player1.display_name}"
                    else:
                        turn = f"{self.player2emoji} {self.player2.display_name}"
                    
                    message = f"__***Tic Tac Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n*Player 1:*\n {self.player1emoji} {self.ctx.author.mention}\n *Player 2:*\n {self.player2emoji} {self.player2.mention}\n\nPress the button corresponding to your desired play position below.\nCurrent Turn: {turn}"
                  
                    await interaction.response.edit_message(content=message, view=self) # edit the message's view
    
    
                    if self.player2_bot is True:
                        await self.bot_make_move()
    
    
        #fourth button
        @discord.ui.button(row=1, emoji="4️⃣", style=discord.ButtonStyle.primary)
        async def fourth_button_callback(self, button, interaction):
            if self.current_turn != interaction.user.id:
                await interaction.response.defer()
                return
            else:
                button.disabled = True
                button.emoji = self.player1emoji if interaction.user.id == self.ctx.author.id else self.player2emoji
      
                position = 3  # The position of the button on the board
                self.board[position] = button.emoji
                check_win = self.check_win(button.emoji)
      
                if check_win is True:
                    for child in self.children:
                        child.disabled = True
                      
                    await interaction.response.edit_message(content = f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n{button.emoji} {interaction.user.mention} wins this round...\n*Congratulations, good sir!*", view=self)

                    #Update the winner database on mongoDB
                    game_played = "tictactoe"
                    self.update_wins(interaction.user, game_played)
                  
                    self.stop()
    
                elif self.check_tie(): #check for a tie
                    for child in self.children: #disable all buttons
                        child.disabled = True
    
                    await interaction.response.edit_message(content=f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\nIt appears there is a tie!\nThe game has officially ended with no winner...", view=self)
                    self.stop() #stop accepting interactions
              
                else:
                    self.toggle_turn() #switch turns
    
                    if self.current_turn == self.player1id:
                        turn = f"{self.player1emoji} {self.player1.display_name}"
                    else:
                        turn = f"{self.player2emoji} {self.player2.display_name}"
                    
                    message = f"__***Tic Tac Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n*Player 1:*\n {self.player1emoji} {self.ctx.author.mention}\n *Player 2:*\n {self.player2emoji} {self.player2.mention}\n\nPress the button corresponding to your desired play position below.\nCurrent Turn: {turn}"
                  
                    await interaction.response.edit_message(content=message, view=self) # edit the message's view
    
    
                    if self.player2_bot is True:
                        await self.bot_make_move()
    
    
        #fifth button
        @discord.ui.button(row=1, emoji="5️⃣", style=discord.ButtonStyle.primary)
        async def fifth_button_callback(self, button, interaction):
            if self.current_turn != interaction.user.id:
                await interaction.response.defer()
                return
            else:
                button.disabled = True
                button.emoji = self.player1emoji if interaction.user.id == self.ctx.author.id else self.player2emoji
      
                position = 4  # The position of the button on the board
                self.board[position] = button.emoji
                check_win = self.check_win(button.emoji)
      
                if check_win is True:
                    for child in self.children:
                        child.disabled = True
                      
                    await interaction.response.edit_message(content = f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n{button.emoji} {interaction.user.mention} wins this round...\n*Congratulations, good sir!*", view=self)

                    #Update the winner database on mongoDB
                    game_played = "tictactoe"
                    self.update_wins(interaction.user, game_played)
                  
                    self.stop()
    
                elif self.check_tie(): #check for a tie
                    for child in self.children: #disable all buttons
                        child.disabled = True
    
                    await interaction.response.edit_message(content=f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\nIt appears there is a tie!\nThe game has officially ended with no winner...", view=self)
                    self.stop() #stop accepting interactions
              
                else:
                    self.toggle_turn() #switch turns
    
                    if self.current_turn == self.player1id:
                        turn = f"{self.player1emoji} {self.player1.display_name}"
                    else:
                        turn = f"{self.player2emoji} {self.player2.display_name}"
                    
                    message = f"__***Tic Tac Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n*Player 1:*\n {self.player1emoji} {self.ctx.author.mention}\n *Player 2:*\n {self.player2emoji} {self.player2.mention}\n\nPress the button corresponding to your desired play position below.\nCurrent Turn: {turn}"
                  
                    await interaction.response.edit_message(content=message, view=self) # edit the message's view
    
    
                    if self.player2_bot is True:
                        await self.bot_make_move()
    
    
    
        #sixth button
        @discord.ui.button(row=1, emoji="6️⃣", style=discord.ButtonStyle.primary)
        async def sixth_button_callback(self, button, interaction):
            if self.current_turn != interaction.user.id:
                await interaction.response.defer()
                return
            else:
                button.disabled = True
                button.emoji = self.player1emoji if interaction.user.id == self.ctx.author.id else self.player2emoji
      
                position = 5  # The position of the button on the board
                self.board[position] = button.emoji
                check_win = self.check_win(button.emoji)
      
                if check_win is True:
                    for child in self.children:
                        child.disabled = True
                      
                    await interaction.response.edit_message(content = f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n{button.emoji} {interaction.user.mention} wins this round...\n*Congratulations, good sir!*", view=self)

                    #Update the winner database on mongoDB
                    game_played = "tictactoe"
                    self.update_wins(interaction.user, game_played)
                  
                    self.stop()
    
                elif self.check_tie(): #check for a tie
                    for child in self.children: #disable all buttons
                        child.disabled = True
    
                    await interaction.response.edit_message(content=f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\nIt appears there is a tie!\nThe game has officially ended with no winner...", view=self)
                    self.stop() #stop accepting interactions
              
                else:
                    self.toggle_turn() #switch turns
    
                    if self.current_turn == self.player1id:
                        turn = f"{self.player1emoji} {self.player1.display_name}"
                    else:
                        turn = f"{self.player2emoji} {self.player2.display_name}"
                    
                    message = f"__***Tic Tac Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n*Player 1:*\n {self.player1emoji} {self.ctx.author.mention}\n *Player 2:*\n {self.player2emoji} {self.player2.mention}\n\nPress the button corresponding to your desired play position below.\nCurrent Turn: {turn}"
                  
                    await interaction.response.edit_message(content=message, view=self) # edit the message's view
    
    
                    if self.player2_bot is True:
                        await self.bot_make_move()
    
    
        #seventh button
        @discord.ui.button(row=2, emoji="7️⃣", style=discord.ButtonStyle.primary)
        async def seventh_button_callback(self, button, interaction):
            if self.current_turn != interaction.user.id:
                await interaction.response.defer()
                return
            else:
                button.disabled = True
                button.emoji = self.player1emoji if interaction.user.id == self.ctx.author.id else self.player2emoji
      
                position = 6  # The position of the button on the board
                self.board[position] = button.emoji
                check_win = self.check_win(button.emoji)
      
                if check_win is True:
                    for child in self.children:
                        child.disabled = True
                      
                    await interaction.response.edit_message(content = f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n{button.emoji} {interaction.user.mention} wins this round...\n*Congratulations, good sir!*", view=self)
                  
                    #Update the winner database on mongoDB
                    game_played = "tictactoe"
                    self.update_wins(interaction.user, game_played)
                  
                    self.stop()
    
                elif self.check_tie(): #check for a tie
                    for child in self.children: #disable all buttons
                        child.disabled = True
    
                    await interaction.response.edit_message(content=f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\nIt appears there is a tie!\nThe game has officially ended with no winner...", view=self)
                    self.stop() #stop accepting interactions
              
                else:
                    self.toggle_turn() #switch turns
    
                    if self.current_turn == self.player1id:
                        turn = f"{self.player1emoji} {self.player1.display_name}"
                    else:
                        turn = f"{self.player2emoji} {self.player2.display_name}"
                    
                    message = f"__***Tic Tac Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n*Player 1:*\n {self.player1emoji} {self.ctx.author.mention}\n *Player 2:*\n {self.player2emoji} {self.player2.mention}\n\nPress the button corresponding to your desired play position below.\nCurrent Turn: {turn}"
                  
                    await interaction.response.edit_message(content=message, view=self) # edit the message's view
    
    
                    if self.player2_bot is True:
                        await self.bot_make_move()
    
    
    
        #eighth button
        @discord.ui.button(row=2, emoji="8️⃣", style=discord.ButtonStyle.primary)
        async def eighth_button_callback(self, button, interaction):
            if self.current_turn != interaction.user.id:
                await interaction.response.defer()
                return
            else:
                button.disabled = True
                button.emoji = self.player1emoji if interaction.user.id == self.ctx.author.id else self.player2emoji
      
                position = 7  # The position of the button on the board
                self.board[position] = button.emoji
                check_win = self.check_win(button.emoji)
      
                if check_win is True:
                    for child in self.children:
                        child.disabled = True
                      
                    await interaction.response.edit_message(content = f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n{button.emoji} {interaction.user.mention} wins this round...\n*Congratulations, good sir!*", view=self)

                    #Update the winner database on mongoDB
                    game_played = "tictactoe"
                    self.update_wins(interaction.user, game_played)
                  
                    self.stop()
    
                elif self.check_tie(): #check for a tie
                    for child in self.children: #disable all buttons
                        child.disabled = True
    
                    await interaction.response.edit_message(content=f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\nIt appears there is a tie!\nThe game has officially ended with no winner...", view=self)
                    self.stop() #stop accepting interactions
              
                else:
                    self.toggle_turn() #switch turns
    
                    if self.current_turn == self.player1id:
                        turn = f"{self.player1emoji} {self.player1.display_name}"
                    else:
                        turn = f"{self.player2emoji} {self.player2.display_name}"
                    
                    message = f"__***Tic Tac Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n*Player 1:*\n {self.player1emoji} {self.ctx.author.mention}\n *Player 2:*\n {self.player2emoji} {self.player2.mention}\n\nPress the button corresponding to your desired play position below.\nCurrent Turn: {turn}"
                  
                    await interaction.response.edit_message(content=message, view=self) # edit the message's view
    
    
                    if self.player2_bot is True:
                        await self.bot_make_move()
    
    
        #ninth button
        @discord.ui.button(row=2, emoji="9️⃣", style=discord.ButtonStyle.primary)
        async def ninth_button_callback(self, button, interaction):
            if self.current_turn != interaction.user.id:
                await interaction.response.defer()
                return
            else:
                button.disabled = True
                button.emoji = self.player1emoji if interaction.user.id == self.ctx.author.id else self.player2emoji
      
                position = 8  # The position of the button on the board
                self.board[position] = button.emoji
                check_win = self.check_win(button.emoji)
      
                if check_win is True:
                    for child in self.children:
                        child.disabled = True
                      
                    await interaction.response.edit_message(content = f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n{button.emoji} {interaction.user.mention} wins this round...\n*Congratulations, good sir!*", view=self)

                    #Update the winner database on mongoDB
                    game_played = "tictactoe"
                    self.update_wins(interaction.user, game_played)
                  
                    self.stop()
    
                elif self.check_tie(): #check for a tie
                    for child in self.children: #disable all buttons
                        child.disabled = True
    
                    await interaction.response.edit_message(content=f"__***Tic-Tac-Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\nIt appears there is a tie!\nThe game has officially ended with no winner...", view=self)
                    self.stop() #stop accepting interactions
              
                else:
                    self.toggle_turn() #switch turns
    
                    if self.current_turn == self.player1id:
                        turn = f"{self.player1emoji} {self.player1.display_name}"
                    else:
                        turn = f"{self.player2emoji} {self.player2.display_name}"
                    
                    message = f"__***Tic Tac Toe***__\n{f'*Difficulty:* {self.difficulty}' if self.player2_bot is True else ''}\n*Player 1:*\n {self.player1emoji} {self.ctx.author.mention}\n *Player 2:*\n {self.player2emoji} {self.player2.mention}\n\nPress the button corresponding to your desired play position below.\nCurrent Turn: {turn}"
                  
                    await interaction.response.edit_message(content=message, view=self) # edit the message's view
    
    
                    if self.player2_bot is True:
                        await self.bot_make_move()

##############################TICTACTOE################################





#################################RPS#########################################
    @discord.slash_command(
        name="rps",
        description="Challenge the automaton or another member of the guild to a game of rock, paper, scissors.",
        # guild_ids=SERVER_ID
        global_command = True
    )
    async def rps(self, ctx, player2: Option(discord.Member, name="player2", description="Opponent for the game.")):
    
        #check the member that is used
        #cannot play against self
        if player2.id == ctx.author.id:
            await ctx.respond(f"Apologies {ctx.author.mention},\nYou are unable to play against yourself in rock, paper, scissors.\n*Please try again using a different member of {ctx.guild.name}.*", ephemeral=True)
            return
    
        #play against Lord Bottington
        elif player2.id == self.bot.user.id:
            player2_bot = True
          
        #cannot play against a bot that is not Lord Bottington
        elif player2.bot:
            await ctx.respond(f"Apologies {ctx.author.mention},\nYou cannot play against *{player2.display_name}* in rock, paper, scissors. You may only face myself or another member of {ctx.guild.name}.\n*Please try again.*", ephemeral=True)
            return
    
        else:
            player2_bot = False
    
    
    
        rps_embed = discord.Embed(title="Rock, Paper, Scissors", description=f"Attention members of {ctx.guild.name}\nA game of rock, paper, scissors has commenced.", color = discord.Color.from_rgb(0, 0, 255))
    
        rps_embed.add_field(name="Player 1", value=ctx.author.mention)
        rps_embed.add_field(name="Player 2", value=player2.mention)
    
        rps_embed.set_thumbnail(url="https://i.imgur.com/ExzGCb4.gif") #rps GIF
    
        await ctx.respond(embed=rps_embed, view=self.RPSView(ctx, ctx.author.id, player2.id, player2_bot, ctx.author, player2))
    
    
    
    
    class RPSView(discord.ui.View):
        def __init__(self, ctx, player1id, player2id, player2_bot, player1, player2):
            super().__init__(timeout=120) # specify the timeout here
            self.ctx = ctx #initialize the context
            self.player1id = player1id #initialize player 1's ID
            self.player2id = player2id #initialize player 2's ID
            self.player2_bot = player2_bot #check whether player 2 is the bot
            self.choices = [None, None]
            self.player1 = player1
            self.player2 = player2
      
      
        #rock button
        @discord.ui.button(label="Rock", emoji="🪨", style=discord.ButtonStyle.primary)
        async def rock_button_callback(self, button, interaction):
            await interaction.response.defer()
            await self.process_move(button, interaction, "rock")
    
    
        #paper button
        @discord.ui.button(label="Paper", emoji="📄", style=discord.ButtonStyle.primary)
        async def paper_button_callback(self, button, interaction):
            await interaction.response.defer()
            await self.process_move(button, interaction, "paper")
    
    
    
        #scissors button
        @discord.ui.button(label="Scissors", emoji="✂", style=discord.ButtonStyle.primary)
        async def scissors_button_callback(self, button, interaction):
            await interaction.response.defer()
            await self.process_move(button, interaction, "scissors")
    
    
        # Handle timeout (e.g., if no moves are made within the specified timeout)
        async def on_timeout(self):
            for child in self.children: #disable all the buttons
                child.disabled = True
    
            rps_embed = discord.Embed(title="Rock, Paper, Scissors", description=f"Attention members of {self.ctx.guild.name}\nA game of rock, paper, scissors has ended...\nOne or more of the players did not respond in time.", color = discord.Color.from_rgb(0, 0, 255))
      
            rps_embed.add_field(name="Player 1", value=self.player1.mention)
            rps_embed.add_field(name="Player 2", value=self.player2.mention)
      
            rps_embed.set_thumbnail(url="https://i.imgur.com/ExzGCb4.gif") #rps GIF

            try:
                await self.message.edit(embed=rps_embed, view=None) #remove the buttons and send the updated embed
            except discord.errors.NotFound: #if message deleted before timeout
                pass
          
            self.stop() #stop accepting button clicks
    
      
      
        async def process_move(self, button, interaction, choice):
            # Check if the user making the move is one of the players
            if interaction.user.id == self.player1id or interaction.user.id == self.player2id:
                index = 0 if interaction.user.id == self.player1id else 1
                self.choices[index] = choice
      
                # Disable the button to prevent further input from the player
                button.disabled = True
      
                # Check if both players have made their choices
                if self.player2_bot is False:
                    if all(self.choices):
                        await self.game_over()
    
                else:
                    #make bot choice
                    choices = ["rock", "paper", "scissors"]
                    bot_choice = random.choice(choices)
                    self.choices[1] = bot_choice
                    # await asyncio.sleep(1)
                    
                    await self.game_over()
    
      
    
        async def game_over(self):
            for child in self.children: #disable all the buttons
                child.disabled = True
    
          
            # Get the choices made by each player
            player1_choice = self.choices[0]
            player2_choice = self.choices[1]
    
    
            choice_dict = {
              "rock": "🪨 Rock",
              "paper": "📄 Paper",
              "scissors": "✂ Scissors"
            }
    
            player1_choice_emoji = choice_dict[player1_choice]
            player2_choice_emoji = choice_dict[player2_choice]
    
          
            if player1_choice == player2_choice:
                description = "The results are in...\nIt is a tie!"
                winner = None
            elif (player1_choice == "rock" and player2_choice == "scissors") or (player1_choice == "paper" and player2_choice == "rock") or (player1_choice == "scissors" and player2_choice == "paper"):
                description = f"The results are in...\n{self.player1.mention} wins!"
                winner = self.player1
            else:
                description = f"The results are in...\n{self.player2.mention} wins!"
                winner = self.player2

            
            if winner and not winner.bot:
                game_played = "rps"
                games = ["battleship", "connectfour", "mastermind", "rps", "tictactoe", "wumpus"]

                i = 0
                for game in games:
                    if game_played == game:
                        game_index = i
                        break

                    i = i + 1

                no_wins = [0 for _ in range(6)] #blank array of wins
                no_shillings = [0 for _ in range(6)] #blank array of shillings
              
                #update the number of wins for connectfour for the winner
                guild_wins = games_db[f"winnings_{self.ctx.guild.id}"]
                game_key = {"player_id": winner.id}
    
                player_record = guild_wins.find_one(game_key)
              
                if player_record is None:
                    no_wins[game_index] = 1
                    no_shillings[game_index] = 5
                  
                    guild_wins.insert_one(
                      {
                        "server_id": self.ctx.guild.id,
                        "server_name": self.ctx.guild.name,
                        "player_name": winner.display_name,
                        "player_id": winner.id,
                        "games": games,
                        "wins": no_wins,
                        "shillings": no_shillings
                      }
                    )
                else:
                    wins_obtained = player_record["wins"]
                    shillings_obtained = player_record["shillings"]

                    wins_obtained[game_index] += 1
                    shillings_obtained[game_index] += 5
                  
                    guild_wins.update_one(
                        game_key,
                        {"$set": {
                          "wins": wins_obtained,
                          "shillings": shillings_obtained
                          }
                        }
                    )

              
                #wallets for the guild
                guild_wallets = wallets_db[f"wallets_{self.ctx.guild.id}"]
                wallet_key = {"player_id": winner.id}
              
                wallet_record = guild_wallets.find_one(wallet_key)

                if wallet_record is None:
                    guild_wallets.insert_one(
                      {
                        "server_id": self.ctx.guild.id,
                        "server_name": self.ctx.guild.name,
                        "player_name": winner.display_name,
                        "player_id": winner.id,
                        "wallet": 5
                      }
                    )
              
                else:
                    guild_wallets.update_one(
                        wallet_key,
                        {"$inc": {
                          "wallet": 5
                          }
                        }
                    )
          

          
    
            # Example code to display the result in an embed
            rps_embed = discord.Embed(title="Rock, Paper, Scissors Result",
                                      description=description,
                                      color=discord.Color.from_rgb(0, 0, 255))
    
            rps_embed.add_field(name="Player 1", value=f"{self.player1.mention}\n{player1_choice_emoji}") #author choice
            rps_embed.add_field(name="Player 2", value=f"{self.player2.mention}\n{player2_choice_emoji}") #player 2 choice
      
            rps_embed.set_thumbnail(url="https://i.imgur.com/ExzGCb4.gif") #rps GIF
          
            await self.message.edit(embed=rps_embed, view=None)
    
            self.stop() #stop accepting button clicks
  
#################################RPS#########################################








def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Games(bot)) # add the cog to the bot