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


  <!-- параметры страницы -->
  <xsl:key name="param" match="/page/state/param" use="@name" />
  <xsl:variable name="param" select="/page/state/param" />

  <!-- язык запроса -->
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

  <!-- корпус -->
  <xsl:variable name="mode" select="/page/state/param[@name='mode']"/>


  <xsl:template name="h1">
   <br/><h1>
    <xsl:value-of select="$lang/created-distribution" /> <xsl:text> </xsl:text>
    <xsl:value-of select="$lang/corpora-list/corpus[@mode=$mode]/@in" /> <!--xsl:text> (&#946;)</xsl:text-->
   </h1><br clear="all" />
  </xsl:template>


  <xsl:template match="page">
    <html>
      <head>
            <xsl:copy-of select="$lang/header"/>
            <link rel="stylesheet" type="text/css" href="http://ruscorpora.ru/verstka/common.css" />
            <script type="text/javascript" src="http://ruscorpora.ru/verstka/jquery.js"></script>
            <script type="text/javascript" src="http://ruscorpora.ru/verstka/common.js"></script>
      </head>
      <body>
        <xsl:call-template name="metrika" />

        <div class="hat">
          <div class="logo">
            <xsl:copy-of select="$lang/logo"/>
          </div>
        </div>
        <div class="line">
          <img alt="line under logo" src="http://ruscorpora.ru/verstka/i/bottom_logo.gif" width="169" height="9" />
          <br />
        </div>
        <div class="content">
          <xsl:call-template name="h1" />
          <xsl:apply-templates select="searchresult" />
        </div>
        <div class="footer">
          <xsl:copy-of select="$lang/footer" />
        </div>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="searchresult">
      <!-- Результаты поиска -->
      <xsl:apply-templates select="/page/searchresult/body/result/tables" />
  </xsl:template>

  <xsl:template match="tables">
    <div id="tables" style="">
      <table style="margin-left: -20px" cellspacing="20">
        <tbody><tr><xsl:apply-templates /></tr></tbody>
      </table>
    </div>
  </xsl:template>

  <xsl:template match="table">
    <xsl:variable name="query_words" select="attribute::query"/>
      <td valign="top">
        <table cellpadding="7" border="1"><tbody>
            <tr><td colspan="2">
              <a target="_blank" href="http://processing.ruscorpora.ru:8888/search.xml?mode=main&amp;env=alpha&amp;text=lexform&amp;req={$query_words}&amp;sort=gr_tagging"><b>
                <!-- <script type="text/javascript">document.write('<xsl:value-of select="$query_words" />');</script> -->
                <xsl:value-of select="$query_words" />
              </b></a>
            </td></tr>
            <xsl:apply-templates />
        </tbody></table>
      </td>
  </xsl:template>

  <xsl:template match="row">
    <xsl:variable name="query_words" select="../attribute::query"/>
    <xsl:variable name="year" select="attribute::year"/>
    <xsl:variable name="s_created" select="attribute::s_created"/>
    <tr>
      <td>
        <a target="_blank" href="http://processing.ruscorpora.ru:8888/search.xml?mode=main&amp;env=alpha&amp;text=lexform&amp;req={$query_words}&amp;mycorp=s_year_created:%22{$s_created}%22&amp;sort=gr_tagging">
        <!--a target="_blank" href="http://localhost.ru:8001/search.xml?mode=main&amp;env=alpha&amp;text=lexform&amp;req={$query_words}&amp;mycorp=s_year_created:%22{$s_created}%22&amp;sort=gr_tagging"-->
          <xsl:value-of select="$year" />
        </a>
      </td>
      <td><xsl:value-of select="attribute::cnt" /></td>
    </tr>
  </xsl:template>
</xsl:stylesheet>
