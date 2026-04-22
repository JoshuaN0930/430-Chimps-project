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


    def typecheck_struct(self, struct):
        field_dict = self.struct_dict[struct.name]

        for field in struct.params:
            if field.name in field_dict:
                raise Exception(f'Duplicate field found: {field.name} in struct {struct.name}')
            
            field_type = self.check_nonvoid_type(field.type, f"field {field.name} of struct {struct.name}")
            field_dict[field.name] = field_type

    # Places each struct in the program into a dictionary
    def get_struct(self):
        for struct in self.program.structs:
            # Checks if a struct with the same name is already in the dictionary
            if struct.name in self.struct_dict:
                raise Exception(f"Duplicate struct found: {struct.name}")

            # Adds the struct name as a key with an empty dictionary for its fields
            self.struct_dict[struct.name] = {}

        for struct in self.program.structs:
            # Typechecks the fields of each struct and fills in its field dictionary
            self.typecheck_struct(struct)


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
                param_types.append(
                    self.check_nonvoid_type(param.type, f"parameter {param.name} of function {funcs.name}")
                )


            rtype = self.check_type(funcs.Rtype)

            self.func_dict[funcs.name] = {
                "param_types": param_types,
                "return": rtype
            }


    def typecheck_func(self, func):

        var_env = {}
        return_type = self.check_type(func.Rtype)

        for param in func.params:
            if param.name in var_env:
                raise Exception(f"Duplicate parameter name: {param.name}")
            var_env[param.name] = self.check_nonvoid_type(param.type, "function parameter")

        for stmt in func.body:
            self.typecheck_stmt(stmt, var_env, return_type)

        if not isinstance(return_type, VoidType):
            if not self.good_return_body(func.body):
                raise Exception(f"Function {func.name} may not return a value")





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
            var_env[stmt.name] = self.check_nonvoid_type(stmt.type, f"variable {stmt.name}")

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
            if not isinstance(cond_type, BoolType):
                raise Exception(f"While condition must be bool, got {cond_type}")
            self.typecheck_stmt(stmt.stmt, while_env_var, return_type)

        elif isinstance(stmt, IfStmt):
            cond_type = self.typechecker_exp(stmt.exp, var_env)
            if not isinstance(cond_type, BoolType):
                raise Exception(f"If condition must be bool, got {cond_type}")
            self.typecheck_stmt(stmt.then_stmt, var_env.copy(), return_type)
            if stmt.else_stmt is not None:
                self.typecheck_stmt(stmt.else_stmt, var_env.copy(), return_type)


        elif isinstance(stmt, BlockStmt):
            list_of_stmt = stmt.stmt
            block_env = var_env.copy()
            for stmts in list_of_stmt:
                self.typecheck_stmt(stmts, block_env, return_type)

        elif isinstance(stmt, PrintlnStmt):
            exp_type = self.typechecker_exp(stmt.exp, var_env)
            if not isinstance(exp_type, (IntType, BoolType, PointerType)):
                raise Exception(f"println only supports int, bool, and pointers, got {exp_type}")

        elif isinstance(stmt, ExpStmt):
            self.typechecker_exp(stmt.exp, var_env)

        elif isinstance(stmt, ReturnStmt):
            # checks if the return statement has no expression
            if stmt.exp is None:
                if not isinstance(return_type, VoidType):
                    raise Exception(f"Incorrect return type: void, should be {return_type}")

            else:
                # returns null
                if isinstance(stmt.exp, NullExp):
                    # null can only be returned from a function with a pointer return type
                    if not isinstance(return_type, PointerType):
                        raise Exception(f"Cannot return null for non-pointer return type {return_type}")
                else:
                    return_stmt_type = self.typechecker_exp(stmt.exp, var_env)
                    # checks that the expression type matches the function's return type
                    if return_stmt_type != return_type:
                        raise Exception(f"Incorrect return type: {return_stmt_type}, should be {return_type}")

        else:
            raise Exception(f"Invalid statement: {stmt}")





    def typechecker_exp(self, exp, env_variable) -> Type:

        #exp = 5
        if isinstance(exp, IntLiteralExp):
            return IntType()

        #exp = true/false
        elif isinstance(exp, BooleanLiteralExp):
            return BoolType()

        #exp = null
        elif isinstance(exp, NullExp):
            return NullType()

        #exp = lhs
        elif isinstance(exp, LhsExp):
            return self.typecheck_lhs(exp.lhs, env_variable)

        #exp = & lhs
        elif isinstance(exp, AddressOfExp):
            return PointerType(inner=self.typecheck_lhs(exp.lhs, env_variable))

        #exp = * exp
        elif isinstance(exp, DerefExp):
            t = self.typechecker_exp(exp.exp, env_variable)
            if not isinstance(t, PointerType):
                raise Exception(f"Cannot dereference non-pointer type: {t}")

            return t.inner

        #exp = (op exp exp)
        elif isinstance(exp, BinaryOpExp):
            left_type  = self.typechecker_exp(exp.first_exp, env_variable)
            right_type = self.typechecker_exp(exp.second_exp, env_variable)
            op = exp.op

            # Binop
            if isinstance(op, (AddOp, MinusOp, MultiplyOp, DivideOp)):
                if not isinstance(left_type, IntType) or  not isinstance(right_type, IntType):
                    raise Exception(f"Arithmetic operators require int operands, got ({left_type}) , ({right_type})")
                return IntType()

            # < comparasion
            if isinstance(op, LessThanOp):
                if not isinstance(left_type, IntType) or not isinstance(right_type, IntType):
                    raise Exception(f"require int on left and right, got ({left_type}) ({right_type})")
                return BoolType()

            #== !=
            if isinstance(op, (EqualOp, NotEqualOp)):
               if not self.types_compatible(left_type, right_type):
                   raise Exception(f"Cannot compare {left_type} with {right_type}")
               return BoolType()

            raise Exception(f"Unknown operator: {op}")

        #exp = call funcname exp*
        elif isinstance(exp, FunctionCallExp):
            #func must already exist
            if exp.func_name not in self.func_dict:
                raise Exception(f"Unknown Function: {exp.func_name}")

            func_info = self.func_dict[exp.func_name]
            expected_params = func_info["param_types"]
            return_type = func_info["return"]

            # check arity
            if len(exp.exp) != len(expected_params):
                raise Exception(f"Function {exp.func_name} expects arity {len(expected_params)}, got arity {len(exp.exp)}")

            #check var being passed in matches expected type
            for i, (arg, expected_type) in enumerate(zip(exp.exp, expected_params)):
                arg_type = self.typechecker_exp(arg, env_variable)
                if not self.types_compatible(expected_type, arg_type):
                    raise Exception(f"Arg {i} of {exp.func_name}: expected {expected_type}, got {arg_type}")

            return return_type

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

    # Checks that a type is valid and not void
    def check_nonvoid_type(self, type_value: Type, where: str) -> Type:
        # First makes sure the type itself is a valid type
        checked = self.check_type(type_value)
        # Raises an error if the type is void
        if isinstance(checked, VoidType):
            raise Exception(f"void is not allowed for {where}")
        return checked

    # Checks that a return type is valid
    def check_return_type(self, type_value: Type) -> Type:
        return self.check_type(type_value)


    def types_compatible(self, t1: Type, t2: Type) -> bool:
        if isinstance(t1, NullType) and isinstance(t2, PointerType):
            return True
        if isinstance(t2, NullType) and isinstance(t1, PointerType):
            return True
        return t1 == t2

    # Checks if a statement always returns
    def good_return_stmt(self, stmt) -> bool:
        # return statement always returns
        if isinstance(stmt, ReturnStmt):
            return True

        # block returns if any statement inside guarantees a return
        if isinstance(stmt, BlockStmt):
            for state in stmt.stmt:
                if self.good_return_stmt(state):
                    return True
            return False

        # if statement only guarantees a return if both branches return
        if isinstance(stmt, IfStmt):
            if stmt.else_stmt is None:
                return False
            return (
                    self.good_return_stmt(stmt.then_stmt)
                    and self.good_return_stmt(stmt.else_stmt)
            )

        # while loop does not guarantee a return because it may not run
        if isinstance(stmt, WhileStmt):
            return False

        # Any other kind of statement does not guarantee a return
        return False

    # Checks if a function body has a guaranteed return
    def good_return_body(self, stmts) -> bool:
        for stmt in stmts:
            # If one statement guarantees a return, then the body is good
            if self.good_return_stmt(stmt):
                return True
        # If no statement guarantees a return, then the body is not good
        return False




