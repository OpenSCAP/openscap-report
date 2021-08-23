
class ReportGenerator():
    def __init__(self, data):
        self.data = data

    def generate_html_report(self):
        return "<html><h1>TEST REPORT</h1><h2>{}</h2></html>\n".format(self.data)
