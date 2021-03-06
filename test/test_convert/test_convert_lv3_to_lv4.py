import unittest

from heat_load_calc.external.factor_h import NextSpace
import heat_load_calc.convert.convert_lv3_to_lv4 as nb
from heat_load_calc.convert.ees_house import SpaceType
from heat_load_calc.convert.ees_house import UpperArealEnvelope
from heat_load_calc.convert.ees_house import EarthfloorCenter, EarthfloorCenterSpec
from heat_load_calc.convert.ees_house import Layer
from heat_load_calc.convert.ees_house import HeatResistanceInputMethod
from heat_load_calc.external.factor_nu import Direction


class TestLV3toLV4(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print('\n testing convert lv3 to lv4')

    ### get_inner_floor_spec 関数のテスト ###

    def test_get_inner_floor_spec(self):
        layers = nb.get_inner_floor_layers()

        # number of array test
        self.assertEqual(1, len(layers))

        layer0: Layer = layers[0]

        # name test
        self.assertEqual('plywood', layer0.name)

        # thermal resistance input method test
        self.assertEqual(HeatResistanceInputMethod.CONDUCTIVITY, layer0.heat_resistance_input_method)

        # thermal conductivity test
        self.assertEqual(0.16, layer0.thermal_conductivity)

        # volumetric specific heat test
        self.assertEqual(720.0, layer0.volumetric_specific_heat)

        # thickness test
        self.assertEqual(0.024, layer0.thickness)

    ### get_downward_envelope_total_area 関数のテスト ###

    # direction の条件に合うものがきちんと集約されているかのテスト
    def test_1_get_downward_envelope_total_area(self):
        envelope = {
            'general_parts': [
                {
                    'space_type': 'main_occupant_room',
                    'area': 55.5,
                    'direction': 'bottom',
                },
                {
                    'space_type': 'main_occupant_room',
                    'area': 15.2,
                    'direction': 'downward',
                },
                {
                    'space_type': 'main_occupant_room',
                    'area': 55.5,
                    'direction': 'top',
                },
                {
                    'space_type': 'other_occupant_room',
                    'area': 44.4,
                    'direction': 'bottom',
                },
                {
                    'space_type': 'other_occupant_room',
                    'area': 14.1,
                    'direction': 'downward',
                },
                {
                    'space_type': 'other_occupant_room',
                    'area': 44.4,
                    'direction': 'top',
                },
                {
                    'space_type': 'non_occupant_room',
                    'area': 33.3,
                    'direction': 'bottom',
                },
                {
                    'space_type': 'non_occupant_room',
                    'area': 13.1,
                    'direction': 'downward',
                },
                {
                    'space_type': 'non_occupant_room',
                    'area': 33.3,
                    'direction': 'top',
                },
            ],
            'windows': [],
            'doors': []
        }

        gps = [
            UpperArealEnvelope(
                name='test',
                next_space=NextSpace.OUTDOOR,
                direction=Direction(gp['direction']),
                area=gp['area'],
                space_type=SpaceType(gp['space_type'])
            ) for gp in envelope['general_parts']
        ]

        ws = [
            UpperArealEnvelope(
                name='test',
                next_space=NextSpace.OUTDOOR,
                direction=Direction(w['direction']),
                area=w['area'],
                space_type=SpaceType(w['space_type'])
            ) for w in envelope['windows']
        ]

        ds = [
            UpperArealEnvelope(
                name='test',
                next_space=NextSpace.OUTDOOR,
                direction=Direction(d['direction']),
                area=d['area'],
                space_type=SpaceType(d['space_type'])
            ) for d in envelope['doors']
        ]

        a_evlp_down_mr, a_evlp_down_or, a_evlp_down_nr = nb.get_downward_envelope_total_area(gps, ws, ds)

        self.assertEqual(70.7, a_evlp_down_mr)
        self.assertEqual(58.5, a_evlp_down_or)
        self.assertEqual(46.4, a_evlp_down_nr)

    # 異なる envelope type が合算されているかを見るテスト
    def test_2_get_downward_envelope_total_area(self):
        envelope = {
            'general_parts': [
                {
                    'space_type': 'main_occupant_room',
                    'area': 55.5,
                    'direction': 'bottom',
                }
            ],
            'windows': [
                {
                    'space_type': 'main_occupant_room',
                    'area': 5.5,
                    'direction': 'bottom',
                }
            ],
            'doors': [
                {
                    'space_type': 'main_occupant_room',
                    'area': 4.4,
                    'direction': 'bottom',
                }
            ],
        }

        gps = [
            UpperArealEnvelope(
                name='test',
                next_space=NextSpace.OUTDOOR,
                direction=Direction(gp['direction']),
                area=gp['area'],
                space_type=SpaceType(gp['space_type'])
            ) for gp in envelope['general_parts']
        ]

        ws = [
            UpperArealEnvelope(
                name='test',
                next_space=NextSpace.OUTDOOR,
                direction=Direction(w['direction']),
                area=w['area'],
                space_type=SpaceType(w['space_type'])
            ) for w in envelope['windows']
        ]

        ds = [
            UpperArealEnvelope(
                name='test',
                next_space=NextSpace.OUTDOOR,
                direction=Direction(d['direction']),
                area=d['area'],
                space_type=SpaceType(d['space_type'])
            ) for d in envelope['doors']
        ]

        a_evlp_down_mr, a_evlp_down_or, a_evlp_down_nr = nb.get_downward_envelope_total_area(gps, ws, ds)

        self.assertEqual(65.4, a_evlp_down_mr)
        self.assertEqual(0.0, a_evlp_down_or)
        self.assertEqual(0.0, a_evlp_down_nr)

    ### get_earthfloor_total_area 関数のテスト ###

    # きちんと集約されているかを見るテスト
    def test_1_get_earthfloor_total_area(self):
        envelope = {
            'earthfloor_centers': [
                {
                    'name': 'ec1',
                    'area': 55.5,
                    'space_type': 'main_occupant_room',
                },
                {
                    'name': 'ec2',
                    'area': 44.4,
                    'space_type': 'other_occupant_room',
                },
                {
                    'name': 'ec3',
                    'area': 33.3,
                    'space_type': 'non_occupant_room',
                },
                {
                    'name': 'ec4',
                    'area': 22.2,
                    'space_type': 'underfloor',
                },
                {
                    'name': 'ec5',
                    'area': 5.5,
                    'space_type': 'main_occupant_room',
                },
                {
                    'name': 'ec6',
                    'area': 4.4,
                    'space_type': 'other_occupant_room',
                },
                {
                    'name': 'ec7',
                    'area': 3.3,
                    'space_type': 'non_occupant_room',
                },
                {
                    'name': 'ec8',
                    'area': 2.2,
                    'space_type': 'underfloor',
                },
            ]
        }

        ecs = [
            EarthfloorCenter(
                name=s['name'],
                area=s['area'],
                space_type=s['space_type'],
                earthfloor_center_spec=EarthfloorCenterSpec(layers=[])
            )
            for s in envelope['earthfloor_centers']
        ]

        a_ef_mr, a_ef_or, a_ef_nr, a_ef_uf = nb.get_earthfloor_total_area(ecs=ecs)

        self.assertEqual(55.5 + 5.5, a_ef_mr)
        self.assertEqual(44.4 + 4.4, a_ef_or)
        self.assertEqual(33.3 + 3.3, a_ef_nr)
        self.assertEqual(22.2 + 2.2, a_ef_uf)

    # earthfloor が無い場合に面積をすべて0として返すかどうかを見るテスト
    def test_2_get_earthfloor_total_area(self):
        envelope = {
            'earthfloor_centers': []
        }

        ecs = [
            EarthfloorCenter(
                name=s['name'],
                area=s['area'],
                space_type=s['space_type'],
                earthfloor_center_spec=EarthfloorCenterSpec(layers=[])
            )
            for s in envelope['earthfloor_centers']
        ]

        a_ef_mr, a_ef_or, a_ef_nr, a_ef_uf = nb.get_earthfloor_total_area(ecs=ecs)

        self.assertEqual(0.0, a_ef_mr)
        self.assertEqual(0.0, a_ef_or)
        self.assertEqual(0.0, a_ef_nr)
        self.assertEqual(0.0, a_ef_uf)

    ### get_inner_floor_total_area 関数のテスト ###

    # 答えが0より大きい場合のテスト
    def test_1_get_inner_floor_total_area_upper0(self):
        a_if_mr, a_if_or, a_if_nr = nb.get_inner_floor_total_area(
            a_a=120.0, a_mr=50.0, a_or=40.0,
            a_evlp_down_mr=20.0, a_evlp_down_or=15.0, a_evlp_down_nr=10.0,
            a_ef_mr=7.0, a_ef_or=6.0, a_ef_nr=4.0)

        self.assertEqual(23.0, a_if_mr)
        self.assertEqual(19.0, a_if_or)
        self.assertEqual(16.0, a_if_nr)

    # 答えが0より小さい場合のテスト
    def test_1_get_inner_floor_total_area_lower0(self):
        a_if_mr, a_if_or, a_if_nr = nb.get_inner_floor_total_area(
            a_a=120.0, a_mr=50.0, a_or=40.0,
            a_evlp_down_mr=80.0, a_evlp_down_or=60.0, a_evlp_down_nr=40.0,
            a_ef_mr=50.0, a_ef_or=6.0, a_ef_nr=4.0)

        self.assertEqual(0.0, a_if_mr)
        self.assertEqual(0.0, a_if_or)
        self.assertEqual(0.0, a_if_nr)

    ### get_inner_floor_over_underfloor_total_area 関数のテスト ###

    # a_if_mr + a_if_or + a_if_nr > 0.0 の場合
    def test_1_get_inner_floor_over_underfloor_total_area(self):
        a_if_mr_uf, a_if_or_uf, a_if_nr_uf = nb.get_inner_floor_over_underfloor_total_area(
            a_if_mr=25.0, a_if_or=15.0, a_if_nr=10.0, a_ef_uf=30.0)

        self.assertEqual(15.0, a_if_mr_uf)
        self.assertEqual(9.0, a_if_or_uf)
        self.assertEqual(6.0, a_if_nr_uf)

    # a_ef_uf = 0.0 の場合
    def test_2_get_inner_floor_over_underfloor_total_area(self):
        a_if_mr_uf, a_if_or_uf, a_if_nr_uf = nb.get_inner_floor_over_underfloor_total_area(
            a_if_mr=25.0, a_if_or=15.0, a_if_nr=10.0, a_ef_uf=0.0)

        self.assertEqual(0.0, a_if_mr_uf)
        self.assertEqual(0.0, a_if_or_uf)
        self.assertEqual(0.0, a_if_nr_uf)

    # a_if_mr=0.0, a_if_or=0.0, a_if_nr=0.0 の場合
    def test_3_get_inner_floor_over_underfloor_total_area(self):
        a_if_mr_uf, a_if_or_uf, a_if_nr_uf = nb.get_inner_floor_over_underfloor_total_area(
            a_if_mr=0.0, a_if_or=0.0, a_if_nr=0.0, a_ef_uf=30.0)

        self.assertEqual(0.0, a_if_mr_uf)
        self.assertEqual(0.0, a_if_or_uf)
        self.assertEqual(0.0, a_if_nr_uf)

    ### get_inner_floor_between_rooms 関数のテスト ###

    # その他の居室と非居室の床面積の合計がともに0の場合
    def test_1_get_inner_floor_between_rooms(self):
        a_if_mr_or, a_if_mr_nr, a_if_or_mr, a_if_or_nr, a_if_nr_mr, a_if_nr_or \
            = nb.get_inner_floor_between_rooms(a_mr=120.0, a_or=0.0, a_a=120.0,
                                               a_if_mr=35.0, a_if_or=30.0, a_if_nr=25.0,
                                               a_if_mr_uf=8.0, a_if_or_uf=7.0, a_if_nr_uf=6.0)

        self.assertEqual(0.0, a_if_mr_or)
        self.assertEqual(0.0, a_if_mr_nr)
        self.assertEqual(0.0, a_if_or_mr)
        self.assertEqual(0.0, a_if_or_nr)
        self.assertEqual(0.0, a_if_nr_mr)
        self.assertEqual(0.0, a_if_nr_or)

    # その他の居室の床面積の合計が0で、非居室の床面積の合計が0ではない場合
    def test_2_get_inner_floor_between_rooms(self):
        a_if_mr_or, a_if_mr_nr, a_if_or_mr, a_if_or_nr, a_if_nr_mr, a_if_nr_or \
            = nb.get_inner_floor_between_rooms(a_mr=30.0, a_or=0.0, a_a=120.0,
                                               a_if_mr=35.0, a_if_or=30.0, a_if_nr=25.0,
                                               a_if_mr_uf=8.0, a_if_or_uf=7.0, a_if_nr_uf=6.0)

        self.assertEqual(0.0, a_if_mr_or)
        self.assertEqual(27.0, a_if_mr_nr)
        self.assertEqual(0.0, a_if_or_mr)
        self.assertEqual(0.0, a_if_or_nr)
        self.assertEqual(19.0, a_if_nr_mr)
        self.assertEqual(0.0, a_if_nr_or)

    # その他の居室の床面積の合計が0でなく、非居室の床面積の合計が0の場合
    def test_3_get_inner_floor_between_rooms(self):
        a_if_mr_or, a_if_mr_nr, a_if_or_mr, a_if_or_nr, a_if_nr_mr, a_if_nr_or \
            = nb.get_inner_floor_between_rooms(a_mr=30.0, a_or=90.0, a_a=120.0,
                                               a_if_mr=35.0, a_if_or=30.0, a_if_nr=25.0,
                                               a_if_mr_uf=8.0, a_if_or_uf=7.0, a_if_nr_uf=6.0)

        self.assertEqual(27.0, a_if_mr_or)
        self.assertEqual(0.0, a_if_mr_nr)
        self.assertEqual(23.0, a_if_or_mr)
        self.assertEqual(0.0, a_if_or_nr)
        self.assertEqual(0.0, a_if_nr_mr)
        self.assertEqual(0.0, a_if_nr_or)

    # その他の居室、非居室の床面積の合計がともに0ではない場合
    def test_4_get_inner_floor_between_rooms(self):
        a_if_mr_or, a_if_mr_nr, a_if_or_mr, a_if_or_nr, a_if_nr_mr, a_if_nr_or \
            = nb.get_inner_floor_between_rooms(a_mr=30.0, a_or=60.0, a_a=120.0,
                                               a_if_mr=35.0, a_if_or=30.0, a_if_nr=25.0,
                                               a_if_mr_uf=8.0, a_if_or_uf=7.0, a_if_nr_uf=6.0)

        self.assertEqual(13.5, a_if_mr_or)
        self.assertEqual(13.5, a_if_mr_nr)
        self.assertEqual(11.5, a_if_or_mr)
        self.assertEqual(11.5, a_if_or_nr)
        self.assertEqual(9.5, a_if_nr_mr)
        self.assertEqual(9.5, a_if_nr_or)

    ### get_inner_wall_spec 関数のテスト ###

    def test_get_inner_wall_spec(self):
        layers = nb.get_inner_wall_layers()

        # number of array test
        self.assertEqual(3, len(layers))

        layer0 = layers[0]
        layer1 = layers[1]
        layer2 = layers[2]

        # name test
        self.assertEqual('gpb', layer0.name)
        self.assertEqual('air_layer', layer1.name)
        self.assertEqual('gpb', layer2.name)

        # thermal resistance input method test
        self.assertEqual(HeatResistanceInputMethod.CONDUCTIVITY, layer0.heat_resistance_input_method)
        self.assertEqual(HeatResistanceInputMethod.RESISTANCE, layer1.heat_resistance_input_method)
        self.assertEqual(HeatResistanceInputMethod.CONDUCTIVITY, layer2.heat_resistance_input_method)

        # thermal conductivity test
        self.assertEqual(0.22, layer0.thermal_conductivity)
        self.assertEqual(0.22, layer2.thermal_conductivity)

        # volumetric specific heat test
        self.assertEqual(830.0, layer0.volumetric_specific_heat)
        self.assertEqual(0.0, layer1.volumetric_specific_heat)
        self.assertEqual(830.0, layer2.volumetric_specific_heat)

        # thickness test
        self.assertEqual(0.0125, layer0.thickness)
        self.assertEqual(0.0125, layer2.thickness)

        # thermal resistance test
        self.assertEqual(0.09, layer1.thermal_resistance)

    ### get_horizontal_envelope_total_area 関数のテスト ###

    # 指定された direction がきちんと集約されているかどうかのテスト
    def test_1_get_horizontal_envelope_total_area(self):
        envelope = {
            'general_parts': [
                {
                    'space_type': 'main_occupant_room',
                    'area': 10.0,
                    'direction': 'n',
                },
                {
                    'space_type': 'main_occupant_room',
                    'area': 10.0,
                    'direction': 'ne',
                },
                {
                    'space_type': 'main_occupant_room',
                    'area': 10.0,
                    'direction': 'e',
                },
                {
                    'space_type': 'main_occupant_room',
                    'area': 10.0,
                    'direction': 'se',
                },
                {
                    'space_type': 'main_occupant_room',
                    'area': 10.0,
                    'direction': 's',
                },
                {
                    'space_type': 'main_occupant_room',
                    'area': 10.0,
                    'direction': 'sw',
                },
                {
                    'space_type': 'main_occupant_room',
                    'area': 10.0,
                    'direction': 'w',
                },
                {
                    'space_type': 'main_occupant_room',
                    'area': 10.0,
                    'direction': 'nw',
                },
                {
                    'space_type': 'main_occupant_room',
                    'area': 10.0,
                    'direction': 'horizontal',
                },
                {
                    'space_type': 'other_occupant_room',
                    'area': 9.0,
                    'direction': 'n',
                },
                {
                    'space_type': 'other_occupant_room',
                    'area': 9.0,
                    'direction': 'ne',
                },
                {
                    'space_type': 'other_occupant_room',
                    'area': 9.0,
                    'direction': 'e',
                },
                {
                    'space_type': 'other_occupant_room',
                    'area': 9.0,
                    'direction': 'se',
                },
                {
                    'space_type': 'other_occupant_room',
                    'area': 9.0,
                    'direction': 's',
                },
                {
                    'space_type': 'other_occupant_room',
                    'area': 9.0,
                    'direction': 'sw',
                },
                {
                    'space_type': 'other_occupant_room',
                    'area': 9.0,
                    'direction': 'w',
                },
                {
                    'space_type': 'other_occupant_room',
                    'area': 9.0,
                    'direction': 'nw',
                },
                {
                    'space_type': 'other_occupant_room',
                    'area': 9.0,
                    'direction': 'horizontal',
                },
                {
                    'space_type': 'non_occupant_room',
                    'area': 8.0,
                    'direction': 'n',
                },
                {
                    'space_type': 'non_occupant_room',
                    'area': 8.0,
                    'direction': 'ne',
                },
                {
                    'space_type': 'non_occupant_room',
                    'area': 8.0,
                    'direction': 'e',
                },
                {
                    'space_type': 'non_occupant_room',
                    'area': 8.0,
                    'direction': 'se',
                },
                {
                    'space_type': 'non_occupant_room',
                    'area': 8.0,
                    'direction': 's',
                },
                {
                    'space_type': 'non_occupant_room',
                    'area': 8.0,
                    'direction': 'sw',
                },
                {
                    'space_type': 'non_occupant_room',
                    'area': 8.0,
                    'direction': 'w',
                },
                {
                    'space_type': 'non_occupant_room',
                    'area': 8.0,
                    'direction': 'nw',
                },
                {
                    'space_type': 'non_occupant_room',
                    'area': 8.0,
                    'direction': 'horizontal',
                },
            ],
            'windows': [],
            'doors': []
        }

        gps = [
            UpperArealEnvelope(
                name='test',
                next_space=NextSpace.OUTDOOR,
                direction=Direction(gp['direction']),
                area=gp['area'],
                space_type=SpaceType(gp['space_type'])
            ) for gp in envelope['general_parts']
        ]

        ws = [
            UpperArealEnvelope(
                name='test',
                next_space=NextSpace.OUTDOOR,
                direction=Direction(w['direction']),
                area=w['area'],
                space_type=SpaceType(w['space_type'])
            ) for w in envelope['windows']
        ]

        ds = [
            UpperArealEnvelope(
                name='test',
                next_space=NextSpace.OUTDOOR,
                direction=Direction(d['direction']),
                area=d['area'],
                space_type=SpaceType(d['space_type'])
            ) for d in envelope['doors']
        ]

        a_ow_mr, a_ow_or, a_ow_nr = nb.get_horizontal_envelope_total_area(gps, ws, ds)

        self.assertEqual(90.0, a_ow_mr)
        self.assertEqual(81.0, a_ow_or)
        self.assertEqual(72.0, a_ow_nr)

    # きちんと面積が合算されているかどうかのテスト
    def test_2_get_horizontal_envelope_total_area(self):
        envelope = {
            'general_parts': [
                {
                    'space_type': 'main_occupant_room',
                    'area': 55.5,
                    'direction': 'horizontal',
                }
            ],
            'windows': [
                {
                    'space_type': 'main_occupant_room',
                    'area': 5.5,
                    'direction': 'horizontal',
                }
            ],
            'doors': [
                {
                    'space_type': 'main_occupant_room',
                    'area': 4.4,
                    'direction': 'horizontal',
                }
            ],
        }

        gps = [
            UpperArealEnvelope(
                name='test',
                next_space=NextSpace.OUTDOOR,
                direction=Direction(gp['direction']),
                area=gp['area'],
                space_type=SpaceType(gp['space_type'])
            ) for gp in envelope['general_parts']
        ]

        ws = [
            UpperArealEnvelope(
                name='test',
                next_space=NextSpace.OUTDOOR,
                direction=Direction(w['direction']),
                area=w['area'],
                space_type=SpaceType(w['space_type'])
            ) for w in envelope['windows']
        ]

        ds = [
            UpperArealEnvelope(
                name='test',
                next_space=NextSpace.OUTDOOR,
                direction=Direction(d['direction']),
                area=d['area'],
                space_type=SpaceType(d['space_type'])
            ) for d in envelope['doors']
        ]

        a_ow_mr, a_ow_or, a_ow_nr = nb.get_horizontal_envelope_total_area(gps, ws, ds)

        self.assertEqual(65.4, a_ow_mr)
        self.assertEqual(0.0, a_ow_or)
        self.assertEqual(0.0, a_ow_nr)

    ### get_inner_wall_total_area 関数のテスト ###

    # 床面積が0の場合
    def test_1_get_inner_wall_total_area(self):
        a_iw_mr, a_iw_or, a_iw_nr = nb.get_inner_wall_total_area(
            a_mr=0.0, a_or=0.0, a_a=0.0,
            a_evlp_hzt_mr=15.0, a_evlp_hzt_or=15.0, a_evlp_hzt_nr=15.0)

        self.assertEqual(0.0, a_iw_mr)
        self.assertEqual(0.0, a_iw_or)
        self.assertEqual(0.0, a_iw_nr)

    # 床面積が0より大で間仕切り壁が負にならない
    def test_2_get_inner_wall_total_area(self):
        a_iw_mr, a_iw_or, a_iw_nr = nb.get_inner_wall_total_area(
            a_mr=30.0, a_or=40.0, a_a=120.0,
            a_evlp_hzt_mr=15.0, a_evlp_hzt_or=20.0, a_evlp_hzt_nr=25.0)

        self.assertAlmostEqual(4 * 1.2 * 2.8 * (30.0 ** 0.5) - 15.0, a_iw_mr)
        self.assertAlmostEqual(4 * 1.4 * 2.8 * (40.0 ** 0.5) - 20.0, a_iw_or)
        self.assertAlmostEqual(4 * 1.4 * 2.8 * (50.0 ** 0.5) - 25.0, a_iw_nr)

    ### get_inner_wall_total_area_between_rooms ###

    # a_or=0, a_nr=0 のテスト
    def test_1_get_inner_wall_total_area_between_rooms(self):
        a_iw_mr_or, a_iw_mr_nr, a_iw_or_nr \
            = nb.get_inner_wall_total_area_between_rooms(
            a_mr=30.0, a_or=0.0, a_a=30.0,
            a_iw_mr=50.0, a_iw_or=90.0, a_iw_nr=120.0)

        self.assertEqual(a_iw_mr_or, 0.0)
        self.assertEqual(a_iw_mr_nr, 0.0)
        self.assertEqual(a_iw_or_nr, 0.0)

    # a_or=0, a_nr>0 のテスト
    def test_2_get_inner_wall_total_area_between_rooms(self):
        a_iw_mr_or, a_iw_mr_nr, a_iw_or_nr \
            = nb.get_inner_wall_total_area_between_rooms(
            a_mr=30.0, a_or=0.0, a_a=120.0,
            a_iw_mr=50.0, a_iw_or=90.0, a_iw_nr=120.0)

        self.assertEqual(a_iw_mr_or, 0.0)
        self.assertEqual(a_iw_mr_nr, 85.0)
        self.assertEqual(a_iw_or_nr, 0.0)

    # a_or>0, a_nr=0 のテスト
    def test_3_get_inner_wall_total_area_between_rooms(self):
        a_iw_mr_or, a_iw_mr_nr, a_iw_or_nr \
            = nb.get_inner_wall_total_area_between_rooms(
            a_mr=30.0, a_or=90.0, a_a=120.0,
            a_iw_mr=50.0, a_iw_or=90.0, a_iw_nr=120.0)

        self.assertEqual(a_iw_mr_or, 70.0)
        self.assertEqual(a_iw_mr_nr, 0.0)
        self.assertEqual(a_iw_or_nr, 0.0)

    # a_or>0, a_nr>0 かつ、a_iw_mr>a_iw_or+a_iw_nr のテスト
    def test_4_get_inner_wall_total_area_between_rooms(self):
        a_iw_mr_or, a_iw_mr_nr, a_iw_or_nr \
            = nb.get_inner_wall_total_area_between_rooms(
            a_mr=30.0, a_or=50.0, a_a=120.0,
            a_iw_mr=220.0, a_iw_or=90.0, a_iw_nr=120.0)

        self.assertEqual(a_iw_mr_or, 95.0)
        self.assertEqual(a_iw_mr_nr, 125.0)
        self.assertEqual(a_iw_or_nr, 0.0)

    # a_or>0, a_nr>0 かつ、a_iw_or>a_iw_mr+a_iw_nr のテスト
    def test_5_get_inner_wall_total_area_between_rooms(self):
        a_iw_mr_or, a_iw_mr_nr, a_iw_or_nr \
            = nb.get_inner_wall_total_area_between_rooms(
            a_mr=30.0, a_or=50.0, a_a=120.0,
            a_iw_mr=90.0, a_iw_or=220.0, a_iw_nr=120.0)

        self.assertEqual(a_iw_mr_or, 95.0)
        self.assertEqual(a_iw_mr_nr, 0.0)
        self.assertEqual(a_iw_or_nr, 125.0)

    # a_or>0, a_nr>0 かつ、a_iw_nr>a_iw_mr+a_iw_or のテスト
    def test_6_get_inner_wall_total_area_between_rooms(self):
        a_iw_mr_or, a_iw_mr_nr, a_iw_or_nr \
            = nb.get_inner_wall_total_area_between_rooms(
            a_mr=30.0, a_or=50.0, a_a=120.0,
            a_iw_mr=90.0, a_iw_or=120.0, a_iw_nr=220.0)

        self.assertEqual(a_iw_mr_or, 0.0)
        self.assertEqual(a_iw_mr_nr, 95.0)
        self.assertEqual(a_iw_or_nr, 125.0)

    # a_or>0, a_nr>0 かつ、 a_iw_nr,a_iw_mr,a_iw_or の関係が上記以外の場合のテスト
    def test_7_get_inner_wall_total_area_between_rooms(self):
        a_iw_mr_or, a_iw_mr_nr, a_iw_or_nr \
            = nb.get_inner_wall_total_area_between_rooms(
            a_mr=30.0, a_or=50.0, a_a=120.0,
            a_iw_mr=120.0, a_iw_or=200.0, a_iw_nr=100.0)

        self.assertEqual(a_iw_mr_or, 110.0)
        self.assertEqual(a_iw_mr_nr, 10.0)
        self.assertEqual(a_iw_or_nr, 90.0)

    def test_convert_spec_lv3_to_lv4(self):

        d = {
            'common': {
                'region': 6,
                'main_occupant_room_floor_area': 30.0,
                'other_occupant_room_floor_area': 60.0,
                'total_floor_area': 120.0
            },
            'envelope': {
                'general_parts': [
                    {
                        'name': 'floor',
                        'general_part_type': 'floor',
                        'next_space': 'open_underfloor',
                        'direction': 'bottom',
                        'area': 60.0,
                        'space_type': 'main_occupant_room',
                        'sunshade': {
                            'is_defined': False
                        },
                        'spec': {
                            'structure': 'other',
                            'u_value_other': 2.0,
                            'weight': 'light'
                        }
                    },
                ],
                'windows': [],
                'doors': [],
                'earthfloor_perimeters': [],
                'earthfloor_centers': [
                    {'name': 'other', 'area': 5.0, 'space_type': 'underfloor', 'spec': {'layers': []}},
                    {'name': 'entrance', 'area': 5.0, 'space_type': 'underfloor', 'spec': {'layers': []}}
                ],
                'heat_bridges': []
            }
        }

        t = nb.convert_spec(d['common'], d['envelope'])

        gp = t['general_parts'][0]
        self.assertEqual('floor', gp['name'])
        self.assertEqual('floor', gp['general_part_type'])
        self.assertEqual('open_underfloor', gp['next_space'])
        self.assertEqual('bottom', gp['direction'])
        self.assertEqual(60.0, gp['area'])
        self.assertEqual('main_occupant_room', gp['space_type'])
        self.assertEqual({'is_defined': False}, gp['sunshade'])
        self.assertEqual({'structure': 'other', 'u_value_other': 2.0, 'weight': 'light'}, gp['spec'])

        ws = t['windows']
        self.assertEqual([], ws)

        ds = t['doors']
        self.assertEqual([], ds)

        eps = t['earthfloor_perimeters']
        self.assertEqual([], eps)

        ec0 = t['earthfloor_centers'][0]
        self.assertEqual('other', ec0['name'])
        self.assertEqual(5.0, ec0['area'])
        self.assertEqual('underfloor', ec0['space_type'])
        self.assertEqual([], ec0['spec']['layers'])

        ec1 = t['earthfloor_centers'][1]
        self.assertEqual('entrance', ec1['name'])
        self.assertEqual(5.0, ec1['area'])
        self.assertEqual('underfloor', ec1['space_type'])
        self.assertEqual([], ec1['spec']['layers'])

        expected_inner_floor_spec = {
            'layers': [
                {
                    'name': 'plywood',
                    'heat_resistance_input_method': 'conductivity',
                    'thermal_conductivity': 0.16,
                    'volumetric_specific_heat': 720.0,
                    'thickness': 0.024
                }
            ]
        }

        ifs = t['inner_floors']
        f = ifs[0]
        self.assertEqual('inner_floor_other_to_underfloor', f['name'])
        self.assertAlmostEqual(6.666666666666667, f['area'])
        self.assertEqual('other_occupant_room', f['upper_space_type'])
        self.assertEqual('underfloor', f['lower_space_type'])
        self.assertEqual(expected_inner_floor_spec, f['spec'])
        f = ifs[1]
        self.assertEqual('inner_floor_non_to_underfloor', f['name'])
        self.assertAlmostEqual(3.3333333333333335, f['area'])
        self.assertEqual('non_occupant_room', f['upper_space_type'])
        self.assertEqual('underfloor', f['lower_space_type'])
        self.assertEqual(expected_inner_floor_spec, f['spec'])
        f = ifs[2]
        self.assertEqual('inner_floor_other_to_main', f['name'])
        self.assertAlmostEqual(26.666666666666668, f['area'])
        self.assertEqual('other_occupant_room', f['upper_space_type'])
        self.assertEqual('main_occupant_room', f['lower_space_type'])
        self.assertEqual(expected_inner_floor_spec, f['spec'])
        f = ifs[3]
        self.assertEqual('inner_floor_other_to_non', f['name'])
        self.assertAlmostEqual(26.666666666666668, f['area'])
        self.assertEqual('other_occupant_room', f['upper_space_type'])
        self.assertEqual('non_occupant_room', f['lower_space_type'])
        self.assertEqual(expected_inner_floor_spec, f['spec'])
        f = ifs[4]
        self.assertEqual('inner_floor_non_to_main', f['name'])
        self.assertAlmostEqual(13.333333333333334, f['area'])
        self.assertEqual('non_occupant_room', f['upper_space_type'])
        self.assertEqual('main_occupant_room', f['lower_space_type'])
        self.assertEqual(expected_inner_floor_spec, f['spec'])
        f = ifs[5]
        self.assertEqual('inner_floor_non_to_other', f['name'])
        self.assertAlmostEqual(13.333333333333334, f['area'])
        self.assertEqual('non_occupant_room', f['upper_space_type'])
        self.assertEqual('other_occupant_room', f['lower_space_type'])
        self.assertEqual(expected_inner_floor_spec, f['spec'])

        expected_inner_wall_spec = {
            'layers': [
                {
                    'name': 'gpb',
                    'heat_resistance_input_method': 'conductivity',
                    'thermal_conductivity': 0.22,
                    'thickness': 0.0125,
                    'volumetric_specific_heat': 830.0
                },
                {
                    'name': 'air_layer',
                    'heat_resistance_input_method': 'resistance',
                    'thermal_resistance': 0.09,
                    'thickness': 0.120,
                    'volumetric_specific_heat': 0.0
                },
                {
                    'name': 'gpb',
                    'heat_resistance_input_method': 'conductivity',
                    'thermal_conductivity': 0.22,
                    'thickness': 0.0125,
                    'volumetric_specific_heat': 830.0
                }
            ]
        }

        iws = t['inner_walls']
        w = iws[0]
        self.assertEqual('inner_wall_main_to_other', w['name'])
        self.assertAlmostEqual(54.59388622447443, w['area'])
        self.assertEqual('main_occupant_room', w['space_type_1'])
        self.assertEqual('other_occupant_room', w['space_type_2'])
        self.assertEqual(expected_inner_wall_spec, w['spec'])
        w = iws[1]
        self.assertEqual('inner_wall_main_to_non', w['name'])
        self.assertAlmostEqual(19.020025504219888, w['area'])
        self.assertEqual('main_occupant_room', w['space_type_1'])
        self.assertEqual('non_occupant_room', w['space_type_2'])
        self.assertEqual(expected_inner_wall_spec, w['spec'])
        w = iws[2]
        self.assertEqual('inner_wall_other_to_non', w['name'])
        self.assertAlmostEqual(66.86287151259015, w['area'])
        self.assertEqual('other_occupant_room', w['space_type_1'])
        self.assertEqual('non_occupant_room', w['space_type_2'])
        self.assertEqual(expected_inner_wall_spec, w['spec'])



if __name__ == '__main__':
    unittest.main()
