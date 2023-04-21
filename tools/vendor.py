# Copyright (C) 2014 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause

#
#  This comes from conda_build/jinja_context.py
#  conda-build has a lot of dependencies and this reduces the overhead
#
import jinja2


class UndefinedNeverFail(jinja2.Undefined):
    """
    A class for Undefined jinja variables.
    This is even less strict than the default jinja2.Undefined class,
    because it permits things like {{ MY_UNDEFINED_VAR[:2] }} and
    {{ MY_UNDEFINED_VAR|int }}. This can mask lots of errors in jinja templates, so it
    should only be used for a first-pass parse, when you plan on running a 'strict'
    second pass later.
    Note:
        When using this class, any usage of an undefined variable in a jinja template is recorded
        in the (global) all_undefined_names class member.  Therefore, after jinja rendering,
        you can detect which undefined names were used by inspecting that list.
        Be sure to clear the all_undefined_names list before calling template.render().
    """

    all_undefined_names = []

    def __init__(
        self,
        hint=None,
        obj=jinja2.runtime.missing,
        name=None,
        exc=jinja2.exceptions.UndefinedError,
    ):
        jinja2.Undefined.__init__(self, hint, obj, name, exc)

    # Using any of these methods on an Undefined variable
    # results in another Undefined variable.
    __add__ = (
        __radd__
    ) = (
        __mul__
    ) = (
        __rmul__
    ) = (
        __div__
    ) = (
        __rdiv__
    ) = (
        __truediv__
    ) = (
        __rtruediv__
    ) = (
        __floordiv__
    ) = (
        __rfloordiv__
    ) = (
        __mod__
    ) = (
        __rmod__
    ) = (
        __pos__
    ) = (
        __neg__
    ) = (
        __call__
    ) = (
        __getitem__
    ) = (
        __lt__
    ) = (
        __le__
    ) = (
        __gt__
    ) = (
        __ge__
    ) = (
        __complex__
    ) = __pow__ = __rpow__ = lambda self, *args, **kwargs: self._return_undefined(
        self._undefined_name
    )

    # Accessing an attribute of an Undefined variable
    # results in another Undefined variable.
    def __getattr__(self, k):
        try:
            return object.__getattr__(self, k)
        except AttributeError:
            self._return_undefined(self._undefined_name + "." + k)

    # Unlike the methods above, Python requires that these
    # few methods must always return the correct type
    __str__ = __repr__ = lambda self: self._return_value("")
    __unicode__ = lambda self: self._return_value("")
    __int__ = lambda self: self._return_value(0)
    __float__ = lambda self: self._return_value(0.0)
    __nonzero__ = lambda self: self._return_value(False)

    def _return_undefined(self, result_name):
        # Record that this undefined variable was actually used.
        UndefinedNeverFail.all_undefined_names.append(self._undefined_name)
        return UndefinedNeverFail(
            hint=self._undefined_hint,
            obj=self._undefined_obj,
            name=result_name,
            exc=self._undefined_exception,
        )

    def _return_value(self, value=None):
        # Record that this undefined variable was actually used.
        UndefinedNeverFail.all_undefined_names.append(self._undefined_name)
        return value
