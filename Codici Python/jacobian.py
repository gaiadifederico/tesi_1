# coding: utf-8
""" demo on dynamic eit using JAC method """
# Copyright (c) Benyuan Liu. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
from __future__ import absolute_import, division, print_function

import matplotlib.pyplot as plt
import numpy as np
import pyeit.eit.jac as jac
import pyeit.mesh as mesh
from pyeit.eit.fem import EITForward
from pyeit.eit.interp2d import sim2pts
from pyeit.mesh.shape import thorax
import pyeit.eit.protocol as protocol
from pyeit.mesh.wrapper import PyEITAnomaly_Circle

""" 0. build mesh """
n_el = 8  # nb of electrodes
use_customize_shape = False
if use_customize_shape:
    # Mesh shape is specified with fd parameter in the instantiation, e.g : fd=thorax
    mesh_obj = mesh.create(n_el, h0=0.1, fd=thorax)
else:
    mesh_obj = mesh.create(n_el, h0=0.1)

# extract node, element, alpha
pts = mesh_obj.node
tri = mesh_obj.element
x, y = pts[:, 0], pts[:, 1]


""" 1. problem setup """
# mesh_obj["alpha"] = np.random.rand(tri.shape[0]) * 200 + 100 # NOT USED
#anomaly = PyEITAnomaly_Circle(center=[0.5, 0.5], r=0.1, perm=1000.0)
#mesh_new = mesh.set_perm(mesh_obj, anomaly=anomaly)
el_pos = mesh_obj.el_pos

""" 2. FEM simulation """
# setup EIT scan conditions
protocol_obj = protocol.create(n_el, dist_exc=1, step_meas=1, parser_meas="std")

#v0=np.array([508.91,473.01,473.01,473.01,508.91,473.01,525.36,508.91,508.91,473.01,508.91,473.01,525.36,490.76,473.01,508.91,473.01,458.33,473.01,473.01,508.91,429.48,473.01,508.91,473.01,473.01,508.91,473.01,508.91,473.01,473.01,473.01,508.91,473.01,473.01,458.33,508.91,473.01,473.01,473.01])
#v1=np.array([508.91,486.14,525.36,525.36,525.36,473.01,508.91,508.91,473.01,473.01,508.91,508.91,508.91,508.91,525.36,473.01,473.01,508.91,508.91,473.01,508.91,473.01,508.91,508.91,508.91,473.01,508.91,508.91,508.91,525.36,508.91,486.14,525.36,508.91,525.36,486.14,550.00,508.91,458.33,486.14])
#v2=np.array([525.36,550.00,508.91,508.91,570.94,508.91,525.36,508.91,508.91,525.36,550.00,525.36,508.91,508.91,508.91,473.01,525.36,473.01,550.00,508.91,508.91,525.36,525.36,508.91,525.36,473.01,525.36,550.00,486.14,473.01,550.00,473.01,508.91,473.01,525.36,508.91,473.01,490.76,490.76,508.91])
#v3=np.array([525.36,550.00,525.36,508.91,525.36,473.01,508.91,508.91,473.01,473.01,508.91,550.00,508.91,508.91,525.36,508.91,508.91,473.01,508.91,508.91,525.36,550.00,550.00,508.91,508.91,508.91,550.00,525.36,486.14,508.91,508.91,508.91,508.91,508.91,508.91,508.91,508.91,508.91,508.91,508.91])
#v4=np.array([570.94,550.00,525.36,550.00,525.36,508.91,525.36,525.36,473.01,508.91,508.91,486.14,508.91,550.00,550.00,490.76,508.91,473.01,473.01,473.01,473.01,525.36,508.91,508.91,508.91,508.91,508.91,486.14,508.91,473.01,508.91,508.91,508.91,508.91,508.91,486.14,508.91,486.14,570.94,473.01])

#v0=np.array([550.00,550.00,511.21,550.00,567.78,511.21,567.78,511.21,617.04,550.00,525.39,550.00,550.00,550.00,594.41,550.00,511.21,511.21,550.00,525.39,511.21,525.39,550.00,511.21,525.39,550.00,550.00,511.21,550.00,495.34,550.00,550.00,594.41,550.00,511.21,550.00,511.21,567.78,550.00,550.00])
#v1=np.array([594.41,567.78,567.78,550.00,594.41,511.21,550.00,511.21,550.00,550.00,550.00,550.00,594.41,511.21,550.00,511.21,530.38,511.21,550.00,525.39,594.41,567.78,550.00,550.00,511.21,511.21,567.78,550.00,550.00,550.00,594.41,525.39,550.00,525.39,511.21,511.21,550.00,511.21,550.00,567.78])
#v2=np.array([594.41,550.00,550.00,567.78,567.78,550.00,550.00,550.00,550.00,550.00,550.00,550.00,550.00,567.78,550.00,495.34,550.00,594.41,511.21,511.21,550.00,550.00,567.78,550.00,511.21,511.21,567.78,511.21,550.00,567.78,594.41,550.00,530.38,550.00,511.21,567.78,550.00,511.21,550.00,530.38])
#v3=np.array([594.41,550.00,567.78,511.21,550.00,550.00,525.39,511.21,511.21,511.21,550.00,550.00,511.21,550.00,550.00,567.78,550.00,550.00,550.00,550.00,550.00,550.00,594.41,550.00,550.00,511.21,567.78,511.21,550.00,550.00,594.41,530.38,511.21,550.00,550.00,511.21,550.00,567.78,567.78,511.21])
#v4=np.array([594.41,567.78,567.78,550.00,550.00,525.39,594.41,511.21,550.00,550.00,511.21,511.21,550.00,567.78,594.41,550.00,550.00,530.38,550.00,550.00,511.21,594.41,550.00,594.41,550.00,550.00,550.00,594.41,550.00,525.39,550.00,550.00,550.00,550.00,550.00,511.21,594.41,525.39,567.78,530.38])

