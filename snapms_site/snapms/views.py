from django.shortcuts import render

# Create your views here.
def dashboard(request):
    context = dict(page_name="SnapMS")
    return render(request, "dashboard.html", context)


def docs(request):
    context = dict(page_name="SnapMS Documentation")
    return render(request, "docs.html", context)
