import requests
import json
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import spacy
import datetime as dt

#import dictionaries 
from importData import bundesländerImport, landkreiseImport, bundesländerRegelnImport
bundesländer = bundesländerImport
bundesländerRegeln = bundesländerRegelnImport 
landkreise = landkreiseImport

#set all commands
commands = { 
    'start'       : 'Get used to the bot',
    'help'        : 'Zeigt alle verfügbaren commands',
}

#set the key figures for the counties in a dict
kennzahlenLK = {"fall": "cases", "fälle": "cases", "infektionen": "cases", "tod":"deaths", "fsall je 100000 einwohner":"'cases_per_100k'", "einwohner": 'EWZ', "einwohnerzahl": 'EWZ',
              "7 tage inzidenz" :'cases7_per_100k_txt', "inzidenz":'cases7_per_100k_txt', "fälle der letzt 7 tag": 'cases7_lk', "fallzahl der letzte 7 tag": 'cases7_lk'
              , "fälle letzte 7 tag": 'cases7_lk', "fälle letzte woche": 'cases7_lk', "infektionen letzte woche": 'cases7_lk', "infektionen letzte 7 tag": 'cases7_lk', 
              "tode der letzte 7 tag": 'death7_lk', "tode der letzt woche": 'death7_lk'}

#set the key figures for the federal states in a dict
kennzahlenBL = {"fall": "Fallzahl", "fälle": "Fallzahl", "infektionen": "Fallzahl", "tod":"Death", "fall je 100000 einwohner":"faelle_100000_EW", "einwohner": 'LAN_ew_EWZ', "einwohnerzahl": 'LAN_ew_EWZ',
              "7 tage inzidenz" :"cases7_bl_per_100k_txt", "inzidenz":"cases7_bl_per_100k_txt", "fälle der letzt 7 tag": "cases7_bl", "fallzahl der letzte 7 tag": "cases7_bl"
              , "fälle letzte 7 tag": "cases7_bl", "fälle letzte woche": "cases7_bl" , "infektionen letzte woche": "cases7_bl", "infektionen letzte 7 tag": "cases7_bl"
              ,  "tode der letzte 7 tag": "death7_bl", "tode der letzt woche": "death7_bl", 
              "regeln": "Fallzahl", "beschränkungen": "Fallzahl", "regel": "Fallzahl", "verordnung":"Fallzahl"}
#load german spacy library 
nlp = spacy.load('de_core_news_sm')

#save the unique telegram bot token and import telebot 
tokenTelegram = '<insert token here>'
bot = telebot.TeleBot(tokenTelegram)

#list to save user IDs
userID =[]

#function to set actions when bot is started the first time or /start command gets called
@bot.message_handler(commands=['start'])
def command_start(message):
	ID = message.chat.id
	bot.send_message(ID, "Willkomen zum CoronaBot! Hier kannst du alle aktuellen Informationen zu Corona in den Deutschen Landkreisen und Bundesländern erfahren. \n Zum Beispiel kannst du einfach 'Corona in Sachsen' oder auch über spezifischere Dinge wie die Inzidenz im Ostalbkreis fragen!")
	command_help(message)

#function to set actions when /help command is called
@bot.message_handler(commands=['help'])
def command_help(message):
	ID = message.chat.id
	help_text = "Die folgenden Antworten sind für alle Bundesländer und Landkreise verfügbar: \n -Gesamtüberblick \n -Inzidenz \n -Todesfälle \n -Todesfälle der letzten 7 Tage \n -Fallzahl gesamt \n -Fallzahl letzte 7 Tage \n -Einwohnerzahl"
	bot.send_message(ID, help_text)  # send the generated help page

