var wordsEnumerated = false;
var docsEnumerated = false;

$(document).ready(function() {
    var id = window.location.toString().match(/[\?&]highlight_word_id=([0-9]+)/);
    if (id) enumerateWords(id[1]);

    id = window.location.toString().match(/[\?&]highlight_doc_id=([0-9]+)/);
    if (id) enumerateDocuments(id[1]);

    $(document.body).bind("click", function(e) {
        var wordExpl = e.target.className.indexOf("b-wrd-expl") > -1;
        var docExpl = e.target.className.indexOf("b-doc-expl") > -1;
        var bugReport = e.target.className.indexOf("bug-reporter") > -1;

        if (wordExpl) {
            showHint(e, "word");
        } else if (docExpl) {
            showHint(e, "document");
        } else if (!bugReport) {
            hideHint();
        }
    });

    $(document.body).bind("mouseover", function(e) {
        var kwicExpl = e.target.className.indexOf("b-kwic-expl") > -1;

        if (kwicExpl) {
            showKwicHint(e);
        } else {
            hideKwicHint();
        }
     });
});

function enumerateWords(ind) {
    if (wordsEnumerated) return;
    wordsEnumerated = true;
    $(".b-wrd-expl").each(function(i) {
        this.setAttribute("_id", i);
        if (i == ind)
            this.style.cssText = 'background-color: yellow';
            //this.setAttribute('style', 'background-color: yellow');
    });
}

function enumerateDocuments(ind) {
    if (docsEnumerated) return;
    docsEnumerated = true;
    $(".b-doc-expl").each(function(i) {
        this.setAttribute("_id", i);
        if (i == ind)
            this.setAttribute('style', 'background-color: yellow');
    });
}

function showHint(e, type) {
    var el = e.target;

    type = type + "-info";

    // Current tooltips
    var tooltips = $(document.body).find(".b-tooltip");

    if(el.className.indexOf("expl") > -1) {
        // If tooltip is present for the current word, remove it
        if($(el).find(".b-tooltip").length > 0) {
            var tooltip = $(el).find(".b-tooltip")[0];

            tooltip.parentNode.removeChild(tooltip);
        } else {
            // Remove tooltips for other words if present
            tooltips.each(function() {
                if(this && this.parentNode) {
                    this.parentNode.removeChild(this);
                }
            });

            var requestText = el.getAttribute("explain");
            var url = "cgi/"+window.location.toString().match(/\/([\w|\-]+)\.html/)[1] + (type == "document-info" ? "-docinfo.html" :"-explain.html"); 
            var params = window.location.search.replace(/text=[^&]*/, "").replace(/source=[^&]*/, "").replace(/docid=[^&]*/, "").replace(/language=[^&]*/, "");

            url += params + "&text=" + type + "&requestid=" + generateId();

            var bugReportUrl = window.location.toString();
            bugReportUrl = bugReportUrl.replace(/highlight_word_id=[^&]*/, "").replace(/highlight_doc_id=[^&]*/, "");

            var lang_attr = el.getAttribute("l");
            if (lang_attr && lang_attr != "") {
                url += "&language=" + lang_attr;
            } else {
                url += "&language=ru";
            }

            var url_add = ""
            if(type == "word-info") {
                url_add += "&source=" + requestText;
                enumerateWords(-1);
                bugReportUrl += "&highlight_word_id=" + el.getAttribute("_id");
            }

            if(type == "document-info") {
                url_add += "&docid=" + requestText;
                enumerateDocuments(-1);
                bugReportUrl += "&highlight_doc_id=" + el.getAttribute("_id");
            }

            url += url_add
            $.get(url, function(response) {
                var tooltip = document.createElement("div");
                tooltip.className = "b-tooltip";
                tooltip.innerHTML = response.replace(/([\|\,])/g, "$1<wbr/>"); // Insert soft breaks
                tooltip.setAttribute("url", bugReportUrl);
                tooltip.setAttribute("id", "b-tooltip");
                coords = pointer(e);
                tooltip.style.top = coords[1] + 10 + 'px';
                tooltip.style.left = coords[0] + 'px';
                tooltip.style.zIndex = 100;
                el.appendChild(tooltip);
            });
        }
    }
    return false;
}

function hideHint() {
    var tooltips = $(document.body).find(".b-tooltip");

    tooltips.each(function() {
        if(this && this.parentNode) {
            this.parentNode.removeChild(this);
        }
    });
}

