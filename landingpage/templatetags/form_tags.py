# In your app, create a `templatetags` directory if it doesn't exist and add an `__init__.py` file in it.
# Then create a file named `form_tags.py` and add the following code:

from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})