#main function to handle all the incoming messages from telegram user 
@bot.message_handler(func=lambda m: True)
def messageHandler(message):
    userID.append(message.chat.id) #save userID in userID list to call from other functions
    bundeslandBenutzung = False
    landkreisBenutzung = False
    messageString = str(message.text) #parse input text to string
    nlp = spacy.load('de_core_news_sm')
    doc = nlp(messageString) #load input test in spacy
    for token in doc:
        messageString = " ".join(token.lemma_ for token in doc) #lemmatize messageString
    messageStringLower = messageString.lower() #set messageString to lower to avoid uppercase/lowercase mistakes
    ID = message.chat.id 
    for bundesland, bundeslandID in bundesländer.items(): #iterate through bundesländer dict to check if input message contains a valid federal county
        #if a valid federal county gets found in input message call getBundesland function 
        if messageStringLower.find(bundesland)!= -1:
            bundeslandAktuell=bundesland
            getBundesland(bundeslandID, bundeslandAktuell ,messageStringLower, ID)
            bundeslandBenutzung = True
            break
    #if no valid federal county gets detected set bundeslandBenutzung false and check if message contains valid counties
    if bundeslandBenutzung== False: 
        for landkreis, landkreisID in landkreise.items(): #iterate through landkreise dict to check if input message contains a valid county
            #if a valid county gets found in input message call getLandkreis function 
            if messageStringLower.find(landkreis)!= -1:
                landkreisAktuell = landkreis
                landkreisBenutzung = True
                getLandkreis(landkreisID,landkreisAktuell, messageStringLower, ID)
    #if input message contains a greeting send greeting back and call /help function
    if (messageStringLower.find("hi")!= -1 or messageStringLower.find("hallo")!= -1 or messageStringLower.find("servus")!= -1 or messageStringLower.find("wie geht")!= -1) and bundeslandBenutzung == False and landkreisBenutzung ==False:
        bot.send_message(message.chat.id, "Hallo! Wie kann ich dir helfen?")
        command_help(message)
        botBegrüssung = True
    else:
        botBegrüssung = False
    #if no federal county, county or greeting gets detected send error message
    if bundeslandBenutzung== False and botBegrüssung == False and landkreisBenutzung == False:    
        bot.send_message(message.chat.id, '"' + message.text + '" ' + "ist eine ungültige Eingabe, \n versuche /help für mehr Optionen.")
        #set keyboard buttons in tuple to give users a few suggestions
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Corona Lage Baden-Württemberg",callback_data=1)],
            [InlineKeyboardButton(text="Inzidenz im Rems-Murr-Kreis",callback_data=2)],
            [InlineKeyboardButton(text="Corona Fälle der letzten 7 Tage im Ostalbkreis",callback_data=3)]
            ])        
        bot.send_message(message.chat.id, "Oder probiere einfach die folgenden Eingaben:", reply_markup=keyboard)
             
