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

    """Display class for the tft display.

    :ivar fb_interface: (:py:class:`str`) framebuffer interface
        name (ex: /dev/fb0)
    :ivar cairo_format: (:py:class:`int`) cairo pixel format.
        see cairocffi documentation:
        https://pythonhosted.org/cairocffi/api.html#pixel-format
    :ivar fps: (:py:class:`int`) forced fps
    :ivar _blit_flag: (:py:class:`bool`) used in forced fps mode: each blit()
        call will activate the blit flag in order to do a real buffer copy
        in the next blit.
    :ivar _fbmem: (:class:`cairotft.linuxfb.FbMem`) framebuffer memory
        interface. This object is the memory interface to the screen.
    :ivar _buffermem: (ctypes array of c_char) memory buffer.
        This object is the memory buffer for the double buffer.
    :ivar surf: (:class:`cairocffi.ImageSurface`) cairo surface pointing to
        the actual screen.
    :ivar buffer_surf: (:class:`cairocffi.ImageSurface`) cairo surface pointing
        to the double buffer.
    :ivar width: (:py:class:`int`) width of the screen in pixels.
    :ivar height: (:py:class:`int`) height of the screen in pixels.
    :ivar size_per_pixel: (:py:class:`int`) number of bytes per pixel.
    :ivar ctx: (:class:`cairocffi.Context`) cairocffi default context.
        This context draws in the double (memory) buffer.
    :ivar screen_ctx: (:class:`cairocffi.Context`) cairocffi context to draw
        directly on the screen.
    :ivar loop: (:py:class:`asyncio.BaseEventLoop`) The main event loop.
    """

    def __init__(self, interface='/dev/fb0', cairo_format=cairo.FORMAT_ARGB32,
                 fps=None):
        """Initialisation of the class.

        :param str interface: framebuffer interface name
        :param int cairo_format: the pixel format.
            see: https://pythonhosted.org/cairocffi/api.html#pixel-format
        :param int fps: a forced fps.
            * If no forced fps is given (fps=None),
              each blit() call will copy the memory buffer into the screen
              buffer.
            * If a forced fps is given, each call to :class:`TftDisplay.blit`
              will not redraw the screen but only trigger a redraw for the
              next frame. The 'real' blit is called every 1/fps seconds.

              .. warning:: choose your fps carefully: if you choose a to high
                 fps for your hardware, the application may pass all its time
                 to redraw the screen instead of actually really drawing
                 objects.

                 Also, take care of the bus speed and size that defines a max
                 fps. For example a SPI screen with 480x272 resolution in
                 16bits a 20 Mhz has an absolute max FPS of:
                 20 000 000 / (480 * 272 * 2 * 8) = 9.57 fps
                 (without taking care of the spi communications overhead)

        """
        self.fb_interface = interface
        self.cairo_format = cairo_format
        self.fps = fps
        self._blit_flag = False

        # two memory buffers:
        #     * fbmem for direct draw on the screen
        #     * buffermem: memory buffer for double buffering.
        self._fbmem = linuxfb.open_fbmem(self.fb_interface)
        self._buffermem = linuxfb.memory_buffer(self._fbmem.fix_info.smem_len)

        # two cairo surface, directly on the screen and in the memory buffer.
        self.surf = linuxfb.cairo_surface_from_fbmem(
            self._fbmem,
            self._fbmem.mmap,
            cairo_format)
        self.buffer_surf = linuxfb.cairo_surface_from_fbmem(
            self._fbmem,
            self._buffermem,
            cairo_format)

        # calculates width and height of the screen
        self.width, self.height = self.surf.get_width(), self.surf.get_height()
        self.size_per_pixel = self._fbmem.fix_info.smem_len / (self.width *
                                                               self.height)
        # by default we write only in buffer using self.ctx
        self.ctx = cairo.Context(self.buffer_surf)

        # cairo context for direct rendering on the screen.
        # normaly only used with blit.
        self.screen_ctx = cairo.Context(self.surf)

        # async io loop
        self.loop = asyncio.get_event_loop()

    def blit(self, force=False):
        """Display the buffer in the screen.

        Take the content of the memory buffer and draw it on the screen.

        :param bool force: if force is True, force a buffer copy, even in fps
            mode.
        """
        if self.fps is None or force:
            self.screen_ctx.set_source_surface(self.buffer_surf)
            self.screen_ctx.paint()
        else:
            self._blit_flag = True

    def fps_call(self):
        """force a redraw screen. Called every x ms when fps mode is set."""
        if self._blit_flag:
            self.blit(force=True)
            self._blit_flag = False
        self.loop.call_later(1 / self.fps, self.fps_call)

    def close(self):
        """Close the interface."""
        # Back to black background
        self.blank_screen(self.ctx)
        linuxfb.close_fbmem(self._fbmem)

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
        """Method that should be overriden by subclasses.

        :param ctx: cairocffi context
        :type ctx: :class:`cairocffi.Context`
        """
        raise NotImplementedError

    def run(self):
        """main loop."""
        # just afer loop is started, draw the interface
        self.loop.call_soon(self.draw_interface, self.ctx)
        if self.fps:
            self.loop.call_later(1 / self.fps, self.fps_call)
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.loop.close()
            self.close()
