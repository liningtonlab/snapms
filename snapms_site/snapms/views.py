from django.shortcuts import render

# Create your views here.
def dashboard(request):
    context = dict(page_name="SnapMS")
    return render(request, "dashboard.html", context)
