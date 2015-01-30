import json, os, collections
import urllib.request
from fractions import Fraction

#BEGIN CONSTANTS#
CWD = os.getcwd()
API_ROOT = "https://na.api.pvp.net/api/lol/static-data/na/v1.2/"
API_KEY = "e171bba5-29fa-41e8-a1af-2c82b601b947"
WIN_RATE_JSON = CWD + "\PositionWinRate.json"
CHAMPION_INFO_JSON = CWD + "\ChampionJson.json"
LOG_JSON = CWD + "\log.json"
#END CONSTANTS#

class CaseInsensitiveDict( collections.Mapping ):
    def __init__( self, d ):
        self._d = d
        self._s = dict( ( k.lower(), k ) for k in d )
    def __contains__( self, k ):
        return k.lower() in self._s
    def __len__( self ):
        return len( self._s )
    def __iter__( self ):
        return iter( self._s )
    def __getitem__( self, k ):
        return self._d[self._s[k.lower()]]
    def actual_key_case( self, k ):
        return self._s.get( k.lower() )

#sentence=''.join(sentence.split()) #i think this is code to remove white space
def main():
    print( "Welcome to LoL Matchups!\n" )
    win_rate_exists = os.path.isfile( WIN_RATE_JSON )
    champInfo_exists = os.path.isfile( CHAMPION_INFO_JSON )
    log_exists = os.path.isfile( LOG_JSON )
    if not ( win_rate_exists and champInfo_exists ):
        print( "Missing one of the following configuration files with the specified path:" )
        print( WIN_RATE_JSON )
        print( CHAMPION_INFO_JSON )
        print( "Exiting." )
        exit()

    if not log_exists:
        print( "Note: the log file is missing. If you have never logged historical matchup data before, don't worry!" )
        print( "But if you have, then you should track down that log file. You will be starting over without it!\n" )
    while 1:
        command = input( "Enter command: " ).lower()
        if command == "exit":
            break
        
        if command == "help":
            printHelpDialogue( "main" )
        elif  command == "version":
            versionCommand()
        elif command == "position":
            posCommand()
        elif command == "patch":
            patchCommand()
        elif command == "matchup":
            matchupCommand()
        elif command == "log":
            logCommand()
        elif command == "history":
            historyCommand()
        elif command == "champion info":
            champInfoCommand()
        else:
            print( "Invalid command. Type 'help' for a list of available commands." )
    print( "Now exiting. Thanks for using LoL Matchups." )
    exit()

def versionCommand():
    print( "0.1.4" )
    return

def patchCommand():
    print( "5.1.0" )
    return

def posCommand():
    pos = input( "Position: " ).lower()
    if exitReturnFlow( pos ):
        return

    if pos == "help":
        printHelpDialogue( "pos" )
    elif pos != "top" and pos != "mid" and pos != "adc" and pos != "sup" and pos != "jun" and pos != "fountain":
        print( "Invalid input. Type 'help' for a list of available commands." )
    else:
        posChamps( pos )
        posLoop( pos )
    return

def posChamps( pos ):
    f = open( WIN_RATE_JSON, 'r' )
    winRatePos = json.load( f )
    for champ in winRatePos[pos]:
        print( champ )
    return

def posLoop( pos ): 
    while 1:
        filt = input( "Filter: " ).lower()
        if exitReturnFlow( filt ):
            return

        if filt == "help":
            printHelpDialogue( "posLoop" )
        elif filt == "top10":
            top10PosFilter( pos )
        #elif filt == "mytop":
        #    myTopPosFilter( pos )
        else:
            print( "Invalid input. Type 'help' for a list of filters or commands" )
    return

def top10PosFilter( pos ):
    f = open( WIN_RATE_JSON, 'r' )
    winRatePos = json.load( f )
    winRatePos = CaseInsensitiveDict( winRatePos ) #change me to make more sense
    length = len( winRatePos[pos] )
    if length >= 10:
        for i in range( 10 ):
            print( winRatePos[pos][i] )
    else:
        for i in range( length ):
            print( winRatePos[pos][i] )
    return

def matchupCommand():
    f = open( CHAMPION_INFO_JSON, 'r' )
    champInfo = json.load( f )
    champInfo = CaseInsensitiveDict( champInfo ) #change me to make sense
    champ1 = ""
    champ2 = ""
    while 1:
        while 1:
            champ1 = input( "First champion: " ).lower()
            if exitReturnFlow( champ1 ):
                return

            if champ1 == "help":
                printHelpDialogue( "matchup" )
            elif not champ1 in champInfo:
                print( "Invalid champion name. Please double check the spelling is correct or type 'help' for a list of commands." )
            else:
                break
        while 1:
            champ2 = input( "Second champion: " )
            if exitReturnFlow( champ2 ):
                return

            if champ2 == "help":
                matchupHelpCommand()
            elif not champ2 in champInfo:
                print( "Invalid champion name. Please double check the spelling is correct or type 'help' for a list of commands." )
            else:
                break
        if champ2 in champInfo[champ1]["strong"]:
            print( champ1 + " is strong against " + champ2 + "." )
        elif champ2 in champInfo[champ1]["skill"]:
            print( champ1 + " has a skill matchup against " + champ2 + "." )
        elif champ2 in champInfo[champ1]["weak"]:
            print( champ1 + " is weak against " + champ2 + "." )
        else:
            print( "No matchup information between champions " + champ1 + " and " + champ2 + "." )
    return

