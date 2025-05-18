from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import File
from .serializers import FileSerializer
import hashlib
from django.core.files.base import ContentFile
from rest_framework.decorators import action
from django.db import models
from django.core.files.base import File as DjangoFile

# Create your views here.

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def create(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a file with the same original filename already exists
        if File.objects.filter(original_filename=file_obj.name).exists():
            return Response(
                {'error': f"A file named '{file_obj.name}' has already been uploaded."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate SHA256 hash
        hasher = hashlib.sha256()
        for chunk in file_obj.chunks():
            hasher.update(chunk)
        file_hash = hasher.hexdigest()

        # Check for duplicate by hash
        existing_file = File.objects.filter(file_hash=file_hash).first()
        if existing_file:
            # Create a new DB entry referencing the existing file path only
            new_file = File(
                original_filename=file_obj.name,
                file_type=file_obj.content_type,
                size=file_obj.size,
                file_hash=file_hash
            )
            new_file.file.name = existing_file.file.name
            new_file.save()
            serializer = self.get_serializer(new_file)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {**serializer.data, 'deduplicated': True, 'message': 'Duplicate file detected. Reference created.'},
                status=status.HTTP_201_CREATED,
                headers=headers
            )

        # Not a duplicate, save as new (this will upload the file)
        data = {
            'file': file_obj,
            'original_filename': file_obj.name,
            'file_type': file_obj.content_type,
            'size': file_obj.size,
            'file_hash': file_hash
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'])
    def storage_savings(self, request):
        total_files = File.objects.count()
        unique_files = File.objects.values('file_hash').distinct().count()
        total_size = File.objects.aggregate(models.Sum('size'))['size__sum'] or 0
        unique_size = File.objects.values('file_hash').distinct().aggregate(models.Sum('size'))['size__sum'] or 0
        savings = total_size - unique_size
        return Response({
            'total_files': total_files,
            'unique_files': unique_files,
            'total_size': total_size,
            'unique_size': unique_size,
            'savings': savings
        })
