"""Signaler class that allows observers thereof to listen to changes."""


import sys


class Signaler:
    """Class that signals observers of methods and attribute setters.

    Args:
        must_listen (bool): If true, raises error if method listener not found
    """
    def __init__(self, must_listen=True):
        super().__init__()
        self.observers = []
        self.must_listen = must_listen

    def _signal(self, *args, **kwargs):
        """Signal a property change to observer listeners."""
        if f_back := sys._getframe().f_back:
            if f_code := f_back.f_code:
                property_ = f_code.co_name  # Name of caller of _signal()
            else:
                return
        else:
            return

        for observer in self.observers:
            listener = getattr(observer, f'{property_}_listener', None)
            if listener:
                listener(*args, **kwargs)
            else:
                if self.must_listen:
                    raise NotImplementedError(f"""\
One or more observer(s) does not have a method `{property_}_listener`, so it \
won't update when {self.__class__.__name__}.{property_} is signaled. \
This is raised because `must_listen=True`. You can suppress it by setting it \
to `False`.""")


class ExampleSignaler(Signaler):
    """Example implementation of Signaler class."""
    def __init__(self, my_attribute, observers: list | None = None):
        super().__init__(must_listen=True)
        if observers:
            self.observers.extend(observers)
        self.my_attribute = my_attribute

    @property
    def my_attribute(self):
        """Example attribute."""
        return self._my_attribute

    @my_attribute.setter
    def my_attribute(self, attribute):
        self._my_attribute = attribute
        self._signal(attribute)


class ExampleListener:
    """Example implementation of a listener of Signaler."""
    def __init__(self):
        pass

    def my_attribute_listener(self, attribute):
        """my_attribute listener.

        Args:
            attribute: Value to observe.
        """
        print(f"my_attribute was set to {attribute}")


if __name__ == "__main__":
    listener = ExampleListener()
    signaler = ExampleSignaler("exampleString")
    signaler.observers.append(listener)
    signaler.my_attribute = "differentExampleString"  # prints 'my_attribute...'
