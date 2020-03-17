import os
from django.db import models
from django.conf import settings #for django allauth
from django.urls import reverse# Create your models here
from django.utils.text import slugify
from django.utils.dateparse import parse_date
from django.db.models.signals import post_save
from django.dispatch import receiver
#list of states
from localflavor.us.us_states import STATE_CHOICES #pip install django-locaalflavor
from tinymce import HTMLField
from django.contrib.auth import get_user_model
from django.dispatch import Signal
from django.utils import timezone
from datetime import datetime,timedelta
from django.db import connection

CATEGORY_CHOICES = (
    ('S','Shirt'), #first entry goes into the database second is what is displayed
    ('SW','Sport Wear'),
    ('OW','Outwear'),
)

LABEL_CHOICES = ( #changing the css with this
    ('P','primary'),
    ('S','secondary'),
    ('D','danger'),
)

class Item(models.Model):
    title = models.CharField(max_length = 100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True) #don't have to have discount price due to blank/null being true
    category = models.CharField( choices = CATEGORY_CHOICES, max_length=2, default="S") #look up choices in django
    label = models.CharField(choices=LABEL_CHOICES, max_length=1, default="P")
    description = models.TextField(default='NOT_PROVIDED')
    slug = models.SlugField(default= "dummy-item")

    def __str__(self):
        return self.title

    def get_absolute_url(self): #model has a detail page so it need to have this function
        return reverse('core:products',kwargs={'slug':self.slug})

    def get_add_to_cart_url(self): #in views we manipulate the model
        return reverse('core:add_to_cart',kwargs={'slug':self.slug})

    def get_remove_from_cart_url(self): #in views we manipulate the model
        return reverse('core:remove-from-cart',kwargs={'slug':self.slug})




class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,blank=True,null = True) #connecting user to model
    ordered = models.BooleanField(default=False)
    title = models.CharField(max_length = 100)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

class Order(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) #connecting user to model

    items = models.ManyToManyField(OrderItem) #add order item into order
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)


    def __str__(self):
        return self.user.username


class Article(models.Model):
    source = models.CharField(max_length = 500,null=True, blank=True)
    title = models.CharField(max_length = 500,null=True, blank=True)
    description = models.CharField(max_length = 500,null=True, blank=True)
    url = models.URLField(max_length = 500,null=True, blank=True)
    urltoimage = models.URLField(max_length = 500,null=True, blank=True)
    author = models.CharField(max_length = 500,null=True, blank=True)
    published = models.DateField(null=True, blank=True)
    query_cat = models.CharField(max_length = 500,null=True, blank=True)
    created_date =models.DateTimeField(auto_now_add=True,null=True, blank=True)


    def __str__(self):
        return f"{self.source} : {self.title}"


    #         'title':x['articles'][0]['title'] ,
    #         'description':x['articles'][0]['description'] ,
    #         'url': x['articles'][0]['url'],
    #         'urltoimage': x['articles'][0]['urlToImage'],
    #

distrubution_CHOICES = ( #changing the css with this
    ('Q','Quarterly'),
    ('B','Bi Yearly'),
)

months_CHOICES = ( #changing the css with this
    ('J','January/April/July/October'),
    ('F',' February/May/August/November'),
    ('M',' March/June/September/December'),
)

month_CHOICES = ( #changing the css with this
    (1,'Jan'),
    (2,'Feb'),
    (3,'Mar'),
    (4,'Apr'),
    (5,'May'),
    (6,'Jun'),
    (7,'Jul'),
    (8,'Aug'),
    (9,'Sep'),
    (10,'Oct'),
    (11,'Nov'),
    (12,'Dec'),
)
"""
('Jan','Jan'),
('Feb','Feb'),
('Mar','Mar'),
('Apr','Apr'),
('May','May'),
('Jun','Jun'),
('Jul','Jul'),
('Aug','Aug'),
('Sep','Sep'),
('Oct','Oct'),
('Nov','Nov'),
('Dec','Dec'),

"""

