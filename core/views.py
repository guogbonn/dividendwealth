import os
from django.utils import timezone

from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import (Item, OrderItem, Order,Stocks,
User_Profile,Dividend,StockInfo,Article,
Post,Topic,Comments,GenGroup,GroupMember,CommentReply,
Archive,PostArchive,CommentsArchive,CommentReplyArchive,
PostViewCount,PostReport,PostLike,CommentsReport,
CommentsLike,CommentReplyLike,CommentReplyReport,
PostPicture, CommentsPicture, CommentReplyPicture,
GroupWatchlist,WatchStockDetail,StockWatchlist,
WatchlistDownload, File, GroupFileList, FileDownload,
PostUrl, WebsiteUrl,Notification, DividendWealthMembership,
DividendWealthSubscription, UserProfileCards, Cards,
DividendWealthConnectedAccount, DividendWealthConnectedAccountPayments,
GroupCategories,Categories,GroupPayment,GroupSubscription,Credential,UserCredential,
UserFinancialRole,FinancialRole,UserRelationship
)
from django.views import generic
from django.urls import reverse,reverse_lazy
from django.conf import settings #for django allauth
from django.utils import timezone #for order date
from .forms import StocksModelForm,User_profile_form, Stock_profile_form,PostForm,GenGroupForm,PostComment
from allauth.utils import get_user_model
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
import datetime
from django.db.models import Q,Sum, F,FloatField
from chartit import PivotDataPool, PivotChart, DataPool, Chart
import requests
from django.utils.dateparse import parse_date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import ModelFormMixin
from django.views.generic.list import ListView
from dal import autocomplete
from django.utils.safestring import mark_safe
import json
from django.core.files.storage import default_storage
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import date
from datetime import time
from datetime import datetime,timedelta
import re
from django.utils import timezone
from django.http import JsonResponse
from django.utils.text import slugify
import stripe
from django.shortcuts import redirect
import string
from django.utils.timesince import timesince
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import connection
import random
import string
from django.contrib.staticfiles.templatetags.staticfiles import static


stripe.api_key = settings.STRIPE_SECRET_KEY

from PIL import Image, ExifTags

def rotate_image(filepath):
  try:
    image = Image.open(filepath)
    for orientation in ExifTags.TAGS.keys():
      if ExifTags.TAGS[orientation] == 'Orientation':
            break
    exif = dict(image._getexif().items())

    if exif[orientation] == 3:
        image = image.rotate(180, expand=True)
    elif exif[orientation] == 6:
        image = image.rotate(270, expand=True)
    elif exif[orientation] == 8:
        image = image.rotate(90, expand=True)
    image.save(filepath)
    image.close()
  except (AttributeError, KeyError, IndexError):
    # cases: image don't have getexif
    pass

# Create your views here.

"""
def item_list(request):
    context = {
    'items': Item.objects.all()
    }
    return render(request, "home-page.html", context)
"""
# https://docs.djangoproject.com/en/3.0/topics/auth/default/
class StockAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !

        qs = Stocks.objects.all()

        if self.q:
            qs = qs.filter(Q(ticker__icontains=self.q) | Q(company_name__icontains=self.q))

        return qs


#text page for autocomplete
class Autocom(generic.TemplateView):
    template_name = 'autocomplete.html'

    def get_context_data(self, *args, **kwargs):
        # Just include the form

        context = super(Autocom, self).get_context_data(*args, **kwargs)
        stocks = Stocks.objects.all()
        user = User_Profile.objects.filter(user=self.request.user)[0]
        context['stocks'] = stocks
        context['object_list']=StockInfo.objects.filter(userprofile =user).select_related()
        return context






# article =  Article.objects.filter(
#     Q(title__icontains=request) | Q(description__icontains=request) | Q(url__icontains=request)
# ).order_by('-published').order_by('-pk')[:12]
class Feed(generic.TemplateView):
    #list of all the blogs posted as well as stock portfolio recommendations
    template_name = "feed.html"
    def get(self, *args, **kwargs):
        group_infinite_scroll =self.request.GET.getlist('group_infinite_scroll') if 'group_infinite_scroll' in self.request.GET else None
        # group infinite scroll
        if group_infinite_scroll != None:
            # int will be zero if there are no files
            last_group_pk=group_infinite_scroll[0]
            try:
                self.request.session["group_search"]


                group_list = GenGroup.objects.filter(published=True,pk__lt=int(last_group_pk),groupcategories__category__description__in= self.request.session['group_search']['categories'],creator__usercredential__credential__title__in=self.request.session['group_search']['credentials'],price__gte=float(self.request.session['group_search']['min_price'][0])*100,price__lte=float(self.request.session['group_search']['max_price'][0])*100).distinct().order_by('-pk')

            except:
                # self.request.session["group_search"] = {'categories':'none','credentials':['none'],'price':['none','none']}
                group_list = GenGroup.objects.filter(pk__lt=int(last_group_pk),published=True).select_related('creator').order_by('-pk')

            group_list_count=group_list.count()
            paginator = 4
            group_list_count= group_list_count - paginator
            if group_list_count <= 0:
                get_more= "false"
            else:
                get_more= "true"
            group_list = group_list[:paginator]
            group_list_collection = []

            for group in group_list:
                # group pk
                group_pk = group.pk
                # user picture
                if bool(group.creator.profile_pic) != False:
                    user_profile_pic_url =  group.creator.profile_pic.url
                else:
                    user_profile_pic_url = 'false'
                # url to user
                url_to_user = '#'
                # group title
                group_title =string.capwords(group.title)
                # group description
                group_description = group.description
                # group picture
                group_picture = group.group_picture.url

                # group count
                group_membeer_count = group.member_count()
                # get
                group_type = group.group_type
                if group_type != "f":
                    if group_type == "s":
                        group_price ="${:.2f}".format(group.price / 100 )
                        price_description = "/Monthly Fee"
                        group_url = group.landing_page()
                    if group_type == "o":
                        group_price ="${:.2f}".format(group.price / 100 )
                        price_description = "/Addmision Fee"
                        group_url = group.landing_page()
                else:
                    group_price ="Free"
                    price_description = ""
                    group_url = group.get_absolute_url()

                group_info = {
                    #file id
                    "group_pk" : group_pk,
                    "user_profile_pic_url" : user_profile_pic_url,
                    "url_to_user": url_to_user,
                    "group_title": group_title,
                    "group_description": group_description,
                    "group_picture": group_picture,
                    "group_membeer_count": group_membeer_count,
                    "group_price":group_price,
                    "price_description": price_description,
                    "group_url": group_url,
                    'group_membeer_count':group_membeer_count,
                }

                group_info = json.dumps(group_info)
                group_list_collection.append(group_info)

            group_list_collection = json.dumps(group_list_collection)
            data = {
             'group_list_collection': group_list_collection,
             'get_more':get_more
            }
            return JsonResponse(data)

        load_group_metrics =self.request.GET.getlist('load_group_metrics') if 'load_group_metrics' in self.request.GET else None
        # load metrics for infinite scroll groups
        if load_group_metrics != None:
            load_group_metrics_pk=load_group_metrics[0]

            group_list = GenGroup.objects.filter(pk=int(load_group_metrics_pk)).select_related('creator')

            group_list_count=group_list.count()
            paginator = 4
            group_list_count= group_list_count - paginator
            if group_list_count <= 0:
                get_more= "false"
            else:
                get_more= "true"
            group_list = group_list[:paginator]
            group_metric_list_collection = []

            for group in group_list:
                # group pk
                group_pk = group.pk
                # group_post _today
                group_post_today = group.posts_today()
                # group post last thirty days
                group_post_thirty_days=group.posts_last_thirty_days()
                # group activeness
                group_activeness = group.group_activeness()
                # avg members online
                group_avg_mem_online = group.avg_members_online()
                # avg members joining a week
                group_members_joined_week = group.avg_member_joining_a_week()
                # user picture
                administrators = []
                for member in group.group_members():
                    if bool(member.userprofile.profile_pic) != False:
                        user_profile_pic_url = member.userprofile.profile_pic.url
                    else:
                        user_profile_pic_url = 'false'
                    administrators.append(user_profile_pic_url)
                    administrators.append('#')

                group_description = group.description
                group_value_proposition = group.value_proposition

                group_metric_info = {
                    #file id
                    "group_pk" : group_pk,
                    "group_post_today" : group_post_today,
                    "group_post_thirty_days": group_post_thirty_days,
                    "group_activeness": group_activeness,
                    "group_avg_mem_online": group_avg_mem_online,
                    "group_members_joined_week": group_members_joined_week,
                    "administrators": administrators,
                    "group_description":group_description,
                    "group_value_proposition": group_value_proposition,
                }

                group_metric_info = json.dumps(group_metric_info)
                group_metric_list_collection.append(group_metric_info)

            group_metric_list_collection = json.dumps(group_metric_list_collection)
            data = {
             'group_metric_list_collection': group_metric_list_collection,
             'get_more':get_more
            }
            return JsonResponse(data)

        group_filter_catagories =self.request.GET.getlist('group_filter_catagories[]') if 'group_filter_catagories[]' in self.request.GET else None
        group_filter_credentials =self.request.GET.getlist('group_filter_credentials[]') if 'group_filter_credentials[]' in self.request.GET else None
        min_price =self.request.GET.getlist('min_price') if 'min_price' in self.request.GET else None
        max_price =self.request.GET.getlist('max_price') if 'max_price' in self.request.GET else None
        # filter for groups
        if group_filter_catagories != None:
            self.request.session["group_search"] = {'categories':group_filter_catagories,'credentials':group_filter_credentials,'min_price':min_price,'max_price':max_price}
            if "select all" == self.request.session["group_search"]['categories'][0]:
                self.request.session['group_search']['categories']=list(Categories.objects.all().values_list('description', flat=True).order_by('id'))

            if "select all" == self.request.session["group_search"]['credentials'][0]:
                # gets list of values
                self.request.session['group_search']['credentials']=list(Credential.objects.all().values_list('title', flat=True).order_by('id'))

            self.request.session.modified = True
            print(self.request.session['group_search']['min_price'][0])
            price_min=float(self.request.session['group_search']['min_price'][0])*100

            group_list = GenGroup.objects.filter(published=True,groupcategories__category__description__in= self.request.session['group_search']['categories'],creator__usercredential__credential__title__in=self.request.session['group_search']['credentials'],price__gte=float(self.request.session['group_search']['min_price'][0])*100,price__lte=float(self.request.session['group_search']['max_price'][0])*100).distinct().order_by('-pk')
            # .prefetch_related('categories').prefetch_related('creator__user_credentials') possible solution to enhance search outcome 2 connections
            # print("filter results",group_list)
            # print("view connections",len(connection.queries))

            group_list_count=group_list.count()
            paginator = 4
            group_list_count= group_list_count - paginator
            if group_list_count <= 0:
                get_more= "false"
            else:
                get_more= "true"
            group_list = group_list[:paginator]
            group_list_collection = []

            for group in group_list:
                # group pk
                group_pk = group.pk
                # user picture
                if bool(group.creator.profile_pic) != False:
                    user_profile_pic_url =  group.creator.profile_pic.url
                else:
                    user_profile_pic_url = 'false'
                # url to user
                url_to_user = '#'
                # group title
                group_title =string.capwords(group.title)
                # group description
                group_description = group.description
                # group picture
                group_picture = group.group_picture.url

                # group count
                group_membeer_count = group.member_count()
                # get
                group_type = group.group_type
                if group_type != "f":
                    if group_type == "s":
                        group_price ="${:.2f}".format(group.price / 100 )
                        price_description = "/Monthly Fee"
                        group_url = group.landing_page()
                    if group_type == "o":
                        group_price ="${:.2f}".format(group.price / 100 )
                        price_description = "/Addmision Fee"
                        group_url = group.landing_page()
                else:
                    group_price ="Free"
                    price_description = " "
                    group_url = group.get_absolute_url()

                group_info = {
                    #file id
                    "group_pk" : group_pk,
                    "user_profile_pic_url" : user_profile_pic_url,
                    "url_to_user": url_to_user,
                    "group_title": group_title,
                    "group_description": group_description,
                    "group_picture": group_picture,
                    "group_membeer_count": group_membeer_count,
                    "group_price":group_price,
                    "price_description": price_description,
                    "group_url": group_url,
                    'group_membeer_count':group_membeer_count,
                }

                group_info = json.dumps(group_info)
                group_list_collection.append(group_info)
            print(group_list_collection)
            group_list_collection = json.dumps(group_list_collection)
            data = {
             'group_list_collection': group_list_collection,
             'get_more':get_more
            }
            return JsonResponse(data)

        reset_group_filter =self.request.GET.getlist('reset_group_filter') if 'reset_group_filter' in self.request.GET else None
        if reset_group_filter != None:
            group_filter_catagories=list(Categories.objects.all().values_list('description', flat=True).order_by('id'))
            # gets list of values
            group_filter_credentials=list(Credential.objects.all().values_list('title', flat=True).order_by('id'))

            self.request.session["group_search"] = {'categories':group_filter_catagories,'credentials':group_filter_credentials,'min_price':['0'],'max_price':['100']}
            self.request.session.modified = True
            data = {
             'reset':'reset'
            }
            print("reset")
            return JsonResponse(data)

        article_query =self.request.GET.getlist('article_query') if 'article_query' in self.request.GET else None
        if  article_query != None:
            article_list = []
            query ='+'+article_query[0].replace(" ", "+")
            creating_article_database = False
            creating_new_article = False
            paginator = 17
            parse_time =datetime.now()-timedelta(minutes=15)
            # see if we have any article in the data base with current query
            if Article.objects.filter(query_cat=query,created_date__gte=parse_time).exists():
                data_base_article_count=Article.objects.filter(query_cat=query,created_date__gte=parse_time).distinct().count()
                if data_base_article_count >= paginator:
                    # have enough articles
                    print("not creating more")
                    print("query category",query)
                    article_list=Article.objects.filter(query_cat=query,created_date__gte=parse_time).distinct().order_by('-published')[:paginator]
                else:
                    # not enough articles create more
                    article_list=Article.objects.filter(query_cat=query,created_date__gte=parse_time).distinct().order_by('-published')[:paginator]
                    print("have articles in database but not enough creating more")
                    print("query category",query)
                    unfilled = paginator - data_base_article_count

                    print("left unfiled",unfilled)
                    print("articlelist before",article_list)

                    article_list=list(article_list)
                    # print("articlelist turned to list",article_list)
                    news_api_url = ('https://newsapi.org/v2/top-headlines?'
                                    'q={}&'
                                    'language=en&'
                                    'sortBy=publishedAt&'
                                    'apiKey=3cdfd0dd582e4740a2c5cd76ee42089d')
                    news_api_response = requests.get(news_api_url.format(query)).json()
                    total_num_articles = news_api_response["totalResults"]
                    # range starts at 0
                    print("got more articles from api")
                    if total_num_articles == 0:
                        print("tried to get more articles on the subject however there are none",news_api_response)
                        print("total hits:", news_api_response["totalResults"])
                        creating_article_database =True
                        pass
                    else:
                        for x in range(paginator):
                            if x == total_num_articles or x == unfilled:
                                print(x)
                                print("broke")
                                print("total number of articles",total_num_articles)
                                print("unfilled",unfilled)
                                creating_article_database =True

                                break
                            datestrip = news_api_response['articles'][x]['publishedAt']
                            datestrip =datestrip.split('T')
                            datestrip= datestrip[0]
                            datestrip = parse_date(datestrip)
                            created_article,create_date = Article.objects.get_or_create(source=news_api_response['articles'][x]['source']['name'], title=news_api_response['articles'][x]['title'], description=news_api_response['articles'][x]['description'],
                            url=news_api_response['articles'][x]['url'],urltoimage =news_api_response['articles'][x]['urlToImage'], author =news_api_response['articles'][x]['author'],published =datestrip,query_cat=topics_for_dividend_wealth_news[topic_choice_index] )
                            print("article was created or not",create_date)
                            article_list.append(created_article)
                        print(article_list)
                        print("end of sequence")

            else:

                news_api_url = ('https://newsapi.org/v2/everything?'
                                'q={}&'
                                'language=en&'
                                'sortBy=publishedAt&'
                                'apiKey=3cdfd0dd582e4740a2c5cd76ee42089d')
                news_api_response = requests.get(news_api_url.format(query)).json()
                print("creating new set of articles")
                print("query category",query)
                print(news_api_response)
                total_num_articles = news_api_response["totalResults"]

                total_num_articles=total_num_articles
                # range starts at 0
                if total_num_articles == 0:
                    creating_new_article = True
                    pass
                else:
                    for x in range(paginator):
                        if x == total_num_articles:
                            print("total articels",total_num_articles)
                            creating_new_article = True
                            break
                        datestrip = news_api_response['articles'][x]['publishedAt']
                        datestrip =datestrip.split('T')
                        datestrip= datestrip[0]
                        datestrip = parse_date(datestrip)
                        created_article,create_date = Article.objects.get_or_create(source=news_api_response['articles'][x]['source']['name'], title=news_api_response['articles'][x]['title'], description=news_api_response['articles'][x]['description'],
                        url=news_api_response['articles'][x]['url'],urltoimage =news_api_response['articles'][x]['urlToImage'], author =news_api_response['articles'][x]['author'],published =datestrip,query_cat=query )
                        print("article was created or not",create_date)
                        article_list.append(created_article)
            # could combine the two if statements
            if len(article_list) < paginator:
                if creating_new_article == True:
                    print("creating_new_article section")
                    # filter for articles just created
                    article_count=len(article_list)
                    unfilled=paginator-article_count
                    queried_articles=Article.objects.filter(query_cat=query,created_date__gte=parse_time)
                    article_list_all = Article.objects.exclude(query_cat=query,created_date__gte=parse_time).order_by('-published')[:unfilled]
                    article_list = queried_articles | article_list_all
                    article_list=article_list.distinct()
                    article_list=list(article_list)


                if creating_article_database == True:
                    print("creating_article_database section")
                    article_count=len(article_list)
                    unfilled=paginator-article_count
                    queried_articles=Article.objects.filter(query_cat=query,created_date__gte=parse_time)
                    article_list_all = Article.objects.exclude(query_cat=query,created_date__gte=parse_time).order_by('-published')[:unfilled]
                    article_list = queried_articles | article_list_all
                    article_list=article_list.distinct()
                    article_list=list(article_list)

            article_list_collection = []
            for article in article_list:
                article_title = article.title
                if article.source:
                    article_source = article.source
                else:
                    article_source = 'none'

                article_url = article.url

                if article.urltoimage:
                    article_urltoimage = article.urltoimage
                else:
                    article_urltoimage = 'none'

                if article.author:
                    article_author = article.author
                else:
                    article_author ="none"
                article_published = article.published
                article_published=article_published.strftime("%B %d, %Y")
                article_description = article.description
                article_metric_info = {
                    #file id
                    "article_title" : article_title,
                    "article_source" : article_source,
                    "article_description": article_description,
                    "article_url": article_url,
                    "article_urltoimage": article_urltoimage,
                    "article_author": article_author,
                     "article_published": article_published,

                }

                article_metric_info = json.dumps(article_metric_info)
                article_list_collection.append(article_metric_info)

            article_list_collection = json.dumps(article_list_collection)
            data = {
             'article_list_collection': article_list_collection,
            }
            return JsonResponse(data)

        profile_infinite_scroll =self.request.GET.getlist('profile_infinite_scroll') if 'profile_infinite_scroll' in self.request.GET else None
        # profile infinite scroll
        if profile_infinite_scroll != None:
            last_profile_pk=profile_infinite_scroll[0]
            try:
                self.request.session["profile_search"]
                if self.request.user.is_authenticated:
                    current_user = User_Profile.objects.filter(user=self.request.user)[0]
                    profile_list = User_Profile.objects.filter(pk__lt=int(last_profile_pk),usercredential__credential__in= self.request.session['profile_search']['credential'],userfinancialrole__financial_role__in=self.request.session['profile_search']['financial_role']).distinct().order_by('-pk')
                    profile_list=profile_list.exclude(pk=current_user.pk)
                else:
                    profile_list = User_Profile.objects.filter(pk__lt=int(last_profile_pk),usercredential__credential__in= self.request.session['profile_search']['credential'],userfinancialrole__financial_role__in=self.request.session['profile_search']['financial_role']).distinct().order_by('-pk')
            except:
                if self.request.user.is_authenticated:
                    current_user = User_Profile.objects.filter(user=self.request.user)[0]
                    profile_list = User_Profile.objects.filter(pk__lt=int(last_profile_pk)).order_by('-pk')
                    profile_list=profile_list.exclude(pk=current_user.pk)
                else:
                    profile_list = User_Profile.objects.filter(pk__lt=int(last_profile_pk)).order_by('-pk')

            profile_list_count=profile_list.count()
            paginator = 2
            profile_list_count= profile_list_count - paginator
            if profile_list_count <= 0:
                get_more= "false"
            else:
                get_more= "true"
            profile_list = profile_list[:paginator]
            profile_list_collection = []

            for profile in profile_list:
                # group pk
                user_pk = profile.pk
                # user picture
                if bool(profile.profile_pic) != False:
                    user_profile_pic_url =  profile.profile_pic.url
                else:
                    user_profile_pic_url = 'false'
                # user background
                if bool(profile.background_pic) != False:
                    user_background_pic_url =  profile.background_pic.url
                else:
                    user_background_pic_url = 'false'
                # user full name
                if profile.user_fullname() != None:
                    user_full_name = profile.user_fullname()
                else:
                    user_full_name = "false"
                # url to user
                url_to_user = '#'
                # user finacial roles
                user_finacial_roles = profile.user_financial_role()
                # user credentials
                user_credentials = profile.user_financial_credentials()
                # user verification
                if profile.current_dividend_wealth_member():
                    user_current_dividend_wealth_member = "true"
                else:
                    user_current_dividend_wealth_member = "false"
                #user username
                user_username=profile.user.username

                if self.request.user.is_authenticated:
                    # check to see current user (person scrolling) is following the user being evaluated
                    if UserRelationship.objects.filter(following=profile,follower=current_user).exists():
                        user_follow_status = "Following"
                    else:
                        user_follow_status = "Follow"
                    # check to see if the user being evaluated is a follower of the current user
                    if UserRelationship.objects.filter(following=current_user,follower=profile).exists():
                        user_is_a_follower = "true"
                    else:
                        user_is_a_follower = "false"
                else:
                    # user redieriction ot login page is handeled of the client side
                    user_follow_status = "Follow"
                    user_is_a_follower = "false"


                profile_info = {
                    #file id
                    "user_pk" : user_pk,
                    "user_profile_pic_url" : user_profile_pic_url,
                    "url_to_user": url_to_user,
                    "user_background_pic_url": user_background_pic_url,
                    "user_full_name": user_full_name,
                    "user_finacial_roles": user_finacial_roles,
                    "user_credentials": user_credentials,
                    "user_current_dividend_wealth_member":user_current_dividend_wealth_member,
                    "user_follow_status": user_follow_status,
                    "user_is_a_follower": user_is_a_follower,
                    "user_username":user_username,
                }

                profile_info = json.dumps(profile_info)
                profile_list_collection.append(profile_info)

            profile_list_collection = json.dumps(profile_list_collection)
            data = {
             'profile_list_collection': profile_list_collection,
             'get_more':get_more
            }
            return JsonResponse(data)

        profile_filter_financial_role = self.request.GET.getlist('profile_filter_financial_role[]') if 'profile_filter_financial_role[]' in self.request.GET else None
        profile_filter_credentials = self.request.GET.getlist('profile_filter_credentials[]') if 'profile_filter_credentials[]' in self.request.GET else None

        if profile_filter_financial_role != None:

            self.request.session["profile_search"] = {'financial_role':profile_filter_financial_role,'credential':profile_filter_credentials}
            if "select all" == self.request.session["profile_search"]['financial_role'][0]:
                print("here1")
                self.request.session['profile_search']['financial_role']=list(FinancialRole.objects.all().values_list('title', flat=True).order_by('id'))

            if "select all" == self.request.session["profile_search"]['credential'][0]:
                # gets list of values
                self.request.session['profile_search']['credential']=list(Credential.objects.all().values_list('title', flat=True).order_by('id'))
            self.request.session.modified = True

        # try:

            if self.request.user.is_authenticated:
                print("credentials",self.request.session['profile_search']['credential'])
                print("financial_role",self.request.session['profile_search']['financial_role'])
                current_user = User_Profile.objects.filter(user=self.request.user)[0]
                profile_list = User_Profile.objects.filter(usercredential__credential__title__in= self.request.session['profile_search']['credential'],userfinancialrole__financial_role__title__in=self.request.session['profile_search']['financial_role']).distinct().order_by('-pk')
                profile_list=profile_list.exclude(pk=current_user.pk)
                print("her",)
            else:
                profile_list = User_Profile.objects.filter(usercredential__credential__title__in= self.request.session['profile_search']['credential'],userfinancialrole__financial_role__title__in=self.request.session['profile_search']['financial_role']).distinct().order_by('-pk')
        # except:
        #     print("in except ")
        #     if self.request.user.is_authenticated:
        #         current_user = User_Profile.objects.filter(user=self.request.user)[0]
        #         profile_list = User_Profile.objects.all().order_by('-pk')
        #         profile_list=profile_list.exclude(pk=current_user.pk)
        #     else:
        #         profile_list = User_Profile.objects.all().order_by('-pk')

            profile_list_count=profile_list.count()
            paginator = 4
            profile_list_count= profile_list_count - paginator
            if profile_list_count <= 0:
                get_more= "false"
            else:
                get_more= "true"
            profile_list = profile_list[:paginator]
            profile_list_collection = []
            for profile in profile_list:
                # group pk
                user_pk = profile.pk
                # user picture
                if bool(profile.profile_pic) != False:
                    user_profile_pic_url =  profile.profile_pic.url
                else:
                    user_profile_pic_url = 'false'
                # user background
                if bool(profile.background_pic) != False:
                    user_background_pic_url =  profile.background_pic.url
                else:
                    user_background_pic_url = 'false'
                # user full name
                if profile.user_fullname() != None:
                    user_full_name = profile.user_fullname()
                else:
                    user_full_name = "false"
                # url to user
                url_to_user = '#'
                # user finacial roles
                user_finacial_roles = profile.user_financial_role()
                # user credentials
                user_credentials = profile.user_financial_credentials()
                # user verification
                if profile.current_dividend_wealth_member():
                    user_current_dividend_wealth_member = "true"
                else:
                    user_current_dividend_wealth_member = "false"
                #user username
                user_username=profile.user.username

                if self.request.user.is_authenticated:
                    # check to see current user (person scrolling) is following the user being evaluated
                    if UserRelationship.objects.filter(following=profile,follower=current_user).exists():
                        user_follow_status = "Following"
                    else:
                        user_follow_status = "Follow"
                    # check to see if the user being evaluated is a follower of the current user
                    if UserRelationship.objects.filter(following=current_user,follower=profile).exists():
                        user_is_a_follower = "true"
                    else:
                        user_is_a_follower = "false"
                else:
                    # user redieriction ot login page is handeled of the client side
                    user_follow_status = "Follow"
                    user_is_a_follower = "false"


                profile_info = {
                    #file id
                    "user_pk" : user_pk,
                    "user_profile_pic_url" : user_profile_pic_url,
                    "url_to_user": url_to_user,
                    "user_background_pic_url": user_background_pic_url,
                    "user_full_name": user_full_name,
                    "user_finacial_roles": user_finacial_roles,
                    "user_credentials": user_credentials,
                    "user_current_dividend_wealth_member":user_current_dividend_wealth_member,
                    "user_follow_status": user_follow_status,
                    "user_is_a_follower": user_is_a_follower,
                    "user_username":user_username,
                }

                profile_info = json.dumps(profile_info)
                profile_list_collection.append(profile_info)

            profile_list_collection = json.dumps(profile_list_collection)
            data = {
             'profile_list_collection': profile_list_collection,
             'get_more':get_more
            }
            return JsonResponse(data)

        reset_profile_filter =self.request.GET.getlist('reset_profile_filter') if 'reset_profile_filter' in self.request.GET else None
        if reset_profile_filter != None:
            profile_filter_financial_role=list(FinancialRole.objects.all().values_list('title', flat=True).order_by('id'))
            # gets list of values
            profile_filter_credentials=list(Credential.objects.all().values_list('title', flat=True).order_by('id'))

            self.request.session["profile_search"] = {'financial_role':profile_filter_financial_role,'credential':profile_filter_credentials}
            self.request.session.modified = True
            data = {
             'reset':'reset'
            }
            print("reset")
            return JsonResponse(data)

        similar_group_slug=self.request.GET.getlist('similar_group_slug') if 'similar_group_slug' in self.request.GET else None

        if similar_group_slug != None:
            similar_group_slug=similar_group_slug[0]
            group = GenGroup.objects.filter(slug=similar_group_slug)[0]
            value_proposition=group.value_proposition
            rules_guidlines=group.rules_guidlines
            group_title=group.title.title()
            group_description= group.description
            data = {
             'value_proposition': value_proposition,
             'rules_guidlines':rules_guidlines,
             'group_title':group_title,
             'group_description':group_description,
            }
            return JsonResponse(data)
        return super(Feed, self).get(self.request, *args, **kwargs)



    def get_context_data(self, *args, **kwargs):
        # Just include the form
        context = super(Feed, self).get_context_data(*args, **kwargs)
        if self.request.user.is_authenticated:
            user = User_Profile.objects.filter(user=self.request.user)[0]
        # users
            context['user_authenticated'] = "true"
            context["user_username"] = user.user.username
            context['user'] = user
            user_notifications = Notification.objects.filter(userprofile=user).order_by('-date_created')[:10]
            context['user_notifications'] = user_notifications
            profile_list = User_Profile.objects.exclude(pk=user.pk).order_by('-pk')[:4]
            context['profile_list'] = profile_list
        else:
            context['user_authenticated'] = "false"
            profile_list = User_Profile.objects.all().order_by('-pk')[:4]
            context['profile_list'] = profile_list

        featured_members=User_Profile.objects.filter(featured=True).order_by('-pk')[:4]
        context['featured_members'] = featured_members
        #Section is for groups
        max_group_price_list = list(GenGroup.objects.filter(published=True).values_list('price', flat=True).order_by('id'))
        context['max_group_price'] = "{:.2f}".format(max(max_group_price_list)/100)
        context['list_of_credentials'] =Credential.objects.all().values_list('title', flat=True).order_by('id')
        context['list_of_group_categories']=  Categories.objects.all().values_list('description', flat=True).order_by('id')
        list_of_groups = GenGroup.objects.select_related('creator')
        context['group_list'] = GenGroup.objects.filter(published=True).select_related('creator').order_by('-pk')[:3]
        #list of recommended groups for user not the currnet group
        list_of_groups = GenGroup.objects.filter(published=True)
        context['group_list_2'] = list_of_groups
        # Section is for articles
        topics_for_dividend_wealth_news = ["+stocks","+millionare","+building+wealth","+personal+budgeting","+income+investing","+dividend+income","+financial+planning","+early+retirement","+passive+income","+money+mistake","+personal+finance"]
        topic_choice_index = random.randint(0, len(topics_for_dividend_wealth_news)-1)
        # topic_choice_index = 1
        article_list = []
        creating_article_database = False
        creating_new_article = False
        paginator = 17
        parse_time =datetime.now()-timedelta(minutes=15)
        # see if we have any article in the data base with current query
        if Article.objects.filter(query_cat=topics_for_dividend_wealth_news[topic_choice_index],created_date__gte=parse_time).exists():
            data_base_article_count=Article.objects.filter(query_cat=topics_for_dividend_wealth_news[topic_choice_index],created_date__gte=parse_time).distinct().count()
            if data_base_article_count >= paginator:
                # have enough articles
                print("not creating more")
                print("query category",topics_for_dividend_wealth_news[topic_choice_index])
                article_list=Article.objects.filter(query_cat=topics_for_dividend_wealth_news[topic_choice_index],created_date__gte=parse_time).distinct().order_by('-published')[:paginator]
            else:
                # not enough articles create more
                article_list=Article.objects.filter(query_cat=topics_for_dividend_wealth_news[topic_choice_index],created_date__gte=parse_time).distinct().order_by('-published')[:paginator]
                print("have articles in database but not enough creating more")
                print("query category",topics_for_dividend_wealth_news[topic_choice_index])
                unfilled = paginator - data_base_article_count

                print("left unfiled",unfilled)
                print("articlelist before",article_list)

                article_list=list(article_list)
                # print("articlelist turned to list",article_list)
                news_api_url = ('https://newsapi.org/v2/top-headlines?'
                                'q={}&'
                                'language=en&'
                                'sortBy=publishedAt&'
                                'apiKey=3cdfd0dd582e4740a2c5cd76ee42089d')
                news_api_response = requests.get(news_api_url.format(topics_for_dividend_wealth_news[topic_choice_index])).json()
                total_num_articles = news_api_response["totalResults"]
                # range starts at 0
                print("got more articles from api")
                if total_num_articles == 0:
                    print("tried to get more articles on the subject however there are none",news_api_response)
                    print("total hits:", news_api_response["totalResults"])
                    creating_article_database =True
                    pass
                else:
                    for x in range(paginator):
                        if x == total_num_articles or x == unfilled:
                            print(x)
                            print("broke")
                            print("total number of articles",total_num_articles)
                            print("unfilled",unfilled)
                            creating_article_database =True

                            break
                        datestrip = news_api_response['articles'][x]['publishedAt']
                        datestrip =datestrip.split('T')
                        datestrip= datestrip[0]
                        datestrip = parse_date(datestrip)
                        created_article,create_date = Article.objects.get_or_create(source=news_api_response['articles'][x]['source']['name'], title=news_api_response['articles'][x]['title'], description=news_api_response['articles'][x]['description'],
                        url=news_api_response['articles'][x]['url'],urltoimage =news_api_response['articles'][x]['urlToImage'], author =news_api_response['articles'][x]['author'],published =datestrip,query_cat=topics_for_dividend_wealth_news[topic_choice_index] )
                        print("article was created or not",create_date)
                        article_list.append(created_article)
                    print(article_list)
                    print("end of sequence")

        else:

            news_api_url = ('https://newsapi.org/v2/everything?'
                            'q={}&'
                            'language=en&'
                            'sortBy=publishedAt&'
                            'apiKey=3cdfd0dd582e4740a2c5cd76ee42089d')
            news_api_response = requests.get(news_api_url.format(topics_for_dividend_wealth_news[topic_choice_index])).json()
            print("creating new set of articles")
            print("query category",topics_for_dividend_wealth_news[topic_choice_index])
            total_num_articles = news_api_response["totalResults"]

            total_num_articles=total_num_articles
            # range starts at 0
            if total_num_articles == 0:
                creating_new_article = True
                pass
            else:
                for x in range(paginator):
                    if x == total_num_articles:
                        print("total articels",total_num_articles)
                        creating_new_article = True
                        break
                    datestrip = news_api_response['articles'][x]['publishedAt']
                    datestrip =datestrip.split('T')
                    datestrip= datestrip[0]
                    datestrip = parse_date(datestrip)
                    created_article,create_date = Article.objects.get_or_create(source=news_api_response['articles'][x]['source']['name'], title=news_api_response['articles'][x]['title'], description=news_api_response['articles'][x]['description'],
                    url=news_api_response['articles'][x]['url'],urltoimage =news_api_response['articles'][x]['urlToImage'], author =news_api_response['articles'][x]['author'],published =datestrip,query_cat=topics_for_dividend_wealth_news[topic_choice_index] )
                    print("article was created or not",create_date)
                    article_list.append(created_article)
        # could combine the two if statements
        if len(article_list) < paginator:
            if creating_new_article == True:
                print("creating_new_article section")
                # filter for articles just created
                article_count=len(article_list)
                unfilled=paginator-article_count
                queried_articles=Article.objects.filter(query_cat=topics_for_dividend_wealth_news[topic_choice_index],created_date__gte=parse_time)
                article_list_all = Article.objects.exclude(query_cat=topics_for_dividend_wealth_news[topic_choice_index],created_date__gte=parse_time).order_by('-published')[:unfilled]
                article_list = queried_articles | article_list_all
                article_list=article_list.distinct()
                article_list=list(article_list)


            if creating_article_database == True:
                print("creating_article_database section")
                article_count=len(article_list)
                unfilled=paginator-article_count
                queried_articles=Article.objects.filter(query_cat=topics_for_dividend_wealth_news[topic_choice_index],created_date__gte=parse_time)
                article_list_all = Article.objects.exclude(query_cat=topics_for_dividend_wealth_news[topic_choice_index],created_date__gte=parse_time).order_by('-published')[:unfilled]
                article_list = queried_articles | article_list_all
                article_list=article_list.distinct()
                article_list=list(article_list)
        article_list_carousel = article_list[:3]

        article_list_featured= article_list[3:5]
        article_list_scroller1 = article_list[5::2]
        article_list_scroller2 = article_list[6::2]

        print("articles list",len(article_list))
        print("carosel",len(article_list_carousel))
        print("featured",len(article_list_featured))
        print("scroller1",len(article_list_scroller1))
        print("scroller2",len(article_list_scroller2))
        context['article_list_scroller1'] = article_list_scroller1
        context['article_list_scroller2'] = article_list_scroller2
        context['article_list_carousel'] = article_list_carousel
        context['article_list_featured'] = article_list_featured
        context['query'] = string.capwords(topics_for_dividend_wealth_news[topic_choice_index].replace("-", " "))
        # Section is for Profile sc
        default_background_url = static('img/logo.jpg')
        context['default_background_url'] = default_background_url
        default_profile_pic_url = static('img/default-profile-picture-gmail-2.png')
        context['default_profile_pic_url'] = default_profile_pic_url
        dividend_member_tag = static('img/dividend_wealth_member.png')
        context['dividend_member_tag'] = dividend_member_tag
        # self.request.session['news'] = True
        # print("view connections",connection.queries)
        context['financial_roles'] = FinancialRole.objects.all() #filter for active finacial roles
        # keep track of how often the fincal role is searched

        # Section is for Stocks
        stocks=Stocks.objects.all()
        context['stocks'] = stocks

        if self.request.user.is_authenticated:
            user_owned_stocks= user.stock.all()
            context['user_owned_stocks'] = user_owned_stocks
        return context

            #handeling post
    def post(self, request, **kwargs):
        user = User_Profile.objects.filter(user=self.request.user)[0]
        print("made it to post")
        # Section is for checking notitification
        notification_id_checked = self.request.POST.getlist('notification_id_checked') if 'notification_id_checked' in self.request.POST else None
        if notification_id_checked != None:
            notification = Notification.objects.filter(pk=int(notification_id_checked[0]))[0]
            notification.checked = True
            notification.save()
            data= {
            'null':'null'
            }
            print("made it to post")
            return JsonResponse(data)


