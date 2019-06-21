#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from pymessenger.bot import Bot
from pymessenger import Button
import requests
from xml.etree import ElementTree
import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, \
KeywordsOptions, SentimentOptions, SemanticRolesOptions, EmotionOptions
from credentials import ACCESS_TOKEN, VERIFY_TOKEN, API_KEY, IBM_URL, GOODREADS_API_KEY, GOODREADS_SECRET

app = Flask(__name__)

bot = Bot(ACCESS_TOKEN)

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        # to verify the page access token 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        bag_of_single_words = ["hi", "hai", "hello", "bye", "sorry", "welcome", "why", "what", "when", "How", "ok", "okay"]
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                print(message)
                if message.get('message'):
                    #Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    print ("receipient id ")
                    print (recipient_id)
                    
                try:
                    message['message']
                    if message['message'].get('text'):
                        #greeting identifier
                        # added exceptions to identify greetings, bye and thanks
                        greetings, response_sent_text = greeting_and_emotions_finder(message,recipient_id)
                        if greetings==True:
                            send_message(recipient_id, response_sent_text)
                        elif greetings==False:
                            splitted_message_text = message['message']['text'].split(' ')  
                            if len(splitted_message_text)==1 and splitted_message_text[0] not in bag_of_single_words:
                                print (type(splitted_message_text[0]))
                                print (splitted_message_text[0])
                                response_sent_text = get_books_list(splitted_message_text[0])
                                send_message(recipient_id, response_sent_text, generic_message=1)
                            else:
                                response_sent_text = default_message()
                                send_message(recipient_id, response_sent_text)
                except KeyError:
                    recipient_id = message['sender']['id']
                    #to get username
                    username = get_username(recipient_id)
                    # import pdb; pdb.set_trace()
                    message['postback']['payload']
                    user_selected_book_id = message['postback']['payload'].split('-')[0]
                    user_selected_book_name = message['postback']['payload'].split('-')[1]

                    book_review_url = get_reviews_url_by_id(user_selected_book_id)    
                    suggestion=ibm_watson_suggestion(book_review_url)
                    if suggestion:
                        response_sent_text = "Hey %s,I Just done analyze the review you can buy this ! :)" % (username)
                        send_message(recipient_id, response_sent_text)
                        amazon_url = get_amazon_search_page(user_selected_book_name)
                        print("printing the amaonz url")
                        print(amazon_url)
                        send_amazon_url_as_message(recipient_id,user_selected_book_name,amazon_url)
                    else:
                        response_sent_text = "Hey %s, The reviews are not that good dont buy this :(" % (username)   
                        send_message(recipient_id, response_sent_text)
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


# get a list of book up to 5 numbers for the given book name
def get_books_list(book_name):
    elements = []
    url = "https://www.goodreads.com/search/index.xml?key=" + GOODREADS_API_KEY + "&" + "q" + "=" + book_name
    print(url)
    response = requests.get(url = url)
    tree = ElementTree.fromstring(response.content)
    title = [title.text for title in tree.iter("title")][0:5]
    image = [image.text for image in tree.iter("small_image_url")][0:5]
    title_image_dict = dict(zip(title, image))
    for title, image_url in title_image_dict.items():
        id_as_payload_value = image_url.rsplit('/')[-1].split('.')[0]
        element = {
            "title":title,
            "image_url":image_url,
            
            "buttons":[
              {
                "type":"postback",
                "title":title,
                "payload":id_as_payload_value + "-" + title
              }         
            ]    
        }    
        elements.append(element)
    return elements

def get_amazon_search_page(book_name):
    url = "https://www.amazon.in/s?k={0}&ref=nb_sb_noss_2".format(book_name)
    return url

#function to get id for a book and generate url to feed to IBM watson
def get_reviews_url_by_id(book_id):
    good_reads_review_url = "https://www.goodreads.com/book/show/%s#other_reviews" % (book_id)
    return good_reads_review_url


# function to get facebook user's first name 
def get_username(recipient_id):
    url = "https://graph.facebook.com/%s?fields=first_name&access_token=%s" % (recipient_id, ACCESS_TOKEN)
    response = requests.get(url)
    username = str(response.json()['first_name'])
    return username    

# IBM watson analysis logic
def ibm_watson_suggestion(url):
    service = NaturalLanguageUnderstandingV1(
    version='2018-03-16',
    url=IBM_URL,
    iam_apikey=API_KEY)

    # to analyze the review
    response = service.analyze(
    url=url,
    features=Features(sentiment=SentimentOptions())).get_result()
    label_value = response['sentiment']['document']['label']
    if label_value == "positive":
        suggestion = True
        print ("you can buy this !")
    else:
        suggestion = False
        print ("don't buy this")    
    return suggestion


# greeting and thanks finder 
def greeting_and_emotions_finder(message,recipient_id):
    response_sent_text = ''
    username = get_username(recipient_id)
    try: 
        message['message']['nlp']['entities']['greetings']
        response_sent_text = "hey ! %s, Please send me a book name or ID" % (username)
    except KeyError:
        pass  
    try:
        message['message']['nlp']['entities']['bye']
        response_sent_text = "Bye ! %s Take care !" % (username)
    except KeyError:
        pass
    try:
        message['message']['nlp']['entities']['thanks']
        response_sent_text = "You're welcome %s!" % (username) 
    except KeyError:
        pass

    if response_sent_text:
        greetings = True 
    else:
        greetings = False  
             
    return greetings, response_sent_text    

def send_amazon_url_as_message(recipient_id, book_name, amazon_url):
    elements = []
    element = {

            "title":book_name,
            "image_url":"https://img.icons8.com/material-rounded/24/000000/amazon.png",

            "buttons":[
                  {
                    "type":"web_url",
                    "url": amazon_url,
                    "title":"View"
                    
                  }         
                ]    
              }  
    elements.append(element)
    bot.send_generic_message(recipient_id, elements)
    return "success" 



#uses PyMessenger to send response to user
def send_message(recipient_id, response, generic_message=None):
    #sends user the text message provided via input response parameter
    if generic_message:
        bot.send_generic_message(recipient_id, response)
    else:
        bot.send_text_message(recipient_id, response)
    return "success"

def default_message():
    return "Hai ! im Just a fb bot to get books suggestion based on good reads review at very rudimentary level ! I can't get you sometimes :( "    

if __name__ == "__main__":
    app.run()