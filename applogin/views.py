# applogin/views.py
from rest_framework.decorators import api_view, permission_classes # type: ignore
from rest_framework.permissions import AllowAny # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import status # type: ignore
from .models import Usuario
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    try:
        # Consultar el usuario por rut_str
        usuario = Usuario.objects.get(rut_str=request.data.get('rut_str'))
        
        # Verificar si el usuario y la contraseña son correctos
        if usuario.contrasena_str == request.data.get('contrasena_str') and usuario.idtiporol_int_id == request.data.get('idtiporol_int'):
            # Generar tokens de acceso y actualización
            refresh = RefreshToken.for_user(usuario)
            refresh['rut'] = usuario.rut_str  # Añadir el RUT al payload del token
            access_token = str(refresh.access_token)
            
            return Response({
                'mensaje': 'Inicio de sesión exitoso',
                'access_token': access_token,
                'refresh_token': str(refresh)
            }, status=status.HTTP_200_OK)
        else:
            return Response({'mensaje': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
    
    except ObjectDoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({'mensaje': f'Error en el servidor: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
