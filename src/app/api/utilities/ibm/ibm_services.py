from . general_utilities import read_commands_from_yaml_file

# reading credentials from yaml file
commands_dict = read_commands_from_yaml_file("ibm_credentials.yml")

# IBM watson analysis logic
def ibm_watson_suggestion(url):
    service = NaturalLanguageUnderstandingV1(
    version = '2018-03-16',
    url = commands_dict['IBM_URL'],
    iam_apikey = commands_dict['API_KEY'])

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