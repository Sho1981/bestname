from django import forms
from django.conf import settings
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse

from .models import Kanjidata

def boolean(value):
    if value == 'on':
        return True
    else:
        return False

class NameForm(forms.Form):
    lastname = forms.CharField(
            label='姓',
            max_length=10,
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "姓",
            })
    )
    firstname = forms.CharField(
            label='名',
            max_length=10,
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "名",
            })
    )
    sex = forms.ChoiceField(label = '性別', widget=forms.RadioSelect, choices=[
        ('男性', '男性'), ('女性', '女性')
    ])

    def clean(self):
        msgs = []
        last = self.cleaned_data.get('lastname')
        first = self.cleaned_data.get('firstname')

        for char in last:
            try:
                k = Kanjidata.objects.get(figure = char)
#                if not(k.namable()):
#                    msgs.append(forms.ValidationError('『%s』は姓に使用できない文字です。' % char))
            except:
                msgs.append(forms.ValidationError('姓に無効な文字が使われています。'))
                break
        if len(last) > 8:
            msgs.append(forms.ValidationError('姓が長すぎます（8文字以内）。'))

        for char in first:
            try:
                k = Kanjidata.objects.get(figure = char)
                if not(Kanjidata.objects.get(figure = char).namable()):
                    msgs.append(forms.ValidationError('『%s』は名に使用できない文字です。' % char))
            except:
                msgs.append(forms.ValidationError('名に無効な文字が使われています。'))
                break
        if len(first) > 8:
            msgs.append(forms.ValidationError('名が長すぎます（8文字以内）。'))
        
        errorMsgs = []
        print(msgs)
        for _, m in enumerate(msgs):
            if m != None:
                errorMsgs.append(m)

        if len(errorMsgs) != 0:
            raise forms.ValidationError(errorMsgs)

        return self.cleaned_data

class LstrokeSearchForm(forms.Form):
    lastname = forms.CharField(
            label='姓',
            max_length=10,
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "姓",
            })
    )
    sex = forms.ChoiceField(label = '性別', widget=forms.RadioSelect,
        choices=[ ('男性', '男性'), ('女性', '女性') ])

    select_luckyelem = forms.MultipleChoiceField(
        label = '調べる項目（五格＋二運）',
        choices = [ ('0','天格'), ('1','人格'), ('2', '地格'), ('3','総格'),
                    ('4','外格'), ('5','仕事運'), ('6','家庭運')],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'check'}))
    
    choice_type = forms.ChoiceField(
        label = '調べる運勢と個数',
        choices=[('0', '吉以上'), ('1', '大吉')],
        widget=forms.RadioSelect)

    choice_num = forms.ChoiceField(
        choices=[('1', '1つ以上'), ('2', '2つ以上'), ('3', '3つ以上'),
                 ('4', '4つ以上'), ('5', '5つ以上'), ('6', '6つ以上'),
                 ('7', '7つ')])

    choice_unlucky = forms.BooleanField(
        label = '大凶は除く',
        required=False)

class SearchStrokeReadingForm(forms.Form):
    reading = forms.CharField(
            label = '読み',
            max_length=10,
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "読み",
            }),
            required=False
    )
    stroke_choices = [('0', '全て')]
    stroke_choices += [(str(i), str(i)+'画') for i in range(1, 26)]
    select_stroke = forms.ChoiceField(
        label = '画数',
        choices = stroke_choices,
    )

    select_type = forms.MultipleChoiceField(
        label = '漢字の種類',
        choices = [('1','常用'), ('2','人名用'), ('4', 'かな'), ('8','記号')],
        widget=forms.CheckboxSelectMultiple())

class SearchFigureForm(forms.Form):
    figure = forms.CharField(
            label = '漢字',
            max_length=10,
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "漢字一文字",
            })
    )

class ContactForm(forms.Form):
    name = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "お名前",
        }),
    )
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': "メールアドレス",
        }),
    )
    message = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': "お問い合わせ内容",
        }),
    )

    def send_email(self):
        subject = "お問い合わせ"
        message = self.cleaned_data['message']
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        from_email = '{name} <{email}>'.format(name=name, email=email)
        recipient_list = [settings.EMAIL_HOST_USER]  # 受信者リスト
        try:
            send_mail(subject, message, from_email, recipient_list)
        except BadHeaderError:
            return HttpResponse("無効なヘッダが検出されました。")