class User_Profile_Page(generic.TemplateView):
    template_name = 'user_profile.html'
    def get_queryset(self):
        #get current user accessing page
        user = get_object_or_404(User_Profile, user=self.request.user)
        #list of stocks order by slug feild
        user.stock.order_by('slug').all()
        #use intermidary model to get instances where user profile equal to current user
        return StockInfo.objects.filter(userprofile =user).select_related()

    def get_context_data(self, **kwargs):
        """Checks to see if user has stocks or not"""
        context = super(User_Profile_Page, self).get_context_data(**kwargs)
        user = User_Profile.objects.filter(user=self.request.user)[0]
        users = User_Profile.objects.all()
        #post_qs2 = Post.object.filter(author=user)

        #getting list of groups user is a member of or create_date
        #can have a list of created vs joined groups
        group_qs = GenGroup.objects.filter(
            Q(creator=user) | Q(members=user)
            ).distinct()
        total_groups = len(group_qs)
        context['groups'] =group_qs
        context['total_groups'] = total_groups
        context['users'] = users
        print(group_qs)
        #/////////////endsection

        #paginating stock_list
        stock_list = StockInfo.objects.filter(userprofile =user).select_related()
        paginator = Paginator(stock_list,2)
        page_request_var = 'page'
        page = self.request.GET.get(page_request_var)
        try:
            paginated_queryset = paginator.page(page)
        except PageNotAnInteger:
            paginated_queryset = paginator.page(1)
        except EmptyPage:
            paginated_queryset = paginator.page(paginator.num_pages)
        context['stock_list'] = paginated_queryset
        context['page_request_var'] = page_request_var

    #end section

        #paginating posts
        post_list = Spost_qs = user.post_set.all().order_by("-published").select_related() #want to profile affilited with user
        paginator2 = Paginator(post_list,1)
        page_request_var2 = 'posts'
        posts = self.request.GET.get(page_request_var2)
        try:
            paginated_queryset2 = paginator2.page(posts)
        except PageNotAnInteger:
            paginated_queryset2 = paginator2.page(1)
        except EmptyPage:
            paginated_queryset2 = paginator2.page(paginator2.num_pages)
        existing_post = post_list.exists()
    #end section



        context['posts'] = paginated_queryset2
        context['post_request_var2'] = page_request_var2
        context['existing_post'] = existing_post

        return context
#post section /////////////////////
class Create_Post(generic.CreateView):
    template_name = 'post_form.html'
    form_class = PostForm
    success_url = '/'

    def form_valid(self, form,):
        #problem saving a many to many feild because commit = to false
         """Saves current user to the profile """
         postform = form.save(commit=False)

         postform.author = get_object_or_404(User_Profile, user=self.request.user)
         postform.save()
         form.save_m2m()
         print(postform.stocks)
         return HttpResponseRedirect(reverse('core:feed')) #home page

class Detail_Post(generic.DetailView):
    queryset = Post.objects.select_related()
    template_name = "post_detail.html"

    def get_context_data(self, *args, **kwargs):
        # Just include the form
        message = self.request.GET.getlist('message')
        context = super(Detail_Post, self).get_context_data(*args, **kwargs)
        user = User_Profile.objects.filter(user=self.request.user)[0]

        # Postz= get_object_or_404(Post, pk=3)
        # comments = Postz.post_comment.all()
        # print(comments)


        try:
            post=message[0]
            print(post)
        except IndexError:
            post=None
        try:
            comment=message[1]
            print(comment)
        except IndexError:
            comment=None




        if post != None and comment != None:
            current_post = get_object_or_404(Post, pk=post)
            count = current_post.comment_count
            if Comments.objects.filter(author=user,post=current_post,contents__exact=comment).exists():
                print("post not created")
                #send message you already said this
            else:
                Comments.objects.create(author=user,contents=comment,post=current_post)
                current_post.comment_count = count+1
                current_post.save()
                print("post created")
                #add integer to comment feild

        return context
#post section /////////////////////
class Create_Comment(generic.CreateView):
    pass

class Create_DividendWealthGroup(generic.TemplateView):
    template_name = "create_gen_group.html"

    def get_context_data(self, *args, **kwargs):
        # Just include the form
        context = super(Create_DividendWealthGroup, self).get_context_data(*args, **kwargs)
        # check if url has edititable group
        edit_group = self.request.GET.getlist('edit') if 'edit' in self.request.GET else None
        edit_group_form = "false"
        if edit_group == None:
            pass
            # do nothing
        else:
            # get the group to edit
            if GenGroup.objects.filter(slug=edit_group[0]).exists():
                edit_group_form = "true"
                context["current_group"] = GenGroup.objects.filter(slug=edit_group[0])[0]
        context["edit_group"] = edit_group_form
        # !!!!!!!!!!!!
        # current group name will conflict with list of existing group name
        # use the template script to create javascript function
        #get a list of group names that connot be used
        group_names= []
        if GenGroup.objects.all():
            group_list = GenGroup.objects.all()
            for group in group_list:
                group_names.append(group.title.lower())
            context["group_names"] = group_names
        return context

    def post(self,request, **kwargs):
        print(self.request.POST)
        group_create_form = self.request.POST.getlist('group_create_form') if 'group_create_form' in self.request.POST else None
        group_image = self.request.FILES.getlist('group_image') if 'group_image' in request.FILES else None
        edit_group = self.request.POST.getlist('edit_group') if 'edit_group' in request.POST else None
        try:
            if edit_group[0] == '':
                edit_group = None
        except:
            edit_group = None

        if edit_group != None:
            # edit user group
            if group_create_form != None:
                user = User_Profile.objects.filter(user=self.request.user)[0]
                group_title = group_create_form[0]

                group_description = group_create_form[1]
                group_categories = group_create_form[2]
                group_value_proposition = group_create_form[3]
                group_rules_guidelines = group_create_form[4]
                # if user does not select button there is an error
                try:
                    group_payment_option = group_create_form[5]
                except:
                    group_payment_option = "free"
                try:
                    group_pament_method= group_create_form[6]
                except:
                    group_pament_method = "null"

                try:
                    group_price= group_create_form[7]
                except:
                    group_price = "null"

                # validate group name
                #we need to see if the slug exist with a group already
                # group_slug_name=slugify(group_title)
                # if GenGroup.objects.filter(slug=group_slug_name).exists():
                #     group_title = group_title + "-wealth"
                #     messages.info(self.request, "Opps!  There already exists a group with your chosen name.")
                #     url = reverse('core:create-group')
                #     return HttpResponseRedirect(url)
                #Save photo
                # https://stackoverflow.com/questions/41329858/how-to-delete-an-imagefield-image-in-a-django-model
                # delete file Profile.objects.get(id=1).photo.delete(save=True)

                # document = PostPicture.objects.create(post_picture=path, post=created_post)

                # validate price
                # the defalut is empty so if it is empty make it a free group
                if group_payment_option == '' or  group_payment_option == 'free':
                    group_type = 'f'
                    group_price = 0
                else:
                    if group_pament_method != '':
                        group_type = 'o'
                        print(group_price)
                        group_price = int(group_price)
                    else:
                        group_type = 's'
                        group_price = int(group_price)
                # if the user is free and wants to monotize group do not allow
                if user.dividend_wealth_membership.membership == 'f' and group_type != 'f':
                    new_group = GenGroup.objects.filter(slug=edit_group[0])[0]
                    new_group.description = group_description
                    new_group.value_proposition=group_value_proposition
                    new_group.rules_guidlines=group_rules_guidelines
                    # new_group.price=group_price
                    # new_group.group_type=group_type
                    # check if there was a new picture
                    if group_image != None:
                        group_image = group_image[0]
                        save_path = os.path.join(settings.MEDIA_ROOT, 'group_img', group_image.name)
                        path = default_storage.save(save_path, group_image)
                        rotate_image(path)
                        new_group.group_picture=path

                    new_group.published=False
                    if DividendWealthConnectedAccount.objects.filter(user_profile=user).exists():
                        messages.info(self.request, "Paid Groups are reserved for Dividend Wealth Members. Please consider becomming a member, in doing so, your group will be allowed to accept payments from its members")
                        new_group.unpublished_reason = "Freemium Accounts cannot monotize groups please consider becoming a Dividend Wealth Member"
                        new_group.save()
                    else:
                        new_group.published = False
                        messages.info(self.request, "You have recently created a monotized group. Please Go to your Account Page and Connect to Stripe to collect Payments.")

                    new_group.save()
                else:
                    new_group = GenGroup.objects.filter(slug=edit_group[0])[0]
                    new_group.description = group_description
                    new_group.value_proposition=group_value_proposition
                    new_group.rules_guidlines=group_rules_guidelines
                    # new_group.price=group_price
                    # new_group.group_type=group_type
                    # check if there was a new picture
                    if group_image != None:
                        group_image = group_image[0]
                        save_path = os.path.join(settings.MEDIA_ROOT, 'group_img', group_image.name)
                        path = default_storage.save(save_path, group_image)
                        rotate_image(path)
                        new_group.group_picture=path
                    # check if user has connected account
                    if DividendWealthConnectedAccount.objects.filter(user_profile=user).exists():
                        pass
                    else:
                        new_group.published = False
                        messages.info(self.request, "You have recently created a monotized group. Please Go to your Account Page and Connect to Stripe to collect Payments.")
                        new_group.unpublished_reason = "You have not connected your Stripe Account please go to your Dividend Wealth Account page to connnect to stripe"
                    new_group.save()


                #validate categories
                group_categories = group_categories.split(',')
                group_categories=set(group_categories)


                #  delet current categories
                list_of_present_group_cats=GroupCategories.objects.filter(group__slug=edit_group[0])
                for cat in list_of_present_group_cats:
                    cat.delete()

                # create categories
                for word in group_categories:
                    # check if the category exist
                    if Categories.objects.filter(description__iexact=word):
                        cat= Categories.objects.filter(description__iexact=word)[0]
                        GroupCategories.objects.create(group=new_group,category=cat)
                    else:
                        cat=Categories.objects.create(description=word)
                        GroupCategories.objects.create(group=new_group,category=cat)


                new_group.save()
        else:
            # create new cgroup
            if group_create_form != None:
                user = User_Profile.objects.filter(user=self.request.user)[0]
                group_title = group_create_form[0]
                group_image = group_image[0]
                group_description = group_create_form[1]
                group_categories = group_create_form[2]
                group_value_proposition = group_create_form[3]
                group_rules_guidelines = group_create_form[4]
                # if user does not select button there is an error
                try:
                    group_payment_option = group_create_form[5]
                except:
                    group_payment_option = "free"
                try:
                    group_pament_method= group_create_form[6]
                except:
                    group_pament_method = "null"

                try:
                    group_price= group_create_form[7]
                except:
                    group_price = "null"

                # validate group name
                #we need to see if the slug exist with a group already
                group_slug_name=slugify(group_title)
                if GenGroup.objects.filter(slug=group_slug_name).exists():
                    group_title = group_title + "-wealth"
                    messages.info(self.request, "Opps! There already exists a group with your chosen name.")
                    url = reverse('core:create-group')
                    return HttpResponseRedirect(url)
                #Save photo
                save_path = os.path.join(settings.MEDIA_ROOT, 'group_img', group_image.name)
                path = default_storage.save(save_path, group_image)
                rotate_image(path)

                # document = PostPicture.objects.create(post_picture=path, post=created_post)


                # validate price
                # the defalut is empty so if it is empty make it a free group
                if group_payment_option == '' or  group_payment_option == 'free':
                    group_type = 'f'
                    group_price = 0
                else:
                    if group_pament_method != '':
                        group_type = 'o'
                        group_price = int(group_price)
                    else:
                        group_type = 's'
                        group_price = int(group_price)
                # if the user is free and group type choosen is not equal to free do not publish the group
                if user.dividend_wealth_membership.membership == 'f' and group_type != 'f':
                    new_group=GenGroup.objects.create(title=group_title,description=group_description, creator=user,value_proposition=group_value_proposition,rules_guidlines=group_rules_guidelines,price=group_price,group_type=group_type,group_picture=path,published=False)

                    # Do not publish group if person does not have dividend wealth membership
                    if DividendWealthConnectedAccount.objects.filter(user_profile=user).exists():
                        messages.info(self.request, "Paid Groups are reserved for Dividend Wealth Members. Please consider becomming a member, in doing so, your group will be allowed to accept payments from its members")
                        new_group.unpublished_reason = "Freemium Accounts cannot monotize groups please consider becoming a Dividend Wealth Member"
                        new_group.save()
                    else:
                        new_group.published = False
                        messages.info(self.request, "You have recently created a monotized group. Please Go to your Account Page and Connect to Stripe to collect Payments.")
                        new_group.save()
                else:
                    new_group=GenGroup.objects.create(title=group_title,description=group_description, creator=user,value_proposition=group_value_proposition,rules_guidlines=group_rules_guidelines,price=group_price,group_type=group_type,group_picture=path)
                    # Do not publish group if person does not have dividend wealth membership
                    if DividendWealthConnectedAccount.objects.filter(user_profile=user).exists():
                        pass
                    else:
                        new_group.published = False
                        new_group.unpublished_reason = "You have not connected your Stripe Account please go to your Dividend Wealth Account page to connnect to stripe"
                        messages.info(self.request, "You have recently created a monotized group. Please Go to your Account Page and Connect to Stripe to collect Payments.")
                        new_group.save()

                GroupMember.objects.create(group =new_group,userprofile = user,creator=True,member_status='a')

                #validate categories
                group_categories = group_categories.split(',')
                group_categories=set(group_categories)
                for word in group_categories:
                    # check if the category exist
                    if Categories.objects.filter(description__iexact=word):
                        cat= Categories.objects.filter(description__iexact=word)[0]
                        GroupCategories.objects.create(group=new_group,category=cat)
                    else:
                        cat=Categories.objects.create(description=word)
                        GroupCategories.objects.create(group=new_group,category=cat)
                new_group.save()
        print(self.request.POST)
        url = reverse('core:group-landing', kwargs={'slug': new_group.slug,})
        return HttpResponseRedirect(url)

