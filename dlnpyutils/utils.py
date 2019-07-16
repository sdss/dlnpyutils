#!/usr/bin/env python
#
# DLNPYUTILS.PY - Utility functions.
#

from __future__ import print_function

__authors__ = 'David Nidever <dnidever@noao.edu>'
__version__ = '20180823'  # yyyymmdd

import re
import logging
import os
import sys
import numpy as np
import warnings
#from astropy.io import fits
#from astropy.utils.exceptions import AstropyWarning
#import time
#import shutil
#import re
#import subprocess
#import glob
#import logging
#import socket
#from scipy.signal import convolve2d
#from scipy.ndimage.filters import convolve
import astropy.stats

# Ignore these warnings, it's a bug
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

# Size, number of elements
def size(a=None):
    """Returns the number of elements"""
    if a is None: return 0
    return np.array(a,ndmin=1).size

# Median Absolute Deviation
def mad(data, axis=None, func=None, ignore_nan=False):
    """ Calculate the median absolute deviation."""
    if type(data) is not np.ndarray: raise ValueError("data must be a numpy array")    
    return 1.4826 * astropy.stats.median_absolute_deviation(data,axis=axis,func=func,ignore_nan=ignore_nan)

def minmax(a):
    """ Return a 2-element array of minimum and maximum."""
    if type(a) is not np.ndarray: raise ValueError("a must be a numpy array")
    return np.array([np.min(a),np.max(a)])

def stat(a=None,silent=False):
    """ Returns basic statistics on an array."""
    if a is None: raise ValueError("a must be input")
    if type(a) is not np.ndarray: raise ValueError("a must be a numpy array")
    #  This is what stat returns:
    #  info[0]: Number of Elements
    #  info[1]: Minimum
    #  info[2]: Maximum
    #  info[3]: Range
    #  info[4]: Mean
    #  info[5]: Median
    #  info[6]: Standard Deviation
    #  info[7]: Standard Error
    #  info[8]: Root Mean Square (R.M.S.)
    #  info[9]: MAD estimate of St.Dev.
    info = np.zeros(10)
    info[0] = len(a)
    info[1] = np.min(a)
    info[2] = np.max(a)
    info[3] = info[2]-info[1]
    info[4] = np.mean(a)
    if info[0] > 1:
        info[5] = np.median(a)
        info[6] = np.std(a,ddof=1)               # std. dev.
        info[7] = info[6]/np.sqrt(info[0])       # std. err.
        info[8] = np.sqrt(np.sum(a**2)/info[0])  # RMS
        info[9] = mad(a)                         # MAD
    if silent is not True:
        print('----------------------')
        print('elements = %d' % info[0])
        print('minimum  = %f' % info[1])
        print('maximum  = %f' % info[2])
        print('range    = %f' % info[3])
        print('mean     = %f' % info[4])
        print('median   = %f' % info[5])
        print('st. dev. = %f' % info[6])
        print('st. err. = %f' % info[7])
        print('r.m.s.   = %f' % info[8])
        print('mad s.d. = %f' % info[9])
        print('----------------------')
    return


def strlen(lst=None):
    """ Calculate the string lengths of a string array."""
    if lst is None: raise ValueError("lst must be input")
    n = size(lst)
    out = np.zeros(n,int)
    for i,a in enumerate(np.array(lst,ndmin=1)):
        out[i] = len(a)
    if n==1: out=int(out)
    return out


def strip(lst=None,chars=None):
    """ Strip on a scalar or list."""
    if lst is None: raise ValueError("lst must be input")
    if type(lst) is str: return lst.strip(chars)
    return [o.strip(chars) for o in np.array(lst,ndmin=1)]


