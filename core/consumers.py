# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import render, get_object_or_404, redirect
import json
from channels.layers import get_channel_layer
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
GroupCategories,Categories,GroupPayment,GroupSubscription,UserRelationship
)
from django.utils import timezone
from datetime import datetime
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
import json
from asgiref.sync import async_to_sync
from datetime import time
from datetime import datetime
import string
from django.core.files.storage import default_storage

#https://channels.readthedocs.io/en/latest/topics/channel_layers.html  bottom of document, how to send to individual channel and group
#To send to a single channel, just find its channel name (for the example above, we could crawl the database), and use channel_layer.send:

#This Consumer is for group page
class GroupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['groupName']
        self.room_name =str(self.room_name)
        self.room_group_name = self.room_name

        #self.room_group_name = 'group_%s' % self.room_name
        #self.room_group_name = 'test'
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print("connected")

        await self.accept()
#section receive data from WebSocket
    #receiving from the html file
    # Receive message from WebSocket
    async def receive(self, text_data):
        print("receive",text_data)
        #front_text = text_data.get('text',None)
        if text_data is not None:
            event = json.loads(text_data)

            #/////Section is for accepting variables to dealing with online group status/////
            # constant variables from the page section
            #variable give online state "1"
            try:
                user_on_group_page = event['user_on_group_page']
            except KeyError:
                event['user_on_group_page'] = 'null'
                user_on_group_page = event['user_on_group_page']
            #variable gives the user which has come to the page
            try:
                user_username = event['user_username']
            except KeyError:
                event['user_username'] = 'null'
                user_username = event['user_username']
            # redundant variable for another function
            self.user_username = event['user_username']


            #/////Section is for accepting variables to change user member status, sent from group creator/////
            #variable used when creator changes the status of the member
            # member status identifier
            try:
                pending_status = event['pending_status']
            except KeyError:
                event['pending_status'] = 'null'
                pending_status = event['pending_status']
            #variable used when creator changes the status of the member
            # respective member identifier
            try:
                pending_member_change_username = event['pending_member_change_username']
            except KeyError:
                event['pending_member_change_username'] = 'null'
                pending_member_change_username = event['pending_member_change_username']

            #///Section is for telling weather user that just logged in is new or not, new member bool
            try:
                new_member = event['new_member']
            except KeyError:
                event['new_member'] = 'null'
                new_member = event['new_member']

            #///Section is for accepting variable that have to deal with post/comment/reply delete archive and report
            try:
                post_comment_reply_action = event['post_comment_reply_action']
            except KeyError:
                event['post_comment_reply_action'] = 'null'
                post_comment_reply_action = event['post_comment_reply_action']
            #///Section is for removing a watchlist from the group
            try:
                stock_watchlist_remove = event['stock_watchlist_remove']
            except KeyError:
                event['stock_watchlist_remove'] = 'null'
                stock_watchlist_remove = event['stock_watchlist_remove']

            #/////Section is for copying a watchlist from a group
            try:
                stock_watchlist_add = event['stock_watchlist_add']
            except KeyError:
                event['stock_watchlist_add'] = 'null'
                stock_watchlist_add = event['stock_watchlist_add']
            #//////Section is for receiving stock slug to update shares in users portfolio
            try:
                stock_slug_update_portfolio = event['stock_slug_update_portfolio']
            except KeyError:
                event['stock_slug_update_portfolio'] = 'null'
                stock_slug_update_portfolio = event['stock_slug_update_portfolio']

            #//////Section is for receiving stock slug to update shares in users file to delete
            try:
                delete_group_file_pk = event['delete_group_file_pk']
            except KeyError:
                event['delete_group_file_pk'] = 'null'
                delete_group_file_pk = event['delete_group_file_pk']

            #//// Section is for getting the time spent on group page
            try:
                group_time_spent = event['group_time_spent']

            except KeyError:
                event['group_time_spent'] = 'null'
                group_time_spent = event['group_time_spent']

            #//// Section is for getting notification url
            try:
                notification_url = event['notification_url']
            except KeyError:
                event['notification_url'] = 'null'
                notification_url = event['notification_url']

            #////Section is for recivinving variable that contains information on if user has check notification modal can be expanded to individual notification
            try:
                notifiation_checked = event['notifiation_checked']
            except KeyError:
                event['notifiation_checked'] = 'null'
                notifiation_checked = event['notifiation_checked']


            #////Section is for recive inving variable that contains information on mention type ex.post,comment_12 and instance
            try:
                post_comment_reply_mention = event['post_comment_reply_mention']
            except KeyError:
                event['post_comment_reply_mention'] = 'null'
                post_comment_reply_mention = event['post_comment_reply_mention']

            #////Section is for reciv inving variable that contains list of users ex.[dnkldn,kjdkls,]
            try:
                list_of_recipients_notifiction = event['list_of_recipients_notifiction']
            except KeyError:
                event['list_of_recipients_notifiction'] = 'null'
                list_of_recipients_notifiction = event['list_of_recipients_notifiction']

            # Section is for reciving data about if user is manually leaving group or not
            try:
                user_leave_manually = event['user_leave_manually']
            except KeyError:
                event['user_leave_manually'] = 'null'
                user_leave_manually = event['user_leave_manually']


            # Section is for sending notification to appropriate page
            try:
                active_url = event['active_url']
            except KeyError:
                event['active_url'] = 'null'
                active_url = event['active_url']

            relationship_response = 'null'
        # Section is for running function on variables received from page

            if active_url != 'null':
                await database_sync_to_async(self.change_user_url)(user_username,active_url)
            # ///Section running group based functions
            #function is for handling action events dealing with post/comment/reply delete archive and report
            #note will need a specific user
            server_reponse_post_comment_reply_action = 'null' #note contains feedback on action done before
            if post_comment_reply_action != 'null':
                server_reponse_post_comment_reply_action=   await database_sync_to_async(self.post_comment_reply_action_fun)(post_comment_reply_action,user_username,notification_url)

            if pending_member_change_username != 'null':
                #//Section to acess data base and change member status based on creator discretion
                await database_sync_to_async(self.change_group_member_status)(pending_member_change_username,pending_status)

            #might want to move the function below to one of the try methods that triggers when user is on the page
            await database_sync_to_async(self.online_status_open)(user_username)

            if stock_watchlist_remove != 'null':
                await database_sync_to_async(self.remove_watchlist_from_group)(stock_watchlist_remove)

            if stock_watchlist_add != 'null':
                await database_sync_to_async(self.copy_watchlist_from_group)(stock_watchlist_add,user_username)

            share_count_update = 'null'
            if stock_slug_update_portfolio != 'null':
                share_count_update = await database_sync_to_async(self.update_shares_user_portfolio)(stock_slug_update_portfolio,user_username)

            if delete_group_file_pk != 'null':
                await database_sync_to_async(self.remove_file_from_group_files)(delete_group_file_pk)

            if group_time_spent != 'null':
                await database_sync_to_async(self.update_group_member_time)(group_time_spent,user_username)

            if notifiation_checked != 'null':
                await database_sync_to_async(self.reset_notification_count)(user_username)

            if list_of_recipients_notifiction != 'null':
                await database_sync_to_async(self.send_mention_notification)(post_comment_reply_mention,notification_url,list_of_recipients_notifiction)
            # Section is for getting information
            new_member_information = 'null'
            if new_member != 'null':
                new_member_information= await database_sync_to_async(self.get_new_member_information)(user_username)

        # Section Send message to room group
            # print('changed user status')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    # sending variables to chat_message function
                    'type': 'chat_message', #note: needs to be a function called chat_message

                    # variables from  online group status section
                    'user_on_group_page': user_on_group_page,
                    'user_username':user_username,

                    # variables from change user member status section
                    'pending_status':pending_status,
                    'pending_member_change_username':pending_member_change_username,

                    #variable from new member boolean section
                    'new_member':new_member,

                    #variables from post comment reply section
                    'post_comment_reply_action':post_comment_reply_action,
                    'server_reponse_post_comment_reply_action':server_reponse_post_comment_reply_action,

                    #section is for telling the client which watchlist was added
                    'stock_watchlist_add':stock_watchlist_add,

                    #section is for updating the useres Shares
                    'share_count_update': share_count_update,
                    'stock_slug_update_portfolio':stock_slug_update_portfolio,

                    # section is for sending new member information
                    'new_member_information':new_member_information,

                    # section if for user manually opting out of group
                    'user_leave_manually':user_leave_manually,

                    }
                )

