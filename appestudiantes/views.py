from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.http import JsonResponse

@api_view(['POST'])
def resumeAsignaturas(request):
    # Obtener el rut del estudiante de los parámetros del cuerpo de la solicitud POST
    rut_estudiante = request.data.get('rutEstudiante_str')
    
    if not rut_estudiante:
        return JsonResponse({"error": "rutEstudiante_str no proporcionado"}, status=400)

    # Ejecutar la consulta SQL
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    (SELECT nombre_str FROM asignatura WHERE idAsignatura_int = a.idAsignatura_int) AS Nombre, 
                    SUM(CASE WHEN a.idTipoEstado_int = 5 THEN 1 ELSE 0 END) AS Clases_Presentes,
                    SUM(CASE WHEN a.idTipoEstado_int = 6 THEN 1 ELSE 0 END) AS Clases_Ausentes,
                    COUNT(*) AS Clases_Totales,
                    (SUM(CASE WHEN a.idTipoEstado_int = 5 THEN 1 ELSE 0 END) * 100) / NULLIF(COUNT(*), 0) AS Porcentaje_Asistencia,
                    (SELECT TOP 1 n.valor_flo
                     FROM nota n
                     WHERE n.idAsignatura_int = a.idAsignatura_int
                     AND n.rutEstudiante_str = a.rutEstudiante_str
                     ORDER BY n.fechaRegistro_dat DESC) AS Ultima_Nota
                FROM 
                    asistencia a
                WHERE 
                    a.rutEstudiante_str = %s
                GROUP BY 
                    a.idAsignatura_int, a.rutEstudiante_str
                ORDER BY 
                    Nombre
            """, [rut_estudiante])
            rows = cursor.fetchall()

        # Procesar los resultados y convertirlos en una estructura de datos adecuada
        results = []
        for row in rows:
            result = {
                'Nombre': row[0],
                'Clases_Presentes': row[1],
                'Clases_Ausentes': row[2],
                'Clases_Totales': row[3],
                'Porcentaje_Asistencia': row[4],
                'Ultima_Nota': row[5]
            }
            results.append(result)

        # Devolver los datos en formato JSON
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
