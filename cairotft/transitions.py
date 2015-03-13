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
"""Transitions classes.

The Transitions are used in animations to calculates new object positions
based on some parameters like transition time, transition type, etc...

Idea and implementation is taken from mootools Fx project:
https://github.com/mootools/mootools-core/blob/master/Source/Fx/Fx.Transitions.js

see: http://www.chipwreck.de/blog/2010/02/17/mootools-transitions-explained/
"""
import math


class BaseTransition():

    """Base class for all transitions.

    This class will be subclassed by every transition type.
    """

    @classmethod
    def ease_in(cls, progress=0):
        """Method to calculate transition for easeIn display.

        Ease in is the default behaviour: Here the function is applied
        normally.
        """
        return cls.pos(progress)

    @classmethod
    def ease_out(cls, progress=0):
        """Method to calculate transition for easeOut display.

        Ease out inverts the behaviour - so the effect works backwards.
        """
        return 1 - cls.pos(1 - progress)

    @classmethod
    def ease_in_out(cls, progress=0):
        """Method to calculate transition for easeInOut display.

        Ease in and out is more complex:
            In the first half of the time the transition is applied normally,
            in the second half it is applied reverse.
        """
        if progress <= 0.5:
            return cls.pos(2 * progress) / 2
        else:
            return 2 - cls.pos(2 * (1 - progress)) / 2

    @classmethod
    def pos(cls, progress=0):
        """calculate pos based on progress value, progress is between 0 and 1.

        :param float progress: the wanted progression of the transition.
            0 is the 'beginning' of the transition, i.e. 0% of the transition
            1 is the 'end' of the transition, i.e. 100% of the transition.

        This method is defined in subclasses based on the transition type.
        """
        raise NotImplementedError


class LinearTransition(BaseTransition):

    """Simple linear transition.

    A linear transition has no additional ease-parameter,
    since it simply divides the range equally along the timeline.
    """

    @classmethod
    def pos(cls, progress=0):
        """calculate pos based on progress value, progress is between 0 and 1.

        :param float progress: the wanted progression of the transition.
        """
        return progress


class QuadTransition(BaseTransition):

    """Quad (x^2) transition.

    Polynomial (x^n) Transition.
    For these transition the value will first increase slowly and near
    the end of the effect it will grow rapidly - like the well-known parabola.
    """

    @classmethod
    def pos(cls, progress=0):
        """calculate pos based on progress value, progress is between 0 and 1.

        :param float progress: the wanted progression of the transition.
        """
        return math.pow(progress, 2)


class CubicTransition(BaseTransition):

    """Cubic (x^3) transition.

    Polynomial (x^n) Transition.
    For these transition the value will first increase slowly and near
    the end of the effect it will grow rapidly - like the well-known parabola.
    """

    @classmethod
    def pos(cls, progress=0):
        """calculate pos based on progress value, progress is between 0 and 1.

        :param float progress: the wanted progression of the transition.
        """
        return math.pow(progress, 3)


class QuartTransition(BaseTransition):

    """x^4 transition.

    Polynomial (x^n) Transition.
    For these transition the value will first increase slowly and near
    the end of the effect it will grow rapidly - like the well-known parabola.
    """

    @classmethod
    def pos(cls, progress=0):
        """calculate pos based on progress value, progress is between 0 and 1.

        :param float progress: the wanted progression of the transition.
        """
        return math.pow(progress, 4)


class QuintTransition(BaseTransition):

    """x^5 transition.

    Polynomial (x^n) Transition.
    For these transition the value will first increase slowly and near
    the end of the effect it will grow rapidly - like the well-known parabola.
    """

    @classmethod
    def pos(cls, progress=0):
        """calculate pos based on progress value, progress is between 0 and 1.

        :param float progress: the wanted progression of the transition.
        """
        return math.pow(progress, 5)


class PowTransition(BaseTransition):

    """x^6 transition.

    Polynomial (x^n) Transition.
    For these transition the value will first increase slowly and near
    the end of the effect it will grow rapidly - like the well-known parabola.
    """

    @classmethod
    def pos(cls, progress=0):
        """calculate pos based on progress value, progress is between 0 and 1.

        :param float progress: the wanted progression of the transition.
        """
        return math.pow(progress, 6)


class ExpoTransition(BaseTransition):

    """Exponancial transition.

    So the function grows even more rapidly towards the end -
    compared to the x^n-transitions.
    """

    @classmethod
    def pos(cls, progress=0):
        """calculate pos based on progress value, progress is between 0 and 1.

        :param float progress: the wanted progression of the transition.
        """
        return math.pow(2, 8 * (progress - 1))


class CircTransition(BaseTransition):

    """Circular transition.

    The circular transition function describes a perfect circle
    (in this case a quadrant)
    """

    @classmethod
    def pos(cls, progress=0):
        """calculate pos based on progress value, progress is between 0 and 1.

        :param float progress: the wanted progression of the transition.
        """
        return 1 - math.sin(math.acos(progress - 1))


class SineTransition(BaseTransition):

    """Sinus transition.

    The sinusiodal transition delivers a graph which behaves like a part
    of a sine-curve, the result in this case is a smooth, nearly linear
    transition (see the graph below).
    """

    @classmethod
    def pos(cls, progress=0):
        """calculate pos based on progress value, progress is between 0 and 1.

        :param float progress: the wanted progression of the transition.
        """
        return 1 - math.cos(progress * math.pi / 2)


class BackTransition(BaseTransition):

    """Back transition.

    Back moves the value first in the opposite direction
    and then moves it in direction of the target value.
    """

    @classmethod
    def pos(cls, progress=0):
        """calculate pos based on progress value, progress is between 0 and 1.

        :param float progress: the wanted progression of the transition.
        """
        return math.pow(progress, 2) * (2.618 * progress - 1.618)


class BounceTransition(BaseTransition):

    """Bounce transition.

    Bounce is the most complex function - it can’t be described as a
    simple formula.
    It first approaches the target value linear and then it oscillates between
    descreasing intervals, creating a bouncing effect.
    """

    @classmethod
    def pos(cls, progress=0):
        """calculate pos based on progress value, progress is between 0 and 1.

        :param float progress: the wanted progression of the transition.
        """
        value = 0
        p_a = 0
        p_b = 1
        while True:
            if progress >= (7 - 4 * p_a) / 11:
                value = p_b * p_b - math.pow(
                    (11 - 6 * p_a - 11 * progress) / 4, 2)
                break
            p_a += p_b
            p_b /= 2
        return value


class ElasticTransition(BaseTransition):

    """Elastic transition.

    Elastic oscillates in increasing intervals between the opposite direction
    and the desired one. It’s best used with ease:out or ease:in:out,
    otherwise it may happen that effect doesn’t reach its target value.
    """

    @classmethod
    def pos(cls, progress=0):
        """calculate pos based on progress value, progress is between 0 and 1.

        :param float progress: the wanted progression of the transition.
        """
        return math.pow(2, 10 * (progress - 1)) * math.cos(
            20 * progress * math.pi * 1 / 3)
