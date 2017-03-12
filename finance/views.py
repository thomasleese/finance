from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Profile


@login_required
def balance(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'finance/balance.html', {'profile': profile})


@login_required
def spending(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'finance/spending.html', {'profile': profile})
