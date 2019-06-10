import unittest
import os
import subprocess as sp
import ps_minifier.psminifier as psmin

class TestMinifiedOutput(unittest.TestCase):

    def test_equals(self):
        self.assertRegex(psmin.main(["psminifier.py"], file='$a = "b"'), '^\$[a-z]="b"$')
        self.assertRegex(psmin.main(["psminifier.py"], file='$a   = "b"'), '^\$[a-z]="b"$')
        self.assertRegex(psmin.main(["psminifier.py"], file='$a =    "b"'), '^\$[a-z]="b"$')
    
    def test_genVars(self):
        # Test 1 char
        psmin.variables[0] = ""
        psmin.genVars()
        for i in psmin.variables:
            self.assertRegex(i, '^[a-zA-Z]$')
        self.assertEqual(len(psmin.variables), len(set(psmin.variables)))
        
        # Test 2 chars
        psmin.variables[0] = "a"
        psmin.genVars()
        for i in psmin.variables:
            self.assertRegex(i, '^[a-zA-Z][a-zA-Z0-9]$')
        self.assertEqual(len(psmin.variables), len(set(psmin.variables)))
    
    def test_getVar(self):
        psmin.variable = psmin.variables[0]
        psmin.var_count = 0
        self.assertEqual(psmin.variables[psmin.var_count], psmin.getVar())
        self.assertRegex(psmin.getVar(), "^[a-zA-Z][a-zA-Z0-9]*$")

        # Test refresh variables
        psmin.variable = psmin.variables[-1]
        length = len(psmin.variable)
        psmin.getVar()
        self.assertEqual(len(psmin.variable), length+1)
    
    def test_variable_replacement(self):
        self.assertRegex(psmin.main(["psminifier.py"], file='$a = "hello there!";\n$b = "hi";\n$a="hey";'), '^(\$[a-zA-Z][a-zA-Z0-9]*)="hello there!";(\$[a-zA-Z][a-zA-Z0-9]*)="hi";\\1="hey";$')
        self.assertRegex(psmin.main(["psminifier.py"], file='$a1 = "hello there!";\n$b = "hi";\n$a1="hey";'), '^(\$[a-zA-Z][a-zA-Z0-9]*)="hello there!";(\$[a-zA-Z][a-zA-Z0-9]*)="hi";\\1="hey";$')
        self.assertRegex(psmin.main(["psminifier.py"], file='$a1A = "hello there!";\n$b = "hi";\n$a1A="hey";'), '^(\$[a-zA-Z][a-zA-Z0-9]*)="hello there!";(\$[a-zA-Z][a-zA-Z0-9]*)="hi";\\1="hey";$')
        self.assertNotRegex(psmin.main(["psminifier.py"], file='$1a = "hello there!";\n$b2 = "hi";\n$1a="hey";'), '^(\$[a-zA-Z][a-zA-Z0-9]*)="hello there!";(\$[a-zA-Z][a-zA-Z0-9]*)="hi";\\1="hey";$')
        

    def test_string_integrity(self):
        self.assertRegex(psmin.main(["psminifier.py"], file='$a = "hello there!"'), '^\$[a-z]="hello there!"$')

    def test_input_output(self):
        # Test stdin and stdout
        proc = sp.Popen(["python3", "ps_minifier/psminifier.py"], stdout=sp.PIPE, stdin=sp.PIPE)
        resp = (proc.communicate(input="$a = 2".encode()))[0].decode()
        self.assertRegex(resp, "^==RESULT==[\r\n]+\$[a-z]=2[\r\n]*$")

        # Test file input and file output
        with open("test_ps.txt", "w") as f:
            f.write("$a = 1;\n$a = $a * 2;")
        psmin.main(["psminifier.py", "-f", "test_ps.txt", "-o", "test_ps_out.txt"])
        with open("test_ps_out.txt", "r") as f:
            self.assertRegex(f.read(), "^(\$[a-z])=1;\\1=\\1\*2;[\r\n]*$")
        os.remove("test_ps_out.txt")
        os.remove("test_ps.txt")
    
    def test_maths_symbols(self):
        self.assertEqual(psmin.main(["psminifier.py"], file="Get-Command *-Service;"), "Get-Command *-Service;")

    def test_brackets_whitespace_removal(self):
        self.assertEqual(psmin.main(["psminifier.py"], file='If ( 1 -eq 1 ) {\n\tWrite-Output "Test"\n}'), 'If(1 -eq 1){Write-Output "Test"}')

if __name__ == '__main__':
    unittest.main()