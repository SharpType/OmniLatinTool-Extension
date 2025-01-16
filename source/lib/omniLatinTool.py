import ezui
import math

from fontTools.misc.transform import Transform
from glyphConstruction import GlyphConstructionBuilder
from mojo.extensions import getExtensionDefault, setExtensionDefault
from mojo.pens import DecomposePointPen
from mojo.subscriber import Subscriber, WindowController, registerGlyphEditorSubscriber, unregisterGlyphEditorSubscriber
from mojo.events import postEvent
from mojo.subscriber import registerSubscriberEvent
from mojo.UI import inDarkMode, CurrentSpaceCenter, OpenSpaceCenter

import basicGlyphset

import importlib
importlib.reload(basicGlyphset)
from basicGlyphset import OmniLatin

import specialChars_recipe
importlib.reload(specialChars_recipe)
from specialChars_recipe import specialChars

import markFeatureWriter
importlib.reload(markFeatureWriter)
from markFeatureWriter import MarkFeatureWriter

definedGlyphset = OmniLatin

from ccmp_generate import generate_ccmp_feature
from locl_ss_feature import add_ss20_locl_feature
import os

# Accent placements:
# Horizontal : 0=left, 1=center, 2=right, 3=0
# Vertical : 0=top, 1=center, 2=bottom, 3=0

standardAccentPlacements = [
	dict(name="top", horizontal=1, vertical=0),
	dict(name="_top", horizontal=1, vertical=2, extraY=-0),
	dict(name="bottom", horizontal=1, vertical=2),
	dict(name="_bottom", horizontal=1, vertical=0),
	dict(name="ogonek", horizontal=2, vertical=2, point=True),
	dict(name="_ogonek", horizontal=2, vertical=0, point=True),
	dict(name="topRight", horizontal=2, vertical=0, extraX=20),
	dict(name="_topRight", horizontal=0, vertical=0),
	dict(name="middle", horizontal=1, vertical=1),
	dict(name="_middle", horizontal=1, vertical=1),
	dict(name="horn", horizontal=2, vertical=0),
	dict(name="_horn", horizontal=1, vertical=2),
]

for item in standardAccentPlacements:
	item.setdefault('extraX', 0)
	item.setdefault('extraY', 0)
	item.setdefault('point', False)

standardVerticalAccentPlacements = ["descender", "0", "xHeight", "capHeight", "ascender"]



def createDictOfAccentedGlyphsPerBaseGlyph( originalGlyphData ) :
	# Prepare a dictionary where we can look up all of the 
	# accented characters (glyph names) for a base glyph name.
	
	# The dictionary will look like this:
	# {
	#	"R" : ["Racute", "Rcaron", "Rcircumflex"],
	#	"Q" : ["Qhook"],
	# }
	
	# Start an empty dictionary, to fill later (during the loop)
	accentedGlyphsPerBaseGlyph = {}
	
	for accentedGlyphName, accentedGlyphRecipe in originalGlyphData.items() :
		# Get the list of base glyphs for this glyph.
		baseGlyphs = accentedGlyphRecipe.get( "baseGlyphs" )
		# Continue/skip this glyph if it doesn't actually have info about base glyphs
		if not baseGlyphs :
			continue
		# Otherwise go through each base glyph name.
		for thisBaseGlyphName in baseGlyphs :
			# Check if the dictionary already has a key for this base glyph name.
			# If it does not then create a new one
			if thisBaseGlyphName not in accentedGlyphsPerBaseGlyph :
				accentedGlyphsPerBaseGlyph[ thisBaseGlyphName ] = [ accentedGlyphName ]
			# If it does already exist in the dictionary,
			else :
				# Add an entry to the dictionary for this base glyph.
				# The value in the dictionary must be a list of strings, so wrap this accented glyph name
				# in a list (inside square brackets).
				accentedGlyphsPerBaseGlyph[ thisBaseGlyphName ].append( accentedGlyphName )
	
	return accentedGlyphsPerBaseGlyph


# An "inverted" version of the definedGlyphset dictionary of glyph data,
# where a base glyph name is the key and the corresponding value is a
# list of accented glyph names that use the base glyph. Makes it easy to
# look up the accented glyphs for a base glyph.
accentedGlyphsPerBaseGlyph = createDictOfAccentedGlyphsPerBaseGlyph( definedGlyphset )


def determineAccentedAlternateGlyphNamesFor( alternateGlyphName ) :
	# Give this function the name of an alternate glyph (ex: "R.alt") and it will
	# return/provide a list of the glyph names of accented versions based on the
	# base glyph. Each item in the list is a tuple with 2 things: the final
	# accented *alternate* glyph name (ex: "Racute.alt"), and its *non-alternate*
	# accented glyph name (ex: "Racute"). Example list below:
	# [
	# 	('Racute.alt', 'Racute'),
	# 	('Rcaron.alt', "Rcaron")
	# ]
	# Note: In rare cases, an accented character might have multiple base glyphs
	# (ex: AE, NJ). This function only pays attention to the glyph name provided
	# (alternateGlyphName)... so if that was E.alt and there was also an A.alt or
	# an A.swash, this function will only suggest AE.alt (for the E.alt). It will
	# not suggest additional permutations like AE.alt.swash.
	
	# Split the glyph name string into a list of pieces, separated by periods.
	# The periods will be removed, then re-added later.
	alternateGlyphNamePieces = alternateGlyphName.split( "." )  # ["R", "alt", "sl"]
	baseGlyphName = alternateGlyphNamePieces[0]  # R
	
	# What are the accented characters that use this base glyph?
	# This will be revised by getting the info from a dictionary
	accentedGlyphsBasedOnThisGlyph = accentedGlyphsPerBaseGlyph.get( baseGlyphName )
	# If there are no glyphs based on this one, stop this function
	# and return an empty list.
	if accentedGlyphsBasedOnThisGlyph == None :
		return []
	
	# Create an empty list, to fill in the following loop.
	# The final glyph names of accented versions of this alternate glyph.
	alternateAccentedGlyphNames = []
	
	# Go through each accented glyph name, one at a time.
	for thisAccentedGlyphName in accentedGlyphsBasedOnThisGlyph :
	
		# First, figure out the glyph name for this alternate accented character.
		# It should contain all of the suffixes from the original glyph name, but
		# swap out the base glyph name.
		
		# We need to copy the glyph name pieces from the original alternate glyph
		# (ex: "R.alt"), then we can make changes to these new, copied pieces.
		
		alternateAccentedGlyphNamePieces = alternateGlyphNamePieces # ["R", "alt", "sl"]
		
		# Change the first glyph name piece from the base glyph name to the accented glyph name.
		# Essentially we're replacing item 1 in the "pieces" list, with a different string.
		
		alternateAccentedGlyphNamePieces[0] = thisAccentedGlyphName
		
		# Join the alternate accented glyph name pieces, with periods in between.
		alternateAccentedGlyphName = ".".join( alternateAccentedGlyphNamePieces )
		
		# Add this name to the list.
		alternateAccentedGlyphNames.append( (alternateAccentedGlyphName, thisAccentedGlyphName) )
	
	# After finishing creating the glyph names for each accented glyph, return them.
	return alternateAccentedGlyphNames