def champInfoCommand():
    f = open( CHAMPION_INFO_JSON, 'r' )
    champInfo = json.load( f )
    while 1:
        champ = input( "Champion: " )
        if exitReturnFlow( champ ):
            return

        if champ == "help":
            printHelpDialogue( "champInfo" )
        elif not champ in champInfo:
            print( "Invalid champion name. Please double check the spelling is correct or type 'help' for a list of commands." )
        else:
            getChampInfo( champ, champInfo )
    return

def getChampInfo( champ, champInfo ):
    while 1:
        request = input( "Requested info: " ).lower()
        if exitReturnFlow( request ):
            return

        elif request == "help":
            printHelpDialogue( "champInfoLoop" )
        elif request == "all":
            strong_str = ", ".join( champInfo[champ]["strong"] )
            skill_str = ", ".join( champInfo[champ]["skill"] )
            weak_str = ", ".join( champInfo[champ]["weak"] )
            received_byte_data_allytips = urllib.request.urlopen( API_ROOT + "champion/" + str( champInfo[champ]["id"] ) + "?champData=allytips&api_key=" + API_KEY )
            allytips = json.loads( received_byte_data_allytips.read().decode("utf-8") )["allytips"]
            received_byte_data_enemytips = urllib.request.urlopen( API_ROOT + "champion/" + str( champInfo[champ]["id"] ) + "?champData=enemytips&api_key=" + API_KEY )
            enemytips = json.loads( received_byte_data_enemytips.read().decode("utf-8") )["enemytips"]
            
            print( "All information for " + champ + ":" )
            print( "Strong matchups for " + champ + ": " + strong_str + "." )
            print( "Skill matchups for " + champ + ": " + skill_str + "." )
            print( "Weak matchups for " + champ + ": " + weak_str + "." )
            print( "Tips for playing as " + champ + ":" )
            for i in range( len( allytips ) ):
                print( str( i + 1 ) + ". " + allytips[i] )
            print( "Tips for playing against " + champ + ":" )
            for i in range( len( enemytips ) ):
                print( str( i + 1 ) + ". " + enemytips[i] )
        elif request == "strong against":
            print( champ + " is strong against (unsorted):" )
            for i in range( len( champInfo[champ]["strong"] ) ):
                print( str( i + 1 ) + ". " + champInfo[champ]["strong"][i] )
        elif request == "skill":
            print( "The following are skill matchups for " + champ + ":" )
            for i in range( len( champInfo[champ]["skill"] ) ):
                print( str( i + 1 ) + ". " + champInfo[champ]["skill"][i] )
        elif request == "weak against":
            print( champ + " is weak against (unsorted):" )
            for i in range( len( champInfo[champ]["weak"] ) ):
                print( str( i + 1 ) + ". " + champInfo[champ]["weak"][i] )
        elif request == "tips for":
            received_byte_data = urllib.request.urlopen( API_ROOT + "champion/" + str( champInfo[champ]["id"] ) + "?champData=allytips&api_key=" + API_KEY )
            tips = json.loads( received_byte_data.read().decode("utf-8") )["allytips"]
            print( "Tips for playing as " + champ + ":" )
            for i in range( len( tips ) ):
                print( str( i + 1 ) + ". " + tips[i] )
        elif request == "tips against":
            received_byte_data = urllib.request.urlopen( API_ROOT + "champion/" + str( champInfo[champ]["id"] ) + "?champData=enemytips&api_key=" + API_KEY )
            tips = json.loads( received_byte_data.read().decode("utf-8") )["enemytips"]
            print( "Tips for playing against " + champ + ":" )
            for i in range( len( tips ) ):
                print( str( i + 1 ) + ". " + tips[i] )
        else:
            print( "Invalid request. Type 'help' for a list of possibe requests." )
    return

