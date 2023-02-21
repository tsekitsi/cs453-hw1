from collections import deque


def has_children(node):
    """
    Args:
        node (dict): A single-key dict (json-like object) with key = name of the node, value = an array of child nodes
                     (dicts).

    Returns: True if the node has children, else false.
    """

    return type(node) is dict


def get_name(node):
    """
    Args:
        node (dict): A single-key dict (json-like object) with key = name of the node, value = an array of child nodes
                     (dicts).

    Returns: The name of a node (key of the dict).
    """

    return list(node.keys())[0] if has_children(node) else node


def bfs(root):
    """
    Performs a breadth-first search (bfs) on the hierarchy represented by root, and calculates (1) a mapping of nodes to
    their parent nodes, and (2) each node's depth from root in the bfs traversal (i.e. hierarchy level).

    Args:
        root (dict): A single-key dict (json-like object) with key = name of the node, value = an array of child nodes
                     (dicts).

    Returns: A dictionary ('hierarchy') with keys = all the distinct values (across all levels) in the hierarchy root,
             values = tuple (parent, level) where parent is the name of key's parent and level is key's level in the
             hierarchy, and an int ('depth') of the depth of the hierarchy (total number of levels).
    """

    root_name = get_name(root)
    queue = deque([root])
    parents_and_levels = {root_name: (None, 0)}

    max_depth = 0

    while queue:
        node = queue.popleft()
        node_name = get_name(node)
        children = node[node_name] if has_children(node) else []
        for child in children:
            child_name = get_name(child)
            queue.append(child)
            max_depth = parents_and_levels[node_name][1] + 1
            parents_and_levels[child_name] = (node_name, max_depth)

    # Reverse the level numbers:
    for value_name in parents_and_levels:
        parents_and_levels[value_name] = (
            parents_and_levels[value_name][0],
            max_depth-parents_and_levels[value_name][1]
        )

    return {'hierarchy': parents_and_levels, 'depth': max_depth}