class Dividend(models.Model):
    company_name = models.CharField(max_length = 100,null=True, blank=True)
    dividend_amount = models.FloatField( null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    month = models.IntegerField(choices=month_CHOICES,null=True, blank=True) # max_length=3, default="Jan"
    month_int = models.IntegerField(null=True, blank=True)

    #stock = models.ForeignKey(Stocks,null=True,on_delete=models.CASCADE )

    def __str__(self):
        return f"{self.company_name} Dividend Amount  {self.dividend_amount} Date: {self.date}"

class Stocks(models.Model):
    ticker = models.CharField(max_length = 100,unique=True,null=True, blank=True)
    company_name = models.CharField(max_length = 100,null=True, blank=True)
    price = models.FloatField( null=True, blank=True)
    profile_pic = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=100,null=True, blank=True)
    fairvale = models.FloatField( null=True, blank=True)
    dividend_yeild = models.FloatField( null=True, blank=True)
    dividend_growth= models.FloatField( null=True, blank=True)
    earning_growth = models.FloatField( null=True, blank=True)
    distrubution = models.CharField(choices=distrubution_CHOICES, max_length=1, default="S",null=True, blank=True)
    months =  models.CharField(choices=months_CHOICES, max_length=1, default="S",null=True, blank=True)
    slug = models.SlugField(default= "dummy-stock")
    url = models.URLField(max_length=200,null=True, blank=True )
    dividend =models.ManyToManyField(Dividend,blank = True)

 #connecting user to model
    def save(self,*args,**kwargs): #type in what ever you want for name but name wil be slugfied when saved
        self.slug = slugify(self.ticker)
        super().save(*args,**kwargs)

    def get_absolute_url(self): #model has a detail page so it need to have this function
        return reverse('core:stocks_detail',kwargs={'slug':self.slug})


    def __str__(self):
        return f"{self.company_name} : {self.ticker}"



tax_filing_status_CHOICES = ( #changing the css with this
    ('M','Single'),
    ('J','Married Filing Jointly'),
    ('S','Married Filing Separatly'),
    ('H','Head of Household'),
    ('M','Qualifying Widow(er)'),
)

Brokarage_account_CHOICES = ( #changing the css with this
    ('T','TdAmeritrade'),
    ('M','Fidelity Investments'),
    ('W','Wells Fargo Advisors'),
    ('E','Edward Jones'),
    ('R','Raymond James Financial'),
    ('A','AXA Advisors'),
    ('L','LPL Financial'),
    ('I','Ameriprise Financia'),
    ('V','Voya'),
    ('C','Commonwealth Financial Network'),
    ('N','Northwest Mutual Inv. Services'),
    ('B','Cambridge Investment Research'),
    ('S','Securities America'),
    ('D','Waddell & Reed'),
    ('O','Other'),
)

online_status = ( #changing the css with this
    ('o','online'),
    ('f','offline'),
)

employment_status_CHOICES =[
('Employed', (
            ('F', 'Fulltime'),
            ('P', 'Part-Time'),
        )
    ),
    ('S', 'Self Employed'),
    ('T', 'Student'),
    ('R', 'Retired'),
    ('H', 'Homemaker'),
    ('N', 'Not Employed'),
]
#create user pages
#get stock information from api
#create blogs
#create article feed

# class UserProfile(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) #connecting user to model
#     profile_pic = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=100,blank=True,null = True)
#     first_name=models.CharField(max_length=30,null=True, blank=True)
#     last_name=models.CharField(max_length=30,null=True, blank=True)
#     age = models.IntegerField(null=True, blank=True)
#     dependents = models.IntegerField(null=True, blank=True)
#     tax_filing_status = models.CharField(choices=tax_filing_status_CHOICES, max_length=1, default="J",null=True, blank=True)
#     employment_status = models.CharField(choices=employment_status_CHOICES, max_length=1, default="F",null=True, blank=True)
#     occupation=models.CharField(max_length=30,null=True, blank=True)
#     employer=models.CharField(max_length=30,null=True, blank=True)
#     Approximate_Annual_Income = models.IntegerField(null=True, blank=True)
#     Approximate_Net_Worth = models.IntegerField(null=True, blank=True)
#     Brokarage_account =  models.CharField(choices=Brokarage_account_CHOICES, max_length=1, default="S",null=True, blank=True)
#     estimated_investable_assets= models.IntegerField(null=True, blank=True)
#     slug = models.SlugField(null=True, blank=True)
#     stock = models.ManyToManyField(Stocks,blank = True,through='StockInfo')
#     sign_up_date = models.DateTimeField(auto_now_add=True)
#     estimated_dividend_income = models.IntegerField(null=True, blank=True) #I will calculate out the
#     current_dividend_income= models.IntegerField(null=True, blank=True)
Membership_Choices = (
    ('f','Free'),
    ('m','Monthly'),
    ('y','Yearly'),
    ('l','Lifetime')
)
class Cards(models.Model):
    token = models.CharField(max_length=50,null=True, blank=True)

