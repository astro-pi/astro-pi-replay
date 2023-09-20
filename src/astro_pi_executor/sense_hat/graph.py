import functools
import logging
import typing
from collections import defaultdict, deque
from copy import deepcopy
from typing import Callable, TypeAlias, Union

import networkx as nx

from astro_pi_executor.custom_types import RGB, RGBC

logger = logging.getLogger(__name__)


Node: TypeAlias = str
Edge: TypeAlias = tuple[Node, Node]
GroupedEdges: TypeAlias = tuple[Edge, ...]
GroupId: TypeAlias = int


class Converter(dict):
    def __init__(self, name: str, _: Callable):
        # Makes this class json serializable for visualisation
        dict.__init__(self, name=name)
        # self.func = func


class DiGraph(nx.DiGraph):
    def __init__(self) -> None:
        super().__init__(self)
        self.counter = 0
        self.node_to_group_id_map: dict[str, int] = {}
        self.group_id_to_nodes_map: dict[int, set[str]] = defaultdict(set)
        self.group_id_to_edges_map: dict[int, set[Edge]] = defaultdict(set)

    def derives(
        self, original: Union[Node, list[Node]], derivable: Node, converter: Converter
    ) -> None:
        """
        Declare that original 'derives' derivable with the given converter,
        effectively creating a dependency graph.
        """
        group_id: int = self.counter
        self.counter += 1
        original_as_list: list[Node] = (
            [original] if isinstance(original, Node) else original
        )
        for orig in original_as_list:
            self.node_to_group_id_map[orig] = group_id
            nodes: set[str] = self.group_id_to_nodes_map[group_id]
            nodes.add(orig)  # mutates the set inplace
            edges: set[tuple[str, str]] = self.group_id_to_edges_map[group_id]
            edges.add((orig, derivable))  # mutates the set inplace
            self.add_edge(
                orig,
                derivable,
                group_id=group_id,
                label=str(group_id),
                converter=converter,
            )

    def _visualise(self) -> None:
        # pip install pyvis
        from pyvis.network import Network

        g = Network(width="800", height="800", notebook=False, directed=True)
        # g.toggle_hide_edges_on_drag(False)
        # g.barnes_hut()
        g.from_nx(self)
        g.show("ex.html", notebook=False)

    def get_in_edges(self, node: Node) -> list[Edge]:
        return typing.cast(list, self.in_edges(node))

    def edge_groups(self, node: Node) -> list[GroupedEdges]:
        grouped_edges: set[GroupedEdges] = set()
        edges: tuple[Edge] = typing.cast(tuple[Edge], self.in_edges(node))
        for edge in edges:
            attributes: dict = self.edges[edge]
            group_id: int = attributes["group_id"]
            group_edges: set[Edge] = self.group_id_to_edges_map[group_id]
            grouped_edges.add(tuple(group_edges))
        return list(grouped_edges)


