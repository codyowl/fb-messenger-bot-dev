from . general_utilities import read_commands_from_yaml_file

# reading credentials from yaml file
commands_dict = read_commands_from_yaml_file("facebook_credentials.yml")

# function to get facebook user's first name 
def get_username(recipient_id):
    url = "https://graph.facebook.com/%s?fields=first_name&access_token=%s" % (recipient_id, ACCESS_TOKEN)
    response = requests.get(url)
    username = str(response.json()['first_name'])
    return username  

#uses PyMessenger to send response to user
def send_message(recipient_id, response, generic_message=None):
    #sends user the text message provided via input response parameter
    if generic_message:
        bot.send_generic_message(recipient_id, response)
    else:
        bot.send_text_message(recipient_id, response)
    return "success"