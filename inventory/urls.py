from django.urls import path

from . import views


app_name = 'inventory'

urlpatterns = [
    path('categories/', views.category, name='categories'),
    path('categories/<slug:category_slug>/', views.category, name='category'),
    path('categories/<slug:category_slug>/products/',
         views.product_by_category,
         name='product_by_category'),
    path('<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('product/create/', views.add_product, name='add-product'),
    path('product/search/', views.product_search, name="product_search"),
    path('', views.home, name='home'),
]
