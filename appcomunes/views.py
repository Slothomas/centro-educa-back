import os
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response # type: ignore
from rest_framework import status # type: ignore
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.db import connection, transaction
import datetime
from django.utils import timezone
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.conf import settings



@api_view(['GET'])
def getAllEvents(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""

                ;WITH EventosNumerados AS (
    SELECT
        e.idEvento_int AS ID_EVENTO,
        a.nombre_str AS NOMBRE_ASIGNATURA,
        e.descripcion AS DESCRIPCION,
        -- Convertir fecha y formatear con la primera letra en mayúscula
        FORMAT(TRY_CONVERT(DATE, e.fechaEvento_dat, 103), 'dddd d \de', 'es-ES') AS FECHA_EVENTO,
		FORMAT(TRY_CONVERT(DATE, e.fechaEvento_dat, 103), 'MMMM', 'es-ES') AS MES,
        ROW_NUMBER() OVER (PARTITION BY MONTH(TRY_CONVERT(DATE, e.fechaEvento_dat, 103)) ORDER BY TRY_CONVERT(DATE, e.fechaEvento_dat, 103)) AS RowNum
    FROM
        evento e
    INNER JOIN
        asignatura a ON e.idAsignatura_int = a.idAsignatura_int
    WHERE
        TRY_CONVERT(DATE, e.fechaEvento_dat, 103) >= GETDATE() -- Utiliza GETDATE() para obtener la fecha actual
)

SELECT
    ID_EVENTO,
    NOMBRE_ASIGNATURA,
    DESCRIPCION,
    UPPER(SUBSTRING(FECHA_EVENTO, 1, 1)) + LOWER(SUBSTRING(FECHA_EVENTO, 2, LEN(FECHA_EVENTO) - 1)) AS FECHA_EVENTO,
	UPPER(SUBSTRING(MES, 1, 1)) + LOWER(SUBSTRING(MES, 2, LEN(MES) - 1)) AS MES,
    RowNum
FROM EventosNumerados
WHERE RowNum <= 4
ORDER BY MONTH(TRY_CONVERT(DATE, FECHA_EVENTO, 103)), TRY_CONVERT(DATE, FECHA_EVENTO, 103);



                """)
            rows = cursor.fetchall()

        results = []
        for row in rows:
            event = {
                "ID_EVENTO": row[0],
                "NOMBRE_ASIGNATURA": row[1],
                "DESCRIPCION": row[2],
                "FECHA_EVENTO": row[3],  # Formatea la fecha si es necesario
                "MES": row[4]
            }
            results.append(event)

        return Response(results, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['POST'])
def envioCorreo(request):
    nombre = request.data.get('nombre')
    correo = request.data.get('correo')
    mensaje = request.data.get('mensaje')

    if nombre and correo and mensaje:
        destinatario = 'liceomunicipalcerronavia@outlook.com'
        mensaje_completo = (
            f'Mensaje de: {nombre}\n'
            f'Correo: {correo}\n\n'
            f'{mensaje}\n\n'
            'Te contactaremos en breve.'
        )

        try:
            send_mail(
                'Formulario de Contacto',
                mensaje_completo,
                settings.EMAIL_HOST_USER,  # Desde la dirección de correo electrónico configurada en settings.py
                [correo, destinatario],  # Lista de destinatarios (destinatario principal y copia al remitente)
                fail_silently=False,
            )
            return JsonResponse({'mensaje': 'Correo enviado correctamente.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Datos incompletos proporcionados.'}, status=400)
