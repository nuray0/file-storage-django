import mimetypes
import os
import zipfile

from django.conf import settings
from django.http import FileResponse, JsonResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from .models import ActionLog

# Constants
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB
NUM_PARTS = 16


@csrf_exempt
def upload_file(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    if uploaded_file.size > MAX_FILE_SIZE:
        return JsonResponse({'error': 'File exceeds 16MB limit'}, status=400)

    file_data = uploaded_file.read()
    part_size = len(file_data) // NUM_PARTS + (len(file_data) % NUM_PARTS > 0)
    parts = [
        file_data[i : i + part_size]
        for i in range(0, len(file_data), part_size)
    ]

    filename_base, ext = os.path.splitext(uploaded_file.name)
    timestamp = now().strftime('%Y%m%d%H%M%S')
    zip_name = f'{filename_base}_{timestamp}.zip'

    # Define input directory inside MEDIA_ROOT
    input_dir = os.path.join(settings.MEDIA_ROOT, 'input')
    os.makedirs(input_dir, exist_ok=True)  # make sure it exists

    # Final path where ZIP will be saved
    zip_path = os.path.join(input_dir, zip_name)

    with zipfile.ZipFile(zip_path, 'w') as archive:
        for idx, part in enumerate(parts):
            archive.writestr(f'part_{idx + 1:02d}.bin', part)

    # TODO: Replace with actual user ID when auth is implemented
    ActionLog.objects.create(
        user_id=None,
        timestamp=now(),
        action_type='upload',
        filename=zip_name,
        original_filename=filename_base,
        file_extension=ext.lstrip('.'),
    )

    return JsonResponse(
        {
            'message': 'File uploaded and archived',
            'archive_name': zip_name,
            'original_filename': filename_base,
            'file_extension': ext.lstrip('.'),
            'download_url': request.build_absolute_uri(
                f'/download/{zip_name}'
            ),
        }
    )


@csrf_exempt
def download_file(request, archive_name):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET allowed'}, status=405)

    zip_path = os.path.join(settings.MEDIA_ROOT, 'input', archive_name)
    if not os.path.exists(zip_path):
        return JsonResponse({'error': 'Archive not found'}, status=404)

    try:
        with zipfile.ZipFile(zip_path, 'r') as archive:
            parts = [
                archive.open(name).read()
                for name in sorted(archive.namelist())
            ]

        log = (
            ActionLog.objects.filter(filename=archive_name)
            .order_by('-timestamp')
            .first()
        )
        if log:
            original_filename = log.original_filename
            extension = log.file_extension or ''
        else:
            original_filename = os.path.splitext(archive_name)[0]
            extension = ''

        extension = extension.lstrip('.')
        restored_name = (
            f'{original_filename}_restored.{extension}'
            if extension
            else f'{original_filename}_restored'
        )

        output_dir = os.path.join(settings.MEDIA_ROOT, 'output')
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, restored_name)

        # Save restored file in media/output
        with open(output_path, 'wb') as f:
            f.write(b''.join(parts))

        # TODO: Replace with actual user ID when auth is implemented
        ActionLog.objects.create(
            user_id=None,
            timestamp=now(),
            action_type='download',
            filename=restored_name,
        )

        content_type, _ = mimetypes.guess_type(restored_name)
        return FileResponse(
            open(output_path, 'rb'),
            as_attachment=True,
            filename=restored_name,
            content_type=content_type or 'application/octet-stream',
        )

    except Exception as e:
        return JsonResponse(
            {'error': f'Failed to extract archive: {str(e)}'}, status=500
        )
