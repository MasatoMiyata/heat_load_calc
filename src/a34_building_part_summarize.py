import numpy as np
from typing import List

from s3_surface_initializer import IntegratedBoundaries
from s3_surface_loader import Boundary
from s3_surface_loader import InternalPartSpec
from s3_surface_loader import GeneralPartSpec
from s3_surface_loader import TransparentOpeningPartSpec
from s3_surface_loader import OpaqueOpeningPartSpec
from s3_surface_loader import GroundSpec
from a39_global_parameters import BoundaryType

"""
付録34．境界条件が同じ部位の集約
"""


def is_boundary_integratable(b1: Boundary, b2: Boundary) -> bool:
    """
    境界1と境界2が同じであるかを判定する。

    Args:
        b1: 境界1
        b2: 境界2

    Returns:
        判定結果
    """

    # 境界のメイン部分の整合性をチェックし、同じでなければFalseを返して終了。
    if not is_boundary_bodies_integratable(b1, b2):
        return False

    # 境界の種類が間仕切りの場合
    if b1.boundary_type == BoundaryType.Internal:

        return is_boundary_internals_integratable(bi1=b1.spec, bi2=b2.spec)

    # 境界の種類が一般部位の場合
    elif b1.boundary_type == BoundaryType.ExternalGeneralPart:

        return is_boundary_generals_integratable(bg1=b1.spec, bg2=b2.spec)

    # 境界の種類が透明な開口部の場合
    elif b1.boundary_type == BoundaryType.ExternalTransparentPart:

        return is_boundary_transparent_openings_integratable(bto1=b1.spec, bto2=b2.spec)

    # 境界の種類が非透明な開口部の場合
    elif b1.boundary_type == BoundaryType.ExternalOpaquePart:

        return is_boundary_opaque_openings_integratable(boo1=b1.spec, boo2=b2.spec)

    # 境界の種類が地盤の場合
    elif b1.boundary_type == BoundaryType.Ground:

        return is_boundary_grounds_integratable(bg1=b1.spec, bg2=b2.spec)

    else:
        raise ValueError()


def is_almost_equal(v1: float, v2: float) -> bool:
    """
    境界条件が同じかどうかを判定する際に値が同じであるかを判定する時に、プログラム上の誤差を拾わないために、
    少し余裕を見て10**(-5) 以内の差であれば、同じ値であるとみなすことにする。
    この部分はプログラムテクニックの部分であるため、仕様書には書く必要はない。

    Args:
        v1: 比較する値1
        v2: 比較する値2

    Returns:
        同じか否かの判定結果
    """

    return abs(v1 - v2) < 1.0E-5


def is_boundary_bodies_integratable(b1: Boundary, b2: Boundary) -> bool:
    """
    Boundary のメイン部分が統合可能であるかを判断する。

    Args:
        b1: 境界1
        b2: 境界2

    Returns:
        判定結果

    Notes:
        以下の値がすべて同じである場合に、境界1のメイン部分と境界2のメイン部分に関して統合可能であると判断する。
        (1) 境界の種類
        (2) 室内侵入日射吸収の有無
        (3) 日射の有無（境界の種類が「外皮_一般部位」・「外皮_透明な開口部」・「外皮_不透明な開口部」の場合のみ）
        (4) 温度差係数（境界の種類が「外皮_一般部位」・「外皮_透明な開口部」・「外皮_不透明な開口部」の場合のみ）
        (5) 向き(日射の有無が「当たる」の場合）
        (6) 隣室タイプ（境界の種類が「間仕切り」の場合）
        なお、メイン部分とは、
        間仕切り・一般部位・透明な開口部・非透明な開口部・地盤などの仕様や、日除けの仕様を覗いた部分
    """

    # 境界の種類
    if b1.boundary_type != b2.boundary_type:
        return False

    # 室内侵入日射吸収の有無
    if b1.is_solar_absorbed_inside != b2.is_solar_absorbed_inside:
        return False

    # 境界の種類が「外皮_一般部位」、「外皮_透明な開口部」又は「外皮_不透明な開口部」の場合
    if (b1.boundary_type == BoundaryType.ExternalGeneralPart) \
            or (b1.boundary_type == BoundaryType.ExternalTransparentPart) \
            or (b1.boundary_type == BoundaryType.ExternalOpaquePart):

        # 日射の有無
        if b1.is_sun_striked_outside != b2.is_sun_striked_outside:
            return False

        # 温度差係数
        if not is_almost_equal(b1.temp_dif_coef, b2.temp_dif_coef):
            return False

        # 日射の有無が当たるの場合
        if b1.is_sun_striked_outside:

            # 向き
            if b1.direction != b2.direction:
                return False

    # 境界の種類が間仕切りの場合
    if b1.boundary_type == BoundaryType.Internal:

        # 隣室タイプ
        if b1.next_room_type != b2.next_room_type:
            return False

    # 上記のチェックすべてでFalse判定がでなければ、それは同一であるとみなす。
    return True


def is_boundary_internals_integratable(bi1: InternalPartSpec, bi2: InternalPartSpec) -> bool:
    """
    Boundary の InternalPartSpec が統合可能であるかを判断する。

    Args:
        bi1: 境界1の間仕切りの仕様
        bi2: 境界2の間仕切りの仕様

    Returns:
        判定結果

    Notes:
        以下の値がすべて同じである場合に、境界1の間仕切りの仕様と境界2の間仕切りの仕様に関して統合可能であると判断する。
        (1) 室内側熱伝達抵抗
    """

    return is_almost_equal(bi1.inside_heat_transfer_resistance, bi2.inside_heat_transfer_resistance)


