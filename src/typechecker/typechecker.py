
from src.parser.nodes import *
from src.parser.parser import *
from src.lexer.tokenizer import tokenize


class Typechecker:

    def __init__(self, program: Program):
        self.program = program
        self.struct_dict = {}
        self.func_dict = {}



    def typecheck(self):
        self.get_struct()
        self.get_func()












    # Places each struct in the program into a dictionary
    def get_struct(self):
        for struct in self.program.structs:
            # Checks if a struct with the same name is already in the dictionary
            if struct.name in self.struct_dict:
                raise Exception(f'Duplicate struct found: {struct.name}')
            self.struct_dict[struct.name] = {}

        for struct in self.program.structs:
            param_dict = self.struct_dict[struct.name]
            # Checks for any duplicate parameters
            for param in struct.params:
                if param.name in param_dict:
                    raise Exception(f'Duplicate parameter with the same name found: {param.name}')
                param_dict[param.name] = self.check_type(param.type)

            # Adds the struct with its name being the key and the parameter dictionary as its value
            self.struct_dict[struct.name] = param_dict

    # Places each function in the program into a dictionary
    def get_func(self):
        for funcs in self.program.funcs:
            # Checks if a function with the same name is already in the dictionary
            if funcs.name in self.func_dict:
                raise Exception(f'Duplicate function found: {funcs.name}')

            param_names = ()
            param_types = []
            # Checks for any duplicate parameters
            for param in funcs.params:
                if param.name in param_names:
                    raise Exception(f'Duplicate parameter with the same name found: {param.name}')
                param_types.append(self.check_type(param.type))


            rtype = self.check_type(funcs.Rtype)

            self.func_dict[funcs.name] = {
                "param_types": param_types,
                "return": rtype
            }


    # Check if it is a valid type
    def check_type(self, type_value: Type) -> Type:
        if isinstance(type_value, IntType):
            return type_value
        if isinstance(type_value, VoidType):
            return type_value
        if isinstance(type_value, StructType):
            if type_value.name not in self.struct_dict:
                raise Exception(f'Invalid struct type: {type_value}')
            return type_value
        if isinstance(type_value, PointerType):
            self.check_type(type_value.inner)
            return type_value
        raise Exception(f"Invalid type: {type_value}")










# Testing use
    # typecheck("(struct Node(int value)((* Node) next))(func length (((* Node) list)) int(vardec int retval)(assign retval 0)(while (!= list null)(block(assign retval (+ retval 1))(assign list (. (* list) next))))(return retval))(vardec Node first)(vardec Node second)(vardec Node third)(assign (. first value) 1)(assign (. first next) (& second))(assign (. second value) 2)(assign (. second next) (& third))(assign (. third value) 3)(assign (. third next) null)(println (call length (& first)))")
programs = Parser(tokenize("(struct Node(int value)((* Node) next))")).parse_program()
# programs = Parser(tokenize("(vardec int sum)")).parse_program()
tc = Typechecker(programs)
tc.typecheck()