class DividendWealthMembership(models.Model):
    slug = models.SlugField(null=True, blank=True)
    membership = models.CharField(choices=Membership_Choices, max_length=1, default="f",null=True, blank=True)
    price = models.IntegerField(default=0,null=True, blank=True)
    stripe_plan_id = models.CharField(max_length=40,null=True, blank=True)
    subscription = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.membership}"
    def save(self,*args,**kwargs): #type in what ever you want for name but name wil be slugfied when saved
        self.slug = slugify(self.membership)
        #getting percentate
        super().save(*args,**kwargs)

class Credential(models.Model):
    title=models.CharField(max_length=30,null=True, blank=True)
    def __str__(self):
        return f"{self.title}"

class FinancialRole(models.Model):
    title=models.CharField(max_length=30,null=True, blank=True)
    # create a function which after a change in finacnial role by member checks to see if the fincial role is still being used
    def __str__(self):
        return f"{self.title}"

class User_Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) #connecting user to model
    profile_pic = models.ImageField(upload_to='profile_img/', height_field=None, width_field=None, max_length=100,blank=True,null = True)
    first_name=models.CharField(max_length=30,null=True, blank=True)
    last_name=models.CharField(max_length=30,null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    dependents = models.IntegerField(null=True, blank=True)
    tax_filing_status = models.CharField(choices=tax_filing_status_CHOICES, max_length=1, default="J",null=True, blank=True)
    employment_status = models.CharField(choices=employment_status_CHOICES, max_length=1, default="F",null=True, blank=True)
    occupation=models.CharField(max_length=30,null=True, blank=True)
    employer=models.CharField(max_length=30,null=True, blank=True)
    Approximate_Annual_Income = models.IntegerField(null=True, blank=True)
    Approximate_Net_Worth = models.IntegerField(null=True, blank=True)
    Brokarage_account =  models.CharField(choices=Brokarage_account_CHOICES, max_length=1, default="S",null=True, blank=True)
    estimated_investable_assets= models.IntegerField(null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    stock = models.ManyToManyField(Stocks,blank = True,through='StockInfo')
    sign_up_date = models.DateTimeField(auto_now_add=True)
    estimated_dividend_income_wanted = models.IntegerField(null=True, blank=True) #I will calculate out the
    percentage_difference_between_dividend_income_wanted=models.FloatField(null=True,blank=True)
    percentage_of_estimated_income_reached = models.FloatField(null=True,blank=True)
    current_dividend_income= models.IntegerField(null=True, blank=True)
    online_status = models.CharField(choices=online_status, max_length=1, default="f",null=True, blank=True)
    notification_count = models.IntegerField(default=0)
    dividend_wealth_membership = models.ForeignKey(DividendWealthMembership, on_delete=models.SET_NULL,blank=True,null=True)
    stripe_customer_id = models.CharField(max_length=40,null=True, blank=True)
    user_cards= models.ManyToManyField(Cards,blank = True,through='UserProfileCards')
    stripe_user_buisness_type = models.CharField(max_length=30,null=True, blank=True)
    user_credentials= models.ManyToManyField(Credential,blank = True,through='UserCredential')
    user_financial_role= models.ManyToManyField(FinancialRole,blank = True,through='UserFinancialRole')
    background_pic =  models.ImageField(upload_to='profile_background_img/', height_field=None, width_field=None, max_length=100,blank=True,null = True)
    user_relationship =  models.ManyToManyField('self',blank = True,through='UserRelationship', symmetrical=False)
    active_notification_url = models.CharField(max_length=60,null=True, blank=True)
    featured =  models.BooleanField(default=False)
    def save(self,*args,**kwargs): #type in what ever you want for name but name wil be slugfied when saved
        self.slug = slugify(self.user)
        #getting percentate
        super().save(*args,**kwargs)


    def user_fullname(self):
        if self.first_name:
            return self.first_name.title() + ' '+ self.last_name.title()
        else:
            return None
    def user_financial_role(self):
        financial_roles=UserFinancialRole.objects.filter(user_profile=self)
        roles_list = []
        for role in financial_roles:

            title=role.financial_role.title
            if title == "N/A":
                continue
            roles_list.append(title)
        return '/'.join(roles_list)

    def user_financial_credentials(self):
        financial_credential=UserCredential.objects.filter(user_profile=self)
        credential_list = []
        for cred in financial_credential:
            title=cred.credential.title
            if title == "N/A":
                continue
            credential_list.append(title)
        return ' '.join(credential_list)

    def current_dividend_wealth_member(self):
        if self.dividend_wealth_membership.membership != 'f':
            return True
        else:
            return False

    def __str__(self):
        return f"{self.user.username} : user profile"

class UserRelationship(models.Model):
    following = models.ForeignKey(User_Profile, on_delete=models.CASCADE,related_name='following')
    follower = models.ForeignKey(User_Profile, on_delete=models.CASCADE,related_name='follower')
    created = models.DateTimeField(auto_now_add=True)


class UserCredential(models.Model):
    user_profile = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    credential = models.ForeignKey(Credential, on_delete=models.CASCADE)
    credential_pic = models.ImageField(upload_to='credentials/', height_field=None, width_field=None, max_length=100,blank=True,null = True)
    validated = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user_profile} {self.credential}"

class UserFinancialRole(models.Model):
    user_profile = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    financial_role = models.ForeignKey(FinancialRole, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user_profile} {self.financial_role}"


class UserProfileCards(models.Model):
    user_profile = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    card = models.ForeignKey(Cards, on_delete=models.CASCADE)
    sign_up_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

class DividendWealthSubscription(models.Model):
    user_profile = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=40,null=True, blank=True)
    active = models.BooleanField(default=True)
    sub_date = models.DateTimeField(auto_now_add=True,null=True, blank=True)

    def __str__(self):
        return f"{self.user_profile.user.username} subscription"
