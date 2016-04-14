import json

class result_db(object):
    result = []

    @staticmethod
    def add_to_result(type,url,params):
        data = {"url":url,"method":type,"param":params}
        if data not in result_db.result:
            result_db.result.append(data)

    @staticmethod
    def get_result():
        return result_db.result