## appestudiantes/
from django.shortcuts import get_object_or_404
from appestudiantes.models import Estudiante
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.permissions import AllowAny # type: ignore
from appcursos.serializers import EstudianteCursoSerializer



# Vista para el serivicio estudiantes. 
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
                
                SELECT TOP 1
                e.rut_str, e.nombres_str, c.idCurso_int, c.nivelCurso_str, c.letraCurso_str
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


# Vistas para mostar datos en el resumen del dashboard del estudiante
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
                    a.idAsignatura_int as ID_Asignatura,
                    (SELECT nombre_str FROM asignatura WHERE idAsignatura_int = a.idAsignatura_int) AS Nombre, 
                    SUM(CASE WHEN a.idTipoEstado_int = 5 THEN 1 ELSE 0 END) AS Clases_Presentes,
                    SUM(CASE WHEN a.idTipoEstado_int = 6 THEN 1 ELSE 0 END) AS Clases_Ausentes,
                    COUNT(*) AS Clases_Totales,
                    (SUM(CASE WHEN a.idTipoEstado_int = 5 THEN 1 ELSE 0 END) * 100) / NULLIF(COUNT(*), 0) AS Porcentaje_Asistencia,
                    (SELECT TOP 1 n.valor_flo
                     FROM nota n
                     WHERE n.idAsignatura_int = a.idAsignatura_int
                     AND n.rutEstudiante_str = a.rutEstudiante_str
                     AND n.valor_flo IS NOT NULL
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
                'ID_Asignatura': row[0],
                'Nombre': row[1],
                'Clases_Presentes': row[2],
                'Clases_Ausentes': row[3],
                'Clases_Totales': row[4],
                'Porcentaje_Asistencia': row[5],
                'Ultima_Nota': row[6]
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
                    LEFT JOIN cursoEstudiante ce2 ON n2.rutEstudiante_str = ce2.rutEstudiante_str
                    WHERE ca2.idCurso_int = ca.idCurso_int
                        AND n2.idAsignatura_int = n.idAsignatura_int
                        AND n2.nombre_str = n.nombre_str
                        AND ce2.idCurso_int = ca.idCurso_int), 1) AS Promedio_Evaluacion
            FROM 
                nota n
            LEFT JOIN 
                cursoAsignatura ca ON n.idAsignatura_int = ca.idAsignatura_int
            LEFT JOIN 
                asignatura a ON ca.idAsignatura_int = a.idAsignatura_int
            LEFT JOIN 
                cursoEstudiante ce ON n.rutEstudiante_str = ce.rutEstudiante_str
            WHERE 
                ca.idCurso_int = %s -- este es el parámetro que se obtiene de los datos del estudiante del EstudiantesService.
                AND ce.idCurso_int = %s -- para asegurarnos de que solo se consideren estudiantes del mismo curso
                AND n.rutEstudiante_str = %s -- este parámetro también se obtiene del EstudiantesService.
                AND n.valor_flo IS NOT NULL
            ORDER BY 
                n.idAsignatura_int;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [id_curso, id_curso,rut_estudiante])
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
        SELECT TOP 5 *
        FROM (
            SELECT 
                e.descripcion AS Descripcion,
                e.fechaEvento_dat AS Fecha,
                e.lugarEvento_str AS Lugar,
                a.nombre_str AS Nombre_Asignatura,
                te.nombre_str AS Categoria_Evento
            FROM evento e
            LEFT JOIN eventoEstudiante ee ON e.idEvento_int = ee.idEvento_int
            LEFT JOIN asignatura a ON e.idAsignatura_int = a.idAsignatura_int
            LEFT JOIN tipoEvento te ON e.idTipoEvento_int = te.idTipoEvento_int
            WHERE ee.rutEstudiante_str = %s
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


# Vistas para los compoentnes del modulo asignaturas del dashboard estudiante
@api_view(['POST'])
def detalleAsignatura(request):
    
    rut_estudiante = request.data.get('rutEstudiante_str')
    id_Curso = request.data.get('idCurso_int')
    id_Asignatura = request.data.get('idAsignatura_int')

    if not rut_estudiante:
        return JsonResponse({"error": "rutEstudiante_str no proporcionado"}, status=400)

    if not id_Curso:
        return JsonResponse({"error": "idCurso_int no proporcionado"}, status=400)

    if not id_Asignatura:
        return JsonResponse({"error": "idAsignatura_int no proporcionado"}, status=400)

    query = """
        SELECT 
            a.idAsignatura_int as ID_Asignatura,
            a.nombre_str as Nombre_Asignatura,
            a.descripcion_str as Descripcion_Asignatura,
            ta.nombre_str as Tipo_Asignatura,
            CONCAT(p.nombres_str,' ', p.apellidos_str) as Nombre_Profesor,
            p.correo_str as Correo_Profesor,
            p.descripcion_str as Descripcion_Profesor
        FROM asignatura a
        LEFT JOIN asignaturaEstudiante ae ON a.idAsignatura_int = ae.idAsignatura_int
        LEFT JOIN profesor p ON a.rutProfesor_str = p.rut_str
        LEFT JOIN tipoAsignatura ta ON a.idTipoAsignatura_int = ta.idTipoAsignatura_int
        WHERE ae.rutEstudiante_str = %s 
        AND ae.idCurso_int = %s 
        AND a.idTipoEstado_int = 1 
        AND a.idAsignatura_int = %s
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [rut_estudiante, id_Curso, id_Asignatura])
            rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                'ID_Asignatura': row[0],
                'Nombre_Asignatura': row[1],
                'Descripcion_Asignatura': row[2],
                'Tipo_Asignatura': row[3],
                'Nombre_Profesor': row[4],
                'Correo_Profesor': row[5],
                'Descripcion_Profesor': row[6]
            })

        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
@api_view(['POST'])
def detalleCompaneros(request):
    
    id_Curso = request.data.get('idCurso_int')
    id_Asignatura = request.data.get('idAsignatura_int')
    rut_estudiante = request.data.get('rutEstudiante_str')

    if not id_Curso:
        return JsonResponse({"error": "idCurso_int no proporcionado"}, status=400)

    if not id_Asignatura:
        return JsonResponse({"error": "idAsignatura_int no proporcionado"}, status=400)

    if not rut_estudiante:
        return JsonResponse({"error": "rutEstudiante_str no proporcionado"}, status=400)

    query = """
        SELECT
            CONCAT(e.nombres_str,' ',e.apellidos_str) as Nombre_Companero,
            e.correo_str as Correo
        FROM 
            cursoEstudiante ce
        LEFT JOIN 
            cursoAsignatura ca ON ce.idCurso_int = ca.idCurso_int
        LEFT JOIN 
            estudiante e ON ce.rutEstudiante_str = e.rut_str
        WHERE
            ce.idCurso_int = %s
            AND ce.rutEstudiante_str NOT IN ( %s )
            AND ca.idAsignatura_int = %s
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [id_Curso, rut_estudiante, id_Asignatura])
            rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                'Nombre_Companero': row[0],
                'Correo': row[1]
            })

        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