class DividendWealthConnectedAccount(models.Model):
    user_profile = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    stripe_connected_account_id = models.CharField(max_length=30,null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True, blank=True)

class DividendWealthConnectedAccountPayments(models.Model):
    connected_account = models.ForeignKey(DividendWealthConnectedAccount, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    buyer= models.ForeignKey(User_Profile, on_delete=models.CASCADE, related_name="buyer")
    price = models.FloatField(null=True, blank=True)
    description = models.CharField(max_length=50,null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True, blank=True)

class DividendWealthFee(models.Model):
    user_profile = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=40,null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user_profile.user.username} fee"

class File(models.Model):
    creator = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    upload = models.FileField(upload_to='groupfiles/',null=True, blank=True)
    created_date =models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated = models.DateField(null=True,blank = True,)
    title = models.CharField(max_length = 500,null=True, blank=True)
    description = models.CharField(max_length = 500,null=True, blank=True)
    downloaded_num = models.IntegerField(default=0)
    downloaderf = models.ManyToManyField(User_Profile,blank=True, related_name = 'downloadeef', through='FileDownload')

    def filename(self):
        return os.path.basename(self.upload.name)
class FileDownload(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    downloaderf = models.ForeignKey(User_Profile, on_delete=models.CASCADE)

class StockWatchlist(models.Model):
    creator = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    stocks = models.ManyToManyField(Stocks, blank = True,through='WatchStockDetail')
    created_date =models.DateField(null=True,auto_now_add=True)
    updated = models.DateField(null=True,blank = True,)
    title = models.CharField(max_length = 500,null=True, blank=True)
    description = models.CharField(max_length = 500,null=True, blank=True)
    downloaded = models.IntegerField(default=0)
    added = models.BooleanField(default=False)
    checked = models.BooleanField(default=True)
    downloader = models.ManyToManyField(User_Profile,blank=True, related_name = 'downloadee', through='WatchlistDownload')
class WatchlistDownload(models.Model):
    watchlist = models.ForeignKey(StockWatchlist, on_delete=models.CASCADE)
    downloader = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
class WatchStockDetail(models.Model):
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    watchlist = models.ForeignKey(StockWatchlist, on_delete=models.CASCADE)
    date_added = models.DateField(null=True,auto_now_add=True)
class Categories(models.Model):
    description = models.CharField(max_length = 500,null=True, blank=True)
    created = models.DateTimeField(null=True,auto_now_add=True)

    def __str__(self):
        return f"{self.description}"

    def save(self,*args,**kwargs): #type in what ever you want for name but name wil be slugfied when saved
        self.description = self.description.capitalize()
        #getting percentate

        super().save(*args,**kwargs)
# ///////////////////groups
group_type = (
    ('f','Free'),
    ('s','Subscription'),
    ('o','One Time Fee')
)


class GenGroup(models.Model):
    title = models.CharField(max_length = 500,null=True, blank=True, unique = True)
    description = models.CharField(max_length = 500,null=True, blank=True)
    members = models.ManyToManyField(User_Profile,blank = True,through='GroupMember')
    creator = models.ForeignKey(User_Profile,null = True,blank=True,on_delete=models.SET_NULL,related_name ='creator')
    created = models.DateTimeField(null=True,auto_now_add=True)
    slug = models.SlugField(null=True, blank=True)
    value_proposition =  HTMLField(null=True, blank=True)
    rules_guidlines =  HTMLField(null=True, blank=True)
    stock_watchlist = models.ManyToManyField(StockWatchlist, blank = True,through='GroupWatchlist')
    files = models.ManyToManyField(File,blank=True,through='GroupFileList')
    price = models.IntegerField(null=True, blank=True)
    group_type = models.CharField(choices=group_type, max_length=1, default="f",null=True, blank=True)
    group_picture = models.ImageField(upload_to='group-pics/', height_field=None, width_field=None, max_length=100,blank=True,null = True)
    categories = models.ManyToManyField(Categories,blank=True,through='GroupCategories')
    published =  models.BooleanField(default=True) # free membership
    unpublished_reason =  models.CharField(max_length = 500,null=True, blank=True)

    def save(self,*args,**kwargs): #type in what ever you want for name but name wil be slugfied when saved
        self.slug = slugify(self.title)
        #getting percentate

        super().save(*args,**kwargs)
    def member_count(self):
        return GroupMember.objects.filter(group=self,active=True).count()
    def price_reformat(self):
        return "{:.2f}".format(self.price / 100 )
    def get_absolute_url(self): #model has a detail page so it need to have this function
        return reverse('core:group',kwargs={'slug':self.slug})

    def landing_page(self):
        return reverse('core:group-landing', kwargs={'slug': self.slug,})

    def posts_today(self):
         start_of_day=timezone.localtime().replace(hour=0, minute=0)
         post=Post.objects.filter(alert=False,group=self,hidden=False,published__gte=start_of_day).count()
         comment=Comments.objects.filter(post__group=self,hidden=False,published__gte=start_of_day).count()
         reply=CommentReply.objects.filter(comment__post__group=self,hidden=False,published__gte=start_of_day).count()
         return post+comment+reply
    def posts_last_thirty_days(self):
        thirty_days_ago = timezone.localtime()-timedelta(days=30)
        post=Post.objects.filter(alert=False,group=self,hidden=False,published__gte=thirty_days_ago).count()
        comment=Comments.objects.filter(post__group=self,hidden=False,published__gte=thirty_days_ago).count()
        reply=CommentReply.objects.filter(comment__post__group=self,hidden=False,published__gte=thirty_days_ago).count()
        return post+comment+reply

    def group_activeness(self):
        members = GroupMember.objects.filter(group=self,active=True)
        list_of_member_times= []
        x = 0
        for member in members:
            in_group_time=member.in_group_time
            if in_group_time != None:
                list_of_member_times.append(int(in_group_time))
                try:
                    x =sum(list_of_member_times) / len(list_of_member_times)
                except:
                    x = 0
        return "{:.1f}".format(x)

    def avg_members_online(self):
        members = GroupMember.objects.filter(group=self,active=True)
        list_of_member_times= []
        for member in members:
            if member.in_group_time != None:
                if int(member.in_group_time) >= 25:
                    list_of_member_times.append('y')
        return len(list_of_member_times)

    def avg_member_joining_a_week(self):
        members = GroupMember.objects.filter(group=self,active=True,joined__gte=timezone.localtime()-timedelta(days=7)).count()
        return members

    def group_members(self):
        return GroupMember.objects.filter(group=self,member_status__in=["d","a"]).select_related('userprofile')

    def __str__(self):
        return f" {self.title} "

class GroupMetrics(models.Model):
    group = models.OneToOneField(GenGroup, on_delete=models.CASCADE)
    new_posts_today = models.IntegerField(null=True, blank=True)
    posts_this_month =  models.IntegerField(null=True, blank=True)
    avg_num_members_online =  models.IntegerField(null=True, blank=True)
    avg_mem_joining_week =  models.IntegerField(null=True, blank=True)

class GroupCategories(models.Model):
    group = models.ForeignKey(GenGroup, on_delete=models.CASCADE)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    created = models.DateTimeField(null=True,auto_now_add=True)


class GroupWatchlist(models.Model):
    group = models.ForeignKey(GenGroup, on_delete=models.CASCADE)
    stockwatchlist = models.ForeignKey(StockWatchlist, on_delete=models.CASCADE)
    date_added = models.DateTimeField(null=True,auto_now_add=True)

class GroupFileList(models.Model):
    group = models.ForeignKey(GenGroup, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    date_added = models.DateTimeField(null=True,auto_now_add=True)

group_online_status = ( #changing the css with this
    ('o','online'),
    ('f','offline'),
)

group_member_status = ( #changing the css with this
    ('m','Member'),
    ('a','Admin'),
    ('d','Moderator'),
)
class GroupMember(models.Model):
    group = models.ForeignKey(GenGroup, on_delete=models.CASCADE)
    userprofile = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    joined = models.DateTimeField(null=True,auto_now_add=True)
    moderator = models.BooleanField(default=False)
    group_online_status = models.CharField(choices=group_online_status, max_length=1, default="f",null=True, blank=True)
    creator = models.BooleanField(default=False)
    member_status =  models.CharField(choices=group_member_status, max_length=1, default="m",null=True, blank=True)
    timespent_in_group = models.IntegerField(default=0)
    avg_session_time = models.IntegerField(null=True,blank=True)
    in_group_time = models.CharField(max_length = 500,null=True, blank=True)
    active =  models.BooleanField(default=True)
    def __str__(self):
        return f" {self.userprofile} in {self.group}"

class GroupSubscription(models.Model):
    group = models.ForeignKey(GenGroup,null=True, on_delete=models.CASCADE)
    subscription = models.BooleanField(default=False)
    created = models.DateTimeField(null=True,auto_now_add=True)
    price = models.IntegerField(null=True,blank=True)
    group_member = models.ForeignKey(GroupMember, on_delete=models.CASCADE)
    connected_account = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    next_payment = models.DateTimeField(null=True)
    active = models.BooleanField(default=True)

class GroupPayment(models.Model):
    price = models.IntegerField(null=True,blank=True)
    charge_date = models.DateTimeField(null=True,auto_now_add=True)
    person_paying =models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    person_receiving = models.ForeignKey(User_Profile, on_delete=models.CASCADE, related_name="reciver")
    group = models.ForeignKey(GenGroup,null=True, on_delete=models.CASCADE)
    description = models.CharField(max_length = 500,null=True, blank=True)
    charge_id =  models.CharField(max_length = 500,null=True, blank=True)
# ///////////////////groups
class StockInfo(models.Model):
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    userprofile = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True)
    date_included = models.DateField(null=True,auto_now_add=True )

    def __str__(self):
        return f"{self.stock}"

#/////Post /////////////
class WebsiteUrl(models.Model):
    url = models.CharField(max_length = 500,null=True, blank=True)

class Topic(models.Model):
    title =  models.CharField(max_length = 500,null=True, blank=True)
    def __str__(self):
        return f"{self.title}"

class Post(models.Model):
    author = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length = 500,null=True, blank=True)
    topic = models.ManyToManyField(Topic,blank = True)
    description = models.CharField(max_length = 500,null=True, blank=True)
    content = HTMLField(null=True, blank=True)
    stocks = models.ManyToManyField(Stocks,blank = True,)
    user_like = models.ManyToManyField(User_Profile,blank = True,through='PostLike',related_name='post_user_like')
    likes =  models.IntegerField(default=0)
    user_view = models.ManyToManyField(User_Profile,blank = True,through='PostViewCount',related_name='post_user_view')
    viewcount = models.IntegerField(default=0)
    published = models.DateTimeField(auto_now_add=True,null=True)
    comment_count = models.IntegerField(default=0)
    repost = models.ForeignKey('self', on_delete=models.CASCADE,null=True, blank=True)
    repost_count = models.IntegerField(default=0)
    group = models.ForeignKey(GenGroup, on_delete=models.CASCADE,null=True, blank=True)
    hidden = models.BooleanField(default=False)
    reported = models.ManyToManyField(User_Profile,blank = True,through='PostReport',related_name='post_reported')
    reported_count = models.IntegerField(default=0)
    recipients = models.ManyToManyField(User_Profile, blank = True,related_name='postrecipients')
    alert= models.BooleanField(default=False)
    attached_url = models.ManyToManyField(WebsiteUrl,blank = True,through='PostUrl')
    #if reported exceeds 5 hide
    #add comment here then create through feild comment values
    #comments = models.ManyToManyField(Comments,blank=True)
    def __str__(self):
        return f"{self.title} from {self.author} about {self.description}"

    def get_absolute_url(self):
        return reverse('core:post-detail',kwargs={'pk':self.id})

    def check_comment_count(self):
        return Comments.objects.filter(post=self,hidden=False).count() + CommentReply.objects.filter(comment__post=self,hidden=False).count()

    def like_count(self):
        return PostLike.objects.filter(post=self).count()
    def last_like(self):
        return PostLike.objects.filter(post=self).last()

