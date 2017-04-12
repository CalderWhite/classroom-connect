const express = require('express');
const router = express.Router();
const fs = require('fs');
const google = require('googleapis');
const OAuth2 = google.auth.OAuth2;
const swig = require('swig')
const https = require('https')

var utils = {
  z:0
}
// setup
var AUTH_URL;
fs.readFile('client_secret.json', function processClientSecrets(err, content) {
  if (err) {
    console.log('Error loading client secret file: ' + err);
    return;
  }
  setAuth(JSON.parse(content),()=>AUTH_URL=getAuthUrl());
});
var CLIENT_ID
var CLIENT_SECRET
var REDIRECT_URL
var scopes = [
  "https://www.googleapis.com/auth/classroom.courses",
  "https://www.googleapis.com/auth/classroom.coursework.me.readonly",
  "https://www.googleapis.com/auth/classroom.rosters.readonly"
]
var oauth2Client;
function avg(a,callback,iter){
  var s = 0
  for(i in a){
    s+= a[i]
  }
  callback((s/a.length) * 100,iter)
}
function setAuth(j,callback){
  CLIENT_ID = j.web.client_id
  CLIENT_SECRET = j.web.client_secret
  REDIRECT_URL = j.web.redirect_uris[1] // dev uri == 1; deploy uri == 2
  oauth2Client = new OAuth2(
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URL
  );
  callback()
}
function getAuthUrl(){
  var url = oauth2Client.generateAuthUrl({
    // 'online' (default) or 'offline' (gets refresh_token)
    access_type: 'offline',

    // If you only need one scope you can pass it as a string
    scope: scopes,

    // Optional property that passes state parameters to redirect URI
    // state: { foo: 'bar' }
  });
  return url
}
function getUser(code,callback){
  oauth2Client.getToken(code, function (err, tokens) {
    // Now tokens contains an access_token and an optional refresh_token. Save them.
    if (!err) {
      callback(tokens.access_token)
    } else{
      console.log(err)
    }
  });
}
function getSubjects(token,callback){
    https.get("https://classroom.googleapis.com/v1/courses?access_token=" + token,function(res){
        var rawData = '';
        res.on('data', (chunk) => rawData += chunk);
        res.on('end', () => {
            var j = JSON.parse(rawData);
            var r = []
            for(i in j.courses){
                if(j.courses[i].courseState != "ARCHIVED"){
                    r.push({
                        name : j.courses[i].name,
                        section : j.courses[i].section,
                        id : j.courses[i].id
                    })
                }
            }
            callback(r)
        })
    })
}
function compileGrades(token,id,courseId,iter,callback){
  https.get("https://classroom.googleapis.com/v1/courses/" + courseId + "/courseWork?access_token=" + token,function(res){
        var rawData = '';
        res.on('data', (chunk) => rawData += chunk);
        res.on('end', () => {
          var j = JSON.parse(rawData)
          var goodIds = []
          for(i in j.courseWork){
            var a = j.courseWork[i];
            if(Number(a.maxPoints) != 100){
              goodIds.push({id:a.id,maxPoints:a.maxPoints})
            }
          }
          if(goodIds.length == 0){
            callback(-1,iter)
          }
          var grades = []
          for(i in goodIds){
            https.get("https://classroom.googleapis.com/v1/courses/" + courseId + "/courseWork/" + goodIds[i].id + "/studentSubmissions?access_token=" + function(res){
              var rawData = '';
              res.on('data', (chunk) => rawData += chunk);
              res.on('end', () => {
                var j2 = JSON.parse(rawData);
                grades.push(j2.studentSubmissions[0].assignedGrade/goodIds[0].maxPoints)
                if(i == goodIds.length-1){
                  avg(grades,callback,iter)
                }
              })
            })
          }
        })
  })
}
function getMatches(id,subject,section,callback){
    fs.readFile('users.json',function(err,content){
        var j = JSON.parse(content)
        console.log(j)
        // define the type of the subject string
        var lookforcode = true;
        if(subject.split(" ")[0].length != 6){
          lookforcode = false;
          for(i=0;i<10;i++){
            if(subject.replace(/ /g,"")[3] == i.toString()){
              lookforcode = true;
            }
          }
        }
        if(lookforcode){
          var thecode = subject.replace(/ /g,"").substr(0,6)
        }
        // alogrithm
        var goodUsers = [];
        for(i in j.users){
            var user = j.users[i]
            if(user.id != id){
              if(lookforcode){
                for(i in user.subjects){
                  var sub = user.subjects[i]
                  var newName = sub.name.replace(/ /g,"").substr(0,6)
                  if(newName == thecode){
                    goodUsers.push({id:user.id,fullName:user.fullName})
                  }
                }
              } else{
                for( i in user.subjects){
                  var sub = user.subjects[i].name
                  if(sub.toLowerCase().search("geography") >=0){
                    goodUsers.push({id:user.id,fullName:user.fullName})
                  }
                }
              }
            }
        }
        callback(goodUsers);
    })
}


// routes
/* GET home page. */
router.get('/', function(req, res, next) {
    res.send("NOT HERE BOI");
});
router.get('/signup',function(req,res,next){
    var d = swig.compileFile('./views/signup.html')
    res.send(d({auth_url:AUTH_URL}))
})
router.get('/login',function(req,res,next){
    var d = swig.compileFile('./views/login.html')
    res.send(d({auth_url:AUTH_URL}))
})
router.get('/auth',(req,res) =>{
    getUser(req.query.code,function(token){
        https.get("https://classroom.googleapis.com/v1/userProfiles/me?access_token=" + token,function(rd){
            var rawData = '';
            rd.on('data', (chunk) => rawData += chunk);
            rd.on('end', () => {
            try {
              var parsedData = JSON.parse(rawData);
              var prev = false;
              fs.readFile("users.json",function(err,data){
                  var j = JSON.parse(data);
                  var prev = false
                  for(i in j.users){
                      if(j.users[i].id == parsedData.id){
                          prev = true
                      }
                  }
                  if(!prev){
                      j.users.push({
                          id:parsedData.id,
                          token:token,
                          fullName:parsedData.name.fullName
                      })
                  } else{
                      j.users[i].token = token;
                  }
                  var f = swig.compileFile("./views/app.html")
                  getSubjects(token,function(callData){
                      for(i in j.users){
                          if(j.users[i].id == parsedData.id){
                              j.users[i].subjects = callData
                          }
                      }
                    for(i in j.users){
                      if(j.users[i].id == parsedData.id){
                        for(z=0;z<j.users[i].subjects.length;z++){
                          compileGrades(token,parsedData.id,j.users[i].subjects[z].id,[i,z],function(myAvg,iter){
                            fs.writeFile("./users.json", JSON.stringify(j,null,4), function(err) {
                                if(err) {
                                    return console.log(err);
                                }
                            }); 
                            console.log(j.users[iter[0]].subjects.length,iter[1],iter[0],myAvg)
                            j.users[iter[0]].subjects[iter[1]].average = myAvg
                            if(iter[1] == j.users[iter[0]].subjects.length - 1){
                              res.send(f({
                                  NAME:parsedData.name.fullName,
                                  subjects : callData,
                                  code : j.users[iter[0]].id
                              }))
                            }
                          })
                        }
                      }
                    }
                  })
              })
            } catch (e) {
              res.send(e.message);
            }
            });
        })
    })
});
router.get('/getMatches',function(req, res, next) {
    getMatches(decodeURI(req.query.id),decodeURI(req.query.subject),decodeURI(req.query.section),function(data){
      res.json({"data" : data})
    })
})

module.exports = router;