def createAndFillComposedGlyph( font, overwrite, glyphName, categoryMarkColor, nameOfGlyphToGetAccentsFrom = None) :
	# Creates (and optionally overwrites) a glyph with the specified name, fills it
	# with the necessary components, and adds the glyph to the font.
	# Optionally provide a nameOfGlyphToGetAccentsFrom parameter (string) if you want
	# to add accents from a different glyph (useful for alternates like "R.alt", so that
	# it can get the accents from "R").
	
	
	# Make sure nameOfGlyphToGetAccentsFrom has a value, falling back to glyphName.
	nameOfGlyphToGetAccentsFrom = nameOfGlyphToGetAccentsFrom or glyphName

	#print( glyphName, nameOfGlyphToGetAccentsFrom )
	
	# Look up this glyph in the database
	glyphData = definedGlyphset[ nameOfGlyphToGetAccentsFrom ]
	
	# and make sure it has info about the base glyph name and accents (otherwise stop).
	if 'baseGlyphs' not in glyphData or 'accents' not in glyphData :
		return
	
	
	# Create and/or clear the glyph in the font.
	# If the glyph with glyphName is already in the font;
	if glyphName in font :
		existingGlyph = font[glyphName]
		# If the glyph isn't empty, and overwriting is not allowed, stop this function.
		# Also stop if the glyph has any paths/contours (as something has been decomposed
		# for a custom design).
		if (existingGlyph.bounds and not overwrite) or existingGlyph.contours : #or ('accents' not in existingGlyph)
			return
		# Otherwise, proceed to clear the glyph (delete all paths, components, guidelines, etc.)
		else :
			font.newGlyph(glyphName, clear=True)
	# Otherwise, create a new glyph
	else :
		font.newGlyph(glyphName, clear=True)
	
	# At this point we know the glyph is in the font and ready for accent components.
	glyph = font[ glyphName ]
	

	# Get the name of its base glyph (its *first* base glyph)
	baseGlyphName = glyphData['baseGlyphs'][0]
	
	# Note: This only acknowledges the first base glyph. In rare cases (ex: NJ)
	# there can be multiple base glyphs. Those additional ones will not be added
	# automatically.
	
	# If a different nameOfGlyphToGetAccentsFrom was provided, we need to figure out
	# the glyph name suffix (ex: ".alt") and add the suffix to the base glyph name ("R")
	# as long as it is in the font (an "R.alt" glyph exists).
	glyphNameSuffix = ""
	if nameOfGlyphToGetAccentsFrom in glyphName :
		glyphNameSuffix = glyphName.removeprefix( nameOfGlyphToGetAccentsFrom )
	
	
	# Start to construct a recipe for the Glyph Construction Builder
	construction = glyphName + " = " + baseGlyphName + glyphNameSuffix  # ex: "Racute = R"
	
	# Go through the name of each accent for this glyph (ex: "acute.cap@top").
	for accent in glyphData['accents']:
		# Split the string by the "@" character, separating accent name and anchor name:
		accentData = accent.split('@')
		# As long as there was a "@" we will have those 2 names. Otherwise nothing will
		# happen for this accent; it will proceed to the next accent.
		if len(accentData) > 1:
			# Assign variable names to the accent name and anchor/position name
			accentName, accentPosition = accentData
			# Add to the construction recipe...
			construction += f" + {accentName}@{baseGlyphName+glyphNameSuffix}:{accentPosition}"
			# Our construction string now looks like this:
			# "Racute = R + acute@R:top"
			# (OR) "Racute.alt = R.alt + acute@R.alt:top"
	
	# Use the GlyphConstructionBuilder framework to assemble the components into a glyph,
	# and apply that to the actual glyph in the font.
	with glyph.undo("Build characters"):
		constructionGlyph = GlyphConstructionBuilder(construction, font)
		constructionGlyph.draw(glyph.getPen())
		glyph.width = constructionGlyph.width
		
		# Assign a mark color to this glyph.
		if glyphName in ("Aogonek", "Aogonek.NAV", "Astroke", "Cstroke", "Eth", "Eogonek", "Eogonek.NAV", "Estroke", "Gstroke", "IJacute", "Ldot", "Lstroke", "Lbar", "Lmiddletilde", "Ohorn", "Ohornacute", "Ohorndotbelow", "Ohorngrave", "Ohornhookabove", "Ohorntilde", "Oslash", "Oslashacute", "Rstroke", "Tbar", "Twithdiagonalstroke", "Uhorn", "Uhornacute", "Uhorndotbelow", "Uhorngrave", "Uhornhookabove", "Uhorntilde", "Ustroke", "Zstroke", "Pstroke", "astroke", "aogonek", "aogonek.NAV", "cstroke","dcroat", "eogonek", "eogonek.NAV", "estroke", "gstroke", "hbar", "ldot", "lstroke", "lmiddletilde", "ohorn", "ohornacute", "ohorndotbelow", "ohorngrave", "ohornhookabove", "ohorntilde", "uhornacute", "oogonek", "oslash", "rstroke", "tstroke", "uhorn", "uhorndotbelow", "uhorngrave", "uhornhookabove", "uhorntilde", "uogonek", "uogonek.NAV", "ustroke",  "zstroke"):
			glyph.markColor = (1,0.5,0,.4)
		else:
			glyph.markColor = categoryMarkColor
		

def addChosenGlyphset (chosenGlyphset):
	font = CurrentFont()
	glyphOrder = list(font.lib["public.glyphOrder"])
	# IMPORTANT: Must use `font.lib["public.glyphOrder"]` instead of `font.glyphOrder` because 
	# they actually work slightly differently. This function expects that the glyph order contains 
	# all the glyphs in the font, but RoboFont only includes a glyph in `font.glyphOrder` if it 
	# has/had some paths:components. Newly-created glyphs aren't included. But they are included 
	# in `font.lib["public.glyphOrder"]`.
	
	
	for i, glyph in enumerate(chosenGlyphset):
	
		if not glyph in glyphOrder:
			if i == 0:
				glyphOrder.insert(0, glyph)
			else:
				prevGlyph = list(chosenGlyphset)[i - 1]
				if prevGlyph in glyphOrder:
					prevPlace = glyphOrder.index(prevGlyph)
					glyphOrder.insert(prevPlace + 1, glyph)
				else:
					glyphOrder.append(glyph)
	
	font.glyphOrder = glyphOrder



