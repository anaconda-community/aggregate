from typing import Iterable, Tuple, Set, Dict, Union

from pydantic import BaseModel


class EquivalenceClass(BaseModel):
    members: Set[str]
    cycle_edges: Dict[str, Set[str]]


def _copy_edge_map(edge_map: Dict[str, Set[str]]) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
    depends_on = {}
    required_by = {}
    for src, destinations in edge_map.items():
        depends_on[src] = destinations
        required_by.setdefault(src, set())
        for dest in destinations:
            depends_on.setdefault(dest, set())
            required_by.setdefault(dest, set()).add(src)
    return depends_on, required_by


def _find_unreferenced(nodes: Set[str], depends_on: Dict[str, Set[str]]) -> Tuple[Set[str], Set[str]]:
    unreferenced = {node for node in nodes if not depends_on.get(node)}
    return unreferenced, nodes.difference(unreferenced)


def _collect_dependencies(node: str, depends_on: Dict[str, Set[str]]) -> Set[str]:
    cycle_nodes = {node}
    to_add = depends_on[node]
    while not to_add.issubset(cycle_nodes):
        cycle_nodes.update(to_add)
        to_add = {dependency for n in to_add for dependency in depends_on[n]}
    return cycle_nodes


def topological_sort(edge_map: Dict[str, Set[str]]) -> Iterable[EquivalenceClass]:
    # Essential idea is to iteratively remove nodes without dependencies from the graph.
    # Maintain a set of candidates which we partition into those which can and can't be removed.
    # If we reach a point where no candidates are removable, then we've found at least one cycle.
    # We can remove the cycle and resume.
    # On removal, any node depending on one of the removed nodes becomes a potential candidate.
    # Eventually, we will have removed all the nodes and are done.

    # Maintain a forward map of dependencies (which tracks the current state of the graph)
    # and a reverse map used to update the candidate set.
    depends_on, required_by = _copy_edge_map(edge_map)

    # Initially, all nodes without dependencies are candidates
    # By definition, they are unblocked, so we don't need to partition them
    candidates = {node for node, dependencies in depends_on.items() if not dependencies}
    unblocked = candidates
    blocked = set()

    while unblocked or blocked:
        if unblocked:
            new_candidates = {child for node in unblocked for child in required_by[node]}
            candidates = blocked.union(new_candidates)
            # Remove dependency edges to unblocked nodes
            for node in new_candidates:
                depends_on[node].difference_update(unblocked)
            yield EquivalenceClass(members=unblocked, cycle_edges={})
        else:
            # All remaining candidate nodes are involved in some cycle
            # Choose one node and get all the nodes in the cycle.
            # Because we've removed all (acyclic) dependencies, the dependencies remaining
            # must be part of the cycle. So the reachable dependencies are the cycle
            # (simple or complex).
            cycle_nodes = _collect_dependencies(blocked.pop(), depends_on)

            # All nodes requiring a node in the removed cycle are potential candidates for next wave
            new_candidates = {child for node in cycle_nodes for child in required_by[node] if child not in cycle_nodes}
            # Cycle may have involved additional nodes in blocked which can be removed now
            candidates = blocked.difference(cycle_nodes).union(new_candidates)
            # Remove dependency edges to cycle nodes
            for node in new_candidates:
                depends_on[node].difference_update(cycle_nodes)

            # Get only the edges involving cycle nodes; this is the cycle (perhaps interleaving)
            cycle_edges = {node: set(depends_on[node]) for node in cycle_nodes}
            yield EquivalenceClass(members=cycle_nodes, cycle_edges=cycle_edges)

        unblocked, blocked = _find_unreferenced(candidates, depends_on)