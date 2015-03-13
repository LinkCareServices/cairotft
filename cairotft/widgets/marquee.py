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
"""Text Marquee widget."""
import time

import cairocffi as cairo

from cairotft import linuxfb
from cairotft import transitions


class Marquee():

    """A text marquee widget."""

    def __init__(self, display_object, text,
                 font_face, font_size,
                 text_color,
                 pos_x, pos_y, width, height,
                 background_color=(1, 1, 1, 1),
                 step=1,
                 interval_time=0.05,
                 transition=transitions.LinearTransition.ease_in,
                 smooth=False):
        """Initialisation of the Marquee.

        :param display_object: the Display class instanciation.
        :type display_object: :class:`cairotft.tft.TftDisplay`
        :param str text: the text to display.
        :param font_face: the font face used for the text
        :type font_face: :class:`cairocffi.ToyFontFace`
        :param tuple text_color: a tuple of 4 float representing the rgba
            value of the text color.
        :param int font_size: the size of the font.
        :param int pos_x: x coordinates of the text box (top left corner)
        :param int pos_y: y coordinates of the text box (top left corner)
        :param int width: the width of the text box
        :param int height: the height of the text box
        :param tuple background_color: a tuple of 4 float representing the
            rgba value of the background color to repaint the icon.
        :param int step: number of unit we skip at each frame. (X chars if
            smooth is False, X pixels if smooth is True)
        :param float interval_time: the time in s between two frames

        TODO: instead of repainting with a color, save the background or paint
              in order: from bottom to top.
        """
        self._stop = False
        self._showing = False
        self._pos = 0
        self.display_object = display_object
        self.text = text
        self.full_text = self.text + "   " + self.text
        self._shrinked_text = text
        self.font_face = font_face
        self.font_size = font_size
        self.text_color = text_color
        self.background_color = background_color
        self._old_text_color = text_color
        self._old_background_color = background_color
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height
        self.step = step
        self.smooth = smooth
        self.max_offset = len(self.text) + 3
        self.interval_time = interval_time
        self.transition = transition
        self._transition_time = None
        self._first_time = None
        self._should_scroll = False  # if False, text does not scroll

    def _smooth_init_buffer(self, ctx):
        """Initialise the buffer used in smooth text."""
        # in smooth case, we need to instanciate specific buffers
        # at first, determine the width and height we need:
        ctx.set_font_size(self.font_size)
        ctx.set_font_face(self.font_face)
        (_, _, small_text_width, _,
         x_advance_text, _) = ctx.text_extents(self.text + "   ")
        self.smooth_text_width = int(x_advance_text)
        self.max_offset = self.smooth_text_width

        (_, y_bearing,
         width, height,
         x_advance, _) = ctx.text_extents(self.full_text)
        self.smooth_full_height = int(height)
        self.smooth_full_width = int(max(x_advance, width))
        self.smooth_pos_y = int(-y_bearing)
        stride = cairo.ImageSurface.format_stride_for_width(
            self.display_object.cairo_format, int(x_advance))
        textbuffer = linuxfb.memory_buffer(
            int(stride * self.smooth_full_height))
        self.smooth_textsurf = cairo.ImageSurface(
            format=self.display_object.cairo_format,
            width=self.smooth_full_width,
            height=self.smooth_full_height,
            data=textbuffer,
            stride=stride)
        # if the text does not fit inside the target box, we will scrool it
        if small_text_width > self.width:
            self._should_scroll = True
            self._transition_time = (self.interval_time *
                                     self.smooth_text_width / self.step)

        # creates the context for this memory surface and draw the text
        self.smooth_text_ctx = cairo.Context(self.smooth_textsurf)
        self._smooth_draw_text()

    def _smooth_draw_text(self):
        """draw the text in the smooth text buffer.

        This is not display, only drawed in the smooth buffer.
        """
        # background
        self.smooth_text_ctx.set_source_rgba(*self.background_color)
        self.smooth_text_ctx.rectangle(0,
                                       0,
                                       self.smooth_full_width,
                                       self.smooth_full_height)
        self.smooth_text_ctx.fill()
        # text
        self.smooth_text_ctx.set_font_size(self.font_size)
        self.smooth_text_ctx.set_font_face(self.font_face)
        self.smooth_text_ctx.set_source_rgba(*self.text_color)
        self.smooth_text_ctx.move_to(0, self.smooth_pos_y)
        if self._should_scroll:
            self.smooth_text_ctx.show_text(self.full_text)
        else:
            self.smooth_text_ctx.show_text(self.text)

    def _shrink_text(self, ctx):
        """based on the font size, calculate the width of the text.

        And eventually shrink the name if too long.
        """
        # same font face here than the one displayed.
        if self._pos > 0:
            new_text = (self.full_text)[self._pos:]
        else:
            new_text = self.text[self._pos:]
        while True:
            (_, _, _, _, x_advance, _) = ctx.text_extents(new_text)
            if x_advance > self.width:
                new_text = new_text[:-1]  # + '…'
            else:
                break
        self._shrinked_text = new_text
        if self._shrinked_text != self.text:
            self._should_scroll = True
            self._transition_time = (self.interval_time *
                                     len(self.text + "   ") / self.step)

    def change_color(self, color):
        """Change the text color.

        :param tuple color: a tuple of 4 float representing the
            rgba value of the text color.
        """
        self._old_text_color = self.text_color
        self.text_color = color
        if self.smooth and self._showing:
            self._smooth_draw_text()

    def change_background(self, background_color):
        """Change the background color.

        :param tuple background_color: a tuple of 4 float representing the
            rgba value of the background color to repaint the icon.
        """
        self._old_background_color = self.background_color
        self.background_color = background_color
        if self.smooth and self._showing:
            self._smooth_draw_text()

    def color_changed(self):
        """Return True is either text_color or background_color has changed.

        (since last paint)
        """
        if (self._old_text_color != self.text_color or
                self._old_background_color != self.background_color):
            return True

    def show(self, ctx, no_loop=False):
        """Show the text."""
        if not self._stop and self._showing:
            # here at each frame, move the text and display it.
            if (self.color_changed or self._should_scroll) and not self.smooth:
                # erase the text box
                ctx.set_source_rgba(*self.background_color)
                ctx.rectangle(self.pos_x, self.pos_y, self.width, self.height)
                ctx.fill()

                # display text
                ctx.set_source_rgba(*self.text_color)
                ctx.set_font_size(self.font_size)
                ctx.set_font_face(self.font_face)

                self._shrink_text(ctx)
                ctx.move_to(
                    self.pos_x,
                    (self.pos_y +
                     (self.height - self.font_size) / 2 +
                     self.font_size) - 2)
                ctx.show_text(self._shrinked_text)
                self.display_object.blit()
            elif (self.color_changed or self._should_scroll) and self.smooth:
                # erase the text box
                ctx.set_source_rgba(*self.background_color)
                ctx.rectangle(self.pos_x, self.pos_y, self.width, self.height)
                ctx.fill()
                ctx.set_source_surface(
                    self.smooth_textsurf.create_for_rectangle(
                        self._pos, 0, self.width, self.smooth_full_height),
                    self.pos_x,
                    (self.pos_y +
                     (self.height - self.smooth_full_height) / 2) + 1)
                ctx.paint()
                self.display_object.blit()

            if self._should_scroll:  # only cycle when text is too long.
                now = time.time()
                if self._first_time is not None:
                    transition_offset = self.transition(
                        (now - self._first_time) /
                        self._transition_time)
                else:
                    transition_offset = self.transition(0)
                    self._first_time = now
                self._pos = int(self.max_offset * transition_offset)
                if (now - self._first_time) > self._transition_time:
                    self._first_time = now  # recycle
                    self._pos = int(self.max_offset * self.transition(0))

            self._old_text_color = self.text_color
            self._old_background_color = self.background_color

            if not no_loop:
                self.display_object.io_loop.call_later(
                    self.interval_time, self.show, ctx)

    def start(self, ctx):
        """Start showing the marquee."""
        if not self._showing:
            self._showing = True
            self._stop = False
            self._first_time = None
            if self.smooth:
                self._smooth_init_buffer(ctx)
            else:
                self._shrink_text(ctx)

            self.display_object.io_loop.call_soon(
                self.show, ctx)

    def stop(self):
        """stop showing the marquee."""
        self._stop = True
        self._showing = False
        self._first_time = None
