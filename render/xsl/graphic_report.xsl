<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE xsl:stylesheet SYSTEM "symbols.ent">
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:str="http://exslt.org/strings"
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

  <!-- распределение по годам всех вхождений -->
  <xsl:variable name="year" select="/page/years" />

  <!-- стартовый год -->
   <xsl:variable name="start_year">
    <xsl:choose>
      <xsl:when test="/page/state/param[@name='startyear']">
        <xsl:value-of select="/page/state/param[@name='startyear']"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="1800"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <!-- конечный год -->
  <xsl:variable name="end_year">
    <xsl:choose>
      <xsl:when test="/page/state/param[@name='endyear']">
        <xsl:value-of select="/page/state/param[@name='endyear']"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="2018"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <!-- сглаживание -->
  <xsl:variable name="smoothing">
    <xsl:choose>
      <xsl:when test="/page/state/param[@name='smoothing']">
        <xsl:value-of select="/page/state/param[@name='smoothing']"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="0"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>


  <xsl:template name="h1">
   <br/><h1>
    <xsl:value-of select="$lang/created-distribution" /> <xsl:text> </xsl:text>
    <xsl:value-of select="$lang/corpora-list/corpus[@mode=$mode]/@in" /> <!--xsl:text> (&#946;)</xsl:text-->
    <xsl:text> с </xsl:text> <xsl:value-of select="$start_year" />
    <xsl:text> по </xsl:text><xsl:value-of select="$end_year" />
    <xsl:text> (сглаживание </xsl:text><xsl:value-of select="$smoothing" /><xsl:text>)</xsl:text>
   </h1><br clear="all" />
  </xsl:template>


  <xsl:template name="plot">
    <script type="text/javascript">
      <![CDATA[
      window.start_year = ]]><xsl:value-of select="$start_year" /><![CDATA[;
      window.end_year = ]]><xsl:value-of select="$end_year" /><![CDATA[;
      window.smoothing = ]]><xsl:value-of select="$smoothing" /><![CDATA[;
      ]]>
    </script>
    <script type="text/javascript" src="www/js/graphic.js"></script>

    <xsl:apply-templates select="/page/searchresult/body/result/graphic" />

    <div id="placeholder" style="width:100%;height:500px;"></div>

    <script type="text/javascript">
      <xsl:text>
      queries = [
      </xsl:text>
      <xsl:for-each select="/page/searchresult/body/result/parted_query">
        <xsl:text>'</xsl:text><xsl:value-of select="attribute::query"/><xsl:text>'</xsl:text>
        <xsl:if test="position() != last()"><xsl:text>,</xsl:text></xsl:if>
      </xsl:for-each>
      <xsl:text>
      ];
      totals = {
      </xsl:text>
        <xsl:for-each select="/page/years/group">
          <xsl:text>'</xsl:text><xsl:value-of select="@meta"/><xsl:text>': </xsl:text>
          <xsl:value-of select="@hits" />
          <xsl:if test="position() != last()"><xsl:text>,</xsl:text></xsl:if>
        </xsl:for-each>
      <xsl:text>
      };
      relative = false;
      init();
      $(prepare());
      </xsl:text>
    </script>
  </xsl:template>


  <xsl:template match="page">
    <html>
      <head>
        <xsl:copy-of select="$lang/header"/>
        <link rel="stylesheet" type="text/css" href="http://ruscorpora.ru/verstka/common.css" />
        <script type="text/javascript" src="http://ruscorpora.ru/verstka/jquery.js"></script>
        <script type="text/javascript" src="http://ruscorpora.ru/verstka/excanvas.js"></script>
        <script type="text/javascript" src="http://ruscorpora.ru/verstka/jquery.flot.js"></script>
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

          <table>
            <form action="" onsubmit="new_query(); return false;">
              <tr><td valign="middle" style="font-size: 85%" colspan="2">
                <div>
                  Слова или сочетания слов, через запятую:&nbsp;
                  <input type="text" id="query" name="query" size="50"/>
                </div>
              <br/></td></tr>
              <tr><td style="font-size: 85%" colspan="2">
                <div>
                  Годы с
                  <input type="text" id="year_start" name="year_start" size="4" maxlength="4" value="1800"/>
                  по
                  <input type="text" id="year_end" name="year_end" size="4" maxlength="4" value="2010"/>
                </div>
              <br/></td></tr>
              <tr>
                <td valign="middle" style="font-size: 85%">
                  <div>
                    Сглаживание:&nbsp;&nbsp;
                    <select name="smoothing" id="smoothing">
                      <option value="0">0</option><option value="1">1</option><option value="2">2</option>
                      <option selected="true" value="3">3</option><option value="4">4</option><option value="5">5</option>
                      <option value="6">6</option><option value="7">7</option><option value="8">8</option>
                      <option value="9">9</option><option value="10">10</option><option value="20">20</option>
                      <option value="30">30</option><option value="40">40</option><option value="50">50</option>
                    </select>
                  </div>
                <br/></td>
                <td align="right" valign="top">
                  <input class="button" type="submit" value="построить"/>
                  <!--input class="button" type="reset" value="очистить"-->
              </td></tr>
            </form>
          </table>

          <xsl:call-template name="plot" />
          <xsl:call-template name="other" />
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
        <tbody><tr>
          <xsl:apply-templates />
          <td valign="top">
            <table border="1" cellpadding="7">
              <tr><td colspan="2"><b>Всего:</b></td></tr>
              <xsl:for-each select="/page/years/group">
                <xsl:sort select="@meta" order="descending" />
                <xsl:variable name="meta" select="@meta"/>
                <xsl:if test="/page/searchresult/body/result/graphic/year[@year=$meta]">
                  <tr>
                    <td><xsl:value-of select="@meta"/></td>
                    <td><xsl:value-of select="@hits"/></td>
                  </tr>
                </xsl:if>
              </xsl:for-each>
            </table>
          </td>
        </tr></tbody>
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
          <xsl:value-of select="$year" />
        </a>
      </td>
      <td><xsl:value-of select="attribute::cnt" /></td>
    </tr>
  </xsl:template>


  <xsl:template match="graphic">
    <xsl:variable name="query_words" select="attribute::query" />
    <script type="text/javascript">
      <xsl:text>
      values['</xsl:text><xsl:value-of select="$query_words"/><xsl:text>'] = [
      </xsl:text>
      <xsl:for-each select="year">
        <xsl:text>['</xsl:text>
        <xsl:value-of select="@year" />
        <xsl:text>',</xsl:text>
        <xsl:value-of select="@cnt" />
        <xsl:text>]</xsl:text>
        <xsl:if test="position() != last()"><xsl:text>,</xsl:text></xsl:if>
      </xsl:for-each>
      <xsl:text>];</xsl:text>
    </script>
  </xsl:template>

  <xsl:template name="other">
    <!--xsl:if test="$multi"-->
      <div align="right" style="font-size:smaller">
        <!--
        <a href="http://ruscorpora.ru/ngram-about.html">О проекте</a>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-->
        Искать в
        <a href="javascript:GoogleNgramViewerLink()">Google Books Ngram Viewer</a>
      </div>
    <!--/xsl:if-->
  </xsl:template>
</xsl:stylesheet>