class drawReferenceGlyphs(Subscriber):

	debug = True
	controller = None

	def build(self):
		self.isPreview = False
		
		glyphEditor = self.getGlyphEditor()
		
		self.container = glyphEditor.extensionContainer(
			identifier=DEFAULT_KEY,
   		location='background',
   		clear=True
		)
		self.previewContainer = glyphEditor.extensionContainer(
			identifier=DEFAULT_KEY,
			location='preview',
			clear=True
		)
		self.referenceGlyphLayer = self.container.appendBaseSublayer()

		self.anchorLayer = self.container.appendPathSublayer(
			fillColor= (0,.2,1,.2),
		)
		self.previewGlyphLayer = self.previewContainer.appendPathSublayer()
		self.matchingGlyphAnchors = self.getMatchingAnchors()
		
	def destroy(self):
		self.container.clearSublayers()
		self.previewContainer.clearSublayers()
						
	def getMatchingAnchors(self):
		anchorPreviewTextField = self.controller.w.getItemValue("anchorPreviewTextField")
		currentGlyph = CurrentGlyph()
		matchingGlyphs = {}
		font = CurrentFont()
		
		def previewMatchingAnchor(glyphList):
			
			for glyphName in glyphList:
				if glyphName in font :
					glyph = currentGlyph.font[glyphName]
					for previewAnchor in glyph.anchors:
						if previewAnchor.name == matchingAnchor:
							matchingAnchors[glyph] = (previewAnchor.x, previewAnchor.y)
			
		if currentGlyph is None:
			return
		
		for anchor in currentGlyph.anchors:
			if not anchor.name:
				continue
			matchingAnchors = {}
			if anchor.name.startswith("_"):
				matchingAnchor = anchor.name.split('_')[1]
			else:
				matchingAnchor = f"_{anchor.name}"
			
			if anchorPreviewTextField != '' and anchorPreviewTextField in currentGlyph.font:
				glyph = currentGlyph.font[anchorPreviewTextField]
				for previewAnchor in glyph.anchors:
					if previewAnchor.name == matchingAnchor:
						matchingAnchors[glyph] = (previewAnchor.x, previewAnchor.y)
						
			## SPECIAL PREVIEW CASES
			elif anchor.name == "top" and currentGlyph.name in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "Alpha.LATN", "AE", "Bhook", "Cstroke", "Dhook", "Dafrican", "Dcroat", "Eth", "Dstroke", "Ereversed", "Schwa", "Eopen", "Fhook", "Gstroke", "Scriptg", "Hbar", "Hhook", "Iogonek", "Istroke", "Ismall", "Iota.LATN", "Jstroke", "Khook", "Nhookleft", "Eng", "Eng.locl", "OE", "Phook", "Thorn", "Ohorn", "Oslash", "Obar", "Oopen", "Rstroke", "Rtail", "yr", "Twithdiagonalstroke", "Thook", "Tretroflexhook", "Theta.LATN", "Ubar", "Uhorn", "Ustroke", "Vhook", "Upsilon.LATN", "Vturned", "Whook", "Yhook", "Yturnedsans", "Chi.LATN", "Zstroke", "Ezh", "Gamma.LATN", "Glottalstop", "Esh", "Pstroke", "Hturned", "Jcrossedtail"]:
				previewMatchingAnchor(
					glyphList = ["dotaccent.cap", "circumflex.cap"]
					)

			elif anchor.name == "top":
				previewMatchingAnchor(
					glyphList = ["dotaccentcmb", "circumflexcmb"]
					)
					
			elif anchor.name == "bottom":
				previewMatchingAnchor(
					glyphList =  ["macronbelowcmb", "dotbelowcmb"]
					)

			elif anchor.name == "topRight" and currentGlyph.name not in ["O", "o"]:
				previewMatchingAnchor(
					glyphList = ["caroncmb.slovak"]
					)

			elif anchor.name == "_middle" :
				previewMatchingAnchor(
					glyphList = ["T", "o"]
					)

			elif anchor.name == "middle" :
				previewMatchingAnchor(
					glyphList = ["overlaystrokeshortcmb"]
					)

							
			elif "slovak" in currentGlyph.name:
				previewMatchingAnchor(
					glyphList = ["d", "l", "t"]
					)

			elif "horn" in currentGlyph.name:
				previewMatchingAnchor(
					glyphList = ["O", "o", "U", "u"]
					)

			elif "dotrightabove" in currentGlyph.name:
				previewMatchingAnchor(
					glyphList = ["O", "o"]
					)

			elif "ogonek" in currentGlyph.name:
				previewMatchingAnchor(
					glyphList = ["I", "a", "E", "e"]
					)
		
			elif "cmb" in currentGlyph.name and (anchor.name == "_bottom" or "_top"):
				previewMatchingAnchor(
					glyphList = ["a", "n", "o"]
					)

			elif ".cap" in currentGlyph.name and (anchor.name == "_bottom" or "_top"):
				previewMatchingAnchor(
					glyphList = ["A", "H", "O"]
					)

			else:
				i = 0
				for glyphName in currentGlyph.font.glyphOrder:
					glyph = currentGlyph.font[glyphName]
					if glyph.name == currentGlyph.name: # Removed: "if glyph.components or …" // Condition that would mean "it is skipped"
						continue
					for previewAnchor in glyph.anchors: # For each of the glyph anchors (look for anchors through the whole font)
						if i > 3:	# If there are more than three glyphs with matching anchors, one way or the other, stop then
							break
						try:
							if previewAnchor.name == matchingAnchor:
								matchingAnchors[glyph] = (previewAnchor.x, previewAnchor.y)
								i += 1 # Will show 3(+0) characters
						except Exception as e:
							print(f"Something wrong with {glyphName}: {e}")
			matchingGlyphs[anchor.name] = matchingAnchors
	
		return matchingGlyphs

	def getMatchingComponents(self, currentGlyphName):
		font = CurrentFont()
		matchingComponents = ""

		for glyph in font:
			for component in glyph.components:
				if component.baseGlyph == currentGlyphName:
					matchingComponents += f"/{glyph.name}"

		return matchingComponents
		
	def drawAnchorPreview(self):
		self.anchorLayer.clearSublayers()
		glyph = CurrentGlyph()
		for anchor in glyph.anchors:
			if self.matchingGlyphAnchors:
				matchingGlyphs = self.matchingGlyphAnchors[anchor.name]
				for matchingGlyph in matchingGlyphs:
					previewAnchorPos = matchingGlyphs[matchingGlyph]
					glyphLayer = self.anchorLayer.appendPathSublayer(
						fillColor=(1,.2,0,.2),
						position=(anchor.x - previewAnchorPos[0], anchor.y - previewAnchorPos[1]) 	
					)
					glyphPath = matchingGlyph.getRepresentation("merz.CGPath")
					glyphLayer.setPath(glyphPath)

	def drawPreviewAnchorPreview(self):
		self.previewGlyphLayer.clearSublayers()
		isDarkMode = inDarkMode()
		glyph = CurrentGlyph()

		for anchor in glyph.anchors:
			if self.matchingGlyphAnchors:
				matchingGlyphs = self.matchingGlyphAnchors[anchor.name]
				for matchingGlyph in matchingGlyphs:
					previewAnchorPos = matchingGlyphs[matchingGlyph]
					glyphLayer = self.previewGlyphLayer.appendPathSublayer(
						fillColor=(isDarkMode, isDarkMode, isDarkMode, 1),
						position=(anchor.x - previewAnchorPos[0], anchor.y - previewAnchorPos[1]) 	
					)
					glyphPath = matchingGlyph.getRepresentation("merz.CGPath")
					glyphLayer.setPath(glyphPath)
	
	def drawAll(self):
		doDrawAnchors = self.controller.w.getItemValue("anchorPreviewCheckbox")

		self.matchingGlyphAnchors = self.getMatchingAnchors()

		if doDrawAnchors:
			if self.isPreview == False:
				self.drawAnchorPreview()
			else:
				self.drawPreviewAnchorPreview()
		else:
			self.anchorLayer.clearSublayers()

	def setSpaceCenterPreview(self):
		glyph = CurrentGlyph()
		doDrawSpaceCenter = self.controller.w.getItemValue("spaceCenterPreviewCheckbox")
		sp = CurrentSpaceCenter(currentFontOnly=True)

		if doDrawSpaceCenter:
			text = self.getMatchingComponents(glyph.name)
			sp.setRaw(text)
		
	def glyphEditorDidSetGlyph(self, info):
		self.drawAll()
		self.setSpaceCenterPreview()
		
	def OmniLatinToolDidChange(self, info):  	
		self.drawAll()
		self.setSpaceCenterPreview()

	def glyphDidChange(self, info):
		if self.controller.w.getItemValue("anchorPreviewCheckbox"):
			self.drawAll()

	def glyphEditorWillShowPreview(self, info):
		self.isPreview = True
		self.drawAll()

	def glyphEditorWillHidePreview(self, info):
		self.isPreview = False
		self.drawAll()


