# Copyright (c) 2015, Thomas Chiroux - Link Care Services
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of cairotft nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""Class for display on tft using linuxfb."""
import asyncio
import cairocffi as cairo

from cairotft import linuxfb


class TftDisplay():

    """Display class for the tft display."""

    def __init__(self, interface='/dev/fb0', cairo_format=cairo.FORMAT_ARGB32):
        """Initialisation of the class.

        :param str interface: framebuffer interface name
        :param int cairo_format: the pixel format.
            see: https://pythonhosted.org/cairocffi/api.html#pixel-format
        """
        self.fb_interface = interface
        self.cairo_format = cairo_format

        # two memory buffers:
        #     * fbmem for direct draw on the screen
        #     * buffermem: memory buffer for double buffering.
        self.fbmem = linuxfb.open_fbmem(self.fb_interface)
        self.buffermem = linuxfb.memory_buffer(self.fbmem.fix_info.smem_len)

        # two cairo surface, directly on the screen and in the memory buffer.
        self.surf = linuxfb.cairo_surface_from_fbmem(
            self.fbmem,
            self.fbmem.mmap,
            cairo_format)
        self.buffer_surf = linuxfb.cairo_surface_from_fbmem(
            self.fbmem,
            self.buffermem,
            cairo_format)

        # calculates width and height of the screen
        self.width, self.height = self.surf.get_width(), self.surf.get_height()
        self.size_per_pixel = self.fbmem.fix_info.smem_len / (self.width *
                                                              self.height)
        # by default we write only in buffer using self.ctx
        self.ctx = cairo.Context(self.buffer_surf)

        # cairo context for direct rendering on the screen.
        # normaly only used with blit.
        self.screen_ctx = cairo.Context(self.surf)

        # async io loop
        self.io_loop = asyncio.get_event_loop()

    def blit(self):
        """Display the buffer in the screen.

        Take the content of the memory buffer and draw it on the screen.
        """
        self.screen_ctx.set_source_surface(self.buffer_surf)
        self.screen_ctx.paint()

    def close(self):
        """Close the interface."""
        # Back to black background
        self.blank_screen(self.ctx)
        linuxfb.close_fbmem(self.fbmem)

    def blank_screen(self, ctx, color=(0, 0, 0, 1), blit=True):
        """Blank the screen with the given color.

        :param ctx: cairocffi context
        :type ctx: :class:`cairocffi.Context`
        :param color: 4 int tuple reprensentig the rgba color.
        """
        ctx.set_source_rgba(*color)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()
        if blit:
            self.blit()

    def draw_interface(self, ctx):
        """Method that should be overriden by subclasses."""
        raise NotImplementedError

    def run(self):
        """main loop."""
        # just afer loop is started, draw the interface
        self.io_loop.call_soon(self.draw_interface, self.ctx)
        try:
            self.io_loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.io_loop.close()
            self.close()
