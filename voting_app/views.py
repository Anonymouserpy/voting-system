from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from . import models
from django.db.models import Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required 
from django.core.mail import send_mail
from django.conf import settings

#this is where the voter will login
def login_view(request):
    return render(request, 'user/login.html')
#this will process the account you register and login
def process_login(request):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            voter = models.Voter.objects.get(user_email=user_email)
            if voter.check_password(password):
                request.session['voter_id'] = voter.id
                return redirect('voting_app:vote_view')
            else: 
                return render(request, 'user/login.html', {
                    'error_message': 'invalid email or password'
                })
        except models.Voter.DoesNotExist:
            return render(request, 'user/login.html',{
                'error_message': "Invalid email or password"
            })
#to view the register page
def register(request):
    return render(request, 'user/register.html')

#process to register
def process_register(request):
    fname = request.POST.get('fname')
    lname = request.POST.get('lname')
    email = request.POST.get('email')
    password = request.POST.get('password')
    if models.Voter.objects.filter(user_email=email).exists():
        return render(request, 'user/register.html', {
            'error_message': "Email already registered"
        })
    
    voter = models.Voter(
        user_fname = fname,
        user_lname = lname,
        user_email = email,
    )
    voter.set_password(password)
    voter.save()

    return redirect('voting_app:login_view')

#this is the homepage and where you can vote
def vote_view(request):
    voter_id = request.session.get('voter_id')
    voter = None
    if voter_id:
        try:
            voter = models.Voter.objects.get(id=voter_id)
        except models.Voter.DoesNotExist:
            pass

    president_position = models.Position.objects.get(position='President')
    vp_position = models.Position.objects.get(position='Vice President')
    sec_position = models.Position.objects.get(position='Secretary')
    treas_position = models.Position.objects.get(position='Treasurer')
    auditor_position = models.Position.objects.get(position='Auditor')
    pio_position = models.Position.objects.get(position='Public Information Officer')
    po_position = models.Position.objects.get(position='Peace Officer')

    candidates = models.Candidate.objects.select_related('position').filter(position=president_position)
    candidates1 = models.Candidate.objects.select_related('position').filter(position=vp_position)
    candidates2 = models.Candidate.objects.select_related('position').filter(position=sec_position)
    candidates3 = models.Candidate.objects.select_related('position').filter(position=treas_position)
    candidates4 = models.Candidate.objects.select_related('position').filter(position=auditor_position)
    candidates5 = models.Candidate.objects.select_related('position').filter(position=pio_position)
    candidates6 = models.Candidate.objects.select_related('position').filter(position=po_position)

    return render(request, 'user/vote.html', {
        'voter': voter,
        'president_candidate': candidates,
        'vice_president_candidate': candidates1,
        'secretary_candidate': candidates2,
        'treasurer_candidate': candidates3,
        'auditor_candidate': candidates4,
        'pio_candidate': candidates5,
        'po_candidate': candidates6,
    })

#this where the process
def vote_process(request):
    if request.method == 'POST':
        president_id = request.POST.get('president')
        vice_president_id = request.POST.get('vice_president')  
        secretary_id = request.POST.get('secretary')
        treasurer_id = request.POST.get('treasurer')
        auditor_id = request.POST.get('auditor')
        pio_ids = request.POST.getlist('pio')
        po_ids = request.POST.getlist('po')

        request.session['votes'] = {
            'president': president_id,
            'vice_president': vice_president_id,
            'secretary': secretary_id,
            'treasurer': treasurer_id,
            'auditor': auditor_id,
            'pio': pio_ids,
            'po': po_ids,
        }

        voter_id = request.session.get('voter_id')

        if voter_id:
            voter = models.Voter.objects.get(id=voter_id)
            voter.has_voted = True
            voter.save()

        return redirect('voting_app:submit_vote')

