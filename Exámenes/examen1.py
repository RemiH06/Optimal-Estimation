import pulp


def build_model(corte=230, laminacion=190, materia_prima=340):
    A = pulp.LpVariable("A", lowBound=0)
    B = pulp.LpVariable("B", lowBound=0)
    C = pulp.LpVariable("C", lowBound=0)
    model = pulp.LpProblem("produccion", pulp.LpMaximize)
    model += 50 * A + 40 * B + 70 * C
    model += 2 * A + B + 3 * C <= corte, "corte"
    model += A + 2 * B + 2 * C <= laminacion, "laminacion"
    model += 3 * A + 2 * B + 4 * C <= materia_prima, "materia_prima"
    model += A + B + C >= 80, "produccion_minima"
    model += B >= 0.4 * (A + B + C), "reforzado_minimo"
    model += C <= 40, "premium_maximo"
    return model, (A, B, C)


def solve(**rhs):
    model, (A, B, C) = build_model(**rhs)
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    return {"A": A.value(), "B": B.value(), "C": C.value(), "profit": pulp.value(model.objective)}


def constraints_table(sol, corte=230, laminacion=190, materia_prima=340):
    A, B, C = sol["A"], sol["B"], sol["C"]
    T = A + B + C
    rows = [
        ("corte", 2 * A + B + 3 * C, corte, "<="),
        ("laminacion", A + 2 * B + 2 * C, laminacion, "<="),
        ("materia_prima", 3 * A + 2 * B + 4 * C, materia_prima, "<="),
        ("produccion_minima", T, 80, ">="),
        ("reforzado_minimo", B, 0.4 * T, ">="),
        ("premium_maximo", C, 40, "<="),
    ]
    return [
        (name, lhs, rhs, (rhs - lhs) if op == "<=" else (lhs - rhs))
        for name, lhs, rhs, op in rows
    ]


def print_table(rows):
    print(f"{'restriccion':18}{'lhs':>10}{'limite':>10}{'holgura':>10}  vinculante")
    for name, lhs, rhs, slack in rows:
        print(f"{name:18}{lhs:>10.2f}{rhs:>10.2f}{slack:>10.2f}  {abs(slack) < 1e-6}")


if __name__ == "__main__":
    base = solve()
    print(base)
    print_table(constraints_table(base))

    print()
    escenario = solve(laminacion=180)
    print(escenario)
    print_table(constraints_table(escenario, laminacion=180))
