from django.http import HttpResponse

# Create your views here.
def home(request):
    return HttpResponse("Esta es la pagina del home de tu app Home")   