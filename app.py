import html
import itertools
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

HOST = 'localhost'
PORT = 8000


def evaluate_expression(expr, values):
    expr = expr.replace('<->', ' == ')
    expr = expr.replace('->', ' <= ')
    expr = expr.replace('^', ' and ')
    expr = expr.replace('|', ' or ')
    expr = expr.replace('!', ' not ')

    for var, value in values.items():
        expr = re.sub(rf'\b{re.escape(var)}\b', str(value), expr)

    try:
        return eval(expr, {'__builtins__': None}, {'True': True, 'False': False})
    except Exception:
        return 'Error'


def truth_table(variables, expression):
    rows = []
    for row in itertools.product([True, False], repeat=len(variables)):
        values = dict(zip(variables, row))
        result = evaluate_expression(expression, values)
        rows.append({'values': values, 'result': result})
    return rows


def classify_results(rows):
    results = [row['result'] for row in rows]
    if not results:
        return {'type': '', 'text': ''}
    if all(result is True for result in results):
        return {'type': 'tautology', 'text': 'Tautology (Always True)'}
    if all(result is False for result in results):
        return {'type': 'contradiction', 'text': 'Contradiction (Always False)'}
    return {'type': 'contingency', 'text': 'Contingency (Sometimes True, Sometimes False)'}


def build_html_page(variables='', expression='', rows=None, classification=None):
    variables_escaped = html.escape(variables)
    expression_escaped = html.escape(expression)
    table_html = ''

    if rows is not None and rows:
        headers = ''.join(f'<th>{html.escape(name)}</th>' for name in rows[0]['values'].keys())
        headers += '<th>Result</th>'
        body = ''
        for row in rows:
            values_html = ''.join(f'<td>{html.escape(str(value))}</td>' for value in row['values'].values())
            body += f'<tr>{values_html}<td>{html.escape(str(row['result']))}</td></tr>'
        table_html = f'<h2>Truth Table</h2><table>{headers}{body}</table>'

    classification_html = ''
    if classification and classification['text']:
        classification_html = f'<p class="classification {classification["type"]}">{html.escape(classification["text"])}</p>'

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Logical Expression Web App</title>
  <style>
    body {{
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      margin: 0;
      padding: 2rem;
      line-height: 1.6;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      color: #333;
    }}
    .container {{
      max-width: 800px;
      margin: 0 auto;
      background: white;
      padding: 2rem;
      border-radius: 10px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }}
    h1 {{
      text-align: center;
      color: #4a5568;
      margin-bottom: 2rem;
      font-size: 2.5rem;
      text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }}
    h2 {{
      color: #2d3748;
      margin-top: 2rem;
      font-size: 1.8rem;
    }}
    form {{
      margin-bottom: 2rem;
    }}
    label {{
      display: block;
      margin-bottom: 0.5rem;
      font-weight: 600;
      color: #4a5568;
    }}
    input, textarea {{
      width: 100%;
      max-width: 100%;
      padding: 0.75rem;
      margin: 0.4rem 0 1rem 0;
      font-size: 1rem;
      border: 2px solid #e2e8f0;
      border-radius: 8px;
      transition: border-color 0.3s ease;
      box-sizing: border-box;
    }}
    input:focus, textarea:focus {{
      outline: none;
      border-color: #667eea;
      box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }}
    button {{
      padding: 0.75rem 1.5rem;
      border: none;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      border-radius: 8px;
      transition: all 0.3s ease;
      box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }}
    button:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }}
    table {{
      border-collapse: collapse;
      margin-top: 1rem;
      width: 100%;
      max-width: 100%;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    th, td {{
      border: 1px solid #e2e8f0;
      padding: 0.75rem;
      text-align: center;
    }}
    th {{
      background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
      color: white;
      font-weight: 600;
    }}
    tr:nth-child(even) {{
      background: #f7fafc;
    }}
    tr:hover {{
      background: #edf2f7;
    }}
    .classification {{
      font-weight: bold;
      margin-top: 1.5rem;
      padding: 1rem;
      border-radius: 8px;
      text-align: center;
      font-size: 1.2rem;
    }}
    .classification.tautology {{
      background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
      color: white;
    }}
    .classification.contradiction {{
      background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
      color: white;
    }}
    .classification.contingency {{
      background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
      color: white;
    }}
    .note {{
      margin-top: 2rem;
      padding: 1rem;
      background: #f7fafc;
      border-left: 4px solid #667eea;
      border-radius: 4px;
      color: #4a5568;
      max-width: 100%;
    }}
    .note strong {{
      color: #2d3748;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Logical Expression Web App</h1>
    <form method="get">
      <label>Variables (comma separated, e.g. p, q, r):</label>
      <input name="variables" value="{variables_escaped}" placeholder="p, q, r" required>
      <label>Expression:</label>
      <textarea name="expression" rows="3" placeholder="p ^ q -> r" required>{expression_escaped}</textarea>
      <button type="submit">Evaluate</button>
    </form>
    {classification_html}
    {table_html}
    <div class="note">
      Use operators: <strong>^</strong> for AND, <strong>|</strong> for OR, <strong>!</strong> for NOT, <strong>-></strong> for IMPLIES, <strong><-></strong> for BICONDITIONAL.
    </div>
  </div>
</body>
</html>'''


class LogicalEngineHandler(BaseHTTPRequestHandler):
    def parse_parameters(self):
        if self.command == 'POST':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            return parse_qs(body)
        parsed_url = urlparse(self.path)
        return parse_qs(parsed_url.query)

    def do_GET(self):
        params = self.parse_parameters()
        variables = params.get('variables', [''])[0].strip()
        expression = params.get('expression', [''])[0].strip()
        rows = None
        classification = None

        if variables and expression:
            variable_names = [v.strip() for v in variables.split(',') if v.strip()]
            if variable_names:
                rows = truth_table(variable_names, expression)
                classification = classify_results(rows)

        html_content = build_html_page(variables, expression, rows, classification).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html_content)))
        self.end_headers()
        self.wfile.write(html_content)

    def do_POST(self):
        self.do_GET()

    def log_message(self, format, *args):
        return


if __name__ == '__main__':
    server = HTTPServer((HOST, PORT), LogicalEngineHandler)
    print(f'Serving web app at http://{HOST}:{PORT}/')
    server.serve_forever()
