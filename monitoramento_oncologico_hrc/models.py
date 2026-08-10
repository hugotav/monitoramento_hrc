from django.db import models
from datetime import date

class Paciente(models.Model):
    ESPECIALIDADES = [
        ('cirurgia_oncologica', 'Cirurgia Oncológica'),
        ('cirurgia_toracica', 'Cirurgia Torácica'),
        ('oncoginecologia', 'Oncoginecologia'),
        ('cabeca_pescoco', 'Cirurgia de Cabeça e Pescoço'),
        ('mastologia', 'Mastologia'),
        ('neurocirurgia', 'Neurocirurgia'),
        ('urologia', 'Urologia'),
        ('oncohematologia', 'Oncohematologia'),
        ('oncologia_clinica', 'Oncologia Clínica'),
    ]

    CID_OPCOES = [
        ('C50', 'C50 - Neoplasia maligna da mama'),
        ('C61', 'C61 - Neoplasia maligna da próstata'),
        ('C34', 'C34 - Neoplasia maligna dos brônquios e dos pulmões'),
        # Aqui depois podemos alimentar com a lista completa do CID-10 Oncológico
        ('OUTROS', 'Outros'),
    ]

    # Dados Pessoais
    prontuario = models.AutoField(primary_key=True, verbose_name="Prontuário")
    nome = models.CharField(max_length=200, verbose_name="Nome do Paciente")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    especialidade = models.CharField(max_length=50, choices=ESPECIALIDADES, verbose_name="Especialidade")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    # Datas de Rastreio e Diagnóstico
    data_entrada = models.DateField(verbose_name="Data de Entrada", null=True, blank=True)
    diagnostico = models.CharField(max_length=10, choices=CID_OPCOES, verbose_name="Diagnóstico (CID-10)", null=True, blank=True)
    data_diagnostico = models.DateField(verbose_name="Data do Diagnóstico", null=True, blank=True)

    # Tratamentos (Booleanos para ativar os campos de data no frontend)
    fez_cirurgia = models.BooleanField(default=False, verbose_name="Cirurgia?")
    data_cirurgia = models.DateField(null=True, blank=True)

    fez_qt = models.BooleanField(default=False, verbose_name="Quimioterapia (QT)?")
    data_qt = models.DateField(null=True, blank=True)

    fez_rt = models.BooleanField(default=False, verbose_name="Radioterapia (RT)?")
    data_rt = models.DateField(null=True, blank=True)

    fez_cirurgia_rt = models.BooleanField(default=False, verbose_name="Cirurgia + RT?")
    data_cirurgia_rt = models.DateField(null=True, blank=True)

    fez_cirurgia_qt = models.BooleanField(default=False, verbose_name="Cirurgia + QT?")
    data_cirurgia_qt = models.DateField(null=True, blank=True)

    fez_qt_cirurgia = models.BooleanField(default=False, verbose_name="QT + Cirurgia?")
    data_qt_cirurgia = models.DateField(null=True, blank=True)

    fez_rt_cirurgia = models.BooleanField(default=False, verbose_name="RT + Cirurgia?")
    data_rt_cirurgia = models.DateField(null=True, blank=True)

    fez_qt_rt = models.BooleanField(default=False, verbose_name="QT + RT?")
    data_qt_rt = models.DateField(null=True, blank=True)

    fez_rt_qt = models.BooleanField(default=False, verbose_name="RT + QT?")
    data_rt_qt = models.DateField(null=True, blank=True)

    # REGRAS DE NEGÓCIO E CÁLCULOS AUTOMÁTICOS --------------------------
    
    @property
    def idade(self):
        if self.data_nascimento:
            hoje = date.today()
            return hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        return 0

    @property
    def data_primeiro_tratamento(self):
        """Busca a data mais antiga entre todos os tratamentos preenchidos"""
        datas_preenchidas = [
            d for d in [
                self.data_cirurgia, self.data_qt, self.data_rt, 
                self.data_cirurgia_rt, self.data_cirurgia_qt, 
                self.data_qt_cirurgia, self.data_rt_cirurgia, 
                self.data_qt_rt, self.data_rt_qt
            ] if d is not None
        ]
        if datas_preenchidas:
            return min(datas_preenchidas)
        return None

    @property
    def situacao(self):
        if self.data_entrada and not self.data_diagnostico:
            return "Aguardando Diagnóstico"
        if self.data_diagnostico and not self.data_primeiro_tratamento:
            return "Aguardando Tratamento"
        if self.data_primeiro_tratamento:
            return "Em Tratamento"
        return "Sem Situação Definida"

    @property
    def dias_entrada_diagnostico(self):
        if not self.data_entrada:
            return 0
        data_final = self.data_diagnostico if self.data_diagnostico else date.today()
        return (data_final - self.data_entrada).days

    @property
    def dias_diagnostico_tratamento(self):
        if not self.data_diagnostico:
            return 0
        data_final = self.data_primeiro_tratamento if self.data_primeiro_tratamento else date.today()
        return (data_final - self.data_diagnostico).days

    def __str__(self):
        return f"{self.prontuario} - {self.nome}"