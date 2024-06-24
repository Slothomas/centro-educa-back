# applogin/authentication.py
from rest_framework.authentication import BaseAuthentication # type: ignore
from rest_framework.exceptions import AuthenticationFailed # type: ignore
from rest_framework_simplejwt.tokens import UntypedToken # type: ignore
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError # type: ignore
from .models import Usuario


class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')
        
        if not token:
            return None  # No intento de autenticación
        
        try:
            # Se espera que el token tenga el formato "Bearer <token>"
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            else:
                raise AuthenticationFailed('Formato de token inválido')
            
            # Verificar y decodificar el token
            untyped_token = UntypedToken(token)
            
            # Extraer información del payload del token
            payload = untyped_token.payload
            
            # Obtener el usuario a partir del RUT del payload
            rut_str = payload.get('rut')
            if not rut_str:
                raise AuthenticationFailed('El token no contiene el RUT del usuario')
            
            # Buscar el usuario por rut_str
            usuario = Usuario.objects.filter(rut_str=rut_str).first()
            if not usuario:
                raise AuthenticationFailed('Usuario no encontrado')
            
            return (usuario, None)
        
        except (InvalidToken, TokenError) as e:
            raise AuthenticationFailed(f'Token inválido: {str(e)}')
        
    def authenticate_header(self, request):
        return 'Bearer realm="api"'