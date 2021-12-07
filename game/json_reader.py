import json


class JsonReader:
    @staticmethod
    def read(path):
        f = open(path)
        data = json.load(f)
        f.close()

        return data
