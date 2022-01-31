#!/usr/bin/python3

r'''diff test

Make sure the projection-diff function produces correct results
'''

import sys
import numpy as np
import numpysane as nps
import os

testdir = os.path.dirname(os.path.realpath(__file__))

# I import the LOCAL mrcal since that's what I'm testing
sys.path[:0] = f"{testdir}/..",
import mrcal
import testutils


model_opencv8 = mrcal.cameramodel(f"{testdir}/data/cam0.opencv8.cameramodel")
model_splined = mrcal.cameramodel(f"{testdir}/data/cam0.splined.cameramodel")
gridn_width   = 50

########## Compare the model to itself. I should get 0 diff and identity transform
difflen, diff, q0, implied_Rt10 = \
    mrcal.projection_diff( (model_splined,model_splined),
                           gridn_width       = gridn_width,
                           distance          = None,
                           use_uncertainties = False )

testutils.confirm_equal( difflen.shape[1], gridn_width,
                         msg = "Expected number of columns" )
testutils.confirm_equal( difflen.shape[0], int(round( model_splined.imagersize()[1] / model_splined.imagersize()[0] * gridn_width)),
                         msg = "Expected number of rows" )

icenter = np.array(difflen.shape) // 2


testutils.confirm_equal( difflen*0, difflen,
                         eps = 0.05,
                         worstcase = True,
                         relative  = False,
                         msg = "diff(model,model) at infinity should be 0")

testutils.confirm_equal( 0, np.arccos((np.trace(implied_Rt10[:3,:]) - 1) / 2.) * 180./np.pi,
                         eps = 0.01,
                         msg = "diff(model,model) at infinity should produce a rotation of 0 deg")

testutils.confirm_equal( 0, nps.mag(implied_Rt10[3,:]),
                         eps = 0.01,
                         msg = "diff(model,model) at infinity should produce a rotation of 0 m")

difflen, diff, q0, implied_Rt10 = \
    mrcal.projection_diff( (model_splined,model_splined),
                           gridn_width       = 50,
                           distance          = 3.,
                           use_uncertainties = False )

testutils.confirm_equal( difflen*0, difflen,
                         eps = 0.05,
                         worstcase = True,
                         relative  = False,
                         msg = "diff(model,model) at 3m should be 0")

testutils.confirm_equal( 0, np.arccos((np.trace(implied_Rt10[:3,:]) - 1) / 2.) * 180./np.pi,
                         eps = 0.01,
                         msg = "diff(model,model) at 3m should produce a rotation of 0 deg")

testutils.confirm_equal( 0, nps.mag(implied_Rt10[3,:]),
                         eps = 0.01,
                         msg = "diff(model,model) at 3m should produce a translation of 0 m")


########## Check outlier handling when computing diffs without uncertainties.
########## The model may only fit in one regions. Using data outside of that
########## region poisons the solve unless we treat those measurements as
########## outliers. This is controlled by the f_scale parameter in
########## implied_Rt10__from_unprojections().
difflen, diff, q0, implied_Rt10 = \
    mrcal.projection_diff( (model_opencv8,model_splined),
                           gridn_width       = gridn_width,
                           distance          = 5,
                           use_uncertainties = False,
                           focus_radius      = 800)
testutils.confirm_equal( 0, difflen[icenter[0],icenter[1]],
                         eps = 0.1,
                         msg = "Low-enough diff with high focus_radius")

difflen, diff, q0, implied_Rt10 = \
    mrcal.projection_diff( (model_opencv8,model_splined),
                           gridn_width       = gridn_width,
                           distance          = 5,
                           use_uncertainties = False,
                           focus_radius      = 366)
testutils.confirm_equal( 0, difflen[icenter[0],icenter[1]],
                         eps = 0.1,
                         msg = "Low-enough diff with low focus_radius")

testutils.finish()
