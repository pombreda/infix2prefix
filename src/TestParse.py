'''
Created on Oct 31, 2012

@author: kelly
'''
import unittest
from parser import Parser, InvalidTokenError, ParsingError


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test1(self):
        parser = Parser("1 + 1")
        result = parser.parse(simplify=False, debug=False)
        self.assertEqual(str(result), "(+ 1 1)", result)
        
    def test2(self):
        parser = Parser("3")
        result = parser.parse(simplify=False, debug=False)
        self.assertEqual(str(result), "3", result)
        
    def test3(self):
        parser = Parser("2 * 5 + 1")
        result = parser.parse(simplify=False, debug=False)
        self.assertEqual(str(result), "(+ (* 2 5) 1)", result)
        
    def test4(self):
        parser = Parser("2 / ( 5 + 1 )")
        result = parser.parse(simplify=False, debug=False)
        self.assertEqual(str(result), "(/ 2 (+ 5 1))", result)
    
    def test5(self):
        parser = Parser("3 * x + ( 9 + y ) / 4")
        result = parser.parse(simplify=False, debug=False)
        self.assertEqual(str(result), "(+ (* 3 x) (/ (+ 9 y) 4))", result)
        
    def test6(self):
        parser = Parser("1 + 2 + 3")
        result = parser.parse(simplify=False, debug=False)
        self.assertEqual(str(result), "(+ 1 (+ 2 3))", result)
        
    def test7(self):
        parser = Parser("( 1 + 2 + 3 ) * ( 4 + 5 + 6 ) / 7")
        result = parser.parse(simplify=False, debug=False)
        self.assertEqual(str(result), "(* (+ 1 (+ 2 3)) (/ (+ 4 (+ 5 6)) 7))", result)
        
    def test8(self):
        parser = Parser("( 1 + 2 + 3 )")
        result = parser.parse(simplify=False, debug=False)
        self.assertEqual(str(result), "(+ 1 (+ 2 3))", result)
        
    def test9(self):
        parser = Parser("1 + 2 + 3")
        result = parser.parse(simplify=True, debug=False)
        self.assertEqual(str(result), "6", result)
    
    def test10(self):
        parser = Parser("3 * 3 + ( 9 + 1 ) / 4")
        result = parser.parse(simplify=True, debug=False)
        self.assertEqual(str(result), "11", result)
    
    def testOpPrec(self):
        parser = Parser("3 + 5 * 4")
        result = parser.parse(simplify=True, debug=False)
        self.assertEqual(str(result), "23", result)
    
    def testLargeNumber(self):
        parser = Parser("9 * 9 * 9 * 9 * 9 * 9 * 9 * 9 * 9 * 9 * 9 * 9 * 9 * 9 * 9") # 9^15
        result = parser.parse(simplify=True, debug=False)
        self.assertEqual(str(result), "205891132094649", result)
        
    def test11(self):
        def doParse():
            parser = Parser("")
        
        self.assertRaises(InvalidTokenError, doParse)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()