def strjoin(a=None,b=None,sep=None):
    """ Join two string lists/arrays or scalars"""
    if (a is None) | (b is None): raise ValueError("a and b must be input")
    na = size(a)
    nb = size(b)
    if sep is None: sep=''
    n = np.max([na,nb])
    len1 = strlen(a)
    len2 = strlen(b)
    nlen = np.max(len1)+np.max(len2)+len(sep)
    out = np.zeros(n,(np.str,nlen))
    for i in range(n):
        if na>1:
            a1 = a[i]
        else:
            a1 = np.array(a,ndmin=1)[0]
        if nb>1:
            b1 = b[i]
        else:
            b1 = np.array(b,ndmin=1)[0]
        out[i] = sep.join((a1,b1))
    if (n==1) & (type(a) is str) & (type(b) is str): return out[0]  # scalar
    if (type(a) is list) | (type(b) is list): return list(out)
    return out


def strsplit(lst=None,delim=None,asarray=False):
    """ Split a string array."""
    if (lst is None): raise ValueError("lst must be input")
    if size(lst)==1:
        out = lst.split(delim)
    else:
        out = [l.split(delim) for l in lst]
    if asarray is True:
        nlst = np.array(lst).size
        nel = [len(o) for o in out]
        nlen = np.max(strlen(lst))
        outarr = np.zeros((nlst,np.max(nel)),(np.str,nlen))
        for i in range(nlst):
            temp = np.array(out[i])
            ntemp = len(temp)
            outarr[i,0:ntemp] = temp
        return outarr
    else:
        return out

def pathjoin(indir=None,name=None):
    """ Join two or more pathname components, inserting '/' as needed
    Same as os.path.join but also works on arrays/lists."""
    if indir is None: raise ValueError("must input indir")
    if name is None: raise ValueError("must input name")
    nindir = size(indir)
    nname = size(name)
    n = np.max([nindir,nname])
    len1 = strlen(indir)
    len2 = strlen(name)
    nlen = np.max(len1)+np.max(len2)+1
    out = np.zeros(n,(np.str,nlen))
    for i in range(n):
        if nindir>1:
            indir1 = indir[i]
        else:
            indir1 = np.array(indir,ndmin=1)[0]
        if indir1[-1] != '/': indir1+='/'
        if nname>1:
            name1 = nname[i]
        else:
            name1 = np.array(name,ndmin=1)[0]
        out[i] = indir1+name1
    if (n==1) & (type(indir) is str) & (type(name) is str): return out[0]  # scalar
    if (type(indir) is list) | (type(name) is list): return list(out)
    return out

def first_el(lst):
    """ Return the first element"""
    if lst is None: return None
    if size(lst)>1: return lst[0]
    if (size(lst)==1) & (type(lst) is list): return lst.pop() 
    if (size(lst)==1) & (type(lst) is np.ndarray): return lst.item()
    return lst
        

# Standard grep function that works on string list
def grep(lines=None,expr=None,index=False):
    """
    Similar to the standard unit "grep" but run on a list of strings.
    Returns a list of the matching lines unless index=True is set,
    then it returns the indices.

    Parameters
    ----------
    lines : list
          The list of string lines to check.
    expr  : str
          Scalar string expression to search for.
    index : bool, optional
          If this is ``True`` then the indices of matching lines will be
          returned instead of the actual lines.  index is ``False`` by default.

    Returns
    -------
    out : list
        The list of matching lines or indices.

    Example
    -------

    Search for a string and return the matching lines:

    .. code-block:: python

        mlines = grep(lines,"hello")

    Search for a string and return the indices of the matching lines:

    .. code-block:: python

        index = grep(lines,"hello",index=True)

    """
    if lines is None: raise ValueError("lines must be input")
    if expr is None: raise ValueError("expr must be input")
    out = []
    cnt = 0L
    for l in np.array(lines,ndmin=1):
        m = re.search(expr,l)
        if m != None:
            if index is False:
                out.append(l)
            else:
                out.append(cnt)
        cnt = cnt+1
    return out


