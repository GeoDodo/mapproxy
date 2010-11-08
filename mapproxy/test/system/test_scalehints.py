# This file is part of the MapProxy project.
# Copyright (C) 2010 Omniscale <http://omniscale.de>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import with_statement, division
import math


from mapproxy.request.wms import (
    WMS111MapRequest, WMS111CapabilitiesRequest, WMS130CapabilitiesRequest
)

from mapproxy.test.system import module_setup, module_teardown, make_base_config, SystemTest
from mapproxy.test.image import is_png
from mapproxy.test.system.test_wms import is_111_capa, is_130_capa, ns130
from nose.tools import eq_, assert_almost_equal

test_config = {}

def setup_module():
    module_setup(test_config, 'scalehints.yaml')

def teardown_module():
    module_teardown(test_config)

base_config = make_base_config

def diagonal_res_to_pixel_res(res):
    """
    >>> '%.2f' % round(diagonal_res_to_pixel_res(14.14214), 4)
    '10.00'
    """
    return math.sqrt((float(res)**2)/2)

class TestWMS(SystemTest):
    config = test_config
    def setup(self):
        SystemTest.setup(self)
        self.common_req = WMS111MapRequest(url='/service?', param=dict(service='WMS', 
             version='1.1.1'))
        self.common_map_req = WMS111MapRequest(url='/service?', param=dict(service='WMS', 
             version='1.1.1', bbox='-180,0,0,80', width='200', height='200',
             layers='res', srs='EPSG:4326', format='image/png',
             styles='', request='GetMap'))
    
    def test_capabilities_111(self):
        req = WMS111CapabilitiesRequest(url='/service?').copy_with_request_params(self.common_req)
        resp = self.app.get(req)
        xml = resp.lxml
        assert is_111_capa(xml)
        hints = xml.xpath('//Layer/Layer/ScaleHint')
        assert_almost_equal(diagonal_res_to_pixel_res(hints[0].attrib['min']), 10, 2)
        assert_almost_equal(diagonal_res_to_pixel_res(hints[0].attrib['max']), 10000, 2)
        
        assert_almost_equal(diagonal_res_to_pixel_res(hints[1].attrib['min']), 2.8, 2)
        assert_almost_equal(diagonal_res_to_pixel_res(hints[1].attrib['max']), 280, 2)
        
        assert_almost_equal(diagonal_res_to_pixel_res(hints[2].attrib['min']), 0.28, 2)
        assert_almost_equal(diagonal_res_to_pixel_res(hints[2].attrib['max']), 2.8, 2)
    
    def test_capabilities_130(self):
        req = WMS130CapabilitiesRequest(url='/service?').copy_with_request_params(self.common_req)
        resp = self.app.get(req)
        xml = resp.lxml
        assert is_130_capa(xml)
        min_scales = xml.xpath('//wms:Layer/wms:Layer/wms:MinScaleDenominator/text()', namespaces=ns130)
        max_scales = xml.xpath('//wms:Layer/wms:Layer/wms:MaxScaleDenominator/text()', namespaces=ns130)
        
        assert_almost_equal(float(min_scales[0]), 35714.28, 1)
        assert_almost_equal(float(max_scales[0]), 35714285.7, 1)
        
        assert_almost_equal(float(min_scales[1]), 10000, 2)
        assert_almost_equal(float(max_scales[1]), 1000000, 2)

        assert_almost_equal(float(min_scales[2]), 1000, 2)
        assert_almost_equal(float(max_scales[2]), 10000, 2)