"""
Docstring should be here

"""

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
            raise TypeError('Need a callable for item callback')

    def selected(self):
        if self.on_select_args:
            return self.on_select(*self.on_select_args)
        else:
            return self.on_select()


class Menu(object):
    def __init__(self, items, dialog, **kwargs):
        """
        Menu class

        Args:
            items           (list): A list of MenuItem instances
            dialog (dialog.Dialog): A Dialog instance
            kwargs          (dict): Additional args to be passed to dialog(1)

        """
        self.items = items
        self.dialog = dialog
        self.kwargs = kwargs
        self.choices = [(item.tag, item.description) for item in self.items]
        self._registry = {item.tag: item for item in items}

    def display(self):
        default_item = ''
        while True:
            code, tag = self.dialog.menu(
                choices=self.choices,
                default_item=default_item,
                **self.kwargs
            )

            if code in (self.dialog.CANCEL, self.dialog.ESC):
                break

            item = self._registry.get(tag)
            default_item = tag

            if not item.on_select:
                self.dialog.msgbox('Not implemented')
            else:
                item.selected()
