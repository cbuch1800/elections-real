from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.models import User
from django.urls import reverse
from django.forms import modelformset_factory
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from .models import *
from .forms import *
from .tokens import account_activation_token
from .electoral_system import CountSTV
import json
from pprint import pprint
import logging

logger = logging.getLogger(__name__)
#  Create your views here.


def welcome(request):
    # messages.add_message(request, messages.INFO, 'Hello World.')
    return render(request, 'general/hello.html')


# def newsfeed(request):
#     Elections = Election.objects.filter(Complete=False).filter(CandidateReg=True)
#     Text = Post.objects.all().order_by('-Timestamp')
#     Images = ImagePost.objects.all().order_by('-Timestamp')
#     Posts = []

#     while True:
#         if Text[0].Timestamp >= Images[0].Timestamp:
#             Posts.append(Post.objects.get(id=Text[0].id))
#             Text = Text.exclude(id=Text[0].id)
#         else:
#             Posts.append(ImagePost.objects.get(id=Images[0].id))
#             Images = Images.exclude(id=Images[0].id)
#         if len(Text) == 0:
#             for i in Images:
#                 Posts.append(i)
#             break
#         elif len(Images) == 0:
#             for i in Text:
#                 Posts.append(i)
#             break

#     return render(request, 'campaign/newsfeed.html', {
#         "posts": Posts,
#         'elections': Elections,
#     })

def view_candidates(request):
    elections = Election.objects.all()
    candidates = Candidate.objects.all()
    return render(request, 'campaign/candidates.html', {
        "candidates": candidates,
        "elections": elections,
    })

# def candidate_profile(request, candidateID):
#     try:
#         candidate = Candidate.objects.get(id=candidateID)
#         Text = Post.objects.all().filter(Author=candidateID).order_by('-Timestamp')
#         Images = ImagePost.objects.all().filter(Author=candidateID).order_by('-Timestamp')
#     except:
#         raise Http404()

#     Posts = []

#     while True:
#         if len(Text) == 0 and len(Images) == 0:
#             break
#         elif len(Text) == 0:
#             for i in Images:
#                 Posts.append(i)
#             break
#         elif len(Images) == 0:
#             for i in Text:
#                 Posts.append(i)
#             break
#         if Text[0].Timestamp >= Images[0].Timestamp:
#             Posts.append(Post.objects.get(id=Text[0].id))
#             Text = Text.exclude(id=Text[0].id)
#         else:
#             Posts.append(ImagePost.objects.get(id=Images[0].id))
#             Images = Images.exclude(id=Images[0].id)

    
#     return render(request, 'campaign/profile.html',{
#         "candidate": candidate,
#         "posts": Posts
#     })

@permission_required('elections.can_view_results')
def test_view(request):
    return render(request, 'random/test.html')


# def new_post(request):
#     if request.method == 'POST':
#         form = NewPostForm(request.POST)
#         election_form = ElectionSuggestionForm(request.user, request.POST)
#         if form.is_valid() and election_form.is_valid():
#             post_tmp = form.save(commit=False)
#             post_tmp.Author = Candidate.objects.get(UserID=request.user, ElectionID=election_form.cleaned_data['PostElection'])
#             post_tmp.save()
#             messages.add_message(request, messages.SUCCESS, 'Post made')# and waiting for approval)
#             return redirect('/feed/')
#     else:    
#         form = NewPostForm()
#         election_form = ElectionSuggestionForm(request.user)
#         candidates = Candidate.objects.filter(UserID=request.user)

#     return render(request, 'campaign/new_post.html', {
#         "form": form,
#         "election_form": election_form,
#         "candidates": candidates,
#     })

def add_candidate(request):
    if request.method == 'POST':
        form = AddCandidateForm(request.user, request.POST)
        if form.is_valid():
            candidate = form.save(commit=False)
            # candidate.Poster = request.FILES['Poster']
            candidate.UserID = request.user
            candidate.save()
            messages.add_message(request, messages.SUCCESS, 'You have successfully registered as a candidate in {}'.format(candidate.ElectionID.Name))
            return redirect(reverse('elections:home'))
    else:
        form = AddCandidateForm(request.user)
        elections = Election.objects.all().exclude(candidate__UserID=request.user).filter(Gender=request.user.profile.Gender).filter(CandidateReg=True)
        # filtering of the elections to decide which options can show - not already registered,correct gender,correct user type, Registration is open.
    return render(request, 'registration/cand_reg.html', {
        "form": form,
        "elections": elections,
    })

def open_elections(request):
    elections = Election.objects.all().exclude(ballotcast__UserID=request.user).filter(VotingOpen=True)
    return render(request, 'vote/open_elections.html', {
        "elections": elections
    })

