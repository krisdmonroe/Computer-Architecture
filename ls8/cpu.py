"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        #Setup some amount of digits
        self.ram = [0] * 256 
        self.reg = [0] * 8
        self.pc = 0
        self.ir = 0
        self.FL = 0
        self.running = True
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.HLT = 0b00000001
        self.MULT = 0b10100010
        self.PUSH = 0b01000101
        self.POP = 0b01000110
        self.CAll = 0b01010000
        self.ADD = 0b10100000
        self.RET = 0b00010001
        self.CMP = 0b10100111
        self.JEQ = 0b01010101
        self.JMP = 0b01010100
        self.JNE = 0b01010110
        self.NOP = 0b00000000
        self.branch_table = {
                self.LDI:self.ldi,
                self.PRN:self.prn,
                self.MULT:self.mult,
                self.PUSH:self.push,
                self.POP:self.pop,
                self.CAll:self.call,
                self.ADD:self.add,
                self.RET:self.ret,
                self.CMP:self.cmp_,
                self.JEQ:self.jeq,
                self.JMP:self.jmp,
                self.JNE:self.jne,
                self.NOP:self.nop,
                self.HLT:self.hlt,
            }
        # instruction_length = ((IR & 0b11000000) >>6) + 1
        # set_pc = ((IR & 0b00010000) >> 4)
        # use_alu = ((IR & 0b00100000) >> 5)
        ## Instruction Layout
        # Meanings of the bits in the first byte of each instruction: `AABCDDDD`
        # * `AA` Number of operands for this opcode, 0-2
        # * `B` 1 if this is an ALU operation
        # * `C` 1 if this instruction sets the PC
        # * `DDDD` Instruction identifier
        self.sp = 7 
        self.reg[self.sp] = 0xf4

    #figure out how to do sp here
    def load(self):
        """Load a program into memory."""
        filename = sys.argv[1]
        with open(filename) as f:  # opens file
            address = 0
            for line in f: # reads file line by line
                line = line.split('#')
                line = line[0].strip() #list
                if line == '':
                    continue
                #turns the line into <int> instead of string store the address in memory
                self.ram[address] = int(line, base=2) 
                address +=1 #add one and goes to the next
                # print(line)                
        # print(self.ram[:15])
        # sys.exit(0)
        

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     # self.ram[address] = instruction
        #     self.ram_write(instruction, address)
        #     address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MULT":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'CMP':
            # 00 0 0 0LGE
            # 10 1 0 0100 - Less than
            # 10 1 0 0010 - Greater
            # 10 1 0 0001 - Equal To
            # * If they are equal, set the Equal `E` flag to 1, otherwise set it to 0.
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL = 0b00000001
            # * If registerA is less than registerB, set the Less-than `L` flag to 1,
            # otherwise set it to 0.
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.FL = 0b00000100
            # * If registerA is greater than registerB, set the Greater-than `G` flag
            # to 1, otherwise set it to 0.
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.FL = 0b00000010
            else:
                self.FL = 0b00000000
        else:
            raise Exception("Unsupported ALU operation")

    # def trace(self):
    #     """
    #     Handy function to print out the CPU state. You might want to call this
    #     from run() if you need help debugging.
    #     """

    #     print(f"TRACE: %02X | %02X %02X %02X |" % (
    #         self.pc,
    #         #self.fl,
    #         #self.ie,
    #         self.ram_read(self.pc),
    #         self.ram_read(self.pc + 1),
    #         self.ram_read(self.pc + 2)
    #     ), end='')

    #     for i in range(8):
    #         print(" %02X" % self.reg[i], end='')

    #     print()
    def trace(self, LABEL=str()):
        
        print(f"{LABEL} TRACE --> PC: %02i | RAM: %03i %03i %03i | Register: " % (
            self.pc,
            # self.FL,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')
        for i in range(8):
            print(" %02i" % self.reg[i], end='')
        print(" | Stack:", end='')
        
        for i in range(240, 244):
            print(" %02i" % self.ram_read(i), end='')
        print()

    def run(self):
        """Run the CPU."""
        # pc = 0
        # running = True
        while self.running:
            ir = self.ram_read(self.pc) #instruction register
            # print(bin(ir))
            # -------------------------------------------
            #            Example: branch_table[n](x, y) Not necessary to pass in x or y just yet but mayb
            # -------------------------------------------
            if ir in self.branch_table:
                self.branch_table[ir]() #Do not forget to use () to activate the function you are calling
                # self.trace()
            else:
                print(f'Unkown instruction {self.ir} at address {self.pc}')
                sys.exit(1)
        
    def ram_read(self, pc):
        return self.ram[pc]

    def ram_write(self, value, pc):
        self.ram[pc] = value
        
    def ldi(self):
        reg_num = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.reg[reg_num] = value
        self.pc += 3
        # if self.ir == 0b10000010: # Set the value of a register to an integer.
        #     #register a number with pc in memory starting at the command 0b10000010
        #     # reg_num = self.ram[self.pc + 1]
        #     # value = self.ram[self.pc + 2]
        #     reg_num = self.ram_read(self.pc + 1)
        #     value = self.ram_read(self.pc + 2)
        #     # add the value of reg_num or the first place after the command to value
        #     self.reg[reg_num] = value
        #     #update pc based on location in program
        #     self.pc += 3

    def prn(self):
        print(self.reg[self.ram_read(self.pc + 1)])
        self.pc += 2
        # if self.ir == 0b01000111:
        #     # reg_num = self.ram[self.pc + 1]
        #     # print(self.reg[reg_num])
        #     print(self.reg[self.ram_read(self.pc + 1)])
        #     self.pc += 2

    def hlt(self):
        self.running = False
        # if self.ir == 0b00000001:
        #     running = False

    def mult(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.alu("MULT", reg_a, reg_b)
        self.pc += 3
        # if self.ir == 0b10100010:
        #     reg_a = self.ram[self.pc + 1]
        #     reg_b = self.ram[self.pc + 2]
        #     self.alu("MULT", reg_a, reg_b)
        #     self.pc += 3

    def add(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.alu("ADD", reg_a, reg_b)
        self.pc += 3

    def push(self):
        self.reg[self.sp] -= 1
        # Copy the value given to the address pointed by SP
        reg_num = self.ram[self.pc+1]
        value = self.reg[reg_num]
        # Figure where to put it
        top_of_stack_addr = self.reg[self.sp]
        # put it there
        self.ram[top_of_stack_addr] = value
        self.pc += 2

    def pop(self):
        # 1. Copy the value from the address pointed to by `SP` to the given register.
        reg_index = self.ram_read(self.pc + 1)
        self.reg[reg_index] = self.ram[self.reg[self.sp]]
        # 2. Increment `SP`.
        self.reg[self.sp] += 1
        #increment the pc
        self.pc += 2

    def call(self):
        return_addr = self.pc + 2   # Where we're going to RET to

		# Push on the stack
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = return_addr

		# Get the address to call
        reg_num = self.ram[self.pc + 1]
        subroutine_addr = self.reg[reg_num]

		# Call it
        self.pc = subroutine_addr

    def ret(self):
        # Pop the value from the top of the stack and store it in the `PC`.
        #this should be the top of stack
        top_of_stack_addr = self.reg[self.sp]
        # store pc as the value at the top of stack
        return_addr = self.ram[top_of_stack_addr]
        self.pc = return_addr
        self.reg[self.sp] += 1

    def nop(self):
        pass
        
#Extra stuff for practice ----------------------------------------------------------------------------------------------- 
#-----------------------------------------------------------------------------------------------------------
    def jmp(self):
        # Jump to the address stored in the given register.
        # Set the `PC` to the address stored in the given register.
        address = self.ram_read(self.pc + 1)
        self.pc = self.reg[address]

    def cmp_(self):
        # Compare the values in two registers.
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("CMP", reg_a, reg_b)
        self.pc += 3
        # *This is an instruction handled by the ALU.*
        # Go to alu for more code
    
    def jeq(self):
        # If `equal` flag is set (true), jump to the address stored in the given register.
        address = self.ram_read(self.pc + 1)
        if self.FL == 0b00000001:
            self.pc = self.reg[address]
        else:
            self.pc += 2

    def jne(self):
        # If `E` flag is clear (false, 0), jump to the address stored in the given
        # register.
        address = self.ram_read(self.pc + 1)
        if self.FL != 0b00000001:
            self.pc = self.reg[address]
        else:
            self.pc += 2
    # python3 ls8.py examples/sctest.ls8
