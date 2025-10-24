
import pytest
from unittest.mock import patch, AsyncMock, Mock
import time
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter


# @pytest.fixture(scope="session")
# def multi_page_pdf(request, tmp_path_factory):
#     """
#     Fixture that creates a multi-page PDF file for testing.
#     """
#     print('params', request.param)
#     pdf_path = tmp_path_factory.mktemp("pdf_data") / request.param['pdf_file']
#     print(pdf_path)
#
#     c = canvas.Canvas(str(pdf_path), pagesize=letter)
#     for page in range(request.param['total_pages']):
#         c.drawString(100, 750, f"This is Page {page}")
#         c.showPage()
#
#     c.save()

#     yield pdf_path
@pytest.fixture(scope='session')
def mock_json_load():
    with patch('src.load_config.json.load') as mock_load:
        yield mock_load

@pytest.fixture(scope='session')
def mock_sleep():
    with patch('src.service.util_service.sleep') as mock_sleep:
        yield mock_sleep

@pytest.fixture(scope="function")
def create_named_test_file(request, tmp_path):
    """creates temp input files"""
    file = tmp_path / request.param['file_name']
    file_text = request.param.get('file_text', ' ')
    file.write_text(file_text)
    yield file
    file.unlink()

@pytest.fixture(scope="function")
def create_test_files(request, tmp_path):
    """creates temp input files"""
    files = []
    for prefix in request.param['file_prefixes']:
        filename = f'{prefix}_{time.time()}.txt'
        file = tmp_path / filename
        file.write_text(f'first line\nThis is some test for file {file}')
        files.append(file)
        time.sleep(.1)

    yield files
    for f in files:
        f.unlink()

@pytest.fixture(scope="function")
def create_general_test_file(tmp_path):
    """creates temp input files"""
    file = tmp_path / 'file.ext'
    yield file
    file.unlink()

@pytest.fixture(scope="function")
def mock_uc_start():
    with patch('src.service.nodriver_service.uc.start') as uc_mock:
        uc_mock.return_value.stop = Mock()
        uc_mock.return_value.close = AsyncMock()
        uc_mock.return_value.get = AsyncMock()
        uc_mock.return_value.get.return_value.xpath = AsyncMock()
        uc_mock.return_value.get.return_value.find = AsyncMock()
        page = AsyncMock()
        page.evaluate = AsyncMock()
        page.text = "Original Page"
        page.url = 'example.com'
        page.bring_to_front = AsyncMock()
        uc_mock.return_value.get.return_value = page
        uc_mock.return_value.tabs = [page]
        uc_mock.return_value.get_targets.return_value = [page]

        yield uc_mock

@pytest.fixture(scope='function')
def mock_element():
    element = AsyncMock()
    element.attrs.get = Mock()
    element.click = AsyncMock()
    element.clear_input = AsyncMock()
    element.send_keys = AsyncMock()

    yield element

html_fields = {
    'input_fields':"""
        <h2>Field 1: Username</h2> <div> <input id="username" type="text" placeholder="Your Username"> </div> <div class="spacer"></div> <h2>Field 2: Email</h2> <div> <input id="email" type="text" placeholder="email@"> </div> 
        """
}
xpaths = {
    'uname_input': "//input[@id='username']",
    'email_input': "//input[@id='email']"
}
selectors = {
    'uname_input': "#username",
    'email_input': "#email"
}
@pytest.fixture(scope="function")
def get_test_html(request):
    html_field = request.param['html_field']
    test_html = f""" 
        <!DOCTYPE html> 
        <html lang="en"> 
        <head> 
            <meta charset="UTF-8"> 
            <meta name="viewport" content="width=device-width, initial-scale=1.0"> 
            <title>Test Page</title> 
            <style> 
                body {{ font-family: sans-serif; padding: 20px; }}
                div {{ margin-bottom: 20px; }} 
                input {{ font-size: 1.2em; padding: 5px; }} 
                .spacer {{ height: 1000px; }} /* Ensures scrolling is necessary */ 
            </style> 
        </head> 
        <body> 
            {html_field}
        </body> 
        </html> 
    """

    yield test_html
