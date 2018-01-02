# Copyright (c) 2012, Tenable Network Security
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
#
#    Redistributions of source code must retain the above copyright notice, 
#    this list of conditions and the following disclaimer.
#
#    Redistributions in binary form must reproduce the above copyright notice, 
#    this list of conditions and the following disclaimer in the documentation 
#    and/or other materials provided with the distribution.
#
#    Neither the name of the Tenable Network Security nor the names of its 
#    contributors may be used to endorse or promote products derived from this 
#    software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.

class TextTable():

    def __init__(self):
        self.pad = 2
        self.hr = '='
        self.cr = '-'
        self.header = ''
        self.__col_names = []
        self.__rows = []
        self.__col_widths = []
        self.__num_cols = 0
        self.__col_aligns = []

    
    def __set_num_cols(self, num_cols):
        if self.__num_cols == 0:
            self.__num_cols = num_cols
            
    
    def __set_col_align(self):
        for i in range(self.__num_cols):
            self.__col_aligns.append('<')
            

    def __col_check(self, num_cols):
        if num_cols == self.__num_cols:
            return True
        else:
            return False

            
    def __set_col_widths(self):
        for i in range(self.__num_cols):
            widths = [len(r[i]) for r in self.__rows]
            widths.append(len(self.__col_names[i]))
            self.__col_widths.append(max(widths))

            
    def add_col_align(self, aligns):
        if self.__col_check(len(aligns)):
            for align in aligns:
                if align in ['<', '^', '>']:
                    self.__col_aligns.append(align)
                else:
                    print 'Invalid alignment, using left alignment.'
                    self.__col_aligns.append('<')
        else:
            print 'Column number mismatch, column alignments not set.'
            

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row)

            
    def add_row(self, row):
        self.__set_num_cols(len(row))
        
        if self.__col_check(len(row)):
            self.__rows.append([str(r) for r in row])
        else:
            print 'Column number mismatch, row was not added to the table.'
            
        
    def add_col_names(self, col_names):
        self.__set_num_cols(len(col_names))
            
        if self.__col_check(len(col_names)):
            self.__col_names = col_names
        else:
            print 'Column number mismatch, headings were not added to the table.'
            
           
    def __str__(self):
        self.__set_col_widths()
        if self.__col_aligns == []:
            self.__set_col_align()
        
        s = '\n'

        # Print the header if there is one
        if self.header:
            s += ' ' * self.pad + self.header + '\n'
            s += ' ' * self.pad + self.hr * len(self.header) + '\n'
            s += '\n'

        # Print the column headings if there are any
        if self.__col_names:
            head = ' ' * self.pad
            rule = ' ' * self.pad
            
            for i in range(self.__num_cols):
                width = self.__col_widths[i]
                align = self.__col_aligns[i]
                name = self.__col_names[i]
                head += '{0:{j}{w}} '.format(name, j=align, w=width)
                rule += '{0:{j}{w}} '.format(self.cr * width, j=align, w=width)

            s += head + '\n'
            s += rule + '\n'

        # Print the rows
        for row in self.__rows:
            rstr = ' ' * self.pad
            
            for i in range(self.__num_cols):
                width = self.__col_widths[i]
                align = self.__col_aligns[i]
                rstr += '{0:{j}{w}} '.format(row[i], j=align, w=width)
                                
            s += rstr + '\n'
        #s += '\n'
        
        return s

if __name__ == '__main__':

    t1 = TextTable()
    t1.header = 'A Table of Numbers'
    t1.add_col_names(['Col1', 'Col2', 'Col3', 'Col4'])
    t1.add_col_align(['<', '<', '^', '>'])
    rows = [[1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12],
            [111111, 22222222, 3333333333, 444444444444]]
    t1.add_rows(rows)
    
    print t1
    
    t2 = TextTable()
    t2.header = 'Another Table of Numbers'
    t2.add_col_names(['Col1', 'Col2', 'Col3', 'Col4'])
    t2.add_row([1, 2, 3, 4])
    t2.add_row([5, 6, 7, 8])
    t2.add_row([9, 10, 11, 12])
    print t2