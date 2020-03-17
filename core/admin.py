from django.contrib import admin

# Register your models here.
from .models import (Item, OrderItem, Order,Stocks,
User_Profile,Dividend,StockInfo,Article,
Post,Topic,Comments,GenGroup,GroupMember,CommentReply,
Archive,PostArchive,CommentsArchive,CommentReplyArchive,
PostViewCount,PostReport,PostLike,CommentsReport,
CommentsLike,CommentReplyLike,CommentReplyReport, PostPicture,
CommentsPicture, CommentReplyPicture,
GroupWatchlist,WatchStockDetail,StockWatchlist,
WatchlistDownload, File, GroupFileList, FileDownload,
Notification, DividendWealthMembership,DividendWealthSubscription,
DividendWealthConnectedAccount,DividendWealthConnectedAccountPayments,
GroupCategories,Categories,Credential,UserCredential,UserFinancialRole,
FinancialRole,UserRelationship
)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Stocks)
admin.site.register(User_Profile)
admin.site.register(Dividend)
admin.site.register(StockInfo)
admin.site.register(Article)
admin.site.register(Post)
admin.site.register(Topic)
admin.site.register(Comments)
admin.site.register(GenGroup)
admin.site.register(GroupMember)
admin.site.register(CommentReply)
admin.site.register(Archive)
admin.site.register(PostArchive)
admin.site.register(CommentsArchive)
admin.site.register(CommentReplyArchive)
admin.site.register(PostViewCount)
admin.site.register(PostReport)
admin.site.register(PostLike)
admin.site.register(CommentsReport)
admin.site.register(CommentsLike)
admin.site.register(CommentReplyLike)
admin.site.register(CommentReplyReport)
admin.site.register(PostPicture)
admin.site.register(CommentsPicture)
admin.site.register(CommentReplyPicture)
admin.site.register(GroupWatchlist)
admin.site.register(WatchStockDetail)
admin.site.register(StockWatchlist)
admin.site.register(WatchlistDownload)
admin.site.register(File)
admin.site.register(GroupFileList)
admin.site.register(FileDownload)
admin.site.register(Notification)
admin.site.register(DividendWealthMembership)
admin.site.register(DividendWealthSubscription)
admin.site.register(DividendWealthConnectedAccount)
admin.site.register(DividendWealthConnectedAccountPayments)
admin.site.register(Categories)
admin.site.register(GroupCategories)
admin.site.register(Credential)
admin.site.register(UserCredential)
admin.site.register(UserFinancialRole)
admin.site.register(FinancialRole)
admin.site.register(UserRelationship)
