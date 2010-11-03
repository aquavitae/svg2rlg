#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
svg2rlg is a tool to convert from SVG to reportlab graphics.

License : BSD

version 0.3
"""
import sys

import unittest

from reportlab.lib.units import toLength
import reportlab.lib.colors as colors

from svg2rlg import *

class test_svg2rlg(unittest.TestCase):
    def test_parseStyle(self):
        parse = parseStyle.parse
        
        txt = 'fill: red; stroke: blue; /* comment */ stroke-width: 3; line-height: 125%'
        res = parse(txt)
        
        self.assertTrue(res.pop('fill') == 'red')
        self.assertTrue(res.pop('stroke') == 'blue')
        self.assertTrue(res.pop('stroke-width') == '3')
        self.assertTrue(res.pop('line-height') == '125%')
        self.assertTrue(len(res) == 0)
        
    def test_parseTransform(self):
        parse = parseTransform.iterparse
        
        self.assertTrue(parse('matrix(1.,2.,3.,4.,5.,6.)').next() == ('matrix', (1.,2.,3.,4.,5.,6.)))
        
        test = parse('mat(1.,2.,3.,4.,5.,6.)')
        self.assertRaises(SVGError, test.next)
        
        test = parse('matrix(1.,2.,3.,4.,5.)')
        self.assertRaises(SVGError, test.next)
        
        self.assertTrue(parse('translate(-10,10)').next() == ('translate', (-10.,10.)))
        self.assertTrue(parse('translate(-10)').next() == ('translate', (-10.,0.)))
        
        self.assertTrue(parse('scale(-1, 1.)').next() == ('scale', (-1.,1.)))
        self.assertTrue(parse('scale(-1)').next() == ('scale', (-1.,-1.)))
        
        self.assertTrue(parse('rotate(-45)').next() == ('rotate', (-45.,None)))
        self.assertTrue(parse('rotate(-45, 1.,2.)').next() == ('rotate', (-45.,(1.,2.))))
        
        test = parse('rotate(-45, 1.,)')
        self.assertRaises(SVGError, test.next)
        
        self.assertTrue(parse('skewX(-45)').next() == ('skewX', (-45.,)))
        self.assertTrue(parse('skewY(-45)').next() == ('skewY', (-45.,)))
        
        test = parse('scale(1.8) translate(0, -150)')
        self.assertTrue(test.next() == ('scale', (1.8, 1.8)))
        self.assertTrue(test.next() == ('translate', (0.,-150.)))
        
        
    def test_parsePath(self):
        parse = parsePath.iterparse
        
        path = parse('M250 150 L150 350 L350 350 Z')
        
        expected = (('M', ((250.,150.),)), ('L', ((150.,350.),)), ('L', ((350.,350.),)),
                    ('Z', (None,)))
        
        for a, b in zip(path, expected):
            self.assertTrue(a == b)
        
        path = parse('M250,150 L150,350 L350,350 Z')
        
        for a, b in zip(path, expected):
            self.assertTrue(a == b)
        
        path = parse('M250.,150. L150.,350. L350.,350. Z')
        
        for a, b in zip(path, expected):
            self.assertTrue(a == b)
            
    def test_parseLength(self):
        self.assertTrue(parseLength('50%') == 50.)
        self.assertTrue(parseLength('50') == toLength('50'))
        self.assertTrue(parseLength('-646.595') == -646.595)
        self.assertTrue(parseLength('50em') == toLength('50'))
        self.assertTrue(parseLength('50ex') == toLength('50'))
        self.assertTrue(parseLength('50px') == toLength('50'))
        self.assertTrue(parseLength('50pc') == toLength('50pica'))
        self.assertTrue(parseLength('50pica') == toLength('50pica'))
        self.assertTrue(parseLength('50mm') == toLength('50mm'))
        self.assertTrue(parseLength('50cm') == toLength('50cm'))
        self.assertTrue(parseLength('50in') == toLength('50in'))
        self.assertTrue(parseLength('50i') == toLength('50i'))
        self.assertTrue(parseLength('50pt') == toLength('50pt'))
        self.assertTrue(parseLength('e-014') == 1e-14)
        
        self.assertRaises(SVGError, parseLength, 'mm')
        self.assertRaises(SVGError, parseLength, '50km')
        self.assertRaises(SVGError, parseLength, '50.5.mm')

    def test_parseColor(self):
        self.assertTrue(parseColor('none') == None)
        self.assertTrue(parseColor('currentColor') == 'currentColor')
        self.assertTrue(parseColor('transparent') == colors.Color(0.,0.,0.,0.))
        
        self.assertTrue(parseColor('dimgrey') == colors.dimgrey)
        self.assertRaises(SVGError, parseColor, 'unknown')
        
        self.assertTrue(parseColor('#fab') == colors.HexColor('#ffaabb'))
        self.assertRaises(SVGError, parseColor, '#fa')
        
        self.assertTrue(parseColor('#1a01FF') == colors.HexColor('#1a01FF'))
        self.assertRaises(SVGError, parseColor, '#1a01F')
        
        self.assertTrue(parseColor('rgb(128,9,255)') == colors.Color(128/255.,9/255.,255/255.))
        self.assertTrue(parseColor('rgb(128, 9, 255)') == colors.Color(128/255.,9/255.,255/255.))
        self.assertTrue(parseColor('Rgb(128,9,255)') == colors.Color(128/255.,9/255.,255/255.))
        self.assertRaises(SVGError, parseColor, 'rgb(128,9,256)')
        
        self.assertTrue(parseColor('rgb(40%,90%,8%)') == colors.Color(40/100.,90/100.,8/100.))
        self.assertTrue(parseColor('rgb(40%, 90%, 8%)') == colors.Color(40/100.,90/100.,8/100.))
        self.assertTrue(parseColor('rgB(40%,90%,8%)') == colors.Color(40/100.,90/100.,8/100.))
        self.assertRaises(SVGError, parseColor, 'rgb(40%,101%,8%)')
        
        self.assertRaises(SVGError, parseColor, '')
        self.assertRaises(SVGError, parseColor, '1a01FF')
        self.assertRaises(SVGError, parseColor, 'rgb(40%,90%,8%')
    
if __name__ == "__main__":
    sys.dont_write_bytecode = True
    unittest.main()