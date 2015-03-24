import cairocffi as cairo

from cairotft import svg_image
from cairotft import tft
from cairotft import widgets


class MyDisplay(tft.TftDisplay):

    """Custom display class."""

    def __init__(self, interface='/dev/fb0', cairo_format=cairo.FORMAT_ARGB32,
                 fps=None):
        """Initialisation of the class.

        see :class:`cairotft.widgets.blink_icon.BlinkIcon` for api details.

        Instanciates the blink icon.
        """
        super().__init__(interface=interface,
                         cairo_format=cairo_format,
                         fps=fps)

        # instanciates a blink icon
        self.icon = widgets.BlinkIcon(
            display_object=self,
            pos_x=10,
            pos_y=10,
            width=70,
            height=70,
            svg_icon=svg_image.SVGImage('icon.svg'),
            background_color=(0.5, 0.5, 0.5, 1),
            on_time=0.2,
            off_time=0.8)

    def draw_interface(self, ctx):
        """draw the full interface.

        :param ctx: the cairocffi context.
        :type ctx: :class:`cairocffi.Context`
        """
        # background
        self.blank_screen(ctx=ctx,
                          color=(0.5, 0.5, 0.5, 1),
                          blit=False)

        # start to blink
        self.icon.start(ctx)

        # display on the actual screen
        self.blit()

if __name__ == '__main__':
    disp = MyDisplay()
    disp.run()
