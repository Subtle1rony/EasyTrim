"""
Easy Trim by Eric Kimberly
version 0.0.1
Automates the process of extruding trim profiles along curves
Works around several common issues that happen when doing the
process by hand.
"""
import maya.api.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel
from operator import sub, add
import sys


class EasyTrim(object):

	def __init__(self):
		#suppress warnings that clutter output
		cmds.scriptEditorInfo(suppressWarnings=True)
		pass

	def easyExtrude(self):
		"""
		Core process to extrude a user defined profile curve along a selected edge
		In order for this to work the user must select continuous edges and then the 
		profile curve. Will not work otherwise. 
		"""
		#parse selected objects
		edges, profile = self.handleSelection()
		if edges is None or profile is None:
			return

		#create the path from list of selected edges
		path = self.createPath(edges)
		
		#extrude nurbs surface
		nurbsSurface = cmds.extrude(profile, path, 
						name = 'easyTrimSurface#', et=2, fpt=1, ucp=1, 
						upn=1, sc=1, ro=0, rsp=1 )[0]


		#tessellate trim
		polySurface = self.nurbsToPoly(nurbsSurface)

		#set normal angle
		cmds.polySoftEdge(polySurface, angle = 0)

		#determine normal orientation
		self.fixReversedNormals(path, polySurface, nurbsSurface)

		#fix the maya profile scale issue
		self.fixProfileScale(path, nurbsSurface)

		#clean outliner, hide surfaces
		#group new nodes. 
		group = cmds.group( path, nurbsSurface, polySurface, n='EasyTrim##' )
		sys.stdout.write("%s successfully created." % group)

	def handleSelection(self):
		"""
		Parse selection in Maya scene and separate path edges from profile curve
		"""
		selection = cmds.ls(sl = True)
		
		if selection == []:
			print "None"
			sys.stdout.write("Nothing selected. Select continuous poly edges, " 
							 "then the profile curve")
			return None, None

		#isolate edges from profile
		profile = selection[-1]
		cmds.select(profile, d = True)
		edges = cmds.ls(sl = True)

		print profile
		print edges

		cmds.select(cl = True)
		cmds.select(profile)

		#validate profile is a curve object
		profile = cmds.filterExpand( ex=True, sm=9 )
		if profile is None:
			sys.stdout.write("select continuous poly edges, then the profile curve")
			cmds.confirmDialog( title='Error in Selection', message='Profile curve not found.' + 
								' Make sure it is last in the selection.', 
								button=['Ok','Cancel'], defaultButton='Ok', 
								cancelButton='Cancel', dismissString='No' )
			cmds.select(selection)
			return None, None

		cmds.select(cl = True)
		cmds.select(edges)

		#validate edges are polygon edges
		edges = cmds.filterExpand( ex=True, sm=32 )
		if edges is None:
			sys.stdout.write("select continuous poly edges, then the profile curve")
			cmds.confirmDialog( title='Error in Selection', message='No edges selected.',
								button=['Ok','Cancel'], defaultButton='Ok', 
								cancelButton='Cancel', dismissString='No' )
			return None, None

		cmds.select(cl = True)

		return (edges, profile)

	def createPath(self, edges):
		"""
		Procedure to create and validate curve path from a list of edges
		"""
		cmds.select(cl = True)
		cmds.select(edges)

		#convert edge selection to linear curve
		path = mel.eval("polyToCurve -form 0 -degree 1 -conformToSmoothMeshPreview 0")[0]
		
		#check if closed curve
		isClosed = self.checkForClosedCurve(path)
		
		#if closed, edit curve so profile can extrude around hard corners
		if isClosed:
			path = self.fixCurveEndPoints(path)

		path = cmds.rename(path, "easyTrimCurve#")
		
		cmds.hide( path )

		return path

	def fixCurveEndPoints(self, path):
		"""
		Trim surfaces that end on a hard corner do not resolve nicely.
		To fix this, the following steps are taken: 
		
		detach curve, move one of the new end points slightly
		re-attach, move points together again, then extrude the surface
		This will alloww trim surface to go around closed hard corners
		"""
		detachedPaths = cmds.detachCurve( path, ch=True, p=0.5, replaceOriginal=True )

		path01 = detachedPaths[0]
		path02 = detachedPaths[1]

		origPointPos = cmds.pointPosition( '%s.cv[0]' % path01 )

		x, y, z = list( map(add, origPointPos, [.1, .1, .1]) )

		#move end point slightly before attach
		cmds.move(x, y, z, '%s.ep[0]' % path01, wd=True)

		#attach 2 curves together
		newPath = cmds.attachCurve( path01, path02, 
									ch=0, rpo=1, kmk=1, m=0, 
									bb=.5, p=.1, o=0 )[0]

		x, y, z = origPointPos

		cmds.move(x, y, z, '%s.ep[0]' % newPath, wd=True)

		#rebuild curve for uniform parameterization
		cmds.rebuildCurve( newPath, ch=1, rpo=1, rt=0, 
									end=1, kr=2, kcp=1, 
									kep=1, kt=0, s=0 , d=1, tol=.01)

		#delete the remnants of the original path
		cmds.delete(path)

		return newPath



	def checkForClosedCurve(self, path):
		"""
		check if closed curve and return result
		closed in this case means start point lies on end point
		"""
		isClosed = False

		spans = cmds.getAttr( '%s.spans' % path)
		firstPoint = cmds.pointPosition( '%s.cv[0]' % path )
		lastPoint = cmds.pointPosition( '%s.cv[%s]' % (path, spans) )

		distance = map(sub, firstPoint, lastPoint)
		
		return all((i < .01 and i > -.01) for i in distance)


	def nurbsToPoly(self, nurbsSurface):
		"""
		Convert a Nurbs surface to polygons
		"""
		polySurface = cmds.nurbsToPoly( nurbsSurface, ch=True, n = "easyTrimPolySurface#" )[0]

		#need to get the name of the tessellate attribute
		attrs = cmds.listHistory(polySurface)
		tessellateAttr = [i for i in attrs if i.startswith('nurbsTessellate')][0]

		cmds.setAttr('%s.polygonType' % tessellateAttr, 1)
		cmds.setAttr('%s.format' % tessellateAttr, 2)
		cmds.setAttr('%s.uType' % tessellateAttr, 3)
		cmds.setAttr('%s.uNumber' % tessellateAttr, 1)
		cmds.setAttr('%s.vType' % tessellateAttr, 3)
		cmds.setAttr('%s.vNumber' % tessellateAttr, 1)
		cmds.setAttr('%s.useChordHeightRatio' % tessellateAttr, 0)

		#hide nurbs surface
		cmds.hide( nurbsSurface )

		return polySurface

	def fixReversedNormals(self, curve, polySurface, nurbsSurface):
		"""
		This fixes most reversed normals issues when extruding along a curve
		but only if the curve runs inside the extruded profile curve
		"""
		curvePoint = tuple(cmds.pointOnCurve(curve, p = True, pr = 0))
		print "curvePoint"
		print curvePoint

		cpmNode = cmds.createNode("closestPointOnMesh")

		#replace polyShape with the shapeNode's name
		cmds.connectAttr("%s.outMesh" % polySurface, cpmNode + ".inMesh") 
		cmds.setAttr(cpmNode + ".inPosition", curvePoint[0], curvePoint[1], curvePoint[2], type="double3")

		surfacePoint = cmds.getAttr(cpmNode + ".position")[0]
		surfaceNrm = cmds.getAttr(cpmNode + ".normal")[0]

		#curve point - surface point
		surfToCurve = tuple(map(sub, curvePoint, surfacePoint ))
		length = om.MVector(surfToCurve[0], surfToCurve[1], surfToCurve[2]).length()

		if length <.001:
			print "surf to curve length less than zero, using curve normal"
			curveNormal = tuple(self.getCurveNormal(curve, curvePoint)[0])
			curveNormalWorldPos = tuple(map(add, curvePoint, curveNormal ))
			curvePtToCurveWorldPos = tuple(map(sub, curveNormalWorldPos, curvePoint ))

			angleBetweenTwo = cmds.angleBetween(v1 = surfaceNrm, v2=curvePtToCurveWorldPos)[3]
			print angleBetweenTwo
		else:
			print "surf to curve length greater than zero"
			angleBetweenTwo = cmds.angleBetween(v1 = surfaceNrm, v2=surfToCurve)[3]
			print angleBetweenTwo

		#if angle between 2 vectors is < 90, flip normals
		if int(angleBetweenTwo) <= 90:
			print "reversing normals"
			#reverse surface normals
			#construction history reverses polySurface as well
			cmds.reverseSurface( nurbsSurface, ch = False)

	def getCurveNormal(self, mayaCurve, pos=[0,0,0]):
		"""
		#Returns normal, tangent, at a given point on a curve, given the curve and a position in space.
		#result as a list of openmaya MVector()
		"""
		selectionList = om.MSelectionList()
		selectionList.add(mayaCurve)
		dPath= selectionList.getDagPath(0)
		mCurve=om.MFnNurbsCurve (dPath)
		res=mCurve.closestPoint(om.MPoint(om.MVector(pos)),space=om.MSpace.kWorld)
		point=om.MVector(res[0])
		param=res[1]
		normal=mCurve.normal(param,space=om.MSpace.kWorld)
		tangent=mCurve.tangent(param,space=om.MSpace.kWorld)
		info=[normal,tangent,point]        
		
		return info			

	def fixProfileScale(self, curve, surface):
		"""
		Fix the bug where Maya scales a profile when extruded around a 90 degree corner.
		"""
		#slightly rotate path curve in y
		cmds.setAttr('%s.rotateY' % curve, .01)
		
		#rotate the surface in opposite direction to offset
		cmds.setAttr('%s.rotateY' % surface, -.01)
