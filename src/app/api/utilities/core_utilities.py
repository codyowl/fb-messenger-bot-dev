import yaml


# function to read yaml file
def read_commands_from_yaml_file(yaml_file):
    with open(yaml_file) as file:
        commands_dict = yaml.load(file, Loader=yaml.FullLoader)

    return commands_dict
