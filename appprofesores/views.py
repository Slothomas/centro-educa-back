import os
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response # type: ignore
from rest_framework import status # type: ignore
from .models import Profesor
from .serializers import ProfesorSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.db import connection, transaction
import datetime
from django.utils import timezone


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
    

@api_view(['POST'])
def datosProfesor(request):

    rut_profesor = request.data.get('rutProfesor_str')
    
    if not rut_profesor:
        return JsonResponse({"error": "rutEstudiante_str no proporcionado"}, status=400)

    # Ejecutar la consulta SQL
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                
                SELECT 
	                p.rut_str, p.nombres_str, p.apellidos_str
                FROM profesor p
                WHERE p.rut_str = %s
            """, [rut_profesor])
            rows = cursor.fetchall()

        # Procesar los resultados y convertirlos en una estructura de datos adecuada
        results = []
        for row in rows:
            result = {
                'rut_str': row[0],
                'nombres_str': row[1],
                'apellidos_str': row[2]
            }
            results.append(result)

        # Devolver los datos en formato JSON
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['POST'])
def resumeAsignaturas(request):

    profesor = request.data.get('rutProfesor_str')
        
        
        #Ejecutar Query de SQL
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                    SELECT 
                        c.idCurso_int as ID_Curso,
                        CONCAT(c.nivelCurso_str,' ',c.letraCurso_str) AS Nombre_Curso,
						a.idAsignatura_int AS ID_Asignatura,
						a.nombre_str AS Nombre_Asignatura,
                        COUNT(ae.rutEstudiante_str) AS Cantidad_Alumnos
                    FROM profesor p
                    LEFT JOIN asignatura a ON p.rut_str = a.rutProfesor_str
                    LEFT JOIN cursoAsignatura ca ON a.idAsignatura_int = ca.idAsignatura_int
                    LEFT JOIN curso c ON ca.idCurso_int = c.idCurso_int
                    LEFT JOIN asignaturaestudiante ae ON a.idAsignatura_int = ae.idAsignatura_int AND ca.idCurso_int = ae.idCurso_int
                    WHERE p.rut_str = %s
                    AND a.idTipoEstado_int = 1
                    AND ca.idCurso_int IS NOT NULL
                    GROUP BY c.idCurso_int,a.nombre_str, c.nivelCurso_str, c.letraCurso_str,a.idAsignatura_int
                    ORDER BY Nombre_Curso, Nombre_Asignatura;
                    """
                    , [profesor])
            rows = cursor.fetchall()
            
        results = []
        for row in rows:
            result = {
                "ID_Curso": row[0],
                "Nombre_Curso": row[1],
                "ID_Asignatura": row[2],
                "Nombre_Asignatura": row[3],
                "Cantidad_Alumnos": row[4]
            }
            results.append(result)
                
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
@api_view(['POST'])
def resumeSemanal(request):
    
    rut_profesor = request.data.get('rutProfesor_str')
    
    if not rut_profesor:
        return JsonResponse({"error": "rutProfesor_str no proporcionado"}, status=400)
        
        
    query = """
        SELECT DISTINCT
            h.idBloque_int as Bloque,
            h.idDiaSemana_int as Dia_Semana,
            a.nombre_str as Nombre_Asignatura,
            CONCAT(ts.nombre_str, ' ', CAST(s.numero_int AS varchar)) as Lugar,
            b.horaInicio_tim as Hora_Inicio,
            b.horaFin_tim as Hora_Fin,
            CONCAT(c.nivelCurso_str, ' ', c.letraCurso_str) as Curso        
        FROM 
            horario h
        INNER JOIN 
            asignatura a ON h.idAsignatura_int = a.idAsignatura_int
        INNER JOIN 
            curso c ON h.idCurso_int = c.idCurso_int
        LEFT JOIN 
            sala s ON h.idSala_int = s.idSala_int
        LEFT JOIN 
            tiposala ts ON s.idTipoSala_int = ts.idTipoSala_int
        LEFT JOIN 
            bloque b ON b.idBloque_int = h.idBloque_int
        WHERE 
            a.rutProfesor_str = %s -- este debe ser dinámico entregado por la solicitud HTTP
            AND a.idTipoEstado_int = 1 -- debe estar seteado en 1 para cursos activos
        ORDER BY 
            h.idDiaSemana_int, h.idBloque_int;
    """
            
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [rut_profesor])
            rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append ({
                "Bloque": row[0],
                "Dia_Semana": row[1],
                "Nombre_Asignatura": row[2],
                "Lugar": row[3],
                "Hora_Inicio": row[4],
                "Hora_Fin": row[5],
                "Curso": row[6],
                
            })
            
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
            
        
@api_view(['POST'])
def resumeNotas(request):
        
    rut_profesor = request.data.get('rutProfesor_str')
        
    if not rut_profesor:
            return JsonResponse({"error": "rutProfesor_str no proporcionado"}, status=400)
            
    query = """
            SELECT 
                c.idCurso_int AS ID_Curso,
                a.idAsignatura_int AS ID_Asignatura,
                CONCAT(c.nivelCurso_str, ' ', c.letraCurso_str) AS Nombre_Curso,
                a.nombre_str AS Nombre_Asignatura,
                ROUND(AVG(n.valor_flo), 1) AS Promedio_Nota,
                CAST(ROUND(SUM(CASE WHEN asis.idTipoEstado_int = 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS DECIMAL(5,1)) AS Porcentaje_Asistencia
            FROM 
                nota n 
            INNER JOIN 
                cursoEstudiante ce ON n.rutEstudiante_str = ce.rutEstudiante_str
            INNER JOIN 
                asignatura a ON n.idAsignatura_int = a.idAsignatura_int
            INNER JOIN 
                curso c ON ce.idCurso_int = c.idCurso_int
            LEFT JOIN
                asistencia asis ON n.rutEstudiante_str = asis.rutEstudiante_str
                AND n.idAsignatura_int = asis.idAsignatura_int
            WHERE
                a.rutProfesor_str = %s
                AND a.idTipoEstado_int = 1
                AND n.isActived_int = 1
            GROUP BY
                c.idCurso_int,
                a.idAsignatura_int,
                c.nivelCurso_str,
                c.letraCurso_str,
                a.nombre_str
            ORDER BY ID_Curso;
            """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [rut_profesor])
            rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "ID_Curso": row[0],
                "ID_Asignatura": row[1],
                "Nombre_Curso": row[2],
                "Nombre_Asignatura": row[3],
                "Promedio_Nota": row[4],
                "Porcentaje_Asistencia": row[5]
            })
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['POST'])
def resumeProximos(request):

    rut_prfoesor = request.data.get('rutProfesor_str')
    
    if not rut_prfoesor:
        return JsonResponse({"error": "rutProfesor_str no proporcionado"}, status=400)
    
    query = """
            WITH Eventos AS (
            SELECT 
                e.descripcion AS Descripcion,
                e.fechaEvento_dat AS Fecha,
                e.lugarEvento_str AS Lugar,
                CONCAT(c.nivelCurso_str, ' ', c.letraCurso_str) AS Curso,
                a.nombre_str AS Nombre_Asignatura,
                te.nombre_str AS Categoria_Evento
            FROM 
                evento e
            INNER JOIN 
                asignatura a ON e.idAsignatura_int = a.idAsignatura_int
            INNER JOIN 
                tipoevento te ON e.idTipoEvento_int = te.idTipoEvento_int
            INNER JOIN 
                cursoAsignatura ca ON a.idAsignatura_int = ca.idAsignatura_int
            INNER JOIN 
                curso c ON ca.idCurso_int = c.idCurso_int
            WHERE 
                a.rutProfesor_str = %s
                AND e.fechaEvento_dat > GETDATE()
                AND a.idTipoEstado_int = 1
        ), Evaluaciones AS (
            SELECT DISTINCT
                n.nombre_str AS Descripcion,
                n.fechaEvaluacion_dat AS Fecha,
                CONCAT(ts.nombre_str, ' ', CAST(s.numero_int AS varchar)) AS Lugar,
                CONCAT(c.nivelCurso_str, ' ', c.letraCurso_str) AS Curso,
                a.nombre_str AS Nombre_Asignatura,
                'Evaluacion' AS Categoria_Evento
            FROM 
                nota n
            INNER JOIN 
                asignatura a ON n.idAsignatura_int = a.idAsignatura_int
            INNER JOIN 
                cursoAsignatura ca ON a.idAsignatura_int = ca.idAsignatura_int
            INNER JOIN 
                curso c ON ca.idCurso_int = c.idCurso_int
            LEFT JOIN 
                horario h ON a.idAsignatura_int = h.idAsignatura_int 
                AND DATEPART(WEEKDAY, n.fechaEvaluacion_dat) = h.idDiaSemana_int
            LEFT JOIN 
                sala s ON h.idSala_int = s.idSala_int
            LEFT JOIN 
                tiposala ts ON s.idTipoSala_int = ts.idTipoSala_int
            WHERE 
                a.rutProfesor_str = %s
                AND n.fechaEvaluacion_dat > GETDATE()
                AND a.idTipoEstado_int = 1
        )
        SELECT TOP 6 *
        FROM (
            SELECT * FROM Eventos
            UNION ALL
            SELECT * FROM Evaluaciones
        ) AS eventos_notas
        ORDER BY Fecha;
        """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [rut_prfoesor, rut_prfoesor])
            rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "Descripcion": row[0],
                "Fecha": row[1],
                "Lugar": row[2],
                "Curso": row[3],
                "Nombre_Asignatura": row[4],
                "Categoria_Evento": row[5]
            })
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
#VISTAS PARA EL MODULO DE ASIGNATURAS   
@api_view(['POST'])
def detalleAsignatura(request):
    
        
    rut_Profesor = request.data.get('rutProfesor_str')
    id_Curso = request.data.get('idCurso_int')
    id_Asignatura = request.data.get('idAsignatura_int')

    
    if not rut_Profesor:
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
            COUNT(ae.rutEstudiante_str) AS Cantidad_Alumnos
        FROM asignatura a
        LEFT JOIN profesor p ON a.rutProfesor_str = p.rut_str
        LEFT JOIN cursoAsignatura ca ON a.idAsignatura_int = ca.idAsignatura_int
        LEFT JOIN tipoAsignatura ta ON a.idTipoAsignatura_int = ta.idTipoAsignatura_int
        LEFT JOIN asignaturaestudiante ae ON a.idAsignatura_int = ae.idAsignatura_int AND ca.idCurso_int = ae.idCurso_int AND a.idAsignatura_int = ae.idAsignatura_int
        where a.rutProfesor_str = %s --parametro que se obtienes de los datos del estudiante del shared.service --debe ser dinamico
        AND ca.idCurso_int = %s --parametro que se obtienes de los datos del estudiante del shared.service --debe ser dinamico
        AND a.idTipoEstado_int = 1 --siempre debe ir setiado en 1
        AND a.idAsignatura_int = %s --paremtro del front
        GROUP BY a.idAsignatura_int, a.nombre_str, a.descripcion_str, ta.nombre_str;
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [rut_Profesor, id_Curso, id_Asignatura])
            rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "ID_Asignatura": row[0],
                "Nombre_Asignatura": row[1],
                "Descripcion_Asignatura": row[2],
                "Tipo_Asignatura": row[3],
                "Cantidad_Alumnos": row[4]
            })
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@api_view(['POST'])
def detallePromedioNotaAsistencia(request):
    
    rut_profesor = request.data.get('rutProfesor_str')
    id_curso = request.data.get('idCurso_int')
    id_asignatura = request.data.get('idAsignatura_int')
    
    if not rut_profesor:
        return JsonResponse({"error": "rutProfesor_str no proporcionado"}, status=400)
    
    if not id_curso:
        return JsonResponse({"error": "idCurso_int no proporcionado"}, status=400)
    
    if not id_asignatura:
        return JsonResponse({"error": "idAsignatura_int no proporcionado"}, status=400)
    
    query = """
                ;WITH Promedios AS (
            -- Promedio de Notas
            SELECT
                n.idAsignatura_int AS Id_Asignatura, 
                a.nombre_str AS Nombre_Asignatura,
                ROUND(SUM(n.valor_flo * n.ponderacion_int) / SUM(n.ponderacion_int), 1) AS Registro,
                'Nota' AS Tipo
            FROM 
                nota n
            INNER JOIN 
                asignatura a ON n.idAsignatura_int = a.idAsignatura_int
            INNER JOIN 
                cursoAsignatura ca ON n.idAsignatura_int = ca.idAsignatura_int
            INNER JOIN 
                cursoEstudiante ce ON n.rutEstudiante_str = ce.rutEstudiante_str
            WHERE 
                ca.idCurso_int = ce.idCurso_int
                AND ca.idCurso_int = %s -- Este es el parámetro que se obtiene de los datos del estudiante del EstudiantesService.
                AND a.rutProfesor_str = %s -- Este es el parámetro que se obtiene de los datos del estudiante del EstudiantesService.
                AND ca.idAsignatura_int = %s -- Este parámetro se obtiene del componente asignatura al igual que la sidenav.
                AND n.valor_flo IS NOT NULL -- Filtrar solo los registros que no son NULL
                AND a.idTipoEstado_int = 1 -- Solo asignaturas activas
                AND n.isActived_int = 1 -- Solo registros activos

            GROUP BY 
                a.nombre_str, n.idAsignatura_int

            UNION ALL

            -- Promedio de Asistencia
            SELECT 
                asis.idAsignatura_int AS Id_Asignatura, 
                a.nombre_str AS Nombre_Asignatura,
                CAST(ROUND(SUM(CASE WHEN asis.idTipoEstado_int = 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS DECIMAL(5,1)) AS Registro,
                'Asistencia' AS Tipo
            FROM 
                asistencia asis
            INNER JOIN 
                asignatura a ON asis.idAsignatura_int = a.idAsignatura_int
            INNER JOIN 
                cursoAsignatura ca ON asis.idAsignatura_int = ca.idAsignatura_int
            INNER JOIN 
                cursoEstudiante ce ON asis.rutEstudiante_str = ce.rutEstudiante_str
            WHERE 
                ca.idCurso_int = ce.idCurso_int
                AND ca.idCurso_int = %s -- Este es el parámetro que se obtiene de los datos del estudiante del EstudiantesService.
                AND a.rutProfesor_str = %s -- Este parámetro también se obtiene del EstudiantesService.
                AND asis.idAsignatura_int = %s -- Este parámetro se obtiene del componente asignatura al igual que la sidenav.
                AND a.idTipoEstado_int = 1 -- Solo asignaturas activas
            GROUP BY 
                a.nombre_str, asis.idAsignatura_int
        )

        -- Consulta principal que utiliza la CTE
        SELECT *
        FROM Promedios;

    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [id_curso,rut_profesor, id_asignatura,id_curso,rut_profesor, id_asignatura])
            rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "Id_Asignatura": row[0],
                "Nombre_Asignatura": row[1],
                "Registro": row[2],
                "Tipo": row[3]
            })
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
@api_view(['POST'])
def detallePromedioNotaAsistenciaXAlumno(request):
    
    rut_profesor = request.data.get('rutProfesor_str')
    id_curso = request.data.get('idCurso_int')
    id_asignatura = request.data.get('idAsignatura_int')
    
    if not rut_profesor:
        return JsonResponse({"error": "rutProfesor_str no proporcionado"}, status=400)
    
    if not id_curso:
        return JsonResponse({"error": "idCurso_int no proporcionado"}, status=400)
    
    if not id_asignatura:
        return JsonResponse({"error": "idAsignatura_int no proporcionado"}, status=400)


    query = """
    
        ;WITH PromediosPorEstudiante AS (
            -- Subconsulta para calcular el promedio de notas por estudiante
            SELECT
                n.idAsignatura_int AS Id_Asignatura,
                a.nombre_str AS Nombre_Asignatura,
                CONCAT(e.nombres_str,' ',apellidos_str) AS Nombre_Estudiante,
                ROUND(SUM(n.valor_flo * n.ponderacion_int) / SUM(n.ponderacion_int), 1) AS Promedio,
                'Promedio Notas' AS Tipo
            FROM 
                nota n
            INNER JOIN 
                cursoAsignatura ca ON n.idAsignatura_int = ca.idAsignatura_int
            INNER JOIN 
                asignatura a ON ca.idAsignatura_int = a.idAsignatura_int
            INNER JOIN 
                cursoEstudiante ce ON n.rutEstudiante_str = ce.rutEstudiante_str
            INNER JOIN
                estudiante e ON n.rutEstudiante_str = e.rut_str
            WHERE 
                ca.idCurso_int = ce.idCurso_int
                AND ca.idCurso_int = %s -- Este es el parametro dinamico del curso
                AND a.rutProfesor_str = %s -- Este es el parametro del profesor
                AND ca.idAsignatura_int = %s -- Este es el parametro de la asignatura
                AND n.valor_flo IS NOT NULL -- Filtrar solo los registros que no son NULL
                AND a.idTipoEstado_int = 1 -- Solo asignaturas activas
                AND n.isActived_int = 1 -- Solo registros activos
            GROUP BY 
                a.nombre_str, n.idAsignatura_int,e.nombres_str,e.apellidos_str
            
            UNION ALL
            
            -- Subconsulta para calcular el promedio de asistencia por estudiante
            SELECT 
                asis.idAsignatura_int AS Id_Asignatura, 
                a.nombre_str AS Nombre_Asignatura,
                CONCAT(e.nombres_str,' ',e.apellidos_str) AS Nombre_Estudiante,
                CAST(ROUND(SUM(CASE WHEN asis.idTipoEstado_int = 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS DECIMAL(5,1)) AS Promedio,
                'Promedio Asistencia' AS Tipo
            FROM 
                asistencia asis
            INNER JOIN 
                cursoAsignatura ca ON asis.idAsignatura_int = ca.idAsignatura_int
            INNER JOIN 
                asignatura a ON ca.idAsignatura_int = a.idAsignatura_int
            INNER JOIN 
                cursoEstudiante ce ON asis.rutEstudiante_str = ce.rutEstudiante_str
            INNER JOIN
                estudiante e ON asis.rutEstudiante_str = e.rut_str
            WHERE 
                ca.idCurso_int = ce.idCurso_int
                AND ca.idCurso_int = %s -- Este es el parametro dinamico del curso
                AND a.rutProfesor_str = %s -- Este parametro tambien se obtiene del EstudiantesService.
                AND asis.idAsignatura_int = %s -- Este parametro se obtiene del componente asignatura al igual que la sidenav.
                AND a.idTipoEstado_int = 1 -- Solo asignaturas activas
            GROUP BY 
                a.nombre_str, asis.idAsignatura_int,e.nombres_str,e.apellidos_str
        )

        -- Consulta principal que utiliza la CTE
        SELECT *
        FROM PromediosPorEstudiante
        ORDER BY Tipo,Nombre_Estudiante
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [id_curso,rut_profesor, id_asignatura,id_curso,rut_profesor, id_asignatura])
            rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "Id_Asignatura": row[0],
                "Nombre_Asignatura": row[1],
                "Nombre_Estudiante": row[2],
                "Promedio": row[3],
                "Tipo": row[4]
            })
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
        
