.. image:: https://github.com/meffmadd/pandas-visual-analysis/blob/master/docs/source/_static/assets/banner.jpeg?raw=true
   :width: 95%
   :alt: banner
   :align: center


Status

.. image:: https://github.com/meffmadd/pandas-visual-analysis/workflows/Tests/badge.svg
    :target: https://github.com/meffmadd/pandas-visual-analysis/actions?query=workflow%3ATests

.. image:: https://readthedocs.org/projects/pandas-visual-analysis/badge/?version=latest
    :target: https://pandas-visual-analysis.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://codecov.io/gh/meffmadd/pandas-visual-analysis/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/meffmadd/pandas-visual-analysis

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :alt: MIT License
    :target: https://opensource.org/licenses/MIT

Release

.. image:: https://img.shields.io/pypi/v/pandas-visual-analysis?color=blue
    :target: https://pypi.org/project/pandas-visual-analysis/
    :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/pandas-visual-analysis
    :alt: PyPI - Python Version

Code

.. image:: https://api.codacy.com/project/badge/Grade/87128508f93c474ba93f6eff45e5a9fb
    :alt: Codacy Badge
    :target: https://app.codacy.com/manual/meffmadd/pandas-visual-analysis?utm_source=github.com&utm_medium=referral&utm_content=meffmadd/pandas-visual-analysis&utm_campaign=Badge_Grade_Settings

.. image:: https://api.codeclimate.com/v1/badges/46ff86e0785eda2a2e80/maintainability
   :target: https://codeclimate.com/github/meffmadd/pandas-visual-analysis/maintainability
   :alt: Maintainability

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black


|
|

.. intro-start

Pandas-Visual-Analysis enables visual analysis of a pandas ``DataFrame`` in Jupyter notebooks.
It can display various different types of graphs with support for linked-brushing in interactive widgets.
This allows data exploration and cognition to be easy and convenient, even with complex multivariate datasets.

There is no need to setup and style plots or interactivity - its all ready without any configuration.

|

.. image:: https://github.com/meffmadd/pandas-visual-analysis/blob/master/docs/source/_static/assets/default_layout.gif?raw=true
   :width: 60%
   :alt: interactivity
   :align: center

|

.. intro-end

==================
Installation
==================

.. installation-start

Using pip
##########

You can install using the pip package manager by running

.. code-block::

    pip install pandas-visual-analysis

From Source
###########

Clone into the repository or download the `zip file <https://github.com/meffmadd/pandas-visual-analysis/archive/master.zip>`_
and run

.. code-block::

    python setup.py install


.. installation-end

==================
Usage
==================

.. usage-start

Basic Usage
###############


Having a ``DataFrame``, for example:

.. code-block:: python

    import pandas as pd
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mpg.csv"

    df = pd.read_csv(url)

you can just pass it to ``VisualAnalysis`` to display the default layout:

.. code-block:: python

    from pandas_visual_analysis import VisualAnalysis
    VisualAnalysis(df)

If you want to specify which columns of the ``DataFrame`` are categorical, just pass the ``categorical_coumns`` option:

.. code-block:: python

    from pandas_visual_analysis import VisualAnalysis
    categorical = ["name", "origin", "model_year", "cylinders"]
    VisualAnalysis(df, categorical_columns=categorical)


Using DataSource
################

Instead of passing the ``DataFrame`` object directly to ``VisualAnalysis`` it is possible to use a
a ``DataSource`` object.
This enables linked-brushing across multiple notebook cells if the object is used across cells.

.. code-block:: python

    from pandas_visual_analysis import VisualAnalysis, DataSource

    data = DataSource(df)
    VisualAnalysis(data)

Later you can create a new analysis with the brushing still preserved
simply by using the same ``data`` object created earlier.

.. code-block:: python

    VisualAnalysis(data)

Using Layouts
#############

If you want to specify your own layout, you can do that by passing the ``layout`` parameter.
The parameter is a list of rows, where each row is in turn a list specifying the Widgets in that row.

.. code-block:: python

    VisualAnalysis(df,
        layout=[["Scatter", "Scatter"],
                ["ParallelCoordinates"]]
    )

Here, two scatter plots will share the first row while the second row only contains a parallel coordinates plot.
In order to see all the possible options you can the ``widgets`` method of ``VisualAnalysis``.

.. code-block:: python

    VisualAnalysis.widgets()

This outputs the following list of plots:

.. code-block:: python

    ['Scatter',
     'ParallelCoordinates',
     'BrushSummary',
     'Histogram',
     'ParallelCategories',
     'BoxPlot']

Any of those can be part of the layout specification.

See also: `widgets Documentation <https://pandas-visual-analysis.readthedocs.io/en/latest/api/widgets.html>`_.

.. usage-end


====================
Documentation
====================

For more details see the `Official Documentation <https://pandas-visual-analysis.readthedocs.io/>`_.