"""窓の入射角特性

"""

import numpy as np


def get_tau_d_j_ns(theta_aoi_j_ns: np.ndarray, glazing_type_j: str) -> np.ndarray:
    """
    透明部位の入射角特性
    直達日射の入射角特性の計算

    Args:
        theta_aoi_j_ns:
        glazing_type_j:

    Returns:
        直達日射に対する基準化透過率
    """

    if glazing_type_j == 'single':
        return _get_tau_norm_glass_i_k_n(theta_aoi_i_k=theta_aoi_j_ns)

    elif glazing_type_j == 'multiple':
        return _get_taud_n_double(theta_aoi_i_k=theta_aoi_j_ns)

    else:
        raise ValueError()


def get_c_d_j(glazing_type_j: str) -> float:
    """
    窓ガラスのガラスの入射角特性タイプから拡散日射に対する基準化透過率を求める。

    Args:
        glazing_type_j: 室iの境界kにおける透明な開口部のガラスの入射角特性タイプ

    Returns:
        室iの境界kにおける透明な開口部の拡散日射に対する基準化透過率
    """

    # 入射角特性タイプが単板ガラスの場合
    if glazing_type_j == 'single':
        return _get_c_d_single()

    # 入射角特性タイプが複層ガラスの場合
    elif glazing_type_j == 'multiple':
        return _get_c_d_double()

    else:
        raise ValueError()


# 直達日射に対する基準化透過率の計算（単層ガラス）
def _get_tau_norm_glass_i_k_n(theta_aoi_i_k: np.ndarray) -> np.ndarray:

    c = np.cos(theta_aoi_i_k)



    return 0.000 * c ** 0.0 + 2.552 * c ** 1.0 + 1.364 * c ** 2.0 \
           - 11.388 * c ** 3.0 + 13.617 * c ** 4.0 - 5.146 * c ** 5.0


# 直達日射に対する基準化反射率の計算（単層ガラス）
def _get_rhod_n_single(theta_aoi_i_k) -> np.ndarray:

    cos = np.cos(theta_aoi_i_k)

    return 1.000 * cos ** 0.0 - 5.189 * cos ** 1.0 + 12.392 * cos ** 2.0 \
           - 16.593 * cos ** 3.0 + 11.851 * cos ** 4.0 - 3.461 * cos ** 5.0


# 直達日射に対する基準化透過率の計算（複層ガラス）
def _get_taud_n_double(theta_aoi_i_k: np.ndarray) -> np.ndarray:

    return _get_tau_norm_glass_i_k_n(
        theta_aoi_i_k=theta_aoi_i_k) ** 2.0 / (1.0 - _get_rhod_n_single(theta_aoi_i_k) ** 2.0)


def _get_c_d_single() -> float:
    """
    透明な開口部の拡散日射に対する基準化透過率（単層ガラス）を定義する。

    Returns:
        透明な開口部の拡散日射に対する基準化透過率（単層ガラス）
    """

    return 0.900


def _get_c_d_double() -> float:
    """
    透明な開口部の拡散日射に対する基準化透過率（複層ガラス）を定義する。

    Returns:
        透明な開口部の拡散日射に対する基準化透過率（複層ガラス）
    """

    return 0.832