# Testing use
    # typecheck("(struct Node(int value)((* Node) next))(func length (((* Node) list)) int(vardec int retval)(assign retval 0)(while (!= list null)(block(assign retval (+ retval 1))(assign list (. (* list) next))))(return retval))(vardec Node first)(vardec Node second)(vardec Node third)(assign (. first value) 1)(assign (. first next) (& second))(assign (. second value) 2)(assign (. second next) (& third))(assign (. third value) 3)(assign (. third next) null)(println (call length (& first)))")
# programs = Parser(tokenize("(struct Node(int value)((* Node) next))")).parse_program()
# programs = Parser(tokenize("(vardec int sum)")).parse_program()
# programs = Parser(tokenize("(struct Node(int value)((* Node) next))(func length (((* Node) list)) int(vardec int retval)(assign retval 0)(while (!= list null)(block(assign retval (+ retval 1))(assign list (. (* list) next))))(return retval))(vardec Node first)(vardec Node second)(vardec Node third)(assign (. first value) 1)(assign (. first next) (& second))(assign (. second value) 2)(assign (. second next) (& third))(assign (. third value) 3)(assign (. third next) null)(println (call length (& first)))")).parse_program()
#programs = Parser(tokenize("(struct Node(int value)((* Node) next))(func length (((* Node) list)) int(vardec int retval)(assign retval 0)(while (!= list null)(block(assign retval (+ retval 1))(assign list (. (* list) next))))(return retval))(vardec Node first)(vardec Node second)(vardec Node third)(assign (. first value) 1)(assign (. first next) (& second))(assign (. second value) 2)(assign (. second next) (& third))(assign (. third value) 3)(assign (. third next) null)(println (call length (& first)))")).parse_program()
programs = Parser(tokenize("(func add ((int value)) int (vardec int retval) (assign retval (+ value 1)) (return retval))")).parse_program()
# programs = Parser(tokenize("(struct Node(int value)((* Node) next))(func length (((* Node) list)) int(vardec int retval)(assign retval 0)(vardec Node first)(assign (. first value) 1)(return retval))(vardec Node first)(vardec Node second)(vardec Node third)(assign (. first value) 1)(assign (. first next) (& second))(assign (. second value) 2)(assign (. second next) (& third))(assign (. third value) 3)(assign (. third next) null)(println (call length (& first)))")).parse_program()
#
tc = Typechecker(programs)
tc.typecheck()