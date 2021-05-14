from django import template

register = template.Library() # Djangoのテンプレートタグライブラリ

# カスタムフィルタとして登録する
@register.filter
def lookup(data, key):
    if isinstance(data, list) and isinstance(key, int):
        return data[key]
    if isinstance(data, dict):
        return data[key]
    return None

@register.filter
def make_url_lstroke_result(name, strokes):
    url = name.lastname_text
    url += '_'
    for i in range(3):
        try:
            url += str(strokes[i]) + '_'
        except:
            url += '0_'
    url += name.sex_text
    return url