def ballot(request, ElectionIDx):

    #### REDIRECT HERE IF YOU HAVE ALREADY VOTED ####

    try:
        election = Election.objects.get(id=ElectionIDx, VotingOpen=True, Complete=False)
        allowed = AllowToVote.objects.get(UserTypeID=request.user.profile.UserTypeID, ElectionID=ElectionIDx)
    except:
        raise Http404()

    if len(BallotCast.objects.all().filter(UserID=request.user, ElectionID=ElectionIDx)) > 0:
        messages.add_message(request, messages.SUCCESS, 'You have already voted in {}'.format(election.Name))
        return redirect(reverse('elections:elections'))

    if request.method == 'POST':

        # Parse json
        form_valid = True
        candidate_order = request.POST.get('candidate_order', None)
        candidate_order = json.loads(candidate_order)
        rankings = request.POST.get('rankings', None)
        rankings = json.loads(rankings)

        # print(rankings)
        # print(type(rankings))
        rankings_only = list(filter(None, rankings))
        rankings_only = [int(i) for i in rankings_only]
        # messages.add_message(request, messages.SUCCESS, '{}, {}'.format(rankings_only, set(rankings_only)))

        # Validation:
        if ''.join(rankings).isdigit(): #all rankings are numbers
            if len(set(rankings_only)) == len(rankings_only): #no rankings are repeated
                if sorted(rankings_only)[0] > 0:
                    if sorted(rankings_only)[-1] == len(rankings_only): #no rankings are skipped
                        if len(BallotCast.objects.all().filter(UserID=request.user, ElectionID=ElectionIDx)) == 0: #User hasn't voted yet in this election

                            # Determines how many ranks were submitted
                            ranking_quantity = 0
                            for i in rankings:
                                if i != "":
                                    ranking_quantity += 1
                            # Creates a new list, sorting candidates by their associated rank
                            ordered_candidates = []
                            for i in range(1,ranking_quantity+1):
                                candidate_index = rankings.index(str(i))
                                ordered_candidates.append(candidate_order[candidate_index])
                            ballot_processed = json.dumps(ordered_candidates)

                            election = Election.objects.get(id=ElectionIDx)
                            ballot_instance = CompleteBallot(ElectionID=election, Vote=ballot_processed)
                            cast_ballot_instance = BallotCast(UserID=request.user, ElectionID=election)
                            ballot_instance.save()
                            cast_ballot_instance.save()
                            alert_text = "Ballot successfully cast."
                            messages.add_message(request, messages.SUCCESS, 'Ballot successfully cast in {}'.format(election.Name))

                        else:
                            form_valid = False
                            alert_text = "Error. You have already voted in this election."
                    else:
                        form_valid = False
                        alert_text = "Error. You must rank candidates sequentially without skipping a rank."
                else:
                    form_valid = False
                    alert_text = "Error. You must rank candidates with positive integers."  
                             
            else:
                form_valid = False
                alert_text = "Error. You can not give multiple candidates the same rank."                
        else:
            form_valid = False
            alert_text = "Error. You can only enter numbers as ranks for candidates."

        args = {
            'url': reverse('elections:home'),
            'valid': form_valid,
            'alert': alert_text,
        }
        return JsonResponse(args)

    candidates = Candidate.objects.all().filter(ElectionID=ElectionIDx).order_by('?')
    return render(request, 'vote/ballot.html', {
        "candidates": candidates
    })


@permission_required('elections.can_view_results')
def admin_tools(request):
    ElectionFormSet = modelformset_factory(Election, exclude=('Complete','Seats','Gender'), formset=BaseElectionFormSet, extra=0)
    ResultsFormSet = modelformset_factory(Result, exclude=('ElectionID','Results',), formset=BaseResultsFormSet, extra=0)
    if request.method == 'POST':
        pprint(request.POST)
        if 'new_election' in request.POST:
            new_election = NewElectionForm(request.POST)
            if new_election.is_valid():
                election = new_election.save(commit=False)
                election.save()
                messages.add_message(request, messages.SUCCESS, 'Election created')
                return redirect(reverse('elections:home'))
            else:
                messages.add_message(request, messages.ERROR, 'Problem')
                return redirect(reverse('elections:home'))

        elif 'edit_elections' in request.POST:
            election_formset = ElectionFormSet(request.POST)
            print(election_formset.errors)
            if election_formset.is_valid():
                election_formset.save()
                messages.add_message(request, messages.SUCCESS, 'Election settings saved')
                return redirect(reverse('elections:home'))
            else:
                messages.add_message(request, messages.ERROR, 'Problem')
                return redirect(reverse('elections:home'))

        elif 'public_result' in request.POST:
            formset = ResultsFormSet(request.POST)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Results publicised')
                return redirect(reverse('elections:home'))

    else:
        results = Result.objects.filter(Public=False)
        result_list = []
        for result in results:
            result_data = [result.ElectionID.Name]
            candidates = Candidate.objects.filter(id__in=json.loads(result.Results))
            for candidate in candidates:
                result_data.append(candidate.UserID.get_full_name)
            result_list.append(result_data)

        open_elections = Election.objects.filter(Complete=False)
        new_election_form = NewElectionForm()
        election_formset = ElectionFormSet()
        result_formset = ResultsFormSet()
        
        
    return render(request, 'admin/admin_tools.html',{
        'new_election': new_election_form,
        'formset': election_formset,
        'elections': open_elections,
        'result_formset': result_formset,
        'results': result_list,
    })