function generateId() {
    return ((new Date()).getTime() + Math.round(Math.random() * 10000));
}

function pointer(evt) {
    return [evt.pageX || (evt.clientX + (document.documentElement.scrollLeft || document.body.scrollLeft)),
        evt.pageY || (evt.clientY + (document.documentElement.scrollTop || document.body.scrollTop))];
}

function openSettings() {
    var oDivBlocker = document.getElementById('blocker');

    if (oDivBlocker) {
        document.getElementsByTagName('body')[0].appendChild(oDivBlocker);
        oDivBlocker.style.display = 'block';
    }

    var seed = document.getElementById('seed');
    if (seed)
      seed.value = Math.floor(Math.random() * (32767))

    var oDivInner = document.getElementById('search-form');
    if (oDivInner){
        oDivInner.style.visibility = "hidden";
        oDivInner.style.display = "block";
        oDivInner.style.left = (document.body.offsetWidth / 2) - (oDivInner.offsetWidth / 2) + "px";
        oDivInner.style.visibility = "visible";
    }
    var sortSelect = document.getElementById('settings-sort-select');
    setRangesBySort (sortSelect.options[sortSelect.selectedIndex].value);
    var outputSelect = document.getElementById('settings-output-select');
    setRangesByOutput (outputSelect.options[outputSelect.selectedIndex].value);
}


function getRadioGroupValue(radioGroupObj)
{
  for (var i=0; i < radioGroupObj.length; i++)
    if (radioGroupObj[i].checked) return radioGroupObj[i].value;
  return null;
}


function closeSettings () {
    var dpp = document.getElementsByName("dpp")[0].value;
    var spd = document.getElementsByName("spd")[0].value;
    var spp = document.getElementsByName("spp")[0].value;
    var kwsz = document.getElementsByName("kwsz")[0].value;

//    var out = getRadioGroupValue(document.search_sort.out);

    document.cookie = "dpp=" + dpp + ";domain=ruscorpora.ru";
    document.cookie = "spd=" + spd + ";domain=ruscorpora.ru";
    document.cookie = "spp=" + spp + ";domain=ruscorpora.ru";
    document.cookie = "kwsz=" + kwsz + ";domain=ruscorpora.ru";
//    document.cookie = "out=" + out + ";domain=ruscorpora.ru";

    var oDivBlocker = document.getElementById('blocker');
    if (oDivBlocker) {
        oDivBlocker.style.display = 'none';
    }
    var oDivInner = document.getElementById('search-form');
    if (oDivInner) {
        oDivInner.style.display = 'none';
    }
}

function setDefaults() {
    var dpp = settings.dpp;
    var spd = settings.spd;
    var spp = settings.spp;
    var kwsz = settings.kwsz;

    document.getElementsByName("dpp")[0].value = dpp;
    document.getElementsByName("spd")[0].value = spd;
    document.getElementsByName("spp")[0].value = spp;
    document.getElementsByName("kwsz")[0].value = kwsz;
}

function cleanSubcorpus() {
    document.cookie = settings.mode + "=;domain=ruscorpora.ru";
}

function saveOnDisk() {
    var url = window.location.toString();
    var params = window.location.search.replace(/savepath=[^&]*/, "")
    var date = new Date();
    var path = date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate() + "-" + date.getHours() + "-" + date.getMinutes() + "-" + date.getSeconds();

    url += params + "&requestid=" + generateId() + "&savepath=" + path;

    new Image().src = url;
    alert(settings.saveOnDiskMessage + path);
}

function toggleDisplayStyle(elem) {
    if (elem == null) return;
    if (elem.style.display == '')
        elem.style.display = 'none';
    else
        elem.style.display = '';
}

function showBugReporter() {
    toggleDisplayStyle(document.getElementById("bug-reporter-caption"));
    toggleDisplayStyle(document.getElementById("bug-reporter-form"));
}

