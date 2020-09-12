from . general_utilities import read_commands_from_yaml_file

# reading credentials from yaml file
commands_dict = read_commands_from_yaml_file("goodreads_credentials.yml")

# function to get list of books up to 5 numbers for the given book name
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

# function to get id for a book and generate url to feed to IBM watson
def get_reviews_url_by_id(book_id):
    good_reads_review_url = "https://www.goodreads.com/book/show/%s#other_reviews" % (book_id)
    return good_reads_review_url   