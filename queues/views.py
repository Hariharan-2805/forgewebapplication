from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Queue, Token
import qrcode
from io import BytesIO
from django.core.files import File

def landing_page(request):
    return render(request, 'landing.html')

@login_required
def dashboard(request):
    if request.user.is_owner:
        # Admin / Super Admin dashboard
        if request.user.is_superuser:
            managed_queues = Queue.objects.all().order_by('-created_at')
        else:
            managed_queues = Queue.objects.filter(created_by=request.user).order_by('-created_at')
        
        context = {'queues': managed_queues, 'is_owner': True}
        return render(request, 'dashboard.html', context)
    else:
        # Normal User dashboard
        user_tokens = Token.objects.filter(user=request.user).order_by('-created_at')
        context = {'tokens': user_tokens, 'is_owner': False}
        return render(request, 'dashboard.html', context)

@login_required
def create_queue(request):
    if not request.user.is_owner:
        return redirect('dashboard')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        avg_wait = request.POST.get('avg_wait_time_per_person', 5)
        
        Queue.objects.create(
            name=name,
            description=description,
            avg_wait_time_per_person=int(avg_wait),
            created_by=request.user,
            is_active=True
        )
        return redirect('dashboard')
        
    return render(request, 'create_queue.html')

@login_required
def manage_queue(request, queue_id):
    if not request.user.is_owner:
        return redirect('dashboard')
    
    queue = get_object_or_404(Queue, id=queue_id)
    if not request.user.is_superuser and queue.created_by != request.user:
        return redirect('dashboard')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'serve_next':
            next_token = Token.objects.filter(queue=queue, status='WAITING').order_by('number').first()
            if next_token:
                next_token.status = 'SERVING'
                next_token.save()
        elif action == 'complete':
            token_id = request.POST.get('token_id')
            token = Token.objects.filter(id=token_id).first()
            if token:
                token.status = 'COMPLETED'
                token.save()
                
        return redirect('manage_queue', queue_id=queue.id)

    tokens = Token.objects.filter(queue=queue).order_by('number')
    serving = tokens.filter(status='SERVING')
    waiting = tokens.filter(status='WAITING')
    completed = tokens.filter(status='COMPLETED')
    
    return render(request, 'manage_queue.html', {
        'queue': queue,
        'serving': serving,
        'waiting': waiting,
        'completed_count': completed.count()
    })

@login_required
def join_queue(request):
    queues = Queue.objects.filter(is_active=True)
    if request.method == 'POST':
        queue_id = request.POST.get('queue_id')
        queue = get_object_or_404(Queue, id=queue_id)
        
        # Calculate Number
        last_token = Token.objects.filter(queue=queue).order_by('number').last()
        next_number = (last_token.number + 1) if last_token else 1
        
        token = Token.objects.create(
            queue=queue,
            user=request.user,
            number=next_number
        )
        
        # Output QR code
        qr = qrcode.make(f"Token: {token.id}")
        blob = BytesIO()
        qr.save(blob, 'PNG')
        token.qr_code.save(f'{token.id}.png', File(blob), save=True)
        
        return redirect('queue_status', token_id=token.id)
        
    return render(request, 'join_queue.html', {'queues': queues})

@login_required
def queue_status(request, token_id):
    token = get_object_or_404(Token, id=token_id)
    ahead = Token.objects.filter(queue=token.queue, status='WAITING', number__lt=token.number).count()
    est_wait = ahead * token.queue.avg_wait_time_per_person
    
    context = {
        'token': token,
        'ahead': ahead,
        'est_wait': est_wait
    }
    return render(request, 'queue_status.html', context)

@login_required
def toggle_queue(request, queue_id):
    if not request.user.is_owner:
        return redirect('dashboard')
    
    queue = get_object_or_404(Queue, id=queue_id)
    if not request.user.is_superuser and queue.created_by != request.user:
        return redirect('dashboard')
        
    if request.method == 'POST':
        queue.is_active = not queue.is_active
        queue.save()
        
    return redirect('manage_queue', queue_id=queue.id)

@login_required
def verify_token(request, token_id):
    if not request.user.is_owner:
        return redirect('dashboard')
        
    token = get_object_or_404(Token, id=token_id)
    if not request.user.is_superuser and token.queue.created_by != request.user:
        return redirect('dashboard')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mark_present':
            token.status = 'COMPLETED'
            token.save()
            return redirect('manage_queue', queue_id=token.queue.id)
            
    return render(request, 'verify_token.html', {'token': token})


