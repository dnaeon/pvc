"""
Docstring should go here

"""

from pvc.exceptions import GenericException

__all__ = ['Form', 'FormElement']


class FormElement(object):
    def __init__(self, label, item, xi=20, field_length=60, input_length=0):
        """
        docstring

        """
        self.label = label
        self.item = item
        self.xi = xi
        self.field_length = field_length
        self.input_length = input_length

class Form(object):
    def __init__(self, dialog, form_elements, title='', text='', height=0, width=0, form_height=0):
        """
        A form widget

        Args:
            dialog   (dialog.Dialog): A Dialog instance
            elements          (list): A list of FormElement instances to display
            title              (str): Title of the form
            text_              (str): Text to display in the form
            height             (int): Height of the box
            width              (int): Width of the box
            form_height        (int): Number of lines displayed at the same time

        """
        self.dialog = dialog
        self.form_elements = form_elements
        self._labels = [e.label for e in self.form_elements]
        self._elements = [(element.label, row + 1, 1, element.item, row + 1, element.xi, element.field_length, element.input_length) for row, element in enumerate(self.form_elements)]
        self.title = title
        self.text = text
        self.height = height
        self.width = width
        self.form_height = form_height

    def display(self):
        """
        docstring

        """
        code, items = self.dialog.form(
            title=self.title,
            text=self.text,
            elements=self._elements,
            height=self.height,
            width=self.width,
            form_height=self.form_height
        )

        result = (code, {l:i for l, i in zip(self._labels, items)})

        return result