class Group_Landing_Page(generic.TemplateView):
    template_name = "group_landing_page.html"

    def get_context_data(self, *args, **kwargs):
        # Just include the form
        context = super(Group_Landing_Page, self).get_context_data(*args, **kwargs)
        user = User_Profile.objects.filter(user=self.request.user)[0]

        kw_slug=self.kwargs['slug']
        group=GenGroup.objects.filter(slug=kw_slug)[0]
        context["title"]=group.title

        if group.group_type == 'f':
            context["group_free"] = 'true'
        else:
            context["group_free"] = 'false'
            if group.group_type == 'o':
                context["price_method"] = ' /Admission Fee'
                context["button_statement"] = 'Pay Now'
            else:
                context["price_method"] = ' /Monthly Fee'
                context["button_statement"] = 'Suscribe Now'
        try:
            context["price"]= "{:.2f}".format(group.price /100 )
        except:
            context["price"] = "Free"
        try:
            context["photo"]=group.group_picture.url
        except:
            context["photo"]="/"

        context["group_description"]=group.description
        context["value_proposition"]=group.value_proposition
        context["rules_guidlines"]=group.rules_guidlines
        context["group_slug"]= group.slug
        context["group_type"]= group.group_type

        #check if user has stripe customer id
        if user.stripe_customer_id is None or user.stripe_customer_id == '':
            new_customer_id = stripe.Customer.create(email= user.user.email)
            user.stripe_customer_id = new_customer_id['id']
            DividendWealthSubscription.objects.create(user_profile=user,stripe_subscription_id="free")
            new_membership= DividendWealthMembership.objects.filter(membership='f')[0]
            user.dividend_wealth_membership = new_membership
            user.save()

        # get the categories of group

        if  GroupCategories.objects.filter(group=group).exists():
            group_categories = GroupCategories.objects.filter(group=group)
            context["group_categories"] = group_categories
        # Check if user has default card
        default_card = stripe.Customer.retrieve(user.stripe_customer_id)
        default_card = default_card["default_source"]
        context["default_card_id"] =default_card

        context["has_default_card"]= 'true'
        if default_card is None:
            context["has_default_card"]= 'false'
        else:
            default_card_info=stripe.Customer.retrieve_source(
              user.stripe_customer_id,
             default_card,
            )
            context["card_name"]= default_card_info["name"]
            context["card_last4"]= default_card_info["last4"]
            context["card_month"]= default_card_info["exp_month"]
            context["card_exyear"]= default_card_info["exp_year"]
            context["card_brand"]= default_card_info["brand"]

        # hide group metrics if there are no post
        if Post.objects.filter(group=group).exists():
            if Post.objects.filter(group=group).count()> 5:
                display_metrics = "true"
            else:
                display_metrics = "false"
        else:
            display_metrics = "false"
        context["display_metrics"] = display_metrics

        # calculate group metrics




        context['current_user'] = user
        context['stripe_pluishable_key'] = settings.STRIPE_PUBLIC_KEY
        return context

    def post(self,request, **kwargs):
        # https://stackoverflow.com/questions/33239308/how-to-get-exception-message-in-python-properly
        stripeToken = self.request.POST.getlist('stripeToken') if 'stripeToken' in request.POST else None
        name_on_card = self.request.POST.getlist('name_on_card') if 'name_on_card' in request.POST else None
        use_default_card = self.request.POST.getlist('use_default_card') if 'use_default_card' in request.POST else None
        group_slug_payment = self.request.POST.getlist('group_slug_payment') if 'group_slug_payment' in request.POST else None

        if stripeToken != None:

            selected_membership = self.request.POST.getlist('selected_membership') if 'selected_membership' in request.POST else None
            #create stripe customer id if customer does not already have one
            user = User_Profile.objects.filter(user=self.request.user)[0]
            #check if user has strip customer id
            if user.stripe_customer_id is None or user.stripe_customer_id == '':
                new_customer_id = stripe.Customer.create(email= user.user.email)
                user.stripe_customer_id = new_customer_id['id']
                DividendWealthSubscription.objects.create(user_profile=user,stripe_subscription_id="free")
                new_membership= DividendWealthMembership.objects.filter(membership='f')[0]
                user.dividend_wealth_membership = new_membership
                user.save()
            else:
                print(" has stripe customer id")
            # check to see if we have a valid group membership
            if selected_membership[0] == "s" or selected_membership[0] == "o" :
                try:
                    tokenizedPayment= stripeToken[0]
                    #create card
                    card=stripe.Customer.create_source(
                      user.stripe_customer_id,
                      source=tokenizedPayment,
                    )
                    #add name to card
                    stripe.Customer.modify_source(
                      user.stripe_customer_id,
                      card["id"],
                      name=name_on_card[0],
                    )
                    # create a group admission fee
                    if selected_membership[0] == 'o':
                        #get the connected account
                            #note filter to make sure group exists
                        group = GenGroup.objects.filter(slug=group_slug_payment[0])[0]
                        group_creator_connected_account = DividendWealthConnectedAccount.objects.filter(user_profile=group.creator)[0].stripe_connected_account_id
                        #Create one time fee
                        #payment relationship goes as following, given the sale, less stripe fees, resultant is customer revenue, less Dividend Wealth, resultant is customer income
                        dividend_wealth_percent = .1
                        sale = group.price #the lowest num possible is 2
                        sale_reformated = sale/100
                        stripe_fee = .029 *sale_reformated +.3
                        customer_revenue =sale_reformated - stripe_fee
                        dividend_wealth_fee = dividend_wealth_percent* customer_revenue
                        customer_income = customer_revenue-dividend_wealth_fee

                        # converting the float back to a whole number
                        # print('first',customer_income)
                        customer_income=customer_income *100
                        # print('second',customer_income)
                        # turning float into a string
                        num_string=str(customer_income)
                        # taking the unrounded integer
                        num_string_list=num_string.split('.')
                        customer_income= int(num_string_list[0])
                        # print('third',customer_income)


                        charge = stripe.Charge.create(
                          amount=sale,
                          currency="usd",
                          source= card["id"],
                          customer= user.stripe_customer_id,
                          transfer_data={
                            "amount": customer_income, #make sure that it is a whole number
                            "destination":group_creator_connected_account,
                          }
                        )
                        charge_proof=stripe.Charge.retrieve(
                          charge["id"],
                        )
                        # if the payment was succesful create new subscription
                        if charge_proof["paid"] == True:
                            print("charge went through")
                            #create group_member or grab previous membership
                            if GroupMember.objects.filter(group=group,userprofile=user).exists():
                                member = GroupMember.objects.filter(group=group,userprofile=user)[0]
                            else:
                                member=GroupMember.objects.create(group=group,userprofile=user)#no need to define member_status
                            #Create new subscription or update old member
                            if GroupSubscription.objects.filter(group_member=member,group=group,connected_account=group.creator).exists():
                                 new_group_sup = GroupSubscription.objects.filter(group_member=member,group=group)[0]
                                 new_group_sup.active = True
                                 new_group_sup.price = sale
                                 new_group_sup.save()
                            else:
                                new_group_sup = GroupSubscription.objects.create(price=sale,group=group,group_member=member,connected_account=group.creator)

                            #create payment history
                            description='Membership Fee for '+ group.title.title()
                            GroupPayment.objects.create(price=sale,person_paying=user,person_receiving=group.creator,group=group,description=description,charge_id=charge["id"])

                            messages.info(self.request, "Welcome To "+group.title.title())
                            url = reverse('core:group', kwargs={'slug': group.slug,})
                            return HttpResponseRedirect(url)
                        else:

                            messages.info(self.request, "Your card has been denied")
                            url = reverse('core:group-landing', kwargs={'slug': group.slug,})
                            return HttpResponseRedirect(url)
                    # create group subscription
                    else:
                        #get the connected account
                            #note filter to make sure group exists
                        group = GenGroup.objects.filter(slug=group_slug_payment[0])[0]
                        group_creator_connected_account = DividendWealthConnectedAccount.objects.filter(user_profile=group.creator)[0].stripe_connected_account_id
                        #Create  fee
                        #payment relationship goes as following, given the sale, less stripe fees, resultant is customer revenue, less Dividend Wealth, resultant is customer income
                        dividend_wealth_percent = .1
                        sale = group.price #the lowest num possible is 2
                        sale_reformated = sale/100
                        stripe_fee = .029 *sale_reformated +.3
                        customer_revenue =sale_reformated - stripe_fee
                        dividend_wealth_fee = dividend_wealth_percent* customer_revenue
                        customer_income = customer_revenue-dividend_wealth_fee

                        # converting the float back to a whole number
                        # print('first',customer_income)
                        customer_income=customer_income *100
                        # print('second',customer_income)
                        # turning float into a string
                        num_string=str(customer_income)
                        # taking the unrounded integer
                        num_string_list=num_string.split('.')
                        customer_income= int(num_string_list[0])
                        # print('third',customer_income)


                        charge = stripe.Charge.create(
                          amount=sale,
                          currency="usd",
                          source= card["id"],
                          customer= user.stripe_customer_id,
                          transfer_data={
                            "amount": customer_income, #make sure that it is a whole number
                            "destination":group_creator_connected_account,
                          }
                        )
                        charge_proof=stripe.Charge.retrieve(
                          charge["id"],
                        )
                        # if the payment was succesful create new subscription
                        if charge_proof["paid"] == True:
                            print("charge went through")
                            #create group_member or grab previous membership
                            if GroupMember.objects.filter(group=group,userprofile=user).exists():
                                member = GroupMember.objects.filter(group=group,userprofile=user)[0]
                            else:
                                member=GroupMember.objects.create(group=group,userprofile=user) #no need to define member_status
                            #Create new subscription or update old member
                            if GroupSubscription.objects.filter(group_member=member,group=group,connected_account=group.creator).exists():
                                 new_group_sup = GroupSubscription.objects.filter(group_member=member,group=group)[0]
                                 new_group_sup.active = True
                                 new_group_sup.price = sale
                                 new_group_sup.subscription = True
                                 new_group_sup.save()
                                 # print('created',new_group_sup.created)
                                 new_group_sup.next_payment = datetime.now() + timedelta(days=30)
                                 # thrirty_days = new_group_sup.next_payment
                                 # print("thirty days next bill is ,",thrirty_days)
                                 new_group_sup.save()
                            else:
                                new_group_sup = GroupSubscription.objects.create(price=sale,subscription = True,group=group,group_member=member,connected_account=group.creator)
                                # add thirty days to current bill cycle
                                # new_group_sup.print('created',new_group_sup.created)
                                new_group_sup.next_payment = new_group_sup.next_payment + timedelta(days=30)
                                # thrirty_days = new_group_sup.next_payment
                                # print("thirty days next bill is,",thrirty_days)
                                new_group_sup.save()
                            #create payment history
                            description='Monthly Membership Fee for '+ group.title.title()
                            GroupPayment.objects.create(price=sale,person_paying=user,person_receiving=group.creator,group=group,description=description,charge_id=charge["id"])

                            messages.info(self.request, "Welcome To "+group.title.title())
                            url = reverse('core:group', kwargs={'slug': group.slug,})
                            return HttpResponseRedirect(url)
                        else:

                            messages.info(self.request, "Your card has been denied")
                            url = reverse('core:group-landing', kwargs={'slug': group.slug,})
                            return HttpResponseRedirect(url)
                except Exception as e:
                    messages.info(self.request, "your card has been denied")
                    # Just print(e) is cleaner and more likely what you want,
                    # but if you insist on printing message specifically whenever possible...
                    if hasattr(e, 'message'):
                        print(e.message)
                    else:
                        print(e)
                    url = reverse('core:group-landing', kwargs={'slug': group.slug,})
                    return HttpResponseRedirect(url)
                #create a new subscription
                #Create new subscription
                #
        if use_default_card != None:
            # print("inhere")
            selected_membership_default = self.request.POST.getlist('selected_membership_default') if 'selected_membership_default' in request.POST else None
            #create stripe customer id if customer does not already have one
            user = User_Profile.objects.filter(user=self.request.user)[0]
            #check if user has strip customer id
            if user.stripe_customer_id is None or user.stripe_customer_id == '':
                new_customer_id = stripe.Customer.create(email= user.user.email)
                user.stripe_customer_id = new_customer_id['id']
                DividendWealthSubscription.objects.create(user_profile=user,stripe_subscription_id="free")
                new_membership= DividendWealthMembership.objects.filter(membership='f')[0]
                user.dividend_wealth_membership = new_membership
                user.save()
            else:
                pass
                # customer has stripe id
            # filter membership model for the membership chosen
            if selected_membership_default[0] == "s" or selected_membership_default[0] == "o":
                try:
                    # create a group admission fee
                    if selected_membership_default[0] == 'o':
                        #get the connected account
                            #note filter to make sure group exists
                        group = GenGroup.objects.filter(slug=group_slug_payment[0])[0]
                        group_creator_connected_account = DividendWealthConnectedAccount.objects.filter(user_profile=group.creator)[0].stripe_connected_account_id
                        #Create one time fee
                        #payment relationship goes as following, given the sale, less stripe fees, resultant is customer revenue, less Dividend Wealth, resultant is customer income
                        dividend_wealth_percent = .1
                        sale = group.price #the lowest num possible is 2
                        sale_reformated = sale/100
                        stripe_fee = .029 *sale_reformated +.3
                        customer_revenue =sale_reformated - stripe_fee
                        dividend_wealth_fee = dividend_wealth_percent* customer_revenue
                        customer_income = customer_revenue-dividend_wealth_fee

                        # converting the float back to a whole number
                        # print('first',customer_income)
                        customer_income=customer_income *100
                        # print('second',customer_income)
                        # turning float into a string
                        num_string=str(customer_income)
                        # taking the unrounded integer
                        num_string_list=num_string.split('.')
                        customer_income= int(num_string_list[0])
                        # print('third',customer_income)

                        # get id of default card
                        default_card = stripe.Customer.retrieve(user.stripe_customer_id)

                        #Create one time fee
                        charge = stripe.Charge.create(
                          amount=sale,
                          currency="usd",
                          source= default_card["default_source"],
                          customer= user.stripe_customer_id,
                           transfer_data={
                             "amount": customer_income, #make sure that it is a whole number
                             "destination":group_creator_connected_account,
                           }
                        )
                        charge_proof=stripe.Charge.retrieve(
                          charge["id"],
                        )
                        # if the payment was succesful create new subscription
                        if charge_proof["paid"] == True:
                            print("charge went through")
                            #create group_member or grab previous membership
                            if GroupMember.objects.filter(group=group,userprofile=user).exists():
                                member = GroupMember.objects.filter(group=group,userprofile=user)[0]
                            else:
                                member=GroupMember.objects.create(group=group,userprofile=user)#no need to define member_status
                            #Create new subscription or update old member
                            if GroupSubscription.objects.filter(group_member=member,group=group,connected_account=group.creator).exists():
                                 new_group_sup = GroupSubscription.objects.filter(group_member=member,group=group)[0]
                                 new_group_sup.active = True
                                 new_group_sup.price = sale
                                 new_group_sup.save()
                            else:
                                new_group_sup = GroupSubscription.objects.create(price=sale,group=group,group_member=member,connected_account=group.creator)

                            #create payment history
                            description='Membership Fee for '+ group.title.title()
                            GroupPayment.objects.create(price=sale,person_paying=user,person_receiving=group.creator,group=group,description=description,charge_id=charge["id"])

                            messages.info(self.request, "Welcome To "+group.title.title())
                            url = reverse('core:group', kwargs={'slug': group.slug,})
                            return HttpResponseRedirect(url)
                        else:

                            messages.info(self.request, "Your card has been denied")
                            url = reverse('core:group-landing', kwargs={'slug': group.slug,})
                            return HttpResponseRedirect(url)
                    # create group subscription
                    else:

                        #get the connected account
                            #note filter to make sure group exists
                        group = GenGroup.objects.filter(slug=group_slug_payment[0])[0]
                        group_creator_connected_account = DividendWealthConnectedAccount.objects.filter(user_profile=group.creator)[0].stripe_connected_account_id
                        #Create  fee
                        #payment relationship goes as following, given the sale, less stripe fees, resultant is customer revenue, less Dividend Wealth, resultant is customer income
                        dividend_wealth_percent = .1
                        sale = group.price #the lowest num possible is 2
                        sale_reformated = sale/100
                        stripe_fee = .029 *sale_reformated +.3
                        customer_revenue =sale_reformated - stripe_fee
                        dividend_wealth_fee = dividend_wealth_percent* customer_revenue
                        customer_income = customer_revenue-dividend_wealth_fee

                        # converting the float back to a whole number
                        # print('first',customer_income)
                        customer_income=customer_income *100
                        # print('second',customer_income)
                        # turning float into a string
                        num_string=str(customer_income)
                        # taking the unrounded integer
                        num_string_list=num_string.split('.')
                        customer_income= int(num_string_list[0])
                        # print('third',customer_income)

                        # get id of default card
                        default_card = stripe.Customer.retrieve(user.stripe_customer_id)

                        #Create one time fee
                        charge = stripe.Charge.create(
                          amount=sale,
                          currency="usd",
                          source= default_card["default_source"],
                          customer= user.stripe_customer_id,
                           transfer_data={
                             "amount": customer_income, #make sure that it is a whole number
                             "destination":group_creator_connected_account,
                           }
                        )
                        charge_proof=stripe.Charge.retrieve(
                          charge["id"],
                        )
                        # if the payment was succesful create new subscription
                        if charge_proof["paid"] == True:
                            print("charge went through")
                            #create group_member or grab previous membership
                            if GroupMember.objects.filter(group=group,userprofile=user).exists():
                                member = GroupMember.objects.filter(group=group,userprofile=user)[0]
                            else:
                                member=GroupMember.objects.create(group=group,userprofile=user)#no need to define member_status
                            #Create new subscription or update old member
                            if GroupSubscription.objects.filter(group_member=member,group=group,connected_account=group.creator).exists():
                                 new_group_sup = GroupSubscription.objects.filter(group_member=member,group=group)[0]
                                 new_group_sup.active = True
                                 new_group_sup.price = sale
                                 new_group_sup.subscription = True
                                 new_group_sup.save()
                                 # print('created',new_group_sup.created)
                                 new_group_sup.next_payment = datetime.now() + timedelta(days=30)
                                 # thrirty_days = new_group_sup.next_payment
                                 # print("thirty days next bill is ,",thrirty_days)
                                 new_group_sup.save()
                            else:
                                new_group_sup = GroupSubscription.objects.create(price=sale,subscription = True,group=group,group_member=member,connected_account=group.creator)
                                # add thirty days to current bill cycle
                                # new_group_sup.print('created',new_group_sup.created)
                                new_group_sup.next_payment = datetime.now()+ datetime.timedelta(days=30)
                                # thrirty_days = new_group_sup.next_payment
                                # print("thirty days next bill is,",thrirty_days)
                                new_group_sup.save()
                            #create payment history
                            description='Monthly Membership Fee for '+ group.title.title()
                            GroupPayment.objects.create(price=sale,person_paying=user,person_receiving=group.creator,group=group,description=description,charge_id=charge["id"])

                            messages.info(self.request, "Welcome To "+group.title.title())
                            url = reverse('core:group', kwargs={'slug': group.slug,})
                            return HttpResponseRedirect(url)
                        else:

                            messages.info(self.request, "Your card has been denied")
                            url = reverse('core:group-landing', kwargs={'slug': group.slug,})
                            return HttpResponseRedirect(url)
                except Exception as e:
                    messages.info(self.request, "your card has been denied")
                    # Just print(e) is cleaner and more likely what you want,
                    # but if you insist on printing message specifically whenever possible...
                    if hasattr(e, 'message'):
                        print(e.message)
                    else:
                        print(e)
                    url = reverse('core:group-landing', kwargs={'slug': group.slug,})
                    return HttpResponseRedirect(url)


    # Previous solution for creating group
    # def form_valid(self, form,):
    #      """Saves current user to the profile """
    #      groupform = form.save(commit=False)
    #      groupform.creator = get_object_or_404(User_Profile, user=self.request.user)
    #      groupform.save()
    #      return HttpResponseRedirect(reverse('core:user_dashboard')) #home page

