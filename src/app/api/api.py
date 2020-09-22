from flask import Flask, request
from pymessenger.bot import Bot
from utilities.amazon.amazon_services import (
    get_amazon_search_page,
    send_amazon_url_as_message,
)
from utilities.core_utilities import read_commands_from_yaml_file
from utilities.facebook.facebook_services import (
    get_username,
    send_message,
    verify_fb_token,
)
from utilities.goodreads.goodreads_services import get_books_list, get_reviews_url_by_id
from utilities.ibm.ibm_services import ibm_watson_suggestion
from utilities.messages import GREETINGS_EXCEPTION, MESSAGE_PROCESSED

# reading credentials from yaml file
yaml_file = "./credentials.yaml"
commands_dict = read_commands_from_yaml_file(yaml_file)
ACCESS_TOKEN = commands_dict["ACCESS_TOKEN"]

app = Flask(__name__)
bot = Bot(ACCESS_TOKEN)

# end point to recieve messages to bot from facebook
@app.route("/", methods=["GET", "POST"])
def receive_message():
    if request.method == "GET":
        # to verify the page access token
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        bag_of_single_words = [
            "hi",
            "hai",
            "hello",
            "bye",
            "sorry",
            "welcome",
            "why",
            "what",
            "when",
            "How",
            "ok",
            "okay",
        ]
        for event in output["entry"]:
            messaging = event["messaging"]
            for message in messaging:
                if message.get("message"):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message["sender"]["id"]
                try:
                    message["message"]
                    if message["message"].get("text"):
                        # greeting identifier
                        # added exceptions to identify greetings, bye and thanks
                        greetings, response_sent_text = greeting_and_emotions_finder(
                            message, recipient_id
                        )
                        if greetings == True:
                            send_message(bot, recipient_id, response_sent_text)
                        elif greetings == False:
                            splitted_message_text = message["message"]["text"].split(
                                " "
                            )
                            if (
                                len(splitted_message_text) == 1
                                and splitted_message_text[0] not in bag_of_single_words
                            ):
                                response_sent_text = get_books_list(
                                    splitted_message_text[0]
                                )
                                send_message(
                                    bot,
                                    recipient_id,
                                    response_sent_text,
                                    generic_message=1,
                                )
                            else:
                                response_sent_text = default_message()
                                send_message(bot, recipient_id, response_sent_text)
                except KeyError:
                    recipient_id = message["sender"]["id"]
                    # to get username
                    username = get_username(recipient_id)
                    message["postback"]["payload"]
                    user_selected_book_id = message["postback"]["payload"].split("-")[0]
                    user_selected_book_name = message["postback"]["payload"].split("-")[
                        1
                    ]

                    book_review_url = get_reviews_url_by_id(user_selected_book_id)
                    suggestion = ibm_watson_suggestion(book_review_url)
                    if suggestion:
                        response_sent_text = (
                            "Hey %s,I Just done analyze the review you can buy this ! :)"
                            % (username)
                        )
                        send_message(bot, recipient_id, response_sent_text)
                        amazon_url = get_amazon_search_page(user_selected_book_name)
                        send_amazon_url_as_message(
                            bot, recipient_id, user_selected_book_name, amazon_url
                        )
                    else:
                        response_sent_text = (
                            "Hey %s, The reviews are not that good dont buy this :("
                            % (username)
                        )
                        send_message(bot, recipient_id, response_sent_text)
    return MESSAGE_PROCESSED


# greeting and thanks finder
def greeting_and_emotions_finder(message, recipient_id):
    response_sent_text = ""
    username = get_username(recipient_id)
    try:
        message["message"]["nlp"]["entities"]["greetings"]
        response_sent_text = "hey ! %s, Please send me a book name or ID" % (username)
    except KeyError:
        raise GREETINGS_EXCEPTION
    try:
        message["message"]["nlp"]["entities"]["bye"]
        response_sent_text = "Bye ! %s Take care !" % (username)
    except KeyError:
        raise GREETINGS_EXCEPTION
    try:
        message["message"]["nlp"]["entities"]["thanks"]
        response_sent_text = "You're welcome %s!" % (username)
    except KeyError:
        raise GREETINGS_EXCEPTION

    if response_sent_text:
        greetings = True
    else:
        greetings = False

    return greetings, response_sent_text


if __name__ == "__main__":
    app.run(debug=True)