toolWidth = 250

class OmniLatinToolInterface(ezui.WindowController):

	def build(self):
		content = """
		!§ GENERAL
		* VerticalStack @topStack
		> * TwoColumnForm @form
		>> : Apply to:
		>> ( ) All Glyphs	@whichGlyphsOptionButtons
		>> ( ) Selected Glyphs
		>> (X) Current Glyph
		> [ ] Overwrite Anchors / Components	@overwriteCheckbox
		> ---
		
		* Accordion: CHARACTER SET @charsetAccordion
		> (Add OmniLatin Glyphset)	@addGlyphsetButton
		---
		
		* Accordion: BASE LETTERS & DIACRITICS @baseAccordion
		> (Prebuild Characters)	@buildSpecialCharButton
		> Scale Ratio for Ordinals: [_0.60_]	@scaleRatioOrdinalTextfield
		> (Paste Components)	@addComponentsButton
		> (Center Glyphs)	@centerGlyphButton
		> (Fix Diacritics Sidebearings) 	@fixDiacriticsWidthButton
		> Modifiers Sidebearings: [_50_]	@diacriticsWidthField
		---

		* Accordion: ANCHORS & PREVIEW	@anchorsAccorion
		> (Remove Anchors)	@removeAnchorsButton
		> * HorizontalStack
		>> (Autoplace Anchors)	@placeAnchorsButton
		>> ({gear})  	@anchorPlacementsButton
		> (Get Anchors from Base Glyphs)	@getBaseGlyphAnchorsButton
		> * HorizontalStack
		>> [ ] Anchor Preview (Glyph View)   @anchorPreviewCheckbox
		> Anchor Preview Glyph: [_ _]	@anchorPreviewTextField
		> [ ] Component Preview (Space Center)   @spaceCenterPreviewCheckbox
		---

		* Accordion: ACCENTED CHARACTERS	@accentedAccordion
		> (Build Accented Characters)	@buildAccentedGlyphsButton
		> (Build Characters from Alternate)	@buildAlternatesGlyphsButton
		---

		* Accordion: ENCODING & FEATURES   @generateAccordion
		> (Fix Unicodes)	@fixUnicodeButton
		> (Generate Features)	@markFeaturesButton
		> !* ! Check Features panel before generating again
		
		"""

		descriptionData=dict(
			charsetAccordion=dict(
				closed=True,
			),
			baseAccordion=dict(
				closed=True,
			),
			anchorsAccorion=dict(
				closed=True,
			),
			accentedAccordion=dict(
				closed=True,
			),
			generateAccordion=dict(
				closed=True,
			),
			topStack=dict(
				height=100
			),
			buildSpecialCharButton=dict(
				width=toolWidth,
			),
			addComponentsButton=dict(
				width=toolWidth,
			),
			centerGlyphButton=dict(
				width=toolWidth,
			),
			fixDiacriticsWidthButton=dict(
				width=toolWidth,
			),
			diacriticsWidthField=dict(
				#width=toolWidth-120,
				valueType="number",
			),
			placeAnchorsButton=dict(
				width=toolWidth-30,
			),
			getBaseGlyphAnchorsButton=dict(
				width=toolWidth,
			),
			addGlyphsetButton=dict(
				width=toolWidth,
			),
			removeAnchorsButton=dict(
				width=toolWidth,
			),
			fixUnicodeButton=dict(
				width=toolWidth,
			),
			buildAccentedGlyphsButton=dict(
				width=toolWidth,
			),
			buildAlternatesGlyphsButton=dict(
				width=toolWidth,
			),
			markFeaturesButton=dict(
				width=toolWidth,
			),
			LOCLFeaturesButton=dict(
				width=toolWidth,
			),
		)
		self.w = ezui.EZPanel(
			title="OmniLatin Tool",
			content=content,
			descriptionData=descriptionData,
			controller=self
		)
		#self.w.getItem("anchorPreviewTextField").enable(False)

	def started(self):
		self.accentPlacements = getExtensionDefault(f"{DEFAULT_KEY}.accentPlacements", fallback=standardAccentPlacements)
		self.verticalAccentPlacements = getExtensionDefault(f"{DEFAULT_KEY}.verticalAccentPlacements", fallback=standardVerticalAccentPlacements)
		drawReferenceGlyphs.controller = self
		registerGlyphEditorSubscriber(drawReferenceGlyphs)
		self.w.open()

	def destroy(self):
		setExtensionDefault(f"{DEFAULT_KEY}.accentPlacements", self.accentPlacements)
		setExtensionDefault(f"{DEFAULT_KEY}.verticalAccentPlacements", self.verticalAccentPlacements)
		unregisterGlyphEditorSubscriber(drawReferenceGlyphs)
		drawReferenceGlyphs.controller = None

	def spaceCenterPreviewCheckboxCallback(self, sender):
		if sender.get():
			sp = CurrentSpaceCenter(currentFontOnly=True)
			if sp is None:
				sp = OpenSpaceCenter(CurrentFont())

		postEvent(eventName)

	def addGlyphsetButtonCallback(self, sender):
		glyphsetName = "OmniLatin glyphset"
		chosenGlyphset = OmniLatin
		
		addChosenGlyphset(chosenGlyphset)
		print(glyphsetName + " has been added")
	

	def buildSpecialCharButtonCallback(self, sender):
		self.currentFont = CurrentFont()
		glyphSet = self.getWhichGlyphs()
		doOverwrite = self.w.getItemValue("overwriteCheckbox")
		charactersBuilt = ""
		scaleRatio = float(self.w.getItemValue("scaleRatioOrdinalTextfield")) or 0.6
		# Deactivated here because the value is not update wit the textfield

		for glyphName in glyphSet:
			if glyphName in specialChars:
				glyph = self.currentFont[glyphName]
				if not doOverwrite and glyph.bounds:
					continue

				with glyph.undo("Build Glyph"):
					glyph.clear()

					specialCharData = specialChars[glyphName]
					for buildBlock in specialCharData:
						if 'scale' in buildBlock:
							if buildBlock['scale'] == 'xHeight':
								scaled = self.currentFont.info.xHeight / self.currentFont.info.capHeight
								buildBlock['scale'] = scaled
							elif buildBlock['scale'] == 'capHeight':
								scaled = self.currentFont.info.capHeight / self.currentFont.info.xHeight 
								buildBlock['scale'] = scaled
							elif buildBlock['scale'] == 'scaleRatio':
								scaled = 43 
								buildBlock['scale'] = scaled

						if 'translate' in buildBlock:
							x, y = buildBlock['translate']
							
							capValue = (self.currentFont.info.capHeight - self.currentFont.info.xHeight)/2
							capAccents = self.currentFont.info.capHeight - self.currentFont.info.xHeight
							
							for i, move in enumerate(buildBlock['translate']):
								
								
								
								if move == 'capHeight':
									if i == 0:
										x = self.currentFont.info.capHeight
									if i == 1:
										y = self.currentFont.info.capHeight
								if move == 'xHeight':
									if i == 0:
										x = self.currentFont.info.xHeight
									if i == 1:
										y = self.currentFont.info.xHeight
								if move == 'descender':
									if i == 0:
										x = self.currentFont.info.descender
									if i == 1:
										y = self.currentFont.info.descender
								if move == 'capValue':
									if i == 0:
										x = capValue
									if i == 1:
										y = capValue
								if move == 'capAccents':
									if i == 0:
										x = capAccents
									if i == 1:
										y = capAccents
								if move == 'ordinalHeight':
									if i == 0:
										x = round(self.currentFont.info.ascender - self.currentFont.info.ascender*scaleRatio)
									if i == 1:
										y = round(self.currentFont.info.ascender - self.currentFont.info.ascender*scaleRatio)

							buildBlock['translate'] = (x, y)
						import traceback
						try:
							self.buildSpecialChar(glyph, **buildBlock)
						except Exception as e:
							print(f"Mistake in the specialChars_recipe: {e}")

					glyph.markColor = (1,0,0,.4)
					charactersBuilt += glyphName + ", "

		print(f"OmniLatin Tool pre-built characters: {charactersBuilt}")


	def buildSpecialChar(self, mainGlyph, glyphName=None, decompose=True, rotate=0, scale=(1, 1), translate=(0, 0), fallback=None, addWidth=False):
		glyph = None
	
	# new contour = the component (Rcomponent)
	# main glyph = "new" character (Rglyph)

		if glyphName in self.currentFont:
			glyph = self.currentFont[glyphName]
		elif fallback is not None:
			for i, fallbackGlyphName in enumerate(fallback):
				if glyph is not None:
					continue
				elif fallbackGlyphName in self.currentFont:
					glyph = self.currentFont[fallbackGlyphName]

		if glyph is None or glyph.bounds == None:
			return

		xMin, yMin, xMax, yMax = glyph.bounds
		centerPoint = (xMin + (xMax - xMin)/2, yMin + (yMax - yMin)/2)

		if not mainGlyph.bounds:
			mainGlyph.leftMargin = glyph.leftMargin
			mainGlyph.width = glyph.width

		newContour = mainGlyph.appendComponent(glyph.name)

		if addWidth:
			newContour.moveBy((mainGlyph.width, 0))
			mainGlyph.width += glyph.width
			
		# Other transformations
		newContour.rotateBy(rotate, centerPoint)
		

		if scale:
			if scale == 43: # Default ordinal value - random unlikely value	/ Needs to be a float/int/tuple / defined in buildSpecialCharButtonCallback
				scale = float(self.w.getItemValue("scaleRatioOrdinalTextfield")) 
				# Refresh the value / Gets it from the scaleRatioOrdinalTextfield
				mainGlyph.angledLeftMargin = glyph.angledLeftMargin*scale
				mainGlyph.angledRightMargin = glyph.angledRightMargin*scale	
			newContour.scaleBy(scale, (centerPoint[0], 0))
			newContour.moveBy((translate))
			
		else:
			newContour.moveBy((translate))
		

		if decompose:
			newContour.decompose()
			# if scale[0] < 0:
			# 	conto.reverse()

	def refenceGlyphPointsCheckboxCallback(self, sender):
		postEvent(eventName)

	def referenceGlyphTextFieldCallback(self, sender):
		postEvent(eventName)
	
	def addComponentsButtonCallback(self, sender):
		font = CurrentFont()
		doOverwrite = self.w.getItemValue("overwriteCheckbox")
		glyphSet = self.getWhichGlyphs()
		addComponentMarkColor = (0,0,1,.3)

		for glyphName in glyphSet:
			if glyphName in definedGlyphset:
				glyphData = definedGlyphset[glyphName]
				glyph = font[glyphName]
				
				if (glyph.components and not doOverwrite) or glyph.contours or ('accents' in glyphData) : # won't erase decomposed glyphs
					continue
				
				with glyph.undo("Place Component(s)"):

					if 'baseGlyphs' in glyphData: # and glyph.bounds == None:
						glyph.clearComponents()
						glyphWidth = 0
						for baseGlyphName in glyphData['baseGlyphs']:
							newCompo = glyph.appendComponent(baseGlyphName)
							newCompo.moveBy((glyphWidth, 0))
							
							# if not glyph.markColor == (1, .3, 0, .5):
							glyph.markColor = addComponentMarkColor
						
							if baseGlyphName in font:
								baseGlyph = font[baseGlyphName]
								glyphWidth += baseGlyph.width

						glyph.width = glyphWidth
							
					# if 'accents' in glyphData:
