from django.shortcuts import render

def hopehub_landing(request):
    return render(request, 'hopehub/landing.html')
