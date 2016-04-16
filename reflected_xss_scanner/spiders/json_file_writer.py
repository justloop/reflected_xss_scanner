import json

class json_file_writer(object):

    @staticmethod
    def write_json(filename,data):
        with open(filename, 'w') as outfile:
            json.dumps(data, outfile, indent=4)