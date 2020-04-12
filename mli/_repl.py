import re


def _readline(prompt='>> ', cont='... '):
    expression = input(prompt)
    while expression.endswith(('...', '\\')):
        expression = expression.rstrip('\\')
        expression += '\n' + input(cont)
    return expression


def repl(source):
    background = False
    expression = None
    while True:
        if expression:
            if re.match(r'^\s*(exit|quit)\s*(\(\))?\s*$', expression):
                break
            match = re.match(r'^\s*-async\s*(.*)', expression)
            if match:
                background = True
                expression = match.group(1)
            print(source(expression, background))

        background = False
        expression = _readline()
