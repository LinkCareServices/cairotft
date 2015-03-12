# Copyright (c) 2012 Kurichan
#
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.
"""Small wrapping of linux/fb.h.

update for cairotft: this module has been modified to support
        double buffering and is not api-compatible anymore with the original
        module from Kurichan.

        It has also been modified for python 3.4 compat'
"""
import os
import mmap
import ctypes
from fcntl import ioctl

#
# Working without ctypes example
#
# >>> buf = array.array('B', (0x00,)*(16+8+4))
# >>> fcntl.ioctl(fid, 0x4602, buf)
# 0
# >>> struct.unpack('I', buf[-4:])
# (2457600,)
#

FBIOGET_VSCREENINFO = 0x4600
FBIOGET_FSCREENINFO = 0x4602


class FbFid(int):

    """The framebuffer file descriptor.

    The name attribute gives the
    opened framebuffer file.
    """

    # __slots__ = ('name',)
    pass


class FixScreenInfo(ctypes.Structure):

    """The fb_fix_screeninfo from fb.h."""

    _fields_ = [
        ('id_name', ctypes.c_char * 16),
        ('smem_start', ctypes.c_ulong),
        ('smem_len', ctypes.c_uint32),
        ('type', ctypes.c_uint32),
        ('type_aux', ctypes.c_uint32),
        ('visual', ctypes.c_uint32),
        ('xpanstep', ctypes.c_uint16),
        ('ypanstep', ctypes.c_uint16),
        ('ywrapstep', ctypes.c_uint16),
        ('line_length', ctypes.c_uint32),
        ('mmio_start', ctypes.c_ulong),
        ('mmio_len', ctypes.c_uint32),
        ('accel', ctypes.c_uint32),
        ('reserved', ctypes.c_uint16 * 3),
    ]


class FbBitField(ctypes.Structure):

    """The fb_bitfield struct from fb.h."""

    _fields_ = [
        ('offset', ctypes.c_uint32),
        ('length', ctypes.c_uint32),
        ('msb_right', ctypes.c_uint32),
    ]


class VarScreenInfo(ctypes.Structure):

    """The fb_var_screeninfo struct from fb.h."""

    _fields_ = [
        ('xres', ctypes.c_uint32),
        ('yres', ctypes.c_uint32),
        ('xres_virtual', ctypes.c_uint32),
        ('yres_virtual', ctypes.c_uint32),
        ('xoffset', ctypes.c_uint32),
        ('yoffset', ctypes.c_uint32),

        ('bits_per_pixel', ctypes.c_uint32),
        ('grayscale', ctypes.c_uint32),

        ('red', FbBitField),
        ('green', FbBitField),
        ('blue', FbBitField),
        ('transp', FbBitField),
    ]


def open_fbdev(fbdev=None):
    """Return the framebuffer file descriptor.

    Try to use the FRAMEBUFFER
    environment variable if fbdev is not given. Use '/dev/fb0' by
    default.
    """
    dev = fbdev or os.getenv('FRAMEBUFFER', '/dev/fb0')
    fbfid = FbFid(os.open(dev, os.O_RDWR))
    fbfid.name = dev
    return fbfid


def close_fbdev(fbfid):
    """Close the framebuffer file descriptor."""
    os.close(fbfid)


def get_fix_info(fbfid):
    """Return the fix screen info from the framebuffer file descriptor."""
    fix_info = FixScreenInfo()
    ioctl(fbfid, FBIOGET_FSCREENINFO, fix_info)
    return fix_info


def get_var_info(fbfid):
    """Return the var screen info from the framebuffer file descriptor."""
    var_info = VarScreenInfo()
    ioctl(fbfid, FBIOGET_VSCREENINFO, var_info)
    return var_info


def map_fb_memory(fbfid, fix_info):
    """Map the framebuffer memory."""
    return mmap.mmap(
        fbfid,
        fix_info.smem_len,
        mmap.MAP_SHARED,
        mmap.PROT_READ | mmap.PROT_WRITE,
        offset=0
    )


class FbMem(object):

    """The framebuffer memory object.

    Made of:
        - the framebuffer file descriptor
        - the fix screen info struct
        - the var screen info struct
        - the mapped memory
    """

    __slots__ = ('fid', 'fix_info', 'var_info', 'mmap')


def open_fbmem(fbdev=None):
    """Create the FbMem framebuffer memory object."""
    fid = open_fbdev(fbdev)
    fix_info = get_fix_info(fid)
    fbmmap = map_fb_memory(fid, fix_info)
    fbmem = FbMem()
    fbmem.fid = fid
    fbmem.fix_info = fix_info
    fbmem.var_info = get_var_info(fid)
    fbmem.mmap = fbmmap
    return fbmem


def memory_buffer(buffer_len):
    """Create a memory buffer of buffer_len size.

    this memory buffer can be used to create a custom cairo surface for
    double buffering (or n-buffering)

    :param int buffer_len: size of the buffer.

    :return: the created buffer
    """
    _buffer = ctypes.create_string_buffer(buffer_len)
    return _buffer


def close_fbmem(fbmem):
    """Close the FbMem framebuffer memory object."""
    fbmem.mmap.close()
    close_fbdev(fbmem.fid)
    # TODO: free the double_buffer ?


def cairo_surface_from_fbmem(fbmem, mem, cairo_format):
    """Create a cairo surface from FbMem object.

    :param fbmem: framebuffer memory object
    :param mem: the memory buffer, either created directly or via mmap
    :param int cairo_format: cairo pixel format.
    """
    import cairocffi as cairo
    return cairo.ImageSurface.create_for_data(
        mem,
        cairo_format,  # cairo.FORMAT_RGB24,  # cairo.FORMAT_RGB16_565, etc...
        fbmem.var_info.xres,
        fbmem.var_info.yres,
        fbmem.fix_info.line_length)