def is_boundary_generals_integratable(bg1: GeneralPartSpec, bg2: GeneralPartSpec) -> bool:
    """
    Boundary の GeneralPartSpec が統合可能であるかを判断する。

    Args:
        bg1: 境界1の一般部位の仕様
        bg2: 境界2の一般部位の仕様

    Returns:
        判定結果

    Notes:
        以下の値がすべて同じである場合に、境界1の間仕切りの仕様と境界2の間仕切りの仕様に関して統合可能であると判断する。
        (1) 室外側長波長放射率
        (2) 室外側日射吸収率
        (3) 室外側日射吸収率
        (4) 室外側熱伝達抵抗
    """

    # 室外側長波長放射率
    if not is_almost_equal(bg1.outside_emissivity, bg2.outside_emissivity):
        return False

    # 室外側日射吸収率
    if not is_almost_equal(bg1.outside_solar_absorption, bg2.outside_solar_absorption):
        return False

    # 室内側熱伝達抵抗
    if not is_almost_equal(bg1.inside_heat_transfer_resistance, bg2.inside_heat_transfer_resistance):
        return False

    # 室外側熱伝達抵抗
    if not is_almost_equal(bg1.outside_heat_transfer_resistance, bg2.outside_heat_transfer_resistance):
        return False

    # 上記のチェックすべてでFalse判定がでなければ、それは同一であるとみなす。
    return True


def is_boundary_transparent_openings_integratable(
        bto1: TransparentOpeningPartSpec, bto2: TransparentOpeningPartSpec) -> bool:
    """
    Boundary の TransparentOpeningPartSpec が統合可能であるかを判断する。
    Args:
        bto1: 境界1の透明な開口部の仕様
        bto2: 境界2の透明な開口部の仕様

    Returns:
        判定結果

    Notes:
        以下の値がすべて同じである場合に、
        境界の透明な開口部の仕様1と境界の透明な開口部の仕様2に関して統合可能であると判断する。
        (1) 室外側長波長放射率
        (2) 室内側熱伝達抵抗
        (3) 室外側熱伝達抵抗
    """

    # 室外側長波長放射率
    if not is_almost_equal(bto1.outside_emissivity, bto2.outside_emissivity):
        return False

    # 室内側熱伝達抵抗
    if not is_almost_equal(bto1.inside_heat_transfer_resistance, bto2.inside_heat_transfer_resistance):
        return False

    # 室外側熱伝達抵抗
    if not is_almost_equal(bto1.outside_heat_transfer_resistance, bto2.outside_heat_transfer_resistance):
        return False

    # 上記のチェックすべてでFalse判定がでなければ、それは同一であるとみなす。
    return True


def is_boundary_opaque_openings_integratable(boo1: OpaqueOpeningPartSpec, boo2: OpaqueOpeningPartSpec) -> bool:
    """
    Boundary の OpaqueOpeningSpec が統合可能であるかを判断する。

    Args:
        boo1: 境界1の不透明な開口部の仕様
        boo2: 境界2の不透明な開口部の仕様

    Returns:
        判定結果

    Notes:
        以下の値がすべて同じである場合に、
        境界1の不透明な開口部の仕様と境界2の不透明な開口部の仕様に関して統合可能であると判断する。
        (1) 室外側長波長放射率
        (2) 室外側日射吸収率
        (3) 室外側日射吸収率
        (4) 室外側熱伝達抵抗
    """

    # 室外側長波長放射率
    if not is_almost_equal(boo1.outside_emissivity, boo2.outside_emissivity):
        return False

    # 室外側日射吸収率
    if not is_almost_equal(boo1.outside_solar_absorption, boo2.outside_solar_absorption):
        return False

    # 室内側熱伝達抵抗
    if not is_almost_equal(boo1.inside_heat_transfer_resistance, boo2.inside_heat_transfer_resistance):
        return False

    # 室外側熱伝達抵抗
    if not is_almost_equal(boo1.outside_heat_transfer_resistance, boo2.outside_heat_transfer_resistance):
        return False

    # 上記のチェックすべてでFalse判定がでなければ、それは同一であるとみなす。
    return True


def is_boundary_grounds_integratable(bg1: GroundSpec, bg2: GroundSpec) -> bool:
    """
    Boundary の GroundSpec が統合可能であるかを判断する。

    Args:
        bg1: 境界1の地盤の仕様
        bg2: 境界2の地盤の仕様

    Returns:
        判定結果

    Notes:
        以下の値がすべて同じである場合に、境界1の地盤の仕様と境界2の地盤の仕様に関して統合可能であると判断する。
        (1) 室内側熱伝達抵抗
    """

    return is_almost_equal(bg1.inside_heat_transfer_resistance, bg2.inside_heat_transfer_resistance)


def get_group_indices(boundaries: List[Boundary]) -> np.ndarray:
    """
    集約化できるBoundaryには共通のIDをふっていく。

    Args:
        boundaries: 室iにおける境界kのリスト

    Returns:
        グループ番号 * 境界の数

    Notes:
        例えば、境界の種類が擬似的に、
        [A,B,C,B,A,C,D,E,F,D,E]
        だった場合は、Aからグループ番号を振り、
        [0,1,2,1,0,2,3,4,5,3,4]
        となる。
    """

    n = len(boundaries)

    # 部位番号とグループ番号の対応表 (-1は未割当)
    g_k = np.zeros(n, dtype=np.int64) - 1

    # 部位のグループ化
    for k in range(n):

        # 同じ境界条件の部位を探す
        gs_index = np.array(
            [l for l in range(n)
             if g_k[l] < 0 and is_boundary_integratable(boundaries[k], boundaries[l])], dtype=np.int64)

        # 部位番号とグループ番号の対応表に新しいグループ番号を記述
        g_k[gs_index] = np.max(g_k) + 1

    return g_k
