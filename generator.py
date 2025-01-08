class CodeGenerator:
    def __init__(self):
        self.code = []

    def generate(self, node):
        if node.node_type == 'Program':
            for child in node.children:
                self.generate(child)
        elif node.node_type == 'Headers':
            pass
        elif node.node_type == 'Namespaces':
            pass
        elif node.node_type == 'MainFunction':
            self.code.append("public class Main {")
            self.code.append("public static void main(String[] args) {")
            for child in node.children:
                self.generate(child)
            self.code.append("}")
            self.code.append("}")
        elif node.node_type == 'While':
            for child in node.children:
                if child.node_type == 'Condition':
                    self.code.append(f'while ({" ".join([sub_child.value for sub_child in child.children])})' + '{')
                if child.node_type == 'Body':
                    for sub_child in child.children:
                        self.generate(sub_child)
                    self.code.append('}')
        elif node.node_type == 'Body':
            for child in node.children:
                self.generate(child)
            if 'Scanner scanner = new Scanner(System.in);' in self.code:
                self.code.append('scanner.close();')
        elif node.node_type == 'Instruction':
            for child in node.children:
                self.generate(child)
        elif node.node_type == 'VariableDeclaration':
            var_type = node.children[0].value
            identifier = node.children[1].value
            if len(node.children) > 2:
                self.code.append(f'{var_type} {identifier} = {node.children[2].value};')
            else:
                self.code.append(f'{var_type} {identifier};')
        elif node.node_type == 'Assignment':
            identifier = node.children[0].value
            assign_operator = node.children[1].value
            self.code.append(f'{identifier} {assign_operator} {" ".join([child.value for child in node.children[2:]])};')
        elif node.node_type == 'Cout':
            self.code.append(f'System.out.println({node.value});')
        # сложные махинации с Cin
        elif node.node_type == 'Cin':
            value = node.children[1].value
            if 'import java.util.Scanner;' not in self.code:
                self.code.insert(0, 'import java.util.Scanner;')
            if 'Scanner scanner = new Scanner(System.in);' not in self.code:
                self.code.append('Scanner scanner = new Scanner(System.in);')
            if value == 'string':
                type = 'Line'
            elif value == 'int':
                type = 'Int'
            elif value == 'bool':
                type = 'Boolean'
            elif value == 'float':
                type = 'Double'
            else:
                raise Exception(f'ошибка типа данных считываемой переменной{node.children[0].value}')
            self.code.append(f'{node.children[0].value} = scanner.next{type}();')

        else:
            raise Exception(f'Unknown node type: {node.node_type}')

    def get_code(self):
        return "\n".join(self.code)
