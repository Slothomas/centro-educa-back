from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.http import JsonResponse
from django.utils import timezone


@api_view(['POST'])
def datosEstudiante(request):
    # Obtener el rut del estudiante de los parámetros del cuerpo de la solicitud POST
    rut_estudiante = request.data.get('rutEstudiante_str')
    
    if not rut_estudiante:
        return JsonResponse({"error": "rutEstudiante_str no proporcionado"}, status=400)

    # Ejecutar la consulta SQL
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT e.rut_str, e.nombres_str, c.idCurso_int, c.nivelCurso_str, c.letraCurso_str
                FROM estudiante e
                LEFT JOIN cursoEstudiante ce ON e.rut_str = ce.rutEstudiante_str
                LEFT JOIN curso c ON ce.idCurso_int = c.idCurso_int
                WHERE e.rut_str = %s
            """, [rut_estudiante])
            rows = cursor.fetchall()

        # Procesar los resultados y convertirlos en una estructura de datos adecuada
        results = []
        for row in rows:
            result = {
                'rut_str': row[0],
                'nombres_str': row[1],
                'idCurso_int': row[2],
                'nivelCurso_str': row[3],
                'letraCurso_str': row[4]
            }
            results.append(result)

        # Devolver los datos en formato JSON
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['POST'])
def resumeAsignaturas(request):
    # Obtener el rut del estudiante y el ID del curso de los parámetros del cuerpo de la solicitud POST
    rut_estudiante = request.data.get('rutEstudiante_str')
    id_curso = request.data.get('idCurso_int')

    if not rut_estudiante or not id_curso:
        return JsonResponse({"error": "Parámetros no proporcionados"}, status=400)

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
                    LEFT JOIN asignatura asig ON a.idAsignatura_int = asig.idAsignatura_int
                    LEFT JOIN cursoEstudiante ce ON a.rutEstudiante_str = ce.rutEstudiante_str
                WHERE 
                    a.rutEstudiante_str = %s
                    AND asig.idTipoEstado_int = 1
                    AND ce.idCurso_int = %s
                GROUP BY 
                    a.idAsignatura_int, a.rutEstudiante_str, ce.idCurso_int
                ORDER BY 
                    Nombre
            """, [rut_estudiante, id_curso])
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


