from xml.etree import ElementTree

import yaml
from dotmap import DotMap

from ..core_utilities import read_commands_from_yaml_file

# reading credentials from yaml file
yaml_path = "utilities/goodreads/goodreads_credentials.yaml"
commands_dict = read_commands_from_yaml_file(yaml_path)

# function to get list of books up to 5 numbers for the given book name
def get_books_list(book_name):
    elements = []
    GOODREADS_API_KEY = commands_dict["GOODREADS_API_KEY"]
    url = commands_dict["good_reads_serach_url"] % (GOODREADS_API_KEY, book_name)
    tree = ElementTree.fromstring(response.content)
    title = [title.text for title in tree.iter("title")][0:5]
    image = [image.text for image in tree.iter("small_image_url")][0:5]
    title_image_dict = dict(zip(title, image))
    for title, image_url in title_image_dict.items():
        id_as_payload_value = image_url.rsplit("/")[-1].split(".")[0]
        element = DotMap()
        element.title = title
        element.image_url = image_url
        element.buttons = []
        buttons_map = DotMap()
        buttons_map.type = "postback"
        buttons_map.title = title
        buttons_map.payload = id_as_payload_value + "-" + title
        element.buttons.append(buttons_map)
        elements.append(element)
    return elements


# function to get id for a book and generate url to feed to IBM watson
def get_reviews_url_by_id(book_id):
    good_reads_review_url = "https://www.goodreads.com/book/show/%s#other_reviews" % (
        book_id
    )
    return good_reads_review_url