class PostReport(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    userprofile = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    date_reported = models.DateField(null=True,auto_now_add=True )

class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    userprofile = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    date_liked = models.DateField(null=True,auto_now_add=True)

class PostViewCount(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    userprofile = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    date_viewed = models.DateField(null=True,auto_now_add=True)

class PostPicture(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    post_picture = models.ImageField(upload_to='post_img/', height_field=None, width_field=None, max_length=100,blank=True,null = True)

class PostUrl(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    url =  models.ForeignKey(WebsiteUrl, on_delete=models.CASCADE)

class Comments(models.Model):
    author =models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    contents = models.CharField(max_length = 500,null=True, blank=True)
    recipients = models.ManyToManyField(User_Profile, blank = True, related_name='recipients')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,blank=True, null=True,related_name ='post_comment')
    stocks = models.ManyToManyField(Stocks,blank = True,)
    user_like = models.ManyToManyField(User_Profile,blank = True,through='CommentsLike',related_name='comment_user_like')
    likes =  models.IntegerField(default=0)
    published = models.DateTimeField(auto_now_add=True,null=True)
    hidden = models.BooleanField(default=False)
    reported = models.ManyToManyField(User_Profile,blank = True,through='CommentsReport',related_name='comment_reported')
    reported_count = models.IntegerField(default=0)
    def __str__(self):
        return f"Comment from {self.author} about {self.contents}"

    def check_reply_count(self):
        return CommentReply.objects.filter(comment=self,hidden=False).count()
    def comment_like_count(self):
        return CommentsLike.objects.filter(comments=self).count()
    def comment_last_like(self):
        return CommentsLike.objects.filter(comments=self).last()

class CommentsLike(models.Model):
    comments = models.ForeignKey(Comments, on_delete=models.CASCADE)
    userprofile = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    date_liked = models.DateField(null=True,auto_now_add=True)

class CommentsReport(models.Model):
    comments = models.ForeignKey(Comments, on_delete=models.CASCADE)
    userprofile = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    date_reported = models.DateField(null=True,auto_now_add=True )

class CommentsPicture(models.Model):
    comments = models.ForeignKey(Comments, on_delete=models.CASCADE)
    comments_picture = models.ImageField(upload_to='comments_img/', height_field=None, width_field=None, max_length=100,blank=True,null = True)

class CommentReply(models.Model):

    author =models.ForeignKey(User_Profile, on_delete=models.CASCADE,related_name='author')
    recipients = models.ManyToManyField(User_Profile, blank = True)
    contents = models.CharField(max_length = 500,null=True, blank=True)
    comment = models.ForeignKey(Comments, on_delete=models.CASCADE,blank=True, null=True)
    likes =  models.IntegerField(default=0)
    user_like = models.ManyToManyField(User_Profile,blank = True,through='CommentReplyLike',related_name='reply_user_like')
    published = models.DateTimeField(auto_now_add=True,null=True)
    hidden = models.BooleanField(default=False)
    reported = models.ManyToManyField(User_Profile,blank = True,through='CommentReplyReport',related_name='reply_reported')
    reported_count = models.IntegerField(default=0)
    stocks = models.ManyToManyField(Stocks,blank = True,)
    def __str__(self):
        return f"ReplyComment from {self.author} about {self.contents}"

    def reply_like_count(self):
        return CommentReplyLike.objects.filter(commentreply=self).count()
    def reply_last_like(self):
        return CommentReplyLike.objects.filter(commentreply=self).last()

class CommentReplyLike(models.Model):
    commentreply = models.ForeignKey(CommentReply, on_delete=models.CASCADE)
    userprofile = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    date_liked = models.DateField(null=True,auto_now_add=True)

class CommentReplyReport(models.Model):
    commentreply = models.ForeignKey(CommentReply, on_delete=models.CASCADE)
    userprofile = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    date_reported = models.DateField(null=True,auto_now_add=True )

class CommentReplyPicture(models.Model):
    commentreply = models.ForeignKey(CommentReply, on_delete=models.CASCADE)
    commentreply_picture = models.ImageField(upload_to='commentreply_img/', height_field=None, width_field=None, max_length=100,blank=True,null = True)

class Archive(models.Model):
    userprofile = models.OneToOneField(User_Profile, on_delete=models.CASCADE,null=True)
    posts = models.ManyToManyField(Post, blank = True,through='PostArchive')
    comments = models.ManyToManyField(Comments, blank = True,through='CommentsArchive')
    commentreply = models.ManyToManyField(CommentReply, blank = True,through='CommentReplyArchive')

class PostArchive(models.Model):
    archive = models.ForeignKey(Archive, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    date_included = models.DateField(null=True,auto_now_add=True )

class CommentsArchive(models.Model):
    archive = models.ForeignKey(Archive, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comments, on_delete=models.CASCADE)
    date_included = models.DateField(null=True,auto_now_add=True )

class CommentReplyArchive(models.Model):
    archive = models.ForeignKey(Archive, on_delete=models.CASCADE)
    reply = models.ForeignKey(CommentReply, on_delete=models.CASCADE)
    date_included = models.DateField(null=True,auto_now_add=True )


class Notification(models.Model):
    userprofile = models.ForeignKey(User_Profile, on_delete=models.CASCADE) #notification belongs to this user
    action_user =  models.ForeignKey(User_Profile, on_delete=models.CASCADE,related_name='action_userprofile') #this user did something to the userpofile
    action_statement = models.CharField(max_length = 500,null=True, blank=True)
    url = models.CharField(max_length = 500,null=True, blank=True)
    checked = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    post_id = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length = 500,null=True, blank=True)
    action = models.CharField(max_length = 500,null=True, blank=True)

# use this in template tag stock.stock_comment.all() returns all stock comments related to stock.
# >>> b = Blog.objects.get(id=1)
# >>> b.entry_set.all() # Returns all Entry objects related to Blog.
#
# # b.entry_set is a Manager that returns QuerySets.
# >>> b.entry_set.filter(headline__contains='Lennon')
# >>> b.entry_set.count()
#b.entry_set.count()

#/////Post ////////////////////
Support_dependents_CHOICES = ( #changing the css with this
    (1,'Yes'),
    (0,'No'),
)

New_investor_CHOICES = ( #changing the css with this
    (1,'Yes'),
    (0,'No'),
)

investing_CHOICES = ( #changing the css with this
    (0,'Having money in case of emergencies'),
    (1,'Earing more from savings'),
    (2,'I just want to grow my money'),
    (3,'Being able to retire comfortably'),
    (4,'Becoming a homeowner'),
    (5,'Financial Independance'),
    (5,'Lifestyle Improvement'),
)


Lifestyle_CHOICES = ( #changing the css with this
    (1,'Yes (Earn More Live More)'),
    (0,'No (Earn More, Save More)'),
)

class FinancialGoals(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) #connecting user to model
    New_investor = models.CharField(choices=New_investor_CHOICES, max_length=1, default=1,null=True, blank=True)
    What_are_you_looking_to_acheive_through_investing=models.CharField(choices=investing_CHOICES, max_length=1, default=3,null=True, blank=True)
    number_of_income_sources =models.IntegerField(null=True, blank=True)
    How_much_income_after_taxex_do_you_want_yearly=models.IntegerField(null=True, blank=True)
    How_much_dividend_income_do_you_expect_to_need_during_retirment = models.IntegerField(null=True, blank=True)
    What_percentage_of_your_income_do_you_save_a_month = models.IntegerField(null=True, blank=True)
    With_more_money_do_you_expect_enhance_your_lifestyle = models.CharField(choices=Lifestyle_CHOICES, max_length=1, default=1,null=True, blank=True)





risk_CHOICES = ( #changing the css with this
    (1,'High'),
    (2,'Medium'),
    (3,'Low'),
)

check_investments_CHOICES = ( #changing the css with this
    (1,'At Least Once a Week'),
    (2,'At Least Once a Month'),
    (3,'At Least Once a Year'),
)

Market_Downturn_CHOICES = ( #changing the css with this
    (1,'Ride it Out'),
    (2,'Get out of the market'),
)

class RiskProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) #connecting user to model
    risk_tolerance = models.CharField(choices=risk_CHOICES, max_length=1, default=1)
    What_age_do_you_want_to_retire = models.IntegerField(default=1)
    How_ofen_do_you_check_your_investment_statements = models.CharField(choices=check_investments_CHOICES, max_length=1, default=1)
    How_likely_are_you_to_pull_out_of_the_market_assuming_a_market_downturn = models.CharField(choices=check_investments_CHOICES, max_length=1, default=1)
