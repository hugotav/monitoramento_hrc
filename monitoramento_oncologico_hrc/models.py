from django.db import models
from datetime import date

class Paciente(models.Model):

    SEXO_OPCOES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]

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
        ('C00', 'C00 - Neoplasia maligna do lábio'),
        ('C01', 'C01 - Neoplasia maligna da base da língua'),
        ('C02', 'C02 - Neoplasia maligna de outras partes da língua'),
        ('C03', 'C03 - Neoplasia maligna da gengiva'),
        ('C04', 'C04 - Neoplasia maligna do assoalho da boca'),
        ('C05', 'C05 - Neoplasia maligna do palato'),
        ('C06', 'C06 - Neoplasia maligna de outras partes da boca'),
        ('C07', 'C07 - Neoplasia maligna da glândula parótida'),
        ('C08', 'C08 - Neoplasia maligna de outras glândulas salivares'),
        ('C09', 'C09 - Neoplasia maligna da amígdala'),
        ('C10', 'C10 - Neoplasia maligna da orofaringe'),
        ('C11', 'C11 - Neoplasia maligna da nasofaringe'),
        ('C12', 'C12 - Neoplasia maligna do seio piriforme'),
        ('C13', 'C13 - Neoplasia maligna da hipofaringe'),
        ('C14', 'C14 - Neoplasia maligna de outras localizações do lábio, cavidade oral e faringe'),
        ('C15', 'C15 - Neoplasia maligna do esôfago'),
        ('C16', 'C16 - Neoplasia maligna do estômago'),
        ('C17', 'C17 - Neoplasia maligna do intestino delgado'),
        ('C18', 'C18 - Neoplasia maligna do cólon'),
        ('C19', 'C19 - Neoplasia maligna da junção retossigmoide'),
        ('C20', 'C20 - Neoplasia maligna do reto'),
        ('C21', 'C21 - Neoplasia maligna do ânus e do canal anal'),
        ('C22', 'C22 - Neoplasia maligna do fígado e das vias biliares intra-hepáticas'),
        ('C23', 'C23 - Neoplasia maligna da vesícula biliar'),
        ('C24', 'C24 - Neoplasia maligna de outras partes das vias biliares'),
        ('C25', 'C25 - Neoplasia maligna do pâncreas'),
        ('C26', 'C26 - Neoplasia maligna de outros órgãos digestivos e de localizações mal definidas'),
        ('C30', 'C30 - Neoplasia maligna das fossas nasais e do ouvido médio'),
        ('C31', 'C31 - Neoplasia maligna dos seios da face'),
        ('C32', 'C32 - Neoplasia maligna da laringe'),
        ('C33', 'C33 - Neoplasia maligna da traqueia'),
        ('C34', 'C34 - Neoplasia maligna dos brônquios e dos pulmões'),
        ('C37', 'C37 - Neoplasia maligna do timo'),
        ('C38', 'C38 - Neoplasia maligna do coração, mediastino e pleura'),
        ('C39', 'C39 - Neoplasia maligna de outros órgãos respiratórios e intratorácicos'),
        ('C40', 'C40 - Neoplasia maligna dos ossos e cartilagens dos membros'),
        ('C41', 'C41 - Neoplasia maligna dos ossos e cartilagens de outras localizações'),
        ('C43', 'C43 - Melanoma maligno da pele'),
        ('C44', 'C44 - Outras neoplasias malignas da pele'),
        ('C45', 'C45 - Mesotelioma'),
        ('C46', 'C46 - Sarcoma de Kaposi'),
        ('C47', 'C47 - Neoplasia maligna dos nervos periféricos e do sistema nervoso autônomo'),
        ('C48', 'C48 - Neoplasia maligna do retroperitônio e do peritônio'),
        ('C49', 'C49 - Neoplasia maligna de outros tecidos conjuntivos e tecidos moles'),
        ('C50', 'C50 - Neoplasia maligna da mama'),
        ('C51', 'C51 - Neoplasia maligna da vulva'),
        ('C52', 'C52 - Neoplasia maligna da vagina'),
        ('C53', 'C53 - Neoplasia maligna do colo do útero'),
        ('C54', 'C54 - Neoplasia maligna do corpo do útero'),
        ('C55', 'C55 - Neoplasia maligna do útero, porção não especificada'),
        ('C56', 'C56 - Neoplasia maligna do ovário'),
        ('C57', 'C57 - Neoplasia maligna de outros órgãos genitais femininos'),
        ('C58', 'C58 - Neoplasia maligna da placenta'),
        ('C60', 'C60 - Neoplasia maligna do pênis'),
        ('C61', 'C61 - Neoplasia maligna da próstata'),
        ('C62', 'C62 - Neoplasia maligna dos testículos'),
        ('C63', 'C63 - Neoplasia maligna de outros órgãos genitais masculinos'),
        ('C64', 'C64 - Neoplasia maligna do rim, exceto pelve renal'),
        ('C65', 'C65 - Neoplasia maligna da pelve renal'),
        ('C66', 'C66 - Neoplasia maligna do ureter'),
        ('C67', 'C67 - Neoplasia maligna da bexiga'),
        ('C68', 'C68 - Neoplasia maligna de outros órgãos urinários'),
        ('C69', 'C69 - Neoplasia maligna do olho e anexos'),
        ('C70', 'C70 - Neoplasia maligna das meninges'),
        ('C71', 'C71 - Neoplasia maligna do encéfalo'),
        ('C72', 'C72 - Neoplasia maligna da medula espinhal, dos nervos cranianos e de outras partes do sistema nervoso central'),
        ('C73', 'C73 - Neoplasia maligna da glândula tireoide'),
        ('C74', 'C74 - Neoplasia maligna da glândula suprarrenal'),
        ('C75', 'C75 - Neoplasia maligna de outras glândulas endócrinas e estruturas relacionadas'),
        ('C76', 'C76 - Neoplasia maligna de outras localizações e de localizações mal definidas'),
        ('C77', 'C77 - Neoplasia maligna secundária e não especificada dos gânglios linfáticos'),
        ('C78', 'C78 - Neoplasia maligna secundária dos órgãos respiratórios e digestivos'),
        ('C79', 'C79 - Neoplasia maligna secundária de outras localizações'),
        ('C80', 'C80 - Neoplasia maligna sem especificação de localização'),
        ('C81', 'C81 - Doença de Hodgkin'),
        ('C82', 'C82 - Linfoma folicular'),
        ('C83', 'C83 - Linfoma não folicular'),
        ('C84', 'C84 - Linfoma de células T periféricas e cutâneas'),
        ('C85', 'C85 - Outros tipos especificados de linfoma não Hodgkin'),
        ('C86', 'C86 - Outros tipos especificados de linfoma de células T/NK'),
        ('C88', 'C88 - Doenças malignas relacionadas às células linfoides'),
        ('C90', 'C90 - Mieloma múltiplo e neoplasias malignas de plasmócitos'),
        ('C91', 'C91 - Leucemia linfoide'),
        ('C92', 'C92 - Leucemia mieloide'),
        ('C93', 'C93 - Leucemia monocítica'),
        ('C94', 'C94 - Outras leucemias de células especificadas'),
        ('C95', 'C95 - Leucemia de tipo celular não especificado'),
        ('C96', 'C96 - Outras neoplasias malignas do tecido linfoide, hematopoético e tecidos correlatos'),
        ('C97', 'C97 - Neoplasias malignas de localizações múltiplas independentes'),
    ]

    # Dados Pessoais
    prontuario = models.CharField(max_length=50, primary_key=True, verbose_name="Prontuário")
    nome = models.CharField(max_length=200, verbose_name="Nome do Paciente")
    sexo = models.CharField(max_length=1, choices=SEXO_OPCOES, verbose_name="Sexo", null=True)
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    especialidade = models.CharField(max_length=50, choices=ESPECIALIDADES, verbose_name="Especialidade")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    # Datas de Rastreio e Diagnóstico
    data_entrada = models.DateField(verbose_name="Data de Entrada")
    diagnostico = models.CharField(max_length=10, choices=CID_OPCOES, verbose_name="Diagnóstico (CID-10)", null=True, blank=True)
    data_diagnostico = models.DateField(verbose_name="Data do Diagnóstico", null=True, blank=True)

    # REGRAS DE NEGÓCIO E CÁLCULOS AUTOMÁTICOS --------------------------
    
    @property
    def idade(self):
        if self.data_nascimento:
            hoje = date.today()
            return hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        return 0

    @property
    def data_primeiro_tratamento(self):
        """Busca a data mais antiga na tabela separada de histórico, ignorando 'Indicação de Cirurgia'"""
        primeiro = self.tratamentos.exclude(tipo_tratamento='Indicação de Cirurgia').order_by('data').first()
        if primeiro:
            return primeiro.data
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


# NOVA TABELA PARA O HISTÓRICO INFINITO DE TRATAMENTOS
class HistoricoTratamento(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='tratamentos')
    tipo_tratamento = models.CharField(max_length=100, verbose_name="Tipo")
    data = models.DateField(verbose_name="Data do Tratamento")
    detalhes = models.CharField(max_length=200, blank=True, null=True, verbose_name="Detalhes")
    data_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f"{self.paciente.nome} - {self.tipo_tratamento} ({self.data})"