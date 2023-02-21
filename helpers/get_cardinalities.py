def get_cardinalities(gen_status):
    """
    TO-DO!!!

    Args:
        gen_status: TO-DO!!!

    Returns: TO-DO!!!
    """

    cardinalities = {}

    for qid, status in gen_status.items():
        count = 0
        for group_name, tuple_ in status['hierarchy'].items():
            if tuple_[1] == status['level']:
                count += 1
        cardinalities[qid] = count

    return cardinalities
