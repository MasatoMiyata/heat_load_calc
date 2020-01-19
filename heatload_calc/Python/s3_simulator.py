import numpy as np
from typing import List

import s4_1_sensible_heat as s41
import s4_2_latent_heat as s42

import a1_calculation_surface_temperature as a1
import apdx3_human_body as a3
import a9_rear_surface_equivalent_temperature as a9
import a13_Win_ACselect as a13
import a16_blowing_condition_rac as a16
import a18_initial_value_constants as a18
import a35_PMV as a35
from a39_global_parameters import OperationMode
from s3_space_loader import Space

import Psychrometrics as psy
from a39_global_parameters import BoundaryType


# 地盤の計算
def run_tick_groundonly(spaces: List[Space], To_n: float, Tave: float):

    for s in spaces:

        g = s.boundary_type_i_jstrs == BoundaryType.Ground  # [jstr]

        theta_srf_dsh_a_i_jstrs_npls_ms = a1.get_theta_srf_dsh_a_i_jstrs_npls_ms(
            q_srf_i_jstrs_n=s.q_srf_i_jstrs_n[g], phi_a_1_bnd_i_jstrs_ms=s.phi_a_1_bnd_i_jstrs_ms[g, :],
            r_bnd_i_jstrs_ms=s.r_bnd_i_jstrs_ms[g,:],
            theta_srf_dsh_a_i_jstrs_n_ms=s.theta_srf_dsh_a_i_jstrs_n_m[g, :])

        Ts_i_k_n = (s.phi_a_0_bnd_i_jstrs[g] * s.h_i_bnd_i_jstrs[g] * To_n
                            + np.sum(theta_srf_dsh_a_i_jstrs_npls_ms, axis=1) + Tave)\
            / (1.0 + s.phi_a_0_bnd_i_jstrs[g] * s.h_i_bnd_i_jstrs[g])

        q_srf_i_jstrs_n = s.h_i_bnd_i_jstrs[g] * (To_n - Ts_i_k_n)

        # 次の時刻のために保存する

        s.q_srf_i_jstrs_n[g] = q_srf_i_jstrs_n
        s.theta_srf_dsh_a_i_jstrs_n_m[g, :] = theta_srf_dsh_a_i_jstrs_npls_ms


