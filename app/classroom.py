"""
Module wrapper for all use of google classroom's api.
"""
from oauth2client.client import flow_from_clientsecrets
import oauth2client.client, json
import requests
class Auth(object):
    """
    :type filename: string
    :param filename: filename that leads to a json file following `this format <https://developers.google.com/api-client-library/python/guide/aaa_client_secrets>`_
    :type scopes: list
    :param scopes: A list of `google api scopes`_.

    .. _`google api scopes`: https://developers.google.com/classroom/guides/auth

    Self contained authentication object for the google classroom api. Mainly for giving authentication tokens and urls.
    Google classroom api docs can be found here_.

    .. _here: https://developers.google.com/classroom/reference/rest/
    """
    def __init__(self,filename,scopes):
        self.scopes = scopes
        r = open(filename,'r')
        j = json.loads(r.read())
        self.flow = flow_from_clientsecrets('client_secret.json',
           scope=scopes,
           redirect_uri=j["web"]["redirect_uris"][1]
        )
        r.close()
    def get_auth_url(self):
        """
        Get a redirect uri from this object's flow data. (For oauth2_)

        .. _oauth2: https://developers.google.com/identity/protocols/OAuth2
        """
        return self.flow.step1_get_authorize_url()
    def get_token(self,code):
        """
        :type code: string
        :param code: The code variable in the redirect_uri query string.

        Turns a `redirect URI <#app.classroom.Auth.get_auth_url>`_ code into an api key.
        """
        credentials = self.flow.step2_exchange(code)
        return credentials  
        
def get_user(token):
    """
    :type token: string
    :param token: The ``access_token`` of user you want to find.
    
    Gets name and id of a user, according to their access token.
    """
    x = requests.get("https://classroom.googleapis.com/v1/userProfiles/me?access_token=" + token)
    if x.status_code != 200:
        raise Exception("BAD STATUS CODE IN [get_user].")
    else:
        return json.loads(x.text)
def get_subjects(token,noarchive=True):
    """
    :type token: string
    :param token: The ``access_token`` of the user you to get subjects from.
    :type noarchive: bool
    :param noarchive: If ``True``, it will only return courses you are currently taking. If ``False``, it will return **all** courses the user's ever taken.
    
    Returns a user's courses. See parameters for query specification.0
    
    """
    res = requests.get("https://classroom.googleapis.com/v1/courses?access_token=" + token)
    if res.status_code != 200:
        raise Exception("BAD STATUS CODE IN [get_subjects].")
    else:
        j = json.loads(res.text)["courses"]
        subs = []
        # don't return courses the user isn't currently taking
        # (unless you want that [noarchive=False])
        for s in j:
            if s["courseState"] != "ARCHIVED" and noarchive:
                subs.append(s)
            elif not noarchive:
                subs.append(s)
        return subs
def compileGrades(token,courseId):
    """
    :type token: string
    :param token: The ``access_token`` of the user you want to get grades from.
    :type courseId: string
    :param courseId: The ``id`` of the the user's course you want to get grades from.
    
    Return a user's average in a course.
    """
    req = requests.get("https://classroom.googleapis.com/v1/courses/" + courseId + "/courseWork?access_token=" + token)
    if req.status_code != 200:
        raise Exception("BAD STATUS CODE IN [compileGrades].")
    else:
        j = json.loads(req.text)
        projects = []
        try:
            j["courseWork"]
        except KeyError:
            return -1
        for project in j["courseWork"]:
            try:
                project["maxPoints"]
            except:
                print("https://classroom.googleapis.com/v1/courses/" + courseId + "/courseWork?access_token=" + token)
                return -1
            # TODO: create project validator that includes a max of 100 points.
            # (The reason this quazi works is the default value is 100, so if the teacher/admin changed it, it must be a viable project)
            if project["maxPoints"] != 100:
                projects.append(project)
        grades = []
        for project in projects:
            res = requests.get("https://classroom.googleapis.com/v1/courses/%s/courseWork/%s/studentSubmissions?access_token=%s" % (courseId,project["id"],token))
            if res.status_code != 200:
                raise Exception("BAD STATUS CODE WHILE GETTING STUDENT PROJECT SUBMISSION in [compileGrades].")
            else:
                j = json.loads(res.text)
                try:
                    grades.append(j["studentSubmissions"][0]["assignedGrade"] / project["maxPoints"])
                except KeyError:
                    # For whatever reason, one of these isn't there...
                    # For now, do nothing.
                    pass
        # find the average of grades
        if len(grades) < 1:
            return -1
        else:
            avg = 0
            for i in grades:
                avg+=i
            avg /= len(grades)
        return avg * 100