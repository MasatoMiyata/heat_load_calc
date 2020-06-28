import numpy as np

from heat_load_calc.external.psychrometrics import get_p_vs, get_x, get_p_vs_is2
from heat_load_calc.external.global_number import get_c_air, get_rho_air


def get_v_ac_x_e_out_is(lcs_is_n, theta_r_is_npls, rac_spec):
    # Lcsは加熱が正で表される。
    # 加熱時は除湿しない。
    # 以下の取り扱いを簡単にするため（冷房負荷を正とするため）、正負を反転させる
    qs_is_n = -lcs_is_n.flatten()

    dh = qs_is_n > 1.0e-3

    vac_is_n = np.zeros_like(lcs_is_n, dtype=float).flatten()

    vac_is_n[dh] = get_vac_is_n(
        q_max=rac_spec['q_max'][dh],
        q_min=rac_spec['q_min'][dh],
        qs_is_n=qs_is_n[dh],
        v_max=rac_spec['v_max'][dh],
        v_min=rac_spec['v_min'][dh]
    )

    bf = 0.2

    x_e_out_is_n = np.zeros_like(lcs_is_n, dtype=float).flatten()

    x_e_out_is_n[dh] = get_x_e_out_is_n(
        bf=bf,
        qs_is_n=qs_is_n[dh],
        theta_r_is_npls=theta_r_is_npls[dh],
        vac_is_n2=vac_is_n[dh]
    )

    vac_is_n = vac_is_n * (1 - bf)

    return np.array(vac_is_n), np.array(x_e_out_is_n)


def get_x_e_out_is_n(bf, qs_is_n, theta_r_is_npls, vac_is_n2):

    # 熱交換器温度＝熱交換器部分吹出温度 式(113)

    theta_e_out_is_n = theta_r_is_npls - qs_is_n / (get_c_air() * get_rho_air() * vac_is_n2 * (1.0 - bf))

    x_e_out_is_n = get_x(get_p_vs_is2(theta_e_out_is_n))

    return x_e_out_is_n


def get_vac_is_n(q_max, q_min, qs_is_n, v_max, v_min):

    # TODO 最小値・最大値処理がないような気がする
    return (v_min + (v_max - v_min) / (q_max - q_min) * (qs_is_n - q_min)) / 60.0

