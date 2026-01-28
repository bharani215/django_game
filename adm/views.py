from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import *
import random
import json


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        age = request.POST.get('age')

        if not username or not email or not password or not age:
            messages.error(request, 'All fields are required!')
            return render(request, 'signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return render(request, 'signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'signup.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        Profile.objects.create(
            user=user,
            age=age,
            coin=5000
        )

        messages.success(request, 'Account created successfully! You have 5000 coins.')
        return redirect('signin')

    return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Please enter both username and password')
            return render(request, 'signin.html')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'signin.html')


@login_required
def signout(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('signin')


@login_required
def dashboard(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, age=18, coin=5000)
    
    recent_games = GameRecord.objects.filter(user=request.user).order_by('-update_at')[:5]
    
    return render(request, 'dashboard.html', {
        'profile': profile,
        'recent_games': recent_games
    })


@login_required
def tournament(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, age=18, coin=5000)
    
    if request.method == 'POST':
        game_type = request.POST.get('game_type', '1')

        if game_type == '1':  # Number Game
            if profile.coin < 500:
                messages.error(request, 'Not enough coins! You need 500 coins')
                return render(request, 'tournament.html', {'coin': profile.coin})

            # Deduct coins
            profile.coin -= 500
            profile.save()

            # Create tournament (if doesn't exist)
            tournament_obj, created = Tournament.objects.get_or_create(
                id=1,
                defaults={'name': 'Number Game', 'fee': 500, 'is_active': True}
            )

            # Create player history
            PlayerHistory.objects.create(
                user=request.user,
                tournament=tournament_obj
            )

            # Initialize game session
            request.session['game_active'] = True
            request.session['secret'] = ''.join(str(random.randint(1, 9)) for _ in range(4))
            request.session['attempt'] = 0
            request.session['max_score'] = 0
            request.session['history'] = []
            print("Secret Number:", request.session['secret'])  # For debugging
            messages.success(request, '500 coins deducted. Game starting...')
            return redirect('game')

        elif game_type == '2':  # Stone Paper Scissor
            messages.info(request, 'Stone Paper Scissor coming soon!')
            return render(request, 'tournament.html', {'coin': profile.coin})

    return render(request, 'tournament.html', {'coin': profile.coin})


@login_required
def game(request):
    if not request.session.get('game_active'):
        messages.error(request, 'No active game. Please select a game first.')
        return redirect('tournament')

    secret = request.session.get('secret', '')
    
    if request.method == 'POST':
        guess = request.POST.get('guess', '')
        
        if len(guess) != 4 or not guess.isdigit():
            messages.error(request, 'Please enter exactly 4 digits (0-9)')
            return render(request, 'game.html', {
                'attempt': request.session.get('attempt', 0),
                'history': request.session.get('history', []),
                'max_score': request.session.get('max_score', 0)
            })

        attempt = request.session.get('attempt', 0) + 1
        request.session['attempt'] = attempt

        clue = ""
        correct = 0
        
        for i in range(4):
            if guess[i] == secret[i]:
                clue += "*"
                correct += 1
            elif guess[i] in secret:
                clue += "#"
            else:
                clue += "_"

        if correct > request.session['max_score']:
            request.session['max_score'] = correct

        # Save to session history
        history = request.session.get('history', [])
        history.append({
            'guess': guess,
            'clue': clue,
            'attempt': attempt
        })
        request.session['history'] = history

        # Save to database
        GameHistory.objects.create(
            user=request.user,
            output=clue
        )

        if clue == "****":
            GameRecord.objects.create(
                user=request.user,
                attempt_count=attempt,
                max_score=request.session['max_score'],
                status='Won'
            )
            
            # Award bonus coins
            profile = Profile.objects.get(user=request.user)
            profile.coin += 2000
            profile.save()
            
            # Clear game session
            request.session['game_active'] = False
            
            return render(request, 'win.html', {
                'attempt': attempt,
                'secret': secret,
                'new_coins': profile.coin
            })

        request.session.modified = True
        return render(request, 'game.html', {
            'clue': clue,
            'attempt': attempt,
            'history': history,
            'max_score': request.session['max_score']
        })

    return render(request, 'game.html', {
        'attempt': request.session.get('attempt', 0),
        'history': request.session.get('history', []),
        'max_score': request.session.get('max_score', 0)
    })


@login_required
def win(request):
    # Clear game session
    if 'game_active' in request.session:
        del request.session['game_active']
    if 'secret' in request.session:
        del request.session['secret']
    if 'attempt' in request.session:
        del request.session['attempt']
    if 'max_score' in request.session:
        del request.session['max_score']
    if 'history' in request.session:
        del request.session['history']
    
    return render(request, 'win.html')


@login_required
def history(request):
    game_records = GameRecord.objects.filter(user=request.user).order_by('-update_at')
    game_history = GameHistory.objects.filter(user=request.user).order_by('-time')[:50]

    return render(request, 'history.html', {
        'game_records': game_records,
        'game_history': game_history
    })


@login_required
def profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, age=18, coin=5000)

    

    if request.method == 'POST':
        age = request.POST.get('age')
        if age and age.isdigit():
            profile.age = int(age)
        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']    
        profile.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('profile')
    
    return render(request, 'profile.html', {'profile': profile})