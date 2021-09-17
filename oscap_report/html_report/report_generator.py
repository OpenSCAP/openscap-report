import re
from io import BytesIO
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


class ReportGenerator():
    def __init__(self, parser):
        self.report = parser.parse_report()
        self.file_loader = FileSystemLoader(str(Path(__file__).parent / "templates"))
        self.env = Environment(loader=self.file_loader)
        self.env.trim_blocks = True
        self.env.lstrip_blocks = True

    def generate_html_report(self):
        template = self.env.get_template("template_report.html")
        html_report = template.render(report=self.report)
        minified_html_report = re.sub(r'>\s+<', '><', html_report)
        return BytesIO(minified_html_report.encode())