@api_view(['POST'])
def resumeNotas(request):
    
    rut_estudiante = request.data.get('rutEstudiante_str')
    id_curso = request.data.get('idCurso_int')

    if not rut_estudiante or not id_curso:
        return JsonResponse({"error": "Parámetros no proporcionados"}, status=400)

    query = """
        SELECT 
            a.nombre_str as Nombre_Asignatura,
            n.rutEstudiante_str AS Rut_Estudiante, 
            n.idAsignatura_int AS Asignatura, 
            n.nombre_str AS Evaluacion, 
            n.valor_flo AS Nota, 
            ca.idCurso_int AS Id_Curso, 
            n.fechaRegistro_dat,
            ROUND((SELECT AVG(n2.valor_flo) 
             FROM nota n2
             LEFT JOIN cursoAsignatura ca2 ON n2.idAsignatura_int = ca2.idAsignatura_int
             WHERE ca2.idCurso_int = ca.idCurso_int
             AND n2.idAsignatura_int = n.idAsignatura_int
             AND n2.nombre_str = n.nombre_str),1) AS Promedio_Evaluacion
        FROM 
            nota n
        LEFT JOIN 
            cursoAsignatura ca ON n.idAsignatura_int = ca.idAsignatura_int
        LEFT JOIN 
            asignatura a ON ca.idAsignatura_int = a.idAsignatura_int
        WHERE 
            ca.idCurso_int = %s
            AND n.rutEstudiante_str = %s
        ORDER BY 
            n.idAsignatura_int, n.nombre_str;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [id_curso, rut_estudiante])
        rows = cursor.fetchall()

    results = []
    for row in rows:
        results.append({
            'Nombre_Asignatura': row[0],
            'Rut_Estudiante': row[1],
            'Asignatura': row[2],
            'Evaluacion': row[3],
            'Nota': row[4],
            'Id_Curso': row[5],
            'fechaRegistro_dat': row[6],
            'Promedio_Evaluacion': row[7],
        })

    return JsonResponse(results, safe=False)



@api_view(['POST'])
def proximosFeed(request):
    
    rut_estudiante = request.data.get('rutEstudiante_str')

    if not rut_estudiante:
        return JsonResponse({"error": "rutEstudiante_str no proporcionado"}, status=400)

    query = """
        SELECT *
        FROM (
            SELECT 
                e.descripcion as Descripcion,
                e.fechaEvento_dat as Fecha,
                e.lugarEvento_str as Lugar,
                a.nombre_str as Nombre_Asignatura,
                te.nombre_str as Categoria_Evento
            FROM evento e
            LEFT JOIN asignatura a ON e.idAsignatura_int = a.idAsignatura_int
            LEFT JOIN tipoevento te ON e.idTipoEvento_int = te.idTipoEvento_int
            WHERE e.rutEstudiante_str = %s
            AND e.fechaEvento_dat > GETDATE()

            UNION ALL

            SELECT DISTINCT 
                n.nombre_str as Descripcion,
                n.fechaEvaluacion_dat as Fecha,
                CONCAT(ts.nombre_str,' ',CAST(s.numero_int AS varchar)) as Lugar,
                a.nombre_str as Nombre_Asignatura,
                'Evaluacion' as Categoria_Evento
            FROM nota n
            LEFT JOIN asignatura a ON n.idAsignatura_int = a.idAsignatura_int
            LEFT JOIN horario h ON a.idAsignatura_int = h.idAsignatura_int 
                AND DATEPART(WEEKDAY, n.fechaEvaluacion_dat) = h.idDiaSemana_int
            LEFT JOIN sala s ON h.idSala_int = s.numero_int
            LEFT JOIN tiposala ts ON s.idTipoSala_int = ts.idTipoSala_int
            WHERE n.rutEstudiante_str = %s
            AND n.fechaEvaluacion_dat > GETDATE()
        ) AS eventos_notas
        ORDER BY Fecha;
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [rut_estudiante, rut_estudiante])
            rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                'Descripcion': row[0],
                'Fecha': row[1],
                'Lugar': row[2],
                'Nombre_Asignatura': row[3],
                'Categoria_Evento': row[4]
            })

        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
    
@api_view(['POST'])
def resumeSemanal(request):
    
    rut_estudiante = request.data.get('rutEstudiante_str')
    id_Curso = request.data.get('idCurso_int')

    if not rut_estudiante:
        return JsonResponse({"error": "rutEstudiante_str no proporcionado"}, status=400)

    if not id_Curso:
        return JsonResponse({"error": "id_Curso no proporcionado"}, status=400)

    query = """
        SELECT DISTINCT
            h.idBloque_int as Bloque,
            h.idDiaSemana_int as Dia_Semana,
            a.nombre_str as Nombre_Asignatura,
            CONCAT(ts.nombre_str, ' ', CAST(s.numero_int AS varchar)) as Lugar,
            b.horaInicio_tim as Hora_Inicio,
            b.horaFin_tim as Hora_Fin
        FROM horario h
        LEFT JOIN asignaturaestudiante ae ON h.idAsignatura_int = ae.idAsignatura_int
        LEFT JOIN asignatura a ON h.idAsignatura_int = a.idAsignatura_int
        LEFT JOIN sala s ON h.idSala_int = s.idSala_int
        LEFT JOIN tiposala ts ON s.idTipoSala_int = ts.idTipoSala_int
        LEFT JOIN bloque b ON b.idBloque_int = h.idBloque_int
        WHERE ae.rutEstudiante_str = %s
        AND a.idTipoEstado_int = 1
        AND ae.idCurso_int = %s
        ORDER BY h.idDiaSemana_int, h.idBloque_int
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [rut_estudiante, id_Curso])
            rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                'Bloque': row[0],
                'Dia_Semana': row[1],
                'Nombre_Asignatura': row[2],
                'Lugar': row[3],
                'Hora_Inicio': row[4],
                'Hora_Fin': row[5]
            })

        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