def logCommand():
    f_champInfo = open( CHAMPION_INFO_JSON, 'r' )
    
    f_log = None
    if os.path.isfile( LOG_JSON ):
        f_log = open( LOG_JSON, 'r' )
    else:
        f_log = open( LOG_JSON, 'w' )
        
    champInfo = json.load( f_champInfo )
    log_dict = {}
    if not os.stat( LOG_JSON ).st_size == 0:
        log_dict = json.load( f_log )

    while 1:
        your_champ = input( "You played as: " )
        if exitReturnFlow( your_champ ):
            return

        if your_champ == "help":
            printHelpDialogue( "logYourChamp" )
        elif not your_champ in champInfo:
            print( "Invalid champion name. Please double check the spelling is correct or type 'help' for a list of commands." )
        else:
            while 1:
                their_champ = input( "You played against: " )
                if exitReturnFlow( their_champ ):
                    return

                if their_champ == "help":
                    printHelpDialogue( "logTheirChamp" )
                elif not their_champ in champInfo:
                    print( "Invalid champion name. Please double check the spelling is correct or type 'help' for a list of commands." )
                else:
                    while 1:
                        wl = input( "Win or lose(w/l): " ).lower()
                        if exitReturnFlow( wl ):
                            return

                        if wl == "help":
                            printHelpDialogue( "wl" )
                        elif not ( wl == "w" or wl == "l" ):
                            print( "Invalid input. Valid entries are w or l." )
                        else:
                            if not your_champ in log_dict:
                                log_dict[your_champ] = {}
                            wins = None
                            total = None
                            if not their_champ in log_dict[your_champ]:
                                wins = 0
                                total = 0
                            else:
                                win_fract = log_dict[your_champ][their_champ]
                                wins = int( win_fract.split( '/' )[0] )
                                total = int( win_fract.split( '/' )[1] )
                            total += 1
                            if wl == "w":
                                wins += 1
                            log_dict[your_champ][their_champ] = str( wins ) + "/" + str( total )
                                
                            print( "Beginning write to log file." )
                            f_log.close()
                            f_log = open( LOG_JSON, 'w' )
                            json.dump( log_dict, f_log, indent='\t' )
                            print( "Write complete." )
                            return
    return

def historyCommand():
    f = open( LOG_JSON, 'r' )
    log_dict = json.load( f )
    while 1:
        champ = input( "View your history for champion: " )

        if exitReturnFlow( champ ):
            return

        if champ == "help":
            printHelpDialogue( "history" )
        elif not champ in log_dict:
            print( "You have no logged win/loss information for this champion or you input the name incorrectly. Please double check the spelling before trying again." )
        else:
            sorted_dict = collections.OrderedDict( sorted( log_dict[champ].items() ) )
            for champ_key in sorted_dict:
                print( champ_key + ": " + sorted_dict[champ_key] )
                
            while 1:
                filt = input( "Filter: " )

                if exitReturnFlow( filt ):
                    return

                if filt == "help":
                    printHelpDialogue( "historyFilter" )
                elif filt == "all":
                    for champ_key in sorted_dict:
                        print( champ_key + ": " + sorted_dict[champ_key] )
                elif filt == "top 5 win":
                    count = 0
                    sorted_by_win = sorted( log_dict[champ].items(), key = lambda champ_tuple: Fraction( champ_tuple[1] ), reverse = True )
                    for champ_tuple in sorted_by_win:
                        count += 1
                        print( str( count ) + ". " + champ_tuple[0] + ": " + champ_tuple[1] )
                        if count == 5 :
                            break
                elif filt == "top 5 loss":
                    count = 0
                    sorted_by_loss = sorted( log_dict[champ].items(), key = lambda champ_tuple: Fraction( champ_tuple[1] ) )
                    for champ_tuple in sorted_by_loss:
                        count += 1
                        print( str( count ) + ". " + champ_tuple[0] + ": " + champ_tuple[1] )
                        if count == 5:
                            break
                elif not filt in log_dict[champ]:
                    print( "Filter or champion does not exist. Type 'help' for a list of commands or make sure the champion name spelling is correct." )
                else:
                    print( filt + ": " + log_dict[champ][filt] )
    return

"""
Function exitReturnFlow
Helper function called after every user input to see if the user had entered "exit" or "return" to go back up the execution
@param u_input {str} user input string to be compared against
@return {boolean} returns boolean for if the parent function should return
"""
def exitReturnFlow( u_input ):
    if u_input == "exit":
        exit()
    elif u_input == "return":
        return True
    return False

def printHelpDialogue( source ):
    print( "Available commands:" )

    if source == "main":
        print( "position" )
        print( "matchup" )
        print( "log" )
        print( "history" )
        print( "champion info" )
        print( "patch" )
        print( "version" )
    elif source == "pos":
        print( "top" )
        print( "jun" )
        print( "mid" )
        print( "adc" )
        print( "sup" )
        print( "fountain" )
    elif source == "champInfo" or source == "matchup" or source == "logYourChamp" or source == "logTheirChamp" or source == "history":
        print( "<champion name>" )
    elif source == "champInfoLoop":
        print( "all" )
        print( "strong against" )
        print( "skill" )
        print( "weak against" )
        print( "tips for" )
        print( "tips against" )
    elif source == "wl":
        print( "w" )
        print( "l" )

    print( "help" )
    if source != "main":
        print( "return" )
    print( "exit" )

    if source == "posLoop":
        print( "Available filters:" )
        print( "top10" )
        #print( "mytop" )
    elif source == "historyFilter":
        print( "Available filters:" )
        print( "all" )
        print( "top 5 win" )
        print( "top 5 loss" )
        print( "<champion name>" )
    return

main()
