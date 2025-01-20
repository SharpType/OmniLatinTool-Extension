import re
import shutil
import os

UC_ACCENTED_DECOMP_ALL = ["Aacute", "Abreve", "Abreveacute", "Abrevedotbelow", "Abrevegrave", "Abrevehookabove", "Abrevetilde", "Acaron", "Acircumflex", "Acircumflexacute", "Acircumflexdotbelow", "Acircumflexgrave", "Acircumflexhookabove", "Acircumflextilde", "Adieresis", "Adieresismacron", "Adot", "Adotbelow", "Agrave", "Ahookabove", "Amacron", "Aring", "Aringacute", "Atilde", "AEacute", "Bdotbelow", "Blinebelow", "Cacute", "Ccaron", "Ccircumflex", "Cdotaccent", "Dcaron", "Dcircumflexbelow", "Dcommaaccent", "Ddotbelow", "Dlinebelow", "Eacute", "Ebreve", "Ecaron", "Ecircumflex", "Ecircumflexacute", "Ecircumflexdotbelow", "Ecircumflexgrave", "Ecircumflexhookabove", "Ecircumflextilde", "Edieresis", "Edotaccent", "Edotbelow", "Egrave", "Ehookabove", "Emacron", "Etilde", "Etildebelow", "Ezhcaron", "Gacute", "Gbreve", "Gcaron", "Gcircumflex", "Gcommaaccent", "Gdotaccent", "Hcaron", "Hcircumflex", "Hdieresis", "Hdotbelow", "Iacute", "Ibreve", "Icaron", "Icircumflex", "Idieresis", "Idotaccent", "Idotbelow", "Igrave", "Ihookabove", "Imacron", "Itilde", "Itildebelow", "Jcircumflex", "Kacute", "Kcaron", "Kcommaaccent", "Kdotbelow", "Klinebelow", "Lacute", "Lcaron", "Lcircumflexbelow", "Lcommaaccent", "Ldot", "Ldotbelow", "Llinebelow", "Macute", "Nacute", "Ncaron", "Ncircumflexbelow", "Ncommaaccent", "Ndot", "Ndotbelow", "Ngrave", "Nlinebelow", "Ntilde", "Oacute", "Obreve", "Ocaron", "Ocircumflex", "Ocircumflexacute", "Ocircumflexdotbelow", "Ocircumflexgrave", "Ocircumflexhookabove", "Ocircumflextilde", "Odieresis", "Odot", "Odotbelow", "Ograve", "Ohookabove", "Ohornacute", "Ohorndotbelow", "Ohorngrave", "Ohornhookabove", "Ohorntilde", "Ohungarumlaut", "Omacron", "Oslashacute", "Otilde", "Otildeacute", "Pdotaccent", "Racute", "Rcaron", "Rcommaaccent", "Rdotbelow", "Rlinebelow", "Sacute", "Scaron", "Scircumflex", "Scommaaccent", "Sdotbelow", "Tcaron", "Tcircumflexbelow", "Tcommaaccent", "Tdotbelow", "Tlinebelow", "Uacute", "Ubreve", "Ucaron", "Ucircumflex", "Udieresis", "Udieresisacute", "Udieresiscaron", "Udieresisgrave", "Udieresismacron", "Udotbelow", "Ugrave", "Uhookabove", "Uhornacute", "Uhorndotbelow", "Uhorngrave", "Uhornhookabove", "Uhorntilde", "Uhungarumlaut", "Umacron", "Uring", "Utilde", "Utildeacute", "Utildebelow", "Vtilde", "Wacute", "Wcircumflex", "Wdieresis", "Wgrave", "Xdieresis", "Xdot", "Yacute", "Ycircumflex", "Ydieresis", "Ydotbelow", "Ygrave", "Yhookabove", "Ymacron", "Ytilde", "Zacute", "Zcaron", "Zcircumflex", "Zdotaccent", "Zdotbelow", "Aogonek.NAV", "Astroke", "Cstroke", "Estroke", "Twithdiagonalstroke", "Ustroke", "Oslash", "Eth", "Istroke", "Lbar", "Lmiddletilde", "Rstroke", "Tbar", "Zstroke", "Gstroke", "Hbar", "Pstroke", "Lstroke", "Jstroke", "Aogonek", "Eogonek", "Ecedilla", "Iogonek", "Oogonek", "Uogonek"]
LC_ACCENTED_DECOMP_ALL = ["aacute", "abreve", "abreveacute", "abrevedotbelow", "abrevegrave", "abrevehookabove", "abrevetilde", "acaron", "acircumflex", "acircumflexacute", "acircumflexdotbelow", "acircumflexgrave", "acircumflexhookabove", "acircumflextilde", "adieresis", "adieresismacron", "adot", "adotbelow", "agrave", "ahookabove", "amacron", "aring", "atilde", "aeacute", "bdotbelow", "blinebelow", "cacute", "ccaron", "ccircumflex", "cdotaccent", "dcaron", "dcircumflexbelow", "dcommaaccent", "ddotbelow", "dlinebelow", "eacute", "ebreve", "ecaron", "ecircumflex", "ecircumflexacute", "ecircumflexdotbelow", "ecircumflexgrave", "ecircumflexhookabove", "ecircumflextilde", "edieresis", "edotaccent", "edotbelow", "egrave", "ehookabove", "emacron", "etilde", "etildebelow", "ezhcaron", "gacute", "gbreve", "gcaron", "gcircumflex", "gcommaaccent", "gdotaccent", "hcaron", "hcircumflex", "hdieresis", "hdotbelow", "iacute", "ibreve", "icaron", "icircumflex", "idieresis", "idotaccent", "igrave", "ihookabove", "imacron", "itilde", "jcaron", "jcircumflex", "kacute", "kcaron", "kcommaaccent", "kdotbelow", "klinebelow", "lacute", "lcaron", "lcircumflexbelow", "lcommaaccent", "ldot", "ldotbelow", "llinebelow", "macute", "nacute", "ncaron", "ncircumflexbelow", "ncommaaccent", "ndot", "ndotbelow", "ngrave", "nlinebelow", "ntilde", "oacute", "obreve", "ocaron", "ocircumflex", "ocircumflexacute", "ocircumflexdotbelow", "ocircumflexgrave", "ocircumflexhookabove", "ocircumflextilde", "odieresis", "odot", "odotbelow", "ograve", "ohookabove", "ohornacute", "ohorndotbelow", "ohorngrave", "ohornhookabove", "ohorntilde", "ohungarumlaut", "omacron", "oslashacute", "otilde", "otildeacute", "pdotaccent", "racute", "rcaron", "rcommaaccent", "rdotbelow", "rlinebelow", "sacute", "scaron", "scircumflex", "scommaaccent", "sdotbelow", "tcaron", "tcircumflexbelow", "tcommaaccent", "tdotbelow", "tlinebelow", "uacute", "ubreve", "ucaron", "ucircumflex", "udieresis", "udieresisacute", "udieresiscaron", "udieresisgrave", "udieresismacron", "udotbelow", "ugrave", "uhookabove", "uhornacute", "uhorndotbelow", "uhorngrave", "uhornhookabove", "uhorntilde", "uhungarumlaut", "umacron", "uring", "utilde", "utildeacute", "utildebelow", "vtilde", "wacute", "wcircumflex", "wdieresis", "wgrave", "xdieresis", "xdot", "yacute", "ycircumflex", "ydieresis", "ydotbelow", "ygrave", "yhookabove", "ymacron", "ytilde", "zacute", "zcaron", "zcircumflex", "zdotaccent", "zdotbelow", "astroke", "cstroke", "estroke", "tstroke", "ustroke", "oslash", "dcroat", "hbar", "lstroke", "lbar", "lmiddletilde", "gstroke", "rstroke", "tbar", "zstroke", "aogonek", "eogonek", "ecedilla", "oogonek", "uogonek"]
UPPERCASE = ["A", "Aogonek", "Astroke", "AE", "B", "Bhook", "C", "Ccedilla", "Chook", "Cstroke", "D", "Dhook", "Dstroke", "Eth", "E", "Ecedilla", "Eogonek", "Eopen", "Ereversed", "Esh", "Estroke", "Schwa", "Ezh", "F", "Fhook", "G", "Ghook", "Glottalstop", "Gstroke", "H", "Hbar", "Hhook", "Hturned", "I", "Iogonek", "Ismall", "Istroke", "J", "Jcrossedtail", "Jstroke", "K", "Khook", "L", "Lbar", "Lbelt", "Lmiddletilde", "Lslash", "Lstroke", "M", "N", "Nhookleft", "Eng", "O", "Obar", "Ohorn", "Oogonek", "Oopen", "Oslash", "OE", "P", "Phook", "Thorn", "Pstroke", "Q", "R", "Rstroke", "Rtail", "S", "Scriptg", "T", "Tbar", "Thook", "Tretroflexhook", "Twithdiagonalstroke", "U", "Ubar", "Uhorn", "Uogonek", "Ustroke", "V", "Vhook", "Vturned", "W", "Whook", "X", "Y", "Yhook", "Z", "Zstroke", "Alpha.LATN", "Chi.LATN", "Iota.LATN", "Aogonek.NAV", "Eogonek.NAV", "Uogonek.NAV", "Upsilon.LATN", "Eng.locl", "Theta.LATN"]
MARKS_CMB_ABOVE_ALL = ["dieresiscmb", "dotaccentcmb", "gravecmb", "acutecmb", "hungarumlautcmb", "circumflexcmb", "caroncmb", "brevecmb", "ringabovecmb", "tildecmb", "macroncmb", "hookabovecmb", "verticallineabovecmb", "doublegravecmb", "invertedbrevecmb", "revcommaaccentcmb", "turnedabovecmb", "turnedcommaabovecmb", "horncmb", "inverteddoublebrevecmb", "acutemacroncmb", "gravemacroncmb", "macronacutecmb", "macrongravecmb", "dieresis.cap", "dotaccent.cap", "grave.cap", "acute.cap", "hungarumlaut.cap", "circumflex.cap", "caron.cap", "breve.cap", "ring.cap", "tilde.cap", "macron.cap", "breveacute", "brevegrave", "brevehook", "brevetilde", "circumflexacute", "circumflexgrave", "circumflexhook", "circumflextilde", "dieresisacutecmb", "dieresiscaron", "dieresisgravecmb", "dieresismacron", "breveacute.cap", "brevegrave.cap", "brevehook.cap", "brevetilde.cap", "circumflexacute.cap", "circumflexgrave.cap", "circumflexhook.cap", "circumflextilde.cap", "dieresisacute.cap", "dieresiscaron.cap", "dieresisgrave.cap", "dieresismacron.cap", "doublegrave.cap", "hookabove.cap", "invertedbreve.cap", "ringacute.cap"]
MARKS_CMB_BELOW = ["minusbelowcmb", "dotbelowcmb", "dieresisbelowcmb", "ringbelowcmb", "commaaccentbelowcmb", "cedillacmb", "ogonekcmb", "circumflexbelowcmb", "invertedbelowbrevecmb", "tildebelowcmb", "macronbelowcmb", "lowlinecmb", "righthalfringbelowcmb", "macrondoublebelowcmb"]
MARKS_CMB_ABOVE = ["dieresiscmb", "dotaccentcmb", "gravecmb", "acutecmb", "hungarumlautcmb", "circumflexcmb", "caroncmb", "brevecmb", "ringabovecmb", "tildecmb", "macroncmb", "soliduslongoverlaycmb"]
MARKS_CMB_ABOVE_CAP = ["dieresis.cap", "dotaccent.cap", "grave.cap", "acute.cap", "hungarumlaut.cap", "circumflex.cap", "caron.cap", "breve.cap", "ring.cap", "tilde.cap", "macron.cap", "soliduslongoverlaycmb.cap"]

