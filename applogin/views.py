# applogin/views.py
from rest_framework.decorators import api_view, permission_classes # type: ignore
from rest_framework.permissions import AllowAny, IsAuthenticated # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import status # type: ignore
from .models import Usuario
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from django.db import connection
from appestudiantes.models import Estudiante
from appprofesores.models import Profesor


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


@api_view(['POST'])
def perfil(request):
    try:
        # Obtener los parámetros rut_str y idtiporol_int
        rut_str = request.data.get('rut_str')
        idtiporol_int = request.data.get('idTipoRol_int')

        if idtiporol_int == 3:  # Si es un estudiante
            # Ejecutar la consulta para estudiantes
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        CONCAT(e.nombres_str, ' ', e.apellidos_str) as Nombre,
                        e.correo_str as Correo,
                        e.telContacto_str as Telefono,
                        tb.nombre_str as Info,
                        FORMAT(fechaNacimiento_dat, 'dddd, dd "de" MMMM', 'es-es') AS Fecha_Cumpleanos
                    FROM estudiante e
                    LEFT JOIN beca b ON e.rut_str = b.rutBeneficiario_str
                    LEFT JOIN tipoBeca tb ON b.idTipoBeca_int = tb.idTipoBeca_int
                    WHERE e.rut_str = %s
                """, [rut_str])
                row = cursor.fetchone()

        elif idtiporol_int == 2:  # Si es un profesor
            # Ejecutar la consulta para profesores
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        CONCAT(p.nombres_str, ' ', p.apellidos_str) as Nombre,
                        p.correo_str as Correo,
                        p.telContacto_str as Telefono,
                        c.nombre_str as Info,
                        FORMAT(fechaNacimiento_dat, 'dddd, dd "de" MMMM', 'es-es') AS Fecha_Cumpleanos
                    FROM profesor p
                    LEFT JOIN certificacion c ON p.idCertificacion_int = c.idCertificacion_int
                    WHERE p.rut_str = %s
                """, [rut_str])
                row = cursor.fetchone()

        else:
            return Response({'mensaje': 'Tipo de rol no válido'}, status=status.HTTP_400_BAD_REQUEST)

        if row:
            # Convertir los resultados en un diccionario y devolverlos como respuesta
            perfil = {
                'Nombre': row[0],
                'Correo': row[1],
                'Telefono': row[2],
                'Info': row[3],  # Nombre de la certificación para profesores
                'Fecha_Cumpleanos': row[4]
            }
            return Response(perfil, status=status.HTTP_200_OK)
        else:
            return Response({'mensaje': 'Perfil no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    except ObjectDoesNotExist:
        return Response({'mensaje': 'Perfil no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        # Manejo de errores
        print(f"Error en el servidor: {str(e)}")
        return Response({'mensaje': 'Error en el servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def actualizarClave(request):
    try:
        # Obtener los datos enviados desde Angular
        rut = request.data.get('rut_str')
        nueva_contrasena = request.data.get('contrasena_str')

        # Consultar el usuario por rut
        usuario = Usuario.objects.get(rut_str=rut)
        
        # Actualizar la contraseña si el usuario existe
        usuario.contrasena_str = nueva_contrasena
        usuario.save()

        return Response({'mensaje': 'Clave actualizada correctamente'}, status=status.HTTP_200_OK)
    
    except ObjectDoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({'mensaje': f'Error en el servidor: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    

@api_view(['PUT'])
def actualizarDatos(request):
    try:
        # Obtener los datos enviados desde Angular
        rut = request.data.get('rut_str')
        idtiporol = request.data.get('idTipoRol_int')
        nuevo_correo = request.data.get('nuevo_correo', None)
        nuevo_telefono = request.data.get('nuevo_telefono', None)
        
        if idtiporol == 2:
            tabla = Profesor
        elif idtiporol == 3:
            tabla = Estudiante
        
        # Consultar el usuario por rut
        usuario = tabla.objects.get(rut_str=rut)
        
        # Actualizar los datos si el usuario existe
        if nuevo_correo:
            usuario.correo_str = nuevo_correo
        if nuevo_telefono:
            usuario.telcontacto_str = nuevo_telefono
        usuario.save()

        return Response({'mensaje': 'Datos actualizados correctamente'}, status=status.HTTP_200_OK)
    
    except ObjectDoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({'mensaje': f'Error en el servidor: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)