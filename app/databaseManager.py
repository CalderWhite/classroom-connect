import pyrebase, json
class Database(object):
    def __init__(self,filename):
        j = json.loads(open(filename,'r').read())
        firebase = pyrebase.initialize_app(j["config"])
        self.db = firebase.database()
        self.token = j["secret"]
    def child(self,name):
        return self.db.child(name)