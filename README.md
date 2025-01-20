# OmniLatinTool
The OmniLatin Tool is an open source RoboFont Extension that streamlines the design of a typeface with OmniLatin support. Find [here](https://www.sharptype.co/case-studies/omni-latin-tool) on Sharp Type website a step by step documentation. 

Here on Github, you will find a description of each button of the tool and the action they can have on your font file.

This tool is divided in 5 accordions that regroups actions according on what they affect. The first **GENERAL** section will be referred to for each actions of the tool. Please be very careful on what you pre-select there. 

## GENERAL
```
Apply to: 		- All Glyphs
			- Selected Glyphs
			- Current Glyph
```
These buttons define on which glyphs the actions are performed. The *Current Glyph* is pre-selected.

```
Overwrite Anchors / Component
```
If checked, the existing anchors and/or components will be overwritten. 
Glyphs with decomposed contours will always be skipped to protect your designs.

## CHARACTER SET

```
Add OmniLatin Glyphset
```
This button will add all the empty OmniLatin glyphs boxes to your existing character set.

## BASE LETTERS & DIACRITICS
```
Prebuild Characters
```
This button will adds reference glyphs that will help for the design of what we call the special characters (ex: A an E wil be copied in the Æ glyph box). This function can be used for letters and diacritics. Drawing all these characters is the first step.

Mark Color: RED

*Note: The recipe for the pre-built glyphs is defined in the separate file `specialChars_recipe.py` in the extension.*


```
Scale Ratio for Ordinal Letters: [textfield]
```
Some languages need ordinal letters (named with the suffix .sup). To help you design them, you can set a value in the Scale Ratio For Ordinal Letters textfield to scale the component and the sidebearings. Click again on `Prebuild Characters`.

*Note: There is no interpolation involved, only rescaling.*

```
Paste components
```
This button will add components and their respective width. It is mainly used to add components for the diacritics with identical designs and for the digram letters.

Mark Color: DARK BLUE

```
Center Glyphs
```
This button will center the glyph in its width.


```
Fix Diacritics Sidebearings
```
The tool has pre-saved values for the diacritics widths:

1. the cmb = zero width
2. the double cmb = zero width
3. the .cap = zero width
4. the modifiers = width of the contour + 50 units on the right and left sidebearings

If you wish to change the preset value of 50 units, you can use the Modifiers Sidebearings textfield and re-hit `Fix Diactritics Sidebearings`

## ANCHORS & PREVIEW
```
Remove Anchors
```
Removes all the anchors of the chosen glyph(s).

*Note: If you have a different anchor naming, we advise you to start anew and remove your previous anchors by hitting this button.*

```
Autoplace Anchors
```
This function will automatically place anchors according to predefined settings. 

*Note: This is a smart guess by the tool and it should always be manually checked.
You should place anchors on base letters and diacritics as well on special characters with decomposed contours. No need to put anchors on glyphs made of components only (accented letters).*

```
Gear Icon
```
Click on it for personalized settings. You can visualize the preset settings for each anchor. Anchors can be placed on the closest vertical metrics (above or below) or on the closest extreme point coordinates.
Enter the value of your choice to the Extra X or Extra Y coordinates to add it to the auto-placement. 
*Note: Make sure to press Enter to validate the value before clicking OK and closing the pop-up window.*

```
Get Anchors from Base Glyphs
```
If the glyph is made from a component (with an additional decomposed contour) you can get the anchors from the base glyph by hitting this button.

```
Anchor Preview (Glyph window)
```
Helps you preview the diacritics placement on letters, using the existing anchors: 
In the letter glyph window, preview some diacritics.
In the diacritics glyph window, preview a selection of letters.
Reacts in real time if you move the anchors. Darkens as you preview the character.

```
Anchor Preview Glyph: [textfield]
```
The OmniLatin Tool automatically picks some accents or glyphs to showcase in the Anchor Preview but if you want to see a specific letter, you can type it in the *Anchor Preview Glyph* textfield. 

```
Component Preview (SpaceCenter)
```
Preview in the Space Center all the characters using this glyph as component: you can preview all the accented versions of a letter, or all the characters using one diacritic.

## ACCENTED CHARACTERS

```
Build Accented Characters
```
This button will build all the accented characters, using components and anchors. 

*Note: The recipe for these accented characters is defined in the separate file `basicGlyphset.py` in the extension.*

```
Build Characters from Alternate
```
This button will build all the accented and special characters needed for your alternate letter.
Before using this button, make sure to have all the anchors needed on the alternate glyphs. ⚠️ The behavior of this button is different than the others. You need to select the alternate character(s) and then hit the button, the tool will create the new glyphs at the end of the character set. 


## ENCODING & FEATURES

```
Fix Unicodes
```
Adds unicode value to the OmniLatin glyphs. Some letters have multiple unicodes. The tool will inform you in the output window if it deleted or changed something. 

```
Generate Features
```
Behind the scene, this button generates the combining marks list, the languagesytem list, the decomposition list, the locl feature and the cmcp feature, and writes them in the Features panel of the font. It also builds two external files: mkmk.fea and mark.fea.

*Note: If you need to generate the features a second time, make sure to delete the files and features in the panel beforehand.*


# The future of this tool

We decided to share the OmniLatin Tool as an open source tool because this knowledge needs to be shared and used for a better representation of all the Latin languages.

[→ Read the Case Study about the OmniLatin Research](https://www.sharptype.co/case-studies/omni-latin-research)

This extension was designed for the software RoboFont and is available on Mechanic 2 and on Github. The tool and research are always ongoing projects and we are looking forward to hear back from the type community about what we could add or improve. For example, the localized features could be expended to other languages with their specifications. We are also always looking for samples of texts in rare languages.

We invite you to pull a request on Github if you are able to contribute to this great tool! If you are interested to develop it for Glyphs App, feel free to do it.

# Credits

The OmniLatin tool was co-directed by Léna Le Pommelet & My-Lan Thuong.

It was developed by Marte Verhagen, with the contribution of Calvin Kwok, My-Lan Thuong and Peter Nowell.

The OmniLatin character set is based on the research by My-Lan Thuong, Cris Hernández, Glenda Bellarosa, the Rosetta Type team (Hyperglot) and the Google team (Shaperglot).

Thank you Frederik Berlaen (RoboFont), Tal Leming (Ezui), Frank Grießhammer (Mark Feature Writer) and Petr van Blokland who inspired us with his Font Assistant.