#function to get data and check message if federal county gets detected
def getBundesland(bundeslandID, bundeslandAktuell, message, ID):
    bundesländerRegeln = bundesländerRegelnImport[bundeslandID]
    kennzahlenBenutzungBL = False
    #get data from RKI API
    url="https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/Coronaf%C3%A4lle_in_den_Bundesl%C3%A4ndern/FeatureServer/0/query?"
    bl_id=bundeslandID #set bundesland ID to get correct API call 
    bundeslandBenutzung=True
    parameter={
    'referer':'https://www.mywebapp.com',
    'user-agent':'python-requests/2.9.1',
    'where': f'OBJECTID_1 = {bl_id}', #get federal county which was found in message
    'outFields': '*', #get all fields from API call
    'returnGeometry': False, #dont return geometry
    'f':'json', #get JSON
    'cacheHint': True
    }
    result = requests.get(url=url, params=parameter) #call API request
    resultsBundesländer = json.loads(result.text) #save JSON in python dict
    suche = "" #set kennzahl to default value
    #set timestamp from API result
    timestamp = resultsBundesländer['features'][0]['attributes']["Aktualisierung"] 
    timestampInt = int(timestamp) /1000

    for kennzahlenDE, kennzahlenAPI in kennzahlenBL.items(): #iterate through kennzahlenBL dict to check if input message contains a valid key figure
        #check if message contains key figures from kennzahlenBL dict
        if (message.find(kennzahlenDE) != -1) and (bundeslandBenutzung == True):
            messageStringLower = message #set message to messageStringLower
            kennzahlenBenutzungBL = True
            suche = kennzahlenAPI
            var =  resultsBundesländer['features'][0]['attributes'][suche] #set var according to found key figure
            bundeslandCapitalized = bundeslandAktuell.capitalize() #capitalize the federal counties again
            #check again for certain words and set right value 
            if messageStringLower.find("tod") != -1 and messageStringLower.find("7") != -1:
                var =  str(resultsBundesländer['features'][0]['attributes']["death7_bl"])
                bot.send_message(ID, "Tode durch Corona in den letzten 7 Tagen in " + bundeslandCapitalized + ": " + var + "\n" + "Letzte Aktualisierung: " + dt.datetime.utcfromtimestamp(timestampInt).strftime('%d %B %Y'))
                break
            if messageStringLower.find("tod") != -1 and messageStringLower.find("woche") != -1:
                var =  str(resultsBundesländer['features'][0]['attributes']["death7_bl"])
                bot.send_message(ID, "Tode durch Corona in der letzten Woche in " + bundeslandCapitalized + ": " + var + "\n"  + "Letzte Aktualisierung: " + dt.datetime.utcfromtimestamp(timestampInt).strftime('%d %B %Y'))
                break
            if messageStringLower.find("tod")!= -1:
                var =  str(resultsBundesländer['features'][0]['attributes']["Death"])
                bot.send_message(ID, "Tode durch Corona in " + bundeslandCapitalized + ": " + var + "\n"  +  "Letzte Aktualisierung: " + dt.datetime.utcfromtimestamp(timestampInt).strftime('%d %B %Y'))
                break
            if messageStringLower.find("inzidenz" or "7 tage inzidenz")!= -1:
                bot.send_message(ID, "7 Tage Inzidenz in " + bundeslandCapitalized + ": " + var + "\n"  +  "Letzte Aktualisierung: " + dt.datetime.utcfromtimestamp(timestampInt).strftime('%d %B %Y'))
                break
            if messageStringLower.find("fälle der letzte 7 tag"  or "fallzahl der letzte 7 tag" or "letzte 7 tag" or "infektion") and messageStringLower.find("7")!= -1:
                var =  str(resultsBundesländer['features'][0]['attributes']["cases7_bl"])
                bot.send_message(ID, "Fallzahlen in " + bundeslandCapitalized + " der letzten 7 Tage" + ": " + var + " Fälle " + "\n"  + "Letzte Aktualisierung: " + dt.datetime.utcfromtimestamp(timestampInt).strftime('%d %B %Y'))
                break
            if  messageStringLower.find("woche")!= -1:
                if messageStringLower.find("fälle") != -1 or messageStringLower.find("fallzahl") != -1 or messageStringLower.find("infektion")!= -1:
                    var =  str(resultsBundesländer['features'][0]['attributes']["cases7_bl"])
                    bot.send_message(ID, "Fallzahlen in " + bundeslandCapitalized + " der letzten Woche" + ": " + var + " Fälle" + "\n"  +  "Letzte Aktualisierung: " + dt.datetime.utcfromtimestamp(timestampInt).strftime('%d %B %Y'))
                break
            if messageStringLower.find("fälle")!= -1 or messageStringLower.find("fallzahl")!= -1 or messageStringLower.find("fall")!= -1 or messageStringLower.find("infektion")!= -1:
                var = str(var)
                bot.send_message(ID, "Fallzahlen in " + bundeslandCapitalized + " seit Beginn der Pandemie" + ": " + parseFallzahl(var) + " Fälle" + "\n"  +  "Letzte Aktualisierung: " + dt.datetime.utcfromtimestamp(timestampInt).strftime('%d %B %Y'))
                break  
            if messageStringLower.find("einwohnerzahl") != -1  or messageStringLower.find("einwohner")!= -1:
                var = str(var)
                bot.send_message(ID, "Einwohner in " + bundeslandCapitalized + ": " + parseEinwohnerzahl(var) + "\n"  + "Letzte Aktualisierung: " + dt.datetime.utcfromtimestamp(timestampInt).strftime('%d %B %Y')) 
                break
            if messageStringLower.find("regeln") != -1  or messageStringLower.find("beschränkungen")!= -1 or messageStringLower.find("verordnung")!= -1:
                var = str(var)
                bot.send_message(ID, "Aktuelle Regelungen und Beschränkungen:" + "\n"  + bundesländerRegeln) 
                break
    #if no key figure got found output a overview of the found federal county
    if bundeslandBenutzung == True and kennzahlenBenutzungBL ==False:
        outputHeader = str(resultsBundesländer['features'][0]['attributes']['LAN_ew_GEN'])
        outputInzidenz= str(resultsBundesländer['features'][0]['attributes']['cases7_bl_per_100k_txt'])
        outputEinwohnerzahl = str(resultsBundesländer['features'][0]['attributes']['LAN_ew_EWZ'])
        #parse outputEinwohnerzahl for better readability
        outputEinwohnerzahlParsed = parseEinwohnerzahl(outputEinwohnerzahl)
        outputFallzahl = str(resultsBundesländer['features'][0]['attributes']["Fallzahl"])
        #parse outputFallzahl for better readability
        outputFallzahlParsed = parseFallzahl(outputFallzahl)
        outputFallzahl1000Parsed = '%.2f' % resultsBundesländer['features'][0]['attributes']["faelle_100000_EW"]
        outputFallzahl1000= str(outputFallzahl1000Parsed)
        outputFälle7Tage= str( resultsBundesländer['features'][0]['attributes']['cases7_bl'])
        outputTodesfälleGesamt= str( resultsBundesländer['features'][0]['attributes']["Death"])
        outputTodesfälle7Tage = str(resultsBundesländer['features'][0]['attributes']['death7_bl'])
        #send overview back to user
        outputStringBL = outputHeader + ":" + "\n" + "Inzidenz: " + outputInzidenz + "\n" + "Einwohnerzahl: " + outputEinwohnerzahlParsed + "\n"+ "Fallzahl insgesamt: " + outputFallzahlParsed + "\n"+ "Fallzahl je 100.000 Einwohner: " + outputFallzahl1000 + "\n" + "Fälle der letzten 7 Tage: "+ outputFälle7Tage + "\n" + "Todesfälle insgesamt: " + outputTodesfälleGesamt + "\n" + "Todesfälle der letzten 7 Tage: " + outputTodesfälle7Tage + "\n" + "\n" + "Aktuelle Regeln und Beschränkungen: " + "\n" + bundesländerRegeln
        bot.send_message(ID, outputStringBL + "\n" + "\n" + "Letzte Aktualisierung: " + dt.datetime.utcfromtimestamp(timestampInt).strftime('%d %B %Y'))
    
