from pandas import DataFrame

from pandas_visual_analysis.utils import hex_to_rgb
import pandas_visual_analysis  # import this way to prevent circular imports


def validate_data(data, name="data"):
    if not isinstance(data, (DataFrame, pandas_visual_analysis.DataSource)):
        raise TypeError(
            "The %s parameter must be a Pandas DataFrame or a DataSource" % name
        )


def validate_data_frame(df, name="df"):
    if not isinstance(df, DataFrame):
        raise TypeError("The %s parameter must be a Pandas DataFrame." % name)


def validate_row_height(row_height, name="row_height"):
    if not isinstance(row_height, int):
        raise TypeError("The value for %s has to be an integer." % name)
    if row_height < 0:
        raise ValueError(
            "The value for %s has to be larger than 0. Invalid Value: %d"
            % (name, row_height)
        )


def validate_alpha(alpha):
    if not (isinstance(alpha, float) or isinstance(alpha, int)):
        raise TypeError(
            "Alpha has to be a floating point value, not %s", str(type(alpha))
        )
    if alpha < 0.0 or alpha > 1.0:
        raise ValueError(
            "Alpha value has to be between 0.0 and 1.0. Invalid value: %d" % alpha
        )


def validate_sample(sample, name="sample"):
    if not (isinstance(sample, float) or isinstance(sample, int) or sample is None):
        raise TypeError(
            "The value of the parameter %s has to be a floating point value, not %s"
            % (name, str(type(sample)))
        )


def validate_color(color):
    if isinstance(color, str):
        color = hex_to_rgb(color)
    elif isinstance(color, tuple):
        if len(color) != 3:
            raise ValueError("The tuple specifying select_color has to be of length 3.")
    else:
        raise TypeError("The type of select_color has to be a string or tuple.")

    if (
        not (0 <= color[0] <= 255)
        or not (0 <= color[1] <= 255)
        or not (0 <= color[2] <= 255)
    ):
        raise ValueError(
            "RGB values have to be between 0 and 255. Invalid values: %s" % str(color)
        )
