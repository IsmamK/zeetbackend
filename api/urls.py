from django.urls import path,include
from . import views


urlpatterns = [
    path("create_user",views.create_user,name="create_user"),
    path('login',views.login_view,name='login'),
    path('logout',views.logout_view,name='logout'),
    path('is_authenticated',views.is_authenticated,name="is_authenticated"),
    path("all_products",views.all_products,name='all_products'),
    path("search",views.search,name='search'),
    path('get_search_history',views.get_search_history,name='search_history')
   
]

