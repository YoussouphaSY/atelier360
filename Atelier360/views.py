from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import LoginForm


# views pour gerer les connnexions
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                if user.is_superuser:
                    # Verification si c'est un superutilisateur
                    # redirection vers la page admin
                    return redirect('admin:index')
                elif user.role in ['formateur', 'metier', 'gestionnaire']:
                    # redirection vers la page Acceuil si c'est pas un superutilisateur
                    return redirect('home')
                else:
                    # redirection vers la page erreur si role non identiier
                    return redirect('page')
            else:
                form.add_error(
                    None, "Nom d'utilisateur ou mot de passe incorrect")
    else:
        form = LoginForm()

    return render(request, 'Atelier360/login.html', {'form': form})


# @login_required permet de blocquer l'utilisation des urls tant que l'utilisateur ne s'est pas authentifier
@login_required
def home_view(request):
    return render(request, 'Atelier360/home.html')


@login_required
def page_view(request):
    return render(request, 'Atelier360/page.html')
