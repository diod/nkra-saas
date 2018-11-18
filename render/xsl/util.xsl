<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE xsl:stylesheet SYSTEM "symbols.ent">
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:template name="conj-impl">
 <xsl:param name="caption" />
 <xsl:param name="value" />
 <xsl:param name="lang" />
 <xsl:choose>
  <xsl:when test="$lang='ru' or $lang='ua'">
   <xsl:choose>
    <xsl:when test="($value mod 100 != 11) and ($value mod 10 = 1)">
     <xsl:value-of select="$caption/@f1" />
    </xsl:when>
    <xsl:when test="($value mod 100 != 12) and ($value mod 10 = 2)">
     <xsl:value-of select="$caption/@f234" />
    </xsl:when>
    <xsl:when test="($value mod 100 != 13) and ($value mod 10 = 3)">
     <xsl:value-of select="$caption/@f234" />
    </xsl:when>
    <xsl:when test="($value mod 100 != 14) and ($value mod 10 = 4)">
     <xsl:value-of select="$caption/@f234" />
    </xsl:when>
    <xsl:otherwise>
     <xsl:value-of select="$caption/@f" />
    </xsl:otherwise>
   </xsl:choose>
  </xsl:when>

  <xsl:when test="$lang='en'">
   <xsl:choose>
    <xsl:when test="$value=1">
     <xsl:value-of select="$caption/@f1" />
    </xsl:when>
    <xsl:otherwise>
     <xsl:value-of select="$caption/@f" />
    </xsl:otherwise>
   </xsl:choose>
  </xsl:when>

  <xsl:when test="$lang='default'">
   <xsl:value-of select="$caption/@f" />
  </xsl:when>
 </xsl:choose>
</xsl:template>

<xsl:template name="conj">
 <xsl:param name="caption" />
 <xsl:param name="value" />
 <xsl:param name="lang" value="default" />
 <xsl:param name="is_number_wrong" value="false" />
 <span class="stat-number"><xsl:number value="$value" grouping-size="3" grouping-separator=" " /></span>
 <xsl:choose>
  <xsl:when test="$is_number_wrong='true'"><xsl:text> (приблизительно)</xsl:text></xsl:when>
 </xsl:choose>
 <xsl:text>&#160;</xsl:text>
 <span class="stat-caption">
  <xsl:call-template name="conj-impl">
   <xsl:with-param name="caption" select="$caption" />
   <xsl:with-param name="value" select="$value" />
   <xsl:with-param name="lang" select="$lang" />
  </xsl:call-template>
 </span>
</xsl:template>

<xsl:template name="conj-documents">
 <xsl:param name="value" />
 <xsl:param name="mode" />
 <xsl:param name="is_number_wrong" value="false" />
 <xsl:choose>
  <xsl:when test="$mode='murco'">
   <xsl:call-template name="conj">
    <xsl:with-param name="caption" select="$lang/conj/fragments" />
    <xsl:with-param name="value" select="$value" />
    <xsl:with-param name="lang" select="$ln" />
    <xsl:with-param name="is_number_wrong" select="$is_number_wrong" />
   </xsl:call-template>
  </xsl:when>
  <xsl:otherwise>
   <xsl:call-template name="conj">
    <xsl:with-param name="caption" select="$lang/conj/documents" />
    <xsl:with-param name="value" select="$value" />
    <xsl:with-param name="lang" select="$ln" />
    <xsl:with-param name="is_number_wrong" select="$is_number_wrong" />
   </xsl:call-template>
  </xsl:otherwise>
 </xsl:choose>
</xsl:template>


<xsl:template name="conj-sentences">
 <xsl:param name="value" />
 <xsl:call-template name="conj">
  <xsl:with-param name="caption" select="$lang/conj/sentences" />
  <xsl:with-param name="value" select="$value" />
  <xsl:with-param name="lang" select="$ln" />
 </xsl:call-template>
</xsl:template>

<xsl:template name="conj-contexts">
 <xsl:param name="value" />
 <xsl:call-template name="conj">
  <xsl:with-param name="caption" select="$lang/conj/contexts" />
  <xsl:with-param name="value" select="$value" />
  <xsl:with-param name="lang" select="$ln" />
 </xsl:call-template>
</xsl:template>

<xsl:template name="conj-words">
 <xsl:param name="value" />
 <xsl:call-template name="conj">
  <xsl:with-param name="caption" select="$lang/conj/words" />
  <xsl:with-param name="value" select="$value" />
  <xsl:with-param name="lang" select="$ln" />
 </xsl:call-template>
</xsl:template>

</xsl:stylesheet>
