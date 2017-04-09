const express = require('express');
const router = express.Router();
const fs = require('fs');
const google = require('googleapis');
const OAuth2 = google.auth.OAuth2;
const swig = require('swig')
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
  "https://www.googleapis.com/auth/classroom.coursework.me.readonly"
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
    res.send(AUTH_URL);
});
//HERE

module.exports = router;
