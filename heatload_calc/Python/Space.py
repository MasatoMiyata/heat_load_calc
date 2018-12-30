import numpy as np
from typing import List
from Weather import enmWeatherComponent

import Surface
from Surface import *
import NextVent
from NextVent import *

import SeasonalValue
from SeasonalValue import SeasonalValue

from common import conca, conrowa


# # 室温・熱負荷を計算するクラス

# ## １）室内部位に関連するクラス

# 室内部位に関する情報を保持します。
# 
# - is_skin:      外皮フラグ, 外皮の場合True
# - boundary:  方位・隣室名, string
# - unsteady:  非定常フラグ, 非定常壁体の場合True
# - name:      壁体・開口部名称, string
# - area:      面積, m2
# - sunbreak:  ひさし名称, string
# - flr:       放射暖房吸収比率, －
# - fot:       人体に対する形態係数, －

# ## ４）空間に関するクラス

# 空間に関する情報を保持します。
# 
# - roomname:      室区分, string
# - roomdiv:       室名称, string
# - HeatCcap:      最大暖房能力（対流）[W]
# - HeatRcap:      最大暖房能力（放射）[W]
# - CoolCcap:      最大冷房能力（対流）[W]
# - CoolRcap:      最大冷房能力（放射）[W]
# - Vol:           室気積, m3
# - Fnt:           家具熱容量, kJ/m3K
# - Vent:          計画換気量, m3/h
# - Inf:           すきま風量[Season]（list型、暖房・中間期・冷房の順）, m3/h
# - CrossVentRoom: 通風計算対象室, False
# - RadHeat:       放射暖房対象室フラグ, True
# - Betat:         放射暖房対流比率, －
# - RoomtoRoomVents:      室間換気量（list型、暖房・中間期・冷房、風上室名称）, m3/h
# - d:             室内部位に関連するクラス, Surface

