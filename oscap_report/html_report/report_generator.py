from pathlib import Path

from jinja2 import Environment, FileSystemLoader


class ReportGenerator():
    def __init__(self, parser):
        self.report = parser.parse_report()
        self.file_loader = FileSystemLoader(str(Path(__file__).parent / "templates"))
        self.env = Environment(loader=self.file_loader)

    def generate_html_report(self):
        template = self.env.get_template("template_report.html")
        return template.render(report=self.report)