#end recive section

#section disconnecting websocket
    async def disconnect(self, close_code):
        #Section when user leaves page change online status and group online status
        try:
            closing_user =await database_sync_to_async(self.online_status_close)(self.user_username)
            #await database_sync_to_async(self.Logout_Status)(self.user_username)
            print("Leaving user is ",closing_user)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message', #needs to be a function called chat_message
                    'user_on_group_page': '0',
                    'user_username':closing_user
                    }
                )
        except:
            pass


        # Section Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
#end section



    # Section Receive message from room group
    async def chat_message(self, event):
        #making sure funtion is called
        print("second stage",event)

        #///Section try getting dictionary inputs if you cant find it make it null

        #/////Section is for accepting variables to deal with user logging in and changing online group status/////
        try:
            user_on_group_page = event['user_on_group_page']
        except KeyError:
            event['user_on_group_page'] = 'null'
            user_on_group_page = event['user_on_group_page']
        try:
            user_username = event['user_username']
        except KeyError:
            event['user_username'] = 'null'
            user_username = event['user_username']

        #/////Section is for accepting variables to change user member status, sent from group creator/////
                #variable used when creator changes the status of the member
                # member status identifier
        try:
            pending_status = event['pending_status']
        except KeyError:
            event['pending_status'] = 'null'
            pending_status = event['pending_status']
        #variable used when creator changes the status of the member
        # respective member identifier
        try:
            pending_member_change_username = event['pending_member_change_username']
        except KeyError:
            event['pending_member_change_username'] = 'null'
            pending_member_change_username = event['pending_member_change_username']

        #///Section is for telling weather user that just logged in is new or not, new member bool
        try:
            new_member = event['new_member']
        except KeyError:
            event['new_member'] = 'null'
            new_member = event['new_member']

        #///Section is for accepting variable that have to deal with post/comment/reply delete archive and report
        try:
            post_comment_reply_action = event['post_comment_reply_action']
        except KeyError:
            event['post_comment_reply_action'] = 'null'
            post_comment_reply_action = event['post_comment_reply_action']

        try:
            server_reponse_post_comment_reply_action = event['server_reponse_post_comment_reply_action']
        except KeyError:
            event['server_reponse_post_comment_reply_action'] = 'null'
            server_reponse_post_comment_reply_action = event['server_reponse_post_comment_reply_action']

        #//Section is for accepting post from views and sending it to client
        try:
            view_group_post = event['view_group_post']
        except KeyError:
            event['view_group_post'] = 'null'
            view_group_post = event['view_group_post']

        #//Section is for accepting comment from views and sending it to client
        try:
            view_group_comment = event['view_group_comment']
        except KeyError:
            event['view_group_comment'] = 'null'
            view_group_comment = event['view_group_comment']

        #//Section is for accepting reply from views and sending it to client
        try:
            view_group_reply = event['view_group_reply']
        except KeyError:
            event['view_group_reply'] = 'null'
            view_group_reply = event['view_group_reply']

        #/////Section is for copying a watchlist from a group
        try:
            stock_watchlist_add = event['stock_watchlist_add']
        except KeyError:
            event['stock_watchlist_add'] = 'null'
            stock_watchlist_add = event['stock_watchlist_add']

        #/////Section is for updating share count for stock portfolio
        try:
            share_count_update = event['share_count_update']
        except KeyError:
            event['share_count_update'] = 'null'
            share_count_update = event['share_count_update']

        try:
            stock_slug_update_portfolio = event['stock_slug_update_portfolio']
        except KeyError:
            event['stock_slug_update_portfolio'] = 'null'
            stock_slug_update_portfolio = event['stock_slug_update_portfolio']

        try:
            notification_content = event['notification_content']
            print(notification_content)
        except KeyError:
            event['notification_content'] = 'null'
            notification_content = event['notification_content']
        # ////Section is for sending new_member_information
        try:
            new_member_information = event['new_member_information']
            print(new_member_information)
        except KeyError:
            event['new_member_information'] = 'null'
            new_member_information = event['new_member_information']

        # Section is for reciving data about if user is manually leaving group or not
        try:
            user_leave_manually = event['user_leave_manually']
        except KeyError:
            event['user_leave_manually'] = 'null'
            user_leave_manually = event['user_leave_manually']

        # Section if for user adding a watchlist he already has with the same name

        try:
            user_adds_watchlist_with_same_name = event['user_adds_watchlist_with_same_name']
        except KeyError:
            event['user_adds_watchlist_with_same_name'] = 'null'
            user_adds_watchlist_with_same_name = event['user_adds_watchlist_with_same_name']

        # Section is for getting varialble dealing with the oppening of the ifram
        try:
            zoom_load_iframe = event['zoom_load_iframe']
        except KeyError:
            event['zoom_load_iframe'] = 'null'
            zoom_load_iframe = event['zoom_load_iframe']

        # Section is for getting varialble dealing with closing zoom iframe
        try:
            zoom_close_group_meeting = event['zoom_close_group_meeting']
        except KeyError:
            event['zoom_close_group_meeting'] = 'null'
            zoom_close_group_meeting = event['zoom_close_group_meeting']

        #//section is for group count
        group_count =await database_sync_to_async(self.group_count)()


        #send to the htmlflie
        # Section Send message to WebSocket
        await self.send(text_data=json.dumps({

            # variables from  online group status section
            'user_on_group_page': user_on_group_page,
            'user_username':user_username,

            # variables from change user member status section
            'pending_status':pending_status,
            'pending_member_change_username':pending_member_change_username,

            #variable from new member boolean section
            'new_member':new_member,

            #variable from group count Section
            'group_count':group_count,

            #variable from post comment reply section
            'post_comment_reply_action' :post_comment_reply_action,
            'server_reponse_post_comment_reply_action' :server_reponse_post_comment_reply_action,

            #variable from post VIEWS
            'view_group_post' : view_group_post,

            #variable from comments VIEWS
            'view_group_comment' : view_group_comment,

            #variable from reply VIEWS
            'view_group_reply' : view_group_reply,

            #section is for telling the client which watchlist was added
            'stock_watchlist_add':stock_watchlist_add,

            #section is for updating the users shares
            'share_count_update': share_count_update,
            'stock_slug_update_portfolio': stock_slug_update_portfolio,

            #section is for sending notification content
            'notification_content': notification_content,

            # section is for sending new member information
            'new_member_information': new_member_information,

            # section if for user manually opting out of group
            'user_leave_manually':user_leave_manually,

            # Section if for user adding a watchlist he already has with the same name
            'user_adds_watchlist_with_same_name':user_adds_watchlist_with_same_name,

        # Section is for getting varialble dealing with the oppening of the ifram
            "zoom_load_iframe":zoom_load_iframe,
            
            # Section is for sending information dealing with group closing
            "zoom_close_group_meeting":zoom_close_group_meeting

        }))
        #end chat_message
    def change_user_url(self,user_username,active_url):
        user = User_Profile.objects.filter(user__username=user_username)[0]
        user.active_notification_url = active_url
        user.save()
    #section get the group count
    def group_count (self):
        return str(GroupMember.objects.filter(group__slug=self.room_name,active=True).count())

    #Section to acess data base and change member status based on creator discretion
    def change_group_member_status (self, username,status):
        try:

            print("in close group member status")
            user = User_Profile.objects.filter(user__username=username)[0]
            groupmember = GroupMember.objects.filter(group__slug=self.room_name,userprofile=user)[0]

            if status == "Member":
                status ='m'
                groupmember.member_status = status
                username = user.user.username
                groupmember.save()
                user.save()

            if status == "Moderator":
                status = 'd'
                groupmember.member_status = status
                username = user.user.username
                groupmember.save()
                user.save()

            if status == "Removal":
                # if group Subscription exist turn it to false
                if GroupSubscription.objects.filter(group_member=groupmember,group=groupmember.group).exists():
                    group_sub= GroupSubscription.objects.filter(group_member=groupmember,group=groupmember.group)[0]
                    group_sub.active = False
                    group_sub.save()

                groupmember.active=False
                groupmember.save()

        except:
            pass

    #Section when user leaves the group page we change their group online status
    def online_status_close (self, username):
        try:

            print("in close online status")
            user = User_Profile.objects.filter(user__username=username)[0]
            groupmember = GroupMember.objects.filter(group__slug=self.room_name,userprofile=user)[0]
            user.online_status = 'f'
            groupmember.group_online_status = 'f'
            username = user.user.username
            groupmember.save()
            user.save()

        except:
            username = 'null'
        return username

    #Section when user opens the group page we change their group online status
    def online_status_open (self, username):
        try:

            print("in open online status")
            user = User_Profile.objects.filter(user__username=username)[0]
            groupmember = GroupMember.objects.filter(group__slug=self.room_name,userprofile=user)[0]
            user.online_status = 'o'
            groupmember.group_online_status = 'o'
            username = user.user.username
            groupmember.save()
            user.save()

        except:
            username = 'null'

    #Section is for handling action events dealing with post/comment/reply delete archive and report
    def post_comment_reply_action_fun (self,post_comment_reply_action_arg, username,notification_url):

        action_array = post_comment_reply_action_arg.split("_")
        type = action_array[0]
        action = action_array[1]
        object = action_array[2]
        object = int(object)

        if type == "post":

            if action == "like":
                # check if the post exist.. getpost
                if Post.objects.filter(pk=object).exists():
                    post= Post.objects.filter(pk=object)[0]
                    user = User_Profile.objects.filter(user__username=username)[0]
                    # if the like exists remove like
                    if PostLike.objects.filter(post=post,userprofile__user__username=username).exists():
                        like=PostLike.objects.filter(post=post,userprofile__user__username=username)[0]
                        like.delete()
                        like_count=post.likes
                        post.likes = like_count-1
                        post.save()
                        return "like deleted"
                    else:
                        #create like

                        post.user_like.add(user)
                        like_count=post.likes
                        post.likes = like_count+1
                        post.save()

                        #truncate string
                        post_draft=post.description
                        info = (post_draft[:60] + '...') if len(post_draft) > 60 else post_draft
                        notification_action_statment="liked your post: "+ info
                        if Notification.objects.filter(userprofile=post.author,action_user=user,action_statement=notification_action_statment).exists():
                            pass
                        else:
                            notification_url = notification_url +'#Post'+str(object)
                            note_model= Notification.objects.create(userprofile=post.author,action_user=user,action_statement=notification_action_statment,url=notification_url,type="post",action = "like")
                            user.notification_count = user.notification_count +1
                            user.save()
                            # Section is for sending Async Notification
                            # get the image of the action user
                            if bool(note_model.action_user.profile_pic) != False:
                                action_user_profile_pic =  note_model.action_user.profile_pic.url
                            else:
                                action_user_profile_pic = 'false'

                            now = datetime.now()
                            time_post =now.strftime("%a, %I:%M:%S %p")
                            time_published = time_post

                            channel_layer = get_channel_layer()
                            notification_content =   {
                            'type': 'post',
                            'action': 'like',
                            'userprofile_name':note_model.userprofile.user.username,
                            'action_user': note_model.action_user.user.username,
                            'action_user_profile_pic': action_user_profile_pic,
                            'action_statement': notification_action_statment,
                            'notification_url': notification_url,
                            'notification_pk': note_model.pk,
                            'notification_time': time_published,
                            }
                            notification_content = json.dumps(notification_content)
                            async_to_sync(channel_layer.group_send)(self.room_name, {"type": "chat.message",

                            "notification_content": notification_content,})

                        #notification to the user that someone liked your post
                        return "like added"

            if action == "delete":
                if Post.objects.filter(pk=object).exists():
                    post= Post.objects.filter(pk=object)[0]
                    post.hidden = True
                    post.save()
                    print("worked")
                    return "null"

            if action == "report":
                if Post.objects.filter(pk=object).exists():
                    post= Post.objects.filter(pk=object)[0]
                    # check to see if the current user has reported before
                    if PostReport.objects.filter(post__pk=object,userprofile__user__username=username).exists():
                        # delete report
                        return "Post has all ready been Reported."

                    else:
                        # create a new report
                        user = User_Profile.objects.filter(user__username=username)[0]
                        PostReport.objects.create(post=post,userprofile=user)
                        print("created report")
                        return "null"

            if action == "archive":
                if Post.objects.filter(pk=object).exists():
                    post= Post.objects.filter(pk=object)[0]
                    print("check1")
                    # check to see if the current user has archived post before
                    if PostArchive.objects.filter(post__pk=object,archive__userprofile__user__username=username).exists():
                        # delete archive
                        PostArchive.objects.filter(post__pk=object,archive__userprofile__user__username=username)[0].delete()
                        return "Post Removed From Archive."
                        print("check2")
                    else:
                        print("check3")
                        #check to see if user has an archive
                        user = User_Profile.objects.filter(user__username=username)[0]

                        if Archive.objects.filter(userprofile=user).exists():
                            archive=Archive.objects.filter(userprofile=user)[0]
                            #add create post to archive
                            archive.posts.add(post)
                            print("archived post ")
                            return "null"
                        else:
                            #create archive
                            archive=Archive.objects.create(userprofile=user)
                            #add create post to archive
                            archive.posts.add(post)
                            print("archived post created archive")
                            return "null"

        if type == "comment":

            if action == "like":
                # check if the post exist.. getpost
                print("in comment like")
                if Comments.objects.filter(pk=object).exists():
                    print("in comment like 2")
                    comments= Comments.objects.filter(pk=object)[0]
                    user = User_Profile.objects.filter(user__username=username)[0]
                    # if the like exists remove like
                    if CommentsLike.objects.filter(comments=comments,userprofile__user__username=username).exists():
                        like=CommentsLike.objects.filter(comments=comments,userprofile__user__username=username)[0]
                        like.delete()
                        like_count=comments.likes
                        comments.likes = like_count-1
                        comments.save()
                        return "like deleted"
                    else:
                        #create like

                        comments.user_like.add(user)
                        like_count=comments.likes
                        comments.likes = like_count+1
                        comments.save()

                    #truncate string
                    post_draft=comments.contents
                    info = (post_draft[:60] + '...') if len(post_draft) > 60 else post_draft
                    notification_action_statment="liked your comment: "+ info
                    if Notification.objects.filter(userprofile=comments.author,action_user=user,action_statement=notification_action_statment).exists():
                        pass
                    else:
                        notification_url = notification_url +'#Comment'+str(object)
                        note_model= Notification.objects.create(userprofile=comments.author,action_user=user,action_statement=notification_action_statment,url=notification_url,post_id=comments.post.pk, type="comment",action = "like")
                        user.notification_count = user.notification_count +1
                        user.save()
                        # Section is for sending Async Notification
                        # get the image of the action user
                        if bool(note_model.action_user.profile_pic) != False:
                            action_user_profile_pic =  note_model.action_user.profile_pic.url
                        else:
                            action_user_profile_pic = 'false'

                        now = datetime.now()
                        time_post =now.strftime("%a, %I:%M:%S %p")
                        time_published = time_post

                        channel_layer = get_channel_layer()
                        notification_content =   {
                        'type': 'comment',
                        'action': 'like',
                        'userprofile_name':note_model.userprofile.user.username,
                        'action_user': note_model.action_user.user.username,
                        'action_user_profile_pic': action_user_profile_pic,
                        'action_statement': notification_action_statment,
                        'notification_url': notification_url,
                        'notification_pk': note_model.pk,
                        'notification_time': time_published,
                        'post_pk': comments.post.pk,
                        }
                        notification_content = json.dumps(notification_content)
                        async_to_sync(channel_layer.group_send)(self.room_name, {"type": "chat.message",
                        "notification_content": notification_content,})
                        #notification to the user that someone liked your post
                    return "like added"

            if action == "delete":
                if Comments.objects.filter(pk=object).exists():
                    comments= Comments.objects.filter(pk=object)[0]
                    comments.hidden = True
                    comments.save()
                    print("worked")
                    return "null"

            if action == "report":
                if Comments.objects.filter(pk=object).exists():
                    comments= Comments.objects.filter(pk=object)[0]
                    # check to see if the current user has reported before
                    if CommentsReport.objects.filter(comments__pk=object,userprofile__user__username=username).exists():
                        # delete report
                        return "Comment has all ready been Reported."

                    else:
                        # create a new report
                        user = User_Profile.objects.filter(user__username=username)[0]
                        CommentsReport.objects.create(comments=comments,userprofile=user)
                        print("created report")
                        return "null"

            if action == "archive":
                if Comments.objects.filter(pk=object).exists():
                    comments= Comments.objects.filter(pk=object)[0]
                    print("check1")
                    # check to see if the current user has archived post before
                    if CommentsArchive.objects.filter(comment__pk=object,archive__userprofile__user__username=username).exists():
                        # delete archive
                        CommentsArchive.objects.filter(comment__pk=object,archive__userprofile__user__username=username)[0].delete()
                        return "Comment Removed From Archive."
                        print("check2")
                    else:
                        print("check3")
                        #check to see if user has an archive
                        user = User_Profile.objects.filter(user__username=username)[0]

                        if Archive.objects.filter(userprofile=user).exists():
                            archive=Archive.objects.filter(userprofile=user)[0]
                            #add create post to archive
                            archive.comments.add(comments)
                            print("archived comment ")
                            return "null"
                        else:
                            #create archive
                            archive=Archive.objects.create(userprofile=user)
                            #add create post to archive
                            archive.comments.add(comments)
                            print("archived comment and created archive")
                            return "null"

        if type == "reply":

            if action == "like":
                # check if the post exist.. getpost

                if CommentReply.objects.filter(pk=object).exists():
                    #print("in comment like 2")
                    commentreply= CommentReply.objects.filter(pk=object)[0]
                    user = User_Profile.objects.filter(user__username=username)[0]
                    # if the like exists remove like
                    if CommentReplyLike.objects.filter(commentreply=commentreply,userprofile__user__username=username).exists():
                        like=CommentReplyLike.objects.filter(commentreply=commentreply,userprofile__user__username=username)[0]
                        like.delete()
                        like_count=commentreply.likes
                        commentreply.likes = like_count-1
                        commentreply.save()
                        return "like deleted"
                    else:
                        #create like

                        commentreply.user_like.add(user)
                        like_count=commentreply.likes
                        commentreply.likes = like_count+1
                        commentreply.save()
                        #notification to the user that someone liked your post

                        #truncate string
                        post_draft=commentreply.contents
                        info = (post_draft[:60] + '...') if len(post_draft) > 60 else post_draft
                        notification_action_statment="liked your comment: "+ info
                        if Notification.objects.filter(userprofile=commentreply.author,action_user=user,action_statement=notification_action_statment).exists():
                            pass
                        else:
                            notification_url = notification_url +'#Reply'+str(object)
                            note_model= Notification.objects.create(userprofile=commentreply.author,action_user=user,action_statement=notification_action_statment,url=notification_url,post_id=commentreply.comment.post.pk, type="reply",action = "like")
                            user.notification_count = user.notification_count +1
                            user.save()
                            # Section is for sending Async Notification
                            # get the image of the action user
                            if bool(note_model.action_user.profile_pic) != False:
                                action_user_profile_pic =  note_model.action_user.profile_pic.url
                            else:
                                action_user_profile_pic = 'false'

                            now = datetime.now()
                            time_post =now.strftime("%a, %I:%M:%S %p")
                            time_published = time_post

                            channel_layer = get_channel_layer()
                            notification_content =   {
                            'type': 'reply',
                            'action': 'like',
                            'userprofile_name':note_model.userprofile.user.username,
                            'action_user': note_model.action_user.user.username,
                            'action_user_profile_pic': action_user_profile_pic,
                            'action_statement': notification_action_statment,
                            'notification_url': notification_url,
                            'notification_pk': note_model.pk,
                            'notification_time': time_published,
                            'post_pk': commentreply.comment.post.pk,
                            }
                            notification_content = json.dumps(notification_content)
                            async_to_sync(channel_layer.group_send)(self.room_name, {"type": "chat.message",
                            "notification_content": notification_content,})

                        return "like added"

            if action == "delete":
                if CommentReply.objects.filter(pk=object).exists():
                    commentreply= CommentReply.objects.filter(pk=object)[0]
                    commentreply.hidden = True
                    commentreply.save()
                    print("worked")
                    return "null"

            if action == "report":
                if CommentReply.objects.filter(pk=object).exists():
                    commentreply= CommentReply.objects.filter(pk=object)[0]
                    # check to see if the current user has reported before
                    if CommentReplyReport.objects.filter(commentreply__pk=object,userprofile__user__username=username).exists():
                        # delete report
                        return "Comment has all ready been Reported."

                    else:
                        # create a new report
                        user = User_Profile.objects.filter(user__username=username)[0]
                        CommentReplyReport.objects.create(commentreply=commentreply,userprofile=user)
                        print("created report")
                        return "null"

            if action == "archive":
                if CommentReply.objects.filter(pk=object).exists():
                    commentreply= CommentReply.objects.filter(pk=object)[0]
                    print("check1")
                    # check to see if the current user has archived post before
                    if CommentReplyArchive.objects.filter(reply__pk=object,archive__userprofile__user__username=username).exists():
                        # delete archive
                        CommentReplyArchive.objects.filter(reply__pk=object,archive__userprofile__user__username=username)[0].delete()
                        return "Comment Removed From Archive."
                        print("check2")
                    else:
                        print("check3")
                        #check to see if user has an archive
                        user = User_Profile.objects.filter(user__username=username)[0]

                        if Archive.objects.filter(userprofile=user).exists():
                            archive=Archive.objects.filter(userprofile=user)[0]
                            #add create post to archive
                            archive.commentreply.add(commentreply)
                            print("archived comment ")
                            return "null"
                        else:
                            #create archive
                            archive=Archive.objects.create(userprofile=user)
                            #add create post to archive
                            archive.commentreply.add(commentreply)
                            print("archived comment and created archive")
                            return "null"
    #Section is for handling the removal of a watchlist from group
    def remove_watchlist_from_group (self,watchlist_pk):
        group = GenGroup.objects.filter(slug=self.room_name)[0]
        pk =int(watchlist_pk)
        #print(pk)
        list=StockWatchlist.objects.filter(pk=pk)[0]
        if GroupWatchlist.objects.filter(stockwatchlist=list,group=group ).exists():
            instance =GroupWatchlist.objects.filter(stockwatchlist=list,group=group)
            instance.delete()

    #Section if for copying a given watchlist and making the same watchlist for the user
    def copy_watchlist_from_group (self,watchlist_pk,username):
        user = User_Profile.objects.filter(user__username=username)[0]
        pk =int(watchlist_pk)
        #print(pk)
        list=StockWatchlist.objects.filter(pk=pk)[0]


        # get list of watchlist user has
        list_of_user_watchlist = StockWatchlist.objects.filter(creator=user)
        # check if the name of the watchlist already exists
        for user_list in list_of_user_watchlist:
            if user_list.title.lower() == list.title.lower():
                print("true")
                channel_layer = get_channel_layer()
                user_adds_watchlist_with_same_name =   {
                'true':'true'
                }
                user_adds_watchlist_with_same_name = json.dumps(user_adds_watchlist_with_same_name)
                async_to_sync(channel_layer.group_send)(self.room_name, {"type": "chat.message",
                "user_adds_watchlist_with_same_name": user_adds_watchlist_with_same_name,
                })
                return
        #add user to the people that have downloaded the watchlist
        if WatchlistDownload.objects.filter(watchlist=list,downloader=user).exists():
            x=1
            print("already downloaded it")
        else:
             list.downloader.add(user)
             #increment the number of downloads for the watchlist
             num=list.downloaded +1
             list.downloaded = num
        list.save()

        #copy stocks into the new watchlist
        copy_watchlist =StockWatchlist.objects.create(creator=user,title=list.title,description=list.description,added=True,checked=False)
        model_instances = WatchStockDetail.objects.filter(watchlist=list)
        for item in model_instances:
            copy_watchlist.stocks.add(item.stock)
        copy_watchlist.save()

        print("copied stocklist")

        notification_action_statment="Copied your watchlist: "+ string.capwords(list.title)
        if Notification.objects.filter(userprofile=list.creator,action_user=user,action_statement=notification_action_statment).exists():
            pass
        else:
            notification_url = '#'
            note_model= Notification.objects.create(userprofile=list.creator,action_user=user,action_statement=notification_action_statment,url=notification_url,type="post",action = "watchlist")
            user.notification_count = user.notification_count +1
            user.save()
            # Section is for sending Async Notification
            # get the image of the action user
            if bool(note_model.action_user.profile_pic) != False:
                action_user_profile_pic =  note_model.action_user.profile_pic.url
            else:
                action_user_profile_pic = 'false'

            now = datetime.now()
            time_post =now.strftime("%a, %I:%M:%S %p")
            time_published = time_post

            channel_layer = get_channel_layer()
            notification_content =   {
            'type': 'post',
            'action': 'watchlist',
            'userprofile_name':note_model.userprofile.user.username,
            'action_user': note_model.action_user.user.username,
            'action_user_profile_pic': action_user_profile_pic,
            'action_statement': notification_action_statment,
            'notification_url': notification_url,
            'notification_pk': note_model.pk,
            'notification_time': time_published,
            }
            notification_content = json.dumps(notification_content)
            async_to_sync(channel_layer.group_send)(self.room_name, {"type": "chat.message",
            "notification_content": notification_content,})

    #Section is for updating the shares of the user's portfolio
    def update_shares_user_portfolio (self,stock_slug,username):
        user = User_Profile.objects.filter(user__username=username)[0]
        stockinfo = StockInfo.objects.filter(stock__slug=stock_slug,userprofile=user)[0]
        return str(stockinfo.quantity)

    #Section is for removing file from a group
    def remove_file_from_group_files (self, delete_group_file_pk):
        delete_group_file_pk = int(delete_group_file_pk)
        group_file = GroupFileList.objects.filter(pk=delete_group_file_pk)[0]
        current_file = group_file.file
        path = current_file.upload.path
        default_storage.delete(path)
        group_file.delete()
        current_file.delete()

    #Section is for updating user time in group
    def update_group_member_time (self,group_time_spent,username):
        user = User_Profile.objects.filter(user__username=username)[0]
        member = GroupMember.objects.filter(group__slug=self.room_name,userprofile=user)[0]
        then=member.joined
        this_moment=timezone.now()
        time_since_joining_group=this_moment- then
        member.timespent_in_group += (int(group_time_spent)/1000)
        # print("session time",int(group_time_spent[0])/1000)
        # print("time since joining group",time_since_joining_group.total_seconds())
        # print("time spent int group",member.timespent_in_group)
        percentage_of_time_meber_in_group=member.timespent_in_group/time_since_joining_group.total_seconds()
        # print("percentage of time in group",percentage_of_time_meber_in_group)
        percentage_of_time_meber_in_group=percentage_of_time_meber_in_group*100
        percentage_of_time_meber_in_group="{:.0f}".format(percentage_of_time_meber_in_group)
        print("percentage value",percentage_of_time_meber_in_group)
        member.in_group_time = percentage_of_time_meber_in_group
        member.save()

    def reset_notification_count (self,username):
        user = User_Profile.objects.filter(user__username=username)[0]
        user.notification_count = 0
        user.save()

    #Section is for notifiying users that they have been mentioned
    def send_mention_notification (self,post_comment_reply_mention,notification_url,list_of_recipients_notifiction):

        action_array = post_comment_reply_mention.split("_")
        type = action_array[0]
        object = action_array[1]
        object = int(object)

        if type == 'post':
            if Post.objects.filter(pk=object).exists():
                post= Post.objects.filter(pk=object)[0]

                for person in list_of_recipients_notifiction:
                    user = User_Profile.objects.filter(user__username=person)[0]
                    #truncate string
                    post_draft=post.description
                    info = (post_draft[:60] + '...') if len(post_draft) > 60 else post_draft
                    notification_action_statment="mentioned you : "+ info
                    if Notification.objects.filter(userprofile=user,action_user=post.author,action_statement=notification_action_statment).exists():
                        pass
                    else:
                        notification_url = notification_url +'#Post'+str(object)
                        note_model= Notification.objects.create(userprofile=user,action_user=post.author,action_statement=notification_action_statment,url=notification_url,type="post",action = "mention")
                        user.notification_count = user.notification_count +1
                        user.save()
                        # Section is for sending Async Notification
                        # get the image of the action user
                        if bool(note_model.action_user.profile_pic) != False:
                            action_user_profile_pic =  note_model.action_user.profile_pic.url
                        else:
                            action_user_profile_pic = 'false'

                        now = datetime.now()
                        time_post =now.strftime("%a, %I:%M:%S %p")
                        time_published = time_post

                        channel_layer = get_channel_layer()
                        notification_content =   {
                        'type': 'post',
                        'action': 'mention',
                        'userprofile_name':note_model.userprofile.user.username,
                        'action_user': note_model.action_user.user.username,
                        'action_user_profile_pic': action_user_profile_pic,
                        'action_statement': notification_action_statment,
                        'notification_url': notification_url,
                        'notification_pk': note_model.pk,
                        'notification_time': time_published,
                        }
                        notification_content = json.dumps(notification_content)
                        async_to_sync(channel_layer.group_send)(self.room_name, {"type": "chat.message",

                        "notification_content": notification_content,})

        if type=='comment':
            if Comments.objects.filter(pk=object).exists():
                comments= Comments.objects.filter(pk=object)[0]

                for person in list_of_recipients_notifiction:
                    user = User_Profile.objects.filter(user__username=person)[0]
                    #truncate string
                    post_draft=comments.contents
                    info = (post_draft[:60] + '...') if len(post_draft) > 60 else post_draft
                    notification_action_statment="mentioned you : "+ info
                    if Notification.objects.filter(userprofile=user,action_user=comments.author,action_statement=notification_action_statment).exists():
                        pass
                    else:
                        notification_url = notification_url +'#Comment'+str(object)
                        note_model= Notification.objects.create(userprofile=user,action_user=comments.author,action_statement=notification_action_statment,url=notification_url,post_id=comments.post.pk, type="comment",action = "mention")
                        user.notification_count = user.notification_count +1
                        user.save()
                        # Section is for sending Async Notification
                        # get the image of the action user
                        if bool(note_model.action_user.profile_pic) != False:
                            action_user_profile_pic =  note_model.action_user.profile_pic.url
                        else:
                            action_user_profile_pic = 'false'

                        now = datetime.now()
                        time_post =now.strftime("%a, %I:%M:%S %p")
                        time_published = time_post

                        channel_layer = get_channel_layer()
                        notification_content =   {
                        'type': 'comment',
                        'action': 'mention',
                        'userprofile_name':note_model.userprofile.user.username,
                        'action_user': note_model.action_user.user.username,
                        'action_user_profile_pic': action_user_profile_pic,
                        'action_statement': notification_action_statment,
                        'notification_url': notification_url,
                        'notification_pk': note_model.pk,
                        'notification_time': time_published,
                        'post_pk': comments.post.pk,
                        }
                        notification_content = json.dumps(notification_content)
                        async_to_sync(channel_layer.group_send)(self.room_name, {"type": "chat.message",
                        "notification_content": notification_content,})

        if type == 'reply':
            if CommentReply.objects.filter(pk=object).exists():
                commentreply= CommentReply.objects.filter(pk=object)[0]
                for person in list_of_recipients_notifiction:
                    user = User_Profile.objects.filter(user__username=person)[0]
                    #truncate string
                    post_draft=commentreply.contents
                    info = (post_draft[:60] + '...') if len(post_draft) > 60 else post_draft
                    notification_action_statment="mentioned you : "+ info
                    if Notification.objects.filter(userprofile=user,action_user=commentreply.author,action_statement=notification_action_statment).exists():
                        pass
                    else:
                        notification_url = notification_url +'#Reply'+str(object)
                        note_model= Notification.objects.create(userprofile=user,action_user=commentreply.author,action_statement=notification_action_statment,url=notification_url,post_id=commentreply.comment.post.pk, type="reply",action = "mention")
                        user.notification_count = user.notification_count +1
                        user.save()
                        # Section is for sending Async Notification
                        # get the image of the action user
                        if bool(note_model.action_user.profile_pic) != False:
                            action_user_profile_pic =  note_model.action_user.profile_pic.url
                        else:
                            action_user_profile_pic = 'false'

                        now = datetime.now()
                        time_post =now.strftime("%a, %I:%M:%S %p")
                        time_published = time_post

                        channel_layer = get_channel_layer()
                        notification_content =   {
                        'type': 'reply',
                        'action': 'mention',
                        'userprofile_name':note_model.userprofile.user.username,
                        'action_user': note_model.action_user.user.username,
                        'action_user_profile_pic': action_user_profile_pic,
                        'action_statement': notification_action_statment,
                        'notification_url': notification_url,
                        'notification_pk': note_model.pk,
                        'notification_time': time_published,
                        'post_pk': commentreply.comment.post.pk,
                        }
                        notification_content = json.dumps(notification_content)
                        async_to_sync(channel_layer.group_send)(self.room_name, {"type": "chat.message",
                        "notification_content": notification_content,})

        if type == 'alert':
            if Post.objects.filter(pk=object).exists():
                post= Post.objects.filter(pk=object)[0]
                alert_members=GroupMember.objects.filter(group__slug=self.room_name)
                group = GenGroup.objects.filter(slug=self.room_name)[0]
                groupname= string.capwords(group.title)
                for person in alert_members:
                    user = person.userprofile
                    #truncate string
                    post_draft=post.description
                    info = (post_draft[:60] + '...') if len(post_draft) > 60 else post_draft
                    notification_action_statment=groupname + " Group Alert: "+ info
                    if Notification.objects.filter(userprofile=user,action_user=post.author,action_statement=notification_action_statment).exists():
                        pass
                    else:
                        notification_url = notification_url +'#Post'+str(object)
                        note_model= Notification.objects.create(userprofile=user,action_user=post.author,action_statement=notification_action_statment,url=notification_url,type="post",action = "alert")
                        user.notification_count = user.notification_count +1
                        user.save()
                        # Section is for sending Async Notification
                        # get the image of the action user
                        if bool(note_model.action_user.profile_pic) != False:
                            action_user_profile_pic =  note_model.action_user.profile_pic.url
                        else:
                            action_user_profile_pic = 'false'

                        now = datetime.now()
                        time_post =now.strftime("%a, %I:%M:%S %p")
                        time_published = time_post

                        channel_layer = get_channel_layer()
                        notification_content =   {
                        'type': 'post',
                        'action': 'alert',
                        'userprofile_name':note_model.userprofile.user.username,
                        'action_user': note_model.action_user.user.username,
                        'action_user_profile_pic': action_user_profile_pic,
                        'action_statement': notification_action_statment,
                        'notification_url': notification_url,
                        'notification_pk': note_model.pk,
                        'notification_time': time_published,
                        }
                        notification_content = json.dumps(notification_content)
                        async_to_sync(channel_layer.group_send)(self.room_name, {"type": "chat.message",

                        "notification_content": notification_content,})

    def get_new_member_information (self,username):
        user = User_Profile.objects.filter(user__username=username)[0]
        # get user profile pic
        if bool(user.profile_pic) != False:
            user_profile_pic_url =  user.profile_pic.url
        else:
            user_profile_pic_url = 'false'

        # user discription
        member_information = {
            "user_profile_pic_url":user_profile_pic_url,
        }
        member_information = json.dumps(member_information)
        # user url
        return member_information
