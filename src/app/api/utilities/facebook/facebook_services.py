import yaml

from ..core_utilities import read_commands_from_yaml_file

# reading credentials from yaml file
yaml_path = "utilities/facebook/facebook_credentials.yaml"
commands_dict = read_commands_from_yaml_file(yaml_path)

# function to get facebook user's first name
def get_username(recipient_id):
    ACCESS_TOKEN = commands_dict["ACCESS_TOKEN"]
    url = commands_dict["facebook_username_graph_url"] % (recipient_id, ACCESS_TOKEN)
    response = requests.get(url)
    username = str(response.json()["first_name"])
    return username


# uses PyMessenger to send response to user
def send_message(bot, recipient_id, response, generic_message=None):
    # sends user the text message provided via input response parameter
    if generic_message:
        bot.send_generic_message(recipient_id, response)
    else:
        bot.send_text_message(recipient_id, response)
    return "success"


# function to verify facebook toke
def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    VERIFY_TOKEN = commands_dict["VERIFY_TOKEN"]
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Invalid verification token"
