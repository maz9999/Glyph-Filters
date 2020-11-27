from NaNGFGraphikshared import *
import traceback
import GlyphsApp
from Foundation import NSClassFromString
from NaNGFSpacePartition import *

class NaNFilter:
    def __init__(self):
        self.font = Glyphs.font
        selectedGlyphs = beginFilterNaN(self.font)
        self.setup()
        for glyph in selectedGlyphs:
            self.processGlyph(glyph)
        endFilterNaN(self.font)

    def setup(self):
        pass

    def processGlyph(self, glyph):
        glyph.beginUndo()
        beginGlyphNaN(glyph)

        thislayer = self.font.glyphs[glyph.name].layers[0]
        thislayer.beginChanges()
        if hasattr(self, "params"):
            params = self.params[glyphSize(glyph)]
        else:
            params = None
        self.processLayer(thislayer, params)

        thislayer.endChanges()
        endGlyphNaN(glyph)
        glyph.endUndo()

    def processLayer(self, layer, params):
        raise NotImplementedError

    def doOffset(self, Layer, hoffset, voffset):
        try:
            offsetCurveFilter = NSClassFromString("GlyphsFilterOffsetCurve")
            offsetCurveFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_error_shadow_(
                Layer, hoffset, voffset, False, False, 0.5, None, None
            )
        except Exception as e:
            print "offset failed"

    def saveOffsetPaths(self, Layer, hoffset, voffset, removeOverlap):
        templayer = Layer.copy()
        templayer.name = "tempoutline"
        currentglyph = Layer.parent
        currentglyph.layers.append(templayer)
        tmplayer_id = templayer.layerId
        self.doOffset(templayer, hoffset, voffset)
        if removeOverlap:
            templayer.removeOverlap()
        offsetpaths = templayer.paths
        del currentglyph.layers[tmplayer_id]
        return offsetpaths

    def expandMonoline(self, Layer, noodleRadius):
        try:
            offsetCurveFilter = NSClassFromString("GlyphsFilterOffsetCurve")
            offsetCurveFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_error_shadow_( Layer, noodleRadius, noodleRadius, True, False, 0.5, None,None)
        except Exception as e:
            print( "expandMonoline: %s\n%s" % (str(e), traceback.format_exc()) )

    def SortCollageSpace(self, thislayer, outlinedata, outlinedata2, gridsize, bounds, action, randomize = False):
        isogrid = makeIsometricGrid(bounds, gridsize)
        if randomize:
            isogrid = RandomiseIsoPoints(isogrid, gridsize)
        alltriangles = IsoGridToTriangles(isogrid)

        # Return triangles within and without
        in_triangles, out_triangles = returnTriangleTypes(alltriangles, outlinedata)

        if action == "stick":
            edge_triangles = StickTrianglesToOutline(out_triangles, outlinedata)
            return TrianglesListToPaths(in_triangles + edge_triangles)
        elif action == "overlap":
            edge_triangles = ReturnOutlineOverlappingTriangles(out_triangles, outlinedata)
            # Just return the edges
            return TrianglesListToPaths(edge_triangles)
        else:
            raise NotImplementedError
