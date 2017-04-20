function insertClassmates(data){
    var xz = document.getElementById("access_window").children[0]
    xz.removeChild(xz.firstChild)
    // actual appending
    var a = document.createElement("ol");
    //a.start = "50"
    a.className = "rectangle-list"
    xz.appendChild(a)
    for(i in data.matches){
        var x = document.createElement("li");
        x.textContent = data.matches[i].fullName
        a.appendChild(x)
    }
}
function insertError(data){
    var xz = document.getElementById("access_window").children[0]
    xz.removeChild(xz.firstChild)
    var y = document.createElement("div")
    y.className = "close heavy pointy"
    var x = document.createElement("center")
    x.appendChild(y)
    xz.appendChild(x)
    var x2 = document.createElement("center")
    var p = document.createElement("p")
    p.textContent = "Couldn't get matches due to Error:[" + data.statusText + "], try logging in again."
    x2.appendChild(p)
    xz.appendChild(x2)
}
function openClass(element,user,sub,sec){
    // remember, this function is only meant to run with MAYBE 8 classes in the page.
    const url = "/app/getMatches?id=" + user + "&subject=" + sub + "&section=" + sec;
    var t =document.getElementById("subjects").getElementsByTagName('tbody')[0];
    var w = document.getElementById("access_window")
    if(w != null){
        $('#access_window td').fadeTo(100,0)
        setTimeout(function() {
            $('#access_window td').css("line-height","0px")
            //$('#access_window').css('line-height','0px')
        },101)
        $("#access_window td").animate({
            height : "0px"
        },500)
        setTimeout(function() {
            document.getElementById("subjects").getElementsByTagName('tbody')[0].removeChild(document.getElementById("access_window"))
        },500)
    }
    var tm = 0;
    if(w != null){
        tm = 501;
    }
    setTimeout(function() {
        var x = null;
        for(i=0;i<t.children.length;i++){
            if(t.children[i].children[0].textContent == element.children[0].textContent){
                x=i;
            }
        }
        var r = t.insertRow(x+1)
        r.id = "access_window"
        var td = document.createElement("td")
        td.colSpan="2"
        var wn = document.createElement("div")
        wn.className = "loader center"
        var mwn = document.createElement("div")
        mwn.className = "mini-loader"
        wn.appendChild(mwn)
        td.appendChild(wn)
        r.appendChild(td)
        $.ajax(url,{
            complete:function(s){
                if(s.status != 200 && s.status != 304){
                    console.log(s)
                    insertError(s)
                } else{
                    insertClassmates(s.responseJSON)
                }
            }
        })
        $(td).animate({
            height : (window.innerHeight * 0.5).toString() + "px"
        },1000)
        setTimeout(function() {
            $('html, body').animate({
                scrollTop: $("#access_window").offset().top
            }, 750);  
        },1001)
    },tm)
}