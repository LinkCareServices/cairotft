from cairotft import tft


class MyDisplay(tft.TftDisplay):

    """Custom display class."""

    def draw_interface(self, ctx):
        """draw the full interface.

        :param ctx: the cairocffi context.
        :type ctx: :class:`cairocffi.Context`
        """
        # background
        self.blank_screen(ctx=ctx,
                          color=(0.5, 0.5, 0.5, 1),
                          blit=False)

        # draw red a rectangle inside the screen
        ctx.set_source_rgba(1, 0, 0, 1)
        ctx.rectangle(50, 50, self.width - 50 * 2, self.height - 50 * 2)
        ctx.fill()

        # display on the actual screen
        self.blit()

if __name__ == '__main__':
    disp = MyDisplay()
    disp.run()
