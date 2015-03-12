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
"""BlinkIcon widget."""


class BlinkIcon():

    """A svg icon that can blink."""

    def __init__(self, display_object, svg_icon,
                 pos_x, pos_y, width, height,
                 background_color=(1, 1, 1, 1),
                 on_time=0.5, off_time=0.5):
        """Initialisation of the bliking Icon.

        :param display_object: the Display class instanciation.
        :type display_object: :class:`cairotft.yfy.TftDisplay`
        :param svg_icon: the svg icon to display.
        :type svg_icon: :class:`cairoftf.svg_image.SVGImage`
        :param int pos_x: x coordinates to display the icon
        :param int pos_y: y coordinates to display the icon
        :param int width: the width of the icon
        :param int height: the height of the icon
        :param tuple background_color: a tuple of 4 float representing the
            rgba value of the background color to repaint the icon.
        :param float on_time: the time in s the icon is displayed
        :param float off_time: the time in s the icon is not displayed

        TODO: instead of repainting with a color, save the background before
              painting the icon
        """
        self._stop = False
        self._showing = False
        self.display_object = display_object
        self.svg_icon = svg_icon
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height
        self.background_color = background_color
        self.on_time = on_time
        self.off_time = off_time

    def show(self, ctx):
        """show the icon."""
        if not self._stop:
            self.svg_icon.draw(
                context=ctx,
                pos_x=self.pos_x,
                pos_y=self.pos_y,
                width=self.width,
                height=self.height,
                enlarge=True)
            self.display_object.blit()
            self.display_object.io_loop.call_later(
                self.on_time, self.hide, ctx)

    def hide(self, ctx):
        """hide the icon."""
        if not self._stop:
            ctx.set_source_rgba(*self.background_color)
            ctx.rectangle(self.pos_x, self.pos_y, self.width, self.height)
            ctx.fill()
            self.display_object.blit()

            self.display_object.io_loop.call_later(
                self.off_time, self.show, ctx)
        else:
            self._showing = False

    def start(self, ctx):
        """Start showing the bliking icon."""
        if not self._showing:
            self._showing = True
            self._stop = False
            self.display_object.io_loop.call_soon(
                self.show, ctx)

    def stop(self):
        """stop showing blinking icon."""
        self._stop = True
        self._showing = False
