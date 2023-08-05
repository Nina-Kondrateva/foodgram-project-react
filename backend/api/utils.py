from django.http import HttpResponse


def download(ingredients_list):
    new_list = 'Список покупок: \n'
    for ingredient in ingredients_list:
        new_list += (f'{ingredient["ingredients__name"]} - '
                     f'{ingredient["amount"]} '
                     f'{ingredient["ingredients__measurement_unit"]} \n')
    response = HttpResponse(new_list, 'Content-Type: text/plain')
    response['Content-Disposition'] = ('attachment; '
                                       'filename="buylist.txt"')
    return response
