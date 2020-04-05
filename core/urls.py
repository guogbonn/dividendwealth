from django.urls import path, re_path
from . import views


app_name = 'core'

urlpatterns = [

path('search/',views.SearchResultsView.as_view(), name='search_results'),


path('stock/create/',views.Stocks_Create.as_view(), name ='stocks_create'),
path('userprofile/create/',views.User_Profile_Create.as_view(), name = 'user_create'),
path('userprofile/update/<slug>/',views.User_Profile_Update.as_view(), name = 'user_update'),

path('group/<slug>/',views.Detail_Group.as_view(), name ='group'),

path('',views.User_Dashboard.as_view(),name ='user_dashboard'),
path('stock/<slug>',views.Stocks_Detail.as_view(), name ='stocks_detail'),
path('stockinfo/delete/<int:pk>/',views.Stocks_Delete.as_view(), name ='stocks_delete'),
path('stock/add/<slug>',views.Create_Stock_User.as_view(), name ='stocks_user_create'),
path('stock/update/<int:pk>/',views.Update_Stock_User.as_view(), name ='stocks_user_update'),

# zoom
path('zoom/',views.TestZoom.as_view(), name ='zoom'),
path('zoom-display/',views.DisplayZoom.as_view(), name ='zoomdisplay'),


path('profile/',views.User_Profile_Page.as_view(),name = 'user_profile_page'),

#urls related to posting /////////////////
path('profile/post/create/',views.Create_Post.as_view(), name ='create_post'),
path('profile/post/<int:pk>/',views.Detail_Post.as_view(), name ='post-detail'),

#group_send
#oage to create group
path('group-create/',views.Create_DividendWealthGroup.as_view(), name ='create-group'),

#group landing page
path('group/<slug>/landing-page/',views.Group_Landing_Page.as_view(), name ='group-landing'),

path('feed/',views.Feed.as_view(), name ='feed'),
#<int:pk>

# page for user to choose membership
path('memberships/',views.Membership_Choice.as_view(), name ='membership_choice'),
#page for user account
path('account/<username>/',views.DividendWealthAccount.as_view(), name ='user_account'),

path('stock-autocomplete/',views.StockAutocomplete.as_view(create_field='name'),name='stock-autocomplete'),

#useful test zone below
path('test-autocomplete/',views.Autocom.as_view(),name='test-autocomplete'),
]
