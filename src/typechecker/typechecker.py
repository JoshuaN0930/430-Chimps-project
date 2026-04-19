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

        for func in self.program.funcs:
            self.typecheck_func(func)

        # the variable is the key and their value is their type
        env_variable = {}
        for stmt in self.program.stmts:
            if isinstance(stmt, ReturnStmt):
                raise Exception("Return statement not allowed")
            self.typecheck_stmt(stmt, env_variable, VoidType())




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
                # Adds the struct with its name being the key and the parameter dictionary as its value
                param_dict[param.name] = self.check_type(param.type)


    # Places each function in the program into a dictionary
    def get_func(self):
        for funcs in self.program.funcs:
            # Checks if a function with the same name is already in the dictionary
            if funcs.name in self.func_dict:
                raise Exception(f'Duplicate function found: {funcs.name}')

            param_names = set()
            param_types = []
            # Checks for any duplicate parameters
            for param in funcs.params:
                if param.name in param_names:
                    raise Exception(f'Duplicate parameter with the same name found: {param.name}')
                param_names.add(param.name)
                param_types.append(self.check_type(param.type))


            rtype = self.check_type(funcs.Rtype)

            self.func_dict[funcs.name] = {
                "param_types": param_types,
                "return": rtype
            }


    def typecheck_func(self, func):

        var_env = {}
        return_type = self.check_type(func.Rtype)

        for param in func.params:
            var_env[param.name] = self.check_type(param.type)

        for stmt in func.body:
            self.typecheck_stmt(stmt, var_env, return_type)





    def typecheck_lhs(self, left_hand, env_variable) -> Type:
        if isinstance(left_hand, AssignStmt):
            lhs = left_hand.lhs
        else:
            lhs = left_hand

        # variable assignment: (assign x 5)
        if isinstance(lhs, VarAssign):
            # Make sure the variable exists in the current environment
            if lhs.var not in env_variable:
                raise Exception(f"Variable not found: {lhs.var}")
            #returns type of the variable
            return env_variable[lhs.var]

        # Struct field assignment: (assign (. first value) 1)
        if isinstance(lhs, FieldStructAssign):
            # typecheck the base part before the field
            base_type = self.typecheck_lhs(lhs.lhs, env_variable)
            #base must be a struct type
            if not isinstance(base_type, StructType):
                raise Exception(f"Variable is not a valid StructType for field access: '{lhs.var}'")
            # make sure the struct exists in the struct dictionary
            if base_type.name not in self.struct_dict:
                raise Exception(f"Unknown struct type: '{base_type.name}'")
            # make sure the requested field exists in that struct
            if lhs.var not in self.struct_dict[base_type.name]:
                raise Exception(
                    f"StructType field '{lhs.var}' is not found in '{base_type.name}'"
                )
            # return type of field
            struct_var_type = self.struct_dict[base_type.name][lhs.var]
            return struct_var_type

        # assigning through an address:
        if isinstance(lhs, AssignToAddress):
            # typechecks the inner lhs
            inner_type = self.typecheck_lhs(lhs.lhs, env_variable)
            # the inner lhs must have a pointer type to dereference
            if not isinstance(inner_type, PointerType):
                raise Exception(f"Cannot assign through non-pointer type: {inner_type}")

            return inner_type.inner

        raise Exception(f"Invalid lhs: {lhs}")


    def typecheck_stmt(self, stmt, var_env, return_type):
        if isinstance(stmt, VarDecStmt):
            if stmt.name in var_env:
                raise Exception(f"Variable with same name in use: {stmt.name}")
            var_env[stmt.name] = self.check_type(stmt.type)

        elif isinstance(stmt, AssignStmt):
            left_type = self.typecheck_lhs(stmt, var_env)
            right_type = self.typechecker_exp(stmt.exp, var_env)

            if isinstance(stmt.exp, NullExp):
                if not isinstance(left_type, PointerType):
                    raise Exception(f"Cannot assign null to non-pointer type {left_type}")
            elif left_type != right_type:
                raise Exception(f"Cannot assign expression type {right_type} to lhs type {left_type}")

        elif isinstance(stmt, WhileStmt):
            while_env_var = var_env.copy()
            cond_type = self.typechecker_exp(stmt.exp, var_env)
            if not isinstance(cond_type, IntType):
                raise Exception(f"While condition must be int, got {cond_type}")
            self.typecheck_stmt(stmt.stmt, while_env_var, return_type)

        elif isinstance(stmt, IfStmt):
            cond_type = self.typechecker_exp(stmt.exp, var_env)
            if not isinstance(cond_type, IntType):
                raise Exception(f"If condition must be int, got {cond_type}")
            self.typecheck_stmt(stmt.then_stmt, var_env.copy(), return_type)
            if stmt.else_stmt is not None:
                self.typecheck_stmt(stmt.else_stmt, var_env.copy(), return_type)


        elif isinstance(stmt, BlockStmt):
            list_of_stmt = stmt.stmt
            block_env = var_env.copy()
            for stmts in list_of_stmt:
                self.typecheck_stmt(stmts, block_env, return_type)

        elif isinstance(stmt, PrintlnStmt):
            self.typechecker_exp(stmt.exp, var_env)

        elif isinstance(stmt, ExpStmt):
            self.typechecker_exp(stmt.exp, var_env)

        elif isinstance(stmt, ReturnStmt):
            if stmt.exp is None:
                if not isinstance(return_type, VoidType):
                    raise Exception(f"Incorrect return type: void, should be {return_type}")

            else:
                return_stmt_type = self.typechecker_exp(stmt.exp, var_env)
                if return_stmt_type != return_type:
                    raise Exception(f"Incorrect return type: {return_stmt_type}, should be {return_type}")

        else:
            raise Exception(f"Invalid statement: {stmt}")





    def typechecker_exp(self, exp, env_variable) -> Type:
        if isinstance(exp, IntLiteralExp):
            return IntType()
        raise Exception(f"Unhandled expression: {exp}")



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
# programs = Parser(tokenize("(struct Node(int value)((* Node) next))")).parse_program()
# programs = Parser(tokenize("(vardec int sum)")).parse_program()
programs = Parser(tokenize("(struct Node(int value)((* Node) next))(func length (((* Node) list)) int(vardec int retval)(assign retval 0)(while (!= list null)(block(assign retval (+ retval 1))(assign list (. (* list) next))))(return retval))(vardec Node first)(vardec Node second)(vardec Node third)(assign (. first value) 1)(assign (. first next) (& second))(assign (. second value) 2)(assign (. second next) (& third))(assign (. third value) 3)(assign (. third next) null)(println (call length (& first)))")).parse_program()


# programs = Parser(tokenize("(struct Node(int value)((* Node) next))(func length (((* Node) list)) int(vardec int retval)(assign retval 0)(vardec Node first)(assign (. first value) 1)(return retval))(vardec Node first)(vardec Node second)(vardec Node third)(assign (. first value) 1)(assign (. first next) (& second))(assign (. second value) 2)(assign (. second next) (& third))(assign (. third value) 3)(assign (. third next) null)(println (call length (& first)))")).parse_program()
#
tc = Typechecker(programs)
tc.typecheck()