#---------------------------
#   Import Libraries
#---------------------------
import os
import sys
import clr
import json
import random
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = "Gamble_And_Roulette"
Website = "https://www.streamlabs.com"
Description = "!gamble or !roulette will allow the user to try to double the amount they bet (supports !gamble all and !roulette all)"
Creator = "TheFlippyPenguin"
Version = "1.0.0.0"

#---------------------------
#   Define Global Variables
#---------------------------
configFile = "config.json"
settings = {}
winChance = 40 # percent chance of winning the gamble/roulette
cooldown = 30
global rng

#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():
    global settings
    global rng

    rng = random.SystemRandom()
    path = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
            settings = json.load(file, encoding='utf-8-sig')
    except:
        settings = {
            "gambleCommand": "!gamble",
            "gamblePermission": "Everyone",
            "rouletteCommand": "!roulette",
            "roulettePermission": "Everyone",
            "userWonResponse": "/me $user won $win $currency! PogChamp Feeling lucky? Try again ;)",
            "userLostResponse": "/me $user you lost $loss $currency, oh no! BibleThump",
            "userLostEverything": "/me $user you lost all your $currency! RIP the dream... NotLikeThis",
            "notEnoughCurrencyResponse": "/me $user you only have $points $currency to use!",
            "permissionDenied": "/me $user you don't have permission to do that!",
            "invalidEntryResponse": "/me Please enter a valid number or \"all\"",
            "onCooldown": "/me $user wait $cooldown seconds to bet again"
            }
    #lost ! What a tragedy NotLikeThis
    return

#---------------------------
#   Extra Functions
#---------------------------
def isWinner():
    global winChance
    global rng
    if rng.randint(1,100) <= winChance:
        return True
    return False

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    global settings
    message = ""
    
    if data.IsChatMessage():
        if data.GetParam(0).lower() == settings["gambleCommand"] or data.GetParam(0).lower() == settings["rouletteCommand"]:
            # command is !gamble or !roulette
            if Parent.HasPermission(data.User,settings["gamblePermission"],"") and Parent.HasPermission(data.User,settings["roulettePermission"],""):
                # user has permission
                if Parent.IsOnUserCooldown(ScriptName,ScriptName,data.User) == False:
                    # user is not on cooldown
                    if data.GetParamCount() == 2: #appropriate amount of arguments
                        # see if the user wins their gamble if they have enough points or gamble everything they have
                        # depends on user input
                        try:
                            betAmount = int(data.GetParam(1))
                            if betAmount <= Parent.GetPoints(data.User): # user bet an appropriate amount
                                if isWinner():
                                    Parent.AddPoints(data.User,data.UserName,betAmount)
                                    message = settings["userWonResponse"]
                                    message = message.replace("$win", str(betAmount))
                                else:
                                    Parent.RemovePoints(data.User,data.UserName,betAmount)
                                    message = settings["userLostResponse"]
                                    message = message.replace("$loss", str(betAmount))
                                Parent.AddUserCooldown(ScriptName,ScriptName,data.User,cooldown)
                            else: #user doesn't have enough points to bet
                                message = settings["notEnoughCurrencyResponse"]
                        except:
                            if data.GetParam(1) == "all": # user wants to bet all their points
                                if isWinner():
                                    message = settings["userWonResponse"]
                                    message = message.replace("$win", str(Parent.GetPoints(data.User)))
                                    Parent.AddPoints(data.User,data.UserName,Parent.GetPoints(data.User))
                                else:
                                    Parent.RemovePoints(data.User,data.UserName,Parent.GetPoints(data.User))
                                    message = settings["userLostEverything"]
                                Parent.AddUserCooldown(ScriptName,ScriptName,data.User,cooldown)
                            else:
                                message = settings["invalidEntryResponse"]
                else:
                    message = settings["onCooldown"]
            else:
                message = settings["permissionDenied"]
    
    message = message.replace("$currency", Parent.GetCurrencyName())
    message = message.replace("$points", str(Parent.GetPoints(data.User)))
    message = message.replace("$user", data.UserName)
    message = message.replace("$cooldown", str(Parent.GetUserCooldownDuration(ScriptName,ScriptName,data.User)))
    if data.IsFromTwitch():
        Parent.SendStreamMessage(message)
    if data.IsFromDiscord():
        Parent.SendDiscordMessage(message)
    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    return