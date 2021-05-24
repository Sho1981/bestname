from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.db.models import Q
import re
import jaconv

from . import forms
from .models import Kanjidata
from .extensions import NameLparam, NameLstroke
from .constants import TABLE

# Create your views here.

class TopView(TemplateView):
    template_name = "newname/top.html"    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = forms.NameForm()
        return context

class NameJudgeView(FormView):
    form_class = forms.NameForm
    success_url = '../lparam_result'
    def form_valid(self, form):
        kwargs = {  'lastname'  : form.data.get('lastname'),
                    'firstname' : form.data.get('firstname'),
                    'sex' : form.data.get('sex')}
        return HttpResponseRedirect(reverse('newname:lparam_result',
                                             kwargs=kwargs))
    def render_to_response(self, context, **response_kwargs):
        self.template_name = "newname/top.html"
        return super().render_to_response(context, **response_kwargs)

class LparamResultView(TemplateView):
    template_name = 'newname/lparam_result.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            name = NameLparam( lastname_text = context['lastname'],
                         firstname_text = context['firstname'],
                         sex_text = context['sex'])
            if name.available():
                ft_dict = name.get_fortune_telling_dict(key = 'html')
                context = { 'form' : forms.NameForm(),
                            'name' : name,
                            'ft_dict' : ft_dict,
                            'key' : 'lparam'}
            else:
                context = { 'form' : forms.NameForm(),
                        'error_message' : 'エラー：名前に使用できない文字が入力されました。'}
                self.template_name = 'newname/top.html'               
        except:
            context = { 'form' : forms.NameForm(),
                        'error_message' : 'エラー：無効な文字が入力されました。'}
            self.template_name = 'newname/top.html'
        return context

class LstrokeSearchView(FormView):
    template_name = 'newname/lstroke_search.html'
    form_class = forms.LstrokeSearchForm
    success_url = '../lstroke_search'
    ots_before = {'lastname': '', 'ots': {}}

    def form_valid(self, form):
        try:
            name = NameLstroke( lastname_text = form.data.get('lastname'),
                                firstname_text = 'ー', #仮で記号の『ー』を代入
                                sex_text = form.data.get('sex') )
        except:
            kwargs = {  'form'  : forms.LstrokeSearchForm(),
                        'error_message' : '無効な文字が入力されました。' }
            return self.render_to_response(self.get_context_data(**kwargs))
        if (self.ots_before['lastname'] == name.lastname_text):
            ots = self.ots_before['ots']
        else:
            ots = name.get_original_luckylist_table(max_stroke = 25)
            self.ots_before['lastname'] = name.lastname_text
            self.ots_before['ots'] = ots

        lucky_tables = { "%sさんの検索結果" %  name.lastname_text :
                          self.get_luckystroke_table(ots, form)}
        kwargs = {  'form'  : form,
                    'lucky_tables' : lucky_tables,
                    'name' : name
                 }
        return self.render_to_response(self.get_context_data(**kwargs))

    def get_luckystroke_table(self, original_tables, form):
        luckystroke_table = {}
        for n, ot in original_tables.items():
            luckystroke_table[n] = self.get_luckystroke_list(ot, form)
        return luckystroke_table

    def get_luckystroke_list(self, original_table, form):
        if int(form.data.get('choice_type')):
            values = ['大吉']
        else:
            values = ['吉', '大吉']
        luckystroke_list =\
            sorted(
                [st for st, lucks in original_table.items()
                    if ((
                        not (forms.boolean(form.data.get('choice_unlucky'))
                         * ("大凶" in lucks)))
                        & self.match_value_at_some_indexes_in_list(
                         lucks,
                         values,
                         [int(i) for i in form.cleaned_data['select_luckyelem']],
                         int(form.data.get('choice_num'))))],
                key=lambda x: sum([i for i in x]))
        return luckystroke_list

    def match_value_at_some_indexes_in_list(self, l, values, indexes, num):
        if [(l[index] in values) for index in indexes].count(True) >= num:
            return True
        else:
            return False
    
class LstrokeResultView(TemplateView):
    template_name = 'newname/lstroke_result.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        f_strokes = get_f_strokes([context['first'], context['second'], context['third']])
        firstname = get_firstname(f_strokes)
        try:
            name = NameLparam( lastname_text = context['lastname'],
                         firstname_text = firstname,
                         sex_text = context['sex'])
            name.f_strokes = f_strokes
            name.lucky_table = name.make_luckytable()
            kanji_dict = {}
            for stroke in set(f_strokes):
                kanji_dict[stroke] = get_kanji_by_stroke_reading('', stroke, int_to_max_bit(15, 4))
            if name.available():
                ft_dict = name.get_fortune_telling_dict(key = 'html')
                context = { 'name' : name,
                            'ft_dict' : ft_dict,
                            'kanji_dict' : kanji_dict,
                            'key' : 'lstroke' }
            else:
                context = { 'form' : forms.NameForm(),
                        'error_message' : 'エラー：無効な文字が入力されました。'}
                self.template_name = 'newname/top.html'               
        except:
            context = { 'form' : forms.NameForm(),
                        'error_message' : 'エラー：無効な文字が入力されました。'}
            self.template_name = 'newname/top.html'
        return context