# Read in all lines of files
def readlines(fil=None):
    """
    Read in all lines of a file.
    
    Parameters
    ----------
    file : str
         The name of the file to load.
   
    Returns
    -------
    lines : list
          The list of lines from the file

    Example
    -------

    .. code-block:: python

       lines = readlines("file.txt")

    """
    if fil is None: raise ValueError("File not input")
    f = open(fil,'r')
    lines = f.readlines()
    f.close()
    return lines


# Write all lines to file
def writelines(filename=None,lines=None,overwrite=True):
    """
    Write a list of lines to a file.
    
    Parameters
    ----------
    filename : str
        The filename to write the lines to.
    lines : list
         The list of lines to write to a file.
    overwrite : bool, optional, default is True
        If the output file already exists, then overwrite it.

    Returns
    -------
    Nothing is returned.  The lines are written to `fil`.

    Example
    -------

    .. code-block:: python

       writelines("file.txt",lines)

    """
    # Not enough inputs
    if lines is None: raise ValueError("No lines input")
    if filename is None: raise ValueError("No file name input")
    # Check if the file exists already
    if os.path.exists(filename):
        if overwrite is True:
            os.remove(filename)
        else:
            print(filename+" already exists and overwrite=False")
            return
    # Write the file
    f = open(filename,'w')
    f.writelines(lines)
    f.close()


# Remove indices from a list
def remove_indices(lst=None,index=None):
    """
    This will remove elements from a list given their indices.
    Use numpy.delete() for numpy arrays instead.

    Parameters
    ----------
    lst : list
          The list from which to remove elements.
    index : list or array
          The list or array of indices to remove.

    Returns
    -------
    newlst : list
           The new list with indices removed.

    Example
    -------

    Remove indices 1 and 5 from array `arr`.

    .. code-block:: python

        index = [1,5]
        arr  = range(10)
        arr2 = remove_indices(arr,index)
        print(arr)
          [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    """
    if lst is None: raise ValueError("list must be input")
    if index is None: raise ValueError("index must be input")
    newlst = []
    for i in range(len(lst)):
       if i not in index: newlst.append(lst[i])
    if type(lst) is np.ndarray: newlst = np.array(newlst)
    return newlst


# Little function used by numlines
def blocks(files, size=65536):
    """
    This is a small utility function used by numlines()
    """
    while True:
        b = files.read(size)
        if not b: break
        yield b


# Read number of lines in a file
def numlines(fil=None):
    """
    This function quickly counts the number of lines in a file.

    Parameters
    ----------
    fil : str
          The filename to check the number of lines.

    Returns
    -------
    nlines : int
           The number of lines in `fil`.

    Example
    -------

    .. code-block:: python

        n = numlines("file.txt")

    """
    if fil is None: raise ValueError("file must be input")
    with open(fil, "r") as f:
        return (sum(bl.count("\n") for bl in blocks(f)))

    # Could also use this
    #count=0
    #for line in open(fil): count += 1


# Set up basic logging to screen
def basiclogger(name=None):
    """
    This sets up a basic logger that writes just to the screen.
    """
    if name is None: name = "log"
    logger = logging.getLogger(name)
    # Only add a handler if none exists
    #  the logger might already have been created
    if len(logger.handlers)==0:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)-2s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


# Delete files
def remove(files=None,allow=True):
    """ Delete a list of files."""
    if files is None: raise ValueError("No files input")
    nfiles = np.array(files).size
    for f in np.array(files,ndmin=1):
        if os.path.exists(f):
            os.remove(f)
        else:
            if allow is False: raise Exception(f+" does not exist")

def lt(x,limit):
    """Takes the lesser of x or limit"""
    # np.minimum() also does this
    if np.array(x).size>1:
        out = [i if (i<limit) else limit for i in x]
    else:
        out = x if (x<limit) else limit
    if type(x) is np.ndarray: return np.array(out)
    return out
    
