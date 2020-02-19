#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
svg2rlg is a tool to convert from SVG to reportlab graphics.

License : BSD

version 0.3
"""

import sys
from xml.etree import ElementTree as etree

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

        self.assertTrue(next(parse('matrix(1.,2.,3.,4.,5.,6.)')) == ('matrix', (1.,2.,3.,4.,5.,6.)))

        test = parse('mat(1.,2.,3.,4.,5.,6.)')
        with self.assertRaises(SVGError):
            next(test)

        test = parse('matrix(1.,2.,3.,4.,5.)')
        with self.assertRaises(SVGError):
            next(test)

        self.assertTrue(next(parse('translate(-10,10)')) == ('translate', (-10.,10.)))
        self.assertTrue(next(parse('translate(-10)')) == ('translate', (-10.,0.)))

        self.assertTrue(next(parse('scale(-1, 1.)')) == ('scale', (-1.,1.)))
        self.assertTrue(next(parse('scale(-1)')) == ('scale', (-1.,-1.)))

        self.assertTrue(next(parse('rotate(-45)')) == ('rotate', (-45.,None)))
        self.assertTrue(next(parse('rotate(-45, 1.,2.)')) == ('rotate', (-45.,(1.,2.))))
        test = parse('rotate(-45, 1.,)')

        with self.assertRaises(SVGError):
            next(test)

        self.assertTrue(next(parse('skewX(-45)')) == ('skewX', (-45.,)))
        self.assertTrue(next(parse('skewY(-45)')) == ('skewY', (-45.,)))

        test = parse('scale(1.8) translate(0, -150)')
        self.assertTrue(next(test) == ('scale', (1.8, 1.8)))
        self.assertTrue(next(test) == ('translate', (0.,-150.)))


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

        with self.assertRaises(SVGError):
            parseLength('mm')
        with self.assertRaises(SVGError):
            parseLength('50km')
        with self.assertRaises(SVGError):
            parseLength('50.5.mm')

    def test_parseColor(self):
        self.assertTrue(parseColor('none') == None)
        self.assertTrue(parseColor('currentColor') == 'currentColor')
        self.assertTrue(parseColor('transparent') == colors.Color(0.,0.,0.,0.))

        self.assertTrue(parseColor('dimgrey') == colors.dimgrey)
        with self.assertRaises(SVGError):
            parseColor('unknown')

        self.assertTrue(parseColor('#fab') == colors.HexColor('#ffaabb'))
        with self.assertRaises(SVGError):
            parseColor('#fa')

        self.assertTrue(parseColor('#1a01FF') == colors.HexColor('#1a01FF'))
        with self.assertRaises(SVGError):
            parseColor('#1a01F')

        self.assertTrue(parseColor('rgb(128,9,255)') == colors.Color(128/255.,9/255.,255/255.))
        self.assertTrue(parseColor('rgb(128, 9, 255)') == colors.Color(128/255.,9/255.,255/255.))
        self.assertTrue(parseColor('Rgb(128,9,255)') == colors.Color(128/255.,9/255.,255/255.))
        with self.assertRaises(SVGError):
            parseColor('rgb(128,9,256)')

        self.assertTrue(parseColor('rgb(40%,90%,8%)') == colors.Color(40/100.,90/100.,8/100.))
        self.assertTrue(parseColor('rgb(40%, 90%, 8%)') == colors.Color(40/100.,90/100.,8/100.))
        self.assertTrue(parseColor('rgB(40%,90%,8%)') == colors.Color(40/100.,90/100.,8/100.))
        with self.assertRaises(SVGError):
            parseColor('rgb(40%,101%,8%)')

        with self.assertRaises(SVGError):
            parseColor('')
        with self.assertRaises(SVGError):
            parseColor('1a01FF')
        with self.assertRaises(SVGError):
            parseColor('rgb(40%,90%,8%')


class TestPath(unittest.TestCase):

    def setUp(self):
        self.renderer = Renderer('testfile')

    def getnode(self, xml):
        xml = '''<?xml version="1.0"?>
            <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
                    "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
             <svg xmlns="http://www.w3.org/2000/svg"
                    xmlns:xlink="http://www.w3.org/1999/xlink">
                {}
            </svg>
        '''.format(xml)
        return etree.fromstring(xml)

    def test_line(self):
        root = self.getnode('<path d="M 5 5 L 10 10" />')
        self.renderer.render(root)
        path = self.renderer.mainGroup.contents[0]
        self.assertEqual(path.points, [5, 5, 10, 10])

    def test_close(self):
        root = self.getnode('<path d="M 5 5 Z M 10 10" />')
        self.renderer.render(root)
        path = self.renderer.mainGroup.contents[0]
        self.assertEqual(path.points, [5, 5, 10, 10])

    def test_curve_cubic_absolute(self):
        root = self.getnode('<path d="M 5 5 C 4 6 11 12 10 10" />')
        self.renderer.render(root)
        path = self.renderer.mainGroup.contents[0]
        self.assertEqual(path.points, [5, 5, 4, 6, 11, 12, 10, 10])

    def test_curve_cubic_relative(self):
        root = self.getnode('<path d="M 5 5 c -1 1 6 7 5 5" />')
        self.renderer.render(root)
        path = self.renderer.mainGroup.contents[0]
        self.assertEqual(path.points, [5, 5, 4, 6, 11, 12, 10, 10])

    def test_curve_quadratic_absolute(self):
        root = self.getnode('<path d="M 10 10 Q 13 13 19 19" />')
        self.renderer.render(root)
        path = self.renderer.mainGroup.contents[0]
        self.assertEqual(path.points, [10, 10, 12, 12, 15, 15, 19, 19])

    def test_curve_quadratic_relative(self):
        root = self.getnode('<path d="M 10 10 q 3 3 9 9" />')
        self.renderer.render(root)
        path = self.renderer.mainGroup.contents[0]
        self.assertEqual(path.points, [10, 10, 12, 12, 15, 15, 19, 19])

    def test_curve_smooth_absolute(self):
        root = self.getnode('<path d="M 5 5 T 11 11" />')
        self.renderer.render(root)
        path = self.renderer.mainGroup.contents[0]
        self.assertEqual(path.points, [5, 5, 5, 5, 7, 7, 11, 11])

    def test_curve_smooth_relative(self):
        root = self.getnode('<path d="M 5 5 T 11 11" />')
        self.renderer.render(root)
        path = self.renderer.mainGroup.contents[0]
        self.assertEqual(path.points, [5, 5, 5, 5, 7, 7, 11, 11])


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    unittest.main()