@api_view(['POST'])
def detalleRegistrosNotasAsistenciaXAlumno(request):
    
    
    rut_profesor = request.data.get('rutProfesor_str')
    id_curso = request.data.get('idCurso_int')
    id_asignatura = request.data.get('idAsignatura_int')
    
    if not rut_profesor:
        return JsonResponse({"error": "rutProfesor_str no proporcionado"}, status=400)
    
    if not id_curso:
        return JsonResponse({"error": "idCurso_int no proporcionado"}, status=400)
    
    if not id_asignatura:
        return JsonResponse({"error": "idAsignatura_int no proporcionado"}, status=400)


    query = """
            ;WITH DetalleRegistrosPorEstudiante AS (
            -- Subconsulta para calcular el promedio de notas por estudiante
            SELECT
                n.idAsignatura_int AS Id_Asignatura,
                a.nombre_str AS Nombre_Asignatura,
                e.rut_str AS Rut_Estudiante,
                CONCAT(e.nombres_str,' ',apellidos_str) AS Nombre_Estudiante,
                n.fechaEvaluacion_dat AS Fecha_Registro,
                Round(n.valor_flo,1) AS Registro,
                n.nombre_str AS Tipo,
                n.ponderacion_int AS Ponderacion
            FROM 
                nota n
            INNER JOIN 
                cursoAsignatura ca ON n.idAsignatura_int = ca.idAsignatura_int
            INNER JOIN 
                asignatura a ON ca.idAsignatura_int = a.idAsignatura_int
            INNER JOIN 
                cursoEstudiante ce ON n.rutEstudiante_str = ce.rutEstudiante_str
            INNER JOIN
                estudiante e ON n.rutEstudiante_str = e.rut_str
            WHERE 
                ca.idCurso_int = ce.idCurso_int
                AND ca.idCurso_int = %s -- Este es el parametro dinamico del curso
                AND a.rutProfesor_str = %s -- Este es el parametro del profesor
                AND ca.idAsignatura_int = %s -- Este es el parametro de la asignatura
                AND a.idTipoEstado_int = 1 -- Solo asignaturas activas
                AND n.isActived_int = 1 -- Solo registros activos
            
            UNION ALL
            
            -- Subconsulta para calcular el promedio de asistencia por estudiante
            SELECT 
                asis.idAsignatura_int AS Id_Asignatura, 
                a.nombre_str AS Nombre_Asignatura,
                asis.rutEstudiante_str AS Rut_Estudiante,
                CONCAT(e.nombres_str,' ',e.apellidos_str) AS Nombre_Estudiante,
                asis.fechaRegistro_dat AS Fecha_Registro,
                asis.idTipoEstado_int AS Registro,
                'Asistencia' AS Tipo,
                null AS Ponderacion
            FROM 
                asistencia asis
            INNER JOIN 
                cursoAsignatura ca ON asis.idAsignatura_int = ca.idAsignatura_int
            INNER JOIN 
                asignatura a ON ca.idAsignatura_int = a.idAsignatura_int
            INNER JOIN 
                cursoEstudiante ce ON asis.rutEstudiante_str = ce.rutEstudiante_str
            INNER JOIN
                estudiante e ON asis.rutEstudiante_str = e.rut_str
            WHERE 
                ca.idCurso_int = ce.idCurso_int
                AND ca.idCurso_int = %s -- Este es el parametro dinamico del curso
                AND a.rutProfesor_str = %s -- Este parametro tambien se obtiene del EstudiantesService.
                AND asis.idAsignatura_int = %s -- Este parametro se obtiene del componente asignatura al igual que la sidenav.
                AND a.idTipoEstado_int = 1 -- Solo asignaturas activas

        )

        -- Consulta principal que utiliza la CTE
        SELECT *
        FROM DetalleRegistrosPorEstudiante
        ORDER BY Tipo,Nombre_Estudiante,Fecha_Registro
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [id_curso,rut_profesor, id_asignatura,id_curso,rut_profesor, id_asignatura])
            rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "Id_Asignatura": row[0],
                "Nombre_Asignatura": row[1],
                "Rut_Estudiante": row[2],
                "Nombre_Estudiante": row[3],
                "Fecha_Registro": row[4],
                "Registro": row[5],
                "Tipo": row[6],
                "Ponderacion": row[7]
            })
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
            

@api_view(['PUT'])
def actualizarNota(request):
    try:
        # Obtener los datos enviados desde el frontend
        rut_profesor = request.data.get('rutProfesor_str')
        fecha = request.data.get('fecha_dat')
        nombre = request.data.get('nombre_str')
        rut_estudiante = request.data.get('rutEstudiante_str')
        valor = request.data.get('valor_flo')
        motivo_modificacion = request.data.get('motivo_str')  # Motivo de la modificación
        id_asignatura = request.data.get('idAsignatura_int')
        id_curso = request.data.get('idCurso_int')

        # Validar que los datos no sean nulos
        if not all([rut_profesor, fecha, nombre, rut_estudiante, valor, motivo_modificacion, id_asignatura, id_curso]):
            return JsonResponse({"error": "Datos incompletos proporcionados."}, status=400)

        with connection.cursor() as cursor:
            # Iniciar una transacción
            with transaction.atomic():
                # Buscar el registro existente
                query = """
                    SELECT * FROM Nota n
                    INNER JOIN cursoEstudiante ce ON n.rutEstudiante_str = ce.rutEstudiante_str
                    WHERE n.rutEstudiante_str = %s AND n.nombre_str = %s AND n.fechaEvaluacion_dat = %s 
                    AND n.isActived_int = 1 AND n.idAsignatura_int = %s AND ce.idCurso_int = %s
                """
                cursor.execute(query, [rut_estudiante, nombre, fecha, id_asignatura, id_curso])
                existing_record = cursor.fetchone()

                if not existing_record:
                    return JsonResponse({"error": "Registro no encontrado."}, status=404)

                # Actualizar el campo isActive_int del registro existente a 0 y añadir detalles de modificación
                update_query = """
                    UPDATE Nota
                    SET isActived_int = 0, fechaModificacion_dat = %s, usuarioModificacion_str = %s, motivoModificacion_str = %s
                    WHERE rutEstudiante_str = %s AND nombre_str = %s AND fechaEvaluacion_dat = %s
                    AND idAsignatura_int = %s AND isActived_int = 1
                """
                cursor.execute(update_query, [datetime.datetime.now(), rut_profesor, motivo_modificacion, rut_estudiante, nombre, fecha, id_asignatura])

                # Insertar un nuevo registro con los datos modificados
                insert_query = """
                    INSERT INTO Nota (idAsignatura_int, valor_flo, idTipoNota_int, fechaRegistro_dat, 
                                      fechaModificacion_dat, usuarioModificacion_str, motivoModificacion_str, 
                                      rutEstudiante_str, ponderacion_int, nombre_str, fechaEvaluacion_dat, isActived_int)
                    VALUES (%s, %s, %s, %s, NULL, NULL, NULL, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, [
                    existing_record[1], valor, existing_record[3], datetime.datetime.now(),
                    rut_estudiante, existing_record[9], existing_record[10], existing_record[11], 1
                ])
        
        return JsonResponse({"message": "Nota modificada correctamente."}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    

        
@api_view(['POST'])
def obtenerLista(request):
    
    id_curso = request.data.get('idCurso_int')
    id_asignatura = request.data.get('idAsignatura_int')
    
    if not id_curso or not id_asignatura:
        return JsonResponse({"error": "idCurso_int no proporcionado"}, status=400)
    
    query = """
            SELECT a.fechaRegistro_dat AS Fecha_Registro,
                CONCAT(e.nombres_str,' ',e.apellidos_str) AS Nombre_Estudiante,
                a.rutEstudiante_str AS Rut_Estudiante
            FROM asistencia a
            INNER JOIN cursoEstudiante ce ON a.rutEstudiante_str = ce.rutEstudiante_str
            INNER JOIN estudiante e ON a.rutEstudiante_str = e.rut_str
            WHERE a.idAsignatura_int = %s
            AND ce.idCurso_int = %s
            AND a.fechaRegistro_dat >= CONVERT(DATE, GETDATE())
        
                """
                
    try: 
        with connection.cursor() as cursor:
            cursor.execute(query, [id_asignatura, id_curso])
            rows = cursor.fetchall()
            
        results = []
        for row in rows:
            results.append({
                "Fecha_Registro": row[0],
                "Nombre_Estudiante": row[1],
                "Rut_Estudiante": row[2]
            })
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)    
    
    
@api_view(['POST'])
def enviarAsistencia(request):
    
    data = request.data  # Obtener datos del cuerpo de la solicitud
    if not data:
        return JsonResponse({"error": "Datos no proporcionados"}, status=400)
    
    try:
        with connection.cursor() as cursor:
            for item in data:
                rutEstudiante = item['rutEstudiante_str']
                idTipoEstado = item['idTipoEstado_int']
                fechaRegistro = item['fechaRegistro_dat']
                idAsignatura = item['idAsignatura_int']
                idCurso = item['idCurso_int']
                # Ejecutar el UPDATE para cada estudiante
                cursor.execute("""UPDATE a
                                    SET a.idTipoEstado_int = %s
                                    FROM asistencia a
                                    INNER JOIN cursoEstudiante ce ON a.rutEstudiante_str = ce.rutEstudiante_str
                                    WHERE a.rutEstudiante_str = %s
                                    AND a.fechaRegistro_dat = %s
                                    AND a.idAsignatura_int = %s
                                    AND ce.idCurso_int = %s;
""", 
                               [idTipoEstado, rutEstudiante, fechaRegistro, idAsignatura, idCurso])
        return JsonResponse({'message': 'Actualización exitosa'}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
            
    
#PARA EL MODULO DE EVENTOS 
@api_view(['POST'])
def detalleEventos(request):
    
    rut_profesor = request.data.get('rutProfesor_str')

    if not rut_profesor:
        return JsonResponse({"error": "Parámetros no proporcionados"}, status=400)

    query = """
            ;WITH Event_Count AS (
            SELECT 
                ee2.idEvento_int,
                COUNT(*) AS Cantidad_Estudiantes
            FROM eventoEstudiante ee2
            GROUP BY ee2.idEvento_int
        ),
        Events AS (
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
            WHERE 
            a.idTipoEstado_int = 1
            AND a.rutProfesor_str = %s

        )
        SELECT * FROM Events
        ORDER BY Fecha;


    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [rut_profesor])
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
    
         
@api_view(['POST'])
def asignaturasProfesor(request):
    
    rutPorfesor = request.data.get('rutProfesor_str')
    
    if not rutPorfesor:
        return JsonResponse({"error": "rutProfesor_str no proporcionado"}, status=400)
    
    query = """
        SELECT idAsignatura_int, nombre_str
        FROM asignatura
        WHERE rutProfesor_str = %s
        AND idTipoEstado_int = 1
        """
        
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [rutPorfesor])
            rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "idAsignatura_int": row[0],
                "nombre_str": row[1]
            })
        return JsonResponse(results, safe=False)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
@api_view(['POST'])
def crearEvento(request):
    rut_profesor = request.data.get('rutProfesor_str')
    id_asignatura = request.data.get('idAsignatura_int')
    id_tipo_evento = request.data.get('idTipoEvento_int')
    lugar = request.data.get('lugarEvento_str')
    fecha_evento = request.data.get('fechaEvento_dat')
    descripcion = request.data.get('descripcion')

    if not all([rut_profesor, id_asignatura, id_tipo_evento, lugar, fecha_evento, descripcion]):
        return JsonResponse({"error": "Datos incompletos proporcionados."}, status=400)

    try:
        # Obtener la fecha actual en el formato YYYY-MM-DD
        fecha_actual = datetime.datetime.now().strftime('%Y-%m-%d')

        with connection.cursor() as cursor:
            # Ejecutar la consulta de inserción y obtener el ID del evento insertado
            cursor.execute("""
                INSERT INTO evento (idAsignatura_int, idTipoEvento_int, descripcion, usuarioModificacion_str, 
                motivoModificacion_str, fechaModificacion_dat, fechaRegistro_dat, fechaEvento_dat, lugarEvento_str)
                OUTPUT INSERTED.idEvento_int
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, [
                id_asignatura,
                id_tipo_evento,
                descripcion,
                rut_profesor,
                'Creacion de evento',
                fecha_actual,
                fecha_actual,
                fecha_evento,
                lugar
            ])

            # Obtener el ID del evento insertado
            id_evento_insertado = cursor.fetchone()[0]

        return JsonResponse({"message": "Evento creado correctamente.", "idEvento": id_evento_insertado}, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
@api_view(['POST'])
def obtenerObservaciones(request):

    rut_profesor = request.data.get('rutProfesor_str')
    
    if not rut_profesor:
        return JsonResponse({"error": "rutProfesor_str no proporcionado"}, status=400)
    
    try:
        
        with connection.cursor() as cursor:
            cursor.execute("""
            
        SELECT 
            a.idAsignatura_int AS ID_Asignatura,
            CONCAT(e.nombres_str,' ',e.apellidos_str) AS Nombre_Estudiante,
            o.descripcion AS Descripcion_Observacion,
            o.fechaRegistro_dat AS Fecha_Registro,
            a.nombre_str AS Nombre_Asignatura,
            too.nombre_str AS Tipo_Observacion,
            CONCAT(c.nivelCurso_str,' ', c.letraCurso_str) AS Nombre_Curso,
            e.rut_str AS Rut_Estudiante
        FROM observacion o
        INNER JOIN asignatura a ON o.idAsignatura_int = a.idAsignatura_int
        INNER JOIN tipoObservacion too ON o.idTipoObservacion_int = too.idTipoObservacion_int
        INNER JOIN estudiante e ON o.rutEstudiante_str = e.rut_str
        INNER JOIN cursoEstudiante ce ON o.rutEstudiante_str = ce.rutEstudiante_str
        INNER JOIN curso c ON ce.idCurso_int = c.idCurso_int
        WHERE a.rutProfesor_str = %s
        AND a.idTipoEstado_int = 1

                """, [rut_profesor])
            rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "ID_Asignatura": row[0],
                "Nombre_Estudiante": row[1],
                "Descripcion_Observacion": row[2],
                "Fecha_Registro": row[3],
                "Nombre_Asignatura": row[4],
                "Tipo_Observacion": row[5],
                "Nombre_Curso": row[6],
                "Rut_Estudiante": row[7]
            })
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
                


