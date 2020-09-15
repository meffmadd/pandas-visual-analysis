VisualAnalysis
=========================================

.. currentmodule:: pandas_visual_analysis

.. autoclass:: pandas_visual_analysis.visual_analysis.VisualAnalysis
    :members:
    :show-inheritance:


Advanced Usage of VisualAnalysis
----------------------------------

For getting started see the `basic usage guide <https://pandas-visual-analysis.readthedocs.io/en/latest/#usage>`_.

Row Height
^^^^^^^^^^^

The `row_height` parameter enables control over the height of the widgets in rows.

When the value is an integer, all rows will have that height in pixels:

.. code-block:: python

    from pandas_visual_analysis import VisualAnalysis
    VisualAnalysis(df, row_height=300)

When the parameter is a list of integers, each row will have the height of the value in the list at that position:

.. code-block:: python

    from pandas_visual_analysis import VisualAnalysis
    VisualAnalysis(df, layout=[["Scatter", "Scatter"], ["ParallelCoordinates"]],
                   row_height=[200, 300])

Here, the first row with the two scatter plot will have a height of 200 pixels while the parallel coordinates plot
has a height of 300 pixels.

Sample
^^^^^^^

The sample parameter accepts either an integer or a float value between ``0.0`` and ``1.0``.

When an integer value is passed, the `DataFrame` is sampled to contain that many rows:

.. code-block:: python

    >>> from pandas_visual_analysis import VisualAnalysis
    >>> v = VisualAnalysis(df, sample=100)
    >>> len(v.data_source)
    100

The following analysis will only show 100 data points sampled from ``df``. This means the integer cannot be
larger than the length of the initial DataFrame.

When a float is passed, the `DataFrame` is sampled to contain the fraction of rows given by the value.

.. code-block:: python

    from pandas_visual_analysis import VisualAnalysis
    VisualAnalysis(df, sample=0.5)

Assuming the passed `DataFrame` originally contained 300 rows, the analysis will only show 150 of them.

It is also possible to pass a seed used for sampling:

.. code-block:: python

    from pandas_visual_analysis import VisualAnalysis
    VisualAnalysis(df, sample=0.5, seed=17)

The value of the seed has to be an integer between ``0`` and ``2**32-1`` inclusive.

Colors
^^^^^^^

Instead of using the default color, it is possible to pass custom colors to the `VisualAnalysis` object.
There are ``select_color`` and ``deselect_color`` which specify the colors to use to represent selected and deselected
data points. They can either be hex strings (like `'#323EEC'`) or tuples
representing RGB values (like `(50, 62, 236)`).

The parameter `alpha` specifies the opacity of the data points when applicable and is specified by a float value
between ``0.0`` and ``1.0``. A value of ``0.0`` means transparent and ``1.0`` means opaque.

.. code-block:: python

    from pandas_visual_analysis import VisualAnalysis
    VisualAnalysis(df, select_color='#323EEC', deselect_color='#8A8C93', alpha=0.75)

