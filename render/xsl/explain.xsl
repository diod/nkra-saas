<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE xsl:stylesheet SYSTEM "symbols.ent">
<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:x="http://www.yandex.ru/xscript"
        extension-element-prefixes="x"
        version="1.0">

  <xsl:output method="html" indent="yes" encoding="utf-8"/>

  <xsl:variable name="param" select="/page/state[@type='Request']/param" />

  <xsl:variable name="mode" select="/page/state/param[@name='mode']"/>
  
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
  <xsl:variable name="slav" select="$mode='orthlib' or $mode='old_rus' or $mode='birchbark' or $mode='mid_rus'" />

  <xsl:template match="/">
    <!--<xsl:value-of select="x:http-header-out('Content-Type', 'text/html; charset=utf-8')"/>-->
    <div>
      <xsl:apply-templates select="/page/searchresult/body/result"/>
      <xsl:call-template name="bug-reporter"/>
    </div>
  </xsl:template>

  <xsl:template name="bug-reporter">
    <br />
    <div style="letter-spacing: 0">
    <div id="bug-reporter-caption" align="right">
      <a class="bug-reporter-caption" onclick="javascript:showBugReporter();">Сообщить об ошибке...</a>
    </div>
    <form style="display:none" id="bug-reporter-form">
      <table>
        <tr>
          <td>Сообщение об ошибке:</td>
        </tr>
        <tr>
          <td>
            <textarea onkeypress="return (value.length &lt;=200);" cols="30" rows="3" id="bug-comment" class="bug-reporter-form"></textarea>
          </td>
        </tr>
        <tr>
          <td>
            <div align="right">
              <input type="button" id="bug-apply" class="bug-reporter-button" value="Отправить" onclick="bugReport();"/>
            </div>
          </td>
        </tr>
      </table>
    </form>
    </div>
  </xsl:template>

  <xsl:template match="result">
    <div style="letter-spacing: 0">
    <xsl:apply-templates select="word"/>
    <xsl:apply-templates select="document"/>
    </div>
  </xsl:template>

  <xsl:template match="word">
    <table>
      <tr>
        <th colspan="2">
         <xsl:choose>
          <xsl:when test="$slav">
           <span class="cs"><xsl:value-of select="@text"/></span>
          </xsl:when>
          <xsl:otherwise>
           <xsl:value-of select="@text"/>
          </xsl:otherwise>
         </xsl:choose>
        </th>
      </tr>
      <xsl:apply-templates select="ana"/>
    </table>
  </xsl:template>

  <xsl:template match="ana">
    <xsl:apply-templates select="el"/>
  </xsl:template>

  <xsl:template match="el">
    <xsl:if test="$lang/word-info/*[name() = current()/@name]/@name != ''">
      <tr>
        <xsl:if test="position() = 1">
          <xsl:attribute name="class">sep</xsl:attribute>
        </xsl:if>

        <td>
          <xsl:value-of select="$lang/word-info/*[name() = current()/@name]/@name"/>
        </td>
        <td class="value">
          <xsl:choose>
           <xsl:when test="@name='lex'">
            <xsl:apply-templates/>
            <xsl:variable name="l" select="$param[@name='language']" />
            <xsl:choose>
              <xsl:when test="$slav=false and $l!='' and $l!='ru'">
              <xsl:text> </xsl:text>
              (<a target="_blank" title="Яндекс.Переводчик">
               <xsl:attribute name="href">
                <xsl:text>http://translate.yandex.ru/?text=</xsl:text>
                <xsl:value-of select="el-group/el-atom" />
                <xsl:text>&amp;lang=</xsl:text>
                <xsl:value-of select="$l" />
                <xsl:text>-ru</xsl:text>
               </xsl:attribute>
               <xsl:text>см.&nbsp;перевод</xsl:text>
              </a>)
             </xsl:when>
             <xsl:when test="$slav=false and ($l='' or $l='ru')">
              <xsl:text> </xsl:text>
              (<a target="_blank" title="ABBYY Lingvo Live">
               <xsl:attribute name="href">
                <xsl:text>http://dic.academic.ru/searchall.php?SWord=</xsl:text>
                <xsl:value-of select="el-group/el-atom" />
               </xsl:attribute>
               <xsl:text>см.&nbsp;в&nbsp;словарях</xsl:text>
              </a>)
             </xsl:when>
            </xsl:choose>
           </xsl:when>
           <xsl:otherwise>
            <xsl:apply-templates/>
           </xsl:otherwise>
          </xsl:choose>
        </td>
      </tr>
    </xsl:if>
  </xsl:template>

  <xsl:template match="el-group">
    <xsl:if test="position() - 1">
      <br/>
      <xsl:text></xsl:text>
      <wbr/>
    </xsl:if>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="el-atom">
    <xsl:if test="position() - 1">
      <xsl:text>,&#160;</xsl:text>
    </xsl:if>
    <xsl:variable name="atom" select="text()" />
    <xsl:choose>
      <xsl:when test="$lang/attrs/atom[@key=$atom] and ../../@name!='lex'">
        <xsl:value-of select="$lang/attrs/atom[@key=$atom]" />
      </xsl:when>
      <xsl:otherwise>
       <xsl:apply-templates/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:if test="@modifier">
      <xsl:value-of select="@modifier" />
    </xsl:if>
  </xsl:template>

  <xsl:template match="document">
    <xsl:call-template name="write-list">
      <xsl:with-param name="header" select="$lang/doc-info"/>
      <xsl:with-param name="values" select="attributes"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="write-list">
    <xsl:param name="header"/>
    <xsl:param name="values"/>
    <table>
      <xsl:for-each select="$header/*">
        <xsl:variable name="name" select="name()"/>
        <xsl:if test="$values/*[@name = $name]/@value != ''">
          <tr>
            <td>
              <xsl:value-of select="@name"/>
            </td>
            <td class="value">
             <xsl:choose>
              <xsl:when test="$name='link'">
               <a target="_blank" title="Древнерусские берестяные грамоты">
                <xsl:attribute name="href">
                 <xsl:value-of select="$values/*[@name = $name]/@value" />
                </xsl:attribute>
                <xsl:value-of select="$values/*[@name = $name]/@value" />
               </a>
              </xsl:when>
              <xsl:when test="$name='audio'">
                <a target="_blank" title="Аудиозапись">
                <xsl:attribute name="href">
                 <xsl:text>http://ruscorpora.ru/</xsl:text>
                 <xsl:value-of select="$values/*[@name = $name]/@value" />
                </xsl:attribute>
                <xsl:value-of select="$values/*[@name = $name]/@value" />
               </a>
              </xsl:when>
              <xsl:otherwise>
               <xsl:value-of select="$values/*[@name = $name]/@value"/>
              </xsl:otherwise>
             </xsl:choose>
            </td>
          </tr>
        </xsl:if>
      </xsl:for-each>
    </table>
  </xsl:template>

  <xsl:template match="attr">
    <xsl:choose>
      <xsl:when test="$lang/doc-info/*[name() = current()/@name]/@name != ''">
        <p>
          <b>
            <xsl:value-of select="$lang/doc-info/*[name() = current()/@name]/@name"/>
          </b>
          <xsl:text>: </xsl:text>
          <xsl:value-of select="@value" disable-output-escaping="yes"/>
        </p>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