function bugReport() {
    var tooltip = document.getElementById("b-tooltip");
    var url = tooltip.getAttribute("url");
    var msg_elem = document.getElementById("bug-comment");
    var msg = "";
    if (msg_elem && msg_elem.value)
        msg = msg_elem.value;
    msg = encodeURIComponent (msg);
    //$.post("bug-report.xml", {url: encodeURIComponent(url), msg: msg}, function(data) {
    //var env = window.location.toString().match(/env=([\w|\-]*)/);
    //if (env != null)
    //    env = env[0];
    //else
    //    end = "";
    $.post("bug-report.html", {url: url, msg: msg}, function(data) {
     if (data.getElementsByTagName("bug-reporter").length > 0) {
        var caption = document.getElementById("bug-reporter-caption");
        if (caption) caption.innerHTML = 'Спасибо, Ваше сообщение отправлено!';
        showBugReporter();
     } else {
        alert ('Извините, произошла ошибка при отправке сообщения.');
        hideHint();
     }
    }, "html");
}

function showKwicHint(e) {
  hideKwicHint();
  var el = e.target;
  var tooltip = document.createElement("div");
  tooltip.className = "b-kwic-tooltip";
  tooltip.innerHTML = el.getAttribute("msg");
  tooltip.setAttribute("id", "b");
  tooltip.style.position = 'absolute';
  coords = getOffset(el);
  tooltip.style.top = coords.top + 2 + 'px';
  tooltip.style.left = coords.left + 55 + 'px';
  tooltip.style.zIndex = 100;
  document.body.appendChild(tooltip);
}

function hideKwicHint() {
    var tooltips = $(document.body).find(".b-kwic-tooltip");

    tooltips.each(function() {
        if(this && this.parentNode) {
            this.parentNode.removeChild(this);
        }
    });

}







function getOffset(elem) {
    if (elem.getBoundingClientRect) {
        // "правильный" вариант
        return getOffsetRect(elem)
    } else {
        // пусть работает хоть как-то
        return getOffsetSum(elem)
    }
}

function getOffsetSum(elem) {
    var top=0, left=0
    while(elem) {
        top = top + parseInt(elem.offsetTop)
        left = left + parseInt(elem.offsetLeft)
        elem = elem.offsetParent
    }

    return {top: top, left: left}
}

function getOffsetRect(elem) {
    // (1)
    var box = elem.getBoundingClientRect()

    // (2)
    var body = document.body
    var docElem = document.documentElement

    // (3)
    var scrollTop = window.pageYOffset || docElem.scrollTop || body.scrollTop
    var scrollLeft = window.pageXOffset || docElem.scrollLeft || body.scrollLeft

    // (4)
    var clientTop = docElem.clientTop || body.clientTop || 0
    var clientLeft = docElem.clientLeft || body.clientLeft || 0

    // (5)
    var top  = box.top +  scrollTop - clientTop
    var left = box.left + scrollLeft - clientLeft

    return { top: Math.round(top), left: Math.round(left) }
}


function get_cookie(str) {
  var beg = document.cookie.indexOf(str + "=");
  if(beg==-1)
    return "";
  var end = document.cookie.indexOf(";", beg + str.length);
  if(end==-1)
    end = document.cookie.length;
  return document.cookie.substring(beg + str.length + 1, end);
}


function go_to_the_other_corpus(mode, url) {
  var x = encodeURI(get_cookie(mode));
  if (x) {
    x = x.split("&");
    if (x.length > 0) {
      url += "&mycorp=" + x[0];
    }
    if (x.length > 1) {
      url += "&mysent=" + x[1];
    }
    if (x.length > 2) {
      url += "&mysize=" + x[2];
    }
    if (x.length > 3) {
      url += "&mysentsize=" + x[3];
    }
  }
  window.location = url;
}

function toggleInputs (id, value) {
  var inp = document.getElementById("settings-" + id);
  if (inp) {
   inp.className = value ? "" : "disabled";
   inp.disabled = !value;
  }
  var inpCaption = document.getElementById("settings-" + id + "-caption");
  if (inpCaption) {
    inpCaption.className = value ? "" : "disabled";
    inp.disabled = !value;
  }
}

function setRangesBySort(value) {
  var isCont = value.substr(0,4) == "cont";
  toggleInputs("spp", isCont);
  toggleInputs("dpp", !isCont);
  toggleInputs("spd", !isCont);
}

function setRangesByOutput(value) {
  var isKWIC = value.substr(0,4) == "kwic";
  toggleInputs("kwsz", isKWIC);
}




var dontclosehelp;

