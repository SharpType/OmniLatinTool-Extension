import re

def add_ss20_locl_feature(font):
    """
    Adds the 'ss20' OpenType feature to the current UFO's features.fea file
    if 'Eng.locl' is present in the glyph set, and then adds languagesystems
    and the locl feature inline.
    """
    FEATURE_NAME = "ss20"
    FEATURE_CODE = f'''
# change the number of ss20 to adapt it to your list
feature {FEATURE_NAME} {{
    featureNames {{
        name "Alternate Eng"; #Windows English
        name 1 0 0 "Alternate Eng"; #Mac English
    }};
    sub Eng by Eng.locl;
}} {FEATURE_NAME};
'''.strip()
    
#    font = CurrentFont()
    if not font:
        print("No font is currently open. Please open a font and try again.")
        return
    
    if "Eng.locl" not in font:
        print("'Eng.locl' glyph not found in the current font. The 'ss20' feature will not be added.")
        return
    else:
        print("'Eng.locl' glyph found. Proceeding to add the 'ss20' feature.")
    
    if not font.path:
        print("The font must be saved before modifying 'features.fea'. Please save the font and try again.")
        return
    
    existing_features = font.features.text if font.features.text else ""
    feature_pattern = re.compile(
        rf"feature\s+{FEATURE_NAME}\s*\{{.*?\}}\s*{FEATURE_NAME}\s*;",
        re.DOTALL
    )
       
    # Remove any existing 'ss20' feature
    updated_features, num_subs = feature_pattern.subn("", existing_features)
    if num_subs > 0:
        print(f"Existing '{FEATURE_NAME}' feature removed from 'features.fea'.")
    else:
        print(f"No existing '{FEATURE_NAME}' feature found. A new one will be added.")
    
    # Append the new 'ss20' feature
    if updated_features.strip():
        updated_features = updated_features.strip() + "\n\n" + FEATURE_CODE + "\n"
    else:
        updated_features = FEATURE_CODE + "\n"
    
    # Define the languagesystem lines and locl feature
    languagesystem_lines = """
languagesystem DFLT dflt;
languagesystem latn dflt;
languagesystem latn AZE ;
languagesystem latn CAT ;
languagesystem latn CRT ;
languagesystem latn KAZ ;
languagesystem latn MAR ;
languagesystem latn MOL ;
languagesystem latn NAV ;
languagesystem latn NLD ;
languagesystem latn ROM ;
languagesystem latn TAT ;
languagesystem latn TRK ;
"""

    locl_feature = """
feature locl {
    script latn;
    lookup i_TRK {
        language AZE; # Azeri
        language CRT; # Crimean Tatar
        language KAZ; # Kazakh
        language TAT; # Tatar
        language TRK; # Turkish
            sub i by idotaccent;
        } i_TRK;

        language NLD;
            sub Iacute J by IJacute;
            sub iacute j by ijacute;
            lookup dutchij {
                sub I J by IJ;
                sub i j by ij;
            } dutchij;
         
         language DEU exclude_dflt; #GERMAN
            sub S S by Germandbls;
            sub s s by germandbls;
            sub quotedblleft by quotedblbase;
            sub quotedblright by quotedblleft;

        language FRA exclude_dflt; #FRENCH
            sub quotedblleft by guillemotleft;
            sub quotedblright by guillemotright;

        language CAT; # Catalan
        lookup CAT_Ldot {
            sub l' periodcentered' l by ldot;
            sub L' periodcentered' L by Ldot;
        } CAT_Ldot;

        language MOL;  # Moldavian
        lookup ST_cedilla {
            sub Scedilla by Scommaaccent;
            sub scedilla by scommaaccent;
            sub Tcedilla by Tcommaaccent;
            sub tcedilla by tcommaaccent;
        } ST_cedilla;

        language NAV;  # Navajo
        lookup centerogonek {
            sub Aogonek by Aogonek.NAV;
            sub Eogonek by Eogonek.NAV;
            sub Uogonek by Uogonek.NAV;
            sub aogonek by aogonek.NAV;
            sub eogonek by eogonek.NAV;
            sub uogonek by uogonek.NAV;
        } centerogonek;

        language ROM;  # Romanian
        lookup ST_cedilla;
} locl;
"""

    # Prepend languagesystem lines and append locl feature inline
    updated_features = languagesystem_lines.strip() + "\n\n" + updated_features.strip() + "\n\n" + locl_feature.strip() + "\n"

    font.features.text = updated_features
    print(f"'{FEATURE_NAME}' feature and 'locl' feature successfully added to 'features.fea'.")

#add_ss20_locl_feature()