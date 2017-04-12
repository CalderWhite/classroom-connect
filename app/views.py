from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse
import json
from . import databaseManager, classroom
import oauth2client.client

def getKeyword(s):
    nn = s.replace(" ","")
    # set code to True if the string follows the format of course codes
    if len(nn) >= 6:
        nn = nn[:7]
        if str(nn[3]) in ["1","2","3","4"]:
            return nn
    return "geography"

# Errors
class InvalidUserId(Exception):
    """Error class if user makes request in the name of a user not in the database."""
    def __init__(self):
        message = "User id that was supplied is not in database."
        super(InvalidUserId, self).__init__(message)

# Create your views here.
class Handler(object):
    def __init__(self,googleapi_s,firebase_s,scopes):
        self.auth = classroom.Auth(googleapi_s,scopes)
        self.AUTH_URL = self.auth.get_auth_url()
        self.db = databaseManager.Database(firebase_s)
    def addUser(self,token):
        # get user's name and id
        user = classroom.get_user(token)
        # get user's averages
        subjects = classroom.get_subjects(token)
        for i,course in enumerate(subjects):
            subjects[i]["average"] = classroom.compileGrades(token,course["id"])
        # datbase dicts
        data = {
            "fullName" : user["name"]["fullName"],
            "subjects" : {}
        }
        for i in subjects:
            try:
                i["section"]
            except KeyError:
                # the algorithm will ignore the section, if empty
                i["section"] = ""
            data["subjects"][i["id"]] = {
                "name" : i["name"],
                "section" : i["section"],
                "average" : i["average"]
            }
        # check if this user has already signed up
        if self.db.child("users/" + user["id"]).get(self.db.token).val() == None : 
            # SET
            self.db.child("users").child(user["id"]).set(data,self.db.token)
            pass
        else:
            # UPDATE
            self.db.child("users").child(user["id"]).update(data,self.db.token)
        # return, so we can use this is the response, after logging in or signing up
        return [user["id"],data]
    def signupPage(self,request):
        return render(request,"app/signup.html",context={"auth_url":self.AUTH_URL})
    def loginPage(self,request):
        return redirect(self.AUTH_URL)
    def authenticate(self,request):
        query = {}
        for i in request.META["QUERY_STRING"].split("&"):
            query[i.split("=")[0]] = i.split("=")[1]
        try:
            token = self.auth.get_token(query["code"])
        except oauth2client.client.FlowExchangeError:
            return JsonResponse({"message" : "code parameter expired.","status_code" : 400},status=400)
        info = self.addUser(token.access_token)
        #return JsonResponse(info[1]["subjects"])
        return render(request,"app/app.html",context={
            "NAME" : info[1]["fullName"],
            "subjects" : info[1]["subjects"],
            "code" : info[0]
        })
    def getMatches(self,id,subject,section):
        # exclude the user that is making the query for our matches
        users = self.db.child("users").get(self.db.token).val()
        try:
            del users[id]
        except KeyError:
            raise InvalidUserId()
        matched = []
        for user in users:
            for sub in users[user]["subjects"]:
                keyword = getKeyword(users[user]["subjects"][sub]["name"])
                if subject.find(keyword) >= 0:
                    x = users[user]
                    x["id"] = user
                    matched.append(x)
        # scrape marks
        for k in range(len(matched)):
            for j in matched[k]["subjects"].keys():
                del matched[k]["subjects"][j]["average"]
        return matched
    def matchesHandler(self,request):
        """
        j = {"code" : 500,"message" : "Unknown internal server error."}
        # parse query string
        query = {}
        for s in request.META["QUERY_STRING"].split("&"):
            z = s.split("=")
            query[z[0]]=z[1]
        try:
            j = self.getMatches(query["id"],query["subject"],query["section"])
        except InvalidUserId:
            j = {
                "code" : 400,
                "message" : "User id that was supplied is not in database."
            }
        except KeyError:
            j = {
                "code" : 400,
                "message" : "Insufficient query string."
            }
        finally:
            return JsonResponse(j)
        """
        j = {"code" : 500,"message" : "Unknown internal server error."}
        # parse query string
        query = {}
        for s in request.META["QUERY_STRING"].split("&"):
            z = s.split("=")
            query[z[0]]=z[1]
        j = {"matches" : self.getMatches(query["id"],query["subject"],query["section"])}
        return HttpResponse(json.dumps(j,indent=4),content_type="application/json")

scopes = [
  "https://www.googleapis.com/auth/classroom.courses",
  "https://www.googleapis.com/auth/classroom.coursework.me.readonly",
  "https://www.googleapis.com/auth/classroom.rosters.readonly"
]
handler = Handler("client_secret.json","firebase_secret.json",scopes)