# def edit_profiles(request):

#     if request.method == 'POST':
#         if 'account_profile' in request.POST:
#             account_form = EditAccountForm(request.POST, instance=request.user)
#             profile_form = EditProfileForm(request.POST, instance=request.user.profile)
#             if account_form.is_valid() and profile_form.is_valid():
#                 account_form.save()
#                 profile_form.save()
#                 messages.add_message(request, messages.SUCCESS, "Account information updated")
#                 return redirect(reverse('elections:home'))
    
#     else:
#         account_form = EditAccountForm(instance=request.user)
#         profile_form = EditProfileForm(instance=request.user.profile)
#         user_candidates = Candidate.objects.filter(UserID=request.user)

#     return render(request, 'registration/edit_profiles.html', {
#         'account_form': account_form,
#         'profile_form': profile_form,
#         'candidates': user_candidates,
#     })

def password_change(request):

    if request.method == 'POST':
        password_form = PasswordChangeForm(data=request.POST, user=request.user)
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)
            messages.add_message(request, messages.SUCCESS, "Password reset.")
            return redirect(reverse('elections:home'))
        else:
            return redirect('/password/new/')
    else:
        password_form = PasswordChangeForm(user=request.user)

    return render(request, 'registration/password_change.html', {
        'form': password_form
    })


# def edit_candidate(request, candidate):
#     try:
#         candidate_record = Candidate.objects.get(id=candidate)
#     except:
#         return redirect('/profiles/edit/')
#     if candidate_record.UserID == request.user:

#         if request.method == 'POST':
#             candidate_form = EditCandidateForm(request.POST, request.FILES, instance=candidate_record)
#             if candidate_form.is_valid():
#                 changed_candidate = candidate_form.save(commit=False)
#                 changed_candidate.Poster = request.FILES['Poster']
#                 changed_candidate.save()
#                 messages.add_message(request, messages.SUCCESS, "Candidate profile updated")
#                 return redirect(reverse('elections:home'))

#         else:
#             candidate_form = EditCandidateForm(instance=candidate_record)
        
#         return render(request, 'registration/edit_candidate.html',{
#             'candidate_form': candidate_form
#         })

#     else:
#         return redirect('/profiles/edit/')


# def new_image(request):
#     if request.method == 'POST':
#         form = NewImageForm(request.POST, request.FILES)
#         election_form = ElectionSuggestionForm(request.user, request.POST)
#         if form.is_valid() and election_form.is_valid():
#             new_image = form.save(commit=False)
#             new_image.Image = request.FILES['Image']
#             new_image.Author = Candidate.objects.get(UserID=request.user, ElectionID=election_form.cleaned_data['PostElection'])
#             new_image.save()
#             messages.add_message(request, messages.SUCCESS, 'Post made')# and waiting for approval)
#             return redirect('/feed/')
#     else:    
#         form = NewImageForm()
#         election_form = ElectionSuggestionForm(request.user)
#         candidates = Candidate.objects.filter(UserID=request.user)

#     return render(request, 'campaign/new_image.html', {
#         "form": form,
#         "election_form": election_form,
#         "candidates": candidates,
#     })


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.is_active = False
            new_user.save()
            current_site = get_current_site(request)
            subject = "Activate your DC-Elects account"
            message = render_to_string('registration/account_activation_email.html', {
                'user': new_user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(new_user.id)),
                'token': account_activation_token.make_token(new_user),
            })
            new_user.email_user(subject, message)
            return redirect('elections:account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html',{
        'form': form,
    })


def account_activation_sent(request):
    return render(request, 'registration/account_activation_sent.html')

def error_404(request):
    return render(request, 'general/error_404.html')

def error_500(request):
    return render(request, 'general/error_500.html')

