how to use the cairotft module
==============================

simple usage
------------

Basic use is to simply subclass :class:`cairotft.tft.TftDisplay` and
overwrite the draw_interface method:

.. literalinclude:: examples/simple/simple.py
   :language: python
   :linenos:

.. note:: you may need to be root to access to the framebuffer device.

Some Explanations
*****************

* you can see that TftDisplay provides some basic method to interact with the
  screen.
  In line 15 self.blank_screen repaint the whole screen with the selected color.
  (more about blit=False later)

* by default, TftDisplay automatically discover the screen size. you can access
  to the size (in pixels) with `self.width` and `self.height` properties.

  We use that capability for drawing the second rectange on line 21.

* at the end of the draw_interface method, we call self.blit():
  By default, the loop calls self.draw_interface with a cairo
  context pointing to a memory buffer, not the actual screen buffer (this is
  called double buffering).

  Calling self.blit() copy the content of the memory buffer into
  the screen buffer (and this is only at that time that the
  screen is showing something)

  .. note:: currently, you're responsible of calling self.blit() when you want
     to repaint the screen. You can call self.blit() when you want, but beware
     of the performances (of your system and of your screen)

* On this example, the screen is drawed only one time (then the event loop
  is only looping forever without doing anything).
  We'll cover this on later examples, but you're also
  responsible to handle events in the event loop.
  Events may draw/redraw some object and then call blit()

Run
***

you can run this simple example from the cairotft main dir::

    sudo python docs/examples/simple/simple.py

This will start the program on /dev/fb0.
To see something, you'll need to switch on a linux console (if you're currently
under X):

    * hit: CTRL + ALT + F2
    * log-in and go to the cairotft directory
    * acivate your virtualenv::

        source ~/.virtualenvs/cairotft/bin/activate

    * launch the sample program::

        sudo python docs/examples/simple/simple.py

    * it should display a big red rectangle on top of a grey screen
    * hit CTRL + c to terminate the program
    * hit again CTRL + ALT + F7
      (or sometimes, depending on you system: CTRL + ALT + F1) to go back to X
    * if CTRL + ALT + Fx does not work on your system, you can use the chvt
      command::

        sudo chvt 7

      or::

        sudo chvt 1

      to go back into X

Result
******

.. image:: examples/simple/simple.png