function adjustIFrameSize (iframeWindow) {
    var frameheight = 500;
    var height = document.body.clientHeight;
    var iframeElement;
    if (iframeWindow.document.height) {
        iframeElement = document.getElementById(iframeWindow.name);
        frameheight = iframeWindow.document.height;
    }
    else if (document.all) {
        iframeElement = document.all[iframeWindow.name];
        if (iframeWindow.document.compatMode && iframeWindow.document.compatMode != 'BackCompat')
            frameheight = iframeWindow.document.documentElement.scrollHeight + 5;
        else
            frameheight = iframeWindow.document.body.scrollHeight + 5;
    }
    if (frameheight > height - 150){
        if (document.getElementById("closeinfoframe")) //opera
            document.getElementById("closeinfoframe").style.top = '30px';
        else if (document.getElementById("closeinfo"))
            document.getElementById("closeinfo").style.top = '30px';
        iframeElement.style.top = '30px';
        if (frameheight > height - 50)
            frameheight = height - 50;
    }
    iframeElement.style.height = frameheight + 'px';
    dontclosehelp = 0;
}

function showhelp(Src,w) {
    if (w == 0)
        w = 0.8;
    if (w < 1)
        w *= document.body.clientWidth;
    var x = (document.body.clientWidth-w)/2;
    var realw = (!document.all || document.compatMode && document.compatMode != 'BackCompat')?w+5:w;
    document.getElementById("info").style.visibility = "visible";
    if (!false /*window.opera*/){
        document.getElementById("closeinfo").innerHTML = '<iframe id="closeinfoframe" name="closeinfoframe" src="closeinfo.html" width="14" height="14" style="position: absolute; z-index: 200; border: 0; margin:0; top: 90px; left: '+ (x + realw - 15) + 'px;" />';
    } else {
        document.getElementById("closeinfo").style.left = (x+realw-15) + 'px';
        document.getElementById("closeinfo").style.top = '90px';
    }
    document.getElementById("info").innerHTML = '<iframe id="infoframe" name="infoframe" src="' + Src + '" width="' + w + '" height="500" style="position: absolute; z-index: 100; top: 90px; left: '+ x +'px;" />';
    document.getElementById("closeinfo").style.visibility = "visible";
    dontclosehelp = 1;
    return false;
}

function closehelp(){
    document.getElementById("closeinfo").style.visibility = "hidden";
    document.getElementById("info").style.visibility = "hidden";
}

function bodyclosehelp(){
    if (dontclosehelp == 0)
        closehelp();
}

function pager(cP,lP) {
    if (lP) {
        document.write('<p class="pager">РЎС‚СЂР°РЅРёС†С‹: ');
        var WOPLink = new String(document.location);
        WOPLink = WOPLink.replace(/&p=[0-9]+/,"");
        if (cP) document.write('<a href="'+ WOPLink + '&p=' + (cP-1) + '">РїСЂРµРґС‹РґСѓС‰Р°СЏ СЃС‚СЂР°РЅРёС†Р°</a>');
        left_pager_shift = right_pager_shift = 4;
        if (cP < left_pager_shift) {
          left_pager_shift = cP;
          right_pager_shift = 8 - left_pager_shift;
        }
        if (cP + right_pager_shift > lP) {
          right_pager_shift = lP - cP;
          left_pager_shift = 8 - right_pager_shift;
          if (cP < left_pager_shift)
            left_pager_shift = cP
        }
        for (i = cP - left_pager_shift; i <= cP + right_pager_shift; ++i) {
          if (i == cP)
            document.write('<b>'+(cP+1)+'</b>');
          else
            document.write('<a href="'+ WOPLink + (i==0?'':('&p=' + i)) + '">'+(i+1)+'</a>');
        }
        if (lP > cP) document.write('<a href="'+ WOPLink + '&p=' + (cP+1) + '">СЃР»РµРґСѓС‰Р°СЏ СЃС‚СЂР°РЅРёС†Р°</a>');
        document.write('</p>');
    }
}

function all_examples(docid) {
  var exampleLink = new String(document.location);
  if (-1 == exampleLink.indexOf("&docid=")) {
    exampleLink = exampleLink.replace(/&spd=[0-9]+&/,"&spd=1000&");
    exampleLink = exampleLink.replace(/&p=[0-9]+/,"");
    exampleLink += "&docid=" + docid;
    document.write('<a href="'+ exampleLink + '">Р’СЃРµ РїСЂРёРјРµСЂС‹</a>');
  }
}
