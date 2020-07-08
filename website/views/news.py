from django.shortcuts import render


def news_root(request):
    return render(request, 'website/news.html')
