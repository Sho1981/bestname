from .models import Name, FortuneTelling
from .constants import TABLE

class NameLparam(Name):
    def _setting(self):
        super()._setting()
        self.lucky_table = self.make_luckytable()

    def make_luckytable(self):
        self._make_luckynumber()
        return {'天格': (self.ten, TABLE[self.ten]),
                '人格': (self.jin, TABLE[self.jin]),
                '地格': (self.chi, TABLE[self.chi]),
                '総格': (self.sou, TABLE[self.sou]),
                '外格': (self.gai, TABLE[self.gai]),
                '仕事運': (self.shigoto, TABLE[self.shigoto]),
                '家庭運': (self.katei, TABLE[self.katei])}
    
    def _get_fortune_telling_html(self, ft):
        if isinstance(ft, FortuneTelling):
            return ft.keywords +'<br>～'+ ft.summary +'～<br>'+ ft.detail
        return None

    def get_fortune_telling_dict(self, key = None):
        ft_dict = {}
        statuses = ['天格', '人格', '地格', '総格', '外格', '仕事運', '家庭運']
        if key == 'html':
            for status in statuses:
                ft = FortuneTelling.objects.get(status=status, stroke=self.lucky_table[status][0])
                ft_dict[status] = self._get_fortune_telling_html(ft)
        return ft_dict
    
    class Meta:
        managed = False


class NameLstroke(Name):
    def _setting(self):
        super()._setting()
        self._luckylist_table = {}
        
    def _get_luckynumber(self):
        return (self.ten, self.jin, self.chi, self.sou,
                self.gai, self.shigoto, self.katei)
    
    def _set_luckynumber(self, lucks):
        (self.ten, self.jin, self.chi, self.sou,
         self.gai, self.shigoto, self.katei) = lucks
    
    def _get_luckylist(self):
        return (TABLE[self.ten], TABLE[self.jin], TABLE[self.chi],
                TABLE[self.sou], TABLE[self.gai],
                TABLE[self.shigoto], TABLE[self.katei])
    
    def _get_original_table_from_f_length(self, f_length, max_stroke):
        self._f_length = f_length
        luckystroke_table = {}

        if f_length == 1: #名が1文字の場合
            self.f_strokes = (1,)
            self._make_luckynumber()
            luckystroke_table[(1,)] = self._get_luckylist()
            for i in range(2, max_stroke+1):
                self.jin += 1
                self.chi += 1
                self.sou += 1
                self.shigoto += 1
                self.katei += 1
                luckystroke_table[(i,)] = self._get_luckylist()

        if f_length == 2: #名が2文字の場合
            for i in range(1,max_stroke+1):
                if i == 1:
                    self.f_strokes = (i, 1)
                    self._make_luckynumber()
                    before = self._get_luckynumber()
                else:
                    self._set_luckynumber(before)
                    self.jin += 1
                    self.chi += 1
                    self.sou += 1
                    self.shigoto += 1
                    self.katei += 1
                    before = self._get_luckynumber()
                luckystroke_table[(i, 1)] = self._get_luckylist()
                for j in range(2, max_stroke+1):
                    self.chi += 1
                    self.sou += 1
                    self.gai += 1
                    self.katei += 1
                    luckystroke_table[(i,j)] = self._get_luckylist()

        if f_length == 3: #名が2文字の場合
            for i in range(1,max_stroke+1):
                if i == 1:
                    self.f_strokes = (i, 1, 1)
                    self._make_luckynumber()
                    before_i = self._get_luckynumber()
                else:
                    self._set_luckynumber(before_i)
                    self.jin += 1
                    self.chi += 1
                    self.sou += 1
                    self.shigoto += 1
                    self.katei += 1
                    before_i = self._get_luckynumber()
                luckystroke_table[(i, 1, 1)] = self._get_luckylist()
                for j in range(1, max_stroke+1):
                    if j == 1:
                        before_j = self._get_luckynumber()
                    else:
                        self._set_luckynumber(before_j)
                        self.chi += 1
                        self.sou += 1
                        self.gai += 1
                        self.shigoto += 1
                        self.katei += 1
                        before_j = self._get_luckynumber()
                        luckystroke_table[(i, j, 1)] = self._get_luckylist()
                    for k in range(2, max_stroke+1):
                        self.chi += 1
                        self.sou += 1
                        self.gai += 1
                        self.katei += 1
                        luckystroke_table[(i, j, k)] = self._get_luckylist()
        return luckystroke_table

    def get_original_luckylist_table(self, max_stroke = 6):
        for i in range(1, 4):
            self._luckylist_table[i] =\
                        self._get_original_table_from_f_length(i, max_stroke)
        return self._luckylist_table

    class Meta:
        managed = False
