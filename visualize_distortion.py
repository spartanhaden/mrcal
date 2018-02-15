#!/usr/bin/python2

r'''Renders a vector field to visualize the effect of a model

Synopsis:

  $ visualize_distortion.py left.cameramodel
  ... a plot pops up showing the vector field

This allows us to visually see what a distortion model does. Depending on the
model, the vectors could be very large or very small, and we can scale them by
passing '--scale s'. By default we sample in a 20x20 grid, but this spacing can
be controlled by passing '--gridn N'.

A tool with similar usefulness is undistort.py. That tool removes the distortion
from a given set of images.

'''


import numpy as np
import numpysane as nps
import gnuplotlib as gp
import sys
import re
import argparse
import os

from mrcal import cameramodel
from mrcal import cahvor
from mrcal import projections








def parse_args():

    parser = \
        argparse.ArgumentParser(description = __doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--gridn',
                        type=int,
                        default = 20,
                        help='''How dense the vector field should be. By default we report a 20x20 grid''')

    parser.add_argument('--scale',
                        type=float,
                        default = 1.0,
                        help='''Scale the vectors by this factor. Default is 1.0 (report the truth), but this is often too small to see''')

    parser.add_argument('model',
                        type=lambda f: f if os.path.isfile(f) else \
                                parser.error("The cameramodel must be an existing readable file, but got '{}".format(f)),
                        nargs=1,
                        help='''Input camera model. Assumed to be mrcal native, Unless the name is xxx.cahvor,
                        in which case the cahvor format is assumed''')

    return parser.parse_args()



args = parse_args()
if re.match(".*\.cahvor$", args.model[0]):
    model = cahvor.read(args.model[0])
else:
    model = cameramodel(args.model[0])


intrinsics = model.intrinsics()

dims = model.dimensions()
if dims is None:
    sys.stderr.write("Warning: imager dimensions not available. Using centerpixel*2\n")
    dims = model.intrinsics()[1][2:4] * 2
W,H = dims

# get the input and output grids of shape Nwidth,Nheight,2
grid, dgrid = projections.distortion_map__to_warped(intrinsics,
                                                    np.linspace(0,W,args.gridn),
                                                    np.linspace(0,H,args.gridn))

# shape: gridn*gridn,2
grid  = nps.clump(grid,  n=2)
dgrid = nps.clump(dgrid, n=2)

delta = dgrid-grid
delta *= args.scale
gp.plot( (grid[:,0], grid[:,1], delta[:,0], delta[:,1],
          {'with': 'vectors size screen 0.005,10 fixed filled',
           'tuplesize': 4,
           }),
         (grid[:,0], grid[:,1],
          {'with': 'points',
           'tuplesize': 2,
           }),
         _xrange=(-50,W+50),
         _yrange=(H+50, -50),
         _set='object 1 rectangle from 0,0 to {},{} fillstyle empty'. \
         format(W,H))

import time
time.sleep(100000)