# 室温、熱負荷の計算
def run_tick(spaces: List[Space], theta_o_n: float, xo_n: float, n: int):

    number_of_bdry_is = np.array([s.number_of_boundary for s in spaces])

    start_indices = []
    indices = 0
    for n_bdry in number_of_bdry_is:
        indices = indices + n_bdry
        start_indices.append(indices)
    start_indices.pop(-1)

    ac_demand_is_n = np.array([s.ac_demand[n] for s in spaces])
    m_is = np.concatenate([s.m for s in spaces])
    theta_dstrb_is_jstrs_ns = np.concatenate([s.theta_dstrb_i_jstrs_ns[:, n] for s in spaces])
    n_hum_is_n = np.array([s.n_hum_i_ns[n] for s in spaces])
    q_gen_except_hum_is_n = np.array([s.q_gen_except_hum_i_ns[n] for s in spaces])
    x_gen_except_hum_is_n = np.array([s.x_gen_except_hum_i_ns[n] for s in spaces])

    # ステップnの室iにおける室温, degree C, [i]
    theta_r_is_n = np.array([s.theta_r_i_npls for s in spaces])
    # ステップnの室iにおける絶対湿度, kg/kg(DA), [i]
    x_r_is_n = np.array([s.x_r_i_n for s in spaces])
    # ステップnの室iにおける着衣温度, degree C, [i]
    theta_cl_is_n = np.array([s.theta_cl_i_n for s in spaces])
    # ステップnの室iにおける人体周りの風速, m/s, [i]
    v_hum_is_n = np.array([s.v_hum_i_n for s in spaces])
    # ステップnの室iにおける平均放射温度, degree C, [i]
    theta_mrt_is_n = np.array([s.theta_mrt_i_n for s in spaces])
    # ステップnの室iにおける水蒸気圧, Pa
    p_a_is_n = np.array([s.p_a_i_n for s in spaces])
    operation_mode_is_n_mns = np.array([s.operation_mode for s in spaces])

    # ステップnの室iにおける人体周りの対流熱伝達率, W/m2K, [i]
    h_hum_c_is_n = a35.get_h_hum_c_is_n(theta_r_is_n=theta_r_is_n, t_cl_is_n=theta_cl_is_n, v_hum_is_n=v_hum_is_n)

    # ステップnの室iにおける人体周りの放射熱伝達率, W/m2K, [i]
    h_hum_r_is_n = a35.get_h_hum_r_is_n(theta_cl_is_n=theta_cl_is_n, theta_mrt_is_n=theta_mrt_is_n)

    # ステップnの室iにおける人体周りの総合熱伝達率, W/m2K, [i]
    h_hum_is_n = a35.get_h_hum_is_n(h_hum_r_is_n=h_hum_r_is_n, h_hum_c_is_n=h_hum_c_is_n)

    # ステップnの室iにおける作用温度, degree C, [i]
    theta_ot_is_n = s41.get_theta_ot_is_n(
        h_hum_c_is_n=h_hum_c_is_n,
        h_hum_r_is_n=h_hum_r_is_n,
        h_hum_is_n=h_hum_is_n,
        theta_r_is_n=theta_r_is_n,
        theta_mrt_is_n=theta_mrt_is_n
    )

    # ステップnの室iにおける厚着・中間着・薄着をした場合のそれぞれの着衣温度, degree C, [i]
    theta_cl_heavy_is_n, theta_cl_middle_is_n, theta_cl_light_is_n = a35.get_theta_cl_heavy_middle_light_is_n(
        theta_ot_is_n=theta_ot_is_n,
        h_hum_is_n=h_hum_is_n
    )

    # ステップnの室iにおける厚着・中間着・薄着をした場合のそれぞれのPMV, [i]
    pmv_heavy_is_n, pmv_middle_is_n, pmv_light_is_n = a35.get_pmv_heavy_middle_light_is_n(
        theta_r_is_n=theta_r_is_n,
        theta_cl_heavy_is_n=theta_cl_heavy_is_n,
        theta_cl_middle_is_n=theta_cl_middle_is_n,
        theta_cl_light_is_n=theta_cl_light_is_n,
        p_a_is_n=p_a_is_n,
        h_hum_is_n=h_hum_is_n,
        theta_ot_is_n=theta_ot_is_n
    )

    # ステップnの室iにおける運転モード, [i]
    operation_mode_is_n = a13.get_operation_mode_is_n(
        ac_demand_is_n=ac_demand_is_n,
        operation_mode_is_n_mns=operation_mode_is_n_mns,
        pmv_heavy_is_n=pmv_heavy_is_n,
        pmv_middle_is_n=pmv_middle_is_n,
        pmv_light_is_n=pmv_light_is_n
    )

    # ステップnの室iにおけるClo値, [i]
    clo_is_n = a13.get_clo_is_n(operation_mode_is_n=operation_mode_is_n)

    # ステップnの室iにおける着衣表面温度, degree C, [i]
    theta_cl_is_n = a13.get_theta_cl_is_n(
        operation_mode_is_n=operation_mode_is_n,
        theta_cl_heavy_is_n=theta_cl_heavy_is_n,
        theta_cl_middle_is_n=theta_cl_middle_is_n,
        theta_cl_light_is_n=theta_cl_light_is_n
    )

    # ステップnの室iにおける目標作用温度, degree C, [i]
    OTsets = a13.get_theta_ot_target_is_n(
        p_a_is_n=p_a_is_n,
        h_hum_is_n=h_hum_is_n,
        operation_mode_is_n=operation_mode_is_n,
        clo_is_n=clo_is_n,
        theta_cl_is_n=theta_cl_is_n
    )

    # ステップnの室iの集約された境界j*における裏面温度, degree C, [j*]
    theta_rear_is_jstrs_n = a9.get_theta_rear_i_jstrs_n(
        theta_r_is_n=theta_r_is_n,
        m=m_is,
        theta_dstrb_i_jstrs_n=theta_dstrb_is_jstrs_ns
    )

    # ステップnの室iにおける人体発熱, W, [i]
    q_hum_is_n = a3.get_q_hum_i_n(theta_r_i_n=theta_r_is_n, n_hum_i_n=n_hum_is_n)

    # ステップnの室iにおける人体発湿, kg/s, [i]
    x_hum_is_n = a3.get_x_hum_i_n(theta_r_i_n=theta_r_is_n, n_hum_i_n=n_hum_is_n)

    # ステップnの室iにおける内部発熱, W
    q_gen_is_n = q_gen_except_hum_is_n + q_hum_is_n

    # ステップnの室iにおける内部発湿, kg/s
    x_gen_is_n = x_gen_except_hum_is_n + x_hum_is_n

    for i, s in enumerate(spaces):

        # ステップnの室iにおける内部発熱, W