#function to get data and check message if county gets detected
def getLandkreis(landkreisID, landkreisAktuell, message, ID):
    kennzahlenBenutzungLK = False
    landkreisBenutzung = True
    #get data from RKI API
    url= "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?"
    lk_id = landkreisID #set landkreis ID to get correct API call 
    parameter = {
    'referer':'https://www.mywebapp.com',
    'user-agent':'python-requests/2.9.1',
    'where': f'OBJECTID = {lk_id}', #get county which was found in message
    'outFields': '*', #get all fields from API call
    'returnGeometry': False, #dont return geometry
    'f':'json', #get JSON
    'cacheHint': True
    }
    resultLK = requests.get(url=url, params=parameter) #call API request
    resultsLandkreise = json.loads(resultLK.text) #save JSON in python dict
    timestampLK = resultsLandkreise['features'][0]['attributes']['last_update']

    for kennzahlenDE, kennzahlenAPI in kennzahlenLK.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if (message.find(kennzahlenDE) != -1):
            kennzahlenBenutzungLK = True
            messageStringLower = message #set message to messageStringLower
            suche = kennzahlenAPI
            var =  resultsLandkreise['features'][0]['attributes'][suche] #set var according to found key figure
            landkreisCapitalized = landkreisAktuell.capitalize()  #capitalize the counties again
            #check again for certain words and set right value 
            if messageStringLower.find("tod") != -1 and messageStringLower.find("7") != -1:
                var =  str(resultsLandkreise['features'][0]['attributes']['death7_lk'])
                bot.send_message(ID, "Tode durch Corona in den letzten 7 Tagen in " + landkreisCapitalized + ": " + var + "\n" + "Letzte Aktualisierung: " + timestampLK)
                break
            if messageStringLower.find("tod") != -1 and messageStringLower.find("woche") != -1:
                var =  str(resultsLandkreise['features'][0]['attributes']['death7_lk'])
                bot.send_message(ID, "Tode durch Corona in der letzten Woche in " + landkreisCapitalized + ": " + var + "\n" + "Letzte Aktualisierung: " + timestampLK)
                break
            if messageStringLower.find("tod")!= -1:
                var =  str(resultsLandkreise['features'][0]['attributes']["deaths"])
                bot.send_message(ID, "Tode durch Corona in " + landkreisCapitalized + ": " + var + "\n" + "Letzte Aktualisierung: " + timestampLK)
                break
            if messageStringLower.find("inzidenz" or "7 tage inzidenz")!= -1:
                print("test")
                bot.send_message(ID, "7 Tage Inzidenz in " + landkreisCapitalized + ": " + var + "\n" + "Letzte Aktualisierung: " + timestampLK)
                break
            if messageStringLower.find("fälle der letzte 7 tag"  or "fallzahl der letzte 7 tag" or "letzte 7 tag" or "infektion") and messageStringLower.find("7")!= -1:
                var =  str(resultsLandkreise['features'][0]['attributes']['cases7_lk'])
                bot.send_message(ID, "Fallzahlen in " + landkreisCapitalized + " der letzten 7 Tage" + ": " + var + " Fälle " + "\n" + "Letzte Aktualisierung: " + timestampLK)
                break
            if  messageStringLower.find("woche")!= -1:
                if messageStringLower.find("fälle") != -1 or messageStringLower.find("fallzahl") != -1 or messageStringLower.find("infektion") != -1:
                    var =  str(resultsLandkreise['features'][0]['attributes']['cases7_lk'])
                    bot.send_message(ID, "Fallzahlen in " + landkreisCapitalized + " der letzten Woche" + ": " + var + " Fälle" + "\n" + "Letzte Aktualisierung: " + timestampLK)
                break
            if messageStringLower.find("fälle")!= -1 or messageStringLower.find("fallzahl")!= -1 or messageStringLower.find("fall")!= -1 or messageStringLower.find("infektion")!= -1:
                var = str(var)
                bot.send_message(ID, "Fallzahlen in " + landkreisCapitalized + " seit Beginn der Pandemie" + ": " + parseFallzahl(var) + " Fälle" + "\n" + "Letzte Aktualisierung: " + timestampLK)
                break  
            if messageStringLower.find("einwohnerzahl") != -1  or messageStringLower.find("einwohner")!= -1:
                var = str(var)
                bot.send_message(ID, "Einwohner in " + landkreisCapitalized + ": " + parseEinwohnerzahl(var) + "\n" + "Letzte Aktualisierung: " + timestampLK)
                break
    #if no key figure got found output a overview of the found county
    if landkreisBenutzung == True and kennzahlenBenutzungLK ==False:
        outputHeader = str(resultsLandkreise['features'][0]['attributes']['GEN'])
        outputInzidenz= str(resultsLandkreise['features'][0]['attributes']['cases7_per_100k_txt'])
        outputEinwohnerzahl = str(resultsLandkreise['features'][0]['attributes']['EWZ'])
        #parse outputEinwohnerzahl for better readability
        outputEinwohnerzahlParsed =parseEinwohnerzahl(outputEinwohnerzahl)
        outputFallzahl = str(resultsLandkreise['features'][0]['attributes']["cases"])
        #parse outputFallzahl for better readability
        outputFallzahlParsed = parseFallzahl(outputFallzahl)
        outputFallzahl1000 = '%.2f' % resultsLandkreise['features'][0]['attributes']['cases_per_100k']
        outputFallzahl1000Parsed = str(outputFallzahl1000)
        outputFälle7Tage= str(resultsLandkreise['features'][0]['attributes']['cases7_lk'])
        outputTodesfälleGesamt= str(resultsLandkreise['features'][0]['attributes']["deaths"])
        outputTodesfälle7Tage = str(resultsLandkreise['features'][0]['attributes']['death7_lk'])
        outputBundesland= str(resultsLandkreise['features'][0]['attributes']['BL'])
        outputInzidenzBundesland = '%.2f' % resultsLandkreise['features'][0]['attributes']['cases7_bl_per_100k']
        outputInzidenzBundeslandParsed = str(outputInzidenzBundesland)

        #send overview back to user
        outputStringLK = outputHeader + ":" + "\n" + "Inzidenz: " + outputInzidenz + "\n" + "Einwohnerzahl: " + outputEinwohnerzahlParsed + "\n"+ "Fallzahl insgesamt: " + outputFallzahlParsed + "\n"+ "Fallzahl je 100.000 Einwohner: " + outputFallzahl1000Parsed + "\n" + "Fälle der letzten 7 Tage: "+ outputFälle7Tage + "\n" + "Todesfälle insgesamt: " + outputTodesfälleGesamt + "\n" + "Todesfälle der letzten 7 Tage: " + outputTodesfälle7Tage + "\n" + "Bundesland: " + outputBundesland + "\n" + "Bundesland Inzidenz : " + outputInzidenzBundeslandParsed
        bot.send_message(ID, outputStringLK + "\n" + "\n" + "Letzte Aktualisierung: " + timestampLK) 

