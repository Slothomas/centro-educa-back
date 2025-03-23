from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Usuario
from .serializers import UsuarioSerializer
from django.utils import timezone

# Vista para crear un nuevo usuario
@api_view(['POST'])  # Solo acepta solicitudes HTTP POST
def crear_usuario(request):
    data = request.data.copy()  # Se hace una copia de los datos recibidos para modificarlos si es necesario

    # Agregamos automáticamente la fecha de creación usando la fecha actual del servidor
    data['fechaCreacion_dat'] = timezone.now().date()

    # Creamos una instancia del serializador con los datos que nos llegaron por POST
    serializer = UsuarioSerializer(data=data)

    # Validamos si los datos cumplen con las reglas del modelo
    if serializer.is_valid():
        serializer.save()  # Guardamos el nuevo usuario en la base de datos
        return Response(serializer.data, status=status.HTTP_201_CREATED)  # Devolvemos los datos creados con código 201
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Si hay errores, los devolvemos con código 400


# Vista para obtener el listado completo de usuarios
@api_view(['GET'])  # Solo acepta solicitudes HTTP GET
def listar_usuarios(request):
    usuarios = Usuario.objects.all()  # Consultamos todos los usuarios de la base de datos
    serializer = UsuarioSerializer(usuarios, many=True)  # Serializamos todos los objetos (many=True indica lista)
    return Response(serializer.data, status=status.HTTP_200_OK)  # Retornamos los datos con código 200 (OK)

# Vista para editar un usuario existente
@api_view(['PUT'])  # Acepta solo solicitudes HTTP PUT
def editar_usuario(request, id_usuario):
    try:
        # Intentamos obtener el usuario desde la base de datos por su ID
        usuario = Usuario.objects.get(idUsuario_int=id_usuario)
    except Usuario.DoesNotExist:
        # Si no se encuentra, devolvemos error 404
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    # Cargamos los datos recibidos en el serializador
    # "partial=True" permite que solo se envíen los campos que se desean actualizar
    serializer = UsuarioSerializer(usuario, data=request.data, partial=True)

    # Verificamos si los datos enviados son válidos
    if serializer.is_valid():
        serializer.save()  # Guardamos los cambios en la base de datos
        return Response(serializer.data, status=status.HTTP_200_OK)  # Devolvemos los datos actualizados

    # Si los datos no son válidos, devolvemos los errores con código 400
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

