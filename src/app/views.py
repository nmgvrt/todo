from django.urls import reverse
from django.shortcuts import render, redirect


def error(request):
    msgs = request._messages._get()[0]
    if not msgs:
        return redirect(reverse('index'))

    return render(request, 'base/error.html')