# 						for accent in glyphData['accents']:
# 							accentData = accent.split('@')
# 
# 							if len(accentData) > 1:
# 								accentName, accentPosition = accentData
# 								glyph.appendComponent(accentName)
# 							else:
# 								glyph.appendComponent(accent)
# 
# 							glyph.markColor = addComponentMarkColor

		print(f"OmniLatin Tool: added components")

	def anchorPlacementsButtonCallback(self, sender):
		AnchorSheetController(parentController=self)
									
	def placeAnchorsButtonCallback(self, sender):
		font = CurrentFont()
		doOverwrite = self.w.getItemValue("overwriteCheckbox")
		glyphSet = self.getWhichGlyphs()
		
		for glyphName in glyphSet:
			if glyphName in definedGlyphset:
				glyphData = definedGlyphset[glyphName]
				if "anchors" in glyphData:
					glyph = font[glyphName]
					
					if not glyph.bounds:	# Empty glyphs don't get anchors
						continue

					try:
						with glyph.undo("Place Anchors"):						
							existingAnchors = {}
							for existingAnchor in glyph.anchors:
								existingAnchors[existingAnchor.name] = existingAnchor
						
							for anchorName in glyphData["anchors"]:
								if anchorName in existingAnchors:
									if not doOverwrite:
										continue
									else:
										glyph.removeAnchor(existingAnchors[anchorName])
										anchorPosition = self.getAnchorPosition(glyph, anchorName)
										glyph.appendAnchor(anchorName, anchorPosition)
								else:
									anchorPosition = self.getAnchorPosition(glyph, anchorName)
									glyph.appendAnchor(anchorName, anchorPosition)
					except Exception as e:
						print(f"Something wrong with dictionary data for: {glyphName}")

		print(f"OmniLatin Tool: added anchors")

	def removeAnchorsButtonCallback(self, sender):
		font = CurrentFont()
		glyphSet = self.getWhichGlyphs()
		
		for glyphName in glyphSet:# 
			glyph = font[glyphName]
			with glyph.undo("Remove Anchors"):
				for anchor in glyph.anchors:
					glyph.removeAnchor(anchor)
				print(f"OmniLatin Tool: anchors removed from", glyph.name)

		

	def buildAccentedGlyphsButtonCallback(self, sender):
		font = CurrentFont()
		doOverwrite = self.w.getItemValue("overwriteCheckbox")
		glyphSet = self.getWhichGlyphs()
		
		# Build accented glyphs for KNOWN glyphs (not alternates like "R.alt").
		for glyphName in glyphSet:
			if glyphName in definedGlyphset:
				
				createAndFillComposedGlyph(
					font = font,
					overwrite = doOverwrite,
					glyphName = glyphName,
					categoryMarkColor = (0, .5, 1, .3),
				)
				
		print(f"OmniLatin Tool: built accented glyphs")
	
	
	def buildAlternatesGlyphsButtonCallback(self, sender):
		font = CurrentFont()
		doOverwrite = self.w.getItemValue("overwriteCheckbox")
		glyphSet = self.getWhichGlyphs()
		# Build accented glyphs for ALTERNATE glyphs (ex: "R.alt").
		for glyphName in glyphSet:
			if glyphName not in definedGlyphset:
				
				# Note: at the moment, this function will use the accent components/glyphs
				# specified in the accented glyph database. In the future, a potential 
				# improvement could be checking if there's a version of that accent with
				# the same suffix (ex: ".alt"), and using that for the component instead.
				#
				# need to know the non-alternate accented glyph names (ex: "Racute")
				# then we can look up the glyph data for it
				
				
				# Get a list of the glyph names for all accented versions of this glyph.
				# Each item in the list is a tuple containing both the alternate and
				# non-alternate glyph names. Example below:
				# [
				# 	('Racute.alt', 'Racute'),
				# 	('Rcaron.alt', "Rcaron"),
				# 	('Oslash.alt', "Oslash"),
				# ]
				accentedAlternateGlyphNames = determineAccentedAlternateGlyphNamesFor( glyphName )
				
				# Do another pass, in case there are additional derivatives of these accented glyphs.
				# Example:
				# O > Oslash > Oslashacute
				# O.alt > Oslash.alt > Oslashacute.alt
				
				# Create an empty list to fill with additional glyph name tuples like those above.
				additionsTwoLevelsDeep = []
				# Go through each of the accented alternate glyph names, and check if it should
				# be used as a component for an accented glyph (ex: Oslashacute.alt).
				for accentedAltGlyphName, _ in accentedAlternateGlyphNames :
					additionsForThisGlyph = determineAccentedAlternateGlyphNamesFor( accentedAltGlyphName )
					additionsTwoLevelsDeep += additionsForThisGlyph
				# Add these additional glyph tuples to those from the first pass
				accentedAlternateGlyphNames += additionsTwoLevelsDeep
				
				# Create each of the accented alternate glyphs, filled with components.
				for thisAccentedAlternateGlyphName, thisAccentedGlyphName in accentedAlternateGlyphNames :
					
					createAndFillComposedGlyph(
						font = font,
						overwrite = doOverwrite,
						glyphName = thisAccentedAlternateGlyphName,
						nameOfGlyphToGetAccentsFrom = thisAccentedGlyphName,
						categoryMarkColor = (1, 0.4 , 0.8, 0.5),
					)
					#glyph.markColor = (1, 0.4 , 0.8, 0.5)
				
				# Check if the glyph is empty. If not, and if not allowed to overwrite,
				# continue/skip this glyph and move on to the next.
				# if glyph.bounds and not doOverwrite:
