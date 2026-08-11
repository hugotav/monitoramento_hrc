from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Paciente, HistoricoTratamento
from .forms import PacienteForm
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from datetime import datetime, date

@login_required(login_url='login')
def aba_cadastro(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save()
            
            # Mapeamento atualizado para salvar tratamentos com suporte a observações
            tratamentos_map = [
                ('indicacao_cirurgia', 'data_indicacao_cirurgia', 'Indicação de Cirurgia', 'obs_indicacao_cirurgia'),
                ('fez_qt', 'data_qt', 'Quimioterapia (QT)', 'obs_qt'),
                ('fez_rt', 'data_rt', 'Radioterapia (RT)', 'obs_rt'),
                ('fez_cirurgia_rt', 'data_cirurgia_rt', 'Cirurgia + RT', 'obs_cirurgia_rt'),
                ('fez_cirurgia_qt', 'data_cirurgia_qt', 'Cirurgia + QT', 'obs_cirurgia_qt'),
                ('fez_qt_cirurgia', 'data_qt_cirurgia', 'QT + Cirurgia', 'obs_qt_cirurgia'),
                ('fez_rt_cirurgia', 'data_rt_cirurgia', 'RT + Cirurgia', 'obs_rt_cirurgia'),
                ('fez_qt_rt', 'data_qt_rt', 'QT + RT', 'obs_qt_rt'),
                ('fez_rt_qt', 'data_rt_qt', 'RT + QT', 'obs_rt_qt'),
                ('fez_imunoterapia', 'data_imunoterapia', 'Imunoterapia', 'obs_imunoterapia')
            ]
            
            for checkbox, campo_data, nome, campo_obs in tratamentos_map:
                if form.cleaned_data.get(checkbox) and form.cleaned_data.get(campo_data):
                    HistoricoTratamento.objects.create(
                        paciente=paciente, 
                        tipo_tratamento=nome, 
                        data=form.cleaned_data.get(campo_data),
                        detalhes=form.cleaned_data.get(campo_obs)
                    )

            if form.cleaned_data.get('fez_cirurgia') and form.cleaned_data.get('data_cirurgia'):
                HistoricoTratamento.objects.create(
                    paciente=paciente, 
                    tipo_tratamento='Cirurgia', 
                    data=form.cleaned_data.get('data_cirurgia'),
                    detalhes=form.cleaned_data.get('qual_cirurgia')
                )

            messages.success(request, 'Paciente cadastrado com sucesso!')
            return redirect('aba_dados')
    else:
        form = PacienteForm()
    
    return render(request, 'monitoramento/cadastro.html', {'form': form})

@login_required(login_url='login')
def aba_dados(request):
    pacientes = Paciente.objects.all().order_by('-ativo')
    
    query_prontuario = request.GET.get('prontuario')
    query_nome = request.GET.get('nome')
    query_especialidade = request.GET.get('especialidade')
    query_situacao = request.GET.get('situacao')
    
    if query_prontuario:
        pacientes = pacientes.filter(prontuario__icontains=query_prontuario)
    if query_nome:
        pacientes = pacientes.filter(nome__icontains=query_nome)
    if query_especialidade:
        pacientes = pacientes.filter(especialidade=query_especialidade)
        
    # Filtragem inteligente baseada na lógica da property 'situacao'
    if query_situacao:
        if query_situacao == 'aguardando diagn':
            pacientes = [p for p in pacientes if p.situacao.lower() == 'aguardando diagnóstico']
        elif query_situacao == 'aguardando tratamento':
            pacientes = [p for p in pacientes if p.situacao.lower() == 'aguardando tratamento']
        elif query_situacao == 'em tratamento':
            pacientes = [p for p in pacientes if p.situacao.lower() == 'em tratamento']
        
    context = {
        'pacientes': pacientes,
        'especialidades': Paciente.ESPECIALIDADES
    }
    return render(request, 'monitoramento/dados.html', context)

@login_required(login_url='login')
def aba_metricas(request):
    # ==========================================
    # 1. CAPTURAR FILTROS
    # ==========================================
    data_inicio_str = request.GET.get('data_inicio')
    data_fim_str = request.GET.get('data_fim')
    filtro_especialidade = request.GET.get('especialidade')

    pacientes = Paciente.objects.all()
    tratamentos = HistoricoTratamento.objects.all()

    if filtro_especialidade:
        pacientes = pacientes.filter(especialidade=filtro_especialidade)
        tratamentos = tratamentos.filter(paciente__especialidade=filtro_especialidade)

    if data_inicio_str and data_fim_str:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        
        pacientes = pacientes.filter(data_entrada__range=[data_inicio, data_fim])
        tratamentos = tratamentos.filter(data__range=[data_inicio, data_fim])

    # ==========================================
    # 2. INICIALIZAR CONTADORES
    # ==========================================
    dict_especialidades = dict(Paciente.ESPECIALIDADES)
    hoje = date.today()

    vol_cid = {}
    vol_esp = {}
    cid_sexo = {'Masculino': 0, 'Feminino': 0, 'Não Informado': 0}
    cid_idade = {'0-18': 0, '19-35': 0, '36-50': 0, '51-65': 0, '65+': 0}

    soma_dias_acesso_diag, count_acesso_diag = 0, 0
    soma_dias_diag_trat, count_diag_trat = 0, 0
    soma_dias_acesso_trat, count_acesso_trat = 0, 0

    diag_no_prazo, diag_fora_prazo = 0, 0
    soma_atraso_diag = 0
    
    trat_no_prazo, trat_fora_prazo = 0, 0
    soma_atraso_trat = 0
    
    atraso_por_esp_diag = {}
    atraso_por_esp_trat = {}

    # ==========================================
    # 3. PROCESSAR DADOS DOS PACIENTES
    # ==========================================
    for p in pacientes:
        # A. Especialidade e Volume (Sempre conta)
        nome_esp = dict_especialidades.get(p.especialidade, p.especialidade)
        vol_esp[nome_esp] = vol_esp.get(nome_esp, 0) + 1

        # B. Sexo e Idade (MOVIMENTADO PARA FORA DO IF DIAGNOSTICO - Conta todos!)
        if p.sexo == 'M': cid_sexo['Masculino'] += 1
        elif p.sexo == 'F': cid_sexo['Feminino'] += 1
        else: cid_sexo['Não Informado'] += 1

        idade = p.idade if p.idade is not None else 0
        if idade <= 18: cid_idade['0-18'] += 1
        elif idade <= 35: cid_idade['19-35'] += 1
        elif idade <= 50: cid_idade['36-50'] += 1
        elif idade <= 65: cid_idade['51-65'] += 1
        else: cid_idade['65+'] += 1

        # C. Diagnóstico (Apenas se existir para o CID)
        if p.diagnostico:
            cid_curto = p.diagnostico.split(' - ')[0] if ' - ' in p.diagnostico else p.diagnostico
            vol_cid[cid_curto] = vol_cid.get(cid_curto, 0) + 1

        # --- Lógica de Diagnóstico (Entrada -> Diagnóstico) ---
        if p.data_entrada:
            if p.data_diagnostico:
                dias_diag = (p.data_diagnostico - p.data_entrada).days
                if dias_diag < 0: dias_diag = 0
                
                soma_dias_acesso_diag += dias_diag
                count_acesso_diag += 1

                if dias_diag <= 30:
                    diag_no_prazo += 1
                else:
                    diag_fora_prazo += 1
                    excedente = dias_diag - 30
                    soma_atraso_diag += excedente
                    if nome_esp not in atraso_por_esp_diag: atraso_por_esp_diag[nome_esp] = {'soma': 0, 'qtd': 0}
                    atraso_por_esp_diag[nome_esp]['soma'] += excedente
                    atraso_por_esp_diag[nome_esp]['qtd'] += 1
            else:
                # Paciente aguardando diagnóstico (Conta como pendente)
                dias_pendentes = (hoje - p.data_entrada).days
                if dias_pendentes > 30:
                    diag_fora_prazo += 1
                    excedente = dias_pendentes - 30
                    soma_atraso_diag += excedente
                    if nome_esp not in atraso_por_esp_diag: atraso_por_esp_diag[nome_esp] = {'soma': 0, 'qtd': 0}
                    atraso_por_esp_diag[nome_esp]['soma'] += excedente
                    atraso_por_esp_diag[nome_esp]['qtd'] += 1
                else:
                    diag_no_prazo += 1

        # --- Lógica de Tratamento (Diagnóstico -> 1º Tratamento) ---
        if p.data_diagnostico and p.data_primeiro_tratamento:
            dias_trat = (p.data_primeiro_tratamento - p.data_diagnostico).days
            if dias_trat < 0: dias_trat = 0
            
            soma_dias_diag_trat += dias_trat
            count_diag_trat += 1
            
            soma_dias_acesso_trat += (p.data_primeiro_tratamento - p.data_entrada).days
            count_acesso_trat += 1

            if dias_trat <= 60:
                trat_no_prazo += 1
            else:
                trat_fora_prazo += 1
                excedente = dias_trat - 60
                soma_atraso_trat += excedente
                if nome_esp not in atraso_por_esp_trat: atraso_por_esp_trat[nome_esp] = {'soma': 0, 'qtd': 0}
                atraso_por_esp_trat[nome_esp]['soma'] += excedente
                atraso_por_esp_trat[nome_esp]['qtd'] += 1

    # ==========================================
    # 4. PROCESSAR DADOS DE TRATAMENTOS
    # ==========================================
    vol_tratamentos = {}
    matriz_esp_trat = {}

    for t in tratamentos:
        tipo = t.tipo_tratamento
        vol_tratamentos[tipo] = vol_tratamentos.get(tipo, 0) + 1
        nome_esp = dict_especialidades.get(t.paciente.especialidade, t.paciente.especialidade)
        if nome_esp not in matriz_esp_trat: matriz_esp_trat[nome_esp] = {}
        matriz_esp_trat[nome_esp][tipo] = matriz_esp_trat[nome_esp].get(tipo, 0) + 1

    # ==========================================
    # 5. CÁLCULO E EMPACOTAMENTO
    # ==========================================
    def calcular_media(soma, qtd): return round(soma / qtd, 1) if qtd > 0 else 0

    media_atraso_esp_diag = {esp: calcular_media(d['soma'], d['qtd']) for esp, d in atraso_por_esp_diag.items()}
    media_atraso_esp_trat = {esp: calcular_media(d['soma'], d['qtd']) for esp, d in atraso_por_esp_trat.items()}

    context = {
        'total_pacientes': pacientes.count(),
        'especialidades_opcoes': Paciente.ESPECIALIDADES,
        'medias_jornada': {'acesso_diag': calcular_media(soma_dias_acesso_diag, count_acesso_diag), 'diag_trat': calcular_media(soma_dias_diag_trat, count_diag_trat)},
        'medias_atraso': {'diag_geral': calcular_media(soma_atraso_diag, diag_fora_prazo), 'trat_geral': calcular_media(soma_atraso_trat, trat_fora_prazo)},
        'diag_no_prazo': diag_no_prazo, 'diag_fora_prazo': diag_fora_prazo,
        'trat_no_prazo': trat_no_prazo, 'trat_fora_prazo': trat_fora_prazo,
        'g_vol_cid': json.dumps({'labels': list(vol_cid.keys()), 'dados': list(vol_cid.values())}),
        'g_cid_sexo': json.dumps({'labels': list(cid_sexo.keys()), 'dados': list(cid_sexo.values())}),
        'g_cid_idade': json.dumps({'labels': list(cid_idade.keys()), 'dados': list(cid_idade.values())}),
        'g_vol_trat': json.dumps({'labels': list(vol_tratamentos.keys()), 'dados': list(vol_tratamentos.values())}),
        'g_atraso_diag_esp': json.dumps({'labels': list(media_atraso_esp_diag.keys()), 'dados': list(media_atraso_esp_diag.values())}),
        'g_atraso_trat_esp': json.dumps({'labels': list(media_atraso_esp_trat.keys()), 'dados': list(media_atraso_esp_trat.values())}),
        'matriz_esp_trat': matriz_esp_trat, 
    }
    return render(request, 'monitoramento/metricas.html', context)

@login_required(login_url='login')
def editar_paciente(request, prontuario):
    paciente = get_object_or_404(Paciente, prontuario=prontuario)
    
    if not paciente.ativo:
        messages.error(request, f'O paciente {paciente.nome} está desabilitado e não pode ser editado.')
        return redirect('aba_dados')
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            
            tratamentos_map = [
                ('indicacao_cirurgia', 'data_indicacao_cirurgia', 'Indicação de Cirurgia', 'obs_indicacao_cirurgia'),
                ('fez_qt', 'data_qt', 'Quimioterapia (QT)', 'obs_qt'),
                ('fez_rt', 'data_rt', 'Radioterapia (RT)', 'obs_rt'),
                ('fez_cirurgia_rt', 'data_cirurgia_rt', 'Cirurgia + RT', 'obs_cirurgia_rt'),
                ('fez_cirurgia_qt', 'data_cirurgia_qt', 'Cirurgia + QT', 'obs_cirurgia_qt'),
                ('fez_qt_cirurgia', 'data_qt_cirurgia', 'QT + Cirurgia', 'obs_qt_cirurgia'),
                ('fez_rt_cirurgia', 'data_rt_cirurgia', 'RT + Cirurgia', 'obs_rt_cirurgia'),
                ('fez_qt_rt', 'data_qt_rt', 'QT + RT', 'obs_qt_rt'),
                ('fez_rt_qt', 'data_rt_qt', 'RT + QT', 'obs_rt_qt'),
                ('fez_imunoterapia', 'data_imunoterapia', 'Imunoterapia', 'obs_imunoterapia')
            ]
            
            for checkbox, campo_data, nome, campo_obs in tratamentos_map:
                if form.cleaned_data.get(checkbox) and form.cleaned_data.get(campo_data):
                    HistoricoTratamento.objects.create(
                        paciente=paciente, 
                        tipo_tratamento=nome, 
                        data=form.cleaned_data.get(campo_data),
                        detalhes=form.cleaned_data.get(campo_obs)
                    )

            if form.cleaned_data.get('fez_cirurgia') and form.cleaned_data.get('data_cirurgia'):
                HistoricoTratamento.objects.create(
                    paciente=paciente, 
                    tipo_tratamento='Cirurgia', 
                    data=form.cleaned_data.get('data_cirurgia'),
                    detalhes=form.cleaned_data.get('qual_cirurgia')
                )

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
            return redirect('aba_cadastro')
    else:
        form = AuthenticationForm()
    return render(request, 'monitoramento/login.html', {'form': form})

def fazer_logout(request):
    logout(request)
    return redirect('login')

def alternar_status_paciente(request, prontuario):
    paciente = get_object_or_404(Paciente, prontuario=prontuario)
    paciente.ativo = not paciente.ativo
    paciente.save()
    
    status_texto = "ativado" if paciente.ativo else "desabilitado"
    messages.success(request, f'Paciente {paciente.nome} foi {status_texto} com sucesso!')
    return redirect('aba_dados')