#---------------------------
#   Import Libraries
#---------------------------
import os
import sys
import clr
import json
import time
import random
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = "Raffle"
Website = "https://www.streamlabs.com"
Description = "!raffle will begin a raffle that you can !join or !cancelraffle will end after raffleTime seconds"
Creator = "TheFlippyPenguin"
Version = "1.0.0.0"

#---------------------------
#   Define Global Variables
#---------------------------
configFile = "config.json"
raffleIsLive = False
didLastMinuteCall = False
settings = {}
names = ["hello"]
ids = ["there"]
nameCount = 0
startTime = 0
raffleTime = 300
winnersPurse = 0

#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():
    global settings
    global raffleIsLive
    global didLastMinuteCall
    global names
    global ids
    global nameCount
    global winnersPurse
    
    raffleIsLive = False
    didLastMinuteCall = False
    winnersPurse = 0
    nameCount = 0
    del names[:]
    del ids[:]

    path = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
            settings = json.load(file, encoding='utf-8-sig')
    except:
        settings = {
            "startCommand": "!raffle",
            "startPermission": "Moderator",
            "stopCommand": "!cancelraffle",
            "stopPermission": "Moderator",
            "joinCommand": "!join",
            "joinPermission": "Everyone",
            "raffleStarted": "/me PogChamp A new raffle has started! Type !join to potentially win some $currency (Ends in 5 minutes) PogChamp",
            "userJoinedResponse" : "/me $user joined the raffle!",
            "userWonResponse" : "/me Congratulations $user you won $win $currency! Kreygasm",
            "notLiveResponse" : "/me Raffle isn't live right now!",
            "alreadyJoinedResponse" : "/me $user you already joined the raffle!",
            "alreadyLiveResponse": "/me $user there's already a raffle live. Type !cancelraffle to cancel current raffle",
            "permissionDenied": "/me $user you don't have permission to do that!",
            "cancelResponse": "/me The raffle has been canceled",
            "invalidEntryResponse": "/me Please enter a valid number",
            "lastCall": "/me There's only one minute left to enter the raffle! Type !join to enter if you haven't already"
            }
    
    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    global raffleIsLive
    global settings
    global names
    global ids
    global startTime
    global nameCount
    global winnersPurse
    message = ""
    
    if data.IsChatMessage():
        if data.GetParam(0).lower() == settings["joinCommand"]: # command is !join
            if raffleIsLive == False:
                # Tell user trying to join that they can't if a raffle isn't live
                message = settings["notLiveResponse"]
            else:
                if Parent.HasPermission(data.User,settings["joinPermission"],"") and ids.count(data.User) == 0:
                    # Let user join
                    message = settings["userJoinedResponse"]
                    ids.append(data.User)
                    names.append(data.UserName)
                    nameCount = nameCount + 1
                else:
                    # Tell user they've already joined
                    message = settings["alreadyJoinedResponse"]
        if data.GetParam(0).lower() == settings["startCommand"]: # command is !raffle
            if Parent.HasPermission(data.User,settings["startPermission"],""): # user has permission
                if raffleIsLive == False:
                    if data.GetParamCount() == 2:
                        # begin a new raffle and reset variables
                        try :
                            winnersPurse = int(data.GetParam(1))
                            Parent.BroadcastWsEvent("EVENT_MINE","{'show':false}")
                            message = settings["raffleStarted"]
                            raffleIsLive = True
                            didLastMinuteCall = False
                            del names[:]
                            del ids[:]
                            nameCount = 0
                            startTime = time.time()
                        except:
                            message = settings["invalidEntryResponse"]
                else:
                    # Tell user to cancel the current raffle if they want to start another
                    message = settings["alreadyLiveResponse"]
            else:
                # tell user they don't have permission
                message = settings["permissionDenied"]
        if data.GetParam(0).lower() == settings["stopCommand"]: # command is !cancelraffle
            if raffleIsLive: # only act if a raffle is currently going
                if Parent.HasPermission(data.User,settings["stopPermission"],""): # user has permission
                    raffleIsLive = False
                    message = settings["cancelResponse"]
                else:
                    # tell user they don't have permission
                    message = settings["permissionDenied"]
    
    message = message.replace("$currency", Parent.GetCurrencyName())
    message = message.replace("$user", data.UserName)
    Parent.SendStreamMessage(message)

    
    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    if raffleIsLive:
        global didLastMinuteCall
        global winnersPurse
        global raffleIsLive
        global raffleTime
        global startTime
        global nameCount
        global names
        global ids
        
        if didLastMinuteCall == False and time.time() - startTime >= raffleTime - 60:
            Parent.SendStreamMessage(settings["lastCall"])
            didLastMinuteCall = True
        if time.time() - startTime >= raffleTime:
            winner = random.randint(0,nameCount - 1)
            message = settings["userWonResponse"]
            message = message.replace("$user", names[winner])
            message = message.replace("$win", str(winnersPurse))
            message = message.replace("$currency", Parent.GetCurrencyName())
            Parent.AddPoints(ids[winner],names[winner],winnersPurse)
            Parent.SendStreamMessage(message)
            raffleIsLive = False
    return