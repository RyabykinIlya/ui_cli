from .models import MenuItems
import re

def menu(request):
    menu_items = MenuItems.objects.filter(is_public=True).order_by('order_by')
    '''
    for special needs, creates individual link for users
    usage: create menu item with link like 'com/cat/<user>'
    for item in menu_items:
        if re.search('<user>', item.link):
            item.link = re.sub('<user>', request.user.username, item.link)
    '''
    return {'menu': menu_items}


def get_constant(expr):
    constants = {
        'post_not_ready': 'Some text',
    }
    try:
        return constants[expr]
    except:
        return ''
