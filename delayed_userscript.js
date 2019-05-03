// ==UserScript==
// @name         delayed issues
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match *://instantview.telegram.org/*
// @match        *://instantview.telegram.org/contest/*/template*?url=*
// @match        *://instantview.telegram.org/contest/*/template*
// @grant window
// @grant    GM_xmlhttpRequest
// @grant    GM_addStyle

// ==/UserScript==


(function() {
    'use strict';
    const url = "http://127.0.0.1:5000";

    GM_addStyle (`
.rainbow{font-family:Pacifico,cursive;text-shadow:1px 1px 1px #000;font-size:25px;animation:rainbow 7s infinite}@-webkit-keyframes rainbow{0%{color:orange}10%{color:purple}20%{color:red}30%{color:#5f9ea0}40%{color:#ff0}50%{color:coral}60%{color:green}70%{color:#0ff}80%{color:#ff1493}90%{color:#1e90ff}100%{color:orange}}@-ms-keyframes rainbow{0%{color:orange}10%{color:purple}20%{color:red}30%{color:#5f9ea0}40%{color:#ff0}50%{color:coral}60%{color:green}70%{color:#0ff}80%{color:#ff1493}90%{color:#1e90ff}100%{color:orange}}@keyframes rainbow{0%{color:orange}10%{color:purple}20%{color:red}30%{color:#5f9ea0}40%{color:#ff0}50%{color:coral}60%{color:green}70%{color:#0ff}80%{color:#ff1493}90%{color:#1e90ff}100%{color:orange}}
.iv-logo .iv-icon{     background-image: url(https://yt3.ggpht.com/a-/AAuE7mB0JS7Kt0BpqFZ_TSAIn4VF8mlThOWjIDUF=s900-mo-c-c0xffffffff-rj-k-no) !important;
    background-size: 20px 20px;
    background-repeat: no-repeat;    background-position: 0px 0px !important; }
.wrapper{height:100%;width:100%;left:0;right:0;top:0;bottom:0;position:absolute;background:linear-gradient(124deg,#ff2400,#e81d1d,#e8b71d,#e3e81d,#1de840,#1ddde8,#2b1de8,#dd00f3,#dd00f3);background-size:1800% 1800%;-webkit-animation:rainbow2 18s ease infinite;-z-animation:rainbow2 18s ease infinite;-o-animation:rainbow2 18s ease infinite;animation:rainbow2 18s ease infinite}@-webkit-keyframes rainbow2{0%{background-position:0 82%}50%{background-position:100% 19%}100%{background-position:0 82%}}@-moz-keyframes rainbow2{0%{background-position:0 82%}50%{background-position:100% 19%}100%{background-position:0 82%}}@-o-keyframes rainbow2{0%{background-position:0 82%}50%{background-position:100% 19%}100%{background-position:0 82%}}@keyframes rainbow2{0%{background-position:0 82%}50%{background-position:100% 19%}100%{background-position:0 82%}}
`);



    function error(e) {
        showAlert("Failed to contact delay server. Is it really enabled?");
    };
    var editor = $("#rules-field");
    if(editor.length > 0) {
        GM_xmlhttpRequest({
            method: "GET",
            url: url + "/snippets",
            onload: function(e) {
                try {
                    var json = JSON.parse(e.response);
                    if(json["status"] != "ok") {
                        showAlert("Error! " + JSON.stringify(json));
                        return;
                    }
                    var snippets = json["snippets"];
                    console.log(snippets);


                    var value = App.editor.getValue();
                    App.editor.setValue(value.replace(/(?=^## <snippet "(.*?)">\n).*?## <snippet end>\n/gms, "@snippet: \"$1\"\n"));

                    var _oldProcessRules = processRules;
                    unsafeWindow.onbeforeunload = function(){};
                    unsafeWindow.processRules = function processRules(rules) {
                        if(rules.includes("## <snippet")) {
                            var c = App.editor.getCursor();
                            rules = rules.replace(/(?=^## <snippet "(.*?)">\n).*?## <snippet end>\n/gms, "@snippet: \"$1\"\n");
                            App.editor.setValue(rules);
                            App.editor.setCursor(c);
                        }
                        rules = rules.replace(/^@snippet\s*?:\s*?(".*?")$/gms, "## <snippet $1>\n{code}\n## <snippet end>");
                        console.log("old = " + rules);
                        if(rules.length > 5) {
                            var lines = rules.split('\n');
                            var newRules = "";
                            var nextSnippet = "";
                            for(var i = 0; i < lines.length; i++){
                                if(lines[i].startsWith("## <snippet")) {
                                    if(nextSnippet != "") {
                                        nextSnippet = "";
                                    } else {
                                        nextSnippet = snippets[/^## <snippet "(.*?)">$/.exec(lines[i])[1]];
                                        if(nextSnippet == undefined) {
                                            nextSnippet = "@ERROR_NO_SUCH_SNIPPET";
                                        }
                                        console.log("nextsnippet = " + nextSnippet);
                                    }
                                } else if(nextSnippet != "") {
                                    if(lines[i] == "{code}") {
                                        newRules += nextSnippet + "\n";
                                        continue;
                                    }
                                }
                                newRules += lines[i] + (i == lines.length - 1 ? "" : "\n");
                            }
                            console.log(newRules);
                            return _oldProcessRules(newRules);
                        }
                    }
                    processRules(App.editor.getValue());
                } catch(e) {
                    showAlert("Error while parsing json: " + e);
                }
            },
            onerror: error,
            ontimeout: error,
            onabort: error
        });
    }

    var logo = $(".dev_side_image img");
    if(logo.length > 0){
        logo.attr("src", "https://i.imgur.com/5TGMjSl.png");
    }
        var header = $(".header-wrap");
    var urlform = $("#url-form");
    if(header.length > 0 && urlform.length > 0 && urlform.attr("action").includes("/contest/")) {
        header.append(`<button href="#" target="_blank" id="diff" class="btn btn-link btn-lg">Diff</button>`);
        header.find("button#diff").click(function() {
            var request = {
                section: App.state.section,
                url: App.state.result_url,
                rules_id: App.state.rules_id || 0
            };
            GM_xmlhttpRequest({
                method: "POST",
                url: url + "/diff",
                data: JSON.stringify(request),
                headers: {
                    "Content-Type": "application/json"
                },
                onload: function(e) {
                    try {
                        var json = JSON.parse(e.response);
                        if(json["status"] != "ok") {
                            showAlert("Error! " + JSON.stringify(json));
                            return;
                        }
                        showAlert("Success! has diff = " + json["has_diff"]);
                    } catch(e) {
                        showAlert("Error while parsing json: " + e);
                    }
                },
                onerror: error,
                ontimeout: error,
                onabort: error
            });
        });
    }
    if(header.length > 0 && $("#url-mark-btn").length > 0) {
        var url_contest = document.URL.replace("/my/", "/contest/");
        header.append(`<a href="${url_contest}" target="_blank" id="url-share" class="btn btn-link btn-lg">Contest</a>`);
        header.append(`<button href="#" target="_blank" id="download" class="btn btn-link btn-lg">Download</button>`);
        header.append(`<button href="#" target="_blank" id="undiff" class="btn btn-link btn-lg">Undiff</button>`);
        header.find("button#undiff").click(function() {
            var request = {
                section: App.state.section
            };
            GM_xmlhttpRequest({
                method: "POST",
                url: url + "/undiff",
                data: JSON.stringify(request),
                headers: {
                    "Content-Type": "application/json"
                },
                onload: function(e) {
                    try {
                        var json = JSON.parse(e.response);
                        if(json["status"] != "ok") {
                            showAlert("Error! " + JSON.stringify(json));
                            return;
                        }
                        showAlert("ok");
                        location.reload();
                    } catch(e) {
                        showAlert("Error while parsing json: " + e);
                    }
                },
                onerror: error,
                ontimeout: error,
                onabort: error
            });
        });
        header.find("button#download").click(function() {
            var request = {
                url: App.state.result_url
            };
            GM_xmlhttpRequest({
                method: "POST",
                url: url + "/download",
                data: JSON.stringify(request),
                headers: {
                    "Content-Type": "application/json"
                },
                onload: function(e) {
                    try {
                        var json = JSON.parse(e.response);
                        if(json["status"] != "ok") {
                            showAlert("Error! " + JSON.stringify(json));
                            return;
                        }
                        showAlert("ok");
                    } catch(e) {
                        showAlert("Error while parsing json: " + e + "\n" + e.response);
                    }
                },
                onerror: error,
                ontimeout: error,
                onabort: error
            });
        });
    }
    var username = $(".logged-name");
    if(username.length > 0) {
        var realName = username.text();
        username.text("durov");
        username.addClass("rainbow");
        var winner = $("div.contest-winner-row");
        if(winner.length > 0) {
            $("header").css("background-color", "transparent");
            if(winner.find(".contest-item-author a").text() == realName) {
                $("body").addClass("wrapper");
                $("a.status-winner").css("font-size", "1.5em").addClass("rainbow");
                // stupid me decided to put the song on the hosting that removes it after 14 days
                $("body").append(`<audio autoplay src="https://transfer.sh/EVUUW/Pesnya_papicha_VI_KA_pobednaya_(mp3ix.net).mp3"/>`);
                $(".list-group-contest-item").each(function() {
                    if($(this).find(".contest-item-author a").text() != realName) {
                        $(this).find(".contest-item-author a").text("SUCKER!");
                    } else {
                        $(this).find(".contest-item-author a").text("Величайший " + realName + "!");
                    }
                });
                $("body").append(`<script>var canvas=document.createElement("canvas");canvas.style.position="fixed",canvas.width=document.body.clientWidth,canvas.height=document.body.clientHeight,document.body.appendChild(canvas);var context=canvas.getContext("2d"),id=52,cwidth=100,cwidthhalf=cwidth/2,cheight=128,cheighthalf=cheight/2,particles=[],Particle=function(t,h,a,c,i){0===c&&(c=2);this.update=function(){if(a+=i,(h+=c)<-cwidthhalf||h>canvas.width+cwidthhalf){var t=particles.indexOf(this);return particles.splice(t,1),!1}return a>canvas.height-cheighthalf&&(a=canvas.height-cheighthalf,i=.85*-i),i+=.98,context.drawImage(image,0,0,cwidth,cheight,Math.floor(h-cwidthhalf),Math.floor(a-cheighthalf),cwidth,cheight),!0}},image=document.createElement("img");image.src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAACACAMAAADK6TzyAAABS2lUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDIgNzkuMTYwOTI0LCAyMDE3LzA3LzEzLTAxOjA2OjM5ICAgICAgICAiPgogPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIi8+CiA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgo8P3hwYWNrZXQgZW5kPSJyIj8+nhxg7wAAAARnQU1BAACxjwv8YQUAAAABc1JHQgCuzhzpAAADAFBMVEX///8BrOH/yAH4/f0BpuD9//4AquEkJSYBreT/wwH8xAsEptz///wAcbcDq+rv7u/29/YDpeUAdb8CfLro6Of/4wj/1QcCsuXa29kDAQOIvNkBfMV+tdL8+vsAbMGsrbAmEg0BnOPHxsoGp9Ti4N/u9/n/zgbV09MtNkRBO0P/3Ql0SSHRy8sDhbz+vQcCvv4Cm9bQ7vcCeK7+/vJmPyy3trg/p8gXBgVZY26/wcGdm5yXlJTm8vmKgYnx+/0AZ7h+fH0ErtprZ2VPnrnG6PH/7AqQjYxzvNpPT1Hp+PuTlaBeXmF1c3WgbzygpadbMR7R5/DC3ellPRgzGQkAccozIjoHnssFjcICg8wPCxQWGSTd9fhxss738+4DSmg0S0+x2edhb3WFj5UrlsNhtdqNXjN0Sju54vBSanw+ntPa7PUzMTIEWXNLKSI2OFUSh7wDjtJTMg8EuuZ/l6AYJDiisL5NVV5Lrdej3fBtYEsDtfGPscCAUymOx+JjlK/apg9BHB0onc6uvr5eTT9dqtCk0d94nKyEVkiYz+fMxbvS09///OKQp65JXG561fDd2sbY3+VrhpYAk960pojBta22v9KgoLJhpr/y8tpFR1t+wePwlAGcYT9Fv+vGz9h1qMPGlwtIJAgLwu0vuuUBZazn09Khv9BrZnAOmLsAnu84Ihizz9ibg1WqnqCaaiPp5M61ssc9h6O3gQk9Vl17h4peUV61raCN3vFfGQFpmp9oe4EmY3x/d49/MgZkco+AUgcSi6wAW780itFsQgOmloDHhDYrrtMWbo2WinXuxwljzeowlLKdUwTo17g5SmaaaVyzcSyFcWMBsfzsuBn897zmrg2yfkgasOOHXBwUh8pFEAP04uGGg6GtbgInhKNXiJ5Hd5AqW3HGjVYiCSDJcg7+7M7SyK8NfJtRQCjeyJEzhr5Fz+r++6bbokRjwOKYaQHQu59SS3j75KHWhQD/+wrFqWXNu4W3jHC56PyhgRYAz//53oPa1Z7ftnANL1D+zEq3qO8PAAAbHUlEQVRo3u2ad1xTV//4D4TLyCATCEQSEhIyCHsT9haQJXvIUlllyVJBkCEyBZQhVhAciCJDEVfde9e9q1brHnV39/mdm0DbV79gqb6e31/PR4Lhnns/7/OZ99wBlCYrI15KnypACUxOGn77jQg+TSYDMYuJIRF/OHfkyHdn/jsQUsOT90egnDtyJdv/yidSPg4hHr62b8+h7MdB5+7dG/BP9z/33c2/jGrXVfI+H9K8Y4f/Rh0rKP4rr6zUDwoyP/Id6U/G3TrWTuRzIdu6L73StJqOiv+sadOu6esHzT5y5Y/hO1uB9s6Az4RwrX4F+E2aELGxO2jWwLSVs/SD/GedezU6XJfMJWkP9XwmROcKaN5WG2TVPb072xxaMk2KOXdalsiBM5ppRDy/EvksCD8bcJfZDz3vXpidHVS0cuU0GWbluQFpSpwtflBDxN/M4X0W5PgTXr/HcRvw/ka2P2rIrKJZX3+9uKho5Z5mAM6cOz0tjkdCzHIaPweC/wCWnbc9XKttNnAjSH+W/uzZi7/++ocfvl68+Gt97ZjTRUE7vFjQcX4tnwM5U1t9/vzx2gc3zS4NdPtDwuLFs81nQ1vQr9Ou6ej4Zw/HcwCn7jMg+DcP55UfP/Ng3QOz2mkLzWeX+/ubm5vPXrzYPN1/sb//Y52NN8735cd6rKtDPsOSS8vmHW5+cObSpWXCEPN0HZ1089mzUcpsSJu9UGd69vTzNxvrhq13aX8GhPh+2UPIeFJupZOuY6WzcSHUbQ4jMzt948aFsHL0u53WidfRcmJjPgNCmv7L4Js3m3Q0N0630tHRmb4wHVqSvnDjwoXp6d3+/vpBG5vXQUpM4aLPgGhb6T9/Ym5lBVuXDgqB80+HLiuaBaXIX39W9vmtGbtvrosR964x+fQ6KdfRN7+vY6UpZVhZTU83L7ry4sW9K7BizIMWb8w9G7kxLaRZW+yqSu6I+lTI+enp/gutpJAIq43+RdOuXLl378iVTdP2dOtERjz+6acS7Il9IRwz1/lyOPYSzKdBDvuXb5wOTdCEjRi6ZyVsLJAybaX+eYmfxCv7G7V3WD21LY+9oy84z1fVVTX5FMiPx/T9Ny7U0dTU1PGHPR5SYOuCnau7XzrMeT29S80Q6355R8Z8I1VVZ9UN25F/DVly4dge/XSYWOlB+ub+QeZFRUWzFw+cu/iNF5oU6B559yHFUE1vz7Gf5eRUyc4bOjD/DoLvIK+esePxwmxzaERQkD/Mq6KBI5ex6u923IKj+OpqPB606qhjsViR4eMLF5xVVTU0Nlx1+DcQpINtZPR7urn+rKDu7uxs/2vnfuq6qK6mrmKolt0KzICZpqYYojK+V1NRkZfXX2oEERoaymSFqZOH4Nds+Hn+V/qwHm5kz4bN6v70kncidRWoECv6/jUwwwOJCw2pBbd2oBDD8g3znZWhaGgoTEAZD9JxYc7totMr9bOn+9ABHjiIW0O+cceqyMNZG6p374ULMbgTDEDGPghRUSlaOl9OWSoa5A0Ok4ScvNBbvmNPtk6EZrm0iUGVdiFdahChAkNw4sZr2cmw8XX3CXnIUPtu7c+qoxRnsgZmUpDtF27v2WGlGQET6yacM95Kk4YHnf4wyCqoNepq+4S3hixurU/f5y4yhBDRl18ZKcsgcnLzcUcnAzFhr96/48aObh3NgYEWYIbgPbyI0Gchp90Nsahz1LdcPHEo+9Ch77HvtlxGLVGXQkZFEdbLP0MwumRdo6xvhRvNyy+eEP5xbh3SvCGSN4SGqKiX+He9E+mpvXP3DxKNQVRlCGVVnK7Ghqh/hLxkq85XMPr52A6sOlbUFbS7JcAOMzXglv9PVuegKTD2hqITQdf03EVdC4PU9KSmffntGEROTkPZWUEV+QeICVtZjiznbPT7HjhLQ5F8108DmzZt0j90+d2hhe5Yqb+w6uoDQfsebxxw1zNUGbVkjAFtUXZmL/k4BCGT5RTlFJXn555Wk8di9eRLSrCXt2zBuuupl9y/7C6dud7FWV0n0G0i7B8QxVFRVoQNRpfN+yhk7gZnZ2j6fOeIb9Tk5S9fdO/aV3RtoEtPBSvvvjD9RImhPGpJif61EpH65S0len+3BE0xVWVcx8cgCBv2bDlluQu6EGKod7FoQF104gQWTV5DUUm6/k8wKConsOqiriL9ooGfLkpN+TsE2hIa9RHIXDbcD/prvmrkWzVDFfWLcCH//cCsErSlGKrrXVRHswltVyLR5RKsmp4hFiuPRSHkUXehHDk5MrtjYgiCgxFBd1VVzX2Ldgw9tYtdXSUX1bEy3Xqy/2TfUSDaAmTZNRoSaanA442nTghxY48Wler83LciaSbpqavroZU+nsjL6+mpqWH/TGEIQX8g5W8J9ldIB9tZNiMI+U7aMrCoyGOxf9OtLlJTU1OXNyzp+n4LVvSHJXLK8CP9xsZhJoDw2KqjEA0jmMIqMuVSDmxaetAokUhNpK6ncrnrm+/37TsUZG7uMgITG20rsvTVkHoLTlLB2G0CSBJbcRSibPT7aTWYOqhmEdSMqjYsebsF6j50KCjocfnI+t3erS2NPIDR6VIbtURZUVkKkUaF/XICSAdOd6yojGbsEcG2rne5pGuLdNZw2uVQ9frdCa1DNbQ/fdGoUzIGISujZ0epKTiYxsi4EAcFXUXVMQjau1SKHkPNUPHuW615QzV/LWMzPN7MzAyPAO/peqK3sopXUJ0zR0NZSsGRldkm40JMluqOMeSM9t+ANW31mufw92aHxyMIAj9wIYFK+yE10TeOq5VVFeRwV1fPIUNblBUVnHHkpXPHhcxdqkjGKUgFpzo/8js10RahVC2XzzUDqFqZ4lH1SAzfw8Uncp+7Hjz9KuMUN1x9tlpBYw6kQIgizrhjXMhJNllBZoiCIg4GRU3F/cZu9Eq7IYZWTQcIGIWg6y4aiUSSCH08+Le63b88ewGuuhTIJ59tmLMaegytSVVF3b82/D8ha8gKOBlGQZF8wfSGip6oxAqetRpiSEQi58+rELGHrwU8V2rTaPAPPx21byhGZLi0e7Z9TccajdUQAqOPU9UNnToOBKPwp+DIaDmqGbpvifCmDYIalt/hV3Qi8SbL47zLyIjPPDHHhkOSLiQzDr07Hbwah2Nf3b5kyRrymtXzpSswBbKicdQ4kCjjv1AUVI2+2AMb8LstmhGDcMEiHhwcpJmZNUskzQ00YLa8mkTS1oaLjNfdempvvzBS1GV3bN/esXTNkmeow+bABZjCUrdxIeS/QMjzjad/qYbFum/R5APbED9WAse21d67kWhrgXAlfGBRA10+pNStru7+3QwjVQXcybnPlqpCY9agFFSDcdI4kFRjBRwOzS740SXjdH+esccd9hS1IzVgJATfHyK0H7ovtBCOhPBZEfbaIa0g9bXO9+7qWPl9Bhdwus5LligYn9x+FXdyzWoNqZq/5vAfELelZDIZJSiQyTicLm6+6v236NJBbxD4RrTSQ+7TQQgLhDiNcOyFTtyMhpq0Qyfc0bPJ4rnGZLYcdFbH3DXsZ0ueOUMdcLpLt48HyZKaAUXGYhsRFhqqG6oY/gqcIjj0+xFicN82JiRthDtiv75a2HmmC5qhAnPjPCjYYHx1CbzaOqlwcvszOWOytNyWLhnfEjYUY1RQa0LZPx847S5vaPgB7NYUe9wP8cHftzcLcfKy9xKGNHvUPEfPi9DQQ7sd6Gz2mpNLr25nr9neYcweDe34kKzQ0tKjlgUzPbWqokM3kHUVjJ3Pfgkp70k1Li5Ovv1pN9PWg/u+XiMhIyFO9i21KuiZRrTvFrGs1vXCko6lL0+S5y7BGePkYFOZyF2kvsDGRhoR5iag51WwNxgX1ETFLdyiJnqRasZt4Yi5nYPVYrPqBrG42oxfbUFfDk8FWNHbkR8xNqS+b9+7GiWdfBZQqrt69WoNXY05c5yzxgs84gBl6lQ7O0xScVtLG7vgpgOwEYTsKymZWj3v+PHj9sc9WCwPlq2fbb+kv1/CWS5dwhTdymssGwLf3Ahd8mPB3O2hvc6r50BrVs/RzRovhRETVFJTHTqL24pXabU1RiXZJRxv+j1kMT7v8PPnl558qH4FF5PLljVvW/b+/SbfmP8Y6rm/bW+hlRW+f3Ht9uYjhT8nFZBDQ2GzxBk7y+GyAsaDuLmZmLgFOMStmqI1pbgtr8ct4EeJvVP+7/m1Qx6XLtU+Wf5k2sPlmzb99gBcev78Fyfaf0TqXeWVZVEWnKI9hZtX7ni0fZGuMy40FCenoRuKUwwdr62AwMCkwMCovuJVU6ZMWXVn1aqeH3/0nefkk1tuZnH80iWzD+8/jGw7c1gysKkWQn61573Ysvh+cU9OX0vj/RFw5Maxu9/tvHBVQ7cXkpxDdUNDMeNBAqrmLjJZtEpLS2vKFK3oO5WrtEys0+zXC8rNho4/v2R25vS0au69V+CHPb/WvvnlN3vEPsRHsCqnsqcsTngE+sv13I7bq8N0dUOdDQycdXWpR8c9n9gtWPRjX3H0lGgo0JbiVavm5mxc7ySYhx/6+pdfHgyevrYcf+WH5Q17fsC/+c8LJ+RhRqywcmdlT15febb+rrsrd3zVkflF71FdZ1NTiGKuGBfCW5G0qNjTcwoqnlpabcWFCyrn+fgKzoOhTb+8qT1zbdqZMw0Pfzuz6fQbCPEAr9rPpu1sqiysa4nX9MHc2/HtnI79X5w6Gnr10SOcsS4jaVwIZu4iaMeqVdAM+DNFa1Wx1ip7l3yfw6Dn3i9vzJ6c/lD74MmHJ2dq3z95/p8XtuChS77gzq7iYu/WO2lHXgwkq5a+fDSj92jvmv372aWhWVPHXxLFuXqu0JIJCplSXFzh3eyVtg20fH3vh+ZNK6ubm7dta24WVy/77cWRftDcHi+8m3xn787dldY39nz1zDLx5e1jlpahR3vlAnlVBZjxIY0pnm3RqCWoLdHRWm23TyVU+wkP4zE1nTWcmsbOTk4Nx0bMGRratq2/Ed8grM8fTh7eW9m+t8maXlzgmjjTstQysbQ3KwlelAfyxodgKmAotBZobf5qszTDXDe33drG2r0Nz60W85fza6rFdH4MTSyWLSdiaiUZycLiu217I4d3JoGEU4mnXC2PhuJ0jV8uD4xDOhsnWHAvckWDcWzGjBnHorWkkK3Nfr4f8Dbe3n50Gz+Ohbe9WLz7FodI5/OJMYP0pr2CnXMrlSJik3flrM88ann1amloae9RmpldT2FhzQQQnuXLKVWuM2Z8MeOLNimkIsfCb94r4G1vYd/qvZvVau9nY8tiebMk3hJazENaS167cLdQKVaQUR/Piitgh55KsTyVtYCEcQjcmUyc6ErL07LC8/aMLyDEdQFM4s0VrdUWx1/Rtm2r7pfYbpPY2ootPPgcW0k/nwMGIaSvKcPFNjakfWcAQLRrLF0tSw+yLRvKCmv6kpMnvJyzq1ix4pgMAoPiutnV5kFM7XLu8uWDy2XS0LB8sKGhYbBZrN3wkFbWube+mZuWW2gSYAem4vtKFUKXlg7iSXmVOYIyePIgjX/1O9N15qNRS6Tuqnvzf+9TwaU2vrofefVralngXq9qScTwzp64Ral2vNqCLONeb4u+qKS9w+1wTWahPT7ErsDz0ZglaOALN/3Ka6BD4a6Dv/j8dVCgJfyHHwY3DTZCiIvYS1OQXFnY0xeYCmz2hxWu68ypK7TOzYPLW9uJ7kissHz0xRikbXPblFubNh0/fvj44R8OHz68bEy2wX/XzoPOoUBryVBkhFJ7clNTU05hAHfz3cN9Ji3WyRkCuCrzok0EwaxBM1gK6Wnb7FlYNuRSXj7vfHns49nz/pDyefNc5g0BTkuPj41HRGRkyNn6+uTk+KZFCayypqa6/LMCWCQWPhPfwHF7dPuUZVs0rEkt1zttxZLW9ty0Xfb1+32st/rGx1tLJVaQP+IkBpzOSl+6vVBTUzNScBZS6it35fTl5Fu358KoE5VgRLSRCe53LTj60jO6zXXz5tv7E0MfuUDNucJ5d18muLjYOvnKxEfo5WKvDXY17ZWIPVzyfSWSulYWK691VVN+8q6MjNwEqF5JDEEWE91UQ/Yb7M8MC8taahwalllcltCU06QkrHiZ1+zix7L1kEg87H1dhGk+En7/1voRP1sLtOjwMXybFo5FJa8sV9CeuxVmr5IfBHmRJrw9aBdmbMw2zgqDrWizd1+8IHbX47tLXOsAi0VChUjkWsQKYvO9hgPi17Nc7GnV/U759T0tnWV3LTCp7bm53gDQlFgQlEb/yI1Ot/DM/YmurpYFL13j8+IjBdZed05+JQBEWzEthqSNwdD8hodjY2MTUnNsPVxyh2PTBHmxgRhQdrem0C0hErrIQokPAD2N/9FbtoFZukfXXF1TYVnBZ8UP1ycPb7b8VtMC8Nc7QXdJvD28hmO94ofzAppcDlvnCoZjd07NrzQx2bl3VV1nHQcQnZwQoG2fRvuHO9xJWexQY5xl4hTAzY+NFdx1tfw2TYKWl5OvCxShYCud6GfdY91vEbuLX5NT15lfmdRT31rH6cwDJBsS0LYVeiD/eK8+Ljw0VLc3rAdeFPomSDafOpVc7ceB22mw6sU2Hj4wdUBnvTdIcEIvU/MKYWfJOVuY19PnTdQmciW+tqTJPHUwCQvL7M0SAy5UzTp2++mdWgv7GK6sfcdYsCz42oCWX2fj269Nw4CanbF7K5OHKysX9SUQ8RwObbKPNqYmhrNdbwKOrc3NO5mnMu8sJ7lwiDZ8OpdGY9lLWGIiIHpvXe/DIvJpgJgfmVwfW5/TtKilifavHtKkplB34kG/jc2r22H7wzYPIutdiNAEG46f03p7Wxs6ICbEe3nZ8m34RODhk3E2o76pqadnN3HSEBKJR4xZXlwJaB78Rsmx3qysUw+4CWk2YqcE74T1Xl4JtiwbEskpXxDp42e/DV65etjHCtr37i0s3E2aJESbjk4HMavthwVt0b/VIMt4Zt86jrfAR5ywy8lH6MOi07jQb9a5aS4sjgXLj2TrYuEnECQnFzZZa08OgojHZkP3Efqyzh/bkEKvxTuQuE5pCX7WcJPM7SSid6T0jEGy4XsIvXxHBPXJOWfjJ/n8hM7FS7sniYjQJS4+TllLzwA8xsEMrPMRJMQLfCADLy0Coh9XNm+6C+zEShn11vVn/SYHIbGINJI2bFI0eiOPRNPmF9ZxiTe5aM/yE7bHCywAMcZM6lVAl9jQpBhbTc3cEEG+9dkM8eQgrK2NNfTGTiJadzBjiTbrjrd0+pXRORyOh5dS7C4iiUsjwktLIo1Is5dw6DQaVzsmLSIkRJiRvDeDNCmIdsiuvLq6hLK+PFRaO/3sretzEqxz6nJycqxjdTS30lgcOodL59M7OSTWeu+yspYyG6JXRHv764zXGU6Te3BmH7nLK3Y4fqt1cvyuXfHW+R62uZGaSkqRSvAToeni4WETz/L24yRY2GxNqGHFWm/dleDtx/IRCjIyIiMjuZOD2AgzYBTbIzRl4kQCXBtfHx9hWppSmtADAF8na+/4rX7oD/wSEaIpSIuIjLDRpvHFHAv6ZJ8z0m3oYl8XWF5OTk62fx6FILITtq9mfqTQWlNQHxGRHxnhMyIUenl5sT7pUfnEj3G1nQRpSrFKkQLoPx8i3FH7c96RmPhlLIRGQ7h0RJuvPdlD/j3kv/Sm2v8gf4Mgqam8Tzqcl5oqvcy1i7LDeB7kfRSSSnCsGHd44vcrZCOejmvj0IcJpgyDaCpz5kchSVRK1TjVEpiSOMFhcSmlshv8wVQUEkcJrgokUDw/CqmiUN3+75iD40Rzc1hLkI0kUajoGzil4QQ7UJDycXd5MqhRAAM9MNVOZgPPDv7xY7CplqyeeXbS4zEIQKJQP7lRKSukI6lU6goYEVNGGAJIUg9ipLti4K4AwYx+k0GOUg0QJJMRt4hBqYCjbgcp1Ou8AGq4QWZmKnRGIpXBSLQDMwnRgadMDXhgETXLIMwUnY8dlQp9VEUgzAUFiSlQaVymqaknwGTCzUiiaRyIMiUskEGQLGoY4DENwimMMMckkOrIoFKYUUsIYWGMYB4MLoNhEOYYAK4HG1AZBsEFoIAZbhAejEJ4VCr0WxiDigFhBAMELHA0ZYSvdcNQmAUggAn1L2Ayk2QQHpViCUyY+8PDM8MpC0AKxWDmzERkBTUszCARJDENKCm9VFMMyDQIY1w3YJTiV0AoNRH1F8aAUoqaYwkcUB12TOr1FdeplrxMgieYSYH2HWT0jsYkFU2MOFMGg5QUbFoFDBhU6HyAKaVmTkUwBlRKAOgNvg4VhhPcMOGMTOgIShhPGhMkMbgXegvukUohrAAphOsIKA0udSglVCHQHXEYBrRGBkliQqaWKXMRCKBQAiEkvAK6F7lOSYFjjsEVAKESLEEUhQEz2oAKf2WiI1JJoVhiEinhCAg0JbghVEap2woDU0skxTEugJBJiXOjmE4dhVQxCQGggEKxA3MJhCSwYG04M1Mb2FHQPI1mEtxAFIGyAk7FcQHq2QIwlUIYK4mZhIIqBrQBVJkSpsKwGpgSgg8EgERmdAHTgFFhySwdS+GZBAIPZAUzELCCwEwFiCvTwHEmCCA4wgpNpDB4IM4xOA7GEE7FhMBcgYZ07P00T2ZmbziaaDMJVEwqIYzhuBatnAJKWNh1y/AsA0LSGCSFQkEQBgwhHCSgSVNlSg0HbgRmAOozyE6hQHNmMglRIG4tMw4yHcduLVcRwhkEdLYpwVTgxjT1TJVWmifFgOAZSGFQGQ6jEEwmJQvwCMHRUCXTAOEFAAyDkgmqgglaGCSTGhwQwGQER4FEU3jEAkcY5BXM4AWjr9okrQ1nrE1C04yQCRPU9CXMVTgBTwLD0QTmmqwxoJCphOAUWBzBC2CjM00BnmstU6iwYU6BoakAlpRwginD1NQBMGCGgZmOTFiVTCpzNPKBjgbhDLRVUGBqYJgMCjXRMRPAaTAICIQwA8YgbgcORIMFB9bOBQHoN4qjKZPgyANzD1DXFoDAA6bBjEzmWgzG8QDMK4YjxMWtNR3raiYHKAfQJHA7AKMIPA8QKMGOptCLBxxTgMlax3BkDBJw8GkgqDr4NBWkHnwaBwIPUikp0LOYaMLaQAAWEKipAQdTEMypgzCiFQfbYHJXBKMj0q6WePApenc24OlTdEtVMMWgAs7e7enBAGD39OmiPxokgrZG6S9ZY3Ows5P2OsROGkS046GbR5uedG6yEWlDxMj2dcCMtVJ0B5m20W3/W0j8D/Lfhfx/kP8HByguNX095QYAAAAASUVORK5CYII=";var throwCard=function(t,h){var a=new Particle(id=0,t,h,2*Math.floor(6*Math.random()-3),16*-Math.random());particles.push(a)};document.addEventListener("mousedown",function(t){t.preventDefault(),canvas.remove(),clearInterval(render)},!1);var render=setInterval(function(){for(var t=0,h=particles.length;t<h;)particles[t].update()?t++:h--},1e3/60);setInterval(function(){throwCard(Math.floor(Math.random()*(document.body.clientWidth-200)+200),Math.floor(Math.random()*(document.body.clientHeight-200)+200))},500);</script>`);
            } else {
                if($(".list-group-contest-item").filter(function() {
                    return $(this).find(".contest-item-author a").text() == realName;
                }).length > 0) {
                    $("body").append(`<audio autoplay src="https://transfer.sh/apCNu/Undertale%20OST_%20011%20-%20Determination.mp3"/>`);
                    $("head").append(`<link rel="stylesheet" type="text/css" href="//undertalefonts.duodecima.technology/webfonts/stylesheet.css">`);
                    $("body").css("background-color", "#000");
                    $(".about-text").append(`<h1 style="font-size: 8em; color: white; text-align:center">GAME OVER</h1><p style="font-size: 3em; color: white; text-align:center">You cannot give up just yet...</p><p style="font-size: 1em; text-align:center">press X to appeal</p>`);
                    $("body").css("font-family", "Determination Mono");
                    $(document).keypress(function(e) {
                        console.log(e.which);
                        if(e.which == 120 || e.which == 1095 || e.which == 1063 || e.which == 88) {
                            // X pressed
                            // sorry Ricky xD
                            window.open("https://t.me/d_Rickyy_b");
                        }
                    });
                }
            }
        }
    }



    var section = $(".contest-section");
    var button = $("div.report-issue-block").find(".issue-send-button");

    // DELAYED LIST
    if(button.length == 0 && $(".section-url-field-wrap").length > 0) {
        section.append(`<h3>Delayed issues<span class="header-count" id="delayedCount">0</span></h3>`);
        section.append(`<div id="delayed" class="list-group-issues"></div>`);
        var issues = $("#delayed");
        var rule = /#(\d+)/.exec(section.find("h3").first().text())[1];
        var sectionId = /contest\/(.*?)\//.exec(document.URL)[1];
        GM_xmlhttpRequest({
            method: "GET",
            url: url + "/list",
            onload: function(e) {
                try {
                    var json = JSON.parse(e.response);
                    if(json["status"] != "ok") {
                        showAlert("Error! " + JSON.stringify(json));
                        return;
                    }
                    if(json["list"][sectionId] != undefined && json["list"][sectionId][rule] != undefined) {
                        $("#delayedCount").text(json["list"][sectionId][rule].length);
                        json["list"][sectionId][rule].forEach(function(i, index) {
                            var appended = $(`<div class="list-group-contest-item">
<div class="contest-item-num" style="width: 100%">
<a href="${document.URL}?url=${i["url"]}" style="color: #333">${i["comment"]}</p></a>
</div>
<div class="contest-item-date" style="width: 100%">${i["reportTime"]}
<button type="button" data-id="${sectionId}:${rule}:${index}" data-json="" class="issue-btn post-now-btn btn btn-link btn-lg iv-btn issue-send-button">Post now</button>
<button type="button" data-id="${sectionId}:${rule}:${index}" data-json="" class="issue-btn remove-btn btn btn-link btn-lg iv-btn issue-send-button">Remove issue</button>
</div>
</div>`).appendTo(issues);
                            //i.key = index;
                            appended.find("button").attr("data-json", JSON.stringify(i));
                            appended.find(".issue-btn").click(function() {
                                console.log($(this).data("json"));
                                GM_xmlhttpRequest({
                                    method: "POST",
                                    url: url + ($(this).hasClass("remove-btn") ? "/remove" : "/post_now"),
                                    data: JSON.stringify($(this).data("json")),
                                    headers: {
                                        "Content-Type": "application/json"
                                    },
                                    onload: function(e) {
                                        console.log(e.response);
                                        try {
                                            var json = JSON.parse(e.response);
                                            if(json["status"] != "ok") {
                                                showAlert("Error! " + JSON.stringify(json));
                                                return;
                                            }
                                            showAlert("Success!");
                                        } catch(e) {
                                            showAlert("Error while parsing json: " + e);
                                        }
                                    },
                                    onerror: error,
                                    ontimeout: error,
                                    onabort: error
                                });
                            });
                        });
                    }
                } catch(e) {
                    showAlert("Error while parsing json: " + e);
                }
            },
            onerror: error,
            ontimeout: error,
            onabort: error
        });
    }

    // LIST ALL ISSUES
    if(/candidate(\d+)/.exec(document.URL) != null) {
        section.first().append(`<h3>Waiting issues<span class="header-count" id="waitingCount">0</span></h3>`);
        section.first().append(`<div id="waiting" class="list-group-issues"></div>`);
        var issuesWaiting = $("#waiting");
        var candidateId = /candidate(\d+)/.exec(document.URL)[1];
        var sect = /contest\/(.*?)\//.exec(document.URL)[1];
        var listNumbers = $.makeArray($(".contest-item-num").map(function() {
            return /template(\d+)/.exec($(this).find("a").attr("href"))[1]
        }));
        var request = {
            section: sect,
            rules: listNumbers
        };
        console.log(request);
        GM_xmlhttpRequest({
            method: "POST",
            data: JSON.stringify(request),
            headers: {
                "Content-Type": "application/json"
            },
            url: url + "/get_issues",
            onload: function(e) {
                try {
                    var json = JSON.parse(e.response);
                    if(json["status"] != "ok") {
                        showAlert("Error! " + JSON.stringify(json));
                        return;
                    }

                    if(json["list"] != undefined && json["list"].length > 0) {
                        var list = json["list"];
                        $("#waitingCount").text(list.length);
                        list.forEach(function(i, index) {
                            var appended = $(`<div class="list-group-contest-item">
<div class="contest-item-num" style="width: 100%">
<a href="${document.URL.replace(/candidate(\d+)/, "template" + listNumbers[0])}?url=${i["url"]}" style="color: #333">${i["comment"]}</p></a>
</div>
<div class="contest-item-date" style="width: 100%">
<button type="button" data-id="${sectionId}:${rule}:${index}" data-json="" class="issue-btn remove-btn btn btn-link btn-lg iv-btn issue-send-button">Remove issue</button>
</div>
</div>`).appendTo(issuesWaiting);
                            //i.key = index;
                            appended.find("button").attr("data-json", JSON.stringify(i));
                            appended.find(".issue-btn").click(function() {
                                console.log($(this).data("json"));
                                GM_xmlhttpRequest({
                                    method: "POST",
                                    url: url + ($(this).hasClass("remove-btn") ? "/remove_all" : "/post_now"),
                                    data: JSON.stringify($(this).data("json")),
                                    headers: {
                                        "Content-Type": "application/json"
                                    },
                                    onload: function(e) {
                                        console.log(e.response);
                                        try {
                                            var json = JSON.parse(e.response);
                                            if(json["status"] != "ok") {
                                                showAlert("Error! " + JSON.stringify(json));
                                                return;
                                            }
                                            showAlert("Success!");
                                        } catch(e) {
                                            showAlert("Error while parsing json: " + e);
                                        }
                                    },
                                    onerror: error,
                                    ontimeout: error,
                                    onabort: error
                                });
                            });
                        });
                    }
                } catch(e) {
                    showAlert("Error while parsing json: " + e);
                }
            },
            onerror: error,
            ontimeout: error,
            onabort: error
        });
    }

    if(button.length > 0) {
        $(document).on('iv:result:updated', function() {
            var button = $("div.report-issue-block:not(.hide)").find(".issue-send-button");

            button.text("Send issue now");
            button.parent().append(`<button type="button" id="delay" class="btn btn-link btn-lg iv-btn issue-send-button" disabled>Delay issue</button>`);
            button.parent().append(`<button type="button" id="add_issue" class="btn btn-link btn-lg iv-btn issue-send-button" disabled>Add issue</button>`);
            var delay = $("#delay");
            var add_issue = $("#add_issue");

            delay.click(function() {
                var form = button.closest("form");

                var comment = form.find('textarea[name="comment"]').val();
                var type = form.find('input[name="type"]').val();

                var request = {
                    url: App.state.result_url,
                    section: App.state.section,
                    rules_id: App.state.rules_id || 0,
                    random_id: App.state.random_id || '',
                    issue_id: App.state.issue_id || 0,
                    regions: App.state.originalRegions + ';' + App.state.resultRegions,
                    type: type,
                    comment: comment
                };

                GM_xmlhttpRequest({
                    method: "POST",
                    url: url + "/report",
                    data: JSON.stringify(request),
                    headers: {
                        "Content-Type": "application/json"
                    },
                    onload: function(e) {
                        try {
                            var json = JSON.parse(e.response);
                            if(json["status"] != "ok") {
                                showAlert("Error! " + JSON.stringify(json));
                                return;
                            }
                            showAlert("Report successfully scheduled, will be posted in " + json["date"]);
                        } catch(e) {
                            showAlert("Error while parsing json: " + e);
                        }
                    },
                    onerror: error,
                    ontimeout: error,
                    onabort: error
                });
            });

            add_issue.click(function() {
                var form = button.closest("form");

                var comment = form.find('textarea[name="comment"]').val();
                var type = form.find('input[name="type"]').val();

                var request = {
                    url: App.state.result_url,
                    section: App.state.section,
                    rules_id: App.state.rules_id || 0,
                    random_id: App.state.random_id || '',
                    issue_id: App.state.issue_id || 0,
                    regions: App.state.originalRegions + ';' + App.state.resultRegions,
                    type: type,
                    comment: comment
                };

                GM_xmlhttpRequest({
                    method: "POST",
                    url: url + "/add_issue",
                    data: JSON.stringify(request),
                    headers: {
                        "Content-Type": "application/json"
                    },
                    onload: function(e) {
                        try {
                            var json = JSON.parse(e.response);
                            if(json["status"] != "ok") {
                                showAlert("Error! " + JSON.stringify(json));
                                return;
                            }
                            showAlert("Report successfully added");
                        } catch(e) {
                            showAlert("Error while parsing json: " + e);
                        }
                    },
                    onerror: error,
                    ontimeout: error,
                    onabort: error
                });
            });
        });
    }
})();