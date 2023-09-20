import pytest

from astro_pi_executor.sense_hat.graph import (
    DiGraph,
    GroupedEdges,
    SenseHatGraph,
    resolve_derivation,
)

cg: DiGraph = SenseHatGraph.colour_graph

first_degree_test_data = [
    (set(["colour"]), "colour_raw"),
    (set(["colour_raw"]), "colour"),
    (set(["colour_raw"]), "rgb"),
    (set(["red"]), "red_raw"),
    (set(["red_raw"]), "red"),
    (set(["green"]), "green_raw"),
    (set(["green_raw"]), "green"),
    (set(["blue"]), "blue_raw"),
    (set(["blue_raw"]), "blue"),
    (set(["clear"]), "clear_raw"),
    (set(["clear_raw"]), "clear"),
    (set(["clear_raw"]), "brightness"),
    (set(["brightness"]), "clear_raw"),
]


@pytest.mark.parametrize("resolved_columns,to_derive", first_degree_test_data)
def test_first_degree_derivations(resolved_columns: set[str], to_derive: str):
    solutions: list[list[GroupedEdges]] = resolve_derivation(
        cg, resolved_columns, to_derive
    )
    assert len(solutions) == 1
    solution: list[GroupedEdges] = solutions[0]
    assert len(solution) == 1
    # Edge (A,B) means A derives B or equivalently B is derivable from A
    assert solution[0] == ((list(resolved_columns)[0], to_derive),)


second_degree_test_data = [
    (set(["colour"]), "rgb"),
]


@pytest.mark.parametrize("resolved_columns,to_derive", second_degree_test_data)
def test_second_degree_derivations(resolved_columns: set[str], to_derive: str):
    solutions: list[list[GroupedEdges]] = resolve_derivation(
        cg, resolved_columns, to_derive
    )
    assert len(solutions) == 1
    solution: list[GroupedEdges] = solutions[0]
    assert len(solution) == 2  # 2nd order
    print(solution)
    assert solution == [(("colour_raw", "rgb"),), (("colour", "colour_raw"),)]


@pytest.mark.parametrize(
    "resolved_columns,to_derive",
    [(set(["red_raw", "green_raw", "blue_raw", "clear_raw"]), "colour_raw")],
)
def test_first_degree_derivations_with_group(
    resolved_columns: set[str], to_derive: str
):
    solutions: list[list[GroupedEdges]] = resolve_derivation(
        cg, resolved_columns, to_derive
    )
    assert len(solutions) == 1
    solution: list[GroupedEdges] = solutions[0]
    assert len(solution) == 1
    assert len(solution[0]) == len(list(resolved_columns))
    assert sorted(solution[0]) == sorted(
        [
            ("red_raw", "colour_raw"),
            ("green_raw", "colour_raw"),
            ("blue_raw", "colour_raw"),
            ("clear_raw", "colour_raw"),
        ]
    )


@pytest.mark.parametrize(
    "resolved_columns,to_derive",
    [(set(["red_raw", "green_raw", "blue_raw", "clear_raw"]), "colour")],
)
def test_second_degree_derivations_with_group(
    resolved_columns: set[str], to_derive: str
):
    solutions: list[list[GroupedEdges]] = resolve_derivation(
        cg, resolved_columns, to_derive
    )
    assert len(solutions) == 1
    solution: list[GroupedEdges] = solutions[0]
    assert len(solution) == 2  # 2nd degree
    assert solution[0] == (("colour_raw", "colour"),)
    assert sorted(solution[1]) == sorted(
        [
            ("red_raw", "colour_raw"),
            ("green_raw", "colour_raw"),
            ("blue_raw", "colour_raw"),
            ("clear_raw", "colour_raw"),
        ]
    )


# FIXME
@pytest.mark.parametrize(
    "resolved_columns, to_derive",
    [(set(["red_raw", "green_raw", "blue_raw"]), "colour")],
)
def test_column_not_derivable(resolved_columns: set[str], to_derive: str):
    solutions: list[list[GroupedEdges]] = resolve_derivation(
        cg, resolved_columns, to_derive
    )
    assert len(solutions) == 0


# TODO test a long-winded example