class SearchStrokeReadingView(FormView):
    template_name = 'newname/search_strokereading.html'
    form_class = forms.SearchStrokeReadingForm
    success_url = '../strokereading/'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        if 'stroke' not in kwargs:
            return super().get_context_data(**kwargs)
        if 'reading' in kwargs:
            reading = kwargs['reading']
            if not re.compile(r'[ぁ-ん]+').fullmatch(reading):
                kwargs['error_message'] = 'エラー：読みはひらがなで入力してください。'
                return super().get_context_data(**kwargs)
        else:
            reading = ''
        choice_stroke = kwargs['stroke']
        choice_types = int_to_max_bit(kwargs['types'], 4)
        if (choice_stroke == 0) & (reading == ''):
            kwargs['error_message'] = 'エラー：読みか画数のいずれかは必須です。'
            return super().get_context_data(**kwargs)
        kanji_list = get_kanji_by_stroke_reading(reading, choice_stroke, choice_types)
        kwargs['form'] = self.get_form()
        kwargs['reading'] = reading
        kwargs['choice_stroke'] = choice_stroke
        kwargs['kanji_list'] = kanji_list        
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        kwargs = { 'stroke' : form.data.get('select_stroke'),
                   'types' : bitlist_to_int(form.cleaned_data['select_type'])}
        if form.data.get('reading'):
            kwargs['reading'] = form.data.get('reading')
            return HttpResponseRedirect(reverse('newname:kanjisearch_strokereading_result', kwargs=kwargs))
        return HttpResponseRedirect(reverse('newname:kanjisearch_stroke_result', kwargs=kwargs))

class SearchFigureView(FormView):
    template_name = 'newname/search_figure.html'
    form_class = forms.SearchFigureForm
    success_url = '../figure/'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        if 'figure' not in kwargs:
            return super().get_context_data(**kwargs)
        kwargs['form'] = self.get_form()
        figure = kwargs['figure']
        try:
            kanji = Kanjidata.objects.get(figure=figure)
        except:
            kwargs['error_message'] = 'エラー：無効な文字が入力されました。'
            return super().get_context_data(**kwargs)                    
        kwargs['kanji'] = kanji
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        kwargs = { 'figure' : form.data.get('figure') }
        return HttpResponseRedirect(reverse('newname:kanjisearch_figure_result', kwargs=kwargs))

class ContactFormView(FormView):
    template_name = 'newname/contact_form.html'
    form_class = forms.ContactForm
    success_url = reverse_lazy('newname:contact_result')

    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)

class ContactResultView(TemplateView):
    template_name = 'newname/contact_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['success'] = "お問い合わせは正常に送信されました。"
        return context

class AboutUsView(TemplateView):
    template_name = 'newname/about_us.html'

class ParametersExplainView(TemplateView):
    template_name = 'newname/parameter_explain.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tab = {'大吉':[], '吉':[], '凶':[], '大凶':[]}
        for i in range(1, 82):
            tab[TABLE[i]].append(i)
        context['tab'] = tab
        return context

class TestSpaceView(TemplateView):
    template_name = "newname/test_space.html"    

#####################
#                   #
# Sub Functions     #
#                   #
#####################
    
def get_firstname(stroke_list):
    return ''.join(['一' for stroke in stroke_list])

def get_f_strokes(stroke_list):
    return [stroke for stroke in stroke_list if stroke]

def int_to_max_bit(num, length):
    """
    15 -> ['1','2','4','8'] etc.
    """
    if num >= 2**length:
        return [None]
    if num == 1:
        return [str(num)]
    a = 2**(length-1)
    if num > a:
        return sorted([str(a)] + int_to_max_bit(num - a, length-1))
    elif num == a:
        return [str(a)]
    else:
        return int_to_max_bit(num, length-1)

def bitlist_to_int(bitlist):
    """
    ['1','2','4','8'] -> 15 etc.
    """
    return sum([int(b) for b in bitlist])

def get_kanji_by_stroke_reading(reading_hira, stroke, types):
    kanji_list = []
    qr_kun = Q()
    qr_on = Q()
    qstroke = Q()
    if reading_hira != '':
        reading_kata = jaconv.hira2kata(reading_hira)
        qr_kun = Q(reading_kunyomi__contains=reading_hira)
        qr_on = Q(reading_onyomi__contains=reading_kata)
        for i in range(1, len(reading_hira)):
            rhi = reading_hira[:i] + '（' + reading_hira[i:] + '）'
            rki = reading_kata[:i] + '（' + reading_kata[i:] + '）'
            qr_kun_i = Q(reading_kunyomi__contains=rhi)
            qr_on_i = Q(reading_onyomi__contains=rki)
            qr_kun = qr_kun | qr_kun_i
            qr_on = qr_on | qr_on_i
    qreading = qr_kun | qr_on
    if stroke:
        qstroke = Q(stroke=stroke)
    for t in types:
        if t == '1':
            qtype = Q(joyo=1)
        if t == '2':
            qtype = Q(jinmeiyo=1)
        if t == '4':
            qtype = Q(kana=1)
        if t == '8':
            qtype = Q(kigou=1)
        qset = Kanjidata.objects.filter(qreading & qstroke & qtype)
        kanji_list += list(qset.values_list('figure', flat=True))
    return kanji_list