class TestConsumer(AsyncWebsocketConsumer):
    #note another way to keep track of logged users
    #grab model keeping tack of users increment model by 1
    async def connect(self):
        self.room_name = 'melle'
        self.room_group_name = 'chat_%s' % self.room_name
        #create model instance to keep track of user in group... so add user to model group keeping track of users on page
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        #grab model keeping track of user decrement by one
        #remove the user from the group
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "test",
            {
                'type': 'chat_message', #needs to be a function called chat_message
                'test': 'user out',
                'open': 'subtract user',
                }
            )
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    #receiving from the html file
    # Receive message from WebSocket
    async def receive(self, text_data):
        print("first stage",text_data)
        #front_text = text_data.get('text',None)
        if text_data is not None:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']

            #one time message per session for keeping count of users
            try:
                open = text_data_json['open']
            except KeyError:
                text_data_json['open'] = ''
                open = text_data_json['open']


        # Send message to room group'
            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                "test",
                {
                    'type': 'chat_message', #needs to be a function called chat_message
                    'test': message,
                    'open': open
                    }
                )
    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        #sending to the htmlflie
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
class FeedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['feed']
        self.room_name =str(self.room_name)
        self.room_group_name = self.room_name

        #self.room_group_name = 'group_%s' % self.room_name
        #self.room_group_name = 'test'
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print("connected")

        await self.accept()
