import itertools

# Evaluate logical expression
def evaluate_expression(expr, values):

    # Replace logical symbols with Python operators
    expr = expr.replace('¬', ' not ')
    expr = expr.replace('∧', ' and ')
    expr = expr.replace('∨', ' or ')

    # Replace implication (P → Q) with (not P or Q)
    expr = expr.replace('→', ' <= ')

    # Replace biconditional
    expr = expr.replace('↔', ' == ')

    # Replace variables with True/False
    for var, val in values.items():
        expr = expr.replace(var, str(val))

    return eval(expr)


# Generate truth table
def truth_table(variables, expression):

    rows = list(itertools.product([True, False], repeat=len(variables)))

    print("\nTruth Table:\n")

    header = variables + [expression]
    print("\t".join(header))

    results = []

    for row in rows:
        values = dict(zip(variables, row))
        result = evaluate_expression(expression, values)
        results.append(result)

        row_values = [str(v) for v in row]
        print("\t".join(row_values + [str(result)]))

    return results


# Example
variables = ['P', 'Q']
expression = "P → Q"

results = truth_table(variables, expression)

if all(results):
    print("\nThe statement is VALID (Tautology)")
else:
    print("\nThe statement is NOT always true")