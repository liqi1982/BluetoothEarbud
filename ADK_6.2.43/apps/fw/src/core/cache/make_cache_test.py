# Copyright (c) 2016 Qualcomm Technologies International, Ltd.
#   Part of 6.2
import sys
import os

class MakeCacheTestFile():
    '''
    This class creates some C files with many functions that are designed to
    test the program read cache of the application subsystem in crescendo.
    '''
    def __init__(self, filename, file_num, num_functions):
        self.filename = filename
        self.num_functions = num_functions
        self.file_num = file_num
    
    def create(self):
        print "Making file %s" % self.filename
        self.fd = file(self.filename, "wb")
        self.write_c_header()
        for i in range(self.num_functions):
            self.create_test_fn(i)
        self.create_caller_function(self.num_functions)
        self.fd.close()

    def write_c_header(self):
        self.fd.write("/**\n")
        self.fd.write(" * C File autogenerated by %s\n" % sys.argv[0])
        self.fd.write(" */\n")
        self.fd.write('#include "cache/cache.h"\n')
        self.fd.write("\n")
        
    def create_test_fn(self, num):
        fd = self.fd
        fd.write("\n")
        fd.write("static uint32 cache_test_fn_%d(uint32 seed, uint32 loops)\n"
                                                                         % num)
        fd.write("{\n")
        fd.write("    uint32 loop;\n")
        fd.write("    uint32 value = seed * %d;\n" % num)
        fd.write("    if (value & 0x20)\n")
        fd.write("    {\n")
        fd.write("        for(loop=0; loop<loops; ++loop)\n")
        fd.write("        {\n")
        fd.write("            uint32 xor_value = value + loop + %d;\n" % num)
        fd.write("            uint32 shift = (loop+2) & cache_const_mask[%d];\n" 
                                                               % (num%20))
        fd.write("            xor_value = (xor_value << shift) |"
                                       " (xor_value >> (32-shift));\n")
        fd.write("            value = value ^ xor_value;\n")
        fd.write("        }\n")
        fd.write("    }\n")
        fd.write("    else\n")
        fd.write("        for(loop=loops; loop; --loop)\n")
        fd.write("        {\n")
        fd.write("            uint32 xor_value = value + loop + %d;\n" 
                                                                    % (num+1))
        fd.write("            uint32 shift = (loop+7) & 31;\n")
        fd.write("            xor_value = (xor_value << shift) |"
                                       " (xor_value >> (32-shift));\n")
        fd.write("            value = value ^ xor_value;\n")
        fd.write("        }\n")
        fd.write("    return value;\n")
        fd.write("}\n")
    
    def create_caller_function(self, num):
        self.fd.write("uint32 cache_test_%d(uint32 value, uint32 loops)\n" 
                                                                % self.file_num)
        self.fd.write("{\n")
        
        for i in range(num):
            self.fd.write("    value = cache_test_fn_%d(value, loops);\n" % (i))
            
        self.fd.write("    return value;\n")
        self.fd.write("}\n")
        

if __name__ == "__main__":
    for i in range(8):
        filename = os.sep.join([os.path.dirname(os.path.realpath(__file__)), 
                                        ("cache_test_%d.c" % (i+1))])
        make_file = MakeCacheTestFile(filename, i+1, 1000)
        make_file.create()
    print "Done"