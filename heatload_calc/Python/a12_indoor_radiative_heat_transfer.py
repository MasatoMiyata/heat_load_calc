import math
import numpy as np

"""
付録12．	室内表面の吸収日射量、形態係数、放射暖房放射成分吸収比率
"""


# 微小体に対する部位の形態係数の計算 式(94)
def calc_form_factor_of_microbodies(space_name, area):
    # 面積比 式(95)
    a_k = get_a_k(area)

    # 面積比の最大値 （ニュートン法の初期値計算用）
    max_a = get_max_a(a_k)

    # 非線形方程式L(f̅)=0の解
    fb = get_fb(max_a, space_name, a_k)

    # 式（123）で示す放射伝熱計算で使用する微小球に対する部位の形態係数 [-] 式(94)
    FF_m = get_FF_m(fb, a_k)
    # print(FF_m)

    # 総和のチェック
    FF = np.sum(FF_m)
    if abs(FF - 1.0) > 1.0e-3:
        print('形態係数の合計値が不正 name=', space_name, 'TotalFF=', FF)

    return FF_m


# 面積比 [-] 式(95)
def get_a_k(A_i_k):
    A_i = sum(A_i_k)
    a_k = A_i_k / A_i
    return a_k


def get_max_a(a):
    return max(a)


# 式（123）で示す放射伝熱計算で使用する微小球に対する部位の形態係数 [-] 式(94)
def get_FF_m(fb, a):
    return 0.5 * (1.0 - np.sign(1.0 - 4.0 * a / fb) * np.sqrt(abs(1.0 - 4.0 * a / fb)))


# 非線形方程式L(f̅)=0の解
def get_fb(max_a, space_name, a):
    # 室のパラメータの計算（ニュートン法）
    # 初期値を設定
    m = 1.0e-5  # 式(99)
    n = 100.0
    m_n = (m + n) / 2.0
    
    # 収束判定
    isConverge = False
    for i in range(50):
        L_m = -1.0  # 式(96)の一部
        L_n = -1.0
        L_m_n = -1.0
        for _a in a:
            L_m += get_L(_a, m)  # 式(96)の一部
            L_n += get_L(_a, n)
            L_m_n += get_L(_a, m_n)
        # print(i, 'm=', m, 'L_m=', L_m, 'n=', n, 'L_n=', L_n, 'm_n=', m_n, 'L_m_n=', L_m_n)
        # 収束判定
        if abs(L_m_n) < 1.e-4:  # 式(100)
            isConverge = True
            break

        if np.sign(L_m_n) == np.sign(L_m):
            m = m_n
        else:
            n = m_n
        m_n = (m + n) / 2.0
            
    # 収束しないときには警告を表示
    if not isConverge:
        print(space_name, '形態係数パラメータが収束しませんでした。')

    return m_n

def get_L(a: float, fbd: float) -> float:
    return 0.5 * (1.0 - np.sign(1.0 - 4.0 * a / fbd) * math.sqrt(abs(1.0 - 4.0 * a / fbd)))
    

# 平均放射温度計算時の各部位表面温度の重み計算 式(101)
def get_F_mrt_i_g(area, hir):
    # 各部位表面温度の重み=面積×放射熱伝達率の比率
    total_area_hir = np.sum(area * hir)

    F_mrt_i_k = area * hir / total_area_hir

    return F_mrt_i_k


def get_r_sol_frnt() -> float:
    """室内侵入日射のうち家具に吸収される割合を計算する。

    Returns:
        室内侵入日射のうち家具に吸収される割合
    """

    return 0.5


