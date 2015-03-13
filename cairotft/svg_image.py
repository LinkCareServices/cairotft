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
"""Load an display a svg image in cairo context.

This module is a modified version of the svg_image module from
WeasyPrint:
https://github.com/Kozea/WeasyPrint/blob/master/weasyprint/images.py#L99
"""
import cairosvg.parser
import cairosvg.surface


class ImageLoadingError(ValueError):

    """An error occured when loading an image.

    The image data is probably corrupted or in an invalid format.
    """

    @classmethod
    def from_exception(cls, exception):
        """Instanciate the class with the given exception."""
        name = type(exception).__name__
        value = str(exception)
        return cls('%s: %s' % (name, value) if value else name)


class ScaledSVGSurface(cairosvg.surface.SVGSurface):

    """Have the cairo Surface object have dimension in px instead of pt."""

    @property
    def device_units_per_user_units(self):
        """Force an eventual new scale.

        In this case, does nothing new.
        """
        scale = super().device_units_per_user_units
        return scale / 1


class SVGImage():

    """SVGImage class."""

    def __init__(self, base_url, svg_data=None):
        """Initialisation of the class.

        :param str base_url: path to a SVG Image.
        :param svg_data: bytestring containing the svg datas.

        You can either provide a base_url, in this case, the file will be
        loaded, or directly use svg_data with a svg content.
        """
        # Don’t pass data URIs to CairoSVG.
        # They are useless for relative URIs anyway.
        self._base_url = (
            base_url if not base_url.lower().startswith('data:') else None)
        self._svg_data = svg_data

        try:
            # cache the rendering
            self._svg = self._render()
        except Exception as exc:
            raise ImageLoadingError.from_exception(exc)
        # TODO: support SVG images with none or only one of intrinsic
        #       width, height and ratio.
        if not (self._svg.width > 0 and self._svg.height > 0):
            raise ImageLoadingError(
                'SVG images without an intrinsic size are not supported.')
        self.intrinsic_width = self._svg.width
        self.intrinsic_height = self._svg.height
        self.intrinsic_ratio = self.intrinsic_width / self.intrinsic_height

    def get_intrinsic_size(self, _image_resolution):
        """Return a tuple: (intrinsic_width, intrinsic_height)."""
        # Vector images are affected by the 'image-resolution' property.
        return self.intrinsic_width, self.intrinsic_height

    def _render(self):
        """Draw to a cairo surface but do not write to a file.

        This is a CairoSVG surface, not a cairo surface.
        """
        return ScaledSVGSurface(
            cairosvg.parser.Tree(
                bytestring=self._svg_data, url=self._base_url),
            output=None, dpi=96)

    @staticmethod
    def _scale_to_fit(image, frame, enlarge=False):
        """scale an image always keeping aspect ratio inside the frame.

        :param image: tuple of int (width, eight)
        :param fram: tuple of int (width, eight)
        :param bool enlarge: if True, do not only shrink, also enlarge.

        :returns= a (widht, eight) tuple representing the target size of the
            object.
        (thanks to jon for this method)
        """
        image_width, image_height = image
        frame_width, frame_height = frame
        image_aspect = float(image_width) / image_height
        frame_aspect = float(frame_width) / frame_height
        # Determine maximum width/height (prevent up-scaling).
        if not enlarge:
            max_width = min(frame_width, image_width)
            max_height = min(frame_height, image_height)
        else:
            max_width = frame_width
            max_height = frame_height
        # Frame is wider than image.
        if frame_aspect > image_aspect:
            height = max_height
            width = int(height * image_aspect)
        # Frame is taller than image.
        else:
            width = max_width
            height = int(width / image_aspect)
        return (width, height)

    def draw(self, context, pos_x, pos_y,
             width, height, enlarge=True, center_y=False):
        """Draw the svg image inside a box of size (width, eight).

        This draw methods keeps automatically the aspect ration of the image.

        :param context: cairo context
        :param int pos_x: x position (top left corner)
        :param int pos_y: y position (top left corner)
        :param int width: width of the box the image will fit inside
        :param int height: height of the box the image will fit inside
        :param bool enlarge: if true and if the base image is smaller than
            the box, it will enlarge the image. If False, display the original
            smaller image.
        :param bool center_y: if True add an offset to y in order to center
            the image into the box.
        """
        # svg = self._render()
        svg = self._svg  # use cached version
        image_width, image_height = self._scale_to_fit(
            image=(svg.width, svg.height),
            frame=(width, height),
            enlarge=enlarge)
        xratio = image_width / svg.width
        yratio = image_height / svg.height
        if center_y:
            y_offset = int((height - image_height) / 2)
        else:
            y_offset = 0
        context.scale(xratio, yratio)
        context.set_source_surface(svg.cairo,
                                   pos_x / xratio,
                                   (pos_y + y_offset) / yratio)
        context.paint()
        # reset the scale
        context.scale(1 / xratio, 1 / yratio)
