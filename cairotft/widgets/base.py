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
"""base widget class."""


class BaseWidget():

    """Base class for all widgets.

    :ivar display_object: (:class:`cairotft.tft.TftDisplay`) The display
        object the widget will display itself.
    :ivar pos_x: (:py:class:`int`) x coordinates to display the widget
    :ivar pos_y: (:py:class:`int`) y coordinates to display the widget
    :ivar width: (:py:class:`int`) the width of the widget
    :ivar height: (:py:class:`int`) the height of the widget
    """

    def __init__(self, display_object,
                 pos_x, pos_y, width, height):
        """Initialisation of the base widget.

        :param display_object: the Display class instanciation.
        :type display_object: :class:`cairotft.tfy.TftDisplay`
        :param int pos_x: x coordinates to display the widget
        :param int pos_y: y coordinates to display the widget
        :param int width: the width of the widget
        :param int height: the height of the widget
        """
        self.display_object = display_object
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height

        self._stop = False
        self._showing = False

    def draw(self, ctx):
        """draw the widget.

        implement this method in your subclasses
        """
        raise NotImplementedError

    def show(self, ctx):
        """show the icon."""
        # here call the draw method (which includes the eventual blit)
        self.draw(ctx)

    def start(self, ctx):
        """Start showing the widget."""
        self.display_object.loop.call_soon(
            self.show, ctx)

    def stop(self):
        """stop showing the widget."""
        pass


class BaseAnimatedWidget(BaseWidget):

    """Base class for all Animated widgets.

    see :class:`BaseWidget` for All BaseWidget variables

    :ivar float interval_time: (:py:class:`float`) interval between
        two frames (in seconds)

    TODO: add transition support in BaseAnimatedWidget
    """

    def __init__(self, display_object,
                 pos_x, pos_y, width, height,
                 interval_time=None):
        """Initialisation of the base animated widget.

        :param display_object: the Display class instanciation.
        :type display_object: :class:`cairotft.tfy.TftDisplay`
        :param int pos_x: x coordinates to display the widget
        :param int pos_y: y coordinates to display the widget
        :param int width: the width of the widget
        :param int height: the height of the widget
        :param float interval_time: interval between two frames (in seconds)
            the widget will first:
                try to use the fps parameter  to calculates a display interval
                or: use the given interval_time
                or: fix an interval time of 1second
        """
        super().__init__(display_object, pos_x, pos_y, width, height)

        if self.display_object.fps is not None and interval_time is not None:
            self.interval_time = max(interval_time,
                                     1 / self.display_object.fps)
        elif self.display_object.fps is not None and interval_time is None:
            self.interval_time = 1 / self.display_object.fps
        elif self.display_object.fps is None and interval_time is not None:
            self.interval_time = interval_time
        else:
            self.interval_time = 1

        self._stop = False
        self._showing = False

    def draw(self, ctx):
        """draw the widget.

        implement this method in your subclasses
        """
        raise NotImplementedError

    def show(self, ctx):
        """show the icon."""
        if not self._stop:
            # here call the draw method (which includes the eventual blit)
            self._showing = True
            self.draw(ctx)
            # the call the next show
            self.display_object.loop.call_later(
                self.interval_time, self.show, ctx)

    def start(self, ctx):
        """Start showing the widget."""
        if not self._showing:
            self._showing = True
            self._stop = False
            self.display_object.loop.call_soon(
                self.show, ctx)

    def stop(self):
        """stop showing the widget."""
        self._stop = True
        self._showing = False