class Converters:
    @staticmethod
    def _not_implemented() -> None:
        raise NotImplementedError()

    @staticmethod
    def _collect_rollpitchyaw_dict(
        roll: float, pitch: float, yaw: float
    ) -> dict[str, float]:
        return {
            "roll": roll,  # TODO define these strings once!
            "pitch": pitch,
            "yaw": yaw,
        }

    @staticmethod
    def _collect_xyz_dict(x: float, y: float, z: float) -> dict[str, float]:
        return {"x": x, "y": y, "z": z}  # TODO define these strings once!

    @staticmethod
    def _collect_rgbc_tuple(r: int, g: int, b: int, c: int) -> RGBC:
        return (r, g, b, c)

    @staticmethod
    def _collect_rgb_tuple(r: int, g: int, b: int) -> RGB:
        return (r, g, b)

    @staticmethod
    def _normalized_rgbc_to_raw(value: int) -> int:
        """Scales from a normalised value to an
        approximate raw value by reversing the
        steps in the original SenseHat module"""
        max_raw = 1024
        return value * (max_raw // 256)

    @staticmethod
    def _normalize_raw_rgbc(value: int) -> int:
        raise NotImplementedError()  # TODO

    not_implemented = Converter("not_implemented", _not_implemented)
    copy_value = Converter("copy_value", lambda x: x)
    collect_rollpitchyaw_dict = Converter(
        "collect_rollpitchyaw_dict", _collect_rollpitchyaw_dict
    )
    collect_xyz_dict = Converter("collect_xyz_dict", _collect_xyz_dict)
    collect_rgbc_tuple = Converter("collect_rgbc_tuple", _collect_rgbc_tuple)
    collect_rgb_tuple = Converter("collect_rgb_tuple", _collect_rgb_tuple)
    normalize_raw_rgbc = Converter("normalize_raw_rgbc", _normalize_raw_rgbc)
    normalized_rgbc_to_raw = Converter("normalized_rgbc_to_raw", _normalize_raw_rgbc)


class SenseHatGraph:
    """
    In these graphs, nodes are sense_hat attribute names
    and edges define a dependency between them.
    For example, one can derive "accel" data using
    "accel_raw" data, so there will be an edge.
    Orientation may be derived from either gyro or accel or
    magnetometer (or their combination!)
    """

    @staticmethod
    def _init_colour_graph() -> DiGraph:
        colour_graph: DiGraph = DiGraph()
        colour_graph.add_nodes_from(
            [
                "blue",
                "blue_raw",
                "brightness",
                "clear",
                "clear_raw",
                "colour",
                "colour_raw",
                "green",
                "green_raw",
                "red",
                "red_raw",
                "rgb",
            ]
        )

        colour_graph.derives(
            original="red",
            derivable="red_raw",
            converter=Converters.normalized_rgbc_to_raw,
        )
        colour_graph.derives(
            original="red_raw", derivable="red", converter=Converters.normalize_raw_rgbc
        )
        colour_graph.derives(
            original="green",
            derivable="green_raw",
            converter=Converters.normalized_rgbc_to_raw,
        )
        colour_graph.derives(
            original="green_raw",
            derivable="green",
            converter=Converters.normalize_raw_rgbc,
        )
        colour_graph.derives(
            original="blue",
            derivable="blue_raw",
            converter=Converters.normalized_rgbc_to_raw,
        )
        colour_graph.derives(
            original="blue_raw",
            derivable="blue",
            converter=Converters.normalize_raw_rgbc,
        )
        colour_graph.derives(
            original="clear",
            derivable="clear_raw",
            converter=Converters.normalized_rgbc_to_raw,
        )
        colour_graph.derives(
            original="clear_raw",
            derivable="clear",
            converter=Converters.normalize_raw_rgbc,
        )
        colour_graph.derives(
            original="clear_raw",
            derivable="brightness",
            converter=Converters.copy_value,
        )
        colour_graph.derives(
            original="brightness",
            derivable="clear_raw",
            converter=Converters.copy_value,
        )
        colour_graph.derives(
            original="colour",
            derivable="colour_raw",
            converter=Converter(
                "mapped_normalized_rgbc_to_raw",
                lambda x: tuple(map(Converters._normalized_rgbc_to_raw, x)),
            ),
        )

        colour_graph.derives(
            original="colour",
            derivable="red",
            converter=Converter("first", lambda x: x[0]),
        )
        colour_graph.derives(
            original="colour",
            derivable="green",
            converter=Converter("second", lambda x: x[1]),
        )
        colour_graph.derives(
            original="colour",
            derivable="blue",
            converter=Converter("third", lambda x: x[2]),
        )
        colour_graph.derives(
            original="colour",
            derivable="clear",
            converter=Converter("fourth", lambda x: x[3]),
        )
        colour_graph.derives(
            original="colour_raw",
            derivable="colour",
            converter=Converter(
                "mapped_normalize_raw_rgbc",
                lambda x: tuple(map(Converters._normalize_raw_rgbc, x)),
            ),
        )
        colour_graph.derives(
            original="colour_raw",
            derivable="red_raw",
            converter=Converter("first", lambda x: x[0]),
        )
        colour_graph.derives(
            original="colour_raw",
            derivable="green_raw",
            converter=Converter("second", lambda x: x[1]),
        )
        colour_graph.derives(
            original="colour_raw",
            derivable="blue_raw",
            converter=Converter("third", lambda x: x[2]),
        )
        colour_graph.derives(
            original="colour_raw",
            derivable="clear_raw",
            converter=Converter("fourth", lambda x: x[3]),
        )
        colour_graph.derives(
            original="colour_raw",
            derivable="rgb",
            converter=Converter("first three elements", lambda x: x[:3]),
        )
        colour_graph.derives(
            original=["red", "green", "blue", "clear"],
            derivable="colour",
            converter=Converters.collect_rgbc_tuple,
        )
        colour_graph.derives(
            original=["red_raw", "green_raw", "blue_raw", "clear_raw"],
            derivable="colour_raw",
            converter=Converters.collect_rgbc_tuple,
        )
        return colour_graph

    # @staticmethod
    # def _init_sh_graph() -> DiGraph:
    #     sh_graph: DiGraph = DiGraph()

    #     sh_graph.add_nodes_from([
    #         "acc_x", "acc_y", "acc_z", "accel", "accel_raw",
    #         "compass", "compass_raw", "gyro_x", "gyro_y", "gyro_z",
    #         "gyro", "gyro_raw", "gyroscope", "gyroscope_raw",
    #         "humidity", "mag_x", "mag_y", "mag_z",
    #         "orientation", "orientation_roll", "orientation_pitch",
    #         "orientation_yaw", "orientation_radians", "pressure",
    #         "temp", "temperature"])

    #     sh_graph.derives(original="accel_raw",
    #                          derivable=["acc_x", "acc_y", "acc_z"],
    #                          converter=Converters.collect_xyz_dict)
    #     # sh_graph.derive(to="accel",
    #     #                      original="accel_raw",
    #     #                      converter=Converters.not_implemented)
    #     sh_graph.derives(original="accel",
    #                          derivable="orientation",
    #                          converter=Converters.copy_value)
    #     # TODO check if the below is correct
    #     sh_graph.derives(original="compass",
    #                          derivable="orientation_yaw",
    #                          converter=Converters.copy_value)
    #     sh_graph.derives(original="compass_raw",
    #                          derivable=["mag_x", "mag_y", "mag_z"],
    #                          converter=Converters.collect_xyz_dict)
    #     sh_graph.derives(original="gyro_raw",
    #                          derivable=["gyro_x", "gyro_y", "gyro_z"],
    #                          converter=Converters.collect_xyz_dict)
    #     # sh_graph.derive(to="gyro",
    #     #                      original="gyro_raw",
    #     #                      converter=Converters.not_implemented)
    #     sh_graph.derives(original="gyro",
    #                          derivable="orientation",
    #                          converter=Converters.copy_value)
    #     # sh_graph.derive(to="humidity",
    #     #                      original="temperature",
    #     #                      converter=Converters.not_implemented)
    #     sh_graph.derives(original="orientation",
    #                          derivable=["orientation_roll", "orientation_pitch",
    #                                    "orientation_yaw"],
    #                          converter=Converters.collect_rollpitchyaw_dict)
    #     sh_graph.derives(original="orientation",
    #                          derivable="orientation_radians",
    #                          # take from sense_hat.py#orientation(self)
    #                          converter=Converters.not_implemented)
    #     sh_graph.derives(original="orientation",
    #                          derivable=["accel_raw", "compass_raw"],
    #                          # take from sense_hat.py#orientation_radians(self)
    #                          converter=Converters.not_implemented)
    #     # should be able to derive orientation from a copy of accel or compass as well
    #     sh_graph.derives(original="orientation",
    #                          derivable="accel_raw",
    #                          converter=Converters.not_implemented)
    #     sh_graph.derives(original="orientation",
    #                          derivable="compass_raw",
    #                          converter=Converters.not_implemented)
    #     # sh_graph.derive(to="temp",
    #     #                      original="humidity",
    #     #                      converter=Converters.not_implemented)
    #     # sh_graph.derive(to="temp",
    #     #                      original="pressure",
    #     #                      converter=Converters.not_implemented)

    #     return sh_graph

    # sh_graph: DiGraph = _init_sh_graph()
    colour_graph: DiGraph = _init_colour_graph()


# Validating new datasets from GDrive entails:
# 1. normalizing the names of the data.csv file
# 2. ensuring that resolved columns in the data.csv -
#    i.e. set of nodes - can reach every other node
#    in the graph. If this is too restrictive, then a
#    threshold can be used instead.

# When trying to get a derivation of X using the graph
# the shortest path should be used to reduce the error
# (or, even better, a percentage error could be put into
# the graph).

# The challenge is how to represent the following:
# colour_raw is derivable from: red + green + blue + clear
# (+ has associativity and commutivity)
# colour_raw is derivable from: colour + None

# A node has an outgoing edge to represent "is derivable from".
# Need to distinguish between a collection of outgoing edges
# where ALL edges are mandatory for a derivation between a
# collection of outgoing edges where ANY edge may be used for a
# derivation.
# https://saturncloud.io/blog/algorithm-for-dependency-resolution-a-comprehensive-guide/#:~:text=The%20Dependency%20Resolution%20Algorithm&text=In%20this%20graph%2C%20each%20node,and%20understand%20the%20dependencies'%20structure.

# Current solution is to add a group_id attribute to each edge.
# The resolver looks at all the outgoing edges from the current
# node (to find dependencies) and then counts the number of
# elements per group, recursively.
#
# It will prune any groups whose elements are not all present, and
# then given a choice of groups, it will select ones with the cumulative
# lowest error (currently it's assumed that shortest path = lower error)


def resolve_derivation(
    graph: DiGraph, normalized_columns: set[str], column_to_derive: str
) -> list[list[GroupedEdges]]:
    """
    Returns the first ordered list of edges to follow to
    derive the column
    """
    logger.debug(
        f"Checking if {column_to_derive} can be " + f"derived from {normalized_columns}"
    )

    solutions: list[
        list[GroupedEdges]
    ] = []  # TODO is this is going to have to be a graph?
    seen_edges: set[Edge] = set()
    remaining_group_edges: dict[GroupId, set[Edge]] = deepcopy(
        graph.group_id_to_edges_map
    )
    # collection of edges to visit, along with their traversal path
    edges: list[tuple[Edge, list[GroupedEdges]]] = list(
        map(lambda x: (x, []), graph.get_in_edges(column_to_derive))
    )
    to_visit: deque[tuple[Edge, list[GroupedEdges]]] = deque(edges)

    while len(to_visit) > 0:
        edge: Edge
        path: list[GroupedEdges]
        edge, path = to_visit.popleft()
        logger.debug(f"Current edge: {edge}")
        # logger.debug(f"To visit queue: {to_visit}")
        derived_from: Node = edge[0]

        edge_attributes: dict = graph.edges[edge]
        group_id: GroupId = edge_attributes["group_id"]
        remaining_edges: set[Edge] = remaining_group_edges[group_id]

        # mark as seen
        seen_edges.add(edge)
        remaining_edges.remove(edge)

        # BASE CASE:
        # The column to derive is derivable
        # and the current group is complete.
        #
        # But should continue until every group in the path
        # is complete.
        derivable: bool = derived_from in normalized_columns
        logger.debug(f"{derived_from} is {'not ' if not derivable else ''}given")
        logger.debug(f"Remaining edges in group {group_id}: {remaining_edges}")
        if derivable and len(remaining_edges) == 0:
            logger.debug(f"Found solution for path {path}")

            for groupedge in path:
                remaining = graph.group_id_to_edges_map[
                    graph[groupedge[0]][groupedge[1]]["group_id"]
                ]
                logger.debug(remaining)
            # Need to mark this edge as derivable somehow
            # then check the path to ensure all group ids have been seen

            # check if there are other nodes in the group
            # TODO need to check that every node in the sequence is now
            # derivable or given
            solution_edges: GroupedEdges = tuple(graph.group_id_to_edges_map[group_id])
            logger.debug(f"Group: {solution_edges}")
            solutions.append(path + [solution_edges])
            break
        logger.debug("Recursive case: adding outer edges...")
        # RECURSIVE CASE:
        # Add the in edges of original to the list to visit, as well as
        # the current path.
        out_edges: list[Edge] = graph.get_in_edges(derived_from)
        new_path: list[GroupedEdges] = path + [(edge,)]
        for out_edge in out_edges:
            # TODO this currently fails when the new_path contains
            # an edge whose original is not derivable
            to_visit.append((out_edge, new_path))

    # https://wiki.python.org/moin/TimeComplexity
    return solutions


# def resolve_derivation2(graph: DiGraph,
#                       normalized_columns: set[str],
#                       column_to_derive: str) -> list[list[GroupedEdges]]:
#    """
#    Returns the first ordered list of edges to follow to
#    derive the column
#    """
#    logger.debug(f"Checking if {column_to_derive} can be " +
#                 f"derived from {normalized_columns}")
#
#    solutions: list[list[GroupedEdges]] = []
#    remaining_group_edges: dict[GroupId, set[Edge]] = deepcopy(
#        graph.group_id_to_edges_map)
#    # collection of GroupedEdges to visit, along with the traversal path
#    to_visit: deque[tuple[GroupedEdges,list[GroupedEdges]]] = deque(
#        list(map(lambda x: (x,[]),
#        graph.get_out_grouped_edges(column_to_derive))))
#
#    while len(to_visit) > 0:
#        grouped_edges: GroupedEdges
#        path: list[GroupedEdges]
#        grouped_edges, path = to_visit.popleft()
#        logger.debug(f"Current edge: {grouped_edges}")
#        logger.debug(f"To visit queue: {to_visit}")
#        for edge in grouped_edges:
#            logger.debug(f"Edge: {edge}")
#        derivable_from: Node = grouped_edges[1]
#
#        edge_attributes: dict = graph.edges[grouped_edges]
#        group_id: GroupId = edge_attributes["group_id"]
#        remaining_edges: set[Edge] = remaining_group_edges[group_id]
#
#        # mark as seen
#        seen_edges.add(grouped_edges)
#        remaining_edges.remove(grouped_edges)
#
#        # BASE CASE:
#        # The column to derive is derivable
#        # and the group is complete.
#        # (every column in the group id is derivable)
#        derivable: bool = derivable_from in normalized_columns
#        logger.debug(f"{derivable_from} is {'not ' if not derivable else ''}given")
#        logger.debug(f"Remaining edges in group {group_id}: {remaining_edges}")
#        if derivable and len(remaining_edges) == 0:
#            logger.debug(f"Found solution for path {path}")
#            # check if there are other nodes in the group
#            # TODO need to check that every node in the sequence is now
#            # derivable or given
#            solution_edges: GroupedEdges = list(graph.group_id_to_edges_map[group_id])
#            logger.debug(f"Group: {solution_edges}")
#            solutions.append(path + [solution_edges])
#            break
#        logger.debug(f"Recursive case: adding outer edges...")
#        # RECURSIVE CASE:
#        # Add the out edges of original to the list to visit, as well as
#        # the current path.
#        out_edges: list[Edge] = graph.get_out_edges(derivable_from)
#        new_path: list[GroupedEdges] = path + [[grouped_edges]]
#        for out_edge in out_edges:
#            # TODO this currently fails when the new_path contains
#            # an edge whose original is not derivable
#            to_visit.append((out_edge, new_path))
#
#    # https://wiki.python.org/moin/TimeComplexity
#    return solutions

# Another way of doing it would be to start with each individual
# resolved column and follow the "in_edges" to get the list of unique
# nodes derivable from there.
# But it would still be difficult to implement the "ALL" logic of the groups

# def resolve_derivation3(graph: DiGraph,
#                        normalized_columns: set[str],
#                        column_to_derive: str) -> list[list[GroupedEdges]]:
#    # Start with each normalized column and see if there is a path
#    # to column to derive
#    for normalized_col in normalized_columns:
#        simple_paths: list[str] = list(nx.all_simple_paths(graph,
#                                                           column_to_derive,
#                                                           normalized_col))
#


# A more formal version of my thinking:
#
# Given a Directed (Cyclic?) Graph
#
# Definitions:
# - An Edge Group, G, is a collection of related edges directed into a node N
# where every edge has the form "X derives N" (X,N), where
# X is some node. We write EG(N)
# - An Edge Group is derivable if every Edge in it is derivable
# - An Edge Group is not derivable if any Edge in it is not derivable
# - An empty Edge Group is derivable
#
# - An edge E=(A,B) ["A derives B"] is derivable if node A is in the given column list
# and the rest of E's Edge Group is derivable.
#
# - An edge E=(A,B) is not derivable if:
#   * node A is a leaf node or A's inward edges have already
# been visited (this avoids infinite cycles).
#
# Therefore there ill be backtracking if an edge E is not derivable.
def get_edge_group(graph: DiGraph, edge: Edge) -> GroupedEdges:
    return tuple()


def is_edge_derivable(graph: DiGraph, columns_given: set[Node], edge: Edge) -> bool:
    edge_group: GroupedEdges = get_edge_group(graph, edge)
    if is_trivially_derivable(columns_given, edge) and len(edge_group) == 0:
        return True
    # HELP
    return False


def is_edge_group_derivable(
    graph: DiGraph, columns_given: set[Node], group: GroupedEdges
) -> bool:
    if len(group) == 0:
        return True
    return all(map(functools.partial(is_edge_derivable, graph, columns_given), group))


def is_trivially_derivable(columns_given: set[Node], edge: Edge) -> bool:
    original: Node = edge[0]
    if original in columns_given:
        return True
    return False


def algorithm(graph: DiGraph, columns_given: set[Node], to_resolve: Node):
    edge_group_stack: list[GroupedEdges] = []
    edges_stack: list[Edge] = []
    seen_edges: set[Edge] = set()
    # To "remove" items
    remaining_group_edges: dict[GroupId, set[Edge]] = deepcopy(
        graph.group_id_to_edges_map
    )
    # edge_groups: list[GroupedEdges] = graph.edge_groups(to_resolve)
    # edge_groups.extend(edge_groups)

    # push to the stack
    edges_stack.extend(graph.get_in_edges(to_resolve))

    while len(edges_stack) > 0:
        edge: Edge = edges_stack.pop()
        edge_group: GroupedEdges = get_edge_group(graph, edge)

        logger.debug(edge_group_stack)
        logger.debug(edge_group)
        logger.debug(remaining_group_edges)
        logger.debug(seen_edges)


# Algorithm:
# Start at column_to_resolve C and create two stacks, EGS and ES
# The EGS will be for Edge Groups, the ES stack will be for Edges.
# Push EG(C) to the stack
# while EGS is not empty:
#   Take the next edge group
#   Loop over each edge and see if it's derivable
#    S = [EG(C), EG(C1), ... ]
# - Traverse the stack and stop when any of the conditions are met:
# 1. S is length 1 and all EGs have been traversed.?
