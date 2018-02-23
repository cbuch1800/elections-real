from django import forms
from .models import *
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User

# Do the validation as methods in the class

# class NewPostForm(forms.ModelForm):
#     Title = forms.CharField(
#         widget=forms.Textarea(attrs={
#             'rows': 2,
#             'placeholder': "Title it!"
#         }),
#         max_length=225
#     )

#     Body = forms.CharField(
#         widget=forms.Textarea(attrs={
#             'rows': 5,
#             'placeholder': "What have you got to say?"
#         }),
#         max_length=1000
#     )

#     class Meta:
#         model = Post
#         fields = ['Title', 'Body']



class AddCandidateForm(forms.ModelForm):

    ElectionID = forms.ModelChoiceField(queryset=None, empty_label=None)

    # Bio = forms.CharField(
    #     widget=forms.Textarea(attrs={
    #         'rows': 5,
    #         'placeholder': "Tell us about yourself."
    #     }),
    #     max_length=500
    # )

    class Meta:
        model = Candidate
        fields = ['ElectionID',]

    def __init__(self, user, *args, **kwargs):
        super(AddCandidateForm, self).__init__(*args, **kwargs)
        self.fields['ElectionID'].queryset = Election.objects.all().exclude(candidate__UserID=user)

class ElectionSuggestionForm(forms.Form):

    PostElection = forms.ModelChoiceField(queryset=None, empty_label=None)

    def __init__(self, user, *args, **kwargs):
        super(ElectionSuggestionForm, self).__init__(*args, **kwargs)
        self.fields['PostElection'].queryset = Election.objects.all().filter(candidate__UserID=user)


class NewElectionForm(forms.ModelForm):

    class Meta:
        model = Election
        fields = ['Name','Description','Seats','FlipGrid']

# class EditAccountForm(forms.ModelForm):

#     class Meta:
#         model = User
#         fields = ['first_name','last_name']

# class EditProfileForm(forms.ModelForm):

#     class Meta:
#         model = Profile
#         fields = ['ProfilePicture']

# class EditCandidateForm(forms.ModelForm):

#     class Meta:
#         model = Candidate
#         fields = ['Bio','Poster']

class ElectionSettingsForm(forms.ModelForm):

    class Meta:
        model = Election
        fields = '__all__'


# class NewImageForm(forms.ModelForm):

#     class Meta:
#         model = ImagePost
#         fields = ['Title','Description','Image']


class BaseElectionFormSet(forms.BaseModelFormSet):

    def __init__(self, *args, **kwargs):
        super(BaseElectionFormSet, self).__init__(*args, **kwargs)
        self.queryset = Election.objects.filter(Complete=False)

class BaseResultsFormSet(forms.BaseModelFormSet):

    def __init__(self, *args, **kwargs):
        super(BaseResultsFormSet, self).__init__(*args, **kwargs)
        self.queryset = Result.objects.filter(Public=False)

class SignUpForm(UserCreationForm):

    email = forms.EmailField(max_length=254, help_text='Must be your DCMail email address.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class CalculateResultForm(forms.Form):

    BeginVoteCounting = forms.BooleanField()