@permission_required('elections.can_view_results')
def get_results(request, ElectionIDx):
    try:
        election = Election.objects.get(id=ElectionIDx)
    except:
        raise Http404()
    
    if request.method == 'POST':
        form = CalculateResultForm(request.POST)
        if form.is_valid() and form.cleaned_data['BeginVoteCounting'] == True:
            election.Complete = True
            election.save()

            candidates = Candidate.objects.filter(ElectionID=election.id)
            CandidatesList = []
            for cand in candidates:
                CandidatesList.append(str(cand.id))

            all_ballots = CompleteBallot.objects.filter(ElectionID=election.id)
            BallotPapers = []
            for ballot in all_ballots:
                ballot_as_lst = json.loads(ballot.Vote)
                BallotPapers.append(ballot_as_lst)

            NumberElected = election.Seats

            ElectionResult = CountSTV(CandidatesList, BallotPapers, NumberElected)
            ElectionResult = json.dumps(ElectionResult)

            new_result = Result(ElectionID=election, Results=ElectionResult)
            new_result.save()
            return redirect('elections:tools')

    else:
        form = CalculateResultForm()

    return render(request, 'admin/calculate_result.html',{
        'form': form,
        'election': election,
    })


def view_results(request):
    results = Result.objects.filter(Public=True)
    result_list = []
    for result in results:
        result_data = [result.ElectionID.Name]
        candidates = Candidate.objects.filter(id__in=json.loads(result.Results))
        for candidate in candidates:
            result_data.append(candidate.UserID.get_full_name)
        result_list.append(result_data)
    return render(request, 'posts/public_results.html', {
        'results': result_list,
    })

@permission_required('elections.can_view_results')
def create_accounts(request):

    if request.method == 'GET':
        csv_form = GetCSVForm()

        return render(request, 'registration/create_accounts.html',{
            'form':csv_form
        })
    
    try:
        my_csv = request.FILES["csv_file"]
        # Ensures a CSV file
        if not my_csv.name.endswith('.csv'):
            messages.add_message(request, messages.ERROR, "You must upload a .csv file")
            return HttpResponseRedirect(reverse('elections:create_accounts'))
        # Ensures file is not too big
        if my_csv.multiple_chunks():
            messages.add_message(request, messages.ERROR, "Your file size is too big")
            return HttpResponseRedirect(reverse('elections:create_accounts'))

        # Turns CSV into useable data
        file_data = my_csv.read().decode("utf-8")
        lines = file_data.split("\r\n")
        pprint(lines)
        pprint(lines[1:-1])
        if 'teachers_button' in request.POST:
            for line in lines[1:-1]:
                fields = line.split(",")

                new_user = User()
                new_user.username = fields[3].split("@")[0]
                new_user.first_name = fields[1]
                new_user.last_name = fields[0]
                new_user.email = fields[3]
                password_string = get_random_string(15)
                new_user.set_password(password_string)
                new_user.is_active = False
                new_user.save()
                new_user.refresh_from_db()
                if fields[2] == "Male":
                    new_user.profile.Gender = "M"
                elif fields[2] == "Female":
                    new_user.profile.Gender = "F"
                new_user.profile.UserTypeID = UserType.objects.get(UserType="Teacher")
                new_user.profile.EmailConfirmed = False
                new_user.save()

                current_site = get_current_site(request)
                subject = "Activate your DC-Elects account"
                message = render_to_string('registration/account_activation_email.html', {
                    'user': new_user,
                    'password': password_string,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(new_user.id)),
                    'token': account_activation_token.make_token(new_user),
                })
                new_user.email_user(subject, message)

        elif 'students_button' in request.POST:
            for line in lines[1:-1]:
                fields = line.split(",")

                if fields[3][0:2] in ['12','13'] and len(fields[3]) == 3:
                    new_user = User()
                    new_user.username = fields[4].split("@")[0]
                    new_user.first_name = fields[1]
                    new_user.last_name = fields[0]
                    new_user.email = fields[4]
                    password_string = get_random_string(15)
                    new_user.set_password(password_string)
                    new_user.is_active = False
                    new_user.save()
                    new_user.refresh_from_db()
                    new_user.profile.Gender = fields[2]
                    if fields[3][0:2] == '12':
                        new_user.profile.UserTypeID = UserType.objects.get(UserType="Year12")
                    elif fields[3][0:2] == '13':
                        new_user.profile.UserTypeID = UserType.objects.get(UserType="Year13")
                    new_user.profile.EmailConfirmed = False
                    new_user.save()
                
                    current_site = get_current_site(request)
                    subject = "Activate your Elect-DC account"
                    message = render_to_string('registration/account_activation_email.html', {
                        'user': new_user,
                        'password': password_string,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(new_user.id)),
                        'token': account_activation_token.make_token(new_user),
                    })
                    new_user.email_user(subject, message)
        
        messages.add_message(request, messages.SUCCESS, "Accounts created successfully")

    except Exception as e:
        messages.add_message(request, messages.ERROR, "An error occured: "+repr(e))
    
    
    return HttpResponseRedirect(reverse('elections:create_accounts'))


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.EmailConfirmed = True
        user.save()
        login(request, user)
        return redirect('elections:home')
    else:
        return render(request, 'account_activation_invalid.html')
