from rest_framework import serializers
from .models import Especialidad
from .models import Medico
from .models import Turno
from .models import DisponibilidadMedico
from .models import Paciente
from django.contrib.auth.hashers import make_password

class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = '__all__'



class MedicoSerializer(serializers.ModelSerializer):
    especialidad = EspecialidadSerializer(read_only=True)
    especialidad_id = serializers.PrimaryKeyRelatedField(
        queryset=Especialidad.objects.all(),
        source='especialidad',
        write_only=True
    )

    class Meta:
        model = Medico
        fields = ['id', 'nombre', 'apellido', 'especialidad', 'especialidad_id']

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido', 'dni', 'password']  # Solo los campos necesarios
        extra_kwargs = {
            'password': {'write_only': True}  # Para que no se muestre en GET
        }

    def create(self, validated_data):
        # Hashear la contraseña antes de guardar
        password = validated_data.pop("password", None)
        if password:
            validated_data["password"] = make_password(password)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Hashear la contraseña solo si se envía
        password = validated_data.pop("password", None)
        if password:
            instance.password = make_password(password)
        # Actualizar el resto de campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    
class DisponibilidadMedicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisponibilidadMedico
        fields = '__all__'

class TurnoSerializer(serializers.ModelSerializer):
    medico = MedicoSerializer(read_only=True)
    medico_id = serializers.PrimaryKeyRelatedField(
        queryset=Medico.objects.all(),
        source='medico',
        write_only=True
    )

    paciente = PacienteSerializer(read_only=True)
    paciente_id = serializers.PrimaryKeyRelatedField(
        queryset=Paciente.objects.all(),
        source='paciente',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Turno
        fields = [
            'id',
            'fecha',
            'hora',
            'disponible',
            'medico',
            'medico_id',
            'paciente',
            'paciente_id'
        ]