v0=np.array([490.25,550.00,506.09,529.83,506.09,506.09,506.09,490.25,490.25,550.00,506.09,550.00,490.25,506.09,506.09,550.00,506.09,455.67,506.09,550.00,529.83,550.00,490.25,490.25,529.83,529.83,506.09,506.09,506.09,529.83,506.09,529.83,506.09,490.25,529.83,490.25,490.25,550.00,506.09,506.09])
v1=np.array([506.09,601.46,490.25,529.83,506.09,550.00,550.00,490.25,455.67,490.25,506.09,529.83,490.25,601.46,550.00,506.09,490.25,506.09,506.09,529.83,506.09,550.00,550.00,529.83,550.00,601.46,550.00,550.00,468.31,550.00,529.83,490.25,550.00,506.09,529.83,550.00,529.83,506.09,490.25,529.83])
v2=np.array([550.00,529.83,601.46,529.83,550.00,529.83,550.00,506.09,550.00,506.09,550.00,506.09,506.09,506.09,550.00,490.25,550.00,490.25,506.09,472.76,529.83,550.00,506.09,506.09,550.00,550.00,529.83,506.09,506.09,550.00,550.00,529.83,490.25,506.09,506.09,550.00,490.25,529.83,550.00,506.09])
v3=np.array([550.00,550.00,550.00,529.83,550.00,506.09,529.83,506.09,550.00,490.25,550.00,506.09,506.09,506.09,506.09,550.00,550.00,506.09,550.00,506.09,506.09,468.31,506.09,529.83,529.83,506.09,550.00,506.09,490.25,529.83,550.00,506.09,506.09,529.83,529.83,506.09,550.00,550.00,550.00,506.09])
v4=np.array([550.00,550.00,490.25,550.00,601.46,550.00,529.83,550.00,529.83,529.83,490.25,529.83,550.00,506.09,550.00,550.00,506.09,490.25,455.67,529.83,506.09,506.09,529.83,506.09,550.00,506.09,550.00,506.09,529.83,506.09,550.00,506.09,550.00,529.83,490.25,550.00,529.83,550.00,550.00,529.83])



""" 3. JAC solver """
# Note: if the jac and the real-problem are generated using the same mesh,
# then, data normalization in solve are not needed.
# However, when you generate jac from a known mesh, but in real-problem
# (mostly) the shape and the electrode positions are not exactly the same
# as in mesh generating the jac, then data must be normalized.
eit = jac.JAC(mesh_obj, protocol_obj)
eit.setup(p=0.5, lamb=0.01, method="kotre", perm=1, jac_normalized=True)
ds = eit.solve(v1, v0, normalize=True)
ds_n = sim2pts(pts, tri, np.real(ds))

ds2 = eit.solve(v2, v0, normalize=True)
ds_n2 = sim2pts(pts, tri, np.real(ds2))

ds3 = eit.solve(v3, v0, normalize=True)
ds_n3 = sim2pts(pts, tri, np.real(ds3))

ds4 = eit.solve(v4, v0, normalize=True)
ds_n4 = sim2pts(pts, tri, np.real(ds4))

# plot EIT reconstruction
fig, axes = plt.subplots(1,4)
ax = axes[0]
im = ax.tripcolor(x, y, tri, ds_n, shading="flat")
for i, e in enumerate(mesh_obj.el_pos):
    ax.annotate(str(i + 1), xy=(x[e], y[e]), size=12)
ax.plot(x[el_pos], y[el_pos], 'ro')
ax.set_aspect("equal")

#fig.colorbar(im)
# plt.savefig('../doc/images/demo_jac.png', dpi=96)

ax = axes[1]
im2 = ax.tripcolor(x, y, tri, ds_n2, shading="flat")
for i, e in enumerate(mesh_obj.el_pos):
    ax.annotate(str(i + 1), xy=(x[e], y[e]), size=12)
ax.plot(x[el_pos], y[el_pos], 'ro')
ax.set_aspect("equal")

#fig.colorbar(im2)

ax = axes[2]
im3 = ax.tripcolor(x, y, tri, ds_n3, shading="flat")
for i, e in enumerate(mesh_obj.el_pos):
    ax.annotate(str(i + 1), xy=(x[e], y[e]), size=12)
ax.plot(x[el_pos], y[el_pos], 'ro')
ax.set_aspect("equal")

#fig.colorbar(im3)

ax = axes[3]
im4 = ax.tripcolor(x, y, tri, ds_n4, shading="flat")
for i, e in enumerate(mesh_obj.el_pos):
    ax.annotate(str(i + 1), xy=(x[e], y[e]), size=12)
ax.plot(x[el_pos], y[el_pos], 'ro')
ax.set_aspect("equal")

#fig.colorbar(im4)
plt.show()