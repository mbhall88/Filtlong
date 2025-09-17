"""
Test short command line options functionality.

This module contains tests for the short options added:
- -l for --min_length
- -L for --max_length 
- -q for --min_mean_q

To run them, execute `python3 -m unittest test.test_short_options` from the
root Filtlong directory.
"""

import unittest
import os
import subprocess


class TestShortOptions(unittest.TestCase):
    
    def setUp(self):
        # Create test data
        self.test_fastq = "test/test_short_options.fastq"
        with open(self.test_fastq, 'w') as f:
            f.write("@read1_short\n")
            f.write("A" * 50 + "\n")  # 50 bp
            f.write("+\n")
            f.write("I" * 50 + "\n")  # high quality
            f.write("@read2_long\n") 
            f.write("A" * 150 + "\n")  # 150 bp
            f.write("+\n")
            f.write("I" * 150 + "\n")  # high quality
            f.write("@read3_low_quality\n")
            f.write("A" * 100 + "\n")  # 100 bp
            f.write("+\n")
            f.write("!" * 100 + "\n")  # low quality (ASCII 33, Phred 0)
    
    def tearDown(self):
        if os.path.exists(self.test_fastq):
            os.remove(self.test_fastq)
    
    def run_command(self, command):
        """Run filtlong command and return output and return code."""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stderr + result.stdout, result.returncode
        except Exception as e:
            return str(e), 1
    
    def test_min_length_short_option(self):
        """Test that -l option works the same as --min_length."""
        # Test with -l
        console_out_short, return_code_short = self.run_command(f'bin/filtlong -l 75 {self.test_fastq}')
        self.assertEqual(return_code_short, 0)
        
        # Test with --min_length  
        console_out_long, return_code_long = self.run_command(f'bin/filtlong --min_length 75 {self.test_fastq}')
        self.assertEqual(return_code_long, 0)
        
        # Both should produce the same output (only reads >= 75bp)
        self.assertEqual(console_out_short, console_out_long)
        # Should only contain read2_long (150bp) and read3_low_quality (100bp), not read1_short (50bp)
        self.assertIn('read2_long', console_out_short)
        self.assertIn('read3_low_quality', console_out_short)
        self.assertNotIn('read1_short', console_out_short)
    
    def test_max_length_short_option(self):
        """Test that -L option works the same as --max_length."""
        # Test with -L
        console_out_short, return_code_short = self.run_command(f'bin/filtlong -L 120 {self.test_fastq}')
        self.assertEqual(return_code_short, 0)
        
        # Test with --max_length
        console_out_long, return_code_long = self.run_command(f'bin/filtlong --max_length 120 {self.test_fastq}')
        self.assertEqual(return_code_long, 0)
        
        # Both should produce the same output (only reads <= 120bp)
        self.assertEqual(console_out_short, console_out_long)
        # Should only contain read1_short (50bp) and read3_low_quality (100bp), not read2_long (150bp)
        self.assertIn('read1_short', console_out_short)
        self.assertIn('read3_low_quality', console_out_short)
        self.assertNotIn('read2_long', console_out_short)
    
    def test_min_mean_q_short_option(self):
        """Test that -q option works the same as --min_mean_q."""
        # Test with -q
        console_out_short, return_code_short = self.run_command(f'bin/filtlong -q 20 {self.test_fastq}')
        self.assertEqual(return_code_short, 0)
        
        # Test with --min_mean_q
        console_out_long, return_code_long = self.run_command(f'bin/filtlong --min_mean_q 20 {self.test_fastq}')
        self.assertEqual(return_code_long, 0)
        
        # Both should produce the same output (only reads with mean quality >= 20)
        self.assertEqual(console_out_short, console_out_long)
        # Should only contain read1_short and read2_long (high quality 'I'), not read3_low_quality (low quality '!')
        self.assertIn('read1_short', console_out_short)
        self.assertIn('read2_long', console_out_short)
        self.assertNotIn('read3_low_quality', console_out_short)
    
    def test_combined_short_options(self):
        """Test that short options can be combined together."""
        # Test combining -l and -L
        console_out, return_code = self.run_command(f'bin/filtlong -l 75 -L 120 {self.test_fastq}')
        self.assertEqual(return_code, 0)
        # Should only contain read3_low_quality (100bp, between 75-120)
        self.assertNotIn('read1_short', console_out)
        self.assertNotIn('read2_long', console_out)
        self.assertIn('read3_low_quality', console_out)
    
    def test_short_options_help(self):
        """Test that help shows the new short options."""
        console_out, return_code = self.run_command('bin/filtlong --help')
        self.assertEqual(return_code, 0)
        # Should show short options in help
        self.assertIn('-l[int], --min_length', console_out)
        self.assertIn('-L[int], --max_length', console_out)
        self.assertIn('-q[float], --min_mean_q', console_out)


if __name__ == '__main__':
    unittest.main()