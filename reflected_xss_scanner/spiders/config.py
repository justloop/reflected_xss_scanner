import ConfigParser

class config:
    def __init__(self):
        print("init config")

    def getConfig(self) :
        parser = ConfigParser.ConfigParser()
        config_file = parser.read("config.cfg")
        print(parser.sections())
        return parser


