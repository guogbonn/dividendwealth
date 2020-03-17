from django import forms
from .models import Stocks, User_Profile, StockInfo,Post,GenGroup,Comments
from tinymce import TinyMCE
from django.forms import Textarea
from dal import autocomplete
class StocksModelForm(forms.ModelForm):
    class Meta:
        model = Stocks
        fields = ['ticker','company_name','price','profile_pic','fairvale','dividend_yeild','dividend_growth','earning_growth','distrubution','months','url']

class User_profile_form(forms.ModelForm):
    class Meta:
        model = User_Profile
        exclude = ["user","sign_up_date","slug"]

class Stock_profile_form(forms.ModelForm):
    class Meta:
        model = StockInfo
        exclude = ["userprofile","stock","date_included"]

class GenGroupForm(forms.ModelForm):
    class Meta:
        model = GenGroup
        exclude =["creator","slug"]

class PostComment(forms.ModelForm):

    class Meta:
        model = Comments
        fields =('contents',)
        exclude =["author","post","stock","likes"]
        widgets = {
            'contents': Textarea(attrs={'class':'col-8 offset-2','cols': 40, 'rows': 10}),

        }
        labels ={
            'contents': '',
        }

#for creating a post/////////////////////////////
class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False, 'cols': 10, 'rows': 10}
        )
    )

    class Meta:
        model = Post
        exclude =["author","likes","viewcount","comment_count","topic","comment_count","repost","repost_count"]
        widgets = {
            'description': Textarea(attrs={'height': '59px', 'rows': 2,}),

            'stocks': autocomplete.ModelSelect2Multiple(
                url='core:stock-autocomplete',
                attrs={
                        # Set some placeholder

                        # Only trigger autocompletion after 3 characters have been typed
                        'data-minimum-input-length': 1,

                        'class': 'list-inline-item',
                        'width': '0px',
                        'type':'hidden'
    },


            ),

        }