# 					continue
		
		print(f"OmniLatin Tool: built alternate glyphs")
		
		
			
	def getBaseGlyphAnchorsButtonCallback(self, sender):	# Check contour/component behavior
		font = CurrentFont()
		glyphSet = self.getWhichGlyphs()
		
		for glyphName in glyphSet:
			if glyphName in definedGlyphset:
				glyphData = definedGlyphset[glyphName]
				glyph = font[glyphName]
				
				if not glyph.bounds:
					continue
				
				if 'baseGlyphs' in glyphData and 'anchors' in glyphData:
					anchorsToAppend = {}
					
					for anchor in glyphData["anchors"]:

						baseGlyphName = glyphData["baseGlyphs"][0]
						baseGlyph = font[baseGlyphName]
						for component in glyph.components:
							if component.baseGlyph == baseGlyphName:
								offset = component.offset
								for baseGlyphAnchor in baseGlyph.anchors:
									if baseGlyphAnchor.name == anchor:
										baseGlyphAnchorPos = baseGlyphAnchor.position
										anchorPos = (baseGlyphAnchorPos[0] + offset[0], baseGlyphAnchorPos[1] + offset[1])
										anchorsToAppend[anchor] = anchorPos

					if anchorsToAppend:
						glyph.clearAnchors()
						for anchor in anchorsToAppend:
							glyph.appendAnchor(anchor, anchorsToAppend[anchor])

		print(f"OmniLatin Tool: get anchors from base glyphs")

	def convertedVerticalAccentPlacementsList(self):
		font = CurrentFont()
		verticalAccentPlacements = []

		for item in self.verticalAccentPlacements:
			if item == 'descender':
				verticalAccentPlacements.append(font.info.descender)
			elif item == 'xHeight':
				verticalAccentPlacements.append(font.info.xHeight)
			elif item == 'capHeight':
				verticalAccentPlacements.append(font.info.capHeight)
			elif item == 'ascender':
				verticalAccentPlacements.append(font.info.ascender)
			else:
				try:
					itemAsFloat = float(item)
				except Exception as e:
					itemAsFloat = 0
				verticalAccentPlacements.append(itemAsFloat)

		return verticalAccentPlacements

	def getAnchorPosition(self, glyph, anchor):
		font = CurrentFont()
		italicSlantOffset = font.lib["com.typemytype.robofont.italicSlantOffset"] or 0

		xPosition, yPosition = 0, 0
		xMin, yMin, xMax, yMax = glyph.bounds
		verticalAccentPlacements = self.convertedVerticalAccentPlacementsList()
		
		for standardAccent in self.accentPlacements:
			if anchor == standardAccent["name"]:
				horizontalPlacement = standardAccent['horizontal']
				verticalPlacement = standardAccent['vertical']

				if standardAccent['point'] is True:
					if glyph.components:
						tempGlyph = RGlyph()
						tempPen = tempGlyph.getPointPen()
						decomposePen = DecomposePointPen(font, tempPen)
						glyph.drawPoints(decomposePen)
						glyph = tempGlyph

					allPoints = []
					for contour in glyph.contours:
						for point in contour.points:
							if point.type == "offcurve":
								continue
							allPoints.append(point.position)
					
					if allPoints:
						xPoint = yPoint = 0
						if verticalPlacement == 0:
							yPoint = yMax
						if verticalPlacement == 1:
							yPoint = (yMin + yMax) / 2
						if verticalPlacement == 2:
							yPoint = yMin
							
						if horizontalPlacement == 0:
							xPoint = xMin
						if horizontalPlacement == 1:
							xPoint = (xMin + xMax) / 2
						if horizontalPlacement == 2:
							xPoint = xMax
						
						xNew, yNew = min(allPoints, key=lambda point: abs(point[0] - xPoint) + abs(point[1] - yPoint))
						xPosition += xNew
						xPosition += yNew
				
				else:
					if verticalPlacement == 0:
						closest = 1000
						for line in verticalAccentPlacements:
							if abs(line-yMax) < closest:
								closest = abs(line-yMax)
								yPosition = line
					elif verticalPlacement == 1:
						yPosition = (yMax - yMin)/2
					elif verticalPlacement == 2:
						closest = 1000
						for line in verticalAccentPlacements:
							if abs(line-yMin) < closest:
								closest = abs(line-yMin)
								yPosition = line  	
					yPosition += standardAccent["extraY"]
					italicOffset = yPosition * math.tan(math.radians(-(font.info.italicAngle or 0))) + italicSlantOffset  						
					if horizontalPlacement == 0:
						xPosition = xMin  + italicOffset
					if horizontalPlacement == 1:
						xPosition = glyph.width / 2 + italicOffset
					elif horizontalPlacement == 2:
						xPosition = xMax  + italicOffset
					xPosition += standardAccent["extraX"]

		return xPosition, yPosition
	
	def anchorPreviewCheckboxCallback(self, sender):
		self.w.getItem("anchorPreviewTextField").enable(sender.get())
		postEvent(eventName)
		
	def anchorPreviewTextFieldCallback(self, sender):
		postEvent(eventName)
		
	def centerGlyphButtonCallback(self, sender):
		glyphSet = self.getWhichGlyphs()
		font = CurrentFont()
		
		for glyphName in glyphSet:
			if glyphName in font.lib["public.glyphOrder"]:
				glyph = font[glyphName]
				if glyph.bounds:
					with glyph.undo("Center Glyph"):
						glyphWidth = glyph.width
						contourWidth = glyph.width - (glyph.angledLeftMargin + glyph.angledRightMargin)
						
						glyph.angledLeftMargin = (glyph.width - contourWidth)/2
						glyph.angledRightMargin = (glyph.width - contourWidth)/2
						glyph.width = glyphWidth
		
		print(f"OmniTool: Glyph(s) centered")
		
	def fixDiacriticsWidthButtonCallback(self, sender):
		font = CurrentFont()
		glyphSet = self.getWhichGlyphs()
		sidebearingValue = self.w.getItemValue("diacriticsWidthField")

		for glyphName in glyphSet:
			if glyphName in definedGlyphset and glyphName in font.lib["public.glyphOrder"]:
				glyph = font[glyphName]
				if 'isAccent' in definedGlyphset[glyphName] and definedGlyphset[glyphName]['isAccent'] is True:
					with glyph.undo("Fix Width"):
						if 'cmb' in glyphName or 'cap' in glyphName:
							if font.info.italicAngle != None :
								# Add a positive angle to 90º. Trigonometry considers
								# an italic angle -6º (right-leaning) to be 84º.
								slantAngle = font.info.italicAngle + 90
								for anchor in glyph.anchors:
									if anchor.name == "_top" or anchor.name == "_bottom":
										opposite = anchor.y
										# Use trigonometry to figure out how much to move
										# in the X direction, if there's a slant angle.
										
										#			⁄|
										#		  ⁄  |
										#		⁄	 | Opposite
										#	  ⁄      |
										# Xº ————————·
										#	 Adjacent
										# Trigonometry works with radians rather than degrees, so convert
										slantAngleInRadians = slantAngle * math.pi / 180
										tangent = math.tan( slantAngleInRadians )
										# Adjacent = Reference "0" value on Italic angle axis
										adjacent = int(opposite / tangent)
										# If anchor.x != adjacent, then needs to be moved by the difference
										howMuchToMoveBy_x = adjacent - anchor.x
										glyph.moveBy((howMuchToMoveBy_x, 0))
							else:
								for anchor in glyph.anchors:
									if anchor.name in ("_top",  "_bottom"):
										if anchor.x != 0:
											moveByXValue = int(anchor.x)
											glyph.moveBy((-moveByXValue, 0))
							glyph.width = 0
						else:
							glyph.angledLeftMargin = sidebearingValue
							glyph.angledRightMargin = sidebearingValue
		print(f"OmniLatin Tool: Fixed diacritics width")
		
	def fixUnicodeButtonCallback(self, sender):
		font = CurrentFont()
		glyphSet = self.getWhichGlyphs()
			
		numberOfGlyphsWithUnicodesAdded = 0
		for glyphName in glyphSet:
			# Get info about this glyph from the available dictionary/dictionaries
			glyphInfo = definedGlyphset.get(glyphName)
			if glyphInfo :
				# If the glyph dict has unicode values, and this glyph name is in the font:
				if 'unicode' in glyphInfo and glyphName in font.lib["public.glyphOrder"]:
					glyph = font[glyphName]
					existingUnicodes = glyph.unicodes
					expectedUnicodes = glyphInfo["unicode"]
					glyphHadNoUnicodes = len(existingUnicodes) == 0
					
					# Determine which unicodes need to be added
					unicodesToAdd = list( set(expectedUnicodes).difference(set(existingUnicodes)) )
					# Determine which unicodes other than the expected ones were already on the glyph.
					# These might be fine, or they might need to be removed.
					otherExistingUnicodes = list( set(existingUnicodes).difference(set(expectedUnicodes)) )
					
					if unicodesToAdd :
						# Set the expected/correct unicodes for this glyph. If it had other unicodes before, they
						# will be preserved *after* the expected unicodes. They may be removed in the next step.
						glyph.unicodes = expectedUnicodes + otherExistingUnicodes
						numberOfGlyphsWithUnicodesAdded += 1
					
					# Check if other glyphs have any of the unicode values expected for this glyph.
					# If they do, remove the unicode values so that only this glyph uses them.
					# From the font, get a dict with int Unicode value keys and list of glyph name values.
					characterMap = font.getCharacterMapping()
					for thisUnicode in expectedUnicodes :
						glyphsUsingThisUnicode = characterMap.get( thisUnicode ) or []
						# Remove this glyph name from the list (if necessary)
						if glyphName in glyphsUsingThisUnicode :
							glyphsUsingThisUnicode.remove( glyphName )
						# If there are other glyphs using this unicode, remove it from them.
						for nameOfIncorrectGlyph in glyphsUsingThisUnicode:
							correctedUnicodes = list(font[nameOfIncorrectGlyph].unicodes)
							correctedUnicodes.remove(thisUnicode)
							font[nameOfIncorrectGlyph].unicodes = correctedUnicodes
							# Print a note about this removal
							unicodeHexValue = hex(thisUnicode)[2:].zfill(4).upper()
							print( f"{unicodeHexValue} was removed from {nameOfIncorrectGlyph}" )
		
		print(f"OmniLatin Tool: fix unicode  -  added Unicode values to {numberOfGlyphsWithUnicodesAdded} glyphs")
	
	def markFeaturesButtonCallback(self, sender):
		marksGroupName = "COMBINING_MARKS"
		font = CurrentFont()

		if font is None:
			print("No current font open. Unable to generate mark features.")
			return
		
		print("Generating ccmp feature...")
		try:
		    # Call the generate_and_write_ccmp function from the ccmp_generator module
		    generate_ccmp_feature(font)
    
		    print("ccmp feature generated successfully.")

		except Exception as e:
		    # Catch-all for any other exceptions
		    print(f"An error occurred while generating the ccmp feature: {e}")
		
		if marksGroupName in font.groups:
		    if not font.groups[marksGroupName]:
		        # If it's empty, remove it
		        del font.groups[marksGroupName]
		        print(f"Removed empty group '{marksGroupName}' from font.groups.")
		
		if not marksGroupName in font.groups:
			print(f"OmniLatin Tool: Adding new group called '{marksGroupName}'")
			combiningAccents = []
			for glyph in font:
				if glyph.name in definedGlyphset:
					if "isAccent" in definedGlyphset[glyph.name] and definedGlyphset[glyph.name]["isAccent"]:
