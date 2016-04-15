from google.appengine.ext.webapp.template import create_template_register

register = create_template_register()

@register.filter(name='split')
def split(value):
    return value.split("\n")

@register.filter
def replace_new_line_with_br(strng):
    return strng.replace("\r\n", "<BR>")