#        q_gen_i_n = s.q_gen_except_hum_i_ns[n] + q_hum_is_n[i]
        q_gen_i_n = q_gen_is_n[i]

        # ステップnの室iにおける内部発湿, kg/s
#        x_gen_i_n = s.x_gen_except_hum_i_ns[n] + x_hum_is_n[i]
        x_gen_i_n = x_gen_is_n[i]

        # ステップnの室iにおける室温, degree C
        theta_r_i_n = theta_r_is_n[i]

        theta_rear_i_jstrs_n = np.split(theta_rear_is_jstrs_n, start_indices)[i]

        theta_srf_dsh_a_i_jstrs_n_m = s.theta_srf_dsh_a_i_jstrs_n_m
        theta_srf_dsh_t_i_jstrs_n_m = s.theta_srf_dsh_t_i_jstrs_n_m
        old_theta_frnt_i = s.old_theta_frnt_i
        q_srf_i_jstrs_n = s.q_srf_i_jstrs_n
        xf_i_npls = s.xf_i_npls
        x_r_i_n = s.x_r_i_n
        v_hum_i_n = s.v_hum_i_n

        operation_mode_i_n = operation_mode_is_n[i]

        OTset = OTsets[i]

        # TODO: すきま風量未実装につき、とりあえず０とする
        # すきま風量を決めるにあたってどういった変数が必要なのかを決めること。
        # TODO: 単位は m3/s とすること。
        v_reak_i_n = 0.0

        # ステップn+1の室iの統合された境界j*における項別公比法の項mの吸熱応答に関する表面温度, degree C, [jstrs, 12]
        theta_srf_dsh_a_i_jstrs_npls_ms = a1.get_theta_srf_dsh_a_i_jstrs_npls_ms(
            q_srf_i_jstrs_n=q_srf_i_jstrs_n, phi_a_1_bnd_i_jstrs_ms=s.phi_a_1_bnd_i_jstrs_ms,
            r_bnd_i_jstrs_ms=s.r_bnd_i_jstrs_ms, theta_srf_dsh_a_i_jstrs_n_ms=theta_srf_dsh_a_i_jstrs_n_m)

        # ステップn+1の室iの統合された境界j*における項別公比法の項mの貫流応答に関する表面温度, degree C, [jstrs, 12]
        theta_srf_dsh_t_i_jstrs_npls_ms = a1.get_theta_srf_dsh_t_i_jstrs_npls_ms(
            theta_rear_i_jstrs_n=theta_rear_i_jstrs_n, phi_t_1_bnd_i_jstrs_ms=s.phi_t_1_bnd_i_jstrs_ms,
            r_bnd_i_jstrs_ms=s.r_bnd_i_jstrs_ms, theta_srf_dsh_t_i_jstrs_n_m=theta_srf_dsh_t_i_jstrs_n_m)

        # ステップn+1の室iの統合された境界j*における係数CVL, degree C, [j*]
        cvl_i_jstrs_npls = a1.get_cvl_i_jstrs_npls(
            theta_srf_dsh_t_i_jstrs_npls_ms=theta_srf_dsh_t_i_jstrs_npls_ms,
            theta_srf_dsh_a_i_jstrs_npls_ms=theta_srf_dsh_a_i_jstrs_npls_ms)

        # ステップn+1の室iの統合された境界j*における係数CRX, degree C, [j*]
        crx_i_jstrs_npls = a1.get_crx_i_jstrs_npls(
            phi_a_0_bnd_i_jstrs=s.phi_a_0_bnd_i_jstrs,
            q_sol_floor_i_jstrs_n=s.q_sol_srf_i_jstrs_ns[:, n],
            phi_t_0_bnd_i_jstrs=s.phi_t_0_bnd_i_jstrs,
            theta_rear_i_jstrs_n=theta_rear_i_jstrs_n)

        # ステップn+1の室iの断熱された境界j*における係数WSC, degree C, [j*]
        wsc_i_jstrs_npls = a1.get_wsc_i_jstrs_npls(ivs_x_i=s.ivs_x_i, crx_i_jstrs_npls=crx_i_jstrs_npls)

        # ステップn+1の室iの断熱された境界j*における係数WSV, degree C, [j*]
        wsv_i_jstrs_npls = a1.get_wsv_i_jstrs_npls(ivs_x_i=s.ivs_x_i, cvl_i_jstrs_npls=cvl_i_jstrs_npls)

        # ステップnの室iにおける隣室i*からの室間換気の空気温度, degree C, [i*]
        theta_r_int_vent_i_istrs_n = np.array([theta_r_is_n[x] for x in s.next_room_idxs_i])

        # ステップnの室iにおける隣室i*からの室間換気の絶対湿度, kg/kgDA, [i*]
        x_r_int_vent_i_istrs_n = np.array([x_r_is_n[x] for x in s.next_room_idxs_i])

        # ステップnの室iにおける係数BRC
        brc_i_n = s41.get_brc_i_n(
            c_room_i=s.c_room_i, deta_t=900.0, theta_r_i_n=theta_r_i_n, h_c_bnd_i_jstrs=s.h_c_bnd_i_jstrs,
            a_bnd_i_jstrs=s.a_bnd_i_jstrs, wsc_i_jstrs_npls=wsc_i_jstrs_npls, wsv_i_jstrs_npls=wsv_i_jstrs_npls,
            v_mec_vent_i_n=s.v_mec_vent_i_ns[n], v_reak_i_n=v_reak_i_n, v_int_vent_i_istrs=s.v_int_vent_i_istrs,
            v_ntrl_vent_i=s.v_ntrl_vent_i, theta_o_n=theta_o_n, theta_r_int_vent_i_istrs_n=theta_r_int_vent_i_istrs_n,
            q_gen_i_n=q_gen_i_n, c_cap_frnt_i=s.c_cap_frnt_i, k_frnt_i=s.k_frnt_i, q_sol_frnt_i_n=s.q_sol_frnt_i_ns[n],
            theta_frnt_i_n=old_theta_frnt_i, operation_mode=operation_mode_i_n)

        brm_non_ntrv_i_n = s.BRMnoncv_i[n]
        brm_ntrv_i_n = brm_non_ntrv_i_n + a18.get_c_air() * a18.get_rho_air() * s.v_ntrl_vent_i
        brm_i_n = brm_ntrv_i_n if operation_mode_i_n == OperationMode.STOP_OPEN else brm_non_ntrv_i_n

        # OT計算用の係数補正
        BRMot, BRCot, BRLot, Xot, XLr, XC = s41.calc_OT_coeff(
            brm_i_n, brc_i_n, s.BRL_i[n], s.WSR_i_k, s.WSB_i_k, wsc_i_jstrs_npls, wsv_i_jstrs_npls,s.Fot_i_g, s.kc_i, s.kr_i)

        # ********** 空調設定温度の計算 **********

        ot_i_n, lcs_i_n, lrs_i_n = s41.calc_next_step(
            s.is_radiative_heating, BRCot, BRMot, BRLot, OTset, s.Lrcap_i, operation_mode_i_n)

        # ********** 室温 Tr、家具温度 Tfun、表面温度 Ts_i_k_n、室内表面熱流 q の計算 **********

        # 自然室温 Tr を計算 式(14)
        theta_r_i_npls = s41.get_Tr_i_n(ot_i_n, lrs_i_n, Xot, XLr, XC)

        # 家具の温度 Tfun を計算 式(15)
        theta_frnt_i_n = s41.get_Tfun_i_n(s.c_cap_frnt_i, old_theta_frnt_i, s.k_frnt_i, theta_r_i_npls, s.q_sol_frnt_i_ns[n])

        # 表面温度の計算 式(23)
        Ts_i_k_n = a1.get_surface_temperature(s.WSR_i_k, s.WSB_i_k, wsc_i_jstrs_npls, wsv_i_jstrs_npls, theta_r_i_npls, lrs_i_n)

        # MRT_i_n、AST、平均放射温度の計算
        theta_mrt_i_n_pls = get_MRT(s.Fot_i_g, Ts_i_k_n)

        # 室内表面熱流の計算 式(28)
        Qc, Qr, q_srf_i_jstrs_n = a1.calc_qi(
            s.h_c_bnd_i_jstrs, s.a_bnd_i_jstrs, s.h_r_bnd_i_jstrs, s.q_sol_srf_i_jstrs_ns[:, n], s.flr_i_k,
            Ts_i_k_n, theta_r_i_npls, s.F_mrt_i_g, lrs_i_n, s.Beta_i)

        # ********** 室湿度 xr、除湿量 G_hum、湿加湿熱量 Ll の計算 **********

        # 式(17)
        BRMX_pre = s42.get_BRMX(
            v_reak_i_n=v_reak_i_n,
            Gf=s.Gf_i,
            Cx=s.Cx_i,
            volume=s.v_room_cap_i,
            v_int_vent_i_istrs=s.v_int_vent_i_istrs,
            v_mec_vent_i_n=s.v_mec_vent_i_ns[n]
        )

        # 式(18)
        BRXC_pre = s42.get_BRXC(
            v_reak_i_n=v_reak_i_n,
            Gf=s.Gf_i,
            Cx=s.Cx_i,
            volume=s.v_room_cap_i,
            v_int_vent_i_istrs=s.v_int_vent_i_istrs,
            xr_next_i_j_nm1=x_r_int_vent_i_istrs_n,
            xr_i_nm1=x_r_i_n,
            xf_i_nm1=xf_i_npls,
            Lin=x_gen_i_n,
            xo=xo_n,
            v_mec_vent_i_n=s.v_mec_vent_i_ns[n]
        )

        # ==== ルームエアコン吹出絶対湿度の計算 ====

        # バイパスファクターBF 式(114)
        BF = a16.get_BF()

        # i室のn時点におけるエアコンの風量[m3/s]
        # 空調の熱交換部飽和絶対湿度の計算
        Vac_n, xeout_i_n = \
            a16.calcVac_xeout(lcs_i_n, s.Vmin_i, s.Vmax_i, s.qmin_c_i, s.qmax_c_i, theta_r_i_npls, BF, operation_mode_i_n)

        # 空調機除湿の項 式(20)より
        RhoVac = get_RhoVac(Vac_n, BF)

        # 室絶対湿度[kg/kg(DA)]の計算
        BRMX_base = BRMX_pre + RhoVac
        BRXC_base = BRXC_pre + RhoVac * xeout_i_n

        # 室絶対湿度の計算 式(16)
        xr_base = s42.get_xr(BRXC_base, BRMX_base)

        # 補正前の加湿量の計算 [ks/s] 式(20)
        Ghum_base = s42.get_Ghum(RhoVac, xeout_i_n, xr_base)

        # 除湿量が負値(加湿量が正)になった場合にはルームエアコン風量V_(ac,n)をゼロとして再度室湿度を計算する
        if Ghum_base > 0.0:
            Ghum_i_n = 0.0
            x_r_i_n_pls = s42.get_xr(BRXC_pre, BRMX_pre)
        else:
            Ghum_i_n = Ghum_base
            x_r_i_n_pls = xr_base

        # 除湿量から室加湿熱量を計算 式(21)
        Lcl_i_n = get_Lcl(Ghum_i_n)

        # 当面は放射空調の潜熱は0
        Lrl_i_n = get_Lrl()

        # ステップn+1の室iにおける飽和水蒸気圧, Pa
        p_vs_i_n_pls = psy.get_p_vs(theta_r_i_npls)

        # ステップn+1の室iにおける水蒸気圧, Pa
        p_v_i_n_pls = psy.get_p_v(x_r_i_n_pls)

        # ステップn+1の室iにおける相対湿度, %
        rh_i_n_pls = psy.get_h(p_v=p_v_i_n_pls, p_vs=p_vs_i_n_pls)

        # ********** 備品類の絶対湿度 xf の計算 **********

        # 備品類の絶対湿度の計算
        xf_i_n = s42.get_xf(s.Gf_i, xf_i_npls, s.Cx_i, x_r_i_n_pls)
        Qfunl_i_n = s42.get_Qfunl(s.Cx_i, x_r_i_n_pls, xf_i_n)

        t_cl_i_n_pls = a35.get_t_cl_i_n(clo_i_n=clo_is_n[i], ot_i_n=ot_i_n, h_a_i_n=h_hum_is_n[i])

        if operation_mode_i_n == OperationMode.HEATING:
            if s.is_radiative_heating:
                v_hum_i_n_pls = 0.0
            else:
                v_hum_i_n_pls = 0.2
        elif operation_mode_i_n == OperationMode.COOLING:
            if s.is_radiative_cooling:
                v_hum_i_n_pls = 0.0
            else:
                v_hum_i_n_pls = 0.2
        elif operation_mode_i_n == OperationMode.STOP_CLOSE:
            v_hum_i_n_pls = 0.0
        elif operation_mode_i_n == OperationMode.STOP_OPEN:
            v_hum_i_n_pls = 0.1

        # 前の時刻からの値
        s.theta_srf_dsh_a_i_jstrs_n_m = theta_srf_dsh_a_i_jstrs_npls_ms
        s.theta_srf_dsh_t_i_jstrs_n_m = theta_srf_dsh_t_i_jstrs_npls_ms
        s.operation_mode = operation_mode_i_n
        s.old_theta_frnt_i = theta_frnt_i_n
        s.theta_r_i_npls = theta_r_i_npls
        s.q_srf_i_jstrs_n = q_srf_i_jstrs_n
        s.xf_i_npls = xf_i_n
        s.x_r_i_n = x_r_i_n_pls
        s.theta_mrt_i_n = theta_mrt_i_n_pls
        s.v_hum_i_n = v_hum_i_n_pls
        s.theta_cl_i_n = t_cl_i_n_pls
        s.p_a_i_n = p_v_i_n_pls

        # ロギング
        s.logger.theta_r_i_ns[n] = theta_r_i_npls
        s.logger.theta_rear_i_jstrs_ns[:, n] = theta_rear_i_jstrs_n
        s.logger.q_hum_i_ns[n] = q_hum_is_n[i]
        s.logger.x_hum_i_ns[n] = x_hum_is_n[i]
        s.logger.operation_mode[n] = operation_mode_i_n
        s.logger.theta_frnt_i_ns[n] = theta_frnt_i_n
        s.logger.OT_i_n[n] = ot_i_n
        s.logger.Qfuns_i_n[n] = s41.get_Qfuns(s.k_frnt_i, theta_r_i_npls, theta_frnt_i_n)
        s.logger.Qc[:, n] = Qc
        s.logger.Qr[:, n] = Qr
        s.logger.Ts_i_k_n[:, n] = Ts_i_k_n
        s.logger.MRT_i_n[n] = theta_mrt_i_n_pls
        # 室内側等価温度の計算 式(29)
        s.logger.Tei_i_k_n[:, n] = a1.calc_Tei(
            s.h_c_bnd_i_jstrs, s.h_i_bnd_i_jstrs, s.h_r_bnd_i_jstrs, s.q_sol_srf_i_jstrs_ns[:, n], s.flr_i_k,
            s.a_bnd_i_jstrs, theta_r_i_npls, s.F_mrt_i_g, Ts_i_k_n, lrs_i_n, s.Beta_i)
        s.logger.Lrs_i_n[n] = lrs_i_n
        s.logger.Lcs_i_n[n] = lcs_i_n
        s.logger.Lcl_i_n[n] = Lcl_i_n
        s.logger.xf_i_n[n] = xf_i_n
        s.logger.Qfunl_i_n[n] = Qfunl_i_n
        s.logger.Vel_i_n[n] = v_hum_i_n
        s.logger.Clo_i_n[n] = clo_is_n[i]
        s.logger.RH_i_n[n] = rh_i_n_pls
        s.logger.x_r_i_ns[n] = x_r_i_n_pls


# MRTの計算
def get_MRT(fot, Ts) -> float:
    return float(np.sum(fot * Ts))


# ASTの計算
def get_AST(area, Ts, Atotal):
    return np.sum(area * Ts / Atotal)


# 当面は放射空調の潜熱は0
def get_Lrl():
    return 0.0


# 除湿量から室加湿熱量を計算 式(21)
def get_Lcl(Ghum: float):
    """除湿量から室加湿熱量を計算

    :param Ghum: i室のn時点における除湿量 [ks/s]
    :return:
    """
    conra = a18.get_conra()
    return Ghum * conra


# 式(20)のうちの一部
def get_RhoVac(Vac: float, BF: float):
    rhoa = a18.get_rho_air()
    return rhoa * Vac * (1.0 - BF)
