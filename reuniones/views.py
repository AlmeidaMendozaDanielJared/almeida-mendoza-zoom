# ========================================
# reuniones/views.py
# Vistas para OAuth User-Level (gratuito)
# ========================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.cache import cache
from .zoom_service import ZoomService
from .models import Reunion, Participante
from datetime import datetime
from django.contrib.auth import login
from django.contrib.auth.models import User

# =====================================
# VISTAS DE AUTENTICACIÓN OAUTH
# =====================================

def zoom_login(request):
    """
    Redirige al usuario a la página de autorización de Zoom.
    Primera vez que el usuario autoriza la app.
    """
    zoom_service = ZoomService()
    authorization_url = zoom_service.get_authorization_url()
    return redirect(authorization_url)


def zoom_oauth_callback(request):
    """
    Callback de Zoom después de que el usuario autoriza.
    Recibe el código y lo intercambia por access token.
    """
    code = request.GET.get('code')
    
    if not code:
        messages.error(request, '❌ Error: No se recibió código de autorización')
        return redirect('inicio')
    
    try:
        zoom_service = ZoomService()
        token_data = zoom_service.exchange_code_for_token(code)
        
        # CORRECCIÓN: Usar 'User' (el modelo), no 'user' (la instancia)
        user, created = User.objects.get_or_create(
            username='admin_zoom',
            defaults={'first_name': 'Zoom', 'last_name': 'Admin'}
        )

        if created:
            user.set_unusable_password()
            user.save()
            
        # Especificamos el backend para evitar errores de autenticación manual
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        messages.success(request, '✅ ¡Autorización exitosa! Ya puedes crear reuniones.')
        return redirect('inicio')
    
    except Exception as e:
        messages.error(request, f'❌ Error al autorizar: {str(e)}')
        return redirect('inicio')


def verificar_autorizacion(request):
    """
    API para verificar si ya hay token (usuario ya autorizó).
    Usado por JavaScript en el frontend.
    """
    tiene_token = cache.get('zoom_access_token') is not None
    return JsonResponse({'autorizado': tiene_token})


# =====================================
# VISTAS PRINCIPALES
# =====================================

def inicio(request):
    """
    Página de inicio.
    Muestra botón de autorizar si no hay token.
    """
    tiene_token = cache.get('zoom_access_token') is not None
    
    context = {
        'autorizado': tiene_token
    }
    return render(request, 'reuniones/inicio.html', context)


@login_required
def crear_reunion(request):
    """
    Vista para crear una reunión de Zoom.
    """
    if request.method == 'POST':
        try:
            # 1. Obtener datos del formulario (siguiendo tus imágenes)
            topic = request.POST.get('topic')
            fecha_str = request.POST.get('start_date')  # Viene como "2024-01-26"
            hora_str = request.POST.get('start_time')    # Viene como "22:25"
            duration = int(request.POST.get('duration'))
            
            # 2. Unir fecha y hora en una sola cadena
            # Formato resultante: "2024-01-26T22:25"
            full_datetime_str = f"{fecha_str}T{hora_str}"
            
            # 3. Convertir a objeto datetime de Python
            start_datetime = datetime.strptime(full_datetime_str, '%Y-%m-%dT%H:%M')
            
            # 4. Convertir a formato ISO 8601 string para la API de Zoom
            # Agregamos los segundos :00 como sugería tu código original
            start_time_iso = start_datetime.strftime('%Y-%m-%dT%H:%M:%S')
            
            # Crear reunión en Zoom
            zoom_service = ZoomService()
            meeting_data = zoom_service.crear_reunion(
                topic=topic,
                start_time=start_time_iso,
                duration=duration
            )
            
            # Guardar en base de datos
            reunion = Reunion.objects.create(
                titulo=topic,
                zoom_meeting_id=meeting_data['id'],
                join_url=meeting_data['join_url'],
                start_url=meeting_data['start_url'],
                fecha_inicio=start_datetime,
                duracion=duration,
                creador=request.user
            )
            
            messages.success(request, f'✅ Reunión "{topic}" creada exitosamente!')
            return redirect('lista_reuniones')
        
        except Exception as e:
            messages.error(request, f'❌ Error al crear reunión: {str(e)}')
    
    return render(request, 'reuniones/crear_reunion.html')


@login_required
def lista_reuniones(request):
    """
    Lista todas las reuniones creadas.
    """
    reuniones = Reunion.objects.filter(creador=request.user)
    
    context = {
        'reuniones': reuniones
    }
    return render(request, 'reuniones/lista_reuniones.html', context)


@login_required
def detalle_reunion(request, reunion_id):
    """
    Muestra detalles de una reunión específica.
    """
    reunion = get_object_or_404(Reunion, id=reunion_id, creador=request.user)
    
    context = {
        'reunion': reunion
    }
    return render(request, 'reuniones/detalle_reunion.html', context)


@login_required
def eliminar_reunion(request, reunion_id):
    """
    Elimina una reunión de Zoom y de la base de datos.
    """
    reunion = get_object_or_404(Reunion, id=reunion_id, creador=request.user)
    
    try:
        # Eliminar de Zoom
        zoom_service = ZoomService()
        zoom_service.eliminar_reunion(reunion.zoom_meeting_id)
        
        # Eliminar de base de datos
        titulo = reunion.titulo
        reunion.delete()
        
        messages.success(request, f'✅ Reunión "{titulo}" eliminada correctamente.')
    
    except Exception as e:
        messages.error(request, f'❌ Error al eliminar: {str(e)}')
    
    return redirect('lista_reuniones')


@login_required
def sincronizar_reuniones(request):
    """
    Sincroniza reuniones desde Zoom API.
    Útil para obtener reuniones creadas directamente en Zoom.
    """
    try:
        zoom_service = ZoomService()
        meetings = zoom_service.listar_reuniones()
        
        count = 0
        for meeting in meetings:
            # Crear o actualizar en base de datos
            Reunion.objects.update_or_create(
                zoom_meeting_id=meeting['id'],
                defaults={
                    'titulo': meeting['topic'],
                    'join_url': meeting['join_url'],
                    'start_url': meeting.get('start_url', ''),
                    'fecha_inicio': datetime.strptime(
                        meeting['start_time'], 
                        '%Y-%m-%dT%H:%M:%SZ'
                    ),
                    'duracion': meeting['duration'],
                    'creador': request.user
                }
            )
            count += 1
        
        messages.success(request, f'✅ Sincronizadas {count} reuniones desde Zoom.')
    
    except Exception as e:
        messages.error(request, f'❌ Error al sincronizar: {str(e)}')
    
    return redirect('lista_reuniones')