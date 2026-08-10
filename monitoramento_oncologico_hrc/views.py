from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Paciente
from .forms import PacienteForm
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

@login_required(login_url='login')
def aba_cadastro(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente cadastrado com sucesso!')
            return redirect('aba_cadastro') # Recarrega a página limpa
    else:
        form = PacienteForm()
    
    return render(request, 'monitoramento/cadastro.html', {'form': form})

@login_required(login_url='login')
def aba_dados(request):
    pacientes = Paciente.objects.all()
    pacientes = Paciente.objects.all().order_by('-ativo')
    
    query_nome = request.GET.get('nome')
    query_especialidade = request.GET.get('especialidade')
    
    if query_nome:
        pacientes = pacientes.filter(nome__icontains=query_nome)
    if query_especialidade:
        pacientes = pacientes.filter(especialidade=query_especialidade)
        
    context = {
        'pacientes': pacientes,
        'especialidades': Paciente.ESPECIALIDADES
    }
    return render(request, 'monitoramento/dados.html', context)

@login_required(login_url='login')
def aba_metricas(request):
    pacientes = Paciente.objects.all()
    total_pacientes = pacientes.count()

    # Dicionários para armazenar a contagem
    especialidade_counts = {}
    situacao_counts = {}
    tratamentos_counts = {
        'Apenas Cirurgia': 0, 'Apenas QT': 0, 'Apenas RT': 0, 
        'Cirurgia+RT': 0, 'Cirurgia+QT': 0, 'QT+Cirurgia': 0, 
        'RT+Cirurgia': 0, 'QT+RT': 0, 'RT+QT': 0
    }
    
    # Pegando a lista de especialidades para mostrar o nome bonito, não a sigla
    dict_especialidades = dict(Paciente.ESPECIALIDADES)

    for p in pacientes:
        # 1. Contagem por Especialidade
        nome_esp = dict_especialidades.get(p.especialidade, p.especialidade)
        especialidade_counts[nome_esp] = especialidade_counts.get(nome_esp, 0) + 1
        
        # 2. Contagem por Situação (Usando a nossa @property)
        situacao = p.situacao
        situacao_counts[situacao] = situacao_counts.get(situacao, 0) + 1
        
        # 3. Contagem de Tratamentos Realizados
        if p.fez_cirurgia: tratamentos_counts['Apenas Cirurgia'] += 1
        if p.fez_qt: tratamentos_counts['Apenas QT'] += 1
        if p.fez_rt: tratamentos_counts['Apenas RT'] += 1
        if p.fez_cirurgia_rt: tratamentos_counts['Cirurgia+RT'] += 1
        if p.fez_cirurgia_qt: tratamentos_counts['Cirurgia+QT'] += 1
        if p.fez_qt_cirurgia: tratamentos_counts['QT+Cirurgia'] += 1
        if p.fez_rt_cirurgia: tratamentos_counts['RT+Cirurgia'] += 1
        if p.fez_qt_rt: tratamentos_counts['QT+RT'] += 1
        if p.fez_rt_qt: tratamentos_counts['RT+QT'] += 1

    # Empacotando os dados em formato JSON para enviar ao Gráfico (HTML/JS)
    context = {
        'total_pacientes': total_pacientes,
        
        'labels_especialidade': json.dumps(list(especialidade_counts.keys())),
        'dados_especialidade': json.dumps(list(especialidade_counts.values())),
        
        'labels_situacao': json.dumps(list(situacao_counts.keys())),
        'dados_situacao': json.dumps(list(situacao_counts.values())),
        
        'labels_tratamentos': json.dumps(list(tratamentos_counts.keys())),
        'dados_tratamentos': json.dumps(list(tratamentos_counts.values())),
    }
    
    return render(request, 'monitoramento/metricas.html', context)

@login_required(login_url='login')
def editar_paciente(request, prontuario):
    paciente = get_object_or_404(Paciente, prontuario=prontuario)
    
    # Se o paciente estiver desabilitado, impede a edição e avisa o usuário
    if not paciente.ativo:
        messages.error(request, f'O paciente {paciente.nome} está desabilitado e não pode ser editado.')
        return redirect('aba_dados')
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Paciente {paciente.nome} atualizado com sucesso!')
            return redirect('aba_dados')
    else:
        form = PacienteForm(instance=paciente)
    
    return render(request, 'monitoramento/cadastro.html', {'form': form, 'editando': True, 'paciente': paciente})

def tela_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('aba_cadastro') # Vai direto para o cadastro após logar
    else:
        form = AuthenticationForm()
    return render(request, 'monitoramento/login.html', {'form': form})

def fazer_logout(request):
    logout(request)
    return redirect('login')

def alternar_status_paciente(request, prontuario):
    paciente = get_object_or_404(Paciente, prontuario=prontuario)
    
    # Inverte o status atual (True vira False, False vira True)
    paciente.ativo = not paciente.ativo
    paciente.save()
    
    status_texto = "ativado" if paciente.ativo else "desabilitado"
    messages.success(request, f'Paciente {paciente.nome} foi {status_texto} com sucesso!')
    return redirect('aba_dados')