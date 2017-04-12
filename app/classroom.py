from oauth2client.client import flow_from_clientsecrets
import oauth2client.client, json
import requests
class Auth(object):
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
        return self.flow.step1_get_authorize_url()
    def get_token(self,code):
        """Turns a redirect URI code into an api key."""
        credentials = self.flow.step2_exchange(code)
        return credentials
        
def get_user(token):
    x = requests.get("https://classroom.googleapis.com/v1/userProfiles/me?access_token=" + token)
    if x.status_code != 200:
        raise Exception("BAD STATUS CODE IN [get_user].")
    else:
        return json.loads(x.text)
def get_subjects(token,noarchive=True):
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
                grades.append(j["studentSubmissions"][0]["assignedGrade"] / project["maxPoints"])
        # find the average of grades
        if len(grades) < 1:
            avg = -1
        else:
            avg = 0
            for i in grades:
                avg+=i
            avg /= len(grades)
        return avg * 100