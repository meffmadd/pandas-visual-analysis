import pandas as pd
import numpy as np


def small_df():
    return pd.DataFrame({'a': [1, 2, 3, 4, 5],
                         'b': ['v', 'W', 'X', 'Y', 'Z'],
                         'c': [1.5, 2.5, 3.5, 4.5, 5.5],
                         'd': [np.datetime64('now'), np.datetime64('now'), np.datetime64('now'), np.datetime64('now'), np.datetime64('now')],
                         'e': [True, True, False, False, True]
                         })


def small_df_non_int_index():
    df = small_df()
    df.set_index(pd.Index(['a_one', 'b_two', 'c_three', 'd_four', 'e_five'], dtype=str), inplace=True)
    return df


def randint_df(size: int):
    return pd.DataFrame(np.random.randint(0, size, size=(size, 4)), columns=list('ABCD'))


def random_float_df(size: int):
    return pd.DataFrame(np.random.uniform(low=0.5, high=13.3, size=(size,4)), columns=list('ABCD'))


def random_df(size: int):
    return pd.DataFrame({'a': np.random.uniform(low=0.5, high=13.3, size=(size,)),
                         'b': np.random.uniform(low=1000.5, high=5000.3, size=(size,)),
                         'c': np.random.choice(['pooh', 'rabbit', 'piglet'], size),
                         'd': np.random.randint(0, 10000, size),
                         'e': np.random.choice([True, False], size),
                         'f': np.random.uniform(low=0.5, high=13.3, size=(size,)),
                         })


def random_df_with_nan(size: int):
    df = random_df(size)
    rand_ind = np.random.randint(1, size, int(size/4))
    df['a'][rand_ind] = np.nan
    return df


def random_float_df_with_nan(size: int):
    df = random_float_df(size)
    rand_ind = np.random.randint(1, size, int(size / 4))
    df['A'][rand_ind] = np.nan
    rand_ind = np.random.randint(1, size, int(size / 4))
    df['C'][rand_ind] = np.nan
    return df
