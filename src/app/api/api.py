from flask import Flask, request

app = Flask(__name__)

# end point to recieve messages to bot from facebook
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