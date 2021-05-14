from django.db import models
import re

# Create your models here.

class Name(models.Model):
    lastname_text = models.CharField(max_length=10)
    firstname_text = models.CharField(max_length=10)
    sex_text = models.CharField(max_length=4)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setting()

    def __str__(self):
        return '%s %s (%s)' %\
                    (self.lastname_text, self.firstname_text, self.sex_text)

    def _setting(self):
        self.l_kanjidata = [Kanjidata.objects.get(figure = char)
                                        for char in self.lastname_text]
        self.f_kanjidata = [Kanjidata.objects.get(figure = char)
                                        for char in self.firstname_text]
        self.l_strokes = [k.stroke for k in self.l_kanjidata]
        self.f_strokes = [k.stroke for k in self.f_kanjidata]
        if not(self.sex_text in ['男性', '女性']):
            raise ValueError
        self._l_length = len(self.lastname_text)
        self._f_length = len(self.firstname_text)
    
    def available(self):
        nb = 1
        for kanji in (self.l_kanjidata + self.f_kanjidata):
            nb *= kanji.namable()
        return bool(nb)

    def _tenkaku(self):
        if self._l_length == 1:
            return self.l_strokes[0] + 1
        else:
            return sum(self.l_strokes)

    def _jinkaku(self):
        return self.l_strokes[-1] + self.f_strokes[0]

    def _chikaku(self):
        if self._f_length == 1:
            return self.f_strokes[0] + 1
        else:
            return sum(self.f_strokes)

    def _soukaku(self):
        return sum(self.l_strokes) + sum(self.f_strokes)

    def _gaikaku(self):
        g = self._soukaku() - self._jinkaku()
        if self._l_length == 1:
            g += 1
        if self._f_length == 1:
            g += 1
        return g

    def _shigotoun(self):
        s = self._soukaku()
        if self._l_length == 1:
            s += 1
        if self._f_length > 1:
            s -= self.f_strokes[-1]
        return s

    def _kateiun(self):
        k = self._soukaku()
        if self._l_length > 1:
            k -= self.l_strokes[0]
        if self._f_length == 1:
            k += 1
        return k
    
    def _make_luckynumber(self):
        self.ten = self._tenkaku()
        self.jin = self._jinkaku()
        self.chi = self._chikaku()
        self.sou = self._soukaku()
        self.gai = self._gaikaku()
        self.shigoto = self._shigotoun()
        self.katei = self._kateiun()

class Kanjidata(models.Model):
    id = models.IntegerField(blank=True, primary_key=True)
    figure = models.TextField(blank=True, null=True)
    stroke = models.IntegerField(blank=True, null=True)
    joyo = models.IntegerField(blank=True, null=True)
    jinmeiyo = models.IntegerField(blank=True, null=True)
    kana = models.IntegerField(blank=True, null=True)
    kigou = models.IntegerField(blank=True, null=True)
    reading_onyomi = models.TextField(blank=True, null=True)
    reading_kunyomi = models.TextField(blank=True, null=True)
    mean = models.TextField(blank=True, null=True)
    search_count = models.IntegerField(blank=True, null=True, default=0)
    p_impression_count = models.IntegerField(blank=True, null=True, default=0)
    n_impression_count = models.IntegerField(blank=True, null=True, default=0)

    def namable(self):
        return bool(self.joyo + self.jinmeiyo + self.kana + self.kigou)
    
    def get_type(self):
        t = []
        if self.joyo: t.append('常用漢字')
        if self.jinmeiyo: t.append('人名用漢字')
        if self.kana: t.append('かな（カナ）')
        if self.kigou: t.append('記号')
        return t
    
    def get_type_html(self):
        return ','.join(self.get_type())
    
    def get_reading_mean(self, param):
        if param == "on":
            sent = self.reading_onyomi
        elif param == "kun":
            sent = self.reading_kunyomi
        elif param == "mean":
            sent = self.mean
        else:
            return None
        return sent.split('\t')
    
    def get_reading_mean_html(self, param):
        sents = self.get_reading_mean(param)
        if param == "mean":
            mean = '<br>'
            for i, sent in enumerate(sents):
                if i>4:
                    mean += '...他 %d 項目' % (len(sents)-i)
                    break
                mean += '%d．%s' % (i+1, sent)
                if not(i == len(sents)-1):
                    mean += '<br>'
            return mean
        return '、'.join(sents)
        
    def get_property_for_tooltip(self):
        prop = []
        prop.append('文字：%s' % self.figure)
        prop.append('画数：%d画' % self.stroke)
        prop.append('分類：%s' % self.get_type_html())
        prop.append('音読：%s' % self.get_reading_mean_html("on"))
        prop.append('訓読：%s' % self.get_reading_mean_html("kun"))
        prop.append('意味：%s' % self.get_reading_mean_html("mean"))
        return '<br>'.join(prop)

    def get_property_dict(self):
        prop = {}
        prop['文字'] = self.figure
        prop['画数'] = '%d画' % self.stroke
        prop['分類'] = '、'.join(self.get_type())
        prop['音読'] = '、'.join(self.get_reading_mean("on"))
        prop['訓読'] = '、'.join(self.get_reading_mean("kun"))
        prop['意味'] = self.get_reading_mean("mean")
        return prop

    class Meta:
        # managed = False
        db_table = 'kanjidata'

class FortuneTelling(models.Model):
    status = models.TextField(blank=True, null=True)
    stroke = models.IntegerField(blank=True, null=True)
    luck = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    detail = models.TextField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'fortunetelling'

