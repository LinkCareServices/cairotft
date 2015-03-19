overview
========

cairotft is a python module used to draw interface on
tft screen using the framebuffer interface.

.. note:: It's not limited strictly to TftDiplays: stricly it's limited to
    framebuffer display (the module could have been called 'cairofb' or
    'cairoframebuffer'

cairotft has a strong dependency on cairocffi
(https://pythonhosted.org/cairocffi/) and you can use the full cairocffi api
in your developments (especially cairocffi.Context and cairocffi.Surface)

for example, to draw a circle, you'll use fully and only cairocffi methods::

    context.set_source_rgba(0, 0, 0, 1)
    context.arc(30, 30, 10, 0, 2 * math.pi)

cairotft works on top of cairocffi and provides these things:

* cairocffi to framebuffer interface bindings, mainly hidden for standard use
  (you only have to paint into your cairo Context)

* double buffering

* widget api and some widget included

* animation framework (for now only very very basic animation bases)

* an async event loop to control all events and display.

More functionnaly will be added later, at this time, cairocffi is at very early
stages of developments.