def submit_vote(request):
    # 1. Retrieve votes from session
    votes = request.session.get('votes')
    if not votes:
        return redirect('voting_app:vote')  # If no votes in session, redirect back

    # 2. Get the logged-in voter (adjust based on your login/session system)
    voter_id = request.session.get('voter_id')  # This assumes you stored voter ID in session at login
    if not voter_id:
        return redirect('voting_app:login_view')  # Or handle it how your app requires

    voter = get_object_or_404(models.Voter, id=voter_id)

    # 3. Prevent double voting
    if models.Vote.objects.filter(voter=voter).exists():
        return redirect('voting_app:already_voted')

    # 4. Save single-choice positions (radio buttons)
    single_positions = ['president', 'vice_president', 'secretary', 'treasurer', 'auditor']
    for pos_key in single_positions:
        candidate_id = votes.get(pos_key)
        if candidate_id:
            candidate = get_object_or_404(models.Candidate, id=candidate_id)
            models.Vote.objects.create(
                voter=voter,
                candidate=candidate,
                position=candidate.position  # Get position from candidate
            )

    # 5. Save multi-choice positions (checkboxes)
    multi_positions = ['pio', 'po']  # 'pio' = Public Information Officer, 'po' = Peace Officer
    for pos_key in multi_positions:
        candidate_ids = votes.get(pos_key, [])
        for candidate_id in candidate_ids:
            candidate = get_object_or_404(models.Candidate, id=candidate_id)
            models.Vote.objects.create(
                voter=voter,
                candidate=candidate,
                position=candidate.position,
            )

    # 6. Clear the session vote data
    del request.session['votes']
    
    # ✅ 7. Get all candidates the voter just voted for
    voted_candidates = models.Candidate.objects.filter(votes__voter=voter).distinct()

    # ✅ 8. Send confirmation email
    send_vote_confirmation_email(voter.user_email, voter.user_fname, voted_candidates)


    
    # 7. Redirect to a success page
    return redirect('voting_app:vote_success')

def vote_success(request):
    return render(request, 'user/success.html')

def already_voted(request):
    return render(request, 'user/already_voted.html')
#result
def vote_result(request):
    position = ["President", "Vice President", "Secretary", "Treasurer", "Auditor", "Public Information Officer", "Peace Officer"]

    context = {}

    for pos in position:
        position_obj = models.Position.objects.get(position=pos)
        candidates = models.Candidate.objects.filter(position=position_obj).annotate(
            vote_count=Count('votes')
        )
        context[f"{pos.lower().replace(' ', '_')}_candidate"] = candidates
    return render(request, 'user/result.html', context)

def admin_view(request):
    return render(request, 'user/admin.html')

def admin_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('voting_app:vote_result')
    else:
        return render(request, 'user/admin.html',{
            'error_message': "Login failed"
        })
    
@permission_required('user.Can_view_candidate')
def view_admin(request):
    position_names = ["President", "Vice President", "Secretary", "Treasurer", "Auditor", "Public Information Officer", "Peace Officer"]
    all_candidates = {}

    for pos_name in position_names:
        try:
            position_obj = models.Position.objects.get(position=pos_name)
            candidates = models.Candidate.objects.filter(position=position_obj)
            all_candidates[pos_name] = candidates
        except models.Position.DoesNotExist:
            all_candidates[pos_name] = []

    return render(request, 'user/admin_view.html', {
        'all_candidates': all_candidates
    })

def edit(request, candidate_id):
    candidate = get_object_or_404(models.Candidate, id=candidate_id)
    position_choices = models.Position.objects.all()
    return render(request, 'user/edit.html', {
        'candidate': candidate,
        'position_choices': position_choices,
    })

def process_edit(request, candidate_id):
    candidate = get_object_or_404(models.Candidate, id=candidate_id)

    if request.method == 'POST':
        candidate.name = request.POST.get('name', '')
        position_id = request.POST.get('position')
        if position_id:
            candidate.position = models.Position.objects.get(id=position_id)
        candidate.save()
        return redirect(reverse('voting_app:view_admin'))
    
def voter_view(request):
    voters = models.Voter.objects.filter().all()
    return render(request, 'user/voter_view.html', {
        'voters': voters
    })

def send_vote_confirmation_email(user_email, user_fname, voted_candidates):
    subject = 'Thank for voting!'

    candidate_list = ""
    for c in voted_candidates:
        candidate_list +=  f"- {c.name} ({c.position.position})\n"

    message = f"""Hi {user_fname},

Your vote has been successfully recorded. You voted for:

{candidate_list}

Thank you for participating in the election.

Best regards,  
Election Committee
"""
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    send_mail(subject, message, email_from, recipient_list)