const express = require('express');
const app = express();
const http = require('http').Server(app);
const port = process.env.PORT || 8080;

var index = require("./routes/index")
var appHandler = require("./routes/appHandler");

app.use('/app', appHandler);
app.use('/', index)

// static after
app.use("/assets",express.static('assets'))
// finally listen

http.listen(port, () => console.log('listening on port ' + port));