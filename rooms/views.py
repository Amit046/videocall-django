from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Room
import uuid


def home(request):
    """Home page - create or join a room."""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            room_name = request.POST.get('room_name', 'My Room').strip() or 'My Room'
            host_name = request.POST.get('host_name', 'Host').strip() or 'Host'
            room = Room.objects.create(name=room_name, host_name=host_name)
            request.session['username'] = host_name
            return redirect('room', code=room.code)
        
        elif action == 'join':
            room_code = request.POST.get('room_code', '').strip()
            username = request.POST.get('username', 'Guest').strip() or 'Guest'
            try:
                room_code_uuid = uuid.UUID(room_code)
                room = get_object_or_404(Room, code=room_code_uuid)
                request.session['username'] = username
                return redirect('room', code=room.code)
            except (ValueError, AttributeError):
                return render(request, 'rooms/home.html', {
                    'error': 'Invalid room code. Please check and try again.'
                })
    
    return render(request, 'rooms/home.html')


def room(request, code):
    """Video call room."""
    room = get_object_or_404(Room, code=code)
    username = request.session.get('username', 'Guest')
    return render(request, 'rooms/room.html', {
        'room': room,
        'username': username,
        'room_code': str(code),
    })


def check_room(request, code):
    """API endpoint to check if a room exists."""
    try:
        room = Room.objects.get(code=code)
        return JsonResponse({'exists': True, 'name': room.name})
    except Room.DoesNotExist:
        return JsonResponse({'exists': False})
