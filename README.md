# OmniLatinTool
This Robofont extension is here to assist you in building your characterset up to OmniLatin. Find [here](https://www.sharptype.co/case-studies/omni-latin-tool) on Sharp Type website a step by step explanation. Here, you will find a description of each button of the tool and the action they can have on your font file.

This tool is divided in 5 accordions that regroups actions according on what they will have an effect. Only the first one **GENERAL** will be referred to for each actions of the tool. Please be very carefull on what you pre-select on this accordion. 

## GENERAL
```
Apply to: 		- All Glyphs
			- Selected Glyphs
			- Current Glyphs
```
They define on which glyphs the actions are performed. The *Current Glyph* is pre-selected.

```
Overwrite Anchors / Component
```
If checked, the existing anchors/components will be overwritten.

## CHARACTER SET

```
Add OmniLatin
```
This button will add all the empty glyphs boxes on the font window, that we will filled up with the OmniLatin Letters.

## BASE LETTERS & DIACRITICS
```
Prebuild Characters
```
This button will adds reference glyphs that will help for the design of what we call the special characters (ex: A an E wil be copied in the Æ glyph box). This function will be used for letters and diacritics. Drawing all these characters is the first step.

Mark Color: RED

*Note: The recipe for these pre-building glyphs are defined in the separate file `specialChars_recipe.py` in the extension.*


```
Scale Ration for Ordinal Letters: [textfield]
```
Some languages uses ordinals letters, to help you design them according to your vertical metrics, you can change the value of this ration in the textfield and click again on `Prebuild Characters` to get it right.

```
Paste component
```
This button will adds components, nothing else. It mainly use to add components for the diacritics that has identical designs.

Mark Color: DARK BLUE

```
Center Glyphs
```
This button will center the glyph on the width it already have.


```
Fix Diacritics Sidebearings
```
The tool has pre-saved the values ​​of the diacritics widths:

1. the cmb = zero width
2. the doube cmb = zero width
3. the .cap = zero width
4. the modifiers = width of the sign + 50 units on the right and left sidebearings

If you wish to change the value of the 50 units, use the textfield and re-hit `Fix Diactritics Sidebearings`

## ANCHORS & PREVIEW
```
Remove Anchors
```
We all have different ways of dealing with Anchors. To make sure that you have to correct anchor naming we advise you to start from fresh and remove all you anchors by hitting this button.

```
Autoplace Anchors
```
The button itself will automatically place anchors. This is just a smart guess by the tool and it should always be manually checked. 

If you click on the gear icon, you can specify where to place the anchors. you can choose to placed some units more or less, on the vertical or the horizontal mark.

```
Get Anchors from Base Glyphs
```
If your glpsh is made out of a compenent you can get the well placed anchors form the base glyph by hitting this button.

*Note: The OmniLatin needs to be able to to build new characters from your glyphset, characters that will maybe stack several accents on top on each other. You don't need to draw all the combinations, just by placing the anchors correctly on every needed glyphs and by generating correctly the features (below on the tool) it will operate fine.*

```
Anchor Preview (Glyph window)
```
You can preview the diacritics on a letter. You can also preview a letter when you are in a diacritic glpyh window. The placement of the preview is made accordingly to the existing anchors.

```
Anchor Preview Glyph: [textfield]
```
The OmniLatin Tool automatically picks some accents or glyphs to showcase but if you want to see a specific letter, you can type it in the *Anchor Preview Glyph* textfield.

```
Component Preview (SpaceCenter)
```
The Component Preview happens in the SpaceCenter. It will show all glyphs that use the currentGlyph as a component.

## ACCENTED CHARACTERS

```
Build Accented Characters
```
This button will build all the accented characters. 

*Note: The recipe for these accented characters are defined in the separate file `basicGlyphset.py` in the extension.*

```
Build Characters from Alternates
```
Before using this button, make sure to have all the anchors needed on those alternate glyphs.  This button will build all the accented characters needed for your alternate letter. ⚠️ The behavior of this button is different than the others. You need to select the alternate character and then hit the button, the tool will take care of the rest. 


## ENCODING & FEATURES

```
Fix Unicodes
```
Add unicode value to the OmniLatin glyphs. Some letters have double unicode. The tool will informe you on the output window if it delete or changes something. 

```
Generate Features
```
This step is crutial, if you want to test your font we advise you to do it before. It will create ccmp feature, locl feature, mark feature and mkmk feature.

It will add also add in the features panel of your font the languages statements and specific features for the identified languages.


# The future of this tool

We decided to share the OmniLatin Tool as an open source tool because this knowledge needs to be shared and used so all the latin languages are represented. We don't pretend that this tool is perfect and we are very looking forward to the improvements from the type community.

The localized feature for example could be expended to other languages with their specifications.

We invite you to pull request here if you are able to contribute to this great tool!

This tool was design for the software Robofont we don't have the knowledge in house to develop it for Glyphs. If you are interested of doing it feel free to reach ou to us!

# Thank you
The first Thank you goes to Marte Verhaegen, she wrote most of this tool code. She came up with the most creative solution to all our wishes. Thank Marte!

The Sharp Type team behind this tool is Léna Le Pommelet, My-Lan Thuong and Clavin Kwok. My-Lan and Léna spend days to imagine the interface, the behavior, the UX, to write, correct and add dictionaries or even add functions. Calvin join for the last but not least step, he wrote the process which allow the font to handle OmniLatin support.

Thank you to Peter Nowell for the precious help and advice.

This tool would not exist without Frederick Berlean (Robofont) and Tal Lemming (ezui), thank you to both of them.

Thank you Frank Grießhammer (Adobe) for the Mark Feature Writer.

Thank you Petr van Blokland who inspired us with his Font Assistant.

The OmniLatin character set was build with the work of Glenda Bellarosa, Cris Hernández, My-Lan Thuong, the Rosetta Type team for the Hyperglot and the Google team for the Shaperglot.
