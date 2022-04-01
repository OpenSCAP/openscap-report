import base64
import re
from io import BytesIO
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

try:
    from jinja2 import pass_context
except ImportError:
    from jinja2 import contextfunction as pass_context

from markupsafe import Markup


class ReportGenerator():
    def __init__(self, parser):
        self.report = parser.parse_report()
        self.file_loader = FileSystemLoader(str(Path(__file__).parent / "templates"))
        self.env = Environment(loader=self.file_loader)
        self.env.globals['include_file_in_base64'] = self.include_file_in_base64
        self.env.filters['set_css_for_list'] = self.set_css_for_list
        self.env.trim_blocks = True
        self.env.lstrip_blocks = True

    def generate_html_report(self, debug_setting):
        template = self.env.get_template("template_report.html")
        html_report = template.render(report=self.report, debug_setting=debug_setting)
        if not debug_setting.no_minify:
            return BytesIO(html_report.encode())
        minified_html_report = re.sub(r'>\s+<', '><', html_report)
        return BytesIO(minified_html_report.encode())

    @staticmethod
    @pass_context
    def include_file_in_base64(context, relative_path):
        real_path = Path(context.environment.loader.searchpath[0]) / relative_path
        base64_data = None
        with open(real_path, "rb") as file_data:
            base64_data = (base64.b64encode(file_data.read())).decode('utf-8')
        return Markup(base64_data)

    @staticmethod
    def set_css_for_list(data):
        out = data.replace("<ul>", "<ul class=\"pf-c-list\">")
        out = out.replace("<ol>", "<ol class=\"pf-c-list\">")
        return out