class Detail_Group(generic.DetailView):
    model = GenGroup
    template_name = "group_detail.html"

    def get(self, *args, **kwargs):
        print(self.request)
        similar_group_slug=self.request.GET.getlist('similar_group_slug') if 'similar_group_slug' in self.request.GET else None
        # section veariabels for loading more comments
        load_more_comments_post_id =self.request.GET.getlist('load_more_comments_post_id') if 'load_more_comments_post_id' in self.request.GET else None
        load_more_comments_last_comment_id =self.request.GET.getlist('load_more_comments_last_comment_id') if 'load_more_comments_last_comment_id' in self.request.GET else None
        # Section variabeles for loading replies
        load_more_replys_post_id =self.request.GET.getlist('load_more_replys_post_id') if 'load_more_replys_post_id' in self.request.GET else None
        load_more_replys_comment_id =self.request.GET.getlist('load_more_replys_comment_id') if 'load_more_replys_comment_id' in self.request.GET else None
        load_more_replys_reply_id =self.request.GET.getlist('load_more_replys_reply_id') if 'load_more_replys_reply_id' in self.request.GET else None

        # section is for getting post id
        load_user_likes =self.request.GET.getlist('load_user_likes') if 'load_user_likes' in self.request.GET else None

        # Section is for getting more files
        group_infinite_file_scroll =self.request.GET.getlist('group_infinite_file_scroll') if 'group_infinite_file_scroll' in self.request.GET else None

        # Section is for getting more stocks
        group_infinite_watchlist_scroll = self.request.GET.getlist('group_infinite_watchlist_scroll') if 'group_infinite_watchlist_scroll' in self.request.GET else None
        # Section if for loading stocks to wath list
        watchlist_stocks = self.request.GET.getlist('watchlist_stocks') if 'watchlist_stocks' in self.request.GET else None

        # section is to load posts of stocks
        watchlist_stock_slug_load_post = self.request.GET.getlist('watchlist_stock_slug_load_post') if 'watchlist_stock_slug_load_post' in self.request.GET else None

        if similar_group_slug != None:
            similar_group_slug=similar_group_slug[0]
            group = GenGroup.objects.filter(slug=similar_group_slug)[0]
            value_proposition=group.value_proposition
            rules_guidlines=group.rules_guidlines
            group_title=group.title.title()
            group_description= group.description
            data = {
             'value_proposition': value_proposition,
             'rules_guidlines':rules_guidlines,
             'group_title':group_title,
             'group_description':group_description,
            }
            return JsonResponse(data)

        if load_more_comments_post_id != None:
            # get the commonts assosiated with the post where omment pk is less than the comment
            last_comment = int(load_more_comments_last_comment_id[0])
            load_more_comments_post_id = int(load_more_comments_post_id[0])
            # check if we should get more comments
            comments_count = Comments.objects.filter(post__pk=load_more_comments_post_id, pk__lt=last_comment).count()
            paginator = 3
            comments_count=comments_count - paginator
            if comments_count <= 0:
                get_more= "false"
            else:
                get_more= "true"

            comments_to_load = Comments.objects.filter(post__pk=load_more_comments_post_id, pk__lt=last_comment,hidden=False).order_by('-pk')[:paginator]
            comment_list= []
            for comment in comments_to_load:
                print(comment)
                # print("comment beng created at the moment",comment.pk)
                reicpients_name_url=[]
                # find recipients associated with the comment
                for user in comment.recipients.all():
                    if User_Profile.objects.filter(pk=user.pk).exists():
                        recipient = User_Profile.objects.filter(pk=user.pk)[0]
                        reicpients_name_url.append(recipient.user.username)
                        reicpients_name_url.append('#')
                    else:
                        print("nope user recipents")
                #add stocks to post if any
                stock_name_url=[]
                for stock in comment.stocks.all():
                    if Stocks.objects.filter(pk=stock.pk).exists():
                        stock_to_add = Stocks.objects.filter(pk=stock.pk)[0]
                        stock_name_url.append(stock_to_add.ticker)
                        stock_name_url.append(stock_to_add.get_absolute_url())
                #add photo to post if any

                url_of_photo_id = []
                comment_pics = CommentsPicture.objects.filter(comments__pk=comment.id)
                for document in comment_pics:
                        url_of_photo_id.append(document.comments_picture.url)
                        url_of_photo_id.append(document.pk)

                # packaging the Comment to send to channels in json format
                #kkeping post_id for simplicity
                post_id = comment.id
                #know which post to put comment under
                current_post_id = load_more_comments_post_id

                user = comment.author

                if bool(user.profile_pic) != False:
                    user_profile_pic_url_post =  user.profile_pic.url
                else:
                    user_profile_pic_url_post = 'false'

                user_name_post = user.user.username

                #time_published_post = created_post.published
                now = timezone.now()
                value = comment.published
                difference = now - value
                if difference <= timedelta(minutes=1):
                    time_post = 'just now'
                time_post =  '%(time)s ago' % {'time': timesince(value).split(', ')[0]}
                # time_post =now.strftime("%a, %I:%M:%S %p")
                time_published_post = time_post

                if comment.stocks.all():
                    stock_list_post = stock_name_url
                else:
                    stock_list_post = 'false'

                content_post = comment.contents

                if comment.commentspicture_set.all():
                    url_of_photo_id_post = url_of_photo_id
                else:
                    url_of_photo_id_post = 'false'

                if comment.recipients.all():
                    reicpients_name_url_post = reicpients_name_url
                else:
                    reicpients_name_url_post = 'false'

                comment_like = CommentsLike.objects.filter(comments=comment).count()

                if CommentReply.objects.filter(comment=comment).exists():
                    reply = "true"
                else:
                    reply = "false"

                commment_like_count_fun = comment.comment_like_count()
                if commment_like_count_fun >0 :
                    comment_like_user = comment.comment_last_like().userprofile.user.username
                else:
                    comment_like_user = "false"


                view_group_comment = {
                    #Comment id
                    "post_id" : post_id,
                    #Post id
                    "current_post_id" : current_post_id,
                    "user_profile_pic_url_post":user_profile_pic_url_post,
                    "user_name_post": user_name_post,
                    # "comments_on_post": comments_on_post,
                    "time_published_post": time_published_post,
                    "stock_list_post": stock_list_post,
                    # "title_of_post": title_of_post,
                    "content_post": content_post,
                    "url_of_photo_id_post":url_of_photo_id_post,
                    "reicpients_name_url_post": reicpients_name_url_post,
                    "comment_like":comment_like,
                    "reply": reply,
                    "comment_like_user":comment_like_user
                }

                view_group_comment = json.dumps(view_group_comment)
                comment_list.append(view_group_comment)

            comment_list=json.dumps(comment_list)
            print(get_more)
            data = {
             'comment_list': comment_list,
             'get_more':get_more
            }
            return JsonResponse(data)

        if load_more_replys_reply_id != None:

            post_id = int(load_more_replys_post_id[0])
            comment_id = int(load_more_replys_comment_id[0])
            reply_id = int(load_more_replys_reply_id[0])
            # why would reply id  equal zeroo???
            if reply_id == 0:

                # Check to see if we have more replies
                reply_count = CommentReply.objects.filter(comment__pk=comment_id,hidden=False).count()
                paginator = 4
                reply_count= reply_count - paginator
                if reply_count <= 0:
                    get_more= "false"
                else:
                    get_more= "true"
                comments_to_load = CommentReply.objects.filter(comment__pk=comment_id,hidden=False).order_by('-pk')[:paginator]
                comment_list = []
            else:

                # Check to see if we have more replies
                reply_count = CommentReply.objects.filter(comment__pk=comment_id, pk__lt=reply_id,hidden=False).count()
                paginator = 4
                reply_count= reply_count - paginator
                if reply_count <= 0:
                    get_more= "false"
                else:
                    get_more= "true"
                comments_to_load = CommentReply.objects.filter(comment__pk=comment_id, pk__lt=reply_id,hidden=False).order_by('-pk')[:paginator]
                comment_list = []
            for comment in comments_to_load:

                # print("comment beng created at the moment",comment.pk)
                reicpients_name_url=[]
                # find recipients associated with the comment
                for user in comment.recipients.all():
                    if User_Profile.objects.filter(pk=user.pk).exists():
                        recipient = User_Profile.objects.filter(pk=user.pk)[0]
                        reicpients_name_url.append(recipient.user.username)
                        reicpients_name_url.append('#')
                    else:
                        print("nope user recipents")
                #add stocks to post if any
                stock_name_url=[]
                for stock in comment.stocks.all():
                    if Stocks.objects.filter(pk=stock.pk).exists():
                        stock_to_add = Stocks.objects.filter(pk=stock.pk)[0]
                        stock_name_url.append(stock_to_add.ticker)
                        stock_name_url.append(stock_to_add.get_absolute_url())
                #add photo to post if any

                url_of_photo_id = []
                comment_pics = CommentReplyPicture.objects.filter(commentreply__pk=comment.id)
                for document in comment_pics:
                        url_of_photo_id.append(document.commentreply_picture.url)
                        url_of_photo_id.append(document.pk)

                # packaging the Comment to send to channels in json format
                #kkeping post_id for simplicity

                #know which post to put comment under
                current_post_id = post_id

                reply_post_id = comment.id

                current_comment_id = comment_id

                user = comment.author

                if bool(user.profile_pic) != False:
                    user_profile_pic_url_post =  user.profile_pic.url
                else:
                    user_profile_pic_url_post = 'false'

                user_name_post = user.user.username

                #time_published_post = created_post.published

                now = timezone.now()
                value = comment.published
                difference = now - value
                if difference <= timedelta(minutes=1):
                    time_post = 'just now'
                time_post =  '%(time)s ago' % {'time': timesince(value).split(', ')[0]}
                # time_post =now.strftime("%a, %I:%M:%S %p")
                time_published_post = time_post

                if comment.stocks.all():
                    stock_list_post = stock_name_url
                else:
                    stock_list_post = 'false'

                content_post = comment.contents

                if comment.commentreplypicture_set.all():
                    url_of_photo_id_post = url_of_photo_id
                else:
                    url_of_photo_id_post = 'false'

                if comment.recipients.all():
                    reicpients_name_url_post = reicpients_name_url
                else:
                    reicpients_name_url_post = 'false'

                comment_like = CommentReplyLike.objects.filter(commentreply=comment).count()

                commment_like_count_fun = comment.reply_like_count()
                if commment_like_count_fun >0 :
                    comment_like_user = comment.reply_last_like().userprofile.user.username
                else:
                    comment_like_user = "false"
                print("post id of reply",current_post_id)
                view_group_comment = {
                    #Comment id
                    "post_id" : reply_post_id,
                    #Post id
                    "current_post_id" : current_post_id,
                    "current_comment_id": current_comment_id,
                    "user_profile_pic_url_post":user_profile_pic_url_post,
                    "user_name_post": user_name_post,
                    # "comments_on_post": comments_on_post,
                    "time_published_post": time_published_post,
                    "stock_list_post": stock_list_post,
                    # "title_of_post": title_of_post,
                    "content_post": content_post,
                    "url_of_photo_id_post":url_of_photo_id_post,
                    "reicpients_name_url_post": reicpients_name_url_post,
                    "comment_like":comment_like,
                    "comment_like_user":comment_like_user,
                }

                view_group_comment = json.dumps(view_group_comment)
                comment_list.append(view_group_comment)

            comment_list=json.dumps(comment_list)
            data = {
             'comment_list': comment_list,
             'get_more':get_more
            }
            return JsonResponse(data)

        if load_user_likes != None:
            media =load_user_likes[0]
            action =media.split("_")
            option = action[0]
            num= action[1]
            if option == 'post':
                post=Post.objects.filter(pk=int(num))[0]
                post_like=PostLike.objects.filter(post=post)
                # list containing the likes of users
                like_users= []
                for like in post_like:
                    username = like.userprofile.user.username
                    url = '#'
                    if bool(like.userprofile.profile_pic) != False:
                        user_profile_pic_url_post =  like.userprofile.profile_pic.url
                    else:
                        user_profile_pic_url_post = 'false'
                    # check whether user is following the current person
                    follow = 'false'
                    like_result = {
                     'username': username,
                     'user_profile_pic_url_post':user_profile_pic_url_post,
                     'following':follow
                    }
                    like_result = json.dumps(like_result)
                    like_users.append(like_result)

                like_users=json.dumps(like_users)
                data = {
                 'like_users': like_users,
                }
                return JsonResponse(data)

            if option == 'comment':
                comment=Comments.objects.filter(pk=int(num))[0]
                comment_like=CommentsLike.objects.filter(comments=comment)
                # list containing the likes of users
                like_users= []
                for like in comment_like:
                    username = like.userprofile.user.username
                    url = '#'
                    if bool(like.userprofile.profile_pic) != False:
                        user_profile_pic_url_post =  like.userprofile.profile_pic.url
                    else:
                        user_profile_pic_url_post = 'false'
                    # check whether user is following the current person
                    follow = 'false'
                    like_result = {
                     'username': username,
                     'user_profile_pic_url_post':user_profile_pic_url_post,
                     'following':follow
                    }
                    like_result = json.dumps(like_result)
                    like_users.append(like_result)

                like_users=json.dumps(like_users)
                data = {
                 'like_users': like_users,
                }
                return JsonResponse(data)

            if option == 'reply':
                reply=CommentReply.objects.filter(pk=int(num))[0]
                reply_like=CommentReplyLike.objects.filter(commentreply=reply)
                # list containing the likes of users
                like_users= []
                for like in reply_like:
                    username = like.userprofile.user.username
                    url = '#'
                    if bool(like.userprofile.profile_pic) != False:
                        user_profile_pic_url_post =  like.userprofile.profile_pic.url
                    else:
                        user_profile_pic_url_post = 'false'
                    # check whether user is following the current person
                    follow = 'false'
                    like_result = {
                     'username': username,
                     'user_profile_pic_url_post':user_profile_pic_url_post,
                     'following':follow
                    }
                    like_result = json.dumps(like_result)
                    like_users.append(like_result)

                like_users=json.dumps(like_users)
                data = {
                 'like_users': like_users,
                }
                return JsonResponse(data)

        if group_infinite_file_scroll != None:
            # int will be zero if there are no files

            last_file_pk=group_infinite_file_scroll[0]
            current_group = get_object_or_404(GenGroup, slug=self.kwargs['slug'])
            file_list_count=GroupFileList.objects.filter(pk__lt=int(last_file_pk),group=current_group).count()
            print("file_list_count",file_list_count)
            paginator = 4
            file_list_count= file_list_count - paginator
            if file_list_count <= 0:
                get_more= "false"
            else:
                get_more= "true"
            file_list = GroupFileList.objects.filter(pk__lt=int(last_file_pk),group=current_group).order_by('-pk')[:paginator]
            file_list_collection = []
            current_user = User_Profile.objects.filter(user=self.request.user)[0]
            current_member=GroupMember.objects.filter(group=current_group,userprofile=current_user)[0]
            current_member_status = current_member.member_status
            for file in file_list:
                print(file)
                # group_file pk
                file_pk = file.pk
                # user picture
                if bool(file.file.creator.profile_pic) != False:
                    user_profile_pic_url =  file.file.creator.profile_pic.url
                else:
                    user_profile_pic_url = 'false'
                # url to user
                url_to_user = '#'
                # file title
                file_title =string.capwords(file.file.title)
                # file description
                file_description = file.file.description
                # file name
                file_name = file.file.filename()
                print(file_name)
                # file url
                file_url = file.file.upload.url
                # file created date
                if file.file.created_date == None:
                    file_date_created = "just created"
                else:
                    now = timezone.now()
                    value = file.file.created_date
                    difference = now - value
                    if difference <= timedelta(minutes=1):
                        time_post = 'just now'
                    time_post =  '%(time)s ago' % {'time': timesince(value).split(', ')[0]}
                    # time_post =now.strftime("%a, %I:%M:%S %p")
                    file_date_created = time_post
                # does file belong to user or is user creator or admin
                user_owns_file = 'false'
                if current_user == file.file.creator:
                    user_owns_file = 'true'
                else:
                    if current_member_status == 'a' or  current_member_status == 'd':
                        user_owns_file = 'true'

                file_info = {
                    #file id
                    "file_pk" : file_pk,
                    "user_profile_pic_url" : user_profile_pic_url,
                    "url_to_user": url_to_user,
                    "file_title": file_title,
                    "file_description": file_description,
                    "file_name": file_name,
                    "file_url": file_url,
                    "user_owns_file":user_owns_file,
                    "file_date_created": file_date_created,

                }

                file_info = json.dumps(file_info)
                file_list_collection.append(file_info)

            file_list_collection = json.dumps(file_list_collection)
            data = {
             'file_list_collection': file_list_collection,
             'get_more':get_more
            }
            return JsonResponse(data)

        if group_infinite_watchlist_scroll != None:
            # int will be zero if there are no files
            last_watchlist_pk=group_infinite_watchlist_scroll[0]
            current_group = get_object_or_404(GenGroup, slug=self.kwargs['slug'])
            group_watchlist_count = GroupWatchlist.objects.filter(group=current_group,stockwatchlist__pk__lt=int(last_watchlist_pk)).count()
            print("watchlist pk",last_watchlist_pk)
            paginator = 4
            group_watchlist_count= group_watchlist_count - paginator
            if group_watchlist_count <= 0:
                get_more= "false"
            else:
                get_more= "true"
            watchlist_list = GroupWatchlist.objects.filter(group=current_group,stockwatchlist__pk__lt=int(last_watchlist_pk)).order_by('-pk')[:paginator]
            watchlist_list_collection = []
            current_user = User_Profile.objects.filter(user=self.request.user)[0]
            current_member=GroupMember.objects.filter(group=current_group,userprofile=current_user)[0]
            current_member_status = current_member.member_status
            user_watchlist = StockWatchlist.objects.filter(creator=current_user)
            for list in watchlist_list:
                # group_file pk
                watchlist_pk = list.stockwatchlist.pk
                print(watchlist_pk)
                # user picture
                if bool(list.stockwatchlist.creator.profile_pic) != False:
                    user_profile_pic_url =  list.stockwatchlist.creator.profile_pic.url
                else:
                    user_profile_pic_url = 'false'
                # url to user
                url_to_user = '#'
                # file title
                watchlist_title =string.capwords(list.stockwatchlist.title)
                # file description
                watchlist_description = list.stockwatchlist.description
                # watchlist_download
                watchlist_download = list.stockwatchlist.downloaded
                # user owns WatchList
                user_owns_list = 'false'
                if list.stockwatchlist in user_watchlist:
                # does watchlist belong to user or is user creator or admin
                    user_owns_list = 'true'
                else:
                    user_owns_list = 'false'
                if current_member_status == 'a' or  current_member_status == 'd':
                    admin_or_creator = 'true'
                else:
                    admin_or_creator = 'false'

                list_info = {
                    #file id
                    "watchlist_pk" : watchlist_pk,
                    "user_profile_pic_url" : user_profile_pic_url,
                    "url_to_user": url_to_user,
                    "watchlist_title": watchlist_title,
                    "watchlist_description": watchlist_description,
                    "admin_or_creator": admin_or_creator,
                    "watchlist_download": watchlist_download,
                    "user_owns_list":user_owns_list,
                }

                list_info = json.dumps(list_info)
                watchlist_list_collection.append(list_info)

            watchlist_list_collection = json.dumps(watchlist_list_collection)
            data = {
             'watchlist_list_collection': watchlist_list_collection,
             'get_more':get_more
            }
            return JsonResponse(data)

        if watchlist_stocks != None:
            # int will be zero if there are no files
            watchlist_pk=watchlist_stocks[0]
            current_group = get_object_or_404(GenGroup, slug=self.kwargs['slug'])

            stock_detail_list = WatchStockDetail.objects.filter(watchlist__pk=int(watchlist_pk))
            stock_list_collection = []
            current_user = User_Profile.objects.filter(user=self.request.user)[0]
            current_member=GroupMember.objects.filter(group=current_group,userprofile=current_user)[0]
            current_member_status = current_member.member_status
            user_watchlist = StockWatchlist.objects.filter(creator=current_user)
            user_owned_stocks= current_user.stock.all()

            stock_list_creator = stock_detail_list[0].watchlist.creator.user.username
            stock_list_date_created= stock_detail_list[0].watchlist.created_date
            for stockinfo in stock_detail_list:
                watchlist_pk = stockinfo.watchlist.pk
                # WatchStockDetail pk
                stockinfo_pk = stockinfo.pk
                print(stockinfo_pk)
                # stock absolute urls
                stock_url = stockinfo.stock.get_absolute_url()
                # stock company name
                stock_company_name = string.capwords(stockinfo.stock.company_name)
                # username
                username=current_user.user.username
                # watchlist_title
                watchlist_title = stockinfo.watchlist.title.title()
                # stock creator
                if current_user == stockinfo.watchlist.creator:
                    stock_creator = "true"
                else:
                    stock_creator = "false"

                username_created_stocklist=stockinfo.watchlist.creator.user.username
                # date add stock

                # stock_date = datetime.date(year_month_day[0], year_month_day[1], year_month_day[2])
                stock_date_added = stockinfo.date_added.strftime(" %B %d, %Y")
                # date watchlist created
                watchlist_created = stockinfo.watchlist.created_date.strftime(" %B %d, %Y")
                # stock ticker
                stock_ticker = stockinfo.stock.ticker
                # updated date
                stock_update_date = "Oct 16, 1:45PM"
                # stock price
                stock_price = stockinfo.stock.price
                # stock_slug
                stock_slug = stockinfo.stock.slug
                # stock dividend Yeild
                stock_yeild = stockinfo.stock.dividend_yeild
                # months
                stock_months = stockinfo.stock.get_months_display()
                # company img
                company_image = "https://mdbootstrap.com/img/Photos/Others/intro1.jpg"
                # company profile
                company_profile = "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Nihil odit magnam minima, soluta doloribus reiciendis molestiae placeat unde eos molestias. Quisquam aperiam, pariatur. Tempora, placeat ratione porro voluptate odit minima at ipsum sit amet."
                # user ouns stock
                user_owns_stock = 'false'
                if stockinfo.stock in user_owned_stocks:
                    user_owns_stock = 'true'
                # creator of stock list


                list_info = {
                    #file id
                    "stockinfo_pk" : stockinfo_pk,
                    "stock_url" : stock_url,
                    "stock_company_name": stock_company_name,
                    "username": username,
                    "stock_creator": stock_creator,
                    "stock_date_added": stock_date_added,
                    "stock_ticker": stock_ticker,
                    "watchlist_pk": watchlist_pk,
                    "stock_update_date" : stock_update_date,
                    "stock_price" : stock_price,
                    "stock_slug": stock_slug,
                    "stock_yeild": stock_yeild,
                    "stock_months": stock_months,
                    "company_image": company_image,
                    "company_profile": company_profile,
                    "watchlist_title":watchlist_title,
                    "watchlist_created":watchlist_created,
                    "user_owns_stock": user_owns_stock,
                    "username_created_stocklist":username_created_stocklist,
                }

                list_info = json.dumps(list_info)
                stock_list_collection.append(list_info)

            stock_list_collection = json.dumps(stock_list_collection)
            data = {
             'stock_list_collection': stock_list_collection,
             'stock_list_creator':stock_list_creator,
             'stock_list_date_created':stock_list_date_created

            }
            return JsonResponse(data)

        if watchlist_stock_slug_load_post != None:
            paginator = 5
            # https://chartio.com/resources/tutorials/how-to-filter-for-empty-or-null-values-in-a-django-queryset/
            # filtering for
            comments_to_load = Post.objects.filter(stocks__slug=watchlist_stock_slug_load_post[0], repost__isnull=True, hidden=False).order_by('-pk')[:paginator]
            comment_list= []
            for comment in comments_to_load:
                print(comment)
                # print("comment beng created at the moment",comment.pk)
                reicpients_name_url=[]
                # find recipients associated with the comment
                for user in comment.recipients.all():
                    if User_Profile.objects.filter(pk=user.pk).exists():
                        recipient = User_Profile.objects.filter(pk=user.pk)[0]
                        reicpients_name_url.append(recipient.user.username)
                        reicpients_name_url.append('#')
                    else:
                        print("nope user recipents")
                #add stocks to post if any
                stock_name_url=[]
                for stock in comment.stocks.all():
                    if Stocks.objects.filter(pk=stock.pk).exists():
                        stock_to_add = Stocks.objects.filter(pk=stock.pk)[0]
                        stock_name_url.append(stock_to_add.ticker)
                        stock_name_url.append(stock_to_add.get_absolute_url())
                #add photo to post if any

                url_of_photo_id = []
                comment_pics = PostPicture.objects.filter(post__pk=comment.id)
                for document in comment_pics:
                        url_of_photo_id.append(document.post_picture.url)
                        url_of_photo_id.append(document.pk)

                # packaging the Comment to send to channels in json format
                #kkeping post_id for simplicity
                post_id = comment.id
                #know which post to put comment under
                current_post_id = load_more_comments_post_id

                user = comment.author

                if bool(user.profile_pic) != False:
                    user_profile_pic_url_post =  user.profile_pic.url
                else:
                    user_profile_pic_url_post = 'false'

                user_name_post = user.user.username

                #time_published_post = created_post.published
                now = datetime.now()
                time_post =now.strftime("%a, %I:%M:%S %p")
                time_published_post = time_post

                if comment.stocks.all():
                    stock_list_post = stock_name_url
                else:
                    stock_list_post = 'false'

                content_post = comment.content

                if comment.postpicture_set.all():
                    url_of_photo_id_post = url_of_photo_id
                else:
                    url_of_photo_id_post = 'false'

                if comment.recipients.all():
                    reicpients_name_url_post = reicpients_name_url
                else:
                    reicpients_name_url_post = 'false'

                comment_like = "1"

                reply = "false"

                url_to_detail_view_of_post = comment.get_absolute_url()
                comment_like_user = "false"


                view_group_comment = {
                    #Comment id
                    "post_id" : post_id,
                    #Post id
                    "url_to_detail_view_of_post":url_to_detail_view_of_post,

                    "current_post_id" : current_post_id,
                    "user_profile_pic_url_post":user_profile_pic_url_post,
                    "user_name_post": user_name_post,
                    # "comments_on_post": comments_on_post,
                    "time_published_post": time_published_post,
                    "stock_list_post": stock_list_post,
                    # "title_of_post": title_of_post,
                    "content_post": content_post,
                    "url_of_photo_id_post":url_of_photo_id_post,
                    "reicpients_name_url_post": reicpients_name_url_post,
                    "comment_like":comment_like,
                    "reply": reply,
                    "alert": "false",
                    "comment_like_user":comment_like_user
                }

                view_group_comment = json.dumps(view_group_comment)
                comment_list.append(view_group_comment)

            comment_list=json.dumps(comment_list)
            data = {
             'comment_list': comment_list,
            }
            return JsonResponse(data)

        # if stripe code is not available then go to regular page
        return super(Detail_Group, self).get(self.request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        # Just include the form
        context = super(Detail_Group, self).get_context_data(*args, **kwargs)
        user = User_Profile.objects.filter(user=self.request.user)[0]
        context['user'] = user.user.username
        context['current_user'] = user

        default_profile_pic_url = static('img/default-profile-picture-gmail-2.png')
        context['default_profile_pic_url'] = default_profile_pic_url
        #getting groups post
        current_group = get_object_or_404(GenGroup, slug=self.kwargs['slug'])
        # Postz= get_object_or_404(Post, pk=3)
        # comments = Postz.post_comment.all()
        # print(comments)

        #list of recommended groups for user not the currnet group
        list_of_groups = GenGroup.objects.filter(~Q(id=current_group.id),published=True)
        context['group_list'] = list_of_groups

        #list of users group for creating watchlist
        users_groups = GenGroup.objects.filter(members=user)
        context['users_groups'] = users_groups

        #when user logs in change online status
        user.online_status = 'o'
        user.save()
        # self.request.session['username']= 'something esle'
        #get list of all the stocks_qun
        #using for tickers
        stocks =Stocks.objects.all()
        context["stocks"] = stocks

        #List of stocks user owns to compare against watchlist
        user_owned_stocks= user.stock.all()
        context["user_owned_stocks"] = user_owned_stocks

        #paginating alert list
        alert_list= Post.objects.filter(group=current_group,hidden=False,alert=True).prefetch_related('author','post_comment__recipients','post_comment__author','post_comment__commentreply_set','post_comment__commentreply_set__recipients','post_comment__commentreply_set__author').order_by('-published')
        paginator_alert = Paginator(alert_list,10)
        page_request_var_alert = 'alert'
        page_alert = self.request.GET.get(page_request_var_alert)
        try:
            paginated_queryset_alert = paginator_alert.page(page_alert)
        except PageNotAnInteger:
            paginated_queryset_alert = paginator_alert.page(1)
        except EmptyPage:
            paginated_queryset_alert = paginator_alert.page(paginator_alert.num_pages)
        context['alert_list'] = paginated_queryset_alert
        context['page_request_var_alert'] = page_request_var_alert

        #paginating post_list
        post_list= Post.objects.filter(group=current_group,hidden=False,alert=False).prefetch_related('author','post_comment__recipients','post_comment__author','post_comment__commentreply_set','post_comment__commentreply_set__recipients','post_comment__commentreply_set__author').order_by('-published')
        paginator = Paginator(post_list,10)
        page_request_var = 'page'
        page = self.request.GET.get(page_request_var)
        try:
            paginated_queryset = paginator.page(page)
        except PageNotAnInteger:
            paginated_queryset = paginator.page(1)
        except EmptyPage:
            paginated_queryset = paginator.page(paginator.num_pages)
        context['post_list'] = paginated_queryset
        context['page_request_var'] = page_request_var

        #get the count of group members
        group_member_count = GroupMember.objects.filter(group=current_group, active=True).count()
        context["group_member_count"] = group_member_count

        #check to see if user is in the group if so change group online statsu else create the group member and change online status
        context['moderator'] = False
        context['group_creator'] = False
        if GroupMember.objects.filter(group=current_group,userprofile=user).exists():
            #change users group online status
            group_member = GroupMember.objects.filter(group=current_group,userprofile=user)[0]
            if group_member.group_online_status == 'f':
                group_member.group_online_status = 'o'
            if group_member.userprofile == current_group.creator:
                group_member.member_status = 'a'
                context['group_creator'] = True
            if group_member.member_status == 'd':
                context['moderator'] = True

            group_member.save()
            new_member= "false"
            context['new_member'] = new_member
            # if  member is returning treat them as new member
            if group_member.active == False:
                group_member.active = True
                group_member.save()
                new_member= "true"
                context['new_member'] = new_member

        else:
            new_group_member = GroupMember.objects.create(group=current_group,userprofile=user)
            new_group_member.group_online_status = 'o'
            new_group_member.save()
            new_member= "true"
            context['new_member'] = new_member


        #WatchList  for group
        watchlist = GroupWatchlist.objects.filter(group=current_group).order_by('-pk')
        paginator_watchlist = Paginator(watchlist,5)
        page_request_var_watchlist = 'pa'
        page_watchlist = self.request.GET.get(page_request_var_watchlist)
        try:
            paginated_queryset_watchlist = paginator_watchlist.page(page_watchlist)
        except PageNotAnInteger:
            paginated_queryset_watchlist = paginator_watchlist.page(1)
        except EmptyPage:
            paginated_queryset_watchlist = paginator_watchlist.page(paginator_watchlist.num_pages)
        context['watchlist'] = paginated_queryset_watchlist
        context['page_request_var_watchlist'] = page_request_var_watchlist
                    # watchlistt = GroupWatchlist.objects.filter(group=current_group)[0]
                    # print(watchlistt.stockwatchlist.watchstockdetail_set.all()[0].stock.post_set.all())

                    # print(watchlist)
                    #
                    # print(watchlist.stockwatchlist.stocks.all())

        #Users_watchlist #note can use value and to make faster
        user_watchlist = StockWatchlist.objects.filter(creator=user)
        context['user_watchlist'] = user_watchlist

        #get the name of the group group creator
        group_creator =current_group.creator.user.username
        context['group_creator'] = group_creator
        #url key for group websocket
        data = mark_safe(json.dumps(current_group.slug))
        context['groupName'] = data

        #check if the creator of the group is the current user
        admin = False
        if current_group.creator == user:
            admin = True
        context["admin"] = admin

        #get the group files

        #groupfiles  for group
        groupfiles = GroupFileList.objects.filter(group=current_group).order_by('-date_added')
        paginator_groupfiles = Paginator(groupfiles,3)
        page_request_var_groupfiles = 'file'
        page_groupfiles = self.request.GET.get(page_request_var_groupfiles)
        try:
            paginated_queryset_groupfiles = paginator_groupfiles.page(page_groupfiles)
        except PageNotAnInteger:
            paginated_queryset_groupfiles = paginator_groupfiles.page(1)
        except EmptyPage:
            paginated_queryset_groupfiles = paginator_groupfiles.page(paginator_groupfiles.num_pages)
        context['groupfiles'] = paginated_queryset_groupfiles
        context['page_request_var_groupfiles'] = page_request_var_groupfiles

        user_notifications = Notification.objects.filter(userprofile=user).order_by('-date_created')[:10]
        context['user_notifications'] = user_notifications

        # hide group metrics if there are no post
        if Post.objects.filter(group=current_group).exists():
            if Post.objects.filter(group=current_group).count()> 5:
                display_metrics = "true"
            else:
                display_metrics = "false"
        else:
            display_metrics = "false"
        context["display_metrics"] = display_metrics
        #Section is for manipulating time spent
        # https://stackoverflow.com/questions/32211596/subtract-two-datetime-objects-python
        # https://stackoverflow.com/questions/796008/cant-subtract-offset-naive-and-offset-aware-datetimes
        #//documentation.onesignal.com/docs
        #https://mkaz.blog/code/python-string-format-cookbook/
        # group_time_spent = self.request.GET.getlist('group_time_spent') if 'group_time_spent' in self.request.GET else None
        # if group_time_spent != None:
        #     member = GroupMember.objects.filter(group=current_group,userprofile=user)[0]
        #
        #     then=member.joined
        #     this_moment=timezone.now()
        #     time_since_joining_group=this_moment- then
        #     member.timespent_in_group += (int(group_time_spent[0])/1000)
        #     # print("session time",int(group_time_spent[0])/1000)
        #     # print("time since joining group",time_since_joining_group.total_seconds())
        #     # print("time spent int group",member.timespent_in_group)
        #     percentage_of_time_meber_in_group=member.timespent_in_group/time_since_joining_group.total_seconds()
        #     # print("percentage of time in group",percentage_of_time_meber_in_group)
        #     percentage_of_time_meber_in_group=percentage_of_time_meber_in_group*100
        #     percentage_of_time_meber_in_group="{:.0f}".format(percentage_of_time_meber_in_group)
        #     print("percentage value",percentage_of_time_meber_in_group)
        #     member.in_group_time = percentage_of_time_meber_in_group
        #     member.save()

        # else:
        #     member = GroupMember.objects.filter(group=current_group,userprofile=user)[0]
        #     then=member.joined
        #     this_moment=timezone.now()
        #     time_since_joining_group=this_moment- then
        #     percentage_of_time_meber_in_group=member.timespent_in_group/time_since_joining_group.total_seconds()
        #     percentage_of_time_meber_in_group=percentage_of_time_meber_in_group*100
        #     percentage_of_time_meber_in_group="{:.0f}".format(percentage_of_time_meber_in_group)
        #     print("percentage value",percentage_of_time_meber_in_group)
        return context
        #handeling request


        #handeling post
    def post(self, request, **kwargs):
        # https://stackoverflow.com/questions/21882298/django-uploading-files-without-model
        #have to tunrn file into something django can handle
        # https://stackoverflow.com/questions/48641130/post-request-file-upload-in-django
        #https://www.revsys.com/tidbits/loading-django-files-from-code/
        #https://gearheart.io/blog/how-to-upload-files-with-django/

        # Import os
        #  from ttps://gearheart.io/blog/how-to-upload-files-with-django/
        # from django.conf import settings
        # save_path = os.path.join(settings.MEDIA_ROOT, 'uploads', request.FILES['file'])
        # path = default_storage.save(save_path, request.FILES['file'])
        # document = Document.objects.create(document=path, upload_by=request.user)


        #ajax
        #https://stackoverflow.com/questions/20822823/django-jquery-ajax-file-upload


        user = User_Profile.objects.filter(user=self.request.user)[0]
        current_group = get_object_or_404(GenGroup, slug=self.kwargs['slug'])

        # Section is for checking notitification
        notification_id_checked = self.request.POST.getlist('notification_id_checked') if 'notification_id_checked' in self.request.POST else None
        if notification_id_checked != None:
            notification = Notification.objects.filter(pk=int(notification_id_checked[0]))[0]
            notification.checked = True
            notification.save()
            data= {
            'null':'null'
            }
            return JsonResponse(data)
        # Section is for self user remove from group
        user_leave_group = self.request.POST.getlist('user_leave_group') if 'user_leave_group' in self.request.POST else None
        if user_leave_group != None:
            groupmember = GroupMember.objects.filter(group=current_group,userprofile=user)[0]

            if GroupSubscription.objects.filter(group_member=groupmember,group=groupmember.group).exists():
                group_sub= GroupSubscription.objects.filter(group_member=groupmember,group=groupmember.group)[0]
                group_sub.active = False
                group_sub.save()

            groupmember.active=False
            groupmember.save()
            messages.info(self.request,'You have left '+ current_group.title.title())
            url = reverse('core:user_dashboard')
            return HttpResponseRedirect(url)

        #Section is for creating alert
        alert_exist = self.request.POST.getlist('group_alert') if 'group_alert' in self.request.POST else None
        group_alert = self.request.POST.getlist('group_alert')
        if alert_exist != None:
            print(group_alert)
            current_group = get_object_or_404(GenGroup, slug=self.kwargs['slug'])
            try:
                group=group_alert[0]
                print(group)
            except IndexError:
                group=None
            try:
                comment=group_alert[1]

                print(comment)
            except IndexError:
                comment=None

            #///Section filters post
            stocks = None
            reicpients = None
            if comment != None:
                #variables for recipients and stocks
                reicpients = []
                stocks = []
                attached_url = []
                # filter post for users
                #split the string on space
                post_list_to_filter = comment.split()
                # check to see if post_list_is still a string
                if isinstance(post_list_to_filter, str):
                    item = post_list_to_filter
                    post_list_to_filter = []
                    post_list_to_filter.append(item)
                # get the length of the post filter variable
                list_lenght= len(post_list_to_filter)
                #print(list_lenght)
                #loop through the post filter variable check for recipents, stocks, and if long word
                for word in range(list_lenght):
                    # the for loop goes through the loop once to much so try statment is here
                    try:
                        #filter Message for stocks
                        if "$" in post_list_to_filter[word]:
                            stock = post_list_to_filter[word].split('$')
                            print(stock)
                            stocks.append(stock[1])
                            # print(stocks)
                        # filtering for user
                        if "@" in post_list_to_filter[word]:
                            reicpient = post_list_to_filter[word].split('@')
                            # print(reicpient)
                            reicpients.append(reicpient[1])
                            # print(reicpients)
                        # deleting word so that word does not break the format of page
                        # if user post embeded links this could change
                        if len(post_list_to_filter[word]) > 20:
                            len(post_list_to_filter[word])
                            del post_list_to_filter[word]

                        # check if url add it to list of url
                        url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', post_list_to_filter[word])
                        if url:
                            attached_url.append(url[0])
                    except:
                        pass
                #join the filtered list back together
                comment=' '.join(post_list_to_filter)
                #set is to make sure evey user and stock is unique
                reicpients = set(reicpients)
                stocks = set(stocks)

            if group != None and comment != None:


                if Post.objects.filter(author=user, group=current_group, content=comment, alert=True).exists():
                    print("post not created")

                    #send message you already said this
                    url = reverse('core:group', kwargs={'slug': self.kwargs['slug'],})
                    return HttpResponseRedirect(url)
                else:
                    created_post = Post.objects.create(author=user, group=current_group, description=comment, content=comment,alert=True)
                    created_post.save()
                    #add recipents to post if any
                    reicpients_name_url=[]
                    if reicpients != None:
                        for user in reicpients:
                            if User_Profile.objects.filter(user__username__iexact=user).exists():
                                recipient = User_Profile.objects.filter(user__username__iexact=user)[0]
                                created_post.recipients.add(recipient)
                                #put user name along with their url into list
                                reicpients_name_url.append(recipient.user.username)
                                reicpients_name_url.append('#')
                        #print(created_post.recipients.all())
                    #add stocks to post if any
                    stock_name_url=[]
                    if stocks != None:
                        for stock in stocks:
                            if Stocks.objects.filter(ticker__iexact=stock).exists():
                                stock_to_add = Stocks.objects.filter(ticker__iexact=stock)[0]
                                created_post.stocks.add(stock_to_add)
                                stock_name_url.append(stock_to_add.ticker)
                                stock_name_url.append(stock_to_add.get_absolute_url())
                    #add photo to post if any
                    file=None
                    photo = file
                    url_of_photo_id = []
                    if photo != None:
                        num_photo = len(photo)
                        for pic in range(num_photo):
                            save_path = os.path.join(settings.MEDIA_ROOT, 'post_img', photo[pic].name)
                            path = default_storage.save(save_path, photo[pic])
                            rotate_image(path)
                            document = PostPicture.objects.create(post_picture=path, post=created_post)
                            url_of_photo_id.append(document.post_picture.url)
                            url_of_photo_id.append(document.pk)

                    if attached_url:
                        for link in attached_url:
                            web_url =WebsiteUrl.objects.create(url=link)
                            PostUrl.objects.create(post=created_post,url=web_url)

                    # packaging the post to send to channels in json format
                    post_id = created_post.pk
                    url_to_detail_view_of_post = created_post.get_absolute_url()

                    user = User_Profile.objects.filter(user=self.request.user)[0]
                    if bool(user.profile_pic) != False:

                        user_profile_pic_url_post =  user.profile_pic.url
                    else:
                        user_profile_pic_url_post = 'false'

                    user_name_post = user.user.username

                    if created_post.post_comment.all():
                         comments_on_post = 'true'
                    else:
                        comments_on_post = 'false'

                    #time_published_post = created_post.published
                    now = datetime.now()
                    time_post =now.strftime("%a, %I:%M:%S %p")
                    time_published_post = time_post
                    if created_post.stocks.all():
                        stock_list_post = stock_name_url
                    else:
                        stock_list_post = 'false'

                    if created_post.title != None:
                        title_of_post = created_post.title
                    else:
                        title_of_post = 'false'

                    content_post = created_post.description

                    if created_post.postpicture_set.all():
                        url_of_photo_id_post = url_of_photo_id
                    else:
                        url_of_photo_id_post = 'false'

                    if created_post.recipients.all():
                        reicpients_name_url_post = reicpients_name_url
                    else:
                        reicpients_name_url_post = 'false'
                    # if attached url is empty assign the null
                    if attached_url:
                        attached_url = attached_url
                    else:
                        attached_url.append('null')



                    view_group_post = {
                        "post_id" : post_id,
                        "url_to_detail_view_of_post":url_to_detail_view_of_post,
                        "user_profile_pic_url_post":user_profile_pic_url_post,
                        "user_name_post": user_name_post,
                        "comments_on_post": comments_on_post,
                        "time_published_post": time_published_post,
                        "stock_list_post": stock_list_post,
                        "title_of_post": title_of_post,
                        "content_post": content_post,
                        "url_of_photo_id_post":url_of_photo_id_post,
                        "reicpients_name_url_post": reicpients_name_url_post,
                        "alert": 'true',
                        "attached_url":attached_url,
                    }

                    view_group_post = json.dumps(view_group_post)


                    #sending data to channels
                    channel_layer = get_channel_layer()

                    async_to_sync(channel_layer.group_send)(current_group.slug, {"type": "chat.message",
                    "view_group_post": view_group_post,})

                    id = created_post.pk
                    add_on = str(id)
                    # https://stackoverflow.com/questions/11531715/django-go-to-id-tag-inside-html
                    # http://www.learningaboutelectronics.com/Articles/How-to-create-a-session-variable-in-Django.php
                    # request.session['username']= 'David'
                    #https://stackoverflow.com/questions/11531715/django-go-to-id-tag-inside-html
                    print("post created")
                    #add integer to comment feild
                    data = {
                     'post_id': created_post.pk,
                    }
                    context = dict()
                    context["message"] = content_post

                    subject = 'Dividend Wealth Group Alert'
                    html_message = render_to_string('alert_email.html', context)
                    plain_message = strip_tags(html_message)
                    from_email = settings.EMAIL_HOST_USER
                    to = 'guogbonn@asu.edu'

                    send_mail(subject, plain_message, from_email, [to], html_message=html_message)


                    return JsonResponse(data)
                    url = reverse('core:group', kwargs={'slug': self.kwargs['slug'],})
                    object = "grouppost"#add_on
                    id = "#"+object
                    url = url + id +add_on
                    print(HttpResponseRedirect(url))
                    return HttpResponseRedirect(url)

        #////Section is for adding a file to groups///////////////////////////////
        file_modal = self.request.POST.getlist('file_modal')
        files = self.request.FILES.getlist('file_modal_file') if 'file_modal_file' in request.FILES else None
        if files != None:
            print(file_modal)
            # print(files)
            try:
                title_of_file=file_modal[0]
                # filter title
            except IndexError:
                title_of_file=None

            try:
                description_of_file=file_modal[1]
                #filter description
            except IndexError:
                description_of_file=None


            print("there is a file")
            num_file = len(files)
            for pic in range(num_file):
                save_path = os.path.join(settings.MEDIA_ROOT, 'groupfiles', files[pic].name)
                path = default_storage.save(save_path, files[pic])
                rotate_image(path)
                document = File.objects.create(upload=path, creator=user, title=title_of_file, description=description_of_file)
                GroupFileList.objects.create(group=current_group,file=document)
            file_download = str(document.filename())

            messages.info(request,file_download+' Uploaded!' )

            url = reverse('core:group', kwargs={'slug': self.kwargs['slug'],})
            object = "grouppost"#add_on
            id = "#"+object
            url = url + id
            print(HttpResponseRedirect(url))
            return HttpResponseRedirect(url)

        #////Section is for add_or_remove_stock_from_portfolio//////////////////
        #print(add_or_remove_stock_from_portfolio)
        add_or_remove_stock_from_portfolio= self.request.POST.getlist('add_or_remove_stock_from_portfolio') if 'add_or_remove_stock_from_portfolio' in self.request.POST else None
        if add_or_remove_stock_from_portfolio != None:
            try:
                option=add_or_remove_stock_from_portfolio[0]
            except IndexError:
                option=None

            try:
                ticker=add_or_remove_stock_from_portfolio[1]
            except IndexError:
                ticker=None

            try:
                quantity=add_or_remove_stock_from_portfolio[2]
            except IndexError:
                quantity=None

            if option != None:
                if option == 'add':
                    if StockInfo.objects.filter(stock__ticker__icontains=ticker,userprofile=user).exists():
                        print('stock already in portfolio')
                    else:

                        stock=Stocks.objects.filter(ticker__icontains=ticker)[0]
                        StockInfo.objects.create(stock=stock, quantity=int(quantity),userprofile=user)

                if option == 'remove':
                    stock=Stocks.objects.filter(ticker__icontains=ticker)[0]
                    if StockInfo.objects.filter(stock=stock,userprofile=user).exists():
                        StockInfo.objects.filter(stock=stock,userprofile=user)[0].delete()

                data = {
                 'message': 'nothing',

                }
                return JsonResponse(data)
        #////Section is for removing stock from watchlist
        remove_stock_from_watchlist = self.request.POST.getlist('remove_stock_from_watchlist') if 'remove_stock_from_watchlist' in self.request.POST else None
        if remove_stock_from_watchlist != None:
            try:
                watchlist_pk=remove_stock_from_watchlist[1]
            except IndexError:
                watchlist_pk=None

            try:
                ticker=remove_stock_from_watchlist[2]
            except IndexError:
                ticker=None

            try:
                element=remove_stock_from_watchlist[3]
            except IndexError:
                element=None

            if element != None:

                pk =int(watchlist_pk)

                if WatchStockDetail.objects.filter(pk=pk).exists():
                    print('here2')
                    pending_watchlist=WatchStockDetail.objects.filter(pk=pk)[0].delete()
                    data = {
                     'message': ticker,
                     'element_id': element,
                    }

                    return JsonResponse(data)
        #//// Section is for adding stocks to watchlists
        watchlist_add_stocks = self.request.POST.getlist('watchlist_add_stocks') if 'watchlist_add_stocks' in self.request.POST else None
        if watchlist_add_stocks != None:
            try:
                add_stock_watchlist_slug=self.request.POST.getlist('add_stock_watchlist_slug')[0]

            except IndexError:
                add_stock_watchlist_slug=None

            # check to see if there are any watchlist to update
            if len(watchlist_add_stocks) !=0:
                #grab the stock that we want to add
                stock = Stocks.objects.filter(slug=add_stock_watchlist_slug)[0]
                list_of_watchlist_that_has_stocks = []

                #iterate through watchlists selected and check conditions
                for list in watchlist_add_stocks:
                    #check if the watchlist exists
                    if StockWatchlist.objects.filter(creator=user,title__iexact=list).exists():
                        #grab the watchlists
                        pending_list = StockWatchlist.objects.filter(creator=user,title__iexact=list)[0]
                        #check if the watchlist has the stock iin it
                        if WatchStockDetail.objects.filter(stock=stock,watchlist=pending_list).exists():
                            #if watchlist has the stocks add the name of the watchlist to watchlist not to be edited list
                            list_of_watchlist_that_has_stocks.append(pending_list.title)
                            print('stock already exists in list')
                        else:
                            print('created new stock for list')
                            #if watchlist does not have the stock create a new model instance
                            WatchStockDetail.objects.create(stock=stock,watchlist=pending_list)


                data = {
                'message': add_stock_watchlist_slug
                }

                return JsonResponse(data)

        #//////Section Update stock portfolio shares
        update_stock_porfolio_list = self.request.POST.getlist('update_stock_porfolio_list') if 'update_stock_porfolio_list' in self.request.POST else None
        if update_stock_porfolio_list != None:
            try:
                share_count=update_stock_porfolio_list[0]
                share_count = int(share_count)
            except IndexError:
                share_count=None

            try:
                stock_slug=update_stock_porfolio_list[1]
            except IndexError:
                stock_slug=None

            if stock_slug != None:
                stockinfo = StockInfo.objects.filter(userprofile=user, stock__slug=stock_slug)[0]
                stockinfo.quantity = share_count
                stockinfo.save()
                url = reverse('core:group', kwargs={'slug': self.kwargs['slug'],})
                object = "grouppost"#add_on
                id = "#"+object
                url = url + id
                print(HttpResponseRedirect(url))
                return HttpResponseRedirect(url)

        #//////Section Post Watchlist

        post_watchlist = self.request.POST.getlist('watchlist_post') if 'watchlist_post' in self.request.POST else None
        if post_watchlist != None:
            already_in_list = []
            not_in_group_list =[]

            #if we recieved values
            if len(post_watchlist)!=0:
                print( "inhere")
                #for every value
                for list in post_watchlist:
                    #check if empty or None
                    if list != "" or list != None:
                        #check if value exist if so check if it is a list already associatied with the group
                        if StockWatchlist.objects.filter(creator=user, title=list).exists():
                             list = StockWatchlist.objects.filter(creator=user, title=list)[0]
                             if GroupWatchlist.objects.filter(stockwatchlist=list,group=current_group).exists():
                                 list_not_to_add = list.title
                                 already_in_list.append(list_not_to_add)
                            #if value is not associated add it to the group
                             else:
                                 list_to_add =list.title
                                 not_in_group_list.append(list_to_add)
                                 current_group.stock_watchlist.add(list)
                if len(already_in_list)!=0:
                    list_of_watchlist=", ".join(already_in_list)
                    user_info=list_of_watchlist+ " is already part your groups watchlist!"
                    messages.info(request, user_info)
                else:
                    list_of_watchlist=", ".join(not_in_group_list)
                    user_info=list_of_watchlist+ " added to your groups watchlist!"
                    messages.info(request, user_info)
                url = reverse('core:group', kwargs={'slug': self.kwargs['slug'],})
                object = "grouppost"#add_on
                id = "#"+object
                url = url + id
                print(HttpResponseRedirect(url))
                return HttpResponseRedirect(url)

        #///////////////////////
        #//Section Create WatchList
        create_watchlist = self.request.POST.getlist('create_watchlist') if 'create_watchlist' in self.request.POST else None
        if create_watchlist != None:
            print(create_watchlist)
            try:
                watchlist_title=create_watchlist[0]

            except IndexError:
                watchlist_title=None

            try:
                watchlist_descr=create_watchlist[1]
            except IndexError:
                watchlist_descr=None

            try:
                watchlist_stocks=create_watchlist[2]
            except IndexError:
                watchlist_stocks=None

            try:
                watchlist_groups=create_watchlist[3]
            except IndexError:
                watchlist_groups=None

            if watchlist_stocks != None:
                created_watch_list = StockWatchlist.objects.create(creator=user, description=watchlist_descr,title =watchlist_title)
                #filter stock_list
                stock_list =watchlist_stocks.strip()
                stock_list= stock_list.split("$")
                while("" in stock_list) :
                    stock_list.remove("")

                stock_list_y = []
                for stock in stock_list:

                    stock_listS=stock.strip()
                    stock_list_y.append(stock_listS)

                stock_list = stock_list_y
                stock_list = set(stock_list)


                for stock in stock_list:
                    if Stocks.objects.filter(ticker__icontains=stock).exists():
                        stock_to_add = Stocks.objects.filter(ticker__icontains=stock)[0]
                        created_watch_list.stocks.add(stock_to_add)

                if watchlist_groups != None:
                    #filter group_list
                    group_list = watchlist_groups.strip()
                    group_list = group_list.split(",")
                    while("" in group_list) :
                        group_list.remove("")

                    group_list_y = []
                    for group in group_list:

                        group_listS=group.strip()
                        group_list_y.append(group_listS)

                    group_list = group_list_y
                    group_list = set(group_list)

                    for group in group_list:
                        if GenGroup.objects.filter(title__icontains=group).exists():
                            group_watchlist = GenGroup.objects.filter(title__icontains=group)[0]
                            group_watchlist.stock_watchlist.add(created_watch_list)


                url = reverse('core:group', kwargs={'slug': self.kwargs['slug'],})
                object = "grouppost"#add_on
                id = "#"+object
                url = url + id
                print(HttpResponseRedirect(url))
                return HttpResponseRedirect(url)


        #////////Section handles creation of Post
        #when user post to a Post model
        #get the file attached to the post
        # file = request.FILES['file'] if 'file' in request.FILES else None
        file = self.request.FILES.getlist('post_img') if 'post_img' in request.FILES else None

        message = self.request.POST.getlist('message') if 'message' in self.request.POST else None
        if message != None:
            print(message)
            current_group = get_object_or_404(GenGroup, slug=self.kwargs['slug'])
            try:
                group=message[0]
                print(group)
            except IndexError:
                group=None
            try:
                comment=message[1]

                print(comment)
            except IndexError:
                comment=None

            #///Section filters post
            stocks = None
            reicpients = None
            if comment != None:
                #variables for recipients and stocks
                reicpients = []
                stocks = []
                attached_url = []
                # filter post for users
                #split the string on space
                post_list_to_filter = comment.split()
                # check to see if post_list_is still a string
                if isinstance(post_list_to_filter, str):
                    item = post_list_to_filter
                    post_list_to_filter = []
                    post_list_to_filter.append(item)
                # get the length of the post filter variable
                list_lenght= len(post_list_to_filter)
                #print(list_lenght)
                #loop through the post filter variable check for recipents, stocks, and if long word
                for word in range(list_lenght):
                    # the for loop goes through the loop once to much so try statment is here
                    try:
                        #filter Message for stocks
                        if "$" in post_list_to_filter[word]:
                            stock = post_list_to_filter[word].split('$')
                            print(stock)
                            stocks.append(stock[1])
                            # print(stocks)
                        # filtering for user
                        if "@" in post_list_to_filter[word]:
                            reicpient = post_list_to_filter[word].split('@')
                            # print(reicpient)
                            reicpients.append(reicpient[1])
                            # print(reicpients)
                        # deleting word so that word does not break the format of page
                        # if user post embeded links this could change

                        # check if url add it to list of url
                        url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', post_list_to_filter[word])
                        if url:
                            attached_url.append(url[0])

                        if len(post_list_to_filter[word]) > 20:
                            len(post_list_to_filter[word])
                            del post_list_to_filter[word]
                    except:
                        pass
                #join the filtered list back together
                comment=' '.join(post_list_to_filter)
                #set is to make sure evey user and stock is unique
                reicpients = set(reicpients)
                stocks = set(stocks)
                attached_url = attached_url

            if group != None and comment != None:

                pausetime=datetime.now()-timedelta(minutes=1)
                if Post.objects.filter(author=user, group=current_group, content=comment,published__gte=pausetime).exists():
                    data = {
                    'created_post_false': "false",
                    }
                    return JsonResponse(data)
                    #send message you already said this
                    url = reverse('core:group', kwargs={'slug': self.kwargs['slug'],})
                    return HttpResponseRedirect(url)
                else:
                    created_post = Post.objects.create(author=user, group=current_group, description=comment, content=comment)
                    created_post.save()
                    #add recipents to post if any
                    reicpients_name_url=[]
                    notification_user_list=[]
                    if reicpients != None:
                        for user in reicpients:
                            if User_Profile.objects.filter(user__username__iexact=user).exists():
                                recipient = User_Profile.objects.filter(user__username__iexact=user)[0]
                                created_post.recipients.add(recipient)
                                #put user name along with their url into list
                                reicpients_name_url.append(recipient.user.username)
                                notification_user_list.append(recipient.user.username)
                                reicpients_name_url.append('#')
                        #print(created_post.recipients.all())
                    #add stocks to post if any
                    stock_name_url=[]
                    if stocks != None:
                        for stock in stocks:
                            if Stocks.objects.filter(ticker__iexact=stock).exists():
                                stock_to_add = Stocks.objects.filter(ticker__iexact=stock)[0]
                                created_post.stocks.add(stock_to_add)
                                stock_name_url.append(stock_to_add.ticker)
                                stock_name_url.append(stock_to_add.get_absolute_url())
                    #add photo to post if any
                    photo = file
                    url_of_photo_id = []
                    if photo != None:
                        num_photo = len(photo)
                        for pic in range(num_photo):
                            save_path = os.path.join(settings.MEDIA_ROOT, 'post_img', photo[pic].name)
                            path = default_storage.save(save_path, photo[pic])
                            rotate_image(path)
                            document = PostPicture.objects.create(post_picture=path, post=created_post)
                            url_of_photo_id.append(document.post_picture.url)
                            url_of_photo_id.append(document.pk)


                    if attached_url:
                        for link in attached_url:
                            web_url =WebsiteUrl.objects.create(url=link)
                            PostUrl.objects.create(post=created_post,url=web_url)


                    # packaging the post to send to channels in json format
                    post_id = created_post.pk
                    url_to_detail_view_of_post = created_post.get_absolute_url()

                    user = User_Profile.objects.filter(user=self.request.user)[0]
                    if bool(user.profile_pic) != False:

                        user_profile_pic_url_post =  user.profile_pic.url
                    else:
                        user_profile_pic_url_post = 'false'

                    user_name_post = user.user.username

                    if created_post.post_comment.all():
                         comments_on_post = 'true'
                    else:
                        comments_on_post = 'fasle'

                    #time_published_post = created_post.published
                    now = datetime.now()
                    time_post =now.strftime("%a, %I:%M:%S %p")
                    time_published_post = time_post
                    if created_post.stocks.all():
                        stock_list_post = stock_name_url
                    else:
                        stock_list_post = 'false'

                    if created_post.title != None:
                        title_of_post = created_post.title
                    else:
                        title_of_post = 'false'

                    content_post = created_post.description

                    if created_post.postpicture_set.all():
                        url_of_photo_id_post = url_of_photo_id
                    else:
                        url_of_photo_id_post = 'false'

                    if created_post.recipients.all():
                        reicpients_name_url_post = reicpients_name_url
                    else:
                        reicpients_name_url_post = 'false'

                    # if attached url is empty assign the null
                    if attached_url:
                        attached_url = attached_url
                    else:
                        attached_url.append('null')

                    view_group_post = {
                        "post_id" : post_id,
                        "url_to_detail_view_of_post":url_to_detail_view_of_post,
                        "user_profile_pic_url_post":user_profile_pic_url_post,
                        "user_name_post": user_name_post,
                        "comments_on_post": comments_on_post,
                        "time_published_post": time_published_post,
                        "stock_list_post": stock_list_post,
                        "title_of_post": title_of_post,
                        "content_post": content_post,
                        "url_of_photo_id_post":url_of_photo_id_post,
                        "reicpients_name_url_post": reicpients_name_url_post,
                        "alert": 'false',
                        "attached_url":attached_url,
                    }

                    view_group_post = json.dumps(view_group_post)


                    #sending data to channels
                    channel_layer = get_channel_layer()

                    async_to_sync(channel_layer.group_send)(current_group.slug, {"type": "chat.message",
                    "view_group_post": view_group_post,})

                    id = created_post.pk
                    add_on = str(id)
                    # https://stackoverflow.com/questions/11531715/django-go-to-id-tag-inside-html
                    # http://www.learningaboutelectronics.com/Articles/How-to-create-a-session-variable-in-Django.php
                    # request.session['username']= 'David'
                    #https://stackoverflow.com/questions/11531715/django-go-to-id-tag-inside-html
                    print("post created")
                    #add integer to comment feild
                    if len(notification_user_list) == 0:
                        notification_user_list= "null"

                    data = {
                    'created_post_false': "true",
                     'list_of_recipients': notification_user_list,
                     'post_id': created_post.pk,
                    }
                    return JsonResponse(data)
                    # url = reverse('core:group', kwargs={'slug': self.kwargs['slug'],})
                    # object = "grouppost"#add_on
                    # id = "#"+object
                    # url = url + id +add_on
                    # print(HttpResponseRedirect(url))
                    # return HttpResponseRedirect(url)

        #//////////////Repost Creation//////////////////////////////////////////////////

        repost = self.request.POST.getlist('repost') if 'repost' in self.request.POST else None
        if repost != None:
            print(repost)
            try:
                postid=repost[0]
                #print(commentid)
            except IndexError:
                postid=None

            try:
                response=repost[1]
                #print(response)
            except IndexError:
                response=None

            #///Section filters Repost
            stocks = None
            reicpients = None
            if response != None:
                #variables for recipients and stocks
                reicpients = []
                stocks = []
                # filter post for users
                #split the string on space
                post_list_to_filter = response.split()
                # check to see if post_list_is still a string
                if isinstance(post_list_to_filter, str):
                    item = post_list_to_filter
                    post_list_to_filter = []
                    post_list_to_filter.append(item)
                # get the length of the post filter variable
                list_lenght= len(post_list_to_filter)
                #print(list_lenght)
                #loop through the post filter variable check for recipents, stocks, and if long word
                for word in range(list_lenght):
                    # the for loop goes through the loop once to much so try statment is here
                    try:
                        #filter Message for stocks
                        if "$" in post_list_to_filter[word]:
                            stock = post_list_to_filter[word].split('$')
                            print(stock)
                            stocks.append(stock[1])
                            # print(stocks)
                        # filtering for user
                        if "@" in post_list_to_filter[word]:
                            reicpient = post_list_to_filter[word].split('@')
                            # print(reicpient)
                            reicpients.append(reicpient[1])
                            # print(reicpients)
                        # deleting word so that word does not break the format of page
                        # if user post embeded links this could change
                        if len(post_list_to_filter[word]) > 20:
                            len(post_list_to_filter[word])
                            print(post_list_to_filter[word])
                            del post_list_to_filter[word]
                    except:
                        pass
                #join the filtered list back together
                response=' '.join(post_list_to_filter)
                #set is to make sure evey user and stock is unique
                reicpients = set(reicpients)
                stocks = set(stocks)


            if postid != None and response != None:
                current_post = get_object_or_404(Post, pk=postid)
                repost_count = current_post.repost_count

                if Post.objects.filter(author=user,description=response,repost=current_post, group=current_group).exists():
                    messages.info(self.request, "You have already shared this post")
                    url = reverse('core:group', kwargs={'slug': self.kwargs['slug'],})
                    object = "grouppos1"#add_on
                    id = "#"+object
                    url = url + id + add_on
                    print(HttpResponseRedirect(url))
                    return HttpResponseRedirect(url)
                    #send message you already said this
                else:
                    repost = Post.objects.create(author=user,description=response,repost=current_post, group=current_group)
                    current_post.repost_count = repost_count+1
                    current_post.save()
                    if reicpients != None:
                        for user in reicpients:
                            if User_Profile.objects.filter(user__username__iexact=user).exists():
                                recipient = User_Profile.objects.filter(user__username__iexact=user)[0]
                                repost.recipients.add(recipient)
                        print(repost.recipients.all())
                    if stocks != None:
                        for stock in stocks:
                            if Stocks.objects.filter(ticker__iexact=stock).exists():
                                stock_to_add = Stocks.objects.filter(ticker__iexact=stock)[0]
                                repost.stocks.add(stock_to_add)
                    id = repost.pk
                    add_on = str(id)
                    # https://stackoverflow.com/questions/11531715/django-go-to-id-tag-inside-html

                    # http://www.learningaboutelectronics.com/Articles/How-to-create-a-session-variable-in-Django.php
                    #request.session['username']= 'David'
                    #https://stackoverflow.com/questions/11531715/django-go-to-id-tag-inside-html
                    # print("post created")
                    #add integer to comment feild

                    url = reverse('core:group', kwargs={'slug': self.kwargs['slug'],})
                    object = "grouppos1"#add_on
                    id = "#"+object
                    url = url + id + add_on
                    print(HttpResponseRedirect(url))
                    return HttpResponseRedirect(url)
                #let user know that their post was reposted
        #//////////////End Repost //////////////////////////////////////////////////

        #return redirect("core:group",slug=self.kwargs['slug'])
        #return render(request, self.template_name slug=self.kwargs['slug'], context)

        #//////////////Creating reply //////////////////////////////////////////////////
        file = self.request.FILES.getlist('reply_img') if 'reply_img' in request.FILES else None

        reply = self.request.POST.getlist('reply') if 'reply' in self.request.POST else None
        if reply != None:
            print(reply)

            try:
                reicpients=reply[0]
                #///////////filtering recipients
                reicpients = reicpients.replace(" ","")
                reicpients = reicpients.split('@')
                del reicpients[0]
                reicpients = set(reicpients)

            except IndexError:
                reicpients=None

            try:
                commentid=reply[1]
                print("reply id ",commentid)
                #print(commentid)
            except IndexError:
                commentid=None

            try:
                postid=reply[2]
                print("post id ",postid)
                #print(postid)
            except IndexError:
                postid=None

            try:
                response=reply[3]
                #print(response)
            except IndexError:
                response=None

            #///Section filters Reply
            stocks = None
            reicpients = None
            if response != None:
                #variables for recipients and stocks
                reicpients = []
                stocks = []
                # filter post for users
                #split the string on space
                post_list_to_filter = response.split()
                # check to see if post_list_is still a string
                if isinstance(post_list_to_filter, str):
                    item = post_list_to_filter
                    post_list_to_filter = []
                    post_list_to_filter.append(item)
                # get the length of the post filter variable
                list_lenght= len(post_list_to_filter)
                #print(list_lenght)
                #loop through the post filter variable check for recipents, stocks, and if long word
                for word in range(list_lenght):
                    # the for loop goes through the loop once to much so try statment is here
                    try:
                        #filter Message for stocks
                        if "$" in post_list_to_filter[word]:
                            stock = post_list_to_filter[word].split('$')
                            print(stock)
                            stocks.append(stock[1])
                            # print(stocks)
                        # filtering for user
                        if "@" in post_list_to_filter[word]:
                            reicpient = post_list_to_filter[word].split('@')
                            # print(reicpient)
                            reicpients.append(reicpient[1])
                            # print(reicpients)
                        # deleting word so that word does not break the format of page
                        # if user post embeded links this could change
                        if len(post_list_to_filter[word]) > 20:
                            len(post_list_to_filter[word])
                            print(post_list_to_filter[word])
                            del post_list_to_filter[word]
                    except:
                        pass
                #join the filtered list back together with space inbetween list elements
                response=' '.join(post_list_to_filter)
                #set is to make sure evey user and stock is unique
                reicpients = set(reicpients)
                stocks = set(stocks)

            if commentid != None and postid != None and response != None:
                current_post = get_object_or_404(Post, pk=postid)
                current_comment = get_object_or_404(Comments, pk=commentid)
                count = current_post.comment_count
                pausetime=datetime.now()-timedelta(minutes=1)
                if CommentReply.objects.filter(author=user,comment=current_comment,contents__exact=response,published__gte=pausetime).exists():
                    data = {
                    'created_post_false': "false",
                    }

                    return JsonResponse(data)
                    #send message you already said this
                else:
                    Reply = CommentReply.objects.create(author=user,contents=response,comment=current_comment)

                    reicpients_name_url=[]
                    notification_user_list=[]
                    if reicpients != None:
                        for user in reicpients:
                            if User_Profile.objects.filter(user__username__iexact=user).exists():
                                recipient = User_Profile.objects.filter(user__username__iexact=user)[0]
                                Reply.recipients.add(recipient)
                                #put user name along with their url into list
                                reicpients_name_url.append(recipient.user.username)
                                notification_user_list.append(recipient.user.username)
                                reicpients_name_url.append('#')
                            else:
                                print('user does not exist')
                    #add stocks to post if any
                    stock_name_url=[]
                    if stocks != None:
                        for stock in stocks:
                            if Stocks.objects.filter(ticker__iexact=stock).exists():
                                stock_to_add = Stocks.objects.filter(ticker__iexact=stock)[0]
                                Reply.stocks.add(stock_to_add)
                                stock_name_url.append(stock_to_add.ticker)
                                stock_name_url.append(stock_to_add.get_absolute_url())
                    photo = file
                    url_of_photo_id = []
                    if photo != None:
                        num_photo = len(photo)
                        for pic in range(num_photo):
                            save_path = os.path.join(settings.MEDIA_ROOT, 'commentreply_img', photo[pic].name)
                            path = default_storage.save(save_path, photo[pic])
                            rotate_image(path)
                            document = CommentReplyPicture.objects.create(commentreply_picture=path, commentreply=Reply)
                            url_of_photo_id.append(document.commentreply_picture.url)
                            url_of_photo_id.append(document.pk)
                    current_post.comment_count = count+1
                    current_post.save()


                    # packaging the Comment to send to channels in json format
                    #kkeping post_id for simplicity
                    post_id = Reply.pk
                    #know which post to put comment under
                    current_post_id = current_post.pk

                    current_comment_id = current_comment.pk

                    user = User_Profile.objects.filter(user=self.request.user)[0]

                    if bool(user.profile_pic) != False:
                        user_profile_pic_url_post =  user.profile_pic.url
                    else:
                        user_profile_pic_url_post = 'false'

                    user_name_post = user.user.username

                    #time_published_post = created_post.published
                    now = datetime.now()
                    time_post =now.strftime("%a, %I:%M:%S %p")
                    time_published_post = time_post

                    if Reply.stocks.all():
                        stock_list_post = stock_name_url
                    else:
                        stock_list_post = 'false'

                    content_post = Reply.contents

                    if Reply.commentreplypicture_set.all():
                        url_of_photo_id_post = url_of_photo_id
                    else:
                        url_of_photo_id_post = 'false'

                    if Reply.recipients.all():
                        reicpients_name_url_post = reicpients_name_url
                    else:
                        reicpients_name_url_post = 'false'

                    view_group_reply = {
                    #reply id
                    "post_id" : post_id,
                    #Post id
                    "current_post_id" : current_post_id,
                    #comment_id
                    "current_comment_id": current_comment_id,
                    "user_profile_pic_url_post":user_profile_pic_url_post,
                    "user_name_post": user_name_post,
                    # "comments_on_post": comments_on_post,
                    "time_published_post": time_published_post,
                    "stock_list_post": stock_list_post,
                    # "title_of_post": title_of_post,
                    "content_post": content_post,
                    "url_of_photo_id_post":url_of_photo_id_post,
                    "reicpients_name_url_post": reicpients_name_url_post
                    }

                    view_group_reply = json.dumps(view_group_reply)


                    #sending data to channels
                    channel_layer = get_channel_layer()

                    async_to_sync(channel_layer.group_send)(current_group.slug, {"type": "chat.message",
                    "view_group_reply": view_group_reply,})



                    id = current_post.pk
                    add_on = str(id)
                    # https://stackoverflow.com/questions/11531715/django-go-to-id-tag-inside-html

                    # http://www.learningaboutelectronics.com/Articles/How-to-create-a-session-variable-in-Django.php
                    #request.session['username']= 'David'
                    #https://stackoverflow.com/questions/11531715/django-go-to-id-tag-inside-html
                    # print("post created")
                    #add integer to comment feild
                    if len(notification_user_list) == 0:
                        notification_user_list= "null"

                    data = {
                     'list_of_recipients': notification_user_list,
                     # listed as post id but it is comment id
                     'post_id': Reply.pk,
                     'created_post_false': "true",
                    }
                    return JsonResponse(data)
                # url = reverse('core:group', kwargs={'slug': self.kwargs['slug'],})
                # object = "grouppost1"#add_on
                # id = "#"+object
                # url = url + id + add_on
                # # print(HttpResponseRedirect(url))
                # return HttpResponseRedirect(url)
                #print("post created")
                #add integer to comment feild
        #//////////////Replying to a Comment or reply //////////////////////////////////////////////////

        #////////////////commenting on a Post//////////////////////////////////
        file = self.request.FILES.getlist('comment_img') if 'comment_img' in request.FILES else None
        comment_request = self.request.POST.getlist('comment') if 'comment' in self.request.POST else None
        if comment_request != None:
            #print(comment_request)
            try:
                #I hid the html element so this code is redundant
                reicpients=comment_request[0]
                #///////////filtering recipients
                reicpients = reicpients.replace(" ","")
                reicpients = reicpients.split('@')
                del reicpients[0]
                reicpients = set(reicpients)

            except IndexError:
                reicpients=None

            try:
                post=comment_request[1]
                print(post)
            except IndexError:
                post=None
            try:
                comment=comment_request[2]
                print(comment)
            except IndexError:
                comment=None

            #///Section filters Comment
            stocks = None
            reicpients = None
            if comment != None:
                #variables for recipients and stocks
                reicpients = []
                stocks = []
                # filter post for users
                #split the string on space
                post_list_to_filter = comment.split()
                # check to see if post_list_is still a string
                if isinstance(post_list_to_filter, str):
                    item = post_list_to_filter
                    post_list_to_filter = []
                    post_list_to_filter.append(item)
                # get the length of the post filter variable
                list_lenght= len(post_list_to_filter)
                #print(list_lenght)
                #loop through the post filter variable check for recipents, stocks, and if long word
                for word in range(list_lenght):
                    # the for loop goes through the loop once to much so try statment is here
                    try:
                        #filter Message for stocks
                        if "$" in post_list_to_filter[word]:
                            stock = post_list_to_filter[word].split('$')
                            print(stock)
                            stocks.append(stock[1])
                            # print(stocks)
                        # filtering for user
                        if "@" in post_list_to_filter[word]:
                            reicpient = post_list_to_filter[word].split('@')
                            # print(reicpient)
                            reicpients.append(reicpient[1])
                            # print(reicpients)
                        # deleting word so that word does not break the format of page
                        # if user post embeded links this could change
                        if len(post_list_to_filter[word]) > 20:
                            len(post_list_to_filter[word])
                            print(post_list_to_filter[word])
                            del post_list_to_filter[word]
                    except:
                        pass
                #join the filtered list back together with space inbetween list elements
                comment=' '.join(post_list_to_filter)
                #set is to make sure evey user and stock is unique
                reicpients = set(reicpients)
                stocks = set(stocks)


            if post != None and comment != None:
                current_post = get_object_or_404(Post, pk=post)
                count = current_post.comment_count
                pausetime=datetime.now()-timedelta(minutes=1)
                if Comments.objects.filter(author=user,post=current_post,contents__exact=comment,published__gte=pausetime).exists():
                    data = {
                    'created_post_false': "false",
                    }
                    return JsonResponse(data)
                else:
                    Reply = Comments.objects.create(author=user,contents=comment,post=current_post)

                    reicpients_name_url=[]
                    notification_user_list=[]
                    if reicpients != None:
                        for user in reicpients:
                            if User_Profile.objects.filter(user__username__iexact=user).exists():
                                recipient = User_Profile.objects.filter(user__username__iexact=user)[0]
                                Reply.recipients.add(recipient)
                                #put user name along with their url into list
                                reicpients_name_url.append(recipient.user.username)
                                notification_user_list.append(recipient.user.username)
                                reicpients_name_url.append('#')
                            else:
                                print('user does not exist')
                    #add stocks to post if any
                    stock_name_url=[]
                    if stocks != None:
                        for stock in stocks:
                            if Stocks.objects.filter(ticker__iexact=stock).exists():
                                stock_to_add = Stocks.objects.filter(ticker__iexact=stock)[0]
                                Reply.stocks.add(stock_to_add)
                                stock_name_url.append(stock_to_add.ticker)
                                stock_name_url.append(stock_to_add.get_absolute_url())
                    #add photo to post if any
                    photo = file
                    url_of_photo_id = []
                    if photo != None:
                        num_photo = len(photo)
                        for pic in range(num_photo):
                            save_path = os.path.join(settings.MEDIA_ROOT, 'comments_img', photo[pic].name)
                            path = default_storage.save(save_path, photo[pic])
                            rotate_image(path)
                            document = CommentsPicture.objects.create(comments_picture=path, comments=Reply)
                            url_of_photo_id.append(document.comments_picture.url)
                            url_of_photo_id.append(document.pk)

                    # packaging the Comment to send to channels in json format
                    #kkeping post_id for simplicity
                    post_id = Reply.pk
                    #know which post to put comment under
                    current_post_id = current_post.pk

                    user = User_Profile.objects.filter(user=self.request.user)[0]

                    if bool(user.profile_pic) != False:
                        user_profile_pic_url_post =  user.profile_pic.url
                    else:
                        user_profile_pic_url_post = 'false'

                    user_name_post = user.user.username

                    #time_published_post = created_post.published
                    now = datetime.now()
                    time_post =now.strftime("%a, %I:%M:%S %p")
                    time_published_post = time_post

                    if Reply.stocks.all():
                        stock_list_post = stock_name_url
                    else:
                        stock_list_post = 'false'

                    content_post = Reply.contents

                    if Reply.commentspicture_set.all():
                        url_of_photo_id_post = url_of_photo_id
                    else:
                        url_of_photo_id_post = 'false'

                    if Reply.recipients.all():
                        reicpients_name_url_post = reicpients_name_url
                    else:
                        reicpients_name_url_post = 'false'

                    view_group_comment = {
                        #Comment id
                        "post_id" : post_id,
                        #Post id
                        "current_post_id" : current_post_id,
                        "user_profile_pic_url_post":user_profile_pic_url_post,
                        "user_name_post": user_name_post,
                        # "comments_on_post": comments_on_post,
                        "time_published_post": time_published_post,
                        "stock_list_post": stock_list_post,
                        # "title_of_post": title_of_post,
                        "content_post": content_post,
                        "url_of_photo_id_post":url_of_photo_id_post,
                        "reicpients_name_url_post": reicpients_name_url_post
                    }

                    view_group_comment = json.dumps(view_group_comment)


                    #sending data to channels
                    channel_layer = get_channel_layer()

                    async_to_sync(channel_layer.group_send)(current_group.slug, {"type": "chat.message",
                    "view_group_comment": view_group_comment,})



                    current_post.comment_count = count+1
                    current_post.save()
                    # print("post created")
                    id = current_post.pk
                    add_on = str(id)
                    # https://stackoverflow.com/questions/11531715/django-go-to-id-tag-inside-html

                    # http://www.learningaboutelectronics.com/Articles/How-to-create-a-session-variable-in-Django.php
                    #request.session['username']= 'David'
                    #https://stackoverflow.com/questions/11531715/django-go-to-id-tag-inside-html
                    print("post created")
                    #add integer to comment feild
                    if len(notification_user_list) == 0:
                        notification_user_list= "null"

                    data = {
                     'list_of_recipients': notification_user_list,
                     # listed as post id but it is comment id
                     'post_id': Reply.pk,
                     # incase user has just said the message
                     'created_post_false': "true",
                    }
                    return JsonResponse(data)
                # url = reverse('core:group', kwargs={'slug': self.kwargs['slug'],})
                # object = "grouppost1"#add_on
                # id = "#"+object
                # url = url + id + add_on
                # # print(HttpResponseRedirect(url))
                # return HttpResponseRedirect(url)
                #add integer to comment feild
class Membership_Choice(generic.TemplateView):
    template_name = 'membership_choice.html'

    def get_context_data(self, *args, **kwargs):


        # Just include the form
        context = super(Membership_Choice, self).get_context_data(*args, **kwargs)
        user = User_Profile.objects.filter(user=self.request.user)[0]
        #check if user has stripe customer id
        if user.stripe_customer_id is None or user.stripe_customer_id == '':
            new_customer_id = stripe.Customer.create(email= user.user.email)
            user.stripe_customer_id = new_customer_id['id']
            DividendWealthSubscription.objects.create(user_profile=user,stripe_subscription_id="free")
            new_membership= DividendWealthMembership.objects.filter(membership='f')[0]
            user.dividend_wealth_membership = new_membership
            user.save()

        # Check if user has default card
        default_card = stripe.Customer.retrieve(user.stripe_customer_id)
        default_card = default_card["default_source"]
        context["default_card_id"] =default_card

        context["has_default_card"]= 'true'
        if default_card is None:
            context["has_default_card"]= 'false'
        else:
            default_card_info=stripe.Customer.retrieve_source(
              user.stripe_customer_id,
             default_card,
            )
            context["card_name"]= default_card_info["name"]
            context["card_last4"]= default_card_info["last4"]
            context["card_month"]= default_card_info["exp_month"]
            context["card_exyear"]= default_card_info["exp_year"]
            context["card_brand"]= default_card_info["brand"]

        membership_accounts = DividendWealthMembership.objects.all()
        context["membership_accounts"]= membership_accounts
        context['current_user'] = user
        context['stripe_pluishable_key'] = settings.STRIPE_PUBLIC_KEY

        return context

    def post(self,request, **kwargs):
        # https://stackoverflow.com/questions/33239308/how-to-get-exception-message-in-python-properly
        stripeToken = self.request.POST.getlist('stripeToken') if 'stripeToken' in request.POST else None
        name_on_card = self.request.POST.getlist('name_on_card') if 'name_on_card' in request.POST else None
        use_default_card = self.request.POST.getlist('use_default_card') if 'use_default_card' in request.POST else None

        if stripeToken != None:

            selected_membership = self.request.POST.getlist('selected_membership') if 'selected_membership' in request.POST else None
            #create stripe customer id if customer does not already have one
            user = User_Profile.objects.filter(user=self.request.user)[0]
            #check if user has strip customer id
            if user.stripe_customer_id is None or user.stripe_customer_id == '':
                new_customer_id = stripe.Customer.create(email= user.user.email)
                user.stripe_customer_id = new_customer_id['id']
                #Create new subscription
                DividendWealthSubscription.objects.create(user_profile=user,stripe_subscription_id="free")
                new_membership= DividendWealthMembership.objects.filter(membership='f')[0]
                user.dividend_wealth_membership = new_membership
                user.save()
            else:
                print(" has stripe customer id")
            # filter membership model for the membership chosen
            if DividendWealthMembership.objects.filter(membership=selected_membership[0]).exists():
                new_membership= DividendWealthMembership.objects.filter(membership=selected_membership[0])[0]

                try:
                    # Process stripe payment
                    #tokenizedPayment was received from stripe and injected into the form
                    tokenizedPayment= stripeToken[0]
                    # # Create payment method
                    # payment =stripe.PaymentMethod.create(
                    #   type="card",
                    #   card={ "token": tokenizedPayment},
                    # )
                    # #attach payment method to the user
                    # stripe.PaymentMethod.attach(
                    #   payment,
                    #   customer = user.stripe_customer_id
                    # )

                    #create card
                    card=stripe.Customer.create_source(
                      user.stripe_customer_id,
                      source=tokenizedPayment,
                    )
                    #add name to card
                    stripe.Customer.modify_source(
                      user.stripe_customer_id,
                      card["id"],
                      name=name_on_card[0],
                    )
                    #Create a stripe subcripiton if it is not a lifetime membership
                    if new_membership.membership != 'l':

                        #Create stripe subscription
                        created_stripe_subscription_id=stripe.Subscription.create(
                          customer=user.stripe_customer_id,
                          items=[{"plan": new_membership.stripe_plan_id}],
                          # default_payment_method = payment,
                          default_source = card["id"],
                        )

                        #deactivate current subscription
                        active_subsription= DividendWealthSubscription.objects.filter(user_profile=user,active=True)[0]
                        if active_subsription.stripe_subscription_id == 'lifetime' or active_subsription.stripe_subscription_id == 'free':
                            pass
                        else:
                            stripe.Subscription.delete(active_subsription.stripe_subscription_id)


                        #deactivate current subscription on our side
                        active_subsription.active = False
                        active_subsription.save()

                        #Create new subscription
                        DividendWealthSubscription.objects.create(user_profile=user,stripe_subscription_id=created_stripe_subscription_id['id'])

                        #note: I change the user membership later in the sequence-
                        # user.dividend_wealth_membership = new_membership
                        # user.save()
                        #Check to make sure subscription fee was collected
                        # if not cancel subscription
                        subscription_check=stripe.Subscription.retrieve(created_stripe_subscription_id["id"])
                        if subscription_check["status"] != "active":
                            #deactivate current subscription
                            active_subsription= DividendWealthSubscription.objects.filter(user_profile=user,active=True)[0]
                            if active_subsription.stripe_subscription_id == 'lifetime' or active_subsription.stripe_subscription_id == 'free':
                                pass
                            else:
                                stripe.Subscription.delete(active_subsription.stripe_subscription_id)

                            #deactivate current subscription on our side
                            active_subsription.active = False
                            active_subsription.save()

                            #Create new subscription
                            DividendWealthSubscription.objects.create(user_profile=user,stripe_subscription_id="free")
                            new_membership= DividendWealthMembership.objects.filter(membership='f')[0]
                            user.dividend_wealth_membership = new_membership

                            user.save()
                            messages.info(self.request, "Your card has been denied")
                            url = reverse('core:membership_choice')
                            return HttpResponseRedirect(url)
                        # Change users membership to the new memebership
                        user.dividend_wealth_membership = new_membership
                        user.save()
                        # check if user has dividend account
                        # putblish all unpublished groups
                        if DividendWealthConnectedAccount.objects.filter(user_profile=user).exists():
                            if user.dividend_wealth_membership.membership != 'f':
                                if GenGroup.objects.filter(published=False,creator=user).exists():
                                    groups_to_publish=GenGroup.objects.filter(published=False,creator=user)
                                    for group in groups_to_publish:
                                        group.published = True
                                        group.save()

                    else:

                        #deactivate current subscription
                        active_subsription= DividendWealthSubscription.objects.filter(user_profile=user,active=True)[0]
                        if active_subsription.stripe_subscription_id == 'lifetime' or active_subsription.stripe_subscription_id == 'free':
                            pass
                        else:
                            stripe.Subscription.delete(active_subsription.stripe_subscription_id)


                        # #Create one time fee
                        # paymentIntent=stripe.PaymentIntent.create(
                        #   amount=40000,
                        #   currency="usd",
                        #   payment_method=payment,
                        #   customer=user.stripe_customer_id,
                        #
                        # )
                        # # Confirm fee
                        # stripe.PaymentIntent.confirm(
                        #   paymentIntent,
                        #   payment_method=payment,
                        # )

                        #Create one time fee
                        charge=stripe.Charge.create(
                          amount=40000,
                          currency="usd",
                          source= card["id"],
                          customer= user.stripe_customer_id,
                        )

                        #deactivate
                        active_subsription.active = False
                        active_subsription.save()
                        #Create new subscription
                        DividendWealthSubscription.objects.create(user_profile=user,stripe_subscription_id='lifetime')

                        charge_proof=stripe.Charge.retrieve(
                          charge["id"],
                        )
                        if charge_proof["paid"] == False:
                            #deactivate current subscription
                            active_subsription= DividendWealthSubscription.objects.filter(user_profile=user,active=True)[0]
                            if active_subsription.stripe_subscription_id == 'lifetime' or active_subsription.stripe_subscription_id == 'free':
                                pass
                            else:
                                stripe.Subscription.delete(active_subsription.stripe_subscription_id)

                            #deactivate current subscription on our side
                            active_subsription.active = False
                            active_subsription.save()

                            #Create new subscription
                            DividendWealthSubscription.objects.create(user_profile=user,stripe_subscription_id="free")
                            new_membership= DividendWealthMembership.objects.filter(membership='f')[0]
                            user.dividend_wealth_membership = new_membership
                            user.save()
                            messages.info(self.request, "Your card has been denied")
                            url = reverse('core:membership_choice')
                            return HttpResponseRedirect(url)

                        # Change users membership to the new memebership
                        user.dividend_wealth_membership = new_membership
                        user.save()
                        # check if user has dividend account
                        # putblish all unpublished groups
                        if DividendWealthConnectedAccount.objects.filter(user_profile=user).exists():
                            if user.dividend_wealth_membership.membership != 'f':
                                if GenGroup.objects.filter(published=False,creator=user).exists():
                                    groups_to_publish=GenGroup.objects.filter(published=False,creator=user)
                                    for group in groups_to_publish:
                                        group.published = True
                                        group.save()

                    # Change users membership to the new memebership
                    user.dividend_wealth_membership = new_membership
                    user.save()
                except Exception as e:
                    messages.info(self.request, "your card has been denied")
                    # Just print(e) is cleaner and more likely what you want,
                    # but if you insist on printing message specifically whenever possible...
                    if hasattr(e, 'message'):
                        print(e.message)
                    else:
                        print(e)
                    url = reverse('core:membership_choice')
                    return HttpResponseRedirect(url)
                #create a new subscription
                #Create new subscription
                #
        if use_default_card != None:
            # print("inhere")
            selected_membership_default = self.request.POST.getlist('selected_membership_default') if 'selected_membership_default' in request.POST else None
            #create stripe customer id if customer does not already have one
            user = User_Profile.objects.filter(user=self.request.user)[0]
            #check if user has strip customer id
            if user.stripe_customer_id is None or user.stripe_customer_id == '':
                new_customer_id = stripe.Customer.create(email= user.user.email)
                user.stripe_customer_id = new_customer_id['id']
                DividendWealthSubscription.objects.create(user_profile=user,stripe_subscription_id="free")
                new_membership= DividendWealthMembership.objects.filter(membership='f')[0]
                user.dividend_wealth_membership = new_membership
                user.save()
            else:
                pass
            # filter membership model for the membership chosen
            if DividendWealthMembership.objects.filter(membership=selected_membership_default[0]).exists():
                new_membership= DividendWealthMembership.objects.filter(membership=selected_membership_default[0])[0]

                try:
                    #Create a stripe subcripiton if it is not a lifetime membership
                    if new_membership.membership != 'l':

                        #Create stripe subscription
                        created_stripe_subscription_id=stripe.Subscription.create(
                          customer=user.stripe_customer_id,
                          items=[{"plan": new_membership.stripe_plan_id}],
                          # default_payment_method = payment,
                        )

                        #deactivate current subscription
                        active_subsription= DividendWealthSubscription.objects.filter(user_profile=user,active=True)[0]
                        if active_subsription.stripe_subscription_id == 'lifetime' or active_subsription.stripe_subscription_id == 'free':
                            pass
                        else:
                            stripe.Subscription.delete(active_subsription.stripe_subscription_id)


                        #deactivate current subscription on our side
                        active_subsription.active = False
                        active_subsription.save()

                        #Create new subscription
                        DividendWealthSubscription.objects.create(user_profile=user,stripe_subscription_id=created_stripe_subscription_id['id'])

                        #Check to make sure subscription fee was collected
                        subscription_check=stripe.Subscription.retrieve(created_stripe_subscription_id["id"])
                        if subscription_check["status"] != "active":
                            #deactivate current subscription
                            active_subsription= DividendWealthSubscription.objects.filter(user_profile=user,active=True)[0]
                            if active_subsription.stripe_subscription_id == 'lifetime' or active_subsription.stripe_subscription_id == 'free':
                                pass
                            else:
                                stripe.Subscription.delete(active_subsription.stripe_subscription_id)

                            #deactivate current subscription on our side
                            active_subsription.active = False
                            active_subsription.save()

                            #Create new subscription
                            DividendWealthSubscription.objects.create(user_profile=user,stripe_subscription_id="free")
                            new_membership= DividendWealthMembership.objects.filter(membership='f')[0]
                            user.dividend_wealth_membership = new_membership
                            user.save()
                            messages.info(self.request, "Your card has been denied")
                            url = reverse('core:membership_choice')
                            return HttpResponseRedirect(url)
                        # Change users membership to the new memebership
                        user.dividend_wealth_membership = new_membership
                        user.save()
                        # check if user has dividend account
                        # putblish all unpublished groups
                        if DividendWealthConnectedAccount.objects.filter(user_profile=user).exists():
                            if user.dividend_wealth_membership.membership != 'f':
                                if GenGroup.objects.filter(published=False,creator=user).exists():
                                    groups_to_publish=GenGroup.objects.filter(published=False,creator=user)
                                    for group in groups_to_publish:
                                        group.published = True
                                        group.save()

                    else:

                        #deactivate current subscription
                        active_subsription= DividendWealthSubscription.objects.filter(user_profile=user,active=True)[0]
                        if active_subsription.stripe_subscription_id == 'lifetime' or active_subsription.stripe_subscription_id == 'free':
                            #no stripe subscription plan for lifetime of free
                            pass
                        else:
                            stripe.Subscription.delete(active_subsription.stripe_subscription_id)

                        # get id of default card
                        default_card = stripe.Customer.retrieve(user.stripe_customer_id)

                        #Create one time fee
                        stripe.Charge.create(
                          amount=40000,
                          currency="usd",
                          source= default_card["default_source"],
                          customer= user.stripe_customer_id,
                        )

                        #deactivate
                        active_subsription.active = False
                        active_subsription.save()
                        #Create new subscription
                        DividendWealthSubscription.objects.create(user_profile=user,stripe_subscription_id='lifetime')

                        charge_proof=stripe.Charge.retrieve(
                          charge["id"],
                        )
                        if charge_proof["paid"] == False:
                            #deactivate current subscription
                            active_subsription= DividendWealthSubscription.objects.filter(user_profile=user,active=True)[0]
                            if active_subsription.stripe_subscription_id == 'lifetime' or active_subsription.stripe_subscription_id == 'free':
                                pass
                            else:
                                stripe.Subscription.delete(active_subsription.stripe_subscription_id)

                            #deactivate current subscription on our side
                            active_subsription.active = False
                            active_subsription.save()

                            #Create new subscription
                            DividendWealthSubscription.objects.create(user_profile=user,stripe_subscription_id="free")
                            new_membership= DividendWealthMembership.objects.filter(membership='f')[0]
                            user.dividend_wealth_membership = new_membership
                            user.save()
                            messages.info(self.request, "Your card has been denied")
                            url = reverse('core:membership_choice')
                            return HttpResponseRedirect(url)


                    # Change users membership to the new memebership
                    user.dividend_wealth_membership = new_membership
                    user.save()

                    # check if user has dividend account
                    # putblish all unpublished groups
                    if DividendWealthConnectedAccount.objects.filter(user_profile=user).exists():
                        if user.dividend_wealth_membership.membership != 'f':
                            if GenGroup.objects.filter(published=False,creator=user).exists():
                                groups_to_publish=GenGroup.objects.filter(published=False,creator=user)
                                for group in groups_to_publish:
                                    group.published = True
                                    group.save()

                except Exception as e:
                    messages.info(self.request, "your card has been denied")
                    # Just print(e) is cleaner and more likely what you want,
                    # but if you insist on printing message specifically whenever possible...
                    if hasattr(e, 'message'):
                        print(e.message)
                    else:
                        print(e)
                    url = reverse('core:membership_choice')
                    return HttpResponseRedirect(url)

        messages.info(self.request, "Thank you")
        url = reverse('core:membership_choice')
        return HttpResponseRedirect(url)

class DividendWealthAccount(generic.TemplateView):
    template_name = 'dividend_wealth_user_account.html'

    def get(self, *args, **kwargs):

        kw_username=self.kwargs['username']
        print(self.request)
        user = User_Profile.objects.filter(user=self.request.user)[0]
        if user.user.username != kw_username:
            return HttpResponseRedirect(reverse('core:user_dashboard')) #home page
        # if stripe code is not available then go to regular page
        return super(DividendWealthAccount, self).get(self.request, *args, **kwargs)


    def get_context_data(self, *args, **kwargs):
        # Just include the form
        context = super(DividendWealthAccount, self).get_context_data(*args, **kwargs)
        #Get the keword argument and compare it to the current userermane
        print(self.request)
        #check if user has stripe customer id

        kw_username=self.kwargs['username']

        user = User_Profile.objects.filter(user=self.request.user)[0]
        # create stripe id
        if user.stripe_customer_id is None or user.stripe_customer_id == '':
            new_customer_id = stripe.Customer.create(email= user.user.email)
            user.stripe_customer_id = new_customer_id['id']
            DividendWealthSubscription.objects.create(user_profile=user,stripe_subscription_id="free")
            new_membership= DividendWealthMembership.objects.filter(membership='f')[0]
            user.dividend_wealth_membership = new_membership
            user.save()

        if 'stripe_auth' in self.request.session:
            try:
                response = stripe.OAuth.token(
                  grant_type='authorization_code',
                  code=self.request.session['stripe_auth'],
                )
                connected_id = response["stripe_user_id"]
                obj, created = DividendWealthConnectedAccount.objects.get_or_create(user_profile=user, stripe_connected_account_id=connected_id)

                # publish user groups if member is not a freemium
                if user.dividend_wealth_membership.membership != 'f':
                    if GenGroup.objects.filter(published=False,creator=user).exists():
                        groups_to_publish=GenGroup.objects.filter(published=False,creator=user)
                        for group in groups_to_publish:
                            group.published = True
                            group.save()

            except Exception as e:
                messages.info(self.request, "Something went wrong please try again")
                # Just print(e) is cleaner and more likely what you want,
                # but if you insist on printing message specifically whenever possible...
                if hasattr(e, 'message'):
                    print(e.message)
                else:
                    print(e)

            del self.request.session['stripe_auth']
        # checking if user has connected account
        connected_acount = "false"
        if DividendWealthConnectedAccount.objects.filter(user_profile=user).exists():
            connected_account=DividendWealthConnectedAccount.objects.filter(user_profile=user)[0]
            if connected_account.stripe_connected_account_id is None or connected_account.stripe_connected_account_id == '':
                pass
            else:
                connected_acount = "true"
                connected_login=stripe.Account.create_login_link(connected_account.stripe_connected_account_id)
                context["connected_login_url"]= connected_login["url"]

        context["connected_acount"] = connected_acount

        #get the users currnet membership and display it on account
        current_user_membership=user.dividend_wealth_membership.get_membership_display()
        context["current_user_membership"]= current_user_membership

        #get the list of credit cards if user has them
        # https://docs.djangoproject.com/en/dev/ref/templates/builtins/#for

        card_list= stripe.Customer.list_sources(
          user.stripe_customer_id,
        )
        cards= card_list["data"]
        default_card = stripe.Customer.retrieve(user.stripe_customer_id)

        # get id of default card
        default_card = default_card["default_source"]
        context["default_card_id"] =default_card

        # go through list of user cards and check if it is the default
        for card in card_list["data"]:
            if card["id"] == default_card:
                card["default"] = "true"
            else:
                card["default"] = "false"
        # print(cards)

        context['user_cards'] =cards


        # return fee information of users current membership
        if DividendWealthSubscription.objects.filter(user_profile=user,active=True).exists():
            sub_model = DividendWealthSubscription.objects.filter(user_profile=user,active=True)[0]
            current_plan=sub_model.stripe_subscription_id
            if current_plan == 'free' or current_plan == 'lifetime' :
                context['hide_cancel_subscription'] = 'true'
                context['sub_model'] = sub_model
                pass
            else:
                context['hide_cancel_subscription'] = 'false'
                context['sub_model'] = sub_model
                context["paidaccount"] = True
                #hit stipe for plan details
                current_plan = stripe.Subscription.retrieve(current_plan)
                #start date
                context["current_period_start"] = datetime.fromtimestamp(current_plan["current_period_start"])
                #renew date
                context["current_period_end"]= datetime.fromtimestamp(current_plan["current_period_end"])
                #amount user has to pay
                amount="{:.2f}".format(current_plan["plan"]["amount"] / 100)
                context["ammount"]= amount

            context["current_user_username"] =kw_username

        # get the list of groups user is subscribed to
        context["paid_subscriptions"] = "false"
        if GroupSubscription.objects.filter(group_member__userprofile=user,subscription=True).exists():
            context["paid_subscriptions"] = "true"
            context["group_user_suscribed"]=GroupSubscription.objects.filter(group_member__userprofile=user,subscription=True)

        # get users connected Payments
        context["user_has_payments"]= "false"
        if DividendWealthConnectedAccount.objects.filter(user_profile=user).exists():
            context["connected_payments"]=DividendWealthConnectedAccount.objects.filter(user_profile=user)[0].date_created
            first_name = user.first_name
            last_name = user.last_name
            try:
                full_name = first_name + ' '+ last_name
            except:
                full_name = 'None'
            context["full_name"]= full_name
            # get record of payments
            if GroupPayment.objects.filter(person_receiving=user).exists():
                context["user_has_payments"]= "true"
                context["user_has_payments_list"]= GroupPayment.objects.filter(person_receiving=user).order_by('-charge_date')
                payments_last_week = GroupPayment.objects.filter(charge_date__gte=datetime.now()-timedelta(days=7))
                amount = 0
                num = 0
                for payment in payments_last_week:
                    num += 1
                    amount += payment.price
                context["payment_last_week"] = amount
                context["payment_num_last_week"] = num
                value = GroupPayment.objects.filter(person_receiving=user).aggregate(Sum('price')).get('price__sum', 0.00)
                context["payment_all_time"]= value
                context["payment_num_all_time"]= GroupPayment.objects.filter(person_receiving=user).count()

        membership_accounts = DividendWealthMembership.objects.all()
        context["membership_accounts"]= membership_accounts
        context['current_user'] = user
        context['stripe_pluishable_key'] = settings.STRIPE_PUBLIC_KEY
        return context

    def post(self,request, **kwargs):
        # https://stackoverflow.com/questions/33239308/how-to-get-exception-message-in-python-properly
        cancel_user_subscription = self.request.POST.getlist('cancel_user_subscription') if 'cancel_user_subscription' in request.POST else None
        delete_card = self.request.POST.getlist('delete_card') if 'delete_card' in request.POST else None
        new_default_card_input = self.request.POST.getlist('new_default_card_input') if 'new_default_card_input' in request.POST else None
        individual_or_company_choice = self.request.POST.getlist('individual_or_company_choice') if 'individual_or_company_choice' in request.POST else None

        if cancel_user_subscription != None:
            user = User_Profile.objects.filter(user=self.request.user)[0]
            active_subsription= DividendWealthSubscription.objects.filter(user_profile=user,active=True)[0]

            #delete stripe subplan
            if active_subsription.stripe_subscription_id == 'lifetime' or active_subsription.stripe_subscription_id == 'free':
                pass
            else:
                stripe.Subscription.delete(active_subsription.stripe_subscription_id)

            #deactivate current subscription
            active_subsription.active = False
            active_subsription.save()
            new_active_subsription =  DividendWealthSubscription.objects.create(user_profile=user,stripe_subscription_id='free')
            #change current subcription to free
            new_membership=DividendWealthMembership.objects.filter(membership='f')[0]
            user.dividend_wealth_membership = new_membership
            user.save()
        if delete_card != None:
            user = User_Profile.objects.filter(user=self.request.user)[0]
            default_card = stripe.Customer.retrieve(user.stripe_customer_id)

            # check if the deleted card is the default card
            if default_card["default_source"] == delete_card[0]:
                # delete card
                stripe.Customer.delete_source(
                 user.stripe_customer_id,
                default_card["default_source"],
                )
                # get new default source
                default_card = stripe.Customer.retrieve(user.stripe_customer_id)
                default_card = default_card["default_source"]

                # check if we have a new default card or not
                if default_card == None:
                    data = {
                     'message': 'null default',
                    }
                    # print("no default card")
                    return JsonResponse(data)
                else:
                    data = {
                      'message': default_card,
                     }
                    # print("new default card")
                    return JsonResponse(data)
            else:
                stripe.Customer.delete_source(
                 user.stripe_customer_id,
                default_card["default_source"],
                )
                data = {
                 'message': 'null',
                }
                #

                print("did not delete default card")
                return JsonResponse(data)
        if new_default_card_input !=None:
            user = User_Profile.objects.filter(user=self.request.user)[0]
            # change default Source
            stripe.Customer.modify(
             user.stripe_customer_id,
              default_source = new_default_card_input[0],
            )
            data = {
              'message': "Default Card Changed",
             }
            # print("new default card")
            return JsonResponse(data)
        if individual_or_company_choice != None:
            user = User_Profile.objects.filter(user=self.request.user)[0]
            user.stripe_user_buisness_type = individual_or_company_choice[0]
            user.save()
            data = {
              'message': user.stripe_user_buisness_type,
              'email': user.user.email,
              'client_id': settings.CLIENT_ID,
             }
            # print("new default card")
            return JsonResponse(data)


        messages.info(self.request, "Canceled Your Current Membership")
        url = reverse('core:user_dashboard')
        return HttpResponseRedirect(url)


class Stocks_Create(generic.CreateView):
    template_name = 'stock_form.html'
    form_class = StocksModelForm
    queryset = Stocks.objects.all()
    success_url = '/'

class Stocks_Delete(generic.DeleteView):
    model = StockInfo
    success_url = reverse_lazy('core:user_dashboard')
    template_name ='stockinfo_confirm_delete.html'


class Stocks_Detail(generic.DetailView):
    model = Stocks
    template_name = 'stocks_detailview.html'

    def get_context_data(self, **kwargs):
        """Checks to see if user has stocks or not"""
        context = super(Stocks_Detail, self).get_context_data(**kwargs)
        user = User_Profile.objects.filter(user=self.request.user)[0]
        #check to see if the current user has the stock in his possesion already
        order_qs = user.stock.filter(slug=self.kwargs['slug']) #only want order that is nto completed
        x = order_qs.exists()
        print(x)
        context['stocks'] = order_qs

        return context


class User_Profile_Create(generic.CreateView):
    template_name = 'user_profile_form.html'
    form_class = User_profile_form
    success_url = '/'
    # I don't know why I have this query
    queryset = User_Profile.objects.all()

    def form_valid(self, form):
         """Saves current user to user profile """
         User_Profile = form.save(commit=False)
         User_Profile.user = self.request.user # use your own profile here
         User_Profile.save()
         return HttpResponseRedirect(reverse('core:user_dashboard')) #home page



class Update_Stock_User(generic.UpdateView):
    template_name = 'create_stock_user.Html'
    form_class = Stock_profile_form

    def form_valid(self, form,):
         """Saves current user to the profile """
         stock_user = form.save(commit=False)
         # user = get_object_or_404(User_Profile, user=self.request.user)
         # id =user.id
         # stock = get_object_or_404(Stocks,id=self.kwargs['id'])
         #
         # stock_user.userprofile_id = id # use your own profile here
         # stock_user.stock = stock
         #making sure that the quantity of stock stays above 0
         if stock_user.quantity <1:
             #post a message saying if you want to remove stock from your portfolio click remove stock
             stock_user.quantity =1

         stock_user.save()
         return HttpResponseRedirect(reverse('core:user_dashboard')) #home page

    def get_queryset(self):
        #get current user accessing page
        user = get_object_or_404(User_Profile, user=self.request.user)
        #list of stocks order by slug feild
        user.stock.order_by('slug').all()
        #use intermidary model to get instances where user profile equal to current user
        return StockInfo.objects.filter(userprofile =user).select_related()

class Create_Stock_User(generic.CreateView):
    template_name = 'create_stock_user.Html'
    form_class = Stock_profile_form

    def form_valid(self, form,):
         """Saves current user to the profile """
         stock_user = form.save(commit=False)
         user = get_object_or_404(User_Profile, user=self.request.user)
         id =user.id
         stock = get_object_or_404(Stocks,slug=self.kwargs['slug'])

         stock_user.userprofile_id = id # use your own profile here
         stock_user.stock = stock
         stock_user.save()
         return HttpResponseRedirect(reverse('core:user_dashboard')) #home page


class User_Dashboard(generic.ListView):

    """
    context = super(User_Dashboard, self).get_context_data(**kwargs)
    user = UserProfile.objects.filter(user=self.request.user)[0]
    stock = user.stock.order_by('slug').all() """
    login_url ='/accounts/login'
    redirect_field_name = '/user_dashboard'
    template_name='user_dashboard.html'
    paginate_by = 2

    def get(self, *args, **kwargs):

        # need to test this when user is creating stripe account
        if self.request.user.is_authenticated:
            pass
        else:
            url = reverse('core:feed')
            return HttpResponseRedirect(url)

        stripeOAUTH = self.request.GET.getlist('code') if 'code' in self.request.GET else None
        if stripeOAUTH != None:
            user = User_Profile.objects.filter(user=self.request.user)[0]
            self.request.session['stripe_auth'] =stripeOAUTH[0]
            print(stripeOAUTH[0])
            url = reverse('core:user_account', kwargs={'username':user.user.username})
            return HttpResponseRedirect(url)
        # if stripe code is not available then go to regular page
        return super(User_Dashboard, self).get(self.request, *args, **kwargs)

    def get_queryset(self):

        #get current user accessing page
        user,create =  User_Profile.objects.get_or_create(user=self.request.user)
        #list of stocks order by slug feild
        user.stock.order_by('slug').all()
        #use intermidary model to get instances where user profile equal to current user
        return StockInfo.objects.filter(userprofile =user).select_related()

    def get_context_data(self, **kwargs):
        context = super(User_Dashboard, self).get_context_data(**kwargs)
        #user = User_Profile.objects.filter(user=self.request.user)[0]
        user,create = User_Profile.objects.get_or_create(user=self.request.user)
        #using
        stock = user.stock.order_by('slug').all()

        # Get List of groups User has made
        if GenGroup.objects.filter(creator=user).exists():
            user_created_groups = GenGroup.objects.filter(creator=user)
            context["user_created_groups"] = user_created_groups

        # Check if user has unpublished groups
        if GenGroup.objects.filter(published=False,creator=user):
            messages.info(self.request, "You have unpublished groups!")
            # could create a notification that linked to the group

        #m =StockInfo.objects.filter(userprofile =user).aggregate(income=Sum('stock__dividend__dividend_amount',output_field=FloatField()))
#get the last 4 dividend entries for each stock user owns
        #/////////////////////////////////succesful annotation
        #qs = Dividend.objects.all()[:3]
        #p =StockInfo.objects.filter(userprofile =user,stock__dividend__date__gt=datetime.date(2018, 8, 24)).aggregate(income=Sum(F('quantity')*F('stock__dividend__dividend_amount'),output_field=FloatField()))
        #q =StockInfo.objects.filter(userprofile =user).filter(stock__dividend__date__gt=datetime.date(2018, 8, 24)).aggregate(income=Sum(F('quantity')*F('stock__dividend__dividend_amount'),output_field=FloatField()))


        queryset = StockInfo.objects.filter(userprofile =user).filter(stock__dividend__date__gt=datetime(year=2018,month=8,day=24))
        #using
        stock_count = len(StockInfo.objects.filter(userprofile =user))
        # stock dividend ammount
        x =StockInfo.objects.filter(userprofile =user).filter(stock__dividend__date__gt=datetime(year=2018,month=8,day=24)).aggregate(dividend_income=Sum(F('quantity')*F('stock__dividend__dividend_amount'),output_field=FloatField()))


        # stock Protfolio cost
        y =StockInfo.objects.filter(userprofile =user).aggregate(stock_portfolio=Sum(F('quantity')*F('stock__price'),output_field=FloatField()))


        #print(x)
        #print(queryset)
        #print(y)
        #/////////////////////////////////
        #protfolio dividend yeild
        if x['dividend_income'] is None:
            z ='None'
            x['dividend_income'] ='none'
            y['stock_portfolio'] = 'none'
        else:
            z= (x['dividend_income']/y['stock_portfolio'] )*100
            user.current_dividend_income = x['dividend_income']
            user.percentage_difference_between_dividend_income_wanted =((user.estimated_dividend_income_wanted - user.current_dividend_income) / user.estimated_dividend_income_wanted)*100
            user.percentage_of_estimated_income_reached = ((user.current_dividend_income/ user.estimated_dividend_income_wanted))*100
            income_wanted = user.percentage_difference_between_dividend_income_wanted
            income_reached = user.percentage_of_estimated_income_reached
            user.save()
        #print(z)
            #/////////////////////////////////
            #manipulating
        ds = PivotDataPool(
        series=[
        {'options': {
            #https://stackoverflow.com/questions/9750330/how-to-convert-integer-into-date-object-python, datetime was messed up from previous iteration changed it to current form the code above that contain date time needs to be changed
            #important read above
            'source':  StockInfo.objects.filter(userprofile =user).filter(stock__dividend__date__gt=datetime(year=2018,month=8,day=24)),#.order_by('stock__dividend__month_int')
            'categories': ['stock__dividend__month'],
            'legend_by': ['stock__company_name',],
            },
            'terms': {
                'Dividend Income': Sum(F('quantity')*F('stock__dividend__dividend_amount'),output_field=FloatField())}}],
                )

        chart_1 = PivotChart(
                  datasource=ds,
                  series_options=[
                    {'options': {
                       'type': 'column',
                       'stacking': True,
                       'xAxis': 0,
                       'yAxis': 0},
                     'terms': ['Dividend Income']}],
                     chart_options={
            'title': {
                'text': 'Dividend Income by Month'
            },
            'xAxis': {
                'title': {
                    'text': 'Month'
                }
            },'yAxis': {
                'title': {
                    'text': 'Dividend Income'
                }
            }


        })

        ds1 = DataPool(
                series=[{
                    'options': {
                        'source': User_Profile.objects.filter(user=self.request.user)
                    },
                    'terms': [
                        'percentage_difference_between_dividend_income_wanted',
                        'percentage_of_estimated_income_reached',
                    ]
                }]
        )


        chart_2 = Chart(
                datasource=ds1,
                series_options=[{
                    'options': {
                        'type': 'pie',
                        'stacking': False
                    },
                    'terms': {

                        'percentage_of_estimated_income_reached':['percentage_difference_between_dividend_income_wanted']

                    }
                }],
                chart_options={
                    'title': {
                        'text': ' '
                    }
                }

        )


        context['stocks_qun'] = stock
        context['user'] = user
        try:
            context['income_wanted'] = income_wanted
        except UnboundLocalError:
            context['income_wanted'] = 1

        try:
            context['income_reached'] = income_reached
        except:
            context['income_reached'] = .5
        try:
            context['protfolio_ammount'] = y['stock_portfolio']
        except:
            context['protfolio_ammount'] = 0

        try:
            context['dividend_income'] = x['dividend_income']
        except:
            context['dividend_income'] = x['dividend_income']

        try:
            context['portfolio_yeild'] =z
        except:
            context['portfolio_yeild'] =0

        try:
            context['chart_list'] = [chart_1,chart_2]
        except:
            context['chart_list'] = [chart_1,chart_2]

        try:
            context['stock_count'] = stock_count
        except:
            context['stock_count'] = 0




        return context


#do not overwrite ds from the first chart


        #////////////////////////////////
        #I don't know why it is not working
        #dividend incom chart



        #////////////////////////////////









class User_Profile_Update(generic.UpdateView):
    template_name = 'user_profile_form.html'
    form_class = User_profile_form
    success_url = '/'
    queryset = User_Profile.objects.all()

def add_stock_to_user(request,slug):
    stock = get_object_or_404(Stocks,slug=slug)
    user = get_object_or_404(User_Profile, user=self.request.user)
    stockinfo,created = StockInfo.objects.get_or_create(userprofile=user,stock =stock)
    stockinfo.save()

class SearchResultsView(generic.ListView):
    model = Stocks
    template_name = 'search_results.html'

    def get_queryset(self): # new
        query = self.request.GET.get('q')
        object_list = Stocks.objects.filter(
            Q(ticker__icontains=query) | Q(company_name__icontains=query)
        )
        return object_list

    def get_context_data(self, **kwargs):
        """Checks to see if user has stocks or not"""
        query = self.request.GET.get('q')
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        user = User_Profile.objects.filter(user=self.request.user)[0]
        order_qs = user.stock.filter(Q(ticker__icontains=query) | Q(company_name__icontains=query)) #only want order that is nto completed
        x = order_qs.exists()
        print(x)
        context['stocks'] = order_qs
        return context




def add_to_cart(request,slug):
    item = get_object_or_404(Item,slug=slug) #get the item instance where the slug is equal to the slug picked
    order_item,created = OrderItem.objects.get_or_create(item=item,user=request.user,ordered=False) #returning a tuple(throws up init error)
    order_qs = Order.objects.filter(user=request.user, ordered=False) #only want order that is nto completed
    if order_qs.exists():
        order = order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists(): #filter items to where the item slug attribute = item.slug
            order_item.quantity +=1 #increment the order item by 1
            order_item.save()
            messages.info(request, "Item quantity was updated")
            return redirect("core:products",slug=slug)

        else:
            messages.info(request, "This item was added to your cart")
            order.items.add(order_item)
            return redirect("core:products",slug=slug)

    else: #if thte query set does not exit
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date = ordered_date )
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart")
        return redirect("core:products",slug=slug)
    #if using reveruse you would use kwargs

def remove_from_cart(request,slug):
        item = get_object_or_404(Item,slug=slug) #get the item instance where the slug is equal to the slug picked
        order_qs = Order.objects.filter(user=request.user, ordered=False) #only want order that is not completed
        if order_qs.exists():
            order = order_qs[0] #grabing order instance
            #check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(item=item,user=request.user,ordered=False)[0]#returning a tuple(throws up init error)
                order.items.remove(order_item)
                messages.info(request, "This item was removed from your cart")
                return redirect("core:products",slug=slug)
            else:
                #dd a message saying the order does not contain the order item
                messages.info(request, "This item was not in your cart")
                return redirect("core:products",slug=slug)
        else: #if thte query set does not exit
            #add a message saying the user doesnt have an order
            messages.info(request, "You do not have an active order")
            return redirect("core:products",slug=slug)
