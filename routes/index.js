var express = require('express');
var router = express.Router();
const swig = require('swig')

/* GET home page. */
router.get('/', function(req, res, next) {
    var d = swig.compileFile('./views/index.html');
    res.send(d());
});

module.exports = router;