#section receive data from WebSocket
    #receiving from the html file
    # Receive message from WebSocket
    async def receive(self, text_data):
        print("receive",text_data)
        #front_text = text_data.get('text',None)
        if text_data is not None:
            event = json.loads(text_data)

            #/////Section is for accepting variables to dealing with online group status/////
            # constant variables from the page section
            #variable give online state "1"
            if True:
                # Section is for getting user on page
                try:
                    user_username = event['user_username']
                except KeyError:
                    event['user_username'] = 'null'
                    user_username = event['user_username']

                try:
                    username = event['user_username']
                except KeyError:
                    event['user_username'] = 'null'
                    username = event['user_username']

                    # Section is for getting the user to follow
                try:
                    user_to_follow = event['user_to_follow']
                except KeyError:
                    event['user_to_follow'] = 'null'
                    user_to_follow = event['user_to_follow']

                try:
                    notifiation_checked = event['notifiation_checked']
                except KeyError:
                    event['notifiation_checked'] = 'null'
                    notifiation_checked = event['notifiation_checked']
                # Section is for getting the url for notifications to be sent to
                try:
                    active_url = event['active_url']
                except KeyError:
                    event['active_url'] = 'null'
                    active_url = event['active_url']

                relationship_response = 'null'
            # Section is for running function on variables received from page
            if True:
                print(user_to_follow)
                if notifiation_checked != 'null':
                    await database_sync_to_async(self.reset_notification_count)(user_username)

                if user_to_follow != 'null':
                    relationship_response= await database_sync_to_async(self.create_user_relationship)(user_username,user_to_follow)

                if active_url != 'null':
                    await database_sync_to_async(self.change_user_url)(user_username,active_url)

        # Section Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    # sending variables to chat_message function
                    'type': 'chat_message', #note: needs to be a function called chat_message

                    'username':username,

                    'user_to_follow':user_to_follow,

                    'relationship_response':relationship_response

                    }
                )