@api_view(['POST'])
def detallePromedioNotaAsistencia(request):
    
    id_Curso = request.data.get('idCurso_int')
    id_Asignatura = request.data.get('idAsignatura_int')
    rut_estudiante = request.data.get('rutEstudiante_str')

    if not id_Curso:
        return JsonResponse({"error": "idCurso_int no proporcionado"}, status=400)

    if not id_Asignatura:
        return JsonResponse({"error": "idAsignatura_int no proporcionado"}, status=400)

    if not rut_estudiante:
        return JsonResponse({"error": "rutEstudiante_str no proporcionado"}, status=400)

    query = """
        SELECT
            n.idAsignatura_int AS Id_Asignatura, 
            a.nombre_str as Nombre_Asignatura,
            ROUND(SUM(n.valor_flo * n.ponderacion_int) / SUM(n.ponderacion_int),1) AS Registro,
            'Promedio' as Tipo
        FROM 
            nota n
        LEFT JOIN 
            cursoAsignatura ca ON n.idAsignatura_int = ca.idAsignatura_int
        LEFT JOIN 
            asignatura a ON ca.idAsignatura_int = a.idAsignatura_int
        WHERE 
            ca.idCurso_int = %s
            AND n.rutEstudiante_str = %s
            AND ca.idAsignatura_int = %s
            AND n.valor_flo IS NOT NULL
        GROUP BY 
            a.nombre_str,n.idAsignatura_int

        UNION ALL

        SELECT 
            asis.idAsignatura_int AS Id_Asignatura, 
            a.nombre_str as Nombre_Asignatura,
            CAST(ROUND(SUM(CASE WHEN asis.idTipoEstado_int = 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 0) AS DECIMAL(5,1)) AS Registro,
            'Asistencia' as Tipo
        FROM 
            asistencia asis
        LEFT JOIN 
            cursoAsignatura ca ON asis.idAsignatura_int = ca.idAsignatura_int
        LEFT JOIN 
            asignatura a ON ca.idAsignatura_int = a.idAsignatura_int
        WHERE 
            ca.idCurso_int = %s
            AND asis.rutEstudiante_str = %s
            AND asis.idAsignatura_int = %s
        GROUP BY 
            a.nombre_str,asis.idAsignatura_int
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [id_Curso, rut_estudiante, id_Asignatura, id_Curso, rut_estudiante, id_Asignatura])
            rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                'Id_Asignatura': row[0],
                'Nombre_Asignatura': row[1],
                'Registro': row[2],
                'Tipo': row[3]
            })

        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
@api_view(['POST'])
def detallePromedioAsignaturas(request):
    
    id_Curso = request.data.get('idCurso_int')
    rut_estudiante = request.data.get('rutEstudiante_str')

    if not id_Curso:
        return JsonResponse({"error": "idCurso_int no proporcionado"}, status=400)

    if not rut_estudiante:
        return JsonResponse({"error": "rutEstudiante_str no proporcionado"}, status=400)

    query = """
        SELECT
            n.idAsignatura_int AS Id_Asignatura, 
            a.nombre_str as Nombre_Asignatura,
            ROUND(SUM(n.valor_flo * n.ponderacion_int) / SUM(n.ponderacion_int),1) AS Registro,
            'Promedio Notas' as Tipo
        FROM 
            nota n
        LEFT JOIN 
            cursoAsignatura ca ON n.idAsignatura_int = ca.idAsignatura_int
        LEFT JOIN 
            asignatura a ON ca.idAsignatura_int = a.idAsignatura_int
        WHERE 
            ca.idCurso_int = %s
            AND n.rutEstudiante_str = %s
            AND n.valor_flo IS NOT NULL
        GROUP BY 
            a.nombre_str,n.idAsignatura_int
        ORDER BY Registro DESC
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [id_Curso, rut_estudiante])
            rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                'Id_Asignatura': row[0],
                'Nombre_Asignatura': row[1],
                'Registro': row[2],
                'Tipo': row[3]
            })

        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
