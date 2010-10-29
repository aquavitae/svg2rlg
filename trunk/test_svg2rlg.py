#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
svg2rlg is a tool to convert from SVG to reportlab graphics.

License : BSD

version 0.3
"""
import sys

import nose
from nose.tools import assert_raises

from reportlab.lib.units import toLength
import reportlab.lib.colors as colors

from svg2rlg import *

def test_parseStyle():
    parse = parseStyle.parse
    
    txt = 'fill: red; stroke: blue; /* comment */ stroke-width: 3; line-height: 125%'
    res = parse(txt)
    
    assert res.pop('fill') == 'red'
    assert res.pop('stroke') == 'blue'
    assert res.pop('stroke-width') == '3'
    assert res.pop('line-height') == '125%'
    assert len(res) == 0
    
def test_parseTransform():
    parse = parseTransform.iterparse
    
    print parse('matrix(1.,2.,3.,4.,5.,6.)').next()
    
    assert parse('matrix(1.,2.,3.,4.,5.,6.)').next() == ('matrix', (1.,2.,3.,4.,5.,6.))
    
    test = parse('mat(1.,2.,3.,4.,5.,6.)')
    assert_raises(SVGError, test.next)
    
    test = parse('matrix(1.,2.,3.,4.,5.)')
    assert_raises(SVGError, test.next)
    
    assert parse('translate(-10,10)').next() == ('translate', (-10.,10.))
    assert parse('translate(-10)').next() == ('translate', (-10.,0.))
    
    assert parse('scale(-1, 1.)').next() == ('scale', (-1.,1.))
    assert parse('scale(-1)').next() == ('scale', (-1.,-1.))
    
    assert parse('rotate(-45)').next() == ('rotate', (-45.,None))
    assert parse('rotate(-45, 1.,2.)').next() == ('rotate', (-45.,(1.,2.)))
    
    test = parse('rotate(-45, 1.,)')
    assert_raises(SVGError, test.next)
    
    assert parse('skewX(-45)').next() == ('skewX', (-45.,))
    assert parse('skewY(-45)').next() == ('skewY', (-45.,))
    
    test = parse('scale(1.8) translate(0, -150)')
    assert test.next() == ('scale', (1.8, 1.8))
    assert test.next() == ('translate', (0.,-150.))
    
    
def test_parsePath():
    parse = parsePath.iterparse
    
    path = parse('M250 150 L150 350 L350 350 Z')
    
    expected = (('M', ((250.,150.),)), ('L', ((150.,350.),)), ('L', ((350.,350.),)),
                ('Z', (None,)))
    
    for a, b in zip(path, expected):
        assert a == b
    
    path = parse('M250,150 L150,350 L350,350 Z')
    
    for a, b in zip(path, expected):
        print a, b
        assert a == b
    
    path = parse('M250.,150. L150.,350. L350.,350. Z')
    
    for a, b in zip(path, expected):
        print a, b
        assert a == b
        
def test_parseLength():
    assert parseLength('50%') == 50.
    assert parseLength('50') == toLength('50')
    assert parseLength('-646.595') == -646.595
    assert parseLength('50em') == toLength('50')
    assert parseLength('50ex') == toLength('50')
    assert parseLength('50px') == toLength('50')
    assert parseLength('50pc') == toLength('50pica')
    assert parseLength('50pica') == toLength('50pica')
    assert parseLength('50mm') == toLength('50mm')
    assert parseLength('50cm') == toLength('50cm')
    assert parseLength('50in') == toLength('50in')
    assert parseLength('50i') == toLength('50i')
    assert parseLength('50pt') == toLength('50pt')
    assert parseLength('e-014') == 1e-14
    
    assert_raises(SVGError, parseLength, 'mm')
    assert_raises(SVGError, parseLength, '50km')
    assert_raises(SVGError, parseLength, '50.5.mm')

def test_parseColor():
    assert parseColor('none') == None
    assert parseColor('currentColor') == 'currentColor'
    assert parseColor('transparent') == colors.Color(0.,0.,0.,0.)
    
    assert parseColor('dimgrey') == colors.dimgrey
    assert_raises(SVGError, parseColor, 'unknown')
    
    assert parseColor('#fab') == colors.HexColor('#ffaabb')
    assert_raises(SVGError, parseColor, '#fa')
    
    assert parseColor('#1a01FF') == colors.HexColor('#1a01FF')
    assert_raises(SVGError, parseColor, '#1a01F')
    
    assert parseColor('rgb(128,9,255)') == colors.Color(128/255.,9/255.,255/255.)
    assert parseColor('rgb(128, 9, 255)') == colors.Color(128/255.,9/255.,255/255.)
    assert parseColor('Rgb(128,9,255)') == colors.Color(128/255.,9/255.,255/255.)
    assert_raises(SVGError, parseColor, 'rgb(128,9,256)')
    
    assert parseColor('rgb(40%,90%,8%)') == colors.Color(40/100.,90/100.,8/100.)
    assert parseColor('rgb(40%, 90%, 8%)') == colors.Color(40/100.,90/100.,8/100.)
    assert parseColor('rgB(40%,90%,8%)') == colors.Color(40/100.,90/100.,8/100.)
    assert_raises(SVGError, parseColor, 'rgb(40%,101%,8%)')
    
    assert_raises(SVGError, parseColor, '')
    assert_raises(SVGError, parseColor, '1a01FF')
    assert_raises(SVGError, parseColor, 'rgb(40%,90%,8%')
    
if __name__ == "__main__":
    sys.argv.append("--verbosity=2")
    result = nose.runmodule()