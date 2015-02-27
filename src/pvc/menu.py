"""
Docstring should be here

"""

from pvc.exceptions import GenericException

__all__ = ['Menu', 'MenuItem']


class MenuItem(object):
    def __init__(self, tag, description, on_select=None, on_select_args=None):
        """
        A menu item

        Args:
            tag                 (str): Unique tag name for the menu item
            description         (str): Short description of the item
            on_select      (callable): A callable to execute when the item is selected
            on_select_args    (tuple): Args to pass to the callable if the item has been selected

        """
        self.tag = tag
        self.description = description
        self.on_select = on_select
        self.on_select_args = on_select_args

        if self.on_select and not callable(self.on_select):
            raise GenericException('Need a callable for item callback')

    def selected(self):
        self.on_select(*self.on_select_args)

class Menu(object):
    def __init__(self, text, items, dialog):
        """
        Menu class

        Args:
            text             (str): Text to display in the menu box
            items           (list): List of MenuItem instances
            dialog (dialog.Dialog): Dialog instance

        """
        self.text = text
        self.items = items
        self.dialog = dialog
        self.choices = [(item.tag, item.description) for item in self.items]
        self._registry = {item.tag: item for item in items}

    def display(self):
        while True:
            code, tag = self.dialog.menu(
                text=self.text,
                choices=self.choices
            )

            if code in (self.dialog.CANCEL, self.dialog.ESC):
                break

            item = self._registry.get(tag)
            item.selected()
