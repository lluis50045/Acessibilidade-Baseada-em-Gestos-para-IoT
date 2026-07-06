import requests
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpResponse
from .models import Conta
from dotenv import load_dotenv
from urllib.parse import urlencode
import os


load_dotenv() 
base_url = os.getenv("AMAZON_AUTH_URL")
params = {
    "client_id": os.getenv("AMAZON_CLIENT_ID"),
    "scope": os.getenv("AMAZON_SCOPE"),
    "response_type": "code",
    "redirect_uri": os.getenv("AMAZON_REDIRECT_URI")
}
auth_url = f"{base_url}?{urlencode(params)}"


def principal(request):
    return render(request, 'index.html')

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, "home.html", {"auth_url": auth_url})


def amazon_callback(request):
    code = request.GET.get('code')
    if not code:

        return redirect('login') # Usando o nome da rota 'login'

    # --- 2. Trocar o 'code' por um 'access_token' ---
    token_url = 'https://api.amazon.com/auth/o2/token'
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': os.getenv("AMAZON_REDIRECT_URI"),
        'client_id': os.getenv("AMAZON_CLIENT_ID"),
        'client_secret': os.getenv("AMAZON_CLIENT_SECRET_ID")
    }
    
    response = requests.post(token_url, data=payload)
    token_data = response.json()

    if 'access_token' not in token_data:

        return redirect('login')

    access_token = token_data['access_token']
    

    profile_url = 'https://api.amazon.com/user/profile'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    profile_response = requests.get(profile_url, headers=headers)
    user_data = profile_response.json()
    
    if 'email' not in user_data:

        return redirect('login')

    # --- 4. Encontrar ou criar o usuário no seu banco de dados ---
    email = user_data['email']
    name = user_data.get('name', '') # Usar .get para evitar erro se o nome não vier
    amazon_user_id = user_data['user_id']
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User.objects.create_user(username=email, email=email, first_name=name)

    # 2. Buscar ou criar o AmazonProfile ligado ao user
    profile, created = Conta.objects.get_or_create(
    amazon_user_id=amazon_user_id,
    defaults={
        'nome': name,
        'email': email,
        'user': user  # <- vincula com User
    }
)

    # 3. Se não criou, pega o usuário do perfil
    if not created:
        profile.user = user
        profile.save()

    # # 4. Fazer login
    login(request, user)
    print(f'Usuário logado: {user.username} com ID da Amazon: {profile.amazon_user_id}')
    # 5. Redirecionar
    return redirect('dashboard')
    
    

