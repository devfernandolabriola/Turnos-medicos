from django import forms
from .models import Turno, Medico,Especialidad,Paciente,ObraSocial

class LoginForm(forms.Form):
    dni = forms.CharField(label="DNI", max_length=20)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

class RegisterForm(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=100)
    apellido = forms.CharField(label="Apellido", max_length=100)
    dni = forms.CharField(label="DNI", max_length=20)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput, min_length=6)
    confirm_password = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)
    correo = forms.EmailField(label="Correo Electrónico",max_length=100,widget=forms.EmailInput(attrs={'class': 'form-control'}))
    telefono = forms.IntegerField(label="Teléfono",widget=forms.NumberInput(attrs={'class': 'form-control'}))
    obrasocial = forms.ModelChoiceField(label="Obra Social",queryset=ObraSocial.objects.all(),empty_label="Seleccione su Obra Social (o Particular)",required=False,widget=forms.Select(attrs={'class': 'form-select'}))
    numero_asociado = forms.CharField(label="Número de Asociado / Afiliado",max_length=200,required=False,widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if Paciente.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Este DNI ya está registrado.")
        if not dni.isdigit() or len(dni) < 7:
            raise forms.ValidationError("DNI inválido.")
        return dni

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Las contraseñas no coinciden.")


class SeleccionTurnoForm(forms.Form):
    especialidad = forms.ModelChoiceField(
        queryset=Especialidad.objects.all(),
        empty_label="Seleccione una especialidad",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'especialidad-select'})
    )
    medico = forms.ModelChoiceField(
        queryset=Medico.objects.none(),  # inicial vacío, se llenará con JS/AJAX
        empty_label="Seleccione un médico",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'medico-select'})
    )
    turno = forms.ModelChoiceField(
        queryset=Turno.objects.none(),  # también vacío
        empty_label="Seleccione un turno",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'turno-select'})
    )

