from django.urls import path
from . import views

app_name = 'newname'
urlpatterns = [
    #
    # Top page and lucky parameter result page
    #
    path('', views.TopView.as_view(), name='top'),
    path('namejudge/', views.NameJudgeView.as_view(), name='namejudge'),
    path('<str:lastname>_<str:firstname>_<str:sex>/lparam_result/',
                    views.LparamResultView.as_view(), name='lparam_result'),

    #
    # Lucky stroke search and result page
    #
    path('lstroke_search/', views.LstrokeSearchView.as_view(), name='lstroke_search'),
    path('<str:lastname>_<int:first>_<int:second>_<int:third>_<str:sex>/lstroke_result/',
                    views.LstrokeResultView.as_view(), name='lstroke_result'),

    #
    # Kanji search page with stroke or reading
    #
    path('kanjisearch/strokereading/', views.SearchStrokeReadingView.as_view(), name='kanjisearch_strokereading'),
    path('kanjisearch/strokereading/<int:stroke>_<int:types>/',
                    views.SearchStrokeReadingView.as_view(), name='kanjisearch_stroke_result'),
    path('kanjisearch/strokereading/<str:reading>_<int:stroke>_<int:types>/',
                    views.SearchStrokeReadingView.as_view(), name='kanjisearch_strokereading_result'),

    #
    # Kanji search page with figure
    #
    path('kanjisearch/figure/', views.SearchFigureView.as_view(), name='kanjisearch_figure'),
    path('kanjisearch/figure/<str:figure>/',
                    views.SearchFigureView.as_view(), name='kanjisearch_figure_result'),

    #
    # Explanation page of lucky parameter
    #
    path('parameters/', views.ParametersExplainView.as_view(), name='parameters_explain'),

    #
    # Contact page
    #
    path('contact/', views.ContactFormView.as_view(), name='contact_form'),
    path('contact/result/', views.ContactResultView.as_view(), name='contact_result'),

    #
    # About us page
    #
    path('about_us/', views.AboutUsView.as_view(), name='about_us'),

    #
    # test page(uncommon)
    #
    path('test_space/', views.TestSpaceView.as_view(), name='test_space')

]