# -*- coding: utf-8 -*-
"""
    test_flask_dropzone
    ~~~~~~~~~~~~~~~~~~~

    :author: Grey Li <withlihui@gmail.com>
    :copyright: (c) 2017 by Grey Li.
    :license: MIT, see LICENSE for more details.
"""
import unittest

from flask import Flask, render_template_string, current_app, url_for

from flask_dropzone import Dropzone, allowed_file_extensions, _Dropzone, get_url
from flask_wtf import CSRFProtect


class DropzoneTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True
        self.app.secret_key = 'for test'
        dropzone = Dropzone(self.app)  # noqa
        csrf = CSRFProtect(self.app)  # noqa

        self.dropzone = _Dropzone

        @self.app.route('/upload')
        def upload():
            pass

        @self.app.route('/')
        def index():
            return render_template_string('''
                    {{ dropzone.load_css() }}\n{{ dropzone.create(action_view='upload') }}
                    {{ dropzone.load_js() }}\n{{ dropzone.config() }}''')

        @self.app.route('/load')
        def load():
            return render_template_string('''
                            {{ dropzone.load() }}\n{{ dropzone.create(action_view='upload') }}''')

        self.context = self.app.test_request_context()
        self.context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.context.pop()

    def test_extension_init(self):
        self.assertIn('dropzone', current_app.extensions)

    def test_load(self):
        rv = self.dropzone.load()
        self.assertIn('https://cdn.jsdelivr.net/npm/dropzone@', rv)
        self.assertIn('dropzone.min.js', rv)
        self.assertIn('dropzone.min.css', rv)
        self.assertIn('Dropzone.options.myDropzone', rv)

    def test_load_css(self):
        rv = self.dropzone.load_css()
        self.assertIn('dropzone.min.css', rv)
        self.assertIn('latest', rv)

        rv = self.dropzone.load_css(version='5.1.0')
        self.assertIn('dropzone.min.css', rv)
        self.assertIn('5.1.0', rv)

    def test_load_js(self):
        rv = self.dropzone.load_js()
        self.assertIn('dropzone.min.js', rv)
        self.assertIn('latest', rv)

        rv = self.dropzone.load_js(version='5.1.0')
        self.assertIn('dropzone.min.js', rv)
        self.assertIn('5.1.0', rv)

    def test_local_resources(self):
        current_app.config['DROPZONE_SERVE_LOCAL'] = True

        css_response = self.client.get('/dropzone/static/dropzone.min.css')
        js_response = self.client.get('/dropzone/static/dropzone.min.js')
        self.assertNotEqual(css_response.status_code, 404)
        self.assertNotEqual(js_response.status_code, 404)

        css_rv = self.dropzone.load_css()
        js_rv = self.dropzone.load_js()
        self.assertIn('/dropzone/static/dropzone.min.css', css_rv)
        self.assertIn('/dropzone/static/dropzone.min.js', js_rv)
        self.assertNotIn('https://cdn.jsdelivr.net/npm/dropzone@', css_rv)
        self.assertNotIn('https://cdn.jsdelivr.net/npm/dropzone@', js_rv)

    def test_config_dropzone(self):
        current_app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image'
        current_app.config['DROPZONE_MAX_FILE_SIZE'] = 5
        current_app.config['DROPZONE_MAX_FILES'] = 40
        current_app.config['DROPZONE_INPUT_NAME'] = 'test'
        current_app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image'
        current_app.config['DROPZONE_DEFAULT_MESSAGE'] = 'Drop file here'
        current_app.config['DROPZONE_REDIRECT_VIEW'] = 'index'
        current_app.config['DROPZONE_TIMEOUT'] = 10000

        rv = self.dropzone.config()
        self.assertIn('Dropzone.options.myDropzone', rv)
        self.assertIn('paramName: "test"', rv)
        self.assertIn('maxFilesize: 5', rv)
        self.assertIn('maxFiles: 40,', rv)
        self.assertIn('acceptedFiles: "%s"' % allowed_file_extensions['image'], rv)
        self.assertIn('dictDefaultMessage: `Drop file here`', rv)
        self.assertIn('this.on("queuecomplete", function(file) {', rv)
        self.assertIn('window.location = "/";', rv)
        self.assertIn('timeout: 10000,', rv)

        rv = self.dropzone.config(redirect_url='/redirect')
        self.assertIn('this.on("queuecomplete", function(file) {', rv)
        self.assertIn('window.location = "/redirect";', rv)

        current_app.config['DROPZONE_TIMEOUT'] = None
        rv = self.dropzone.config()
        self.assertNotIn('timeout:', rv)

    def test_config_overwrite(self):
        rv = self.dropzone.config(input_name='test', max_file_size=12, max_files=60, allowed_file_type='image',
                                  default_message='Drop file here', redirect_view='index', timeout=10000)
        self.assertIn('Dropzone.options.myDropzone', rv)
        self.assertIn('paramName: "test"', rv)
        self.assertIn('maxFilesize: 12', rv)
        self.assertIn('maxFiles: 60,', rv)
        self.assertIn('acceptedFiles: "%s"' % allowed_file_extensions['image'], rv)
        self.assertIn('dictDefaultMessage: `Drop file here`', rv)
        self.assertIn('this.on("queuecomplete", function(file) {', rv)
        self.assertIn('window.location = "/";', rv)
        self.assertIn('timeout: 10000,', rv)

    def test_create_dropzone(self):
        rv = self.dropzone.create(action=url_for('upload'))
        self.assertIn('<form action="/upload" method="post" class="dropzone" id="myDropzone"', rv)

    def test_csrf_field(self):
        rv = self.dropzone.config()
        self.assertNotIn('X-CSRF-Token', rv)

        rv = self.dropzone.config(enable_csrf=True)
        self.assertIn('X-CSRF-Token', rv)

        current_app.config['DROPZONE_ENABLE_CSRF'] = True
        rv = self.dropzone.config()
        self.assertIn('X-CSRF-Token', rv)

    def test_style_dropzone(self):
        rv = self.dropzone.style('width: 500px')
        self.assertIn('.dropzone{width: 500px}', rv)

    def test_render_template(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('https://cdn.jsdelivr.net/npm/dropzone@', data)
        self.assertIn('dropzone.min.js', data)
        self.assertIn('dropzone.min.css', data)
        self.assertIn('Dropzone.options.myDropzone', data)
        self.assertIn('<form action="/upload" method="post" class="dropzone" id="myDropzone"', data)

        response = self.client.get('/load')
        data = response.get_data(as_text=True)
        self.assertIn('https://cdn.jsdelivr.net/npm/dropzone@', data)
        self.assertIn('dropzone.min.js', data)
        self.assertIn('dropzone.min.css', data)
        self.assertIn('Dropzone.options.myDropzone', data)
        self.assertIn('<form action="/upload" method="post" class="dropzone" id="myDropzone"', data)

    def test_get_url(self):
        url1 = get_url('upload')
        url2 = get_url('/upload')
        self.assertEqual(url1, url2)
        self.assertEqual(get_url(''), None)

    def test_click_upload(self):
        current_app.config['DROPZONE_UPLOAD_ON_CLICK'] = True

        rv = self.dropzone.config()
        self.assertIn('dz.processQueue();', rv)
        self.assertIn('autoProcessQueue: false,', rv)

    def test_in_form(self):
        current_app.config['DROPZONE_IN_FORM'] = True
        current_app.config['DROPZONE_UPLOAD_ON_CLICK'] = True
        current_app.config['DROPZONE_UPLOAD_BTN_ID'] = 'submit'
        rv = self.dropzone.create(action=url_for('upload'))
        self.assertEqual(rv, '<div class="dropzone" id="myDropzone"></div>')

        rv = self.dropzone.config()
        self.assertIn('dz.processQueue();', rv)
        self.assertIn('e.preventDefault();', rv)
        self.assertIn('autoProcessQueue: false,', rv)
        self.assertIn('document.getElementById("submit").click();', rv)

    def test_custom_js(self):
        rv = self.dropzone.config(custom_init='dz = this;')
        self.assertIn('dz = this;', rv)

        rv = self.dropzone.config(custom_init='dz = this')
        self.assertIn('dz = this;', rv)

        rv = self.dropzone.config(custom_options='foo = true,')
        self.assertIn('foo = true,', rv)

        rv = self.dropzone.config(custom_options='foo = true')
        self.assertIn('foo = true,', rv)

    def test_custom_id(self):
        rv = self.dropzone.create(action=url_for('upload'))
        self.assertIn('id="myDropzone"', rv)
        rv = self.dropzone.config()
        self.assertIn('Dropzone.options.myDropzone', rv)

        rv = self.dropzone.create(action=url_for('upload'), id='hello')
        self.assertIn('id="hello"', rv)
        rv = self.dropzone.config(id='hello')
        self.assertIn('Dropzone.options.hello', rv)
