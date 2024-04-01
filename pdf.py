import pdfkit
from jinja2 import Environment, FileSystemLoader
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


class PDFGenerator:
    def __init__(self):
        with open('finall_report.txt', 'r') as file:
            self.report = file.readlines()

                
        self.env = Environment(loader=FileSystemLoader('.'))
        self.template = self.env.get_template('template.html')

    def get_main_part(self):
        pages = []
        for lines in range(2, len(self.report), 13):
            lines_info = self.report[lines].split(',')
            severity = lines_info[0]
            component = lines_info[1]
            start_line = lines_info[2]
            end_line = lines_info[3]

            start_line_code = start_line.replace('Start Line: ', '')
            end_line_code = end_line.replace('End Line: ', '')
            

            line_numbers = list(range(int(start_line_code)-4, int(end_line_code) + 6))

            code_lines = self.report[lines+2:lines+12]

            numbered_code = []
            for num, code_line in zip(line_numbers, code_lines):
                numbered_code.append(f'{num:4d} {code_line}')
            
            code_block_string = "\n".join(numbered_code)

            formatted_code = highlight(code_block_string, PythonLexer(), HtmlFormatter(full=True))

            if lines+12 <= len(self.report):
                line = self.report[lines+12][2::]
                if 'VULNERABILITY' in line:
                    color = 'red'
                elif 'BUG' in line:
                    color = 'blue'
                else:
                    color = 'black'

                pages.append({
                    'severity': severity,
                    'component': component,
                    'start_line': start_line,
                    'end_line': end_line,
                    'line': line,
                    'code_block': formatted_code,
                    'color': color,
                })
        
        return pages

    def generate_report(self):
        html = self.template.render(title=self.report[0], 
                                    issue_count=self.report[1][:-1], 
                                    pages=self.get_main_part())
        pdfkit.from_string(html, f'SonarQube_report_{self.report[0]}.pdf')