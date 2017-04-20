"""
Handles all requests in respect to the "app" (Main functionality of this webserver).
"""
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse
import json
import urllib.parse
from . import databaseManager, classroom
import oauth2client.client

def getKeyword(s):
    nn = s.replace(" ","")
    # set code to True if the string follows the format of course codes
    if len(nn) >= 6:
        nn = nn[:6]
        if str(nn[3]) in ["1","2","3","4"]:
            return nn
    return s.lower().split(" ")

# Errors
class InvalidUserId(Exception):
    """Error class if user makes request in the name of a user not in the database."""
    def __init__(self):
        message = "User id that was supplied is not in database."
        super(InvalidUserId, self).__init__(message)

# Create your views here.
class Handler(object):
    """
    :type googleapi_s: string
    :param googleapi_s: The filename of the `google service secret json file. <https://developers.google.com/api-client-library/python/guide/aaa_client_secrets>`_.
    :type firebase_s: string
    :param firebase_s: The filename of a our `custom firebase json files <#app.databaseManager.Database>`_
    :type scopes: list
    :param scopes: A list of `google api scopes`_
    
    Handler object for the app, so we don't have to authenticate everytime we make a request. Only on object creation.
    """
    def __init__(self,googleapi_s,firebase_s,scopes):
        try:
            self.auth = classroom.Auth(googleapi_s,scopes)
            self.AUTH_URL = self.auth.get_auth_url()
            self.db = databaseManager.Database(firebase_s)
        except FileNotFoundError:
            # we have to accept this error so readthedocs will run properly
            print("FILE NOT FOUND!")
    def addUser(self,token):
        """
        :type token: string
        :param token: The ``access_token`` of the user you want to add.
        
        Attempt to add a user (according to the ``token``) to our firebase user database.
        """
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
        """
        Returns a rendered template ``app/signup.html`` with added context of
        
        .. code-block:: python
        
            {
                "auth_url" : self.AUTH_URL
            }
        
        See the source code for ``__init__`` for info on ``self.AUTH_URL``.
        
        """
        return render(request,"app/signup.html",context={"auth_url":self.AUTH_URL})
    def loginPage(self,request):
        """
        redirects the user to the ``self.AUTH_URL`` (see source code).
        """
        return redirect(self.AUTH_URL)
    def authenticate(self,request):
        """
        Forwards request data to `classroom.get_token() <#app.classroom.Auth.get_token>`_
        Requires 1 ``QUERY_STRING`` variable : ``code``
        """
        query = {}
        for i in request.META["QUERY_STRING"].split("&"):
            query[i.split("=")[0]] = i.split("=")[1]
        try:
            token = self.auth.get_token(query["code"])
        except oauth2client.client.FlowExchangeError:
            return JsonResponse({"message" : "code parameter expired.","status_code" : 400},status=400)
        info = self.addUser(token.access_token)
        print("halo")
        if type(info) == bool:
            return JsonResponse({"token" : token.access_token})
        else:
            #return JsonResponse(info[1]["subjects"])
            return render(request,"app/app.html",context={
                "NAME" : info[1]["fullName"],
                "subjects" : info[1]["subjects"],
                "code" : info[0]
            })
    def getMatches(self,id,subject,section):
        """
        :type id: string
        :param id: The id of the user that wants to get matches. This was the method will not return the user themself.
        :type subject: string
        :param subject: The string representing the subject that want to get matches for.
        :type section: string
        :param section: The string representing the section (period) of the user's class.
        """
        # exclude the user that is making the query for our matches
        users = self.db.child("users").get(self.db.token).val()
        try:
            del users[id]
        except KeyError:
            raise InvalidUserId()
        matched = []
        # with this algorithm, double users shouldn't be an issue
        for user in users:
            for sub in users[user]["subjects"]:
                keyword = getKeyword(users[user]["subjects"][sub]["name"])
                if type(keyword) == str:
                    if subject.replace(" ","").find(keyword) >= 0:
                        this_user = users[user]
                        this_user["id"] = user
                        matched.append(this_user)
                elif type(keyword) == list:
                    # exclude integers
                    keyword = [x for x in keyword if not (x.isdigit() 
                                         or x[0] == '-' and x[1:].isdigit())]
                    subject_l = [x for x in subject.lower().split(" ") if not (x.isdigit() 
                                         or x[0] == '-' and x[1:].isdigit())]
                                         
                    finds = 0
                    g = "DERP"
                    if len(keyword) > len(subject_l):
                        for i in subject_l:
                            if i in keyword:
                                finds+=1
                        g = len(subject_l)
                    else:
                        for i in keyword:
                            if i in subject_l:
                                finds+=1
                        g = len(subject_l)
                    # Go by the smallest one, since we only want the on to fit into the other.
                    if g == 1 and finds >= g:
                        this_user = users[user]
                        this_user["id"] = user
                        matched.append(this_user)
                    elif finds >= int(g/2) and int(g/2) > 0:
                        print(finds,g)
                        this_user = users[user]
                        this_user["id"] = user
                        matched.append(this_user)
                else:
                    # what is this??
                    raise Exception("Unknown datatype recived from [getKeyword()]")
        # scrape marks
        for k in range(len(matched)):
            for j in matched[k]["subjects"]:
                del matched[k]["subjects"][j]["average"]
        return matched
    def matchesHandler(self,request):
        """
        Forwards all the data from the ``QUERY_STRING`` into the `getMatches <#app.views.Handler.getMatches>`_ method.
        """
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
        for s in urllib.parse.unquote(request.META["QUERY_STRING"]).split("&"):
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