#end recive section

#section disconnecting websocket
    async def disconnect(self, close_code):
        #Section when user leaves page change online status and group online status
        try:
            closing_user = await database_sync_to_async(self.online_status_close)(self.user_username)
            #await database_sync_to_async(self.Logout_Status)(self.user_username)
            print("Leaving user is ",closing_user)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message', #needs to be a function called chat_message
                    'user_on_group_page': '0',
                    'user_username':closing_user
                    }
                )
        except:
            pass


        # Section Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
#end section

    # Section Receive message from room group
    async def chat_message(self, event):
        #making sure funtion is called
        print("second stage",event)

        #///Section try getting dictionary inputs if you cant find it make it null

        #/////Section is for accepting variables to deal with user logging in and changing online group status/////
        try:
            user_username = event['user_username']
        except KeyError:
            event['user_username'] = 'null'
            user_username = event['user_username']
        try:
            user_to_follow = event['user_to_follow']
        except KeyError:
            event['user_to_follow'] = 'null'
            user_to_follow = event['user_to_follow']

        try:
            notification_content = event['notification_content']
        except KeyError:
            event['notification_content'] = 'null'
            notification_content = event['notification_content']

        try:
            relationship_response = event['relationship_response']
        except KeyError:
            event['relationship_response'] = 'null'
            relationship_response = event['relationship_response']



        #send to the htmlflie
        # Section Send message to WebSocket
        await self.send(text_data=json.dumps({
            # variables from  online group status section
            'user_username':user_username,

            # variables from change user member status section
            'user_to_follow':user_to_follow,

            #section is for sending notification content
            'notification_content': notification_content,
            # section is for sending relationship reponse back to the user that initiated
            'relationship_response': relationship_response,

        }))
        #end chat_message
    def change_user_url(self,user_username,active_url):
        user = User_Profile.objects.filter(user__username=user_username)[0]
        user.active_notification_url = active_url
        user.save()


    def create_user_relationship(self,username,user_to_follow):
        print("in create user relationship")
        current_user = User_Profile.objects.filter(user__username=username)[0]
        user = current_user
        user_to_follow = User_Profile.objects.filter(user__username=user_to_follow)[0]
        # delete user relationship if it exist
        if UserRelationship.objects.filter(following=user_to_follow,follower=current_user).exists():
            UserRelationship.objects.filter(following=user_to_follow,follower=current_user)[0].delete()
            follow_status = "unfollowing user"
        else:
            UserRelationship.objects.create(following=user_to_follow,follower=current_user)
            follow_status = "following user"
            # create notification
            notification_action_statment = "followed you"
            if Notification.objects.filter(userprofile=user_to_follow,action_user=current_user,action_statement=notification_action_statment).exists():
                pass
            else:
                notification_url = "#userurl"
                note_model= Notification.objects.create(userprofile=user_to_follow,action_user=current_user,action_statement=notification_action_statment,url=notification_url,type="follow",action = "follow")
                user_to_follow.notification_count = user_to_follow.notification_count +1
                user_to_follow.save()
                # Section is for sending Async Notification
                # get the image of the action user
                if bool(note_model.action_user.profile_pic) != False:
                    action_user_profile_pic =  note_model.action_user.profile_pic.url
                else:
                    action_user_profile_pic = 'false'

                # replace with timzone on client side
                now = datetime.now()
                time_post =now.strftime("%a, %I:%M:%S %p")
                time_published = time_post

                channel_layer = get_channel_layer()
                notification_content =   {
                'type': 'follow',
                'action': 'follow',
                'userprofile_name':note_model.userprofile.user.username,
                'action_user': note_model.action_user.user.username,
                'action_user_profile_pic': action_user_profile_pic,
                'action_statement': notification_action_statment,
                'notification_url': notification_url,
                'notification_pk': note_model.pk,
                'notification_time': time_published,
                }
                notification_content = json.dumps(notification_content)
                async_to_sync(channel_layer.group_send)(user_to_follow.active_notification_url, {"type": "chat.message",

                "notification_content": notification_content,})
        return {
        "follow_status":follow_status,
        "user_name_of_person_initiating":username
        }
    #Section when user leaves the group page we change their group online status
    def online_status_close (self, username):
        try:

            print("in close online status")
            user = User_Profile.objects.filter(user__username=username)[0]
            groupmember = GroupMember.objects.filter(group__slug=self.room_name,userprofile=user)[0]
            user.online_status = 'f'
            groupmember.group_online_status = 'f'
            username = user.user.username
            groupmember.save()
            user.save()

        except:
            username = 'null'
        return username

    #Section when user opens the group page we change their group online status
    def online_status_open (self, username):
        try:

            print("in open online status")
            user = User_Profile.objects.filter(user__username=username)[0]
            groupmember = GroupMember.objects.filter(group__slug=self.room_name,userprofile=user)[0]
            user.online_status = 'o'
            groupmember.group_online_status = 'o'
            username = user.user.username
            groupmember.save()
            user.save()

        except:
            username = 'null'

    #Section is for updating user time in group
    def update_group_member_time (self,group_time_spent,username):
        user = User_Profile.objects.filter(user__username=username)[0]
        member = GroupMember.objects.filter(group__slug=self.room_name,userprofile=user)[0]
        then=member.joined
        this_moment=timezone.now()
        time_since_joining_group=this_moment- then
        member.timespent_in_group += (int(group_time_spent)/1000)
        # print("session time",int(group_time_spent[0])/1000)
        # print("time since joining group",time_since_joining_group.total_seconds())
        # print("time spent int group",member.timespent_in_group)
        percentage_of_time_meber_in_group=member.timespent_in_group/time_since_joining_group.total_seconds()
        # print("percentage of time in group",percentage_of_time_meber_in_group)
        percentage_of_time_meber_in_group=percentage_of_time_meber_in_group*100
        percentage_of_time_meber_in_group="{:.0f}".format(percentage_of_time_meber_in_group)
        print("percentage value",percentage_of_time_meber_in_group)
        member.in_group_time = percentage_of_time_meber_in_group
        member.save()

    def reset_notification_count (self,username):
        user = User_Profile.objects.filter(user__username=username)[0]
        user.notification_count = 0
        user.save()

    #Section is for notifiying users that they have been mentioned
    def send_mention_notification (self,post_comment_reply_mention,notification_url,list_of_recipients_notifiction):

        action_array = post_comment_reply_mention.split("_")
        type = action_array[0]
        object = action_array[1]
        object = int(object)

        if type == 'post':
            if Post.objects.filter(pk=object).exists():
                post= Post.objects.filter(pk=object)[0]

                for person in list_of_recipients_notifiction:
                    user = User_Profile.objects.filter(user__username=person)[0]
                    #truncate string
                    post_draft=post.description
                    info = (post_draft[:60] + '...') if len(post_draft) > 60 else post_draft
                    notification_action_statment="mentioned you : "+ info
                    if Notification.objects.filter(userprofile=user,action_user=post.author,action_statement=notification_action_statment).exists():
                        pass
                    else:
                        notification_url = notification_url +'#Post'+str(object)
                        note_model= Notification.objects.create(userprofile=user,action_user=post.author,action_statement=notification_action_statment,url=notification_url,type="post",action = "mention")
                        user.notification_count = user.notification_count +1
                        user.save()
                        # Section is for sending Async Notification
                        # get the image of the action user
                        if bool(note_model.action_user.profile_pic) != False:
                            action_user_profile_pic =  note_model.action_user.profile_pic.url
                        else:
                            action_user_profile_pic = 'false'

                        now = datetime.now()
                        time_post =now.strftime("%a, %I:%M:%S %p")
                        time_published = time_post

                        channel_layer = get_channel_layer()
                        notification_content =   {
                        'type': 'post',
                        'action': 'mention',
                        'userprofile_name':note_model.userprofile.user.username,
                        'action_user': note_model.action_user.user.username,
                        'action_user_profile_pic': action_user_profile_pic,
                        'action_statement': notification_action_statment,
                        'notification_url': notification_url,
                        'notification_pk': note_model.pk,
                        'notification_time': time_published,
                        }
                        notification_content = json.dumps(notification_content)
                        async_to_sync(channel_layer.group_send)(self.room_name, {"type": "chat.message",

                        "notification_content": notification_content,})

        if type=='comment':
            if Comments.objects.filter(pk=object).exists():
                comments= Comments.objects.filter(pk=object)[0]

                for person in list_of_recipients_notifiction:
                    user = User_Profile.objects.filter(user__username=person)[0]
                    #truncate string
                    post_draft=comments.contents
                    info = (post_draft[:60] + '...') if len(post_draft) > 60 else post_draft
                    notification_action_statment="mentioned you : "+ info
                    if Notification.objects.filter(userprofile=user,action_user=comments.author,action_statement=notification_action_statment).exists():
                        pass
                    else:
                        notification_url = notification_url +'#Comment'+str(object)
                        note_model= Notification.objects.create(userprofile=user,action_user=comments.author,action_statement=notification_action_statment,url=notification_url,post_id=comments.post.pk, type="comment",action = "mention")
                        user.notification_count = user.notification_count +1
                        user.save()
                        # Section is for sending Async Notification
                        # get the image of the action user
                        if bool(note_model.action_user.profile_pic) != False:
                            action_user_profile_pic =  note_model.action_user.profile_pic.url
                        else:
                            action_user_profile_pic = 'false'

                        now = datetime.now()
                        time_post =now.strftime("%a, %I:%M:%S %p")
                        time_published = time_post

                        channel_layer = get_channel_layer()
                        notification_content =   {
                        'type': 'comment',
                        'action': 'mention',
                        'userprofile_name':note_model.userprofile.user.username,
                        'action_user': note_model.action_user.user.username,
                        'action_user_profile_pic': action_user_profile_pic,
                        'action_statement': notification_action_statment,
                        'notification_url': notification_url,
                        'notification_pk': note_model.pk,
                        'notification_time': time_published,
                        'post_pk': comments.post.pk,
                        }
                        notification_content = json.dumps(notification_content)
                        async_to_sync(channel_layer.group_send)(self.room_name, {"type": "chat.message",
                        "notification_content": notification_content,})

        if type == 'reply':
            if CommentReply.objects.filter(pk=object).exists():
                commentreply= CommentReply.objects.filter(pk=object)[0]
                for person in list_of_recipients_notifiction:
                    user = User_Profile.objects.filter(user__username=person)[0]
                    #truncate string
                    post_draft=commentreply.contents
                    info = (post_draft[:60] + '...') if len(post_draft) > 60 else post_draft
                    notification_action_statment="mentioned you : "+ info
                    if Notification.objects.filter(userprofile=user,action_user=commentreply.author,action_statement=notification_action_statment).exists():
                        pass
                    else:
                        notification_url = notification_url +'#Reply'+str(object)
                        note_model= Notification.objects.create(userprofile=user,action_user=commentreply.author,action_statement=notification_action_statment,url=notification_url,post_id=commentreply.comment.post.pk, type="reply",action = "mention")
                        user.notification_count = user.notification_count +1
                        user.save()
                        # Section is for sending Async Notification
                        # get the image of the action user
                        if bool(note_model.action_user.profile_pic) != False:
                            action_user_profile_pic =  note_model.action_user.profile_pic.url
                        else:
                            action_user_profile_pic = 'false'

                        now = datetime.now()
                        time_post =now.strftime("%a, %I:%M:%S %p")
                        time_published = time_post

                        channel_layer = get_channel_layer()
                        notification_content =   {
                        'type': 'reply',
                        'action': 'mention',
                        'userprofile_name':note_model.userprofile.user.username,
                        'action_user': note_model.action_user.user.username,
                        'action_user_profile_pic': action_user_profile_pic,
                        'action_statement': notification_action_statment,
                        'notification_url': notification_url,
                        'notification_pk': note_model.pk,
                        'notification_time': time_published,
                        'post_pk': commentreply.comment.post.pk,
                        }
                        notification_content = json.dumps(notification_content)
                        async_to_sync(channel_layer.group_send)(self.room_name, {"type": "chat.message",
                        "notification_content": notification_content,})

        if type == 'alert':
            if Post.objects.filter(pk=object).exists():
                post= Post.objects.filter(pk=object)[0]
                alert_members=GroupMember.objects.filter(group__slug=self.room_name)
                group = GenGroup.objects.filter(slug=self.room_name)[0]
                groupname= string.capwords(group.title)
                for person in alert_members:
                    user = person.userprofile
                    #truncate string
                    post_draft=post.description
                    info = (post_draft[:60] + '...') if len(post_draft) > 60 else post_draft
                    notification_action_statment=groupname + " Group Alert: "+ info
                    if Notification.objects.filter(userprofile=user,action_user=post.author,action_statement=notification_action_statment).exists():
                        pass
                    else:
                        notification_url = notification_url +'#Post'+str(object)
                        note_model= Notification.objects.create(userprofile=user,action_user=post.author,action_statement=notification_action_statment,url=notification_url,type="post",action = "alert")
                        user.notification_count = user.notification_count +1
                        user.save()
                        # Section is for sending Async Notification
                        # get the image of the action user
                        if bool(note_model.action_user.profile_pic) != False:
                            action_user_profile_pic =  note_model.action_user.profile_pic.url
                        else:
                            action_user_profile_pic = 'false'

                        now = datetime.now()
                        time_post =now.strftime("%a, %I:%M:%S %p")
                        time_published = time_post

                        channel_layer = get_channel_layer()
                        notification_content =   {
                        'type': 'post',
                        'action': 'alert',
                        'userprofile_name':note_model.userprofile.user.username,
                        'action_user': note_model.action_user.user.username,
                        'action_user_profile_pic': action_user_profile_pic,
                        'action_statement': notification_action_statment,
                        'notification_url': notification_url,
                        'notification_pk': note_model.pk,
                        'notification_time': time_published,
                        }
                        notification_content = json.dumps(notification_content)
                        async_to_sync(channel_layer.group_send)(self.room_name, {"type": "chat.message",

                        "notification_content": notification_content,})
