from optparse import OptionParser

from parser import Parser, InvalidTokenError, ParsingError

def open_file(filename):
    try:
        file = open(filename, 'r')
    except:
        print "Invalid filename: \"" + str(filename) + "\". Please try again."
        return False
        
    if not file:
        print "Unknown error.  Please try again."
        return False
    
    return file

def main(options, args):
    reduce = options.reduce
    filename = None
    
    if len(args) > 0:
        filename = str(args[0])
    
    file = open_file(filename)
    if not file:
        return False
    
    lines = file.readlines()
    if len(lines) != 1:
        print "Unknown file format.  Must contain exactly 1 line."
        return False
    
    expression = lines[0].strip()
    if len(expression) <= 0:
        print "Invalid file format.  Must contain at least one character."
        return False
    
    try:
        parser = Parser(expression)
    except InvalidTokenError as e:
        print "Token error. " + str(e) + " Exiting parsing."
        return False
    
    try:
        result = parser.parse(reduce, debug=False)
    except ParsingError as e:
        print "Parsing Error. " + str(e) + " Exiting parsing."
        return False
    
    print str(result)
    
    
    
    return True

parser = OptionParser()
parser.add_option("-r", "--reduce", action="store_true", dest="reduce", default=False)
(options, args) = parser.parse_args()
   
result = main(options, args)
if result:
    print "Success."
else:
    print "Failure."

