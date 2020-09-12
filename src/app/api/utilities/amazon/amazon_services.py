import yaml

from ..core_utilities import read_commands_from_yaml_file

# reading credentials from yaml file
yaml_path = "utilities/amazon/amazon_credentials.yaml"
commands_dict = read_commands_from_yaml_file(yaml_path)

# function to get amazon search page for a given book
def get_amazon_search_page(book_name):
    amazon_search_url = commands_dict["amazon_search_url"] % (book_name)
    # url = "https://www.amazon.in/s?k={0}&ref=nb_sb_noss_2".format(book_name)
    return amazon_search_url


# function to send amazon url for a given book
def send_amazon_url_as_message(recipient_id, book_name, amazon_url):
    elements = []
    element = {
        "title": book_name,
        "image_url": "https://img.icons8.com/material-rounded/24/000000/amazon.png",
        "buttons": [{"type": "web_url", "url": amazon_url, "title": "View"}],
    }
    elements.append(element)
    bot.send_generic_message(recipient_id, elements)
    return "success"