#						if "cmb" in glyph.name or "comb" in glyph.name:
						if glyph.width == 0:
							combiningAccents.append(glyph.name)

			groups = font.groups
			groups[marksGroupName] = combiningAccents
			font.save()

		try:
		    add_ss20_locl_feature(font)
    
		    print("locl feature generated successfully.")

		except Exception as e:
		    # Catch-all for any other exceptions
		    print(f"An error occurred while generating the locl feature: {e}")

		# Check if COMBINING_MARKS is not empty
		if marksGroupName in font.groups and font.groups[marksGroupName]:
			fontPath = font.path
			if fontPath is None:
				print("Please save the font before running this script.")
				return

			# Set up arguments for MarkFeatureWriter
			args = dict(
				input_file=fontPath,
				trim_tags=False,
				write_classes=False,
				write_mkmk=True,	# Set to True if you want mkmk.fea generated
				indic_format=False,
				mark_file='mark.fea',
				mkmk_file='mkmk.fea',
				mkclass_file='markclasses.fea',
				abvm_file='abvm.fea',
				blwm_file='blwm.fea',
				mkgrp_name=marksGroupName,
			)

			print("Generating mark feature files with MarkFeatureWriter...")
			try:
				MarkFeatureWriter(args)
				print("mark.fea and mkmk.fea have been exported to the UFO directory.")

				# Now append the feature code snippet into features.fea
				snippet = (
					"\n"
					"\nfeature mark {\n"
					"	 include (mark.fea);\n"
					"} mark;\n\n"
					"feature mkmk {\n"
					"	 include (mkmk.fea);\n"
					"} mkmk;\n"
					"\n"
					"#/!\ Delete this section before generating features again\n"
					"#                     + languagesystem at the very top\n"
					"# ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑  OMNILATIN TOOL FEATURES ADDITIONS  ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑\n"
					"# ---------------------------------------------------------------------------------------------\n"
				)

				currentFeatures = font.features.text or ""
				if "feature mark {" not in currentFeatures and "feature mkmk {" not in currentFeatures:
					# Append the snippet
					font.features.text = currentFeatures + snippet
					print("Mark and mkmk feature code appended to features.fea inside the UFO.")
				else:
					print("Mark and mkmk features already present in features.fea. No changes made.")

			except Exception as e:
				print(f"An error occurred while running MarkFeatureWriter: {e}")
		else:
			print("The 'COMBINING_MARKS' group does not exist or is empty.")

			
	def getWhichGlyphs(self):
		font = CurrentFont()
		glyphSet = []
		whichGlyphs = self.w.getItemValue("whichGlyphsOptionButtons")
		
		if whichGlyphs == 0:
			for glyphName in font.lib["public.glyphOrder"]:
				glyphSet.append(glyphName)
		elif whichGlyphs == 1:
			for glyphName in font.templateSelectedGlyphNames:
				glyphSet.append(glyphName)
		elif whichGlyphs == 2:
			if CurrentGlyph() is not None:
				glyphSet.append(CurrentGlyph().name)
		return glyphSet

