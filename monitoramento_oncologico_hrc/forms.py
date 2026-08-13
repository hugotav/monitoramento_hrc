from django import forms
from .models import Paciente

class PacienteForm(forms.ModelForm):
    # Campos de tratamento virtuais (usados apenas na interface para gravar na tabela HistoricoTratamento)

    obs_indicacao_cirurgia = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Observação...'}))
    obs_qt = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Observação...'}))
    obs_rt = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Observação...'}))
    obs_cirurgia_rt = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Observação...'}))
    obs_cirurgia_qt = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Observação...'}))
    obs_qt_cirurgia = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Observação...'}))
    obs_rt_cirurgia = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Observação...'}))
    obs_qt_rt = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Observação...'}))
    obs_rt_qt = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Observação...'}))
    obs_imunoterapia = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Observação...'}))

    indicacao_cirurgia = forms.BooleanField(required=False)
    data_indicacao_cirurgia = forms.DateField(required=False, widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    
    fez_cirurgia = forms.BooleanField(required=False)
    data_cirurgia = forms.DateField(required=False, widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    qual_cirurgia = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Qual cirurgia/detalhes...'}))

    fez_qt = forms.BooleanField(required=False)
    data_qt = forms.DateField(required=False, widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))

    fez_rt = forms.BooleanField(required=False)
    data_rt = forms.DateField(required=False, widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))

    fez_cirurgia_rt = forms.BooleanField(required=False)
    data_cirurgia_rt = forms.DateField(required=False, widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))

    fez_cirurgia_qt = forms.BooleanField(required=False)
    data_cirurgia_qt = forms.DateField(required=False, widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))

    fez_qt_cirurgia = forms.BooleanField(required=False)
    data_qt_cirurgia = forms.DateField(required=False, widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))

    fez_rt_cirurgia = forms.BooleanField(required=False)
    data_rt_cirurgia = forms.DateField(required=False, widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))

    fez_qt_rt = forms.BooleanField(required=False)
    data_qt_rt = forms.DateField(required=False, widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))

    fez_rt_qt = forms.BooleanField(required=False)
    data_rt_qt = forms.DateField(required=False, widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))

    fez_imunoterapia = forms.BooleanField(required=False)
    data_imunoterapia = forms.DateField(required=False, widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = Paciente
        fields = '__all__'
        exclude = ['ativo']
        widgets = {
            'data_nascimento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'data_entrada': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'data_diagnostico': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'especialidade': forms.Select(attrs={'class': 'form-select'}),
            'diagnostico': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. Tradução do 'Selecione uma opção' e Calendários
        for nome_campo, campo in list(self.fields.items()):
            if hasattr(campo, 'choices'):
                campo.choices = [('', 'Selecione uma opção')] + [
                    opcao for opcao in campo.choices if opcao[0] != ''
                ]
            
            if isinstance(campo, forms.DateField):
                campo.widget = forms.DateInput(
                    format='%Y-%m-%d', 
                    attrs={'type': 'date', 'class': 'form-control'}
                )

        # ==========================================
        # REGRAS DE NEGÓCIO 1 E 2
        # ==========================================
        
        # A) Campos obrigatórios no primeiro cadastro
        obrigatorios = ['prontuario', 'nome', 'sexo', 'data_nascimento', 'data_entrada']
        for campo in obrigatorios:
            self.fields[campo].required = True
            # Adiciona o atributo required no HTML para o navegador validar
            self.fields[campo].widget.attrs['required'] = 'required'

        # B) Campos NÃO obrigatórios inicialmente
        nao_obrigatorios = ['especialidade', 'diagnostico', 'data_diagnostico']
        for campo in nao_obrigatorios:
            self.fields[campo].required = False

        # C) Bloqueios (Read-only) caso o paciente já exista
        if self.instance.pk:
            # Impede a edição do número do Prontuário para não duplicar o cadastro no banco
            self.fields['prontuario'].widget.attrs['readonly'] = True
            self.fields['prontuario'].widget.attrs['style'] = 'background-color: #e2e8f0; pointer-events: none;'

        # 2. OCULTAR BLOCO DE TRATAMENTOS NO PRIMEIRO CADASTRO
        if not self.instance.pk:
            campos_tratamento = [
                'indicacao_cirurgia', 'data_indicacao_cirurgia', 'obs_indicacao_cirurgia',
                'fez_cirurgia', 'data_cirurgia', 'qual_cirurgia',
                'fez_qt', 'data_qt', 'obs_qt',
                'fez_rt', 'data_rt', 'obs_rt',
                'fez_cirurgia_rt', 'data_cirurgia_rt', 'obs_cirurgia_rt',
                'fez_cirurgia_qt', 'data_cirurgia_qt', 'obs_cirurgia_qt',
                'fez_qt_cirurgia', 'data_qt_cirurgia', 'obs_qt_cirurgia',
                'fez_rt_cirurgia', 'data_rt_cirurgia', 'obs_rt_cirurgia',
                'fez_qt_rt', 'data_qt_rt', 'obs_qt_rt',
                'fez_rt_qt', 'data_rt_qt', 'obs_rt_qt',
                'fez_imunoterapia', 'data_imunoterapia', 'obs_imunoterapia'
            ]
            
            for campo in campos_tratamento:
                if campo in self.fields:
                    self.fields.pop(campo)