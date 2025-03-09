from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework.validators import UniqueValidator  
from django.contrib.auth.models import User
from .models import Professor, Module, ModuleInstance, Rating


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset = User.objects.all())]  # Use UniqueValidator
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            password = validated_data['password']
        )
        return user


class ProfessorSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Professor
        fields = ('id', 'name', 'department', 'email', 'average_rating')

    def get_average_rating(self, obj):
        return obj.get_average_rating()


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ('id', 'code', 'title')


class ProfessorInModuleInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = ('id', 'name', 'department')


class ModuleInstanceSerializer(serializers.ModelSerializer):
    module_code = serializers.CharField(source = 'module.code', read_only = True)
    module_title = serializers.CharField(source = 'module.title', read_only = True)
    professors = ProfessorInModuleInstanceSerializer(many = True, read_only = True)

    class Meta:
        model = ModuleInstance
        fields = ('id', 'module_code', 'module_title', 'year', 'semester', 'professors')


class RatingSerializer(serializers.ModelSerializer):
    professor_name = serializers.CharField(source = 'professor.name', read_only = True)
    module_instance_details = serializers.SerializerMethodField()

    def get_module_instance_details(self, obj):
        return str(obj.module_instance)

    class Meta:
        model = Rating
        fields = ('id', 'professor_name', 'module_instance_details', 'rating', 'created_at')
        read_only_fields = ('created_at',)


class CreateRatingSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(validators = [MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        model = Rating
        fields = ('professor', 'module_instance', 'rating')

    def validate(self, data):
        professor = data['professor']
        module_instance = data['module_instance']

        if not module_instance.professors.filter(id = professor.id).exists():
            raise serializers.ValidationError("This professor is not assigned to the selected module instance.")
        
        user = self.context['request'].user
        existing_rating = Rating.objects.filter(
            user=user,
            professor=professor,
            module_instance=module_instance
        ).first()

        if existing_rating:
            # If a rating already exists, we will just update the existing one instead of creating a new one
            data['existing_rating'] = existing_rating

        return data
    
    def create(self, validated_data):
        existing_rating = validated_data.get('existing_rating', None)

        if existing_rating:
            existing_rating.rating = validated_data['rating']
            existing_rating.save()
            return existing_rating
        
        # If there's no existing rating, create a new one
        validated_data['user'] = self.context['request'].user  # Assign logged-in user
        return Rating.objects.create(**validated_data)


class ProfessorModuleRatingSerializer(serializers.Serializer):
    average_rating = serializers.IntegerField()
    module_code = serializers.CharField()
    module_title = serializers.CharField()