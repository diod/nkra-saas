var values = {};
var totals = [];
var query = "";
var year_start = window.start_year;
var year_end = window.end_year;
var smoothing = window.smoothing;

function showTooltip(x, y, contents) {
  $('<div id="tooltip">' + contents + '</div>').css( {
   position: 'absolute',
   display: 'none',
   top: y + 5,
   left: x + 5,
   border: '1px solid #fdd',
   padding: '2px',
   'background-color': '#fee',
   opacity: 0.80
  }).appendTo("body").fadeIn(200);
}

function init() {
 query = "";
 for (var ind in queries) {
   if (queries[ind] == "") continue;
   if (query != "") query += ", ";
   query += queries[ind];
 }
 document.getElementById("query").value = query;
 document.getElementById("year_start").value = year_start;
 document.getElementById("year_end").value = year_end;
 document.getElementById("smoothing").value = smoothing.toString();
}

function prepare() {
 plots = [];
 var data = {};
 for (var ind in values) {
  data[ind] = {};
  for (var i = 0; i < values[ind].length; ++i) {
    current_values = values[ind][i][0].split(" | ");
    var count = 0;
    for (var j = 0; j < current_values.length; ++j) {
      var value = current_values[j];
      var start = parseInt(value.substr(0, 4));
      var finish = start;
      if (value.length > 4 && value[4] == '-') {
        finish = parseInt(value.substr(value.length-4, 4));
      }
      count += finish - start + 1;
    }
    var part = parseInt(values[ind][i][1]) * 1000000.0 / count;
    for (var j = 0; j < current_values.length; ++j) {
      var value = current_values[j];
      var start = parseInt(value.substr(0, 4));
      var finish = start;
      if (value.length > 4 && value[4] == '-') {
        finish = parseInt(value.substr(value.length-4, 4));
      }
      for (var year = start; year <= finish; ++year) {
        var year_str = year.toString();
        if (!(data[ind][year_str]))
          data[ind][year_str] = 0;
        data[ind][year_str] += part / totals[year_str];
      }
    }
  }
 }
 if (relative) {
   for (var year = year_start; year <= year_end; ++year)
     data[1][year.toString()] *= 1000000.0 / data[2][year.toString()];
 }

 for (var ind in values) {
  smoothed = [];
  for (var year = year_start; year <= year_end; ++year) {
    average = 0.0;
    var start = Math.max(year - smoothing, year_start);
    var finish = Math.min(year + smoothing, year_end);
    for (var y = start; y <= finish; ++y) {
      var y_str = y.toString();
      if (data[ind][y_str])
        average += data[ind][y_str];
    }
    average /= (finish - start + 1);
    average = Math.round(average * 100000.0) / 100000.0;
    smoothed.push([year, average]);
  }

  plots.push({data: smoothed, label: ind});
  if (relative)
    break;
 }


 $.plot(
  $("#placeholder"), 
  plots, 
  {
   series: { lines: { show: true }, points: { radius: 1, show: false } },
   grid: {hoverable: true, clickable: true},
   xaxis: {min: year_start, max: year_end},
   yaxix: { show: false}
  }
 );

 var previousPoint = null;
 $("#placeholder").bind("plothover", function (event, pos, item) {
   if (item) {
     if (previousPoint != item.dataIndex) {
       previousPoint = item.dataIndex;
       $("#tooltip").remove();
       var x = item.datapoint[0],
       y = item.datapoint[1].toFixed(5);
       label = item.series.label;
       if (label != "") {
         label += ", "
       }
       showTooltip(item.pageX, item.pageY, label + x + ": " + y);
     }
   } else {
     $("#tooltip").remove();
     previousPoint = null;
   }
 });
}

function new_query() {
  var q = document.getElementById("query").value;
  var req = q;
  q = q.replace(/ /g, "\u00A0");
  var url = "http://processing.ruscorpora.ru:8888/graphic.xml?env=alpha&mode=graphic_main" +
            "&mycorp=&mysent=&mysize=&mysentsize=&mydocsize=&dpp=100&spp=&spd=1&text=lexform" +
            "&sort=i_year_created&g=i_year_created&lang=ru&nodia=1";
  url += "&startyear=" + document.getElementById("year_start").value;
  url += "&endyear=" + document.getElementById("year_end").value;
  url += "&smoothing=" + document.getElementById("smoothing").value;
  url += "&req=" + encodeURIComponent(req);
  location.replace(url);
}

function toggleElem(id) {
  var el = document.getElementById(id);
  if (!el) return;
  if (el.style.display == "none") {
    el.style.display = "";
    return true;
  } else {
    el.style.display = "none";
    return false;
  }
}

function toggleTables() {
  var visible = toggleElem("tables");
  var captionElem = document.getElementById("tablesCaption");
  var captionTriangle = document.getElementById("tablesCaptionTriangle");
  if (visible) {
    captionElem.innerHTML = "Скрыть таблицы";
    captionTriangle.innerHTML = "\u25B2";
  } else {
    captionElem.innerHTML = "Показать таблицы";
    captionTriangle.innerHTML = "\u25BC";
  }  
  prepare();
}

function GoogleNgramViewerLink() {
  var url = "http://ngrams.googlelabs.com/graph?";
  var q = '';
  for (var ind in values) {
    if (queries[ind] != '') {
      if (q != '') q += ",";
      q += queries[ind]
    }
  }
  q = q.split("\u00A0").join(" ");
  url += "content=" + encodeURIComponent(q);
  url += "&year_start=" + year_start.toString();
  url += "&year_end=" + year_end.toString();
  url += "&corpus=12";
  url += "&smoothing=" + smoothing.toString();
  window.open(url);
}

