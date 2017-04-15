"""
Module wrapper for all use of firebase's api.
"""
import pyrebase, json
class Database(object):
    """
    :type filename: string
    :param filename: Link to json file with `this format <https://github.com/thisbejim/Pyrebase#add-pyrebase-to-your-application>`_ inside a "config" object, along with a "secret" property for your firebase secret key.

    Simple wrapper for ``pyrebase`` database.
    """
    def __init__(self,filename):
        j = json.loads(open(filename,'r').read())
        firebase = pyrebase.initialize_app(j["config"])
        self.db = firebase.database()
        self.token = j["secret"]
    def child(self,name):
        return self.db.child(name)