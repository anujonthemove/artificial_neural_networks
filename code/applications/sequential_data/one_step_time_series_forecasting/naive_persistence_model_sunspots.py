"""

Model: Persistence Model
Mehtod: Naive (i.e. copying the last value)

Dataset: Monthly sunspots
Task: One-step ahead Forecasting of Univariate Time Series (Univariate Regression)

    Author: Ioannis Kourouklides, www.kourouklides.com
    License:
        https://github.com/kourouklides/artificial_neural_networks/blob/master/LICENSE

"""
# %%
# IMPORTS

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# standard library imports
import argparse
from math import sqrt
import os
import random as rn

# third-party imports
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# %%


def naive_persistence_model_sunspots(new_dir=os.getcwd()):
    """
    Main function
    """
    # %%
    # IMPORTS

    os.chdir(new_dir)

    # code repository sub-package imports
    from artificial_neural_networks.code.utils.download_monthly_sunspots import \
        download_monthly_sunspots
    from artificial_neural_networks.code.utils.generic_utils import series_to_supervised, \
        affine_transformation
    from artificial_neural_networks.code.utils.vis_utils import regression_figs

    # %%
    # SETTINGS
    parser = argparse.ArgumentParser()

    # General settings
    parser.add_argument('--verbose', type=int, default=1)
    parser.add_argument('--reproducible', type=bool, default=True)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--plot', type=bool, default=False)

    # Settings for preprocessing and hyperparameters
    parser.add_argument('--look_back', type=int, default=3)
    parser.add_argument('--scaling_factor', type=float, default=(1 / 780))
    parser.add_argument('--translation', type=float, default=0)

    args = parser.parse_args()

    if args.verbose > 0:
        print(args)

    # For reproducibility
    if args.reproducible:
        os.environ['PYTHONHASHSEED'] = '0'
        np.random.seed(args.seed)
        rn.seed(args.seed)

    # %%
    # Load the Monthly sunspots dataset

    sunspots_path = download_monthly_sunspots()
    sunspots = np.genfromtxt(
        fname=sunspots_path, dtype=np.float32, delimiter=",", skip_header=1, usecols=1)

    # %%
    # Train-Test split

    L_series = len(sunspots)

    split_ratio = 2 / 3  # between zero and one
    n_split = int(L_series * split_ratio)

    look_back = args.look_back

    train = np.concatenate((np.zeros(look_back), sunspots[:n_split]))
    test = sunspots[n_split - look_back:]

    train_x, train_y = series_to_supervised(train, look_back)
    test_x, test_y = series_to_supervised(test, look_back)

    # %%
    # PREPROCESSING STEP

    scaling_factor = args.scaling_factor
    translation = args.translation

    # Apply preprocessing
    train_x_ = affine_transformation(train_x, scaling_factor, translation)
    test_x_ = affine_transformation(test_x, scaling_factor, translation)

    # %%
    # TRAINING PHASE

    def model_predict(x):
        """
        Predict using the Naive Persistence Model
        """
        last = x.shape[1] - 1

        y_pred = []

        y_pred.append(x[0][last])

        for i in range(x.shape[0] - 1):
            y_pred.append(x[i][last])

        return np.array(y_pred)

    # %%
    # TESTING PHASE

    # Predict preprocessed values
    train_y_pred_ = model_predict(train_x_)
    test_y_pred_ = model_predict(test_x_)

    # Remove preprocessing
    train_y_pred = affine_transformation(train_y_pred_, scaling_factor, translation, inverse=True)
    test_y_pred = affine_transformation(test_y_pred_, scaling_factor, translation, inverse=True)

    train_rmse = sqrt(mean_squared_error(train_y, train_y_pred))
    train_mae = mean_absolute_error(train_y, train_y_pred)
    train_r2 = r2_score(train_y, train_y_pred)

    test_rmse = sqrt(mean_squared_error(test_y, test_y_pred))
    test_mae = mean_absolute_error(test_y, test_y_pred)
    test_r2 = r2_score(test_y, test_y_pred)

    if args.verbose > 0:
        print('Train RMSE: %.4f ' % (train_rmse))
        print('Train MAE: %.4f ' % (train_mae))
        print('Train (1 - R_squared): %.4f ' % (1.0 - train_r2))
        print('Train R_squared: %.4f ' % (train_r2))
        print('')
        print('Test RMSE: %.4f ' % (test_rmse))
        print('Test MAE: %.4f ' % (test_mae))
        print('Test (1 - R_squared): %.4f ' % (1.0 - test_r2))
        print('Test R_squared: %.4f ' % (test_r2))

    # %%
    # Data Visualization

    if args.plot:
        regression_figs(train_y=train_y, train_y_pred=train_y_pred,
                        test_y=test_y, test_y_pred=test_y_pred)


# %%

if __name__ == '__main__':
    naive_persistence_model_sunspots('../../../../../')