@api_view(['POST'])
def detalleRegistrosNotasAsignaturas(request):
    
    id_Curso = request.data.get('idCurso_int')
    id_Asignatura = request.data.get('idAsignatura_int')
    rut_estudiante = request.data.get('rutEstudiante_str')

    if not id_Curso:
        return JsonResponse({"error": "idCurso_int no proporcionado"}, status=400)

    if not id_Asignatura:
        return JsonResponse({"error": "idAsignatura_int no proporcionado"}, status=400)

    if not rut_estudiante:
        return JsonResponse({"error": "rutEstudiante_str no proporcionado"}, status=400)

    query = """
    SELECT 
        n.idAsignatura_int AS Asignatura, 
        a.nombre_str as Nombre_Asignatura,
        n.nombre_str AS Tipo, 
        n.ponderacion_int as Ponderacion, 
        n.valor_flo AS Registro, 
        ROUND((SELECT AVG(n2.valor_flo) 
        FROM nota n2
        LEFT JOIN cursoAsignatura ca2 ON n2.idAsignatura_int = ca2.idAsignatura_int
        WHERE ca2.idCurso_int = ca.idCurso_int
        AND n2.idAsignatura_int = n.idAsignatura_int
        AND n2.nombre_str = n.nombre_str),1) AS Promedio,
        n.fechaEvaluacion_dat as Fecha
    FROM 
        nota n
    LEFT JOIN 
        cursoAsignatura ca ON n.idAsignatura_int = ca.idAsignatura_int
    LEFT JOIN 
        asignatura a ON ca.idAsignatura_int = a.idAsignatura_int
    WHERE 
        ca.idCurso_int = %s -- este es el parámetro que se obtiene de los datos del estudiante del EstudiantesService.
        AND n.rutEstudiante_str = %s -- este parametro tambien se obtiene del EstudiantesService.
        AND ca.idAsignatura_int = %s

    UNION ALL

    SELECT 
        asis.idAsignatura_int AS Asignatura, 
        a.nombre_str as Nombre_Asignatura,
        'Asistencia' AS Tipo, 
        null as Ponderacion, 
        asis.idTipoEstado_int AS Registro, 
        null as Promedio,
        asis.fechaRegistro_dat as Fecha
    FROM 
        asistencia asis
    LEFT JOIN 
        cursoAsignatura ca ON asis.idAsignatura_int = ca.idAsignatura_int
    LEFT JOIN 
        asignatura a ON ca.idAsignatura_int = a.idAsignatura_int
    LEFT JOIN 
        tipoEstado te ON asis.idTipoEstado_int = te.idTipoEstado_int
    WHERE 
        ca.idCurso_int = %s -- este es el parámetro que se obtiene de los datos del estudiante del EstudiantesService.
        AND asis.rutEstudiante_str = %s -- este parametro tambien se obtiene del EstudiantesService.
        AND asis.idAsignatura_int = %s --este paremetro se obtiene del componente asignatura al igual que la sidenav.
    ORDER BY TIPO ASC, FECHA ASC
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [id_Curso, rut_estudiante, id_Asignatura, id_Curso, rut_estudiante, id_Asignatura])
            rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                'Asignatura': row[0],
                'Nombree_Asignatura': row[1],
                'Tipo': row[2],
                'Ponderacion': row[3],
                'Registro': row[4],
                'Promedio': row[5],
                'Fecha': row[6]
            })

        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['POST'])
def detalleNotas(request):
    
    rut_estudiante = request.data.get('rutEstudiante_str')
    id_curso = request.data.get('idCurso_int')
    id_Asignatura = request.data.get('idAsignatura_int')


    if not rut_estudiante or not id_curso or not id_Asignatura:
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
                    LEFT JOIN cursoEstudiante ce2 ON n2.rutEstudiante_str = ce2.rutEstudiante_str
                    WHERE ca2.idCurso_int = ca.idCurso_int
                        AND n2.idAsignatura_int = n.idAsignatura_int
                        AND n2.nombre_str = n.nombre_str
                        AND ce2.idCurso_int = ca.idCurso_int), 1) AS Promedio_Evaluacion
            FROM 
                nota n
            LEFT JOIN 
                cursoAsignatura ca ON n.idAsignatura_int = ca.idAsignatura_int
            LEFT JOIN 
                asignatura a ON ca.idAsignatura_int = a.idAsignatura_int
            LEFT JOIN 
                cursoEstudiante ce ON n.rutEstudiante_str = ce.rutEstudiante_str
            WHERE 
                ca.idCurso_int = %s -- este es el parámetro que se obtiene de los datos del estudiante del EstudiantesService.
                AND ce.idCurso_int = %s -- para asegurarnos de que solo se consideren estudiantes del mismo curso
                AND n.rutEstudiante_str = %s -- este parámetro también se obtiene del EstudiantesService.
                AND n.valor_flo IS NOT NULL
                AND n.idAsignatura_int = %s
            ORDER BY 
                n.idAsignatura_int;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [id_curso, id_curso, rut_estudiante, id_Asignatura])
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


# Módulo Eventos
@api_view(['POST'])
def detalleEventos(request):
    
    rut_estudiante = request.data.get('rutEstudiante_str')

    if not rut_estudiante:
        return JsonResponse({"error": "Parámetros no proporcionados"}, status=400)

    query = """
        ;WITH Event_Count AS (
            SELECT 
                ee2.idEvento_int,
                COUNT(*) AS Cantidad_Estudiantes
            FROM eventoEstudiante ee2
            GROUP BY ee2.idEvento_int
        ),
        Student_Events AS (
            SELECT 
                e.idEvento_int AS Id_Evento,
                a.nombre_str AS Nombre_Asignatura,
                te.nombre_str AS Tipo,
                e.lugarEvento_str AS Lugar,
                e.fechaEvento_dat AS Fecha,
                e.descripcion AS Descripcion,
                COALESCE(ec.Cantidad_Estudiantes, 0) AS Cantidad_Estudiantes,
                1 AS Mi_Evento
            FROM evento e
            LEFT JOIN eventoEstudiante ee ON e.idEvento_int = ee.idEvento_int
            LEFT JOIN asignatura a ON e.idAsignatura_int = a.idAsignatura_int
            LEFT JOIN tipoEvento te ON e.idTipoEvento_int = te.idTipoEvento_int
            LEFT JOIN Event_Count ec ON e.idEvento_int = ec.idEvento_int
            WHERE ee.rutEstudiante_str = %s
            AND a.idTipoEstado_int = 1
        ),
        Upcoming_Events AS (
            SELECT 
                e.idEvento_int AS Id_Evento,
                a.nombre_str AS Nombre_Asignatura,
                te.nombre_str AS Tipo,
                e.lugarEvento_str AS Lugar,
                e.fechaEvento_dat AS Fecha,
                e.descripcion AS Descripcion,
                COALESCE(ec.Cantidad_Estudiantes, 0) AS Cantidad_Estudiantes,
                0 AS Mi_Evento
            FROM evento e
            LEFT JOIN asignatura a ON e.idAsignatura_int = a.idAsignatura_int
            LEFT JOIN tipoEvento te ON e.idTipoEvento_int = te.idTipoEvento_int
            LEFT JOIN Event_Count ec ON e.idEvento_int = ec.idEvento_int
            WHERE a.idTipoEstado_int = 1
            AND e.idEvento_int NOT IN (
                SELECT ee.idEvento_int
                FROM eventoEstudiante ee
                WHERE ee.rutEstudiante_str = %s
            )
        )
        SELECT * FROM Student_Events
        UNION ALL
        SELECT * FROM Upcoming_Events
        ORDER BY Fecha;
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [rut_estudiante, rut_estudiante])
            rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                'Id_Evento': row[0],
                'Nombre_Asignatura': row[1],
                'Tipo': row[2],
                'Lugar': row[3],
                'Fecha': row[4],
                'Descripcion': row[5],
                'Cantidad_Estudiantes': row[6],
                'Mi_Evento': row[7]
            })

        return JsonResponse(results, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@api_view(['PUT'])
def inscripcionEvento(request):
    
    rut_estudiante = request.data.get('rutEstudiante_str')
    id_evento = request.data.get('idEvento_int')

    if not rut_estudiante or not id_evento:
        return JsonResponse({"error": "Parámetros no proporcionados"}, status=400)

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO eventoEstudiante (idEvento_int, rutEstudiante_str)
                VALUES (%s, %s)
            """, [id_evento, rut_estudiante])

        return JsonResponse({"message": "Inscripción exitosa"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
#Module Observaciones
@api_view(['POST'])
def detalleObservaciones(request):
    rut_estudiante = request.data.get('rutEstudiante_str')

    if not rut_estudiante:
        return JsonResponse({"error": "Parámetros no proporcionados"}, status=400)

    query = """
        SELECT 
            o.descripcion AS Descripcion_Observacion,
            o.fechaRegistro_dat AS Fecha_Registro,
            a.nombre_str AS Nombre_Asignatura,
            too.nombre_str AS Tipo_Observacion,
            CONCAT(p.nombres_str, ' ', p.apellidos_str) AS Nombre_Profesor
        FROM observacion o
        LEFT JOIN asignatura a ON o.idAsignatura_int = a.idAsignatura_int
        LEFT JOIN tipoObservacion too ON o.idTipoObservacion_int = too.idTipoObservacion_int
        LEFT JOIN profesor p ON o.usuarioModificacion_str = p.rut_str
        WHERE o.rutEstudiante_str = %s
        AND a.idTipoEstado_int = 1
        
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [rut_estudiante])
        rows = cursor.fetchall()

    results = []
    for row in rows:
        results.append({
            'Descripcion_Observacion': row[0],
            'Fecha_Registro': row[1],
            'Nombre_Asignatura': row[2],
            'Tipo_Observacion': row[3],
            'Nombre_Profesor': row[4],
        })

    return JsonResponse(results, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def estudiante_con_curso(request):
    rut_estudiante = request.GET.get('rutEstudiante_str')

    if not rut_estudiante:
        return Response({"error": "Parámetro rutEstudiante_str no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        estudiante = Estudiante.objects.get(rut_str=rut_estudiante)
    except Estudiante.DoesNotExist:
        return Response({"error": "Estudiante no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    serializer = EstudianteCursoSerializer(estudiante)
    return Response(serializer.data, status=status.HTTP_200_OK)