@api_view(['POST'])
def crearObservacion(request):
    
    rut_profesor = request.data.get('rutProfesor_str')
    id_asignatura = int(request.data.get('idAsignatura_int'))
    id_tipo_observacion = int(request.data.get('idTipoObservacion_int'))
    descripcion = request.data.get('descripcion')
    rut_estudiante = request.data.get('rutEstudiante_str')
    

    if not all([rut_profesor, id_asignatura, id_tipo_observacion, descripcion, rut_estudiante]):
        return JsonResponse({"error": "Datos incompletos proporcionados."}, status=400)
    

    try:
        # Obtener la fecha actual en el formato YYYY-MM-DD
        fecha_actual = datetime.datetime.now().strftime('%Y-%m-%d')

        with connection.cursor() as cursor:
            # Ejecutar la consulta de inserción y obtener el ID del evento insertado
            cursor.execute("""
                      INSERT INTO observacion (idAsignatura_int, rutEstudiante_str, idTipoObservacion_int, descripcion, 
                usuarioModificacion_str, motivoModificacion_str, fechaModificacion_dat, fechaRegistro_dat)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                id_asignatura,
                rut_estudiante,
                id_tipo_observacion,
                descripcion,
                rut_profesor,
                'Creacion de Observacion',
                fecha_actual,
                fecha_actual,
            ])

        return JsonResponse({"message": "Evento creado correctamente."}, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)