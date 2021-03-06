# A python wrapper for aclpagerank
# n - number of vertices
# ai,aj - graph in CSR
# alpha - value of alpha
# eps - value of epsilon
# seedids,nseedids - the set of indices for seeds
# maxsteps - the max number of steps
# xlength - the max number of ids in the solution vector
# xids, actual_length - the solution vector
# values - the pagerank value vector for xids (already sorted in decreasing order)

from operator import itemgetter
import numpy as np
from numpy.ctypeslib import ndpointer
import ctypes
#from localgraphclustering.find_library import load_library


def aclpagerank_weighted_cpp(n,ai,aj,a,alpha,eps,seedids,nseedids,maxsteps,lib,xlength=10**6,flag=0):

    float_type = ctypes.c_double

    dt = np.dtype(ai[0])
    (itype, ctypes_itype) = (np.int64, ctypes.c_int64) if dt.name == 'int64' else (np.uint32, ctypes.c_uint32)
    dt = np.dtype(aj[0])
    (vtype, ctypes_vtype) = (np.int64, ctypes.c_int64) if dt.name == 'int64' else (np.uint32, ctypes.c_uint32)

    #lib = load_library()
    
    if (vtype, itype) == (np.int64, np.int64):
        fun = lib.aclpagerank_weighted64
    elif (vtype, itype) == (np.uint32, np.int64):
        fun = lib.aclpagerank_weighted32_64
    else:
        fun = lib.aclpagerank_weighted32

    #call C function
    seedids=np.array(seedids,dtype=vtype)
    xids=np.zeros(xlength,dtype=vtype)
    values=np.zeros(xlength,dtype=float_type)
    a=np.array(a,dtype=float_type)
    fun.restype=ctypes_vtype
    fun.argtypes=[ctypes_vtype,ndpointer(ctypes_itype, flags="C_CONTIGUOUS"),
                  ndpointer(ctypes_vtype, flags="C_CONTIGUOUS"),
                  ndpointer(float_type, flags="C_CONTIGUOUS"),
                  ctypes_vtype,ctypes.c_double,ctypes.c_double,
                  ndpointer(ctypes_vtype, flags="C_CONTIGUOUS"),
                  ctypes_vtype,ctypes_vtype,
                  ndpointer(ctypes_vtype, flags="C_CONTIGUOUS"),
                  ctypes_vtype,ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")]
    actual_length=fun(n,ai,aj,a,flag,alpha,eps,seedids,nseedids,maxsteps,xids,xlength,values)
    if actual_length > xlength:
        xlength = actual_length
        xids=np.zeros(xlength,dtype=vtype)
        values=np.zeros(xlength,dtype=float_type)
        actual_length=fun(n,ai,aj,a,flag,alpha,eps,seedids,nseedids,maxsteps,xids,xlength,values)
    actual_values=values[0:actual_length]
    actual_xids=xids[0:actual_length]
    
    return (actual_length,actual_xids,actual_values)