class AnchorSheetController(ezui.WindowController):

	def build(self, parentController):
		self.parentController = parentController
		content = """
		= Tabs
		* Tab: Anchors @anchorTab
		> |   | @complexTable
		======================

		(Cancel) @cancelButton
		(OK) 	@okButton
		"""

		verticalPositions = " ".join(str(element) for element in parentController.verticalAccentPlacements)
		accentData = parentController.accentPlacements

		descriptionData = dict(
			complexTable=dict(
				items=accentData,
				columnDescriptions=[
					dict(
						identifier="name",
						title="Name",
						width=65,
						editable=True
					),
					dict(
						identifier="horizontal",
						title="Horizontal (X)",
						width=70,
						cellDescription=dict(
							cellType="PopUpButton",
							cellClassArguments=dict(
								items=["left", "center", "right", "0"]
							),
						),
						editable=True
					),
					dict(
						identifier="vertical",
						title="Vertical (Y)",
						width=70,
						cellDescription=dict(
							cellType="PopUpButton",
							cellClassArguments=dict(
								items=["top", "center", "bottom", "0"]
							),
						),
						editable=True
					),
					dict(
						identifier="extraX",
						title="Extra X",
						width=45,
						cellDescription=dict(
							cellType="TextField",
						),
						editable=True
					),
					dict(
						identifier="extraY",
						title="Extra Y",
						width=45,
						editable=True
					),
					dict(
						identifier="point",
						title="Point",
						cellDescription=dict(
							cellType="Checkbox",
						),
						width=35,
						editable=True
					),
				]
			)
		)
		self.w = ezui.EZSheet(
			size=(520, 330),
			content=content,
			descriptionData=descriptionData,
			parent=parentController.w,
			controller=self
		)

	def started(self):
		self.w.open()

	def printButtonCallback(self, sender):
		import pprint
		table = self.w.getItem("complexTable")
		print("complexTable items:")
		pprint.pprint(table.get())		

	def cancelButtonCallback(self, sender):
		self.w.close()

	def okButtonCallback(self, sender): 	

		tableItems = self.w.getItem("complexTable").get()

		for item in tableItems:
			if isinstance(item["extraX"], str):
				try:
					item["extraX"] = float(item["extraX"])
				except Exception as e:
					item["extraX"] = 0

			if isinstance(item["extraY"], str):
				try:
					item["extraY"] = float(item["extraY"])
				except Exception as e:
					item["extraY"] = 0

		self.parentController.accentPlacements = tableItems
		self.w.close()



DEFAULT_KEY = 'com.sharpType'
eventName = f"{DEFAULT_KEY}.changed"

registerSubscriberEvent(
	subscriberEventName=eventName,
	methodName="omniLatinToolDidChange",
	lowLevelEventNames=[eventName],
	dispatcher="roboFont",
	documentation="Send when the OmniLatin Tool did change parameters.",
	delay=0,
	debug=True
)

setExtensionDefault(f"{DEFAULT_KEY}.accentPlacements", standardAccentPlacements)

OmniLatinToolInterface()
