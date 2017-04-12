import pyrebase


firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()