# 空間に関する情報の保持
class Space:
    FsolFlr = 0.5  # 床の日射吸収比率

    # 初期化
    def __init__(self, Gdata, roomname,
                 HeatCcap, HeatRcap, CoolCcap, Vol, Fnt, Vent, Inf, CrossVentRoom,
                 RadHeat, Beta, RoomtoRoomVents, Surfaces: List[dict]):
        """
        :param Gdata:
        :param ExsrfMng:
        :param SunbrkMng:
        :param roomname: 室用途（主たる居室、その他居室、非居室）
        :param HeatCcap:
        :param HeatRcap:
        :param CoolCcap:
        :param Vol:
        :param Fnt:
        :param Vent:
        :param Inf:
        :param CrossVentRoom:
        :param RadHeat:
        :param Beta:
        :param RoomtoRoomVents:
        :param Surfaces:
        """
        self.name = roomname  # 室用途（主たる居室、その他居室、非居室）
        self.__AnnualLoadcC = 0.0  # 年間冷房熱負荷（対流成分）
        self.__AnnualLoadcH = 0.0  # 年間暖房熱負荷（対流成分）
        self.__AnnualLoadrC = 0.0  # 年間冷房熱負荷（放射成分）
        self.__AnnualLoadrH = 0.0  # 年間暖房熱負荷（放射成分）
        self.Tr = 15.0  # 室温の初期化
        self.__oldTr = 15.0  # 前時刻の室温の初期化
        self.__kc = 0.5  # 人体表面の熱伝達率の対流成分比率
        self.__kr = 0.5  # 人体表面の熱伝達率の放射成分比率
        self.__HeatCcap = 0.0
        if HeatCcap is not None:
            self.__HeatCcap = float(HeatCcap)  # 最大暖房能力（対流）
        self.__HeatRcap = 0.0
        if HeatRcap is not None:
            self.__HeatRcap = float(HeatRcap)  # 最大暖房能力（放射）
        self.__CoolCcap = 0.0
        if CoolCcap is not None:
            self.__CoolCcap = float(CoolCcap)  # 最大冷房能力（対流）
        # self.__CoolRcap = CoolRcap                #最大冷房能力（放射）
        self.__Vol = float(Vol)  # 室気積
        self.__Fnt = float(Fnt)  # 家具熱容量
        # print(self.__Vol, self.__Fnt)
        # print(self.__Vol * 1.2 * 1005.0)
        # print(self.__Vol * self.__Fnt * 1000.0)
        # print('aaaaa')
        # print('Hcap=', self.__Hcap)
        # 室空気の熱容量（家具を含む）
        self.__Hcap = self.__Vol * 1.2 * 1005.0 + self.__Vol * self.__Fnt * 1000.0
        # print(self.__Hcap)
        self.__Vent = SeasonalValue(Vent['winter'], Vent['inter'], Vent['summer'])
        # self.__Vent = Vent                        #計画換気量
        # print(self.__Vent)
        # self.__Inf = Inf                          #すきま風量
        self.__Inf = SeasonalValue(Inf['winter'], Inf['inter'], Inf['summer'])
        self.__CrossVentRoom = CrossVentRoom  # 通風対象室フラグ
        self.__RadHeat = RadHeat  # 放射暖房設置フラグ
        self.__Beta = float(Beta)  # 放射暖房対流比率
        # self.__oldNextRoom = []
        # self.__NextVent = []

        # 内部発熱の初期化
        # 機器顕熱
        self.__Appl = 0.0
        # 照明
        self.__Light = 0.0
        # 人体顕熱
        self.__Human = 0.0
        # 内部発熱合計
        self.__Hn = 0.0

        # 室透過日射熱取得の初期化
        self.Qgt = 0.0

        # 室間換気量クラスの構築
        self.__RoomtoRoomVent = []
        # prevroomname = ''
        # winter_vent = 0.0
        # inter_vent = 0.0
        # summer_vent = 0.0
        for room_vent in RoomtoRoomVents:
            self.__RoomtoRoomVent.append(NextVent(room_vent['Windward_roomname'], \
                                                  room_vent['winter'], room_vent['inter'], room_vent['summer']))
        self.__Nsurf = 0  # 部位の数
        self.surfaces = []

        # 部位表面
        total_Fot = 0.0
        for d_surface in Surfaces:
            self.surfaces.append(Surface(d_surface, Gdata))
            # Fot総計のチェック
            total_Fot += d_surface['fot']
        if abs(total_Fot - 1.0) > 0.001:
            print(self.name, 'total_Fot=', total_Fot)

        self.__Nsurf = len(self.surfaces)

        # 面対面の形態係数の計算
        self.__Atotal = 0.0
        self.__TotalAF = 0.0

        # print('合計面積1=', self.__Atotal)
        # 合計面積の計算
        for surface in self.surfaces:
            self.__Atotal += surface.area
            # 合計床面積の計算
            if surface.Floor == True:
                self.__TotalAF += surface.area

        # print('合計表面積=', self.__Atotal)
        # 形態係数の計算（面積比）
        i = 0
        for surface in self.surfaces:
            j = 0
            # 形態係数収録用メモリの確保
            for nxtsurface in self.surfaces:
                surface.setFF(nxtsurface.area / self.__Atotal)
                # print(i, j, surface.FF(j))
                j += 1
            i += 1

        # 透過日射の室内部位表面吸収比率の計算
        # 床に集中的に吸収させ、残りは表面積で案分
        # 床の1次入射比率
        FsolFlr = Gdata.FsolFlr
        TotalR = 0.0
        # 床を除いた室内合計表面積の計算
        temp = self.__Atotal - self.__TotalAF

        for surface in self.surfaces:
            # 床の室内部位表面吸収比率の設定
            if surface.Floor == True:
                SolR = FsolFlr * surface.area / self.__TotalAF
            # 床以外は面積案分
            else:
                # 室に床がある場合
                if self.__TotalAF > 0.0:
                    SolR = surface.area / temp * (1. - FsolFlr)
                # 床がない場合
                else:
                    SolR = surface.area / temp
            surface.SolR = SolR
            # 室内部位表面吸収比率の合計値（チェック用）
            TotalR += SolR
        # 日射吸収率の合計値のチェック
        if abs(TotalR - 1.0) > 0.00001:
            print(self.name, '日射吸収比率合計値エラー', TotalR)

        # 放射収支計算のための行列準備
        # 行列の準備と初期化
        # [AX]
        self.__matAXd = [[0.0 for i in range(self.__Nsurf)] for j in range(self.__Nsurf)]
        # {FIA}
        self.__matFIA = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        # {CRX}
        self.__matCRX = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        # {CVL}
        self.__matCVL = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        # {FLB}
        self.__matFLB = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        # {WSC}
        self.__matWSC = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        # {WSR}
        # self.__matWSR = [ [ 0.0 for i in range(1) ] for j in range(self.__Nsurf) ]
        # {WSV}
        self.__matWSV = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        # {WSB}
        # self.__matWSB = [ [ 0.0 for i in range(1) ] for j in range(self.__Nsurf) ]

        # print('FIA[len]=', len(self.__matFIA))
        i = 0
        for surface in self.surfaces:
            # matFIAの作成
            self.__matFIA[i][0] = surface.RFA0 * surface.hic
            # print('i=', i, 'FIA=', self.__matFIA[i][0])
            # FLB=φA0×flr×(1-Beta)
            self.__matFLB[i][0] = surface.RFA0 * surface.flr * (1. - self.__Beta) / surface.area

            # 放射計算のマトリックス作成
            for j in range(self.__Nsurf):
                # print('i=', i, 'j=', j)
                # print('FIA=', self.__matFIA[0][i])
                # print('FF=', surface.FF(j))
                # 対角要素
                if i == j:
                    self.__matAXd[i][j] = 1. + surface.RFA0 * surface.hi \
                                          - surface.RFA0 * surface.hir * surface.FF(j)
                # 対角要素以外
                else:
                    self.__matAXd[i][j] = - surface.RFA0 * surface.hir * surface.FF(j)
            # print('放射計算マトリックス作成完了')
            i += 1

        # print('[Matrix AXd]')
        # print(self.__matAXd)

        # 逆行列の計算
        self.__matAX = np.linalg.inv(self.__matAXd)
        # print('[Matrix AX  inverse Matrix AXd]')
        # print(self.__matAX)
        # {WSR}の計算
        self.__matWSR = np.dot(self.__matAX, self.__matFIA)
        # print('[Matrix FIA]')
        # print(self.__matFIA)
        # print('[Matrix WSR]')
        # print(self.__matWSR)
        # {WSB}の計算
        self.__matWSB = np.dot(self.__matAX, self.__matFLB)
        # print('[Matrix FLB]')
        # print(self.__matFLB)
        # print('[Matrix WSB]')
        # print(self.__matWSB)

    # 室温を返す
    @property
    def oldTr(self):
        return self.__oldTr

    # 室温、熱負荷の計算
    def calcHload(self, Gdata, spaces, dtmNow, defSolpos, Schedule, Weather):
        # 室間換気の風上室温をアップデート
        for roomvent in self.__RoomtoRoomVent:
            windward_roomname = roomvent.Windward_roomname
            oldTr = spaces[windward_roomname].oldTr
            roomvent.update_oldTr(oldTr)

        # 外皮の傾斜面日射量の計算
        Idn = Weather.WeaData(enmWeatherComponent.Idn, dtmNow)
        Isky = Weather.WeaData(enmWeatherComponent.Isky, dtmNow)
        for surface in self.surfaces:
            if surface.is_skin:
                surface.update_slope_sol(defSolpos, Idn, Isky)

        # 庇の日影面積率計算
        for surface in self.surfaces:
            # 庇がある場合のみ
            if surface.has_sunbrk:
                # 日影面積率の計算
                surface.update_Fsdw(defSolpos)
                # print(surface.Fsdw)

        # 透過日射熱取得の初期化
        self.Qgt = 0.0

        # 透過日射吸収日射の計算
        for surface in self.surfaces:
            if surface.is_window and surface.is_skin:
                surface.update_Qgt_Qga()
                self.Qgt += surface.Qgt

        # 相当外気温度の計算
        Ta = Weather.WeaData(enmWeatherComponent.Ta, dtmNow)
        RN = Weather.WeaData(enmWeatherComponent.RN, dtmNow)
        AnnualTave = Weather.AnnualTave()
        for surface in self.surfaces:
            surface.calcTeo(Ta, RN, self.__oldTr, AnnualTave, spaces)
            # print(surface.name, Ta, RN, self.__oldTr, surface.Teo)

        # 内部発熱の計算（すべて対流成分とする）
        self.__Appl = Schedule.Appl(self.name, '顕熱', dtmNow)
        self.__Light = Schedule.Light(self.name, dtmNow)
        self.__Human = Schedule.Nresi(self.name, dtmNow) \
                       * (63.0 - 4.0 * (self.__oldTr - 24.0))
        self.__Hn = self.__Appl + self.__Light + self.__Human
        # print(self.name, self.__Appl, self.__Light, self.__Human)

        # 室内表面の吸収日射量
        for surface in self.surfaces:
            surface.update_RSsol(self.Qgt)

        # 流入外気風量の計算
        # 計画換気・すきま風量
        season = Schedule.Season(dtmNow)
        if season == '暖房':
            self.__Ventset = self.__Vent.winter
            self.__Infset = self.__Inf.winter
        elif season == '中間':
            self.__Ventset = self.__Vent.inter
            self.__Infset = self.__Inf.inter
        elif season == '冷房':
            self.__Ventset = self.__Vent.summer
            self.__Infset = self.__Inf.summer
        # 局所換気量
        self.__LocalVent = Schedule.LocalVent(self.name, dtmNow)

        # 空調設定温度の取得
        self.__Tset = Schedule.ACSet(self.name, '温度', dtmNow)
        # 空調発停信号
        self.__SW = 0
        if season == '暖房' and self.__Tset > 0.0:
            self.__SW = 1
        elif season == '冷房' and self.__Tset > 0.0:
            self.__SW = -1

        # 室温・熱負荷計算のための係数の計算
        # BRM・BRLの初期化
        self.__BRM = 0.0
        self.__BRL = self.__Beta
        RMdT = self.__Hcap / Gdata.DTime
        self.__BRM += RMdT
        # BRLの計算
        i = 0
        for surface in self.surfaces:
            # 室内対流熱伝達率×面積[W/K]
            AF0 = surface.area * surface.hic
            temp = AF0 * (1.0 - self.__matWSR[i][0])
            # hc×A×(1-WSR)の積算
            self.__BRM += temp
            # BRLの計算
            self.__BRL += AF0 * self.__matWSB[i][0]
            i += 1

        # 外気導入項の計算
        temp = conca * conrowa * \
               (self.__Ventset + self.__Infset + self.__LocalVent) / 3600.0
        self.__BRM += temp
        # 室間換気
        for room_vent in self.__RoomtoRoomVent:
            nextvent = room_vent.next_vent(season)
            temp = conca * conrowa * nextvent / 3600.0
            self.__BRM += temp

        # 定数項の計算
        self.__BRC = 0.0
        # {WSC}、{CRX}の初期化
        self.__matWSC = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        self.__matCRX = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]

        # {CRX}の作成
        i = 0
        for surface in self.surfaces:
            self.__matCRX[i][0] = surface.RFT0 * surface.Teo \
                                  + surface.RSsol * surface.RFA0
            i += 1

        # {WSC}=[XA]*{CRX}
        self.__matWSC = np.dot(self.__matAX, self.__matCRX)
        # {BRC}の計算
        i = 0
        for surface in self.surfaces:
            NowQw = self.__matWSC[i][0] * surface.area * surface.hic
            self.__BRC += NowQw
            i += 1

        # 外気流入風（換気＋すきま風）
        temp = conca * conrowa * \
               (self.__Ventset + self.__Infset + self.__LocalVent) \
               * Weather.WeaData(enmWeatherComponent.Ta, dtmNow) / 3600.0
        self.__BRC += temp

        # 室間換気流入風
        for room_vent in self.__RoomtoRoomVent:
            nextvent = room_vent.next_vent(season)
            temp = conca * conrowa * nextvent \
                   * room_vent.oldTr / 3600.0
            # print(self.name, room_vent.Windward_roomname(), nextvent, room_vent.oldTr())
            self.__BRC += temp
        # RM/Δt*oldTrの項
        temp = self.__Hcap / Gdata.DTime * self.__oldTr
        self.__BRC += temp

        # {WSV}、{CVL}の初期化
        self.__matWSV = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        self.__matCVL = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]

        # 畳み込み演算
        i = 0
        for surface in self.surfaces:
            self.__matCVL[i][0] = surface.convolution()
            i += 1

        # {WSV}=[XA]*{CVL}
        self.__matWSV = np.dot(self.__matAX, self.__matCVL)
        # 畳み込み後の室内表面温度の計算
        i = 0
        for surface in self.surfaces:
            temp = surface.area * surface.hic * self.__matWSV[i][0]

            self.__BRC += temp
            i += 1

        # 定数項への内部発熱の加算
        self.__BRC += self.__Hn

        # OT制御の換算係数の計算
        if Gdata.OTset == True:
            self.__Xot = 0.0
            self.__XLr = 0.0
            self.__XC = 0.0
            temp = 0.0
            XLr = 0.0
            XC = 0.0
            i = 0
            for surface in self.surfaces:
                temp += surface.fot() * self.__matWSR[i][0]
                XLr += surface.fot() * self.__matWSB[i][0]
                XC += surface.fot() * (self.__matWSC[i][0] + self.__matWSV[i][0])
                i += 1

            temp = self.__kc + self.__kr * temp
            self.__Xot = 1.0 / temp
            self.__XLr = self.__kr * XLr / temp
            self.__XC = self.__kr * XC / temp
            self.__BRMot = self.__BRM * self.__Xot
            self.__BRCot = self.__BRC + self.__BRM * self.__XC
            self.__BRLot = self.__BRL + self.__BRM * self.__XLr

        #### 通風計算はここに入れる（今回は未実装）

        # 室温・熱負荷の計算
        Hcap = 0.0
        if self.__SW > 0:
            Hcap = self.__HeatCcap
        elif self.__SW < 0:
            Hcap = self.__CoolCcap

        # 仮の室温、熱負荷の計算
        # 室温設定の場合
        if Gdata.OTset == False:
            self.Tr, self.Lcs, self.Lr = self.calcTrLs(self.__SW,
                                                       self.__RadHeat, self.__BRC, self.__BRM,
                                                       self.__BRL, 0, 0, self.__Tset)
        # OT設定の場合
        else:
            self.__OT, self.Lcs, self.Lr = self.calcTrLs(self.__SW,
                                                         self.__RadHeat, self.__BRCot, self.__BRMot,
                                                         self.__BRLot, 0, 0, self.__Tset)
            # 室温を計算
            self.Tr = self.__Xot * self.__OT - self.__XLr * self.Lr - self.__XC

        # 最終的な運転フラグの設定
        self.__SW = self.reset_SW(Hcap, self.__HeatRcap)

        # 機器容量を再設定
        if self.__SW > 0:
            Hcap = self.__HeatCcap
        elif self.__SW < 0:
            Hcap = self.__CoolCcap
        else:
            Hcap = 0.0

        # 最終室温・熱負荷の再計算
        if Gdata.OTset == False:
            self.Tr, self.Lcs, self.Lr = self.calcTrLs(self.__SW,
                                                       self.__RadHeat, self.__BRC, self.__BRM,
                                                       self.__BRL, Hcap, self.__HeatRcap, self.__Tset)
        # OT設定の場合
        else:
            self.__OT, self.Lcs, self.Lr = self.calcTrLs(self.__SW,
                                                         self.__RadHeat, self.__BRCot, self.__BRMot,
                                                         self.__BRLot, Hcap, self.__HeatRcap, self.__Tset)
            # 室温を計算
            self.Tr = self.__Xot * self.__OT \
                      - self.__XLr * self.Lr - self.__XC

        # 放射暖房最大能力が設定されている場合にはもう１度チェックする
        if self.__SW == 3 and self.Lcs > Hcap and Hcap > 0.0:
            self.__SW = 5
            if Gdata.OTset == False:
                self.Tr, self.Lcs, self.Lr = self.calcTrLs(self.__SW, \
                                                           self.__RadHeat, self.__BRC, self.__BRM, \
                                                           self.__BRL, Hcap, self.__HeatRcap, self.__Tset)
            # OT設定の場合
            else:
                self.__OT, self.Lcs, self.Lr = self.calcTrLs(self.__SW, \
                                                             self.__RadHeat, self.__BRCot, self.__BRMot, \
                                                             self.__BRLot, Hcap, self.__HeatRcap, self.__Tset)
                # 室温を計算
                self.Tr = self.__Xot * self.__OT - self.__XLr * self.Lr - self.__XC

        # 年間熱負荷の積算
        # 助走計算以外の時だけ積算
        if Gdata.FlgOrig(dtmNow) == True:
            # 対流式空調の積算
            if self.Lcs > 0.0:
                self.__AnnualLoadcH += self.Lcs * Gdata.DTime * 0.000000001
            else:
                self.__AnnualLoadcC += self.Lcs * Gdata.DTime * 0.000000001

            # 放射式空調の積算
            if self.Lr > 0.0:
                self.__AnnualLoadrH += self.Lr * Gdata.DTime * 0.000000001
            else:
                self.__AnnualLoadrC += self.Lr * Gdata.DTime * 0.000000001

        # 表面温度の計算
        self.MRT = 0.0
        self.AST = 0.0
        i = 0
        for surface in self.surfaces:
            Ts = self.__matWSR[i][0] * self.Tr \
                 + self.__matWSC[i][0] + self.__matWSV[i][0] \
                 + self.__matWSB[i][0] * self.Lr
            surface.Ts = Ts

            # 人体に対する放射温度：MRT、面積荷重平均温度：ASTの計算
            self.MRT += surface.fot * surface.Ts
            self.AST += surface.area * surface.Ts / self.__Atotal
            i += 1

        # 室内側等価温度の計算
        for surface in self.surfaces:
            Tsx = 0.0

            j = 0
            # 形態係数加重平均表面温度の計算
            for nxtsurface in self.surfaces:
                Tsx += nxtsurface.Ts * nxtsurface.FF(j)
                j += 1

            # 室内側等価温度の計算
            surface.update_Tei(self.Tr, Tsx, self.Lr, self.__Beta)
            # 室内表面熱流の計算
            surface.update_qi(self.Tr, Tsx, self.Lr, self.__Beta)

        return 0

    # 前時刻の室温を現在時刻の室温に置換
    def update_oldTr(self):
        self.__oldTr = self.Tr

    # 室温・熱負荷の計算ルーティン
    def calcTrLs(self, SW, RadHeat, BRC, BRM, BRL, Hcap, Lrcap, Tset):
        Lcs = 0.0
        Lr = 0.0
        Tr = 0.0
        # 非空調時の計算
        if SW == 0:
            Tr = BRC / BRM
        # 熱負荷計算（最大能力無制限）
        elif SW == 1 or SW == -1 or SW == 4:
            # 対流式空調の場合
            if RadHeat != True:
                Lcs = BRM * Tset - BRC
            # 放射式空調
            else:
                Lr = (BRM * Tset - BRC) / BRL
            # 室温の計算
            Tr = (BRC + Lcs + BRL * Lr) / BRM
        # 対流空調最大能力運転
        elif (SW == 2 and Hcap > 0.0) or (SW == -2 and Hcap < 0.0):
            Lcs = Hcap
            Tr = (BRC + Hcap) / BRM
        # 放射暖房最大能力運転（当面は暖房のみ）
        elif SW == 3 and Lrcap > 0.0:
            Lr = Lrcap
            # 室温は対流式で維持する
            Lcs = BRM * Tset - BRC - Lr * BRL
            # 室温の計算
            Tr = (BRC + Lcs + BRL * Lr) / BRM
        # 放射空調も対流空調も最大能力運転
        elif SW == 5:
            # 放射暖房、対流暖房ともに最大能力
            Lr = Lrcap
            Lcs = Hcap
            # 室温を計算する
            Tr = (BRC + Lcs + BRL * Lr) / BRM

        # 室温、対流空調熱負荷、放射空調熱負荷を返す
        return (Tr, Lcs, Lr)

    # 最終の空調信号の計算
    def reset_SW(self, Hcap, Lrcap):
        temp = self.__SW

        # 「冷房時の暖房」、「暖房時の冷房」判定
        if float(self.__SW) * (self.Lcs + self.Lr) < 0.0:
            temp = 0
        # 暖房の過負荷状態
        elif not self.__RadHeat and self.__SW == 1 and Hcap > 0.0 \
                and self.Lcs > Hcap:
            temp = 2
        # 冷房の過負荷状態
        elif self.__SW == -1 and Hcap < 0.0 and self.Lcs < Hcap:
            temp = -2
        # 放射暖房の過負荷状態
        elif self.__RadHeat and self.__SW == 1 and Lrcap > 0.0 \
                and self.Lr > Lrcap:
            temp = 3
        # 放射暖房の過熱状態
        elif self.__RadHeat and self.__SW == 1 and Lrcap <= 0.0:
            temp = 4

        return temp

    # 平均放射温度の計算
    def update_Tsx(self):
        self.__Tsx = 0.0
        i = 0
        for surface in self.surfaces:
            self.__Tsx += surface.Ts.Ts() * surface.FF(i)
            i += 1

    # 表面温度の出力
    def surftemp_print(self):
        for surface in self.surfaces:
            print('{0:.2f}'.format(surface.Ts()), "", end="")

def create_spaces(Gdata, rooms):
    objSpace = {}
    for room in rooms:
        space = Space(Gdata, room['roomname'], \
                      room['HeatCcap'], \
                      room['HeatRcap'], room['CoolCcap'], room['Vol'], \
                      room['Fnt'], room['Vent'], room['Inf'], \
                      room['CrossVentRoom'], room['RadHeat'], room['Beta'], room['NextVent'],
                      room['Surface'])
        objSpace[room['roomname']] = space
    return objSpace