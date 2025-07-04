from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})
<<<<<<< HEAD

@register.filter
def dict_get(d,key):
    return d.get(key)
=======
>>>>>>> 87dd47473da2f5106596a68cfea294ccf720d0c4
