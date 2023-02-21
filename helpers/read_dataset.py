import pandas as pd
import requests
from os import path


def read_dataset(verbose=False):
    """
    Reads the "Adult" dataset into a pandas.DataFrame from a local file, or from the Internet (in that case, it also
    writes it to local storage).

    Args:
        verbose (bool): A boolean to determine whether to print logs or not.

    Returns:
        A pandas.DataFrame of the dataset.
    """

    names = ['age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 'occupation', 'relationship',
             'race', 'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'agrossincome']

    remote_url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data'
    local_path = path.join('data', 'adult.cached')

    source = 'local file' if path.exists(local_path) else 'the net'

    print('Reading data from {}...'.format(source)) if verbose else None

    if source == 'the net':
        with open(local_path, "wb") as f:
            f.write(requests.get(remote_url).content)
    else:
        remote_url = local_path

    return pd.read_csv(remote_url, delimiter=', ', engine='python', header=None, names=names)
