<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE xsl:stylesheet SYSTEM "symbols.ent">
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:str="http://exslt.org/strings"
                xmlns:x="http://www.yandex.ru/xscript"
                extension-element-prefixes="str x"
                version="1.0">

  <xsl:import href="util.xsl"/>
  <xsl:import href="metrika.xsl"/>

  <xsl:output method="html" indent="no" doctype-public="-//W3C//DTD HTML 4.01//EN" doctype-system="http://www.w3.org/TR/html4/strict.dtd"/>

  <!-- страница с поиском -->
  <xsl:variable name="page-name" select="concat(/page/@name, /page/@ext)" />

  <!-- параметры страницы -->
  <xsl:key name="param" match="/page/state/param" use="@name" />

  <xsl:variable name="param" select="/page/state/param" />

  <!-- Запрос введенный пользователем -->
  <xsl:variable name="text" select="/page/searchresult/body/request/query/word/@lex"/>

  <!-- имя страницы на которой прикручен поиск -->
  <xsl:variable name="page" select="/page/@name"/>

  <xsl:template match="param[@name='text']" mode="request"/>
  <xsl:template match="param[@name='p']" mode="request"/>

  <!-- номер текущей страницы пейджера -->
  <xsl:variable name="p" select="/page/yandexsearch/response/results/grouping/page"/>
  <!-- переменная с узлом, в котором содержатся параметры запросов -->
  <xsl:variable name="format" select="/page/searchresult/body/request/format" />

  <!-- текущая страница -->
  <xsl:variable name="curpage" select="number(/page/searchresult/body/request/@page) + 1" />

  <!-- Если данный файл обрабатывается из Yandex.Server, -->
  <!-- следующие параметры будут переписаны обработчиком   -->
  <xsl:param name="script" select="concat('/', $page-name)"/>
  <xsl:param name="images" select="'/i/'"/>
  <!-- Этот элемент не должен производить какой-либо вывод -->
  <xsl:template match="request"/>
  <!-- форма поиска  на этой странице другая -->
  <xsl:template name="search"/>

  <xsl:variable name="allowLineBreaks" select="$mode='poetic' or $mode='murco' or $mode='accent'" />

  <xsl:variable name="slav" select="$mode='orthlib' or $mode='old_rus' or $mode='birchbark' or $mode='mid_rus'" />
  <xsl:variable name="hide_freq_list" select="$mode='para' or $slav" />

  <xsl:variable name="kwic-size">
   <xsl:choose>
    <xsl:when test="$param[@name='kwsz']">
     <xsl:value-of select="$param[@name='kwsz']" />
    </xsl:when>
    <xsl:otherwise>
     <xsl:value-of select="'5'" />
    </xsl:otherwise>
   </xsl:choose>
  </xsl:variable>

  <xsl:variable name="server" select="/page/state[@name='search-host']" />

  <xsl:variable name="environment">
   <xsl:choose>
    <xsl:when test="$server='http://achelata.yandex.ru:8002'">
     <xsl:value-of select="'beta'" />
    </xsl:when>
    <xsl:when test="$server='http://ruscorpora-beta.haze.yandex.net:8002'">
     <xsl:value-of select="'beta'" />
    </xsl:when>
    <xsl:otherwise>
     <xsl:value-of select="'release'" />
    </xsl:otherwise>
   </xsl:choose>
  </xsl:variable>

  <xsl:variable name="env-infix">
   <xsl:choose>
    <xsl:when test="$environment='beta'">
     <xsl:text>beta/</xsl:text>
    </xsl:when>
   </xsl:choose>
  </xsl:variable>

  <xsl:template name="beta-logo">
   <xsl:choose>
    <xsl:when test="$environment='test'">
     <xsl:text> (test)</xsl:text>
    </xsl:when>
    <xsl:when test="$environment='beta'">
     <xsl:text> (&#946;)</xsl:text>
    </xsl:when>
   </xsl:choose>
  </xsl:template>

  <xsl:template name="h1">
   <br />
   <h1>
    <xsl:value-of select="$lang/results" />
    <xsl:text> </xsl:text>
    <xsl:value-of select="$lang/corpora-list/corpus[@mode=$mode]/@in" />
    <xsl:call-template name="beta-logo" />
   </h1>
   <br clear="all" />
  </xsl:template>

  <xsl:template name="h1-url">
   <xsl:choose>
    <xsl:when test="$param[@name='sort']">
     <h1>
      <a>
       <xsl:attribute name="href">
        <xsl:value-of select="concat('/', $page-name, '?')" />
        <xsl:apply-templates select="$param[@name!='docid'][@name!='sid'][@name!='p']" mode="page-url"/>
       </xsl:attribute>
       <xsl:value-of select="$lang/results" />
      </a>
      <xsl:call-template name="beta-logo" />
     </h1>
     <br clear="all"/>
    </xsl:when>
    <xsl:otherwise>
     <br clear="all"/>
    </xsl:otherwise>
   </xsl:choose>
  </xsl:template>


  <xsl:variable name="choose_corpus_url">
   <xsl:value-of select="$lang/choose_corp/url_prefix" />
   <xsl:value-of select="$env-infix" />
   <xsl:value-of select="$lang/choose_corp/url_infix" />
   <xsl:value-of select="$param[@name='mode']" />
   <xsl:value-of select="$lang/choose_corp/url_postfix" />
  </xsl:variable>

  <xsl:variable name="to_search">
   <xsl:value-of select="$lang/to_search/url_prefix" />
   <xsl:value-of select="$env-infix" />
   <xsl:value-of select="$lang/to_search/url_infix" />
   <xsl:value-of select="$param[@name='mode']" />
   <xsl:value-of select="$lang/to_search/url_postfix" />
  </xsl:variable>


  <xsl:variable name="kwic-word-pos">
   <xsl:choose>
    <xsl:when test="$param[@name='kwpos']">
     <xsl:value-of select="$param[@name='kwpos']" />
    </xsl:when>
    <xsl:otherwise>
     <xsl:value-of select="'0'" />
    </xsl:otherwise>
   </xsl:choose>
  </xsl:variable>


  <xsl:variable name="ln">
    <xsl:choose>
      <xsl:when test="$param[@name='lang']">
        <xsl:value-of select="$param[@name='lang']" />
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="'ru'" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="lang" select="/page/langs/*[name() = $ln]" />

  <xsl:variable name="search-type" select="/page/searchresult/body/result/@search-type" />


  <xsl:template match="/">
    <xsl:choose>
      <xsl:when test="key('param', 'xml-result')">
        <xsl:value-of select="x:http-header-out('Content-Type', 'text/xml; charset=utf-8')"/>
        <xsl:apply-templates select="page/searchresult" mode="xml" />
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="page"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- шаблоны, использующиеся при отображении страницы как xml документа -->
  <xsl:template match="*" mode="xml">
    <xsl:element name="{name(.)}">
      <xsl:apply-templates select="@*" mode="xml" />
      <xsl:apply-templates mode="xml" />
    </xsl:element>
  </xsl:template>

  <xsl:template match="@*" mode="xml">
    <xsl:attribute name="{name(.)}">
      <xsl:value-of select="." />
    </xsl:attribute>
  </xsl:template>

  <xsl:template match="sysinfo" mode="xml">
    <xsl:comment>здесь было сисинфо</xsl:comment>
  </xsl:template>

  <xsl:template match="request/@page" mode="xml">
    <xsl:attribute name="mama">papa</xsl:attribute>
  </xsl:template>

  <xsl:template match="format/@* | query" mode="xml" />


  <!-- отсюда начинаются преобразования не xml'ные-->

  <xsl:variable name="mode" select="/page/state/param[@name='mode']"/>

  <xsl:template match="page">
    <html>
      <head>
        <xsl:copy-of select="$lang/header"/>
        <xsl:choose>
          <xsl:when test="$param[@name='print']">
            <link rel="stylesheet" type="text/css" href="print.css" />
          </xsl:when>
          <xsl:otherwise>
            <xsl:if test="$slav">
             <style>
              <xsl:choose>
               <xsl:when test="$mode='mid_rus' or $mode='birchbark'">
                <xsl:text>
@font-face {
  font-family: "BukyVede";
  src: url('http://ruscorpora.ru/verstka/fonts/LDT55__W.eot');
  src: local('Ladoga Text RLI Web Regular'), local('LadogaTextRLIWebRegular'),
       url('http://ruscorpora.ru/verstka/fonts/LDT55__W.eot?#iefix') format('embedded-opentype'),
       url('http://ruscorpora.ru/verstka/fonts/LDT55__W.woff') format('woff'),
       url('http://ruscorpora.ru/verstka/fonts/LDT55__W.ttf') format('truetype'),
       url('http://ruscorpora.ru/verstka/fonts/LDT55__W.svg#LadogaTextRLIWeb-Regular') format('svg');
  font-weight: normal;
  font-style: normal;
}
                </xsl:text>
               </xsl:when>
               <xsl:otherwise>
                <xsl:text>
<!--
@font-face {
 font-family: BukyVede;
 src: local("BukyVede"),
      url("http://ruscorpora.ru/fonts/BukyVede-Regular.ttf");
}
 src: url("http://ruscorpora.ru/verstka/fonts/FlaviusNew.ttf")
 src: url("http://ruscorpora.ru/verstka/fonts/hirmosponomar9.ttf")
-->
@font-face {
 font-family: "BukyVede";
 src: url("http://ruscorpora.ru/verstka/fonts/Flavius2008.ttf")
}
                </xsl:text>
               </xsl:otherwise>
              </xsl:choose>
             </style>
            </xsl:if>
            <link rel="stylesheet" type="text/css" href="http://ruscorpora.ru/verstka/common.css" />
            <script type="text/javascript" src="http://ruscorpora.ru/verstka/jquery.js"></script>
            <script type="text/javascript" src="http://ruscorpora.ru/verstka/common.js"></script>
          </xsl:otherwise>
        </xsl:choose>
      </head>
      <body>
        <xsl:call-template name="metrika"/>

        <div class="hat">
          <div class="logo">
            <xsl:copy-of select="$lang/logo"/>
          </div>
        </div>
        <div class="line">
          <img alt="line under logo" src="http://ruscorpora.ru/verstka/i/bottom_logo.gif" width="169" height="9" />
          <br />
        </div>
        <xsl:apply-templates select="searchresult" />
        <div class="footer">
          <xsl:copy-of select="$lang/footer"/>
        </div>
      </body>
    </html>
  </xsl:template>


  <xsl:template match="searchresult">
    <div class="content">
      <h1 class="alt">
        <xsl:value-of select="$lang/corp_name" />
      </h1>
      <!-- Результаты поиска -->
      <xsl:choose>
        <xsl:when test="count(/page/searchresult/blocked) &gt; 0">
          <div style="padding-top:30px; padding-bottom:70px;">
            <h3>
             <xsl:value-of select="$lang/error/blocked" />
            </h3>
          </div>
        </xsl:when>
        <xsl:when test="not(/page/searchresult/body/result)">
          <div style="padding-top:30px; padding-bottom:70px;">
            <h3>
              <xsl:value-of select="$lang/error/unavailable" />.<br/><xsl:text> </xsl:text><xsl:value-of select="$lang/error/later" />.
            </h3>
          </div>
        </xsl:when>
        <xsl:when test="count(/page/searchresult/result/document) &gt;= 0">
          <div class="set">

            <xsl:if test="$param[@name='lang']">
              <a>
                <xsl:attribute name="href">
                  <xsl:value-of select="concat('/', $page-name, '?')" />
                  <xsl:apply-templates select="$param[@name != 'lang']"  mode="page-url"/>
                  <xsl:value-of select="concat('&amp;lang=', $lang/language/@href)" />
                </xsl:attribute>
                <xsl:value-of select="$lang/language" />
              </a>
            </xsl:if>

            <xsl:if test="$search-type = 'all-documents' or $search-type = 'snippets-titles' or $search-type = 'document'">
             <xsl:call-template name="kwic-link" />
            </xsl:if>

            <xsl:if test="$search-type != 'ngrams'">
              <a onclick="openSettings();" >
                <xsl:value-of select="$lang/settings" />
              </a>
            </xsl:if>
            <xsl:if test="not(key('param','simple')) or (key('param','simple') &lt; 1)">
              <xsl:choose>
                <xsl:when test="$param[@name = 'nodia'] = 1">
                  <a>
                    <xsl:attribute name="href">
                      <xsl:value-of select="concat('/', $page-name, '?')" />
                      <xsl:apply-templates select="$param[@name != 'nodia']"  mode="page-url"/>
                    </xsl:attribute>
                    <xsl:value-of select="$lang/accent_yes" />
                  </a>
                </xsl:when>
                <xsl:otherwise>
                  <a>
                    <xsl:attribute name="href">
                      <xsl:value-of select="concat('/', $page-name, '?nodia=1&amp;')" />
                      <xsl:apply-templates select="$param[@name != 'nodia']"  mode="page-url"/>
                    </xsl:attribute>
                    <xsl:value-of select="$lang/accent_no" />
                  </a>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:if>

            <!--<br clear="all"/>-->

            <xsl:if test="not(key('param','simple')) or (key('param','simple') &lt; 1)">
              <a href="{$choose_corpus_url}">
                <xsl:value-of select="$lang/choose_corp/name" />
              </a>
            </xsl:if>

            <xsl:if test="$param[@name='mycorp'] != '' or $param[@name='mysent'] != ''">
              <a onclick="cleanSubcorpus();">
                <xsl:attribute name="href">
                  <xsl:value-of select="concat('/', $page-name, '?')" />
                  <xsl:apply-templates select="$param[@name != 'mycorp'][@name != 'mysent'][@name != 'mysize'][@name != 'mysentsize']"  mode="page-url"/>
                </xsl:attribute>
                <xsl:value-of select="$lang/reset_corp" />
              </a>
            </xsl:if>

            <xsl:if test="not(key('param','simple')) or (key('param','simple') &lt; 2)">
              <a href="{$to_search}">
                <xsl:value-of select="$lang/to_search/name" />
              </a>
            </xsl:if>

            <xsl:if test="$lang/save_on_disk">
              <a onclick="saveOnDisk();">
                <xsl:value-of select="$lang/save_on_disk/button" />
              </a>
            </xsl:if>
          </div>

          <xsl:apply-templates select="/page/parameters/*[name() = $ln]" mode="form">
            <xsl:with-param name="sort" select="'1'" />
          </xsl:apply-templates>
          <xsl:apply-templates select="/page/searchresult/body/result[../request/query/@request!=''][@documents!='0']"/>
          <xsl:apply-templates select="/page/searchresult/body/request[query/@request='']" mode="zero_request" />
          <xsl:apply-templates select="/page/searchresult/body/result[../request/query/@request!=''][@documents='0']" mode="not_found"/>
        </xsl:when>
        <xsl:otherwise>
          <!--<xsl:apply-templates select="/page/searchresult/body/result"/>-->
        </xsl:otherwise>
      </xsl:choose>
    </div>
   </xsl:template>



  <xsl:template match="request" mode="zero_request" >
   <xsl:call-template name="h1" />
   <xsl:apply-templates select="/page/searchresult/body/request/query[count(word) &gt; 0]" mode="query"/>
   <p>
    <xsl:value-of select="$lang/error/empty" />
   </p>
  </xsl:template>


  <xsl:template name="corp-stat">
   <xsl:if test="/page/searchresult/body/result/corp-stat">
    <p class="res" style="clear: right;">
    <xsl:value-of select="$lang/corp-stat/corp-prefix" />
    <xsl:text>: </xsl:text>

    <xsl:call-template name="conj-documents">
     <xsl:with-param name="value" select="/page/searchresult/body/result/corp-stat/documents/@total" />
     <xsl:with-param name="mode" select="$mode" />
    </xsl:call-template>
    <xsl:text>, </xsl:text>

    <xsl:if test="/page/searchresult/body/result/corp-stat/sentences">
     <xsl:call-template name="conj-sentences">
      <xsl:with-param name="value" select="/page/searchresult/body/result/corp-stat/sentences/@total" />
     </xsl:call-template>
     <xsl:text>, </xsl:text>
    </xsl:if>

    <xsl:call-template name="conj-words">
     <xsl:with-param name="value" select="/page/searchresult/body/result/corp-stat/words/@total" />
    </xsl:call-template>
    <xsl:text>.</xsl:text>
    </p>
   </xsl:if>
  </xsl:template>


  <xsl:template name="subcorp-stat">
   <xsl:if test="$param[@name='mycorp'] != '' or $param[@name='mysent'] != ''">
    <p class="res" style="clear: right;">
     <xsl:value-of select="$lang/search/search_on" />
     <xsl:if test="$param[@name='mysize']">
      <xsl:text> </xsl:text>
      <xsl:value-of select="$lang/search/value" />
      <xsl:text> </xsl:text>

      <xsl:if test="$param[@name='mydocsize'] != ''">
       <xsl:call-template name="conj-documents">
        <xsl:with-param name="value" select="number($param[@name='mydocsize'])" />
        <xsl:with-param name="mode" select="$mode" />
       </xsl:call-template>
       <xsl:text>, </xsl:text>
      </xsl:if>

      <!--<xsl:call-template name="conj-sentences">
       <xsl:with-param name="value" select="number($param[@name='mysentsize'])" />
      </xsl:call-template>
      <xsl:text>, </xsl:text>-->

      <xsl:call-template name="conj-words">
       <xsl:with-param name="value" select="number($param[@name='mysize'])" />
      </xsl:call-template>
      <xsl:text>.</xsl:text>

     </xsl:if>
    </p>
   </xsl:if>
  </xsl:template>

  <xsl:template name="found-1-stat">
   <p class="found">
    <xsl:value-of select="$lang/result/found" />
    <xsl:text> </xsl:text>
    <xsl:value-of select="$lang/result/contexts" />
    <xsl:text>: </xsl:text>
    <xsl:value-of select="@contexts"/>
    <xsl:if test="@sentences != 0">
    <xsl:text>, </xsl:text>
    <xsl:value-of select="$lang/result/sentences" />:
    <xsl:value-of select="@sentences" />
    </xsl:if>
   </p>
  </xsl:template>



  <xsl:template match="result" mode="not_found" >
   <xsl:call-template name="h1" />
   <xsl:call-template name="subcorp-stat" />
   <xsl:apply-templates select="/page/searchresult/body/request/query[count(word) &gt; 0]" mode="query"/>
   <p>
    <xsl:value-of select="$lang/search/not_found" />.
   </p>
   <br />
   <xsl:if test="@search-type!='meta'">
    <xsl:call-template name="other-corpora"/>
   </xsl:if>
  </xsl:template>



  <xsl:template match="parameters/en | parameters/ru" mode="form" >
    <xsl:param name="sort" select="'0'" />

    <script>
      var settings = {
      dpp : <xsl:value-of select="/page/parameters/*[name() = $ln]/group[@name='per-page']/item[@value='dpp']/@def"/>,
      spd : <xsl:value-of select="/page/parameters/*[name() = $ln]/group[@name='per-page']/item[@value='spd']/@def"/>,
      spp : <xsl:value-of select="/page/parameters/*[name() = $ln]/group[@name='per-page']/item[@value='spp']/@def"/>,
      kwsz : <xsl:value-of select="/page/parameters/*[name() = $ln]/group[@name='per-page']/item[@value='kwsz']/@def"/>,
      mode : "<xsl:value-of select="$param[@name = 'mode']"/>",
      saveOnDiskMessage : "<xsl:value-of select="$lang/save_on_disk/message"/>"
      }
    </script>


    <div id="blocker">
      <br />
    </div>
    <div id="search-form">
      <a onclick="closeSettings ();" class="close">&nbsp;x&nbsp;</a>
      <form name="search_sort" method="get" action="{$page-name}">
        <xsl:if test="$sort = '1'">
          <xsl:apply-templates select="group[@name='sort']" mode="sort" />
        </xsl:if>
        <xsl:apply-templates select="group[@name='output']" mode="output" />
        <xsl:apply-templates select="group[@name='per-page']" mode="search" />
        <input type="hidden" id="seed" name="seed" value="" />

        <!-- передаем все текущие параметры, которые были, за исключением настроек (они передаются открыто) -->
        <xsl:for-each select="$param[@name != 'kwsz'][@name != 'dpp'][@name != 'spp'][@name != 'spd'][@name != 'sort'][@name != 'out'][@name != 'seed']">
          <input type="hidden" name="{@name}" value="{node()}" />
        </xsl:for-each>
        <input type="submit" value="{$lang/form/apply}" onclick="closeSettings();" />&nbsp;&nbsp;&nbsp;
        <input type="button" value="{$lang/form/reset}" onclick="setDefaults();" />
       </form>
    </div>


  </xsl:template>



  <xsl:template match="group" mode="sort">
    <p>
      <xsl:value-of select="$lang/form/sort" />:
    </p>
    <select id="settings-sort-select" name="{@name}" onchange="setRangesBySort(this.options[this.selectedIndex].value)">
      <xsl:for-each select="item">
        <option value="{@value}">
          <xsl:if test="key('param', ../@name) = @value">
            <xsl:attribute name="selected">true</xsl:attribute>
          </xsl:if>
          <xsl:value-of select="@name" />
        </option>
      </xsl:for-each>
    </select>
    <br />
    <br />
  </xsl:template>


  <xsl:template match="group" mode="search">
    <p>
      <xsl:value-of select="$lang/form/show" />:
    </p>
    <table class="settings" border="0">
      <xsl:for-each select="item">
        <tr>
          <td>
            <input id="settings-{@value}" name="{@value}" type="text" maxsize="4">
              <xsl:attribute name="value">
               <xsl:choose>
                <xsl:when test="@value='kwsz'">
                 <xsl:value-of select="$kwic-size" />
                </xsl:when>
                <xsl:otherwise>
                 <xsl:value-of select="$format/attribute::*[name()=current()/@format_name]" />
                </xsl:otherwise>
               </xsl:choose>
              </xsl:attribute>
            </input>
          </td>
          <td>
            <span id="settings-{@value}-caption"><xsl:value-of select="@name"/></span>
          </td>
        </tr>
      </xsl:for-each>
    </table>
    <br />
    <br />
  </xsl:template>

  <xsl:template name="kwic-link">
   <xsl:choose>
    <xsl:when test="$param[@name='out']='kwic'">
     <a>
      <xsl:attribute name="href">
       <xsl:value-of select="concat('/', $page-name, '?')" />
       <xsl:apply-templates select="$param[@name != 'out']" mode="page-url"/>
       <xsl:value-of select="'&amp;out=normal'" />
      </xsl:attribute>
      <xsl:value-of select="$lang/format/ordinary"/>
     </a>
    </xsl:when>
    <xsl:otherwise>
     <a>
      <xsl:attribute name="href">
       <xsl:value-of select="concat('/', $page-name, '?')" />
       <xsl:apply-templates select="$param[@name != 'out']" mode="page-url"/>
       <xsl:value-of select="'&amp;out=kwic'" />
      </xsl:attribute>
      <xsl:value-of select="$lang/format/kwic"/>
     </a>
    </xsl:otherwise>
   </xsl:choose>
  </xsl:template>


  <xsl:template match="group" mode="output">
    <p>
      <xsl:value-of select="$lang/form/output" />:
    </p>
    <select id="settings-output-select" name="{@value}" onchange="setRangesByOutput(this.options[this.selectedIndex].value)">
      <xsl:for-each select="item">
        <option value="{@value}">
          <xsl:if test="key('param', ../@value) = @value">
            <xsl:attribute name="selected">true</xsl:attribute>
          </xsl:if>
          <xsl:value-of select="@name" />
        </option>
      </xsl:for-each>
    </select>
    <br />
    <br />
  </xsl:template>



  <xsl:template name="other-corpora-link">
   <xsl:param name="corpus"/>
   <a href="javascript:void()">
    <xsl:attribute name="onclick">
     <xsl:text>go_to_the_other_corpus("</xsl:text>
     <xsl:value-of select="$corpus/@mode"/>
     <xsl:text>", "</xsl:text>
     <xsl:value-of select="concat('/', $corpus/@page, '?')" />
     <xsl:apply-templates select="$param[@name != 'accent' and @name!='mode' and @name!='p' and @name!='mycorp' and @name!='mysize' and @name!='mysent' and @name!='mysentsize']"  mode="page-url"/>
     <xsl:text>&amp;mode=</xsl:text><xsl:value-of select="$corpus/@mode"/>
     <xsl:choose>
      <xsl:when test="$corpus/@mode='accent' or $corpus/@mode='murco' or $corpus/@mode='school'">
       <xsl:text>&amp;accent=1</xsl:text>
      </xsl:when>
      <xsl:otherwise>
      </xsl:otherwise>
     </xsl:choose>
     <xsl:text>");</xsl:text>
    </xsl:attribute>
    <xsl:value-of select="$corpus/@gen"/>
   </a>
  </xsl:template>

  <xsl:template name="other-corpora">
    <xsl:value-of select="$lang/search-in-other-corpora/@name"/>
    <xsl:text> </xsl:text>
    <xsl:for-each select="$lang/corpora-list/corpus[@mode!=$mode]">
     <xsl:call-template name="other-corpora-link">
      <xsl:with-param name="corpus" select="."/>
     </xsl:call-template>
     <xsl:if test="position() != last()">
      <xsl:text>, </xsl:text>
     </xsl:if>
    </xsl:for-each>
    <xsl:text>.</xsl:text>
    <br/>
    <br/>
 </xsl:template>

 <xsl:template name="stat-links">
   <xsl:if test="$mode='main' or $mode='paper' or $mode='poetic'">
    <a target="_blank">
     <xsl:attribute name="href">
      <xsl:choose>
       <xsl:when test="$mode='main'">
        <xsl:text>plot.xml?smoothing=3&amp;stat=gr_created_&amp;</xsl:text>
       </xsl:when>
       <xsl:otherwise>
        <xsl:text>plot-</xsl:text><xsl:value-of select="$mode"/><xsl:text>.xml?smoothing=3&amp;stat=gr_created_&amp;</xsl:text>
       </xsl:otherwise>
      </xsl:choose>
      <xsl:apply-templates select="$param" mode="page-url" />
     </xsl:attribute>
     <xsl:value-of select="$lang/created-distribution"/></a>
     <xsl:text>&#160;&#160;&#160;</xsl:text>
   </xsl:if>
   <xsl:if test="$mode='main' or $mode='test'">
    <a target="_blank">
     <xsl:attribute name="href">
      <xsl:text>stat.xml?</xsl:text>
      <xsl:apply-templates select="$param" mode="page-url" />
     </xsl:attribute>
     <xsl:value-of select="$lang/metaattrs-stat"/></a>
    <br/>
    <br/>
   </xsl:if>
   <xsl:if test="$mode='paper' or $mode='poetic'">
    <br/>
    <br/>
   </xsl:if>
 </xsl:template>

  <xsl:template name="freq">
   <xsl:if test="1!=1 and not ($mode='syntax') and not ($mode='para')"> <!-- TODO: temporarily removed -->
    <xsl:value-of select="$lang/freq/prelink" />
    <xsl:text> </xsl:text>
    <a target="_blank">
     <xsl:attribute name="href">
      <xsl:text>/freq.xml?</xsl:text>
      <xsl:apply-templates select="$param[@name!='p']" mode="page-url"/>
      <xsl:text>&amp;p=0</xsl:text>
      <xsl:text>&amp;freq_diagram=3</xsl:text>
     </xsl:attribute>
     <xsl:value-of select="$lang/freq/link" />
    </a>
    <xsl:text>. </xsl:text>
   </xsl:if>
  </xsl:template>

  <xsl:template name="download-url">
   <xsl:apply-templates select="$param[@name!='dl'][@name!='out'][@name!='spp'][@name!='dpp'][@name!='spd'][@name!='p']" mode="page-url"/>
   <xsl:text>&amp;p=0</xsl:text>
   <xsl:text>&amp;dpp=1000</xsl:text>
   <xsl:text>&amp;spd=10</xsl:text>
   <xsl:text>&amp;spp=1000</xsl:text>
   <xsl:text>&amp;out=kwic</xsl:text>
  </xsl:template>

  <xsl:template name="download-excel">
    <xsl:variable name="infix">
     <xsl:if test="$mode = 'syntax'">
      <xsl:text>-syntax</xsl:text>
     </xsl:if>
    </xsl:variable>
    <xsl:value-of select="$lang/download" />
    <xsl:text> </xsl:text>
    <a>
     <xsl:attribute name="href">
      <xsl:text>/download</xsl:text>
      <xsl:value-of select="$infix" />
      <xsl:text>-excel.xml?</xsl:text>
      <xsl:call-template name="download-url" />
      <xsl:text>&amp;dl=excel</xsl:text>
     </xsl:attribute>
     <xsl:attribute name="onclick">
      <xsl:text>yaCounter2226223.reachGoal('TARGET_Excel'); return true;</xsl:text>
     </xsl:attribute>
     <xsl:text>Excel</xsl:text>
    </a>,
    <a>
     <xsl:attribute name="href">
      <xsl:text>/download</xsl:text>
      <xsl:value-of select="$infix" />
      <xsl:text>-calc.xml?</xsl:text>
      <xsl:call-template name="download-url" />
      <xsl:text>&amp;dl=calc</xsl:text>
     </xsl:attribute>
     <xsl:attribute name="onclick">
      <xsl:text>yaCounter2226223.reachGoal('TARGET_Calc'); return true;</xsl:text>
     </xsl:attribute>
     <xsl:text>OpenOffice Calc</xsl:text>
    </a>,
    <a>
     <xsl:attribute name="href">
      <xsl:text>/download</xsl:text>
      <xsl:value-of select="$infix" />
      <xsl:text>-xml.xml?</xsl:text>
      <xsl:call-template name="download-url" />
      <xsl:text>&amp;dl=xml</xsl:text>
     </xsl:attribute>
     <xsl:attribute name="onclick">
      <xsl:text>yaCounter2226223.reachGoal('TARGET_XML'); return true;</xsl:text>
     </xsl:attribute>
     <xsl:text>XML</xsl:text>
    </a>
    <xsl:text>. </xsl:text>
  </xsl:template>


  <xsl:template match="result">
    <xsl:choose>
      <xsl:when test="@search-type='ngrams'">
        <xsl:call-template name="h1" />

        <!--<xsl:call-template name="corp-stat" />
        <xsl:call-template name="subcorp-stat" />-->

        <xsl:apply-templates select="/page/searchresult/body/request/query[count(word) &gt; 0]" mode="query"/>

        <!--<p class="found">
         <xsl:value-of select="$lang/result/found" />
         <xsl:text> </xsl:text>
           <xsl:if test="@sentences != 0">
            <xsl:text>, </xsl:text>
            <xsl:call-template name="conj-sentences">
             <xsl:with-param name="value" select="@sentences" />
            </xsl:call-template>
           </xsl:if>
         <xsl:text>.</xsl:text>
        </p>-->

        <!--<p class="pager">
         <xsl:call-template name="pager">
          <xsl:with-param name="p_name" select="'p'"/>
          <xsl:with-param name="last-number" select="/page/searchresult/body/result/@documents div $format/@snippets-per-page" />
         </xsl:call-template>
        </p>-->

        <table border="1" cellpadding="5" cellspacing="0" width="100%">
         <tr>
          <th>№</th>
          <th>Вхождения</th>
          <th>Документы</th>
          <th align="left">Фрагмент</th>
         </tr>
         <xsl:for-each select="document/snippet">
          <tr>
           <td align="right">
            <xsl:value-of select="position()"/>
           </td>
           <td align="right">
            <xsl:value-of select="../attributes/attr[@name='freq']/@value" />
           </td>
           <td align="right">
            <xsl:value-of select="../attributes/attr[@name='docs']/@value" />
           </td>
           <td width="100%">
            <xsl:apply-templates select="word | text" />
           </td>
          </tr>
         </xsl:for-each>
        </table>

        <!--<p class="pager">
         <xsl:call-template name="pager">
          <xsl:with-param name="p_name" select="'p'"/>
          <xsl:with-param name="last-number" select="/page/searchresult/body/result/@documents div $format/@snippets-per-page" />
         </xsl:call-template>
        </p>-->

        <br/>

      </xsl:when>

      <xsl:when test="@search-type='meta'">
        <xsl:call-template name="h1" />
        <xsl:call-template name="corp-stat" />

        <xsl:apply-templates select="/page/searchresult/body/request/query[count(word) &gt; 0]" mode="query"/>

        <p class="found">
         <xsl:value-of select="$lang/result/found" />
         <xsl:text> </xsl:text>
         <xsl:call-template name="conj-documents">
          <xsl:with-param name="value" select="@documents" />
          <xsl:with-param name="mode" select="$mode" />
         </xsl:call-template>
         <xsl:if test="/page/searchresult/body/result/subcorp-stat">
          <xsl:text> </xsl:text>
          <xsl:value-of select="$lang/result/total-amount" />
          <xsl:text> </xsl:text>
          <!-- <xsl:call-template name="conj-sentences">
           <xsl:with-param name="value" select="/page/searchresult/body/result/subcorp-stat/sentences/@total" />
          </xsl:call-template>
          <xsl:text>, </xsl:text>-->
          <xsl:call-template name="conj-words">
           <xsl:with-param name="value" select="/page/searchresult/body/result/subcorp-stat/words/@total" />
          </xsl:call-template>
          <xsl:text>.</xsl:text>
         </xsl:if>
        </p>

        <!--<xsl:call-template name="stat-links"/>-->

        <xsl:call-template name="save-results"/>

        <p class="pager">
         <xsl:call-template name="pager">
          <xsl:with-param name="p_name" select="'p'"/>
          <xsl:with-param name="last-number" select="/page/searchresult/body/result/@documents div $format/@documents-per-page" />
         </xsl:call-template>
        </p>

        <ol start="{/page/searchresult/body/request/@page * $format/@documents-per-page + 1}">
         <xsl:apply-templates select="document" />
        </ol>

        <p class="pager">
         <xsl:call-template name="pager">
          <xsl:with-param name="p_name" select="'p'"/>
          <xsl:with-param name="last-number" select="/page/searchresult/body/result/@documents div $format/@documents-per-page" />
         </xsl:call-template>
        </p>

        <xsl:call-template name="save-results"/>

        <p>
         <xsl:call-template name="freq" />
        </p>

      </xsl:when>


      <xsl:when test="@search-type='all-documents'">
        <xsl:call-template name="h1" />

        <xsl:call-template name="corp-stat" />
        <xsl:call-template name="subcorp-stat" />

        <xsl:apply-templates select="/page/searchresult/body/request/query[count(word) &gt; 0]" mode="query"/>

        <p class="found">
         <xsl:value-of select="$lang/result/found" />
         <xsl:text> </xsl:text>
         <xsl:choose>
          <xsl:when test="$param[@name='out']='kwic'">
           <xsl:call-template name="conj-contexts">
            <xsl:with-param name="value" select="@contexts" />
           </xsl:call-template>
          </xsl:when>
          <xsl:otherwise>
           <xsl:call-template name="conj-documents">
            <xsl:with-param name="value" select="@documents" />
             <xsl:with-param name="mode" select="$mode" />
           </xsl:call-template>
           <xsl:if test="@sentences != 0">
            <xsl:text>, </xsl:text>
            <xsl:call-template name="conj-sentences">
             <xsl:with-param name="value" select="@sentences" />
            </xsl:call-template>
           </xsl:if>
           <xsl:if test="@contexts != 0 and ($mode!='murco' or count(/page/searchresult/body/request/query/word) &gt; 0)">
            <xsl:text>, </xsl:text>
            <xsl:call-template name="conj-contexts">
             <xsl:with-param name="value" select="@contexts" />
            </xsl:call-template>
           </xsl:if>
          </xsl:otherwise>
         </xsl:choose>
         <xsl:text>.</xsl:text>
        </p>

        <xsl:call-template name="stat-links" />

        <xsl:call-template name="other-corpora"/>

        <p class="pager">
         <xsl:call-template name="pager">
          <xsl:with-param name="p_name" select="'p'"/>
          <xsl:with-param name="last-number" select="/page/searchresult/body/result/@documents div $format/@documents-per-page" />
         </xsl:call-template>
        </p>

        <xsl:if test="$param[@name='out']='kwic'">
         <xsl:text disable-output-escaping="yes">
          &lt;table align="left" width="100%" border="0" cellpadding="0" cellspacing="0"&gt;
         </xsl:text>
        </xsl:if>


        <xsl:choose>
         <xsl:when test="$mode='multiparc' or $mode='multiparc_rus'">
          <hr/>

          <!--<ol start="{/page/searchresult/body/request/@page * $format/@documents-per-page + 1}">-->
          <ol type="A">

          <xsl:for-each select="document[not(attributes/attr[@name='gr_linked_fragments']/@value=preceding-sibling::document/attributes/attr[@name='gr_linked_fragments']/@value)]">
           <xsl:variable name="fragment" select="attributes/attr[@name='gr_linked_fragments']/@value"/>
            <li><ol>
             <xsl:for-each select="../document[attributes/attr[@name='gr_linked_fragments']/@value=$fragment]">
              <xsl:sort select="attributes/attr[@name='created']/@value"/>
              <xsl:apply-templates select="." />
             </xsl:for-each>
            </ol></li>
           <hr/>
           <br clear="all"/>
          </xsl:for-each>
          </ol>

        </xsl:when>
         <xsl:otherwise>
          <ol start="{/page/searchresult/body/request/@page * $format/@documents-per-page + 1}">
           <xsl:apply-templates select="document" />
          </ol>
         </xsl:otherwise>
        </xsl:choose>

        <xsl:if test="$param[@name='out']='kwic'">
         <xsl:text disable-output-escaping="yes">
          &lt;/table&gt;
         </xsl:text>
         &nbsp;<br/>
        </xsl:if>

        <p class="pager">
         <xsl:call-template name="pager">
          <xsl:with-param name="p_name" select="'p'"/>
          <xsl:with-param name="last-number" select="/page/searchresult/body/result/@documents div $format/@documents-per-page" />
         </xsl:call-template>
        </p>

        <xsl:call-template name="other-corpora"/>
        <p>
         <xsl:call-template name="download-excel" />
         <br />
         <xsl:call-template name="freq" />
        </p>

        <xsl:if test="not($hide_freq_list) and page-stat and (count(/page/searchresult/body/request/query/word) = 1)">
         <h4><xsl:value-of select="$lang/freq/page-stat-title" /></h4>
         <xsl:apply-templates select="page-stat" />
         <br clear="all" />
         <br />
        </xsl:if>

      </xsl:when>


      <xsl:when test="@search-type='document'">
       <xsl:call-template name="h1-url" />

       <xsl:apply-templates select="/page/searchresult/body/request/query[count(word) &gt; 0]" mode="query"/>

       <p class="found">
        <xsl:if test="@sentences != 0">
         <xsl:call-template name="conj-sentences">
          <xsl:with-param name="value" select="@sentences" />
         </xsl:call-template>
         <xsl:text>, </xsl:text>
        </xsl:if>
        <xsl:value-of select="$lang/result/found" />
        <xsl:text> </xsl:text>
        <xsl:call-template name="conj-contexts">
         <xsl:with-param name="value" select="@contexts" />
        </xsl:call-template>
       </p>

       <p class="pager">
        <xsl:call-template name="pager">
         <xsl:with-param name="p_name" select="'ps'"/>
         <xsl:with-param name="last-number" select="/page/searchresult/body/result/document/@snippets div $format/@snippets-per-page" />
        </xsl:call-template>
       </p>

       <xsl:if test="$param[@name='out']='kwic'">
        <xsl:text disable-output-escaping="yes">
         &lt;table align="left" width="100%" border="0" cellpadding="0" cellspacing="0"&gt;
        </xsl:text>
       </xsl:if>

       <ol>
        <xsl:apply-templates select="document"/>
       </ol>

       <xsl:if test="$param[@name='out']='kwic'">
        <xsl:text disable-output-escaping="yes">
         &lt;/table&gt;
        </xsl:text>
        &nbsp;<br/>
       </xsl:if>

       <p class="pager">
        <xsl:call-template name="pager">
         <xsl:with-param name="p_name" select="'ps'" />
         <xsl:with-param name="last-number" select="/page/searchresult/body/result/document/@snippets div $format/@snippets-per-page" />
        </xsl:call-template>
       </p>
      </xsl:when>

      <xsl:when test="@search-type='snippet'">
       <xsl:call-template name="h1-url" />

       <xsl:apply-templates select="/page/searchresult/body/request/query[count(word) &gt; 0]" mode="query"/>

       <span class="snippet-title">
        <span class="b-doc-expl" explain="{document/@id}">
         <xsl:value-of select="document/@title" disable-output-escaping="yes" />
        </span>
       </span>

       <xsl:choose>
        <xsl:when test="document/attributes/attr[@name='video_id'] and document/attributes/attr[@name='video_id']/@value!='null'">
          <!-- murco case -->
          <table class="murco-table" width="100%"><tr valign="top">
           <td valign="top">
           <xsl:variable name="video-name" select="str:split(document/attributes/attr[@name='path']/@value, '/')[last()]" />
           <xsl:for-each select="document/attributes/attr[@name='video_id']">
            <xsl:call-template name="video">
             <xsl:with-param name="id" select="@value" />
             <xsl:with-param name="name" select="$video-name" />
            </xsl:call-template>
           </xsl:for-each>
           <table><tr>
            <td><a>
             <xsl:attribute name="href">
              <xsl:value-of select="concat('/', $page-name, '?')" />
              <xsl:apply-templates select="$param[@name!='docid'][@name!='sid']" mode="page-url"/>
              <xsl:text>&amp;docid=</xsl:text>
              <xsl:value-of select="$param[@name='docid'] - 1" />
              <xsl:text>&amp;sid=0</xsl:text>
              </xsl:attribute>
             <xsl:value-of select="$lang/prev_fragment" />
            </a></td>
            <td align="right"><a>
             <xsl:attribute name="href">
              <xsl:value-of select="concat('/', $page-name, '?')" />
              <xsl:apply-templates select="$param[@name!='docid'][@name!='sid']" mode="page-url"/>
              <xsl:text>&amp;docid=</xsl:text>
              <xsl:value-of select="$param[@name='docid'] + 1" />
              <xsl:text>&amp;sid=0</xsl:text>
             </xsl:attribute>
             <xsl:value-of select="$lang/next_fragment" />
            </a></td>
            </tr></table>
           </td>
           <td valign="top" align="left">
            <!--<ul class="murco-snippet">-->
             <xsl:apply-templates select="document/*" />
            <!--</ul>-->
           </td>
          </tr></table>
         </xsl:when>
         <xsl:otherwise>
          <p><ul><li>
           <xsl:apply-templates select="document/*" />
          </li></ul></p>
         </xsl:otherwise>
       </xsl:choose>

      </xsl:when>

      <xsl:when test="@search-type='snippets-titles'">
        <xsl:call-template name="h1-url" />

        <xsl:call-template name="corp-stat" />
        <xsl:call-template name="subcorp-stat" />

        <xsl:apply-templates select="/page/searchresult/body/request/query[count(word) &gt; 0]" mode="query" />

        <xsl:call-template name="other-corpora" />

        <p class="found">
          <xsl:value-of select="$lang/result/sorted" /><xsl:text> </xsl:text>
          <xsl:call-template name="conj-sentences">
           <xsl:with-param name="value" select="@sentences" />
          </xsl:call-template>
          <xsl:text>. </xsl:text>
          <xsl:value-of select="$lang/result/found" /><xsl:text> </xsl:text>
          <xsl:call-template name="conj-contexts">
           <xsl:with-param name="value" select="@contexts" />
          </xsl:call-template>
          <xsl:text>. </xsl:text>
        </p>

        <p class="pager">
         <xsl:call-template name="pager">
          <xsl:with-param name="p_name" select="'p'" />
          <xsl:with-param name="last-number" select="/page/searchresult/body/result/@sentences div $format/@snippets-per-page" />
         </xsl:call-template>
        </p>

        <xsl:if test="$param[@name='out']='kwic'">
         <xsl:text disable-output-escaping="yes">
          &lt;table align="left" width="100%" border="0" cellpadding="0" cellspacing="0"&gt;
         </xsl:text>
        </xsl:if>

        <ul>
         <xsl:apply-templates select="document/snippet" mode="snippets-list"/>
        </ul>

        <xsl:if test="$param[@name='out']='kwic'">
         <xsl:text disable-output-escaping="yes">
          &lt;/table&gt;
         </xsl:text>
         &nbsp;<br/>
        </xsl:if>

        <br />
        <p class="pager">
          <xsl:call-template name="pager" >
            <xsl:with-param name="p_name" select="'p'" />
            <xsl:with-param name="last-number" select="/page/searchresult/body/result/@sentences div $format/@snippets-per-page" />
          </xsl:call-template>
        </p>

        <xsl:call-template name="other-corpora"/>

        <p>
         <xsl:call-template name="download-excel" />
         <br />
         <xsl:call-template name="freq" />
        </p>

      </xsl:when>

      <xsl:when test="@search-type = 'concordance'">
        <xsl:call-template name="h1" />

        <xsl:call-template name="subcorp-stat" />

        <xsl:apply-templates select="/page/searchresult/body/request/query[count(word) &gt; 0]" mode="query"/>

        <p class="found">
          <xsl:value-of select="$lang/result/found" />
          <xsl:text> </xsl:text>
          <xsl:value-of select="$lang/result/contexts" />
          <xsl:text>: </xsl:text>
          <xsl:value-of select="@sentences" />
        </p>

        <p class="pager">
          <xsl:call-template name="pager" >
            <xsl:with-param name="p_name" select="'p'"/>
            <xsl:with-param name="last-number" select="/page/searchresult/body/result/@sentences div $format/@snippets-per-page" />
          </xsl:call-template>
        </p>


        <table cellspacing="0" cellpadding="0" border="0" class="concor">
          <tr>
            <th class="n">Форма / лемма</th>
            <th>Частота</th>
            <xsl:if test="$param[@name = 'type'] = 'lex'">
              <th class="nl">Примеры</th>
            </xsl:if>
          </tr>
          <xsl:apply-templates mode="concordance"/>
        </table>

        <br />
        <p class="pager">
          <xsl:call-template name="pager" >
            <xsl:with-param name="p_name" select="'p'"/>
            <xsl:with-param name="last-number" select="/page/searchresult/body/result/@sentences div $format/@snippets-per-page" />
          </xsl:call-template>
        </p>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="word" mode="concordance">
    <tr>
      <td class="n">
        <a>
          <xsl:attribute name="href">
            <xsl:value-of select="@url"/>
          </xsl:attribute>
          <xsl:value-of select="@name"/>
        </a>
      </td>
      <td>
        <xsl:if test="@forms=''">
          <xsl:attribute name="colspan">2</xsl:attribute>
        </xsl:if>
        <xsl:value-of select="@freq"/>
      </td>

      <xsl:if test="@forms!=''">
        <td class="nl">
          <xsl:value-of select="@forms"/>
        </td>
      </xsl:if>
    </tr>
  </xsl:template>

  <xsl:template match="query" mode="query">
    <xsl:if test="@request!=''">
      <p class="res">
        <xsl:apply-templates select="word" mode="query" />
      </p>
    </xsl:if>
  </xsl:template>

  <xsl:template match="word" mode="query">
    <xsl:if test="$param[@name='out']='kwic' and $param[@name='mode'] != 'syntax' and (count(../word) > 1)">
      <input type="radio">
        <xsl:if test="$kwic-word-pos = position() - 1">
         <xsl:attribute name="checked">
          <xsl:text>checked</xsl:text>
         </xsl:attribute>
        </xsl:if>
        <xsl:attribute name="onclick">
         <xsl:text>window.location="</xsl:text>
         <xsl:value-of select="concat('/', $page-name, '?')" />
         <xsl:apply-templates select="$param[@name != 'kwpos']" mode="page-url"/>
         <xsl:text>&amp;kwpos=</xsl:text>
         <xsl:value-of select="position() - 1" />
         <xsl:text>";</xsl:text>
        </xsl:attribute>
      </input>
      &nbsp;
    </xsl:if>
    <xsl:call-template name="clone">
      <xsl:with-param name="val" select="@*[name(.)= 'level']"/>
    </xsl:call-template>
    <xsl:apply-templates select="@*[name(.)= 'distance-min']" mode="dist" />
    <xsl:apply-templates select="@*[name(.)= 'distance-max']" mode="dist" />
    <xsl:if test="not(@lex) and not(@gramm) and not(@sem) and not(@flags)">
      <xsl:choose>
        <xsl:when test="not(@distance-min) and not(@distance-max)">
          <xsl:value-of select="$lang/query/any_alone"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$lang/query/any_dist"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>

    <xsl:apply-templates select="@lex" mode="query" />
    <xsl:apply-templates select="@*[name(.)!= 'level'][name(.)!= 'lex'][name(.)!= 'distance-min'][name(.)!= 'distance-max'][name(.)!= 'link']" mode="gr" />
    <xsl:apply-templates select="@link" mode="link" />

   <br />
  </xsl:template>

  <xsl:template name="clone">
    <xsl:param name="val"/>
    <xsl:if test="$val > 0">
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
      <xsl:call-template name="clone">
        <xsl:with-param name="val" select="$val - 1"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <xsl:template match="@lex" mode="query">
    <xsl:if test="current() != ''">
      <b><!-- -->
        <xsl:value-of disable-output-escaping="no" select="."/>
      </b>&nbsp;
    </xsl:if>
  </xsl:template>

  <xsl:template match="@link" mode="link">
    <xsl:if test="current() != ''">
      <xsl:text> </xsl:text><xsl:value-of select="$lang/query/connection"/><xsl:text> </xsl:text><b>
        <!-- -->
        <xsl:value-of disable-output-escaping="no" select="."/>
      </b>&nbsp;
    </xsl:if>
  </xsl:template>


  <xsl:template match="@*" mode="dist" >
    <xsl:choose>
      <xsl:when test="(name(.) = 'distance-min') and current() = ../@distance-max">
        <xsl:value-of select="$lang/query/distance"/>
        <xsl:text> </xsl:text>
        <b>
          <xsl:value-of select="." />
        </b>
        <xsl:text> </xsl:text>
        <xsl:value-of select="$lang/query/from"/>
        <xsl:text> </xsl:text>
      </xsl:when>
      <xsl:when test="(name(.) = 'distance-min') and current() != ../@distance-max">
        <xsl:value-of select="$lang/query/distance"/>
        <xsl:text> </xsl:text>
        <xsl:value-of select="$lang/query/from"/>
        <xsl:text> </xsl:text>
        <b>
          <xsl:value-of select="." />
        </b>
        <xsl:text> </xsl:text>
      </xsl:when>
      <xsl:when test="(name(.) = 'distance-max') and current() != ../@distance-min">
        <xsl:value-of select="$lang/query/to"/>
        <xsl:text> </xsl:text>
        <b>
          <xsl:value-of select="." />
        </b>
        <xsl:text> </xsl:text>
        <xsl:value-of select="$lang/query/from"/>
        <xsl:text> </xsl:text>
      </xsl:when>
      <xsl:when test="(name(.) = 'distance-min') and not(../@distance-max)">
        <xsl:value-of select="$lang/query/distance"/>
        <xsl:text> </xsl:text>
        <xsl:value-of select="$lang/query/from"/>
        <xsl:text> </xsl:text>
        <b>
          <xsl:value-of select="." />
        </b>
        <xsl:text> </xsl:text>
        <xsl:value-of select="$lang/query/from"/>
        <xsl:text> </xsl:text>
      </xsl:when>
      <xsl:when test="(name(.) = 'distance-max') and not(../@distance-min)">
        <xsl:value-of select="$lang/query/distance"/>
        <xsl:text> </xsl:text>
        <xsl:value-of select="$lang/query/to"/>
        <xsl:text> </xsl:text>
        <b>
          <xsl:value-of select="." />
        </b>
        <xsl:text> </xsl:text>
        <xsl:value-of select="$lang/query/from"/>
        <xsl:text> </xsl:text>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="@*" mode="gr" >
    <xsl:if test="current() != ''">
      <b>
        <xsl:value-of select="." />
      </b>&nbsp; <xsl:text> </xsl:text>
    </xsl:if>
  </xsl:template>

  <xsl:template name="pager">
    <xsl:param name="p_name" />
    <xsl:param name="last-number" />
    <xsl:value-of select="$lang/pages" />:
    <xsl:if test="$curpage &gt; 1">
      <a>
        <xsl:attribute name="href">
          <xsl:value-of select="concat('/', $page-name, '?')" />
          <xsl:apply-templates select="$param[@name!=$p_name]"  mode="page-url"/>
          <xsl:value-of select="concat('&amp;', $p_name, '=', ($param[@name=$p_name] -1))" />
        </xsl:attribute>
        <xsl:value-of select="$lang/prev_page" />
      </a>
      <xsl:text> </xsl:text>
    </xsl:if>
    <xsl:call-template name="draw-number">
      <xsl:with-param name="number-to-draw" select="number($curpage)-10"/>
      <xsl:with-param name="last-number" select="$last-number"/>
      <xsl:with-param name="selected-number" select="$curpage"/>
      <xsl:with-param name="p_name" select="$p_name"/>
    </xsl:call-template>

    <xsl:if test="$curpage &lt; $last-number">
      <xsl:text> </xsl:text>
      <a>
        <xsl:attribute name="href">
          <xsl:value-of select="concat('/', $page-name, '?')" />
          <xsl:apply-templates select="$param[@name!=$p_name]"  mode="page-url"/>
          <xsl:choose>
            <xsl:when test="$param[@name=$p_name] != ''">
              <xsl:value-of select="concat('&amp;', $p_name, '=', ($param[@name=$p_name] + 1))" />
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="concat('&amp;', $p_name, '=1')" />
            </xsl:otherwise>
          </xsl:choose>
        </xsl:attribute>
        <xsl:value-of select="$lang/next_page" />
      </a>
    </xsl:if>
  </xsl:template>

  <xsl:template match="param" mode="page-url">
    <xsl:value-of select="concat(@name, '=', node())" />
    <xsl:if test="position() != last()">&amp;</xsl:if>
  </xsl:template>

  <xsl:template match="param">
    <xsl:value-of select="concat(@name, '=', node())" />
    <xsl:if test="position() != last()">&amp;</xsl:if>
  </xsl:template>


 <xsl:template match="document">
  <xsl:choose>
   <xsl:when test="$param[@name='out']='kwic'">
    <xsl:for-each select="snippet">
     <xsl:call-template name="kwic" />
    </xsl:for-each>
    <xsl:for-each select="para/snippet">
     <xsl:call-template name="kwic" />
    </xsl:for-each>
   </xsl:when>
  <xsl:otherwise>
    <li>
      <xsl:if test="not(key('param', 'notitle'))">
        <span class="b-doc-expl" explain="{@id}">
          <xsl:value-of select="@title" disable-output-escaping="yes" />
        </span>
        <xsl:text>&nbsp;&nbsp;</xsl:text>
      </xsl:if>
      <xsl:apply-templates select="." mode="omo"/>
      <xsl:text> </xsl:text>
      <xsl:if test="../@search-type = 'meta' and ($mode='poetic' or $mode='birchbark' or $mode='dialect')">
       &nbsp;<a class="b-kwic-expl">
        <xsl:attribute name="href">
         <xsl:value-of select="concat($page-name, '?')" />
         <xsl:apply-templates select="$param[@name='env' or @name='mode']"  mode="page-url"/>
         <xsl:value-of select="concat('&amp;nodia=1&amp;expand=full', '&amp;docid=', @id, '&amp;sid=0')"/>
        </xsl:attribute>&larr;&hellip;&rarr;
       </a>
      </xsl:if>
      <xsl:if test="../@search-type != 'meta'">
        <xsl:if test="not(key('param','nolinks'))">
          <a>
            <xsl:attribute name="href">
              <xsl:value-of select="concat($page-name, '?')" />
              <xsl:for-each select="/page/state/param">
               <xsl:choose>
                <xsl:when test="$mode='old_rus'">
                 <xsl:value-of select="concat(@name, '=', node(), '&amp;')" />
                </xsl:when>
                <xsl:otherwise>
                 <xsl:value-of select="concat(@name, '=', node(), '&amp;')" />
                </xsl:otherwise>
               </xsl:choose>
              </xsl:for-each>
              <xsl:value-of select="concat('docid=', @id)" />
            </xsl:attribute><xsl:value-of select="$lang/all_contexts" /> (<xsl:value-of select="@snippets" />)
          </a>
        </xsl:if>
        <xsl:choose>
         <xsl:when test="attributes/attr[@name='video_id'] and attributes/attr[@name='video_id']/@value!='null'">
          <table class="murco-table" width="100%"><tr>
           <td valign="top">
           <xsl:variable name="video-name" select="str:split(attributes/attr[@name='path']/@value, '/')[last()]" />
           <xsl:for-each select="attributes/attr[@name='video_id']">
            <xsl:call-template name="video">
             <xsl:with-param name="id" select="@value" />
             <xsl:with-param name="name" select="$video-name" />
           </xsl:call-template>
           </xsl:for-each>
           </td>
           <td valign="top">
           <ul>
            <xsl:apply-templates select="*"/>
           </ul>
           </td>
           </tr>
          </table>
          <br/>
         </xsl:when>
         <xsl:otherwise>
          <table width="100%" cellspacing="10"><tr><td width="100%">
           <ul>
            <xsl:apply-templates select="*"/>
           </ul>
          </td></tr></table>
         </xsl:otherwise>
        </xsl:choose>
      </xsl:if>
    </li>
   </xsl:otherwise>
  </xsl:choose>
  </xsl:template>


  <xsl:template name="video">
    <xsl:param name="id"/>
    <xsl:param name="name"/>
    <xsl:variable name="new_name" select="str:split($name, '.')[1]" />
    <iframe width="320" height="240" src="http://video.yandex.ru/iframe/ruscorpora-video/{$id}/" frameborder="0" allowfullscreen="1"></iframe>
    <!--
    <object>
      <param name="video" value="http://streaming.video.yandex.ru/custom/ruscorpora-video/{$id}/"/>
      <param name="allowFullScreen" value="true"/>
      <param name="allowScriptAccess" value="always"/>
      <param name="width" value="320"/>
      <param name="height" value="240"/>
      <param name="scale" value="noscale"/>
      <param name="wmode" value="opaque"/>
      <embed
       src="http://streaming.video.yandex.ru/custom/ruscorpora-video/{$id}/"
       type="application/x-shockwave-flash"
       allowFullScreen="true"
       allowScriptAccess="always"
       width="320"
       height="240"
       scale="noscale"
       wmode="opaque"
      > </embed>
    </object>
    -->
    <table><tr><td><a href="/video.xml?id={$id}&amp;name={$new_name}.mp4" download="{$new_name}.mp4">Скачать</a></td></tr></table>
  </xsl:template>

  <xsl:template match="gesture">
     <tr>
      <td class="gesture"><xsl:value-of select="@actorname"/></td>
      <td class="gesture"><xsl:value-of select="@actorsex"/></td>
      <td class="gesture"><xsl:value-of select="@mainorgan"/></td>
      <td class="gesture"><xsl:value-of select="@gesturename"/></td>
      <td class="gesture"><xsl:value-of select="@gesturemeaning"/></td>
     </tr>
  </xsl:template>

  <xsl:template match="gestures">
    <xsl:if test="count(gesture) > 0">
      <br />
      <span class="gestures-caption">Жесты:</span><br />
      <table class="gestures-table" cellspacing="0" width="100%">
        <tr>
          <td class="gestures-th">Имя</td>
          <td class="gestures-th">Пол</td>
          <td class="gestures-th">Активный орган</td>
          <td class="gestures-th">Название жеста</td>
          <td class="gestures-th">Значение жеста</td>
        </tr>
        <xsl:for-each select="gesture">
          <xsl:apply-templates select="." />
        </xsl:for-each>
      </table>
      <br />
    </xsl:if>
  </xsl:template>

  <xsl:template name="save-results">
   <xsl:if test="$mode != 'birchbark'">
   <p>
    <input type="button" onclick="saveResults();">
      <xsl:attribute name="value">
        <xsl:value-of select="$lang/choose_corp/save_and_go" />
      </xsl:attribute>
    </input>
   </p>
   <script type="text/javascript">
      <xsl:variable name="request-document">
        <xsl:value-of select="/page/searchresult/body/request/query/@document" />
      </xsl:variable>
      <xsl:variable name="request-sentence">
        <xsl:value-of select="/page/searchresult/body/request/query/@sentence" />
      </xsl:variable>
      <xsl:variable name="subcorpus-size">
        <xsl:value-of select="/page/searchresult/body/result/subcorp-stat/words/@total" />
      </xsl:variable>
      <xsl:variable name="subcorpus-sentsize">
        <xsl:value-of select="/page/searchresult/body/result/subcorp-stat/sentences/@total" />
      </xsl:variable>
      <xsl:variable name="subcorpus-docsize">
        <xsl:value-of select="/page/searchresult/body/result/subcorp-stat/documents/@total" />
      </xsl:variable>

     function saveResults() {
      var mycorp = "<xsl:value-of select="$request-document"/>";
      var mysent = "<xsl:value-of select="$request-sentence"/>";
      var mysize = "<xsl:value-of select="$subcorpus-size"/>";
      var mysentsize= "<xsl:value-of select="$subcorpus-sentsize"/>";
      var mydocsize= "<xsl:value-of select="$subcorpus-docsize"/>";
      document.cookie = "<xsl:value-of select="$param[@name = 'mode']"/>=" + mycorp + "&amp;" + mysent + "&amp;" + mysize + "&amp;" + mysentsize + "&amp;" + mydocsize + "&amp;" + "; domain=ruscorpora.ru";
      window.location = "<xsl:value-of select="$to_search"/>";
     }
   </script>
   </xsl:if>
  </xsl:template>

  <xsl:template match="*" mode="omo">
    <xsl:if test="not(key('param','notag')) or (key('param','notag') != 1)">
      <span>
        <xsl:choose>
          <xsl:when test="@tagging='manual'">
            <xsl:attribute name="class">on</xsl:attribute>
            <xsl:text> [</xsl:text>
            <xsl:value-of select="$lang/omo_off" />
            <xsl:text>] </xsl:text>
          </xsl:when>
          <xsl:otherwise>
            <xsl:attribute name="class">off</xsl:attribute>
            <xsl:text> [</xsl:text>
            <xsl:value-of select="$lang/omo_on" />
            <xsl:text>] </xsl:text>
          </xsl:otherwise>
        </xsl:choose>
      </span>
    </xsl:if>
  </xsl:template>

  <xsl:template match="attr">
    <!--
        <xsl:text> [</xsl:text><xsl:value-of select="@name" /><xsl:text> </xsl:text><xsl:value-of select="@value" /><xsl:text>] </xsl:text>
    -->
  </xsl:template>

  <!-- Шаблон рисования страниц -->
  <xsl:template name="draw-number">
    <!-- текущий номер -->
    <xsl:param name="number-to-draw" />
    <!-- последний номер (количество?) -->
    <xsl:param name="last-number" />
    <!-- выбранный номер -->
    <xsl:param name="selected-number" />
    <!-- название переменной, передаваемой в урле -->
    <xsl:param name="p_name" />

    <!-- рисуем текущий номер -->
    <xsl:choose>
      <!-- если текущий номер - выбранный -->
      <xsl:when test="$number-to-draw = $selected-number">
        <b>
          <xsl:value-of select="$number-to-draw"/>
        </b>
      </xsl:when>
      <!-- иначе - делаем ссылку -->
      <xsl:otherwise>
        <xsl:if test="($number-to-draw &gt; 0) and ($number-to-draw &lt; $last-number+1)">
          <a>
            <xsl:attribute name="href">
              <xsl:value-of select="concat('/', $page-name, '?')" />
              <xsl:apply-templates select="$param[@name!=$p_name]"  mode="page-url"/>
              <xsl:value-of select="concat('&amp;', $p_name, '=', number($number-to-draw)-1)" />
            </xsl:attribute>
            <xsl:value-of select="$number-to-draw "/>
          </a>
        </xsl:if>
      </xsl:otherwise>
    </xsl:choose>

    <!-- рисуем следующий номер, если текущий меньше последнего -->
    <xsl:if test="($number-to-draw &lt;= $last-number) and ($number-to-draw &lt; $selected-number+10)">
      <xsl:call-template name="draw-number">
        <xsl:with-param name="number-to-draw" select="$number-to-draw + 1"/>
        <xsl:with-param name="last-number" select="$last-number"/>
        <xsl:with-param name="selected-number" select="$selected-number"/>
        <xsl:with-param name="p_name" select="$p_name"/>

      </xsl:call-template>
    </xsl:if>
  </xsl:template>
  <!-- /шаблон -->

 <xsl:template name="ellipsis">
  <xsl:param name="document" />
  <xsl:param name="snippet" />
  <xsl:choose>
  <xsl:when test="$snippet/@url">
     <xsl:apply-templates select="/page/parameters/*[name() = $ln]/group[@name='urls']/item" mode="report-links">
       <xsl:with-param name="val" select="$snippet/@url"/>
     </xsl:apply-templates>
     <!-- Показ pdf для Синтаксического корпуса -->
     <a class="linksview" href="http://ruscorpora.ru/syntax/{$snippet/@url}.pdf" target="_blank" >
         <xsl:text>[Показать структуру]</xsl:text>
     </a>
  </xsl:when>
  <xsl:when test="(key('param','ell') or not(key('param','nolinks'))) and not ($document/../@search-type = 'snippet')">
   <a class="b-kwic-expl">
    <xsl:attribute name="msg">
     <xsl:value-of select="$document/@title" disable-output-escaping="no" />
    </xsl:attribute>
    <xsl:attribute name="href">
      <xsl:choose>
        <xsl:when test="@url">
          <xsl:value-of select="@url" />
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="concat($page-name, '?')" />
          <xsl:for-each select="/page/state/param[@name!='sortsnipp'][@name!='ps']">
            <xsl:value-of select="concat(@name, '=', node(), '&amp;')" />
          </xsl:for-each>
          <xsl:choose>
            <xsl:when test="ancestor::result/@search-type = 'document'">
              <xsl:value-of select="concat('sid=', $snippet/@sid )" />
            </xsl:when>
            <!-- test="ancestor::result/@search-type == 'all-documents'" -->
            <xsl:otherwise>
              <xsl:value-of select="concat('docid=', $document/@id, '&amp;sid=', $snippet/@sid )"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>&larr;&hellip;&rarr;
   </a>
  </xsl:when>
  </xsl:choose>
 </xsl:template>


 <xsl:template name="kwic">
   <xsl:for-each select="word[@target='1' and (not(@queryPosition) or (@queryPosition=$kwic-word-pos))]">
    <xsl:if test="position()=1">
    <xsl:variable name="wordsToLeft" select="count(preceding-sibling::word)"/>
    <xsl:variable name="wordsToRight" select="count(following-sibling::word)"/>
    <tr>
     <td align="left" width="40%" style="overflow:hidden;">
     <table width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed">
      <tr><td>
       <div style="float:right;" align ="right">
        <xsl:text disable-output-escaping="yes">&lt;![if !IE]&gt;</xsl:text>
        <nobr>
        <xsl:text disable-output-escaping="yes">&lt;![endif]&gt;</xsl:text>
        <xsl:for-each select="preceding-sibling::*">
         <xsl:variable name="curLevel" select="count(following-sibling::word) - $wordsToRight"/>
         <xsl:if test="$curLevel &lt;= $kwic-size">
          <xsl:apply-templates select="." />
         </xsl:if>
        </xsl:for-each>
        <xsl:text disable-output-escaping="yes">&lt;![if !IE]&gt;</xsl:text>
        </nobr>
        <xsl:text disable-output-escaping="yes">&lt;![endif]&gt;</xsl:text>
      </div>
     </td></tr></table>
     </td>
     <td align="left">
      <nobr>
      <xsl:text>&nbsp;</xsl:text>
      <xsl:apply-templates select="." />
      <xsl:text>&nbsp;</xsl:text>
      </nobr>
     </td>
     <td width="100%">
      <table width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed">
      <tr><td>
        <xsl:text disable-output-escaping="yes">&lt;![if !IE]&gt;</xsl:text>
        <nobr>
        <xsl:text disable-output-escaping="yes">&lt;![endif]&gt;</xsl:text>
        <xsl:for-each select="following-sibling::*">
         <xsl:variable name="curLevel" select="count(preceding-sibling::word) - $wordsToLeft"/>
         <xsl:if test="$curLevel &lt;= $kwic-size">
          <xsl:apply-templates select="." />
         </xsl:if>
        </xsl:for-each>
        <xsl:text>&nbsp;&nbsp;</xsl:text>
        <xsl:call-template name="ellipsis">
         <xsl:with-param name="document" select="ancestor::document" />
         <xsl:with-param name="snippet" select="ancestor::snippet" />
        </xsl:call-template>
        <xsl:text disable-output-escaping="yes">&lt;![if !IE]&gt;</xsl:text>
        </nobr>
        <xsl:text disable-output-escaping="yes">&lt;![endif]&gt;</xsl:text>
      </td></tr></table>
     </td>
    </tr>
    </xsl:if>
   </xsl:for-each>
 </xsl:template>


 <xsl:template match="snippet" mode="snippets-list">
  <xsl:choose>
   <xsl:when test="$param[@name='out']='kwic'">
    <xsl:call-template name="kwic" />
   </xsl:when>
   <xsl:otherwise>
    <li>
      <xsl:apply-templates select="word | text" />
      <xsl:text> </xsl:text>
      <a>
        <xsl:attribute name="href">
          <xsl:value-of select="concat($page-name, '?')" />
          <xsl:for-each select="/page/state/param[@name!='sortsnipp'][@name!='ps']">
            <xsl:value-of select="concat(@name, '=', node(), '&amp;')" />
          </xsl:for-each>
          <xsl:value-of select="concat('docid=', ../@id)" />
        </xsl:attribute>[<xsl:value-of select="../@title" disable-output-escaping="yes" />]
      </a>
      <xsl:text> </xsl:text>
      <xsl:apply-templates select=".." mode="omo"/>
      <xsl:text> </xsl:text>
      <!--<a>
        <xsl:attribute name="href">
          <xsl:choose>
            <xsl:when test="@url">
              <xsl:value-of select="@url" />
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="concat($page-name, '?')" />
              <xsl:for-each select="/page/state/param[@name!='sortsnipp'][@name!='ps']">
                <xsl:value-of select="concat(@name, '=', node(), '&amp;')" />
              </xsl:for-each>
              <xsl:value-of select="concat('docid=', ../@id,'&amp;sid=', @sid )" />
            </xsl:otherwise>
          </xsl:choose>
        </xsl:attribute>&larr;&hellip;&rarr;
      </a>-->
    </li>
   </xsl:otherwise>
  </xsl:choose>
 </xsl:template>

 <xsl:variable name="plainOutput" select="(not($param[@name='out']) or $param[@name='out']!='kwic')" />

 <xsl:template match="br">
  <xsl:if test="$allowLineBreaks and position()!=1 and position()!=last()">
  <br/>
  </xsl:if>
 </xsl:template>

 <xsl:template match="p">
  <xsl:if test="$allowLineBreaks and position()!=1 and position()!=last()">
  <br/>
  <xsl:if test="$mode='poetic'"><br/></xsl:if>
  </xsl:if>
 </xsl:template>

  <xsl:template match="*" mode="report-links">
    <xsl:param name="val"/>
    <a>
      <xsl:attribute name="href">
        <xsl:value-of select="@begin"/>
        <xsl:value-of select="$val"/>
        <xsl:value-of select="@end"/>
      </xsl:attribute>
      <xsl:attribute name="target">_blank</xsl:attribute>
      <xsl:attribute name="class">linksview</xsl:attribute>
      <xsl:value-of select="@name"/>
    </a>&nbsp;
  </xsl:template>

  <xsl:template match="para">
      <table class="para">
       <xsl:for-each select="*">
        <tr><td class="para-lang"><xsl:value-of select="@language"/></td>
        <td class="para-snippet">
         <xsl:call-template name="snippet-impl">
         <xsl:with-param name="document" select="../.."/>
        </xsl:call-template>
        </td>
        </tr>
      </xsl:for-each>
     </table>
    <br/>
  </xsl:template>

  <xsl:template match="snippet">
    <xsl:call-template name="snippet-impl">
      <xsl:with-param name="document" select=".."/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="em">
   <span style="letter-spacing: 0.5em">
    <xsl:apply-templates/>
   </span>
  </xsl:template>

  <xsl:template match="i | b | sup | sub">
   <xsl:element name="{name(.)}">
    <xsl:apply-templates/>
   </xsl:element>
  </xsl:template>

  <xsl:template name="snippet-impl">
    <xsl:param name="document"/>
    <li>
      <xsl:if test="$allowLineBreaks and position() &gt; 2">
        <br/>
      </xsl:if>
      <xsl:apply-templates select="word | text | br | p | i | b | sub | sup | em" />
      <xsl:if test="@is_last='1'">
          <xsl:text> </xsl:text>
          <xsl:if test="not(key('param', 'notitle'))">
            <xsl:if test="$allowLineBreaks"><br/></xsl:if>
            <span class="doc">
             <xsl:choose>
              <xsl:when test="$mode='para' and position() != 1">
               <xsl:text>[</xsl:text><xsl:value-of select="$document/attributes/attr[@name='author_trans']/@value" disable-output-escaping="yes"/><xsl:text>. </xsl:text>
                <xsl:value-of select="$document/attributes/attr[@name='header_trans']/@value" disable-output-escaping="yes"/>
                <xsl:if test="$document/attributes/attr[@name='translator']/@value != '' or $document/attributes/attr[@name='date_trans']/@value != ''">
                  <xsl:text> (</xsl:text><xsl:if test="$document/attributes/attr[@name='translator']/@value != ''">
                     <xsl:value-of select="$document/attributes/attr[@name='translator']/@value" disable-output-escaping="yes"/><xsl:text>, </xsl:text>
                  </xsl:if>
                  <xsl:value-of select="$document/attributes/attr[@name='date_trans']/@value" disable-output-escaping="yes"/><xsl:text>)</xsl:text>
                </xsl:if><xsl:text>]</xsl:text>
              </xsl:when>
              <xsl:otherwise>
                 <xsl:text>[</xsl:text><xsl:value-of select="$document/@title" disable-output-escaping="yes"/><xsl:text>]</xsl:text>
              </xsl:otherwise>
             </xsl:choose>
            </span>
            <!-- Показ pdf для Синтаксического корпуса -->
            <xsl:choose>
              <xsl:when test="@url">
                <xsl:text>&nbsp;&nbsp;</xsl:text>
                  <a class="linksview" href="http://ruscorpora.ru/syntax/{@url}.pdf" target="_blank" >
                    <xsl:text>[Показать структуру]</xsl:text>
                  </a>
              </xsl:when>
            </xsl:choose>
          </xsl:if>

          <xsl:text> </xsl:text>
          <xsl:apply-templates select="$document" mode="omo"/>
          <xsl:text> </xsl:text>
          <xsl:choose>
            <xsl:when test="@url">
              <xsl:apply-templates select="/page/parameters/*[name() = $ln]/group[@name='urls']/item" mode="report-links">
                <xsl:with-param name="val" select="@url"/>
              </xsl:apply-templates>
            </xsl:when>
            <xsl:when test="(key('param','ell') or not(key('param','nolinks'))) and not ($document/../@search-type = 'snippet')">
              <a>
                <xsl:attribute name="href">
                  <xsl:value-of select="concat($page-name, '?')" />
                  <xsl:for-each select="/page/state/param[@name!='ps']">
                    <xsl:value-of select="concat(@name, '=', node(), '&amp;')" />
                  </xsl:for-each>
                  <xsl:choose>
                    <xsl:when test="$document/../@search-type = 'all-documents'">
                      <xsl:value-of select="concat('docid=', $document/@id, '&amp;sid=', @sid )"/>
                    </xsl:when>
                    <xsl:when test="$document/../@search-type = 'document'">
                      <xsl:value-of select="concat('sid=', @sid )" />
                    </xsl:when>
                  </xsl:choose>
                  <xsl:if test="$mode='poetic' or $mode='birchbark' or $mode='dialect'">
                   <xsl:text>&amp;expand=full</xsl:text>
                  </xsl:if>
                </xsl:attribute>
                <xsl:choose>
                 <xsl:when test="key('param','ell')">
                  <xsl:text>&hellip;</xsl:text>
                 </xsl:when>
                 <xsl:otherwise>
                  <xsl:text>&larr;&hellip;&rarr;</xsl:text>
                 </xsl:otherwise>
                </xsl:choose>
              </a>
            </xsl:when>
          </xsl:choose>
      </xsl:if>

      <xsl:if test="key('param', 'notitle')">
        <span class="b-doc-expl" explain="{$document/@id}">
          <xsl:value-of select="$lang/attributes"/>
        </span>
        <xsl:call-template name="doc-info-write-list">
          <xsl:with-param name="header" select="$lang/doc-info/*[@important='1']"/>
          <xsl:with-param name="values" select="$document/attributes"/>
        </xsl:call-template>
      </xsl:if>
    </li>
  </xsl:template>

  <xsl:template name="doc-info-write-list">
    <xsl:param name="header"/>
    <xsl:param name="values"/>
    <xsl:for-each select="$header">
      <xsl:variable name="name" select="name()"/>
      <xsl:if test="$values/*[@name = $name]/@value != ''">
        <xsl:text>&nbsp;</xsl:text>
        <xsl:value-of select="@name"/>
        <xsl:text>:&nbsp;</xsl:text>
        <xsl:value-of select="$values/*[@name = $name]/@value"/>
      </xsl:if>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="text">
    <!-- -->
    <xsl:value-of disable-output-escaping="no" select="." />
  </xsl:template>

  <xsl:template match="word">
    <xsl:choose>
      <xsl:when test="@target='1' and $slav">
        <!--<span class="cs">-->
         <span class="b-wrd-expl g-em cs" explain="{@source}">
          <xsl:value-of select="@text"/>
         </span>
        <!--</span>-->
      </xsl:when>
      <xsl:when test="@target='1' and $slav=false">
        <span class="b-wrd-expl g-em" explain="{@source}">
         <xsl:if test="$mode='para' and ../@language != 'ru'">
          <xsl:attribute name="l">
           <xsl:value-of select="../@language" />
          </xsl:attribute>
         </xsl:if>
         <xsl:value-of select="@text"/>
        </span>
      </xsl:when>
      <xsl:when test="@obsc='1' and not(key('param','noobsc'))">
        <span class="b-wrd-expl g-hidden" explain="{@source}">
         <xsl:if test="$mode='para' and ../@language != 'ru'">
          <xsl:attribute name="l">
           <xsl:value-of select="../@language" />
          </xsl:attribute>
         </xsl:if>
          <xsl:value-of select="@text"/>
        </span>
      </xsl:when>
      <xsl:when test="$slav">
       <span class="b-wrd-expl cs" explain="{@source}">
        <xsl:value-of select="@text"/>
       </span>
      </xsl:when>
      <xsl:otherwise>
        <span class="b-wrd-expl" explain="{@source}">
          <xsl:if test="$mode='para' and ../@language != 'ru'">
          <xsl:attribute name="l">
           <xsl:value-of select="../@language" />
          </xsl:attribute>
         </xsl:if>
         <xsl:value-of select="@text"/>
        </span>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="ana" >
    <!-- -->
    <xsl:value-of select="@lex" disable-output-escaping="no"/>
    <xsl:text> = </xsl:text>
    <!-- -->
    <xsl:value-of select="@gramm" disable-output-escaping="no"/>
    <xsl:apply-templates select="@sem" />
    <xsl:if test="position() != last()">
      <xsl:text>; </xsl:text>
    </xsl:if>
  </xsl:template>


  <xsl:template match="@sem">
    <xsl:text> = </xsl:text>
    <!-- -->
    <xsl:value-of select="." disable-output-escaping="no"/>
  </xsl:template>

  <xsl:template match="error">
    <xsl:if test="string-length(.)&gt;0">
      <ul>
        <b>
          <xsl:value-of select="."/>
        </b>
      </ul>
    </xsl:if>
  </xsl:template>

  <xsl:template match="page-stat">
   <div class="page-stat">
   <table border="1" cellpadding="5" cellspacing="0">
    <tr>
     <td colspan="3"><span class="page-stat-table-title">
      <xsl:choose>
       <xsl:when test="@type='forms'">
        <xsl:value-of select="$lang/freq/form" />
       </xsl:when>
       <xsl:when test="@type='lemmas'">
        <xsl:value-of select="$lang/freq/lemma" />
       </xsl:when>
      </xsl:choose>
     </span></td>
    </tr>
    <xsl:apply-templates />
   </table>
   </div>
  </xsl:template>

  <xsl:template match="page-stat/word">
   <tr>
    <td align="center"><xsl:value-of select="position()" /></td>
    <td><xsl:value-of select="@value" /></td>
    <td align="right"><xsl:value-of select="@rate" /></td>
   </tr>
  </xsl:template>

</xsl:stylesheet>
