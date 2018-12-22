from .models import MenuItems

def menu(request):
    return {'menu': MenuItems.objects.filter(is_public=True).order_by('order_number')}

def get_constant(expr):
    constants = {
        'post_not_ready':'Уважаемый читатель! Статья находится в процессе написания и скоро будет закончена. Обязательно возвращайтесь!',
    }
    try:
        return  constants[expr]
    except:
        return ''