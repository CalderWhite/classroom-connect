const express = require('express');
const router = express.Router();
const fs = require('fs');
const google = require('googleapis');
const OAuth2 = google.auth.OAuth2;
const swig = require('swig')
const http = require('http')
// database
const pg = require('pg');
pg.defaults.ssl = true;
// misc. functions (methods)
var myClient;
// the command to sign in :
// psql --host=ec2-23-23-223-2.compute-1.amazonaws.com --dbname=d2a8fvjr75j0va --username=ywtxabemqjdviz
if (!process.env.DATABASE_URL) {
  myClient = new pg.Client({
    user: "ywtxabemqjdviz",
    password: "afb550105b6176f9942d3def0ee7cf0ea24a6a60228971ef5c8a21fed357f260",
    database: "d2a8fvjr75j0va",
    port: 5432,
    host: "ec2-23-23-223-2.compute-1.amazonaws.com",
    ssl: true
  });
} else {
  myClient = pg;
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
// routes
/* GET home page. */
router.get('/', function(req, res, next) {
    res.send("NOT HERE BOI");
});
router.get('/signup',function(req,res,next){
    var d = swig.compileFile('./views/signup.html')
    res.send(d({auth_url:AUTH_URL}))
})
router.get('/auth',(req,res) =>{
    getUser(req.query.code,function(token){
        console.log("https://classroom.googleapis.com/v1/userProfiles/me?access_token=" + token)
        http.get("https://classroom.googleapis.com/v1/userProfiles/me?access_token=" + token,function(res){
            var rawData = '';
            res.on('data', (chunk) => rawData += chunk);
            res.on('end', () => {
            try {
              var parsedData = JSON.parse(rawData);
              res.send(parsedData);
            } catch (e) {
              res.send(e.message);
            }
            });
        })
    })
});
//HERE

module.exports = router;
