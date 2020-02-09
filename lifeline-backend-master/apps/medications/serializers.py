from rest_framework import serializers

from apps.utils.date_time import get_js_timestamp
from apps.tasks.models import Schedule

from .models import (
    Prescription,
    MedicationCategory,
    MedicationIntake,
    Drug,
    TimeSlot
)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationCategory
        fields = ('id', 'term')


class TimeSlotSerializer(serializers.ModelSerializer):
    timeSlotType = serializers.CharField(source='time_slot_type')
    timeStep = serializers.IntegerField(source='time_step', required=False)
    dateTime = serializers.DateTimeField(source='datetime', required=False)

    class Meta:
        model = TimeSlot
        fields = ('id', 'timeStep', 'timeSlotType', 'quantity', 'dow', 'dateTime', 'prescription')

class IntakeSerializerLight(serializers.ModelSerializer):
    class Meta:
        model = MedicationIntake
        fields = '__all__'

class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = ('id', 'name', 'unit')

class PrescriptionSerializer(serializers.ModelSerializer):
    prescriptionType = serializers.CharField(source='prescription_type')
    isActive = serializers.BooleanField(source='is_active', required=False, default=True)

    category = serializers.CharField(source='drug.category.term', read_only=True)
    drugName = serializers.CharField(source='drug.name', read_only=True)
    drugUnit = serializers.CharField(source='drug.unit', read_only=True)

    durationStart = serializers.DateTimeField(source='duration_start')
    durationEnd = serializers.DateTimeField(source='duration_end', required=False)

    repeatEvery = serializers.IntegerField(source='repeat_every', required=False)
    repeatReccurence = serializers.CharField(source='repeat_reccurence', required=False)

    cycleEveryValue = serializers.IntegerField(source='cycle_every_value', required=False)
    cycleEveryReccurence = serializers.CharField(source='cycle_every_reccurence', required=False)
    cycleOverValue = serializers.IntegerField(source='cycle_over_value', required=False)
    cycleOverReccurence = serializers.CharField(source='cycle_over_reccurence', required=False)

    timeSlots = TimeSlotSerializer(source='time_slots', read_only=True, many=True, default=[])
    intakes = IntakeSerializerLight(read_only=True, many=True, default=[])
    category = CategorySerializer(source='drug.category', read_only=True)

    class Meta:
        model = Prescription
        fields = ('id', 'prescriptionType', 'mode', 'drug', 'duration', 'file',
                  'durationStart', 'durationEnd', 'meal', 'comment', 'repeat', 'editor',
                  'cycle', 'repeatEvery', 'repeatReccurence', 'cycleEveryValue', 'creator',
                  'cycleEveryReccurence', 'cycleOverValue', 'cycleOverReccurence', 'category',
                  'timeSlots', 'intakes', 'mode', 'category', 'isActive', 'drugName', 'drugUnit')


class PrescriptionLightSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='drug.category.term', read_only=True)
    slug = serializers.CharField(default='medication')
    unit = serializers.CharField(source='drug.unit', read_only=True)

    class Meta:
        model = Prescription
        fields = (
            'id', 'creator', 'editor', 'is_active', 'drug', 'name', 'created', 'modified', 'slug',
            'unit', 'max_quantity'
        )


class PrescriptionScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Schedule
        fields = (
            'comment', 'date', 'time', 'slot', 'prescription',
            'status', 'periodic', 'file', 'creator'
        )


class PrescriptionIntakeSerializer(serializers.ModelSerializer):
    maxQuantity = serializers.CharField(source='max_quantity')
    isActive = serializers.CharField(source='is_active')

    category = serializers.SerializerMethodField()
    drug = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = ('id', 'comment', 'maxQuantity', 'isActive', 'category', 'drug')

    def get_category(self, obj):
        return CategorySerializer(obj.drug.category).data

    def get_drug(self, obj):
        return DrugSerializer(obj.drug).data


class MedicationIntakeSerializer(serializers.ModelSerializer):
    stock = serializers.CharField(source='stock_type')
    action = serializers.CharField(source='action_type')

    prescription = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    class Meta:
        model = MedicationIntake
        fields = ('id', 'action', 'stock', 'comment', 'time', 'prescription')

    def get_time(self, obj):
        timestamp = obj.time
        return get_js_timestamp(timestamp)

    def get_prescription(self, obj):
        return PrescriptionIntakeSerializer(obj.prescription).data
