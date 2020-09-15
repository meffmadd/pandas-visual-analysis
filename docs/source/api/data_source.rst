DataSource
=========================================

.. currentmodule:: pandas_visual_analysis

.. autoclass:: pandas_visual_analysis.data_source.DataSource
    :members:
    :show-inheritance:

Advanced Usage of DataSource
------------------------------

For getting started see the `basic usage guide <https://pandas-visual-analysis.readthedocs.io/en/latest/#usage>`_.

Read Data
^^^^^^^^^^^

It is possible to read data directly from from files or URLs from the DataSource using default settings.

.. code-block:: python

    from pandas_visual_analysis import DataSource
    ds = DataSource.read_csv("./mpg.csv")


To infer the file type from the extension use the ``read()`` method. Supported file types are: .csv, .tsv and .json.

.. code-block:: python

    from pandas_visual_analysis import DataSource
    ds = DataSource.read("./mpg.json", orient="columns")

For more advanced options, use the functionality provided by `Pandas <https://pandas.pydata.org/pandas-docs/stable/reference/io.html>`_
and pass the DataFrame to DataSource normally.

Using DataSource as a context manager
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Instead of assigning the DataSource object to a variable, it is also possible to use it as a context manager.

.. code-block:: python

    from pandas_visual_analysis import DataSource, VisualAnalysis
    with DataSource.read("./report.tsv", header=1) as ds:
        VisualAnalysis(ds)
