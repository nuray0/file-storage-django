import os
import shutil
import zipfile
from tempfile import mkdtemp

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings


@override_settings(MEDIA_ROOT=mkdtemp())
class FileStorageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_filename = 'test_file.txt'
        self.test_content = b'Hello, this is a test file for upload.'

        self.uploaded_file = SimpleUploadedFile(
            self.test_filename, self.test_content, content_type='text/plain'
        )

    def tearDown(self):
        # Удаляем временные директории после тестов
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)

    def test_file_upload_creates_archive(self):
        response = self.client.post('/upload/', {'file': self.uploaded_file})
        self.assertEqual(response.status_code, 200)
        data = response.json()

        archive_name = data['archive_name']
        archive_path = os.path.join(settings.MEDIA_ROOT, 'input', archive_name)
        self.assertTrue(os.path.exists(archive_path))

        # Check that ZIP archive has 16 parts or fewer
        with zipfile.ZipFile(archive_path, 'r') as zf:
            self.assertLessEqual(len(zf.namelist()), 16)

    def test_download_restores_original_content(self):
        upload_resp = self.client.post(
            '/upload/', {'file': self.uploaded_file}
        )
        self.assertEqual(upload_resp.status_code, 200)
        archive_name = upload_resp.json()['archive_name']

        download_resp = self.client.get(f'/download/{archive_name}')
        self.assertEqual(download_resp.status_code, 200)

        downloaded_data = b''.join(download_resp.streaming_content)
        self.assertEqual(downloaded_data, self.test_content)

    def test_upload_large_file_rejected(self):
        big_file = SimpleUploadedFile(
            'big_file.bin',
            b'x' * (16 * 1024 * 1024 + 1),  # 16MB + 1 byte
            content_type='application/octet-stream',
        )
        response = self.client.post('/upload/', {'file': big_file})
        self.assertEqual(response.status_code, 400)
        self.assertIn('File exceeds', response.json()['error'])

    def test_download_nonexistent_archive(self):
        response = self.client.get('/download/does_not_exist.zip')
        self.assertEqual(response.status_code, 404)

        if response.headers.get('Content-Type') == 'application/json':
            self.assertIn('Archive not found', response.json()['error'])
        else:
            self.fail(
                f'Expected JSON response, got: {response.content.decode()}'
            )