#function to return keyboard buttons
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id, text='')
    #call the right function according to which buttons gets pressed form user
    if call.data=="1":
        getBundesland(8 ,"Baden-Württemberg" ,"Baden-Württemberg", userID[0])
    if call.data=="2":
        getLandkreis(184 ,"rems-murr-kreis" ,"inzidenz rems-murr-kreis", userID[0])
    if call.data=="3":
        getLandkreis(191 ,"ostalbkreis" ,"fälle der letzten 7 tage im ostalbkreis", userID[0])

#function to parse Einwohnerzahl for better readability
def parseEinwohnerzahl(outputEinwohnerzahl):
    if len(outputEinwohnerzahl) ==8:
        outputEinwohnerzahlParsed = outputEinwohnerzahl[:2] + ' ' + outputEinwohnerzahl[2:]
        outputEinwohnerzahlParsed2 =  outputEinwohnerzahlParsed[:6] + ' ' + outputEinwohnerzahlParsed[6:]
        return outputEinwohnerzahlParsed2
    if len(outputEinwohnerzahl) ==7:
        outputEinwohnerzahlParsed = outputEinwohnerzahl[:1] + ' ' + outputEinwohnerzahl[1:]
        outputEinwohnerzahlParsed2 =  outputEinwohnerzahlParsed[:5] + ' ' + outputEinwohnerzahlParsed[5:]
        return outputEinwohnerzahlParsed2
    if len(outputEinwohnerzahl) ==6:
        outputEinwohnerzahlParsed = outputEinwohnerzahl[:3] + ' ' + outputEinwohnerzahl[3:]
        return outputEinwohnerzahlParsed
    else:
        return outputEinwohnerzahl

#function to parse Fallzahl for better readability
def parseFallzahl(outputFallzahl):
    if len(outputFallzahl) ==7:
        outputFallzahl= outputFallzahl[:4] + ' ' + outputFallzahl[4:]
        return outputFallzahl
    if len(outputFallzahl) ==6:
        outputFallzahl= outputFallzahl[:3] + ' ' + outputFallzahl[3:]
        return outputFallzahl
    if len(outputFallzahl) ==5:
        outputFallzahl= outputFallzahl[:2] + ' ' + outputFallzahl[2:]
        return outputFallzahl
    else:
        return outputFallzahl

#start bot 
bot.polling()