from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response # type: ignore
from rest_framework import status # type: ignore
from .models import Profesor
from .serializers import ProfesorSerializer
from django.core.exceptions import ObjectDoesNotExist

@api_view(['POST'])
@permission_classes([AllowAny])
def getTeacher(request):
    try:
        # Consultar el usuario por rut_str
        usuario = Profesor.objects.get(rut_str=request.data.get('rut_str'))
        
        # Serializar el objeto Profesor
        serializer = ProfesorSerializer(usuario)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    except ObjectDoesNotExist as e:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({'mensaje': 'Error en el servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def getAllTeachers(request):
    try:
        # Obtener todos los profesores
        profesores = Profesor.objects.all()
        
        # Serializar el queryset de profesores
        serializer = ProfesorSerializer(profesores, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'mensaje': 'Error en el servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)