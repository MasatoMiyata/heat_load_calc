import numpy as np

from heat_load_calc.core.pre_calc_parameters import PreCalcParametersGround
from heat_load_calc.core.conditions import GroundConditions


# 地盤の計算
def run_tick(gc_n: GroundConditions, ss: PreCalcParametersGround, n: int):

    h_i_js = ss.h_r_js + ss.h_c_js

    theta_dsh_srf_a_js_ms_npls = ss.phi_a1_js_ms * gc_n.q_srf_js_n + ss.r_js_ms * gc_n.theta_dsh_srf_a_js_ms_n

    theta_s_js_npls = (ss.phi_a0_js * h_i_js * ss.theta_o_ns[n]
        + np.sum(theta_dsh_srf_a_js_ms_npls, axis=1, keepdims=True) + ss.theta_o_ave) \
        / (1.0 + ss.phi_a0_js * h_i_js)

    # TODO: ここの外気温度は n+1 を使用する必要があるのではないか。
    q_srf_js_n = h_i_js * (ss.theta_o_ns[n] - theta_s_js_npls)

    return GroundConditions(
        theta_dsh_srf_a_js_ms_n=theta_dsh_srf_a_js_ms_npls,
        q_srf_js_n=q_srf_js_n,
    )


