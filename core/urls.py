from django.urls import path, re_path
from . import views


app_name = 'core'

urlpatterns = [
# page for practice circle canvas and netflix scroller
path('menu/',views.HtmlPractice.as_view(), name='practice'),
path('userprofile/create/',views.User_Profile_Create.as_view(), name = 'user_create'),
path('userprofile/update/<slug>/',views.User_Profile_Update.as_view(), name = 'user_update'),

path('group/<slug>/',views.Detail_Group.as_view(), name ='group'),

path('',views.User_Dashboard.as_view(),name ='user_dashboard'),

# zoom
path('zoom/',views.TestZoom.as_view(), name ='zoom'),
path('zoom-display/',views.DisplayZoom.as_view(), name ='zoomdisplay'),

#urls related to posting /////////////////
path('profile/post/<int:pk>/',views.Detail_Post.as_view(), name ='post-detail'),

#group_send
#oage to create group
path('group-create/',views.Create_DividendWealthGroup.as_view(), name ='create-group'),

#group landing page
path('group/<slug>/landing-page/',views.Group_Landing_Page.as_view(), name ='group-landing'),

path('feed/',views.Feed.as_view(), name ='feed'),
#<int:pk>
path('ajax/',views.TestAjax.as_view(), name='ajax'),
# page for user to choose membership
path('memberships/',views.Membership_Choice.as_view(), name ='membership_choice'),
#page for user account
path('account/<username>/',views.DividendWealthAccount.as_view(), name ='user_account'),

#useful test zone below
]