def generate_ccmp_feature(font):
    if not font:
        print("No font open.")
        return
    
    # Filter sets by glyph presence in font
    uc_acc = [g for g in UC_ACCENTED_DECOMP_ALL if g in font]
    lc_acc = [g for g in LC_ACCENTED_DECOMP_ALL if g in font]
    uppercase = [g for g in UPPERCASE if g in font]
    marks_above_all = [g for g in MARKS_CMB_ABOVE_ALL if g in font]
    marks_below = [g for g in MARKS_CMB_BELOW if g in font]
    marks_above = [g for g in MARKS_CMB_ABOVE if g in font]
    marks_above_cap = [g for g in MARKS_CMB_ABOVE_CAP if g in font]

    # Build class definitions dynamically
    class_defs = []
    if uc_acc:
        class_defs.append("@UC_ACCENTED_DECOMP_ALL = [" + " ".join(uc_acc) + "];")
    if lc_acc:
        class_defs.append("@LC_ACCENTED_DECOMP_ALL = [" + " ".join(lc_acc) + "];")
    if uppercase:
        class_defs.append("@uppercase = [" + " ".join(uppercase) + "];")
    if marks_above_all:
        class_defs.append("@MARKS_CMB_ABOVE_ALL = [" + " ".join(marks_above_all) + "];")
    if marks_below:
        class_defs.append("@MARKS_CMB_BELOW = [" + " ".join(marks_below) + "];")
    # Add the newly requested groups:
    if marks_above:
        class_defs.append("@MARKS_CMB_ABOVE = [" + " ".join(marks_above) + "];")
    if marks_above_cap:
        class_defs.append("@MARKS_CMB_ABOVE_CAP = [" + " ".join(marks_above_cap) + "];")


    # Initialize the feature code string
    feature_code = ""
    feature_code += "# ---------------------------------------------------------------------------------------------\n"
    feature_code += "# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓  OMNILATIN TOOL FEATURES ADDITIONS  ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓\n"
    # Add class definitions to feature_code
    feature_code += "# Class Definitions\n"
    for cdef in class_defs:
        feature_code += cdef + "\n"
    feature_code += "\n"

    # Dynamically generate lookups for decomposition
    if uc_acc or lc_acc:
        feature_code += "lookup DECOMPOSITION {\n"
        skipped_glyphs = []
        # Combine both uppercase and lowercase accented sets for decomposition
        for g in uc_acc + lc_acc:
            glyphObj = font[g]
            # Check if the glyph has no contours and more than one component
            if len(glyphObj.components) > 1 and len(glyphObj.contours) == 0:
                # Start the substitution rule for this glyph
                sub_rule = f"    sub {g} by"
                # Add each component to the rule
                component_names = [c.baseGlyph for c in glyphObj.components]
                sub_rule += " " + " ".join(component_names) + ";"
                feature_code += sub_rule + "\n"
            else:
                # Record skipped glyph names
                skipped_glyphs.append(g)
        feature_code += "} DECOMPOSITION;\n\n"

        # If needed, add skipped glyphs as comments
        if skipped_glyphs:
            feature_code += "# Skipped glyphs (not purely compositional): " + ", ".join(skipped_glyphs) + "\n\n"

    # Soft dot and related glyphs
    i_variant_glyphs = [g for g in ("i", "j", "iogonek", "istroke") if g in font]
    if i_variant_glyphs:
        feature_code += "lookup SOFT_DOT {\n"
        if "i" in i_variant_glyphs:
            feature_code += "    sub i by dotlessi;\n"
        if "j" in i_variant_glyphs:
            feature_code += "    sub j by dotlessj;\n"
        if "iogonek" in i_variant_glyphs:
            feature_code += "    sub iogonek by dotlessiogonek;\n"
        if "istroke" in i_variant_glyphs:
            feature_code += "    sub istroke by dotlessistroke;\n"
        feature_code += "} SOFT_DOT;\n\n"

    # Dot decomposition glyphs
    dot_decomp_glyphs = [g for g in ("itildebelow", "idotbelow") if g in font]
    if dot_decomp_glyphs:
        feature_code += "lookup DOT_DECOMP {\n"
        if "itildebelow" in dot_decomp_glyphs:
            feature_code += "    sub itildebelow by dotlessi tildebelowcmb;\n"
        if "idotbelow" in dot_decomp_glyphs:
            feature_code += "    sub idotbelow by dotlessi dotbelowcmb;\n"
        feature_code += "} DOT_DECOMP;\n\n"

    # Now build the ccmp feature
    feature_code += "feature ccmp {\n"
    # Only add DECOMPOSE_PRECOMPOSED if accented glyphs and marks exist
    if (uc_acc or lc_acc) and (marks_above_all or marks_below):
        feature_code += "    lookup DECOMPOSE_PRECOMPOSED {\n"
        if uc_acc or lc_acc:
            feature_code += "        sub [@UC_ACCENTED_DECOMP_ALL @LC_ACCENTED_DECOMP_ALL]' lookup DECOMPOSITION [@MARKS_CMB_ABOVE_ALL @MARKS_CMB_BELOW];\n"
        if i_variant_glyphs and marks_above_all:
            # Dynamically create the glyph list for substitution
            i_variant_glyphs_str = "[ " + " ".join(i_variant_glyphs) + " ]"
            feature_code += f"        sub {i_variant_glyphs_str}' lookup SOFT_DOT @MARKS_CMB_ABOVE_ALL;\n"
        if dot_decomp_glyphs and marks_above_all:
            # Dynamically create the glyph list for substitution
            dot_decomp_glyphs_str = "[ " + " ".join(dot_decomp_glyphs) + " ]"
            feature_code += f"        sub {dot_decomp_glyphs_str}' lookup DOT_DECOMP @MARKS_CMB_ABOVE_ALL;\n"
        feature_code += "    } DECOMPOSE_PRECOMPOSED;\n\n"

    # CAP_ACCENTS_CMB_CONTEXT
    if uppercase and marks_above and marks_below and marks_above_cap:
        feature_code += "    lookup CAP_ACCENTS_CMB_CONTEXT {\n"
        feature_code += "        sub @uppercase @MARKS_CMB_ABOVE' by @MARKS_CMB_ABOVE_CAP;\n"
        feature_code += "        sub @MARKS_CMB_ABOVE_CAP @MARKS_CMB_ABOVE' by @MARKS_CMB_ABOVE_CAP;\n"
        feature_code += "        sub @MARKS_CMB_ABOVE_CAP @MARKS_CMB_BELOW @MARKS_CMB_ABOVE' by @MARKS_CMB_ABOVE_CAP;\n"
        feature_code += "    } CAP_ACCENTS_CMB_CONTEXT;\n\n"

    feature_code += "} ccmp;\n"

    # Function to write the feature code to features.fea using RoboFont's API
    def write_feature_to_fea(font, new_ccmp_code):
        try:
            # Ensure the font has a path (i.e., it's saved)
            if not font.path:
                print("Font does not have a saved path. Please save the font first.")
                return

            # Access the existing features text
            existing_features = font.features.text if font.features.text else ""

            # Regex pattern to find existing ccmp feature
            # This pattern matches 'feature ccmp { ... } ccmp;'
            ccmp_pattern = re.compile(r"feature\s+ccmp\s*\{.*?\}\s*ccmp\s*;", re.DOTALL)

            # Remove existing ccmp feature if it exists
            existing_features = re.sub(ccmp_pattern, "", existing_features)

            # Append the new ccmp feature
            updated_features = existing_features.strip() + "\n\n" + new_ccmp_code

            # Update the font's features.text
            font.features.text = updated_features

            print("ccmp feature successfully added to features.fea.")

        except Exception as e:
            print(f"An error occurred while writing to features.fea: {e}")

    # Write the generated feature code to features.fea
    write_feature_to_fea(font, feature_code)
	
# # Run the script
# font = CurrentFont()
# generate_ccmp_feature(font)