def gt(x,limit):
    """Takes the greater of x or limit"""
    # np.maximum() also does this
    if np.array(x).size>1:
        out = [i if (i>limit) else limit for i in x]
    else:
        out = x if (x>limit) else limit
    if type(x) is np.ndarray: return np.array(out)
    return out        

def limit(x,llimit,ulimit):
    """Require x to be within upper and lower limits"""
    return lt(gt(x,llimit),ulimit)
    
def gaussian(x, amp, cen, sig, const=0):
    """1-D gaussian: gaussian(x, amp, cen, sig)"""
    return (amp / (np.sqrt(2*np.pi) * sig)) * np.exp(-(x-cen)**2 / (2*sig**2)) + const

def gaussfit(x,y,initpar,sigma=None, bounds=None):
    """Fit 1-D Gaussian to X/Y data"""
    #gmodel = Model(gaussian)
    #result = gmodel.fit(y, x=x, amp=initpar[0], cen=initpar[1], sig=initpar[2], const=initpar[3])
    #return result
    return curve_fit(gaussian, x, y, p0=initpar, sigma=sigma, bounds=bounds)

def poly(x,coef):
    """ Evaluate a polynomial function of a variable."""
    y = x.copy()*0.0
    for i in range(len(coef)):
        y += coef[i]*x**i
    return y

def poly_fit(x,y,nord,robust=False,sigma=None,bounds=(-np.inf,np.inf)):
    initpar = np.zeros(nord+1)
    # Normal polynomial fitting
    if robust is False:
        #coef = curve_fit(poly, x, y, p0=initpar, sigma=sigma, bounds=bounds)
        weights = None
        if sigma is not None: weights=1/sigma
        coef = np.polyfit(x,y,nord,w=weights)
    # Fit with robust polynomial
    else:
        res_robust = least_squares(poly_resid, initpar, loss='soft_l1', f_scale=0.1, args=(x,y,sigma))
        if res_robust.success is False:
            raise Exception("Problem with least squares polynomial fitting. Status="+str(res_robust.status))
        coef = res_robust.x
    return coef

# Derivative or slope of an array
def slope(array):
    """Derivative or slope of an array: slp = slope(array)"""
    n = len(array)
    return array[1:n]-array[0:n-1]

# Gaussian filter
def gsmooth(data,fwhm,axis=-1,mode='reflect',cval=0.0,truncate=4.0):
    return gaussian_filter1d(data,fwhm/2.35,axis=axis,mode=mode,cval=cval,truncate=truncate)

