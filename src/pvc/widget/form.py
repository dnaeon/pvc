"""
Docstring should go here

"""

from pvc.exceptions import GenericException

__all__ = ['Form', 'FormElement']


class FormElement(object):
    def __init__(self, label, item, xi=20, field_length=60, input_length=0, attributes=0x0):
        """
        A form element

        Args:
           label       (str): Label of the element
           item        (str): Initial value for the element
           xi          (int): Display item value in column 'xi'
           field_lenght(int): Number of characters used to display the item
           field_input (int): Input field characters
           attributes  (int): A bitmask used for elements used in mixed forms

        """
        self.label = label
        self.item = item
        self.xi = xi
        self.field_length = field_length
        self.input_length = input_length
        self.attributes = attributes

class Form(object):
    def __init__(self, dialog, form_elements, title='', text='', height=0, width=0, form_height=0, mixed_form=False):
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
        self.title = title
        self.text = text
        self.height = height
        self.width = width
        self.form_height = form_height
        self.mixed_form = mixed_form
        self._labels = [e.label for e in self.form_elements]

        if self.mixed_form:
            self.form = self.dialog.mixedform
            self._elements = [(e.label, row + 1, 1, e.item, row + 1, e.xi, e.field_length, e.input_length, e.attributes) for row, e in enumerate(self.form_elements)]
        else:
            self.form = self.dialog.form
            self._elements = [(e.label, row + 1, 1, e.item, row + 1, e.xi, e.field_length, e.input_length) for row, e in enumerate(self.form_elements)]

    def display(self):
        """
        docstring

        """
        code, items = self.form(
            title=self.title,
            text=self.text,
            elements=self._elements,
            height=self.height,
            width=self.width,
            form_height=self.form_height
        )

        result = (code, {l:i for l, i in zip(self._labels, items)})

        return result
