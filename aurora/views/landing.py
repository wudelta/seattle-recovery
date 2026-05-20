from django.shortcuts import render

def aurora_landing(request):
    return render(request, 'aurora/landing.html')