def get_r_sol_bnd_i_jstrs(a_bnd_i_jstrs: np.ndarray, is_solar_absorbed_inside_bnd_i_jstrs: np.ndarray) -> np.ndarray:
    """室の統合された境界における室内側表面の日射吸収比率を計算する。

    Args:
        a_bnd_i_jstrs: 室iの統合された境界j*の面積, [j*]
        is_solar_absorbed_inside_bnd_i_jstrs: 室iの統合された境界j*の室内侵入日射吸収の有無, [j*]
        a_floor_i: 室iの床面積の合計, m2, [j*]

    Returns:
        室iの統合された境界j*における室内側表面の日射吸収比率
    """

    # 室内侵入日射のうち統合された境界の室内側表面に吸収される割合
    r_sol_bnds = 1.0 - get_r_sol_frnt()

    return r_sol_bnds * a_bnd_i_jstrs * is_solar_absorbed_inside_bnd_i_jstrs\
        / np.sum(a_bnd_i_jstrs * is_solar_absorbed_inside_bnd_i_jstrs)


def get_f_mrt_hum_is(
        a_bdry_i_jstrs: np.array,
        is_solar_absorbed_inside_bdry_i_jstrs: np.array
):
    """室iの在室者に対する境界j*の形態係数

    Args:
        a_bdry_i_jstrs: 室iの統合された境界j*の面積, m2, [j*]
        is_solar_absorbed_inside_bdry_i_jstrs: 室iの統合された境界j*の室内侵入日射吸収の有無, [j*]

    Returns:
        室iの在室者に対する境界j*の形態係数
    """

    # 室iの下向き部位（床）全体の形態係数
    f_mrt_hum_floor = 0.45

    # 人体に対する部位の形態係数の計算
    f_mrt_hum_is = np.zeros(len(a_bdry_i_jstrs), dtype=np.float)

    # 下向き部位（床）
    f1 = is_solar_absorbed_inside_bdry_i_jstrs
    f_mrt_hum_is[f1] = a_bdry_i_jstrs[f1] / np.sum(a_bdry_i_jstrs[f1]) * f_mrt_hum_floor

    # 床以外
    f2 = np.logical_not(is_solar_absorbed_inside_bdry_i_jstrs)
    f_mrt_hum_is[f2] = a_bdry_i_jstrs[f2] / np.sum(a_bdry_i_jstrs[f2]) * (1.0 - f_mrt_hum_floor)

    return f_mrt_hum_is


def get_q_sol_floor_i_jstrs_ns(
        q_trs_sol_i_ns: np.ndarray, a_bnd_i_jstrs: np.ndarray, is_solar_absorbed_inside_bnd_i_jstrs, a_floor_i):
    """統合された境界における室の透過日射熱取得のうちの吸収日射量を計算する。

    Args:
        q_trs_sol_i_ns: ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
        a_bnd_i_jstrs: 室iの統合された境界j*の面積, [j*]
        is_solar_absorbed_inside_bnd_i_jstrs: 室iの統合された境界j*の床室内侵入日射吸収の有無, [j*]
        a_floor_i: 室iの床面積の合計, m2, [j*]

    Returns:
        室iの統合された境界j*における室の透過日射熱取得のうちの吸収日射量, W/m2, [j*, 8760*4]
    """

    # 室iの統合された境界j*における室内側表面の日射吸収比率
    r_sol_floor_i_jstrs = get_r_sol_bnd_i_jstrs(
        a_bnd_i_jstrs=a_bnd_i_jstrs,
        is_solar_absorbed_inside_bnd_i_jstrs=is_solar_absorbed_inside_bnd_i_jstrs,
    )

    return q_trs_sol_i_ns[np.newaxis, :] * r_sol_floor_i_jstrs[:, np.newaxis] / a_bnd_i_jstrs[:, np.newaxis]


def get_q_sol_frnt_i_ns(q_trs_sol_i_ns):
    """家具の吸収日射量を計算する。

    Args:
        q_trs_sol_i_ns: ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]

    Returns:
        ステップnの室iにおける家具の吸収日射量, W, [8760*4]
    """

    # 室内侵入日射のうち家具に吸収される割合
    r_sol_frnt = get_r_sol_frnt()

    return q_trs_sol_i_ns * r_sol_frnt


# 放射暖房放射成分吸収比率 表7
def get_flr(A_i_g, A_fs_i, is_radiative_heating, is_solar_absorbed_inside):
    return (A_i_g / A_fs_i) * is_radiative_heating * is_solar_absorbed_inside
