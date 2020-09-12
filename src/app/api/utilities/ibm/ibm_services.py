import yaml
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import (
    EmotionOptions,
    EntitiesOptions,
    Features,
    KeywordsOptions,
    SemanticRolesOptions,
    SentimentOptions,
)

from ..core_utilities import read_commands_from_yaml_file

# reading credentials from yaml file
yaml_path = "utilities/ibm/ibm_credentials.yaml"
commands_dict = read_commands_from_yaml_file(yaml_path)

# IBM watson analysis logic
def ibm_watson_suggestion(url):
    service = NaturalLanguageUnderstandingV1(
        version="2018-03-16",
        url=commands_dict["IBM_URL"],
        iam_apikey=commands_dict["API_KEY"],
    )

    # to analyze the review
    response = service.analyze(
        url=url, features=Features(sentiment=SentimentOptions())
    ).get_result()
    label_value = response["sentiment"]["document"]["label"]
    if label_value == "positive":
        suggestion = True
        print("you can buy this !")
    else:
        suggestion = False
        print("don't buy this")
    return suggestion
