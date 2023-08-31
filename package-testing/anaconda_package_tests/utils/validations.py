class Assertions:
    """
    utils to validate the test cases response

    """

    def __init__(self, actual=None, desired=None):
        self.actual = actual
        self.desired = desired

    def arrays_assert_equal(self, err_msg="", verbose=True):
        """
        Raises an AssertionError if two objects are not equal.

        """
        if isinstance(self.desired, dict):
            if not isinstance(self.actual, dict):
                raise AssertionError(repr(type(self.actual)))
            self.arrays_assert_equal(len(self.actual), len(self.desired), err_msg, verbose)
            for k, i in self.desired.items():
                if k not in self.actual:
                    raise AssertionError(repr(k))
                self.arrays_assert_equal(
                    self.actual[k], self.desired[k], f"key={k!r}\n{err_msg}", verbose
                )
            return
        if isinstance(self.desired, (list, tuple)) and isinstance(self.actual, (list, tuple)):
            self.arrays_assert_equal(len(self.actual), len(self.desired), err_msg, verbose)
            for k in range(len(self.desired)):
                self.arrays_assert_equal(
                    self.actual[k], self.desired[k], f"item={k!r}\n{err_msg}", verbose
                )
            return
