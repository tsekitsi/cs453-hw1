from helpers.bfs import *
from helpers.get_cardinalities import *
import pandas as pd


def k_anonymize(private_table, k, k_req, quasi_ids, hierarchies, path_out=None):
    """
    Performs generalization on the specified quasi-identifier attributes, per the provided hierarchies, on the input
    dataset (private_table), guaranteeing personalized k-anonymity.
    Limitations: only works with (1) quasi-identifiers with distinct (not continuous) values, (2) hierarchies with no
    duplicate names.

    Args:
        private_table (pd.DataFrame): The table to anonymize.
        k (int):                      The desired degree of anonymization. It cannot be > num of rows in private_table.
        k_req (str):                  The name of the column in private_table with record-specific k requirements.
        quasi_ids (tuple[str]):       The names of the attributes to consider as quasi-identifiers.
                                      An array of strings, all of which are expected to be valid names of columns in
                                      private_table. Also, it is expected that this is ordered in correspondence to the
                                      order of hierarchies (next parameter).
        hierarchies (tuple[dict]):    Hierarchies for each of the quasi-identifiers. It is expected that (1) there is a
                                      hierarchy provided for each of the quasi-identifiers, (2) each hierarchy is valid
                                      (i.e. each level includes all the values of the level below it), (3) all strings
                                      are valid names of columns in private_table, (4) there are no duplicate value
                                      names!
                                      An array of dictionaries (json-like object). Each hierarchy is represented by a
                                      dictionary with (k, v) pairs, where k is an int or string representing the name of
                                      a group/value, and v is an array representing the children of k in the hierarchy,
                                      with elements that are either int/string/etc. (in the case of bottom-level values)
                                      or dictionary.
                                      Example: suppose we have a 3-level hierarchy of the natural numbers: [1-9] defined
                                      as follows, from bottom-level to top-level:
                                        - Level 0: 1, 2, 3, 4, 5, 6, 7, 8, 9
                                        - Level 1: even, odd
                                        - Level 2: *
                                      Then, we would represent this hierarchy as:
                                        {'*': [{'even': [2, 4, 6, 8]}, {'odd': [1, 3, 5, 7, 9]}]}
        path_out (str):               (Optional) A path (incl. filename) where to export the generalized table as csv.

    Returns: A tuple (df, k_achieved, levels) where df = DataFrame of the anonymized dataset, k = the degree of
             anonymization achieved, levels = dict with values tuples (x, n), where x, n are integers to denote that
             level x generalization was selected out of n levels for each quasi-identifier (the dict keys).
    """

    # Initializations:
    gen_table = private_table.copy()

    gen_status = dict(zip(quasi_ids, [bfs(hierarchy) for hierarchy in hierarchies]))
    for qid in gen_status:
        gen_status[qid]['level'] = 0

    violation = True
    iter_num = 0

    freq_dict = {}

    # Repeat until k-anonymity satisfied:
    while violation:
        violation = False  # start in good faith!
        iter_num += 1

        # (Re)compute freq_dict:
        freq_dict = {}
        for index, row in gen_table.iterrows():
            key = tuple([row[attr] for attr in quasi_ids])

            if key in freq_dict:
                freq_dict[key] += 1
            else:
                freq_dict[key] = 1

        # Exit while loop if there are no more generalizations to be made:
        count_generalizable = len(gen_status)
        for qid, status in gen_status.items():
            if status['level'] == status['depth']:
                count_generalizable -= 1
        if not count_generalizable:
            print('Reach max generalization for all quasi identifiers!')
            break

        # Iterate through all of freq_dict:
        for equiv_class, count in freq_dict.items():
            # Any equiv class violating k-anonymity?
            violation = count < k
            if violation:
                break

        # Check if any record-specific k requirement is violated:
        if not violation:
            for index, row in gen_table.iterrows():
                key = tuple([row[attr] for attr in quasi_ids])
                violation = freq_dict[key] < row[k_req]
                if violation:
                    print('Record-specific k requirement NOT satisfied!')
                    break

        cardinalities = get_cardinalities(gen_status)

        if violation:
            # Generalize heuristically:

            q_max = pd.DataFrame(cardinalities, index=[0]).idxmax(1)[0]

            print('Iteration {}: k={}-anonymity NOT satisfied!'.format(iter_num, k))
            print(' |  Generalization status (* = next to generalize):')
            for qid, status in gen_status.items():
                next_indicator = '*' if qid == q_max else ' '
                print(
                    ' |   |  [{}] {}: level = {} (of {}), cardinality = {}'.format(
                        next_indicator, qid, status['level'], status['depth'], cardinalities[qid]
                    )
                )

            gen_status[q_max]['level'] += 1  # update level of generalization for q

            for index, row in gen_table.iterrows():
                x = gen_status[q_max]['hierarchy'][row[q_max]][0]
                gen_table.at[index, q_max] = x
        else:
            print('Iteration {}: k={}-anonymity SATISFIED!'.format(iter_num, k))
            print(' |  Generalization status:')
            for qid, status in gen_status.items():
                print(
                    ' |   |  [X] {}: level = {} (of {}), cardinality = {}'.format(
                        qid, status['level'], status['depth'], cardinalities[qid]
                    )
                )

    k_achieved = min(list(pd.DataFrame(freq_dict, index=[0]).iloc[0]))

    levels = {qid: (status['level'], status['depth']) for qid, status in gen_status.items()}

    # Export table to csv, if requested:
    if path_out:
        gen_table.to_csv(path_out)

    return gen_table, k_achieved, levels