# Rebin data
def rebin(arr, new_shape):
    if arr.ndim>2:
        raise Exception("Maximum 2D arrays")
    if arr.ndim==0:
        raise Exception("Must be an array")
    if arr.ndim==2:
        shape = (new_shape[0], arr.shape[0] // new_shape[0],
                 new_shape[1], arr.shape[1] // new_shape[1])
        return arr.reshape(shape).mean(-1).mean(1)
    if arr.ndim==1:
        shape = (np.array(new_shape,ndmin=1)[0], arr.shape[0] // np.array(new_shape,ndmin=1)[0])
        return arr.reshape(shape).mean(-1)

def roi_cut(xcut,ycut,x,y):
    """
    Use cuts in a 2D plane to select points from arrays.

    Parameters
    ----------
    xcut : numpy array
         Array of x-values for the cut
    ycut : numpy array
         Array of y-values for the cut
    x : numpy array or list
         Array of x-values that should be cut
    y : numpy array or list
         Array of y-values that should be cut

    Returns
    -------
    ind : numpy array
       The indices of values OUTSIDE the cut
    cutind : 
       The indices of values INSIDE the cut

    Example
    -------

    .. code-block:: python

        ind, cutind = roi_cut(xcut,ycut,x,y)

    """

    from matplotlib.path import Path

    tupVerts = zip(xcut,ycut)

    points = np.vstack((x,y)).T
    
    p = Path(tupVerts) # make a polygon
    inside = p.contains_points(points)

    ind, = np.where(~inside)
    cutind, = np.where(inside)

    return ind, cutind


def create_index(arr):
    """
    Create an index of array values like reverse indices.

    arr[index['index'][index['lo'][2]:index['hi'][2]+1]]
    """

    narr = size(arr)
    si = np.argsort(arr)
    sarr = np.array(arr)[si]
    brklo, = np.where(sarr != np.roll(sarr,1))
    nbrk = len(brklo)
    if nbrk>0:
        brkhi = np.hstack((brklo[1:nbrk]-1,narr-1))
        num = brkhi-brklo+1
        index = {'index':si,'value':sarr[brklo],'num':num,'lo':brklo,'hi':brkhi}
    else:
        index = {'index':si,'value':arr[0],'num':narr,'lo':0L,'hi':narr-1}

    return index


def match(a,b,epsilon=0):
    """
    Routine to match values in two vectors.
    
    CALLING SEQUENCE:
        match, a, b, suba, subb, [ COUNT =, /SORT, EPSILON =  ]
  
    INPUTS:
        a,b - two vectors to match elements, numeric or string data types
    
    OUTPUTS:
      suba - subscripts of elements in vector a with a match
                  in vector b
      subb - subscripts of the positions of the elements in
                  vector b with matchs in vector a.
  
          suba and subb are ordered such that a[suba] equals b[subb]
          suba and subb are set to !NULL if there are no matches (or set to -1
                if prior to IDL Version 8.0)
  
    OPTIONAL INPUT KEYWORD:
          /SORT - By default, MATCH uses two different algorithm: (1) the
                  /REVERSE_INDICES keyword to HISTOGRAM is used for integer data,
                  while (2) a sorting algorithm is used for non-integer data.  The
                  histogram algorithm is usually faster, except when the input
                  vectors are sparse and contain very large numbers, possibly
                  causing memory problems.   Use the /SORT keyword to always use
                  the sort algorithm.
          epsilon - if values are within epsilon, they are considered equal. Used only
                  only for non-integer matching.  Note that input vectors should
                  be unique to within epsilon to provide one-to-one mapping.
                  Default=0.
   
    OPTIONAL KEYWORD OUTPUT:
          COUNT - set to the number of matches, integer scalar
   
    SIDE EFFECTS:
          The obsolete system variable !ERR is set to the number of matches;
          however, the use !ERR is deprecated in favor of the COUNT keyword
   
    RESTRICTIONS:
          The vectors a and b should not have duplicate values within them.
          You can use rem_dup function to remove duplicate values
          in a vector
   
    EXAMPLE:
          If a = [3,5,7,9,11]   & b = [5,6,7,8,9,10]
          then
                  IDL> match, a, b, suba, subb, COUNT = count
   
          will give suba = [1,2,3], subb = [0,2,4],  COUNT = 3
          and       a[suba] = b[subb] = [5,7,9]
   
   
    METHOD:
          For non-integer data types, the two input vectors are combined and
          sorted and the consecutive equal elements are identified.   For integer
          data types, the /REVERSE_INDICES keyword to HISTOGRAM of each array
          is used to identify where the two arrays have elements in common.

    HISTORY:
         D. Lindler  Mar. 1986.
         Fixed "indgen" call for very large arrays   W. Landsman  Sep 1991
         Added COUNT keyword    W. Landsman   Sep. 1992
         Fixed case where single element array supplied   W. Landsman Aug 95
         Use a HISTOGRAM algorithm for integer vector inputs for improved
               performance                W. Landsman         March 2000
         Work again for strings           W. Landsman         April 2000
         Use size(/type)                  W. Landsman         December 2002
         Work for scalar integer input    W. Landsman         June 2003
         Assume since V5.4, use COMPLEMENT to WHERE() W. Landsman Apr 2006
         Added epsilon keyword            Kim Tolbert         March 14, 2008
         Fix bug with Histogram method with all negative values W. Landsman/
         R. Gutermuth, return !NULL for no matches  November 2017
         Added epsilon test in na=1||nb=1 section (missed that when added
               epsilon in 2008)           Kim Tolbert         July 10, 2018
  
    """

    #da = size(a,/type) & db =size(b,/type)
    #if keyword_set(sort) then hist = 0b else $
    #  hist = (( da LE 3 ) || (da GE 12)) &&  ((db LE 3) || (db GE 12 ))

    na = size(a)             # number of elements in a
    nb = size(b)             # number of elements in b
    
    # Check for a single element array
    if (na==1) | (nb==1):
        if (nb>1):
            if epsilon==0.0:
                subb, = np.where(b==a)
                nw = len(subb)
            else:
                subb, = np.where(np.abs(b-a) < epsilon)
                nw = len(subb)
            if (nw>0):
                suba = np.zeros(w,long)
            else:
                suba = np.array([])
        else:
            if epsilon==0.0:
                suba, = np.where(a==b)
                nw = len(suba)
            else:
                suba, = np.where(np.abs(a-b) < epsilon)
                nw = len(suba)
            if (nw>0):
                subb, = np.zero(nw,long)
            else:
                subb = np.array([])
        count = nw
        return suba,subb

    c = np.hstack((np.array(a),np.array(b)))                     # combined list of a and b
    ind = np.hstack((np.arange(na),np.arange(nb)))               # combined list of indices
    vec = np.hstack((np.zeros(na,bool),np.zeros(nb,bool)+True))  # flag of which vector in  combined
    #list   False - a   True - b

    # sort combined list
    sub = np.argsort(c)
    c = c[sub]
    ind = ind[sub]
    vec = vec[sub]

    # find duplicates in sorted combined list
    n = na + nb                            #t otal elements in c
    if epsilon == 0.0:
      firstdup, = np.where( (c == np.roll(c,-1)) & (vec != np.roll(vec,-1)) )
      count = len(firstdup)
    else:
      firstdup, = np.where( (np.abs(c - np.roll(c,-1)) < epsilon) & (vec != np.roll(vec,-1)) )
      count = len(firstdup)

    if count==0:               # any found?
      suba = np.array([])
      subb = np.array([])
      return suba,subb

    dup = np.zeros( count*2, long )        # both duplicate values
    even = np.arange( len(firstdup))*2     # Changed to LINDGEN 6-Sep-1991
    dup[even] = firstdup
    dup[even+1] = firstdup+1
    ind = ind[dup]                         # indices of duplicates
    vec = vec[dup]                         # vector id of duplicates
    vone, = np.where(vec)
    vzero, = np.where(~vec)
    subb = ind[vone]                       # b subscripts
    suba = ind[vzero]


    # # Integer calculation using histogram.
    # else:
    #
    #     minab = min(a, MAX=maxa) > min(b, MAX=maxb) #Only need intersection of ranges
    #     maxab = maxa < maxb
    #
    #     #If either set is empty, or their ranges don't intersect:
    #     #  result = NULL (which is denoted by integer = -1)
    #     !ERR = -1
    #     if !VERSION.RELEASE GE '8.0' then begin
    #        suba = !NULL
    #        subb = !NULL
    #     endif else begin
    #        suba = -1
    #        subb = -1
    #     endelse
    #     COUNT = 0L
    #     if maxab lt minab then return       #No overlap
    #
    #     ha = histogram([a], MIN=minab, MAX=maxab, reverse_indices=reva)
    #     hb = histogram([b], MIN=minab, MAX=maxab, reverse_indices=revb)
    #
    #     r = where((ha ne 0) and (hb ne 0), count)
    #
    #     if count gt 0 then begin
    #        suba = reva[reva[r]]
    #        subb = revb[revb[r]]
    
    return suba, subb

