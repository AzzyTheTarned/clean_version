class Token:
    def __init__(self, token, lexeme, row, column):
        self.token = token
        self.lexeme = lexeme
        self.row = row
        self.column = column

    def __str__(self):
        return f'Токен: {self.token} Лексема: {self.lexeme}'


class Node:
    def __init__(self, node_type, value=None, parent=None):
        self.node_type = node_type
        self.value = value
        self.parent = parent
        self.children = []

    def add_child(self, child):
        child.parent = self
        self.children.append(child)


def find_node(root, value):
    # Проверяем, совпадает ли значение текущего узла с искомым
    if root.value == value:
        return root

    # Рекурсивно ищем в дочерних узлах
    for child in root.children:
        result = find_node(child, value)
        if result is not None:
            return result

    # Если узел не найден, возвращаем None
    return None


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current_token(self):
        '''Возвращает текущий токен'''
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def consume(self, expected_type):
        '''Поглощает токен, то есть сдвигает позицию self.position
        если текущий токен соответствует expected_type'''
        if self.position < len(self.tokens) and self.tokens[self.position].token == expected_type:
            self.position += 1
        else:
            raise Exception(f'Expected token type {expected_type}')

    def checkTokensList(self, tokenlist):
        '''Поглощает последовательность токенов, если она
        соответствует tokenlist'''
        # переменная position вводится для того,
        # чтобы не изменять реальную позицию пока мы
        # не убедимся, что последовательность токенов
        # соответствует tokenlist
        position = self.position
        for i in tokenlist:
            if self.tokens[position].token != i:
                return False
            # если мы не в конце программы,
            # то все ок, смещаемся дальше
            if position < len(self.tokens):
                position += 1
            else:
                return False
        # цикл подошел к концу, теперь можно поменять реальную позицию на нашу
        self.position = position
        return True

    def parse_program(self):
        '''Парсит (добавляет узлы в дерево) прямые потомки Program, то есть
        заголовки, пространство имен, главную функцию, также тут должны быть
        обычные функции (они объявляются на одном уровне с main), классы,
        константы и тд'''
        node = Node('Program')
        while self.position < len(self.tokens):
            node.add_child(self.parse_headers())
            token = self.current_token()
            if token.token == 'K11':
                node.add_child(self.parse_namespace())
            else:
                print(token.token)
            node.add_child(self.parse_main())
        return node

    def parse_namespace(self):
        '''Парсит пространство имен (пока только std)'''
        node = Node('Namespaces')
        thistokenlist = ['K11', 'K13', 'K26', 'D3']
        if self.checkTokensList(thistokenlist):
            node.add_child(Node('Namespace', 'std'))
            return node
        else:
            raise Exception('ошибка пространства имен')

    def parse_headers(self):
        '''Парсит заголовки (любые)'''
        token = self.current_token()
        node = Node('Headers')
        while token.token == 'P1':
            thistokenlist = ['P1', 'O21', 'ID', 'O19', 'O28']
            if self.checkTokensList(thistokenlist):
                node.add_child(Node('ID', self.tokens[self.position - 3].lexeme))
            else:
                raise Exception('ошибка объявления заголовка')
            token = self.current_token()
        return node

    def parse_main(self):
        '''Парсит главную функцию'''
        thistokenlist = ['K17', 'K32', 'D6', 'D7', 'D4']
        if self.checkTokensList(thistokenlist):
            node = Node('MainFunction')
            node.add_child(self.parse_body())
            token = self.current_token()
            if token.token == 'D5':
                self.consume('D5')
                return node
            else:
                raise Exception('не закрыта фигурная скобка')
        else:
            raise Exception('ошибка объявления главной функции')

    def parse_body(self):
        '''Парсит тело функции (любой)'''
        node = Node('Body')
        node.add_child(self.parse_code_block())
        while self.position < len(self.tokens) - 1:
            node.add_child(self.parse_code_block())
        return node

    def parse_code_block(self):
        '''Парсит инструкции внутри тела функции. Пока
        что только объявление переменных, ввод/вывод, присваивание'''
        node = Node('Instruction')
        token = self.current_token()
        if token.token in ['K17', 'K18', 'K22']:
            node.add_child(self.parse_declaration())
        elif token.token == 'K24':
            node.add_child(self.parse_cout())
        elif token.token == 'K25':
            node.add_child(self.parse_cin())
        elif token.token == 'ID':
            node.add_child(self.parse_assignment())
        elif token.token == 'K4':
            node.add_child(self.parse_while())
        # тут надо сделать проверку на if и class, однако в прошлом коде и у нас тут по разному выглядит, так что хз как это делать

        else:
            print('exeption', token.token, token.row, token.column, self.position)
            raise Exception('ошибка в блоке кода')
        return node


    #сюда добавил if и class болки, надо только их объявить в parse_code_block что бы проверить

    def ifBlock(self, spp, indent):
        self.show(indent, 'ifBlock', spp)
        indent += ' '
        spp1 = spp

        if self.tokens[spp] == 'K6':  # if
            spp += 1
            if self.tokens[spp] == 'D6':  # (
                spp += 1
                if self.tokens[spp] == 'ID':  # условие
                    spp += 1
                    if self.tokens[spp] == 'O24':  # ==
                        spp += 1
                        if self.tokens[spp] == 'N1':  # число
                            spp += 1
                            if self.tokens[spp] == 'D7':  # )
                                spp += 1
                                if self.tokens[spp] == 'D4':  # {
                                    spp += 1
                                    # Рекурсивная проверка тела блока
                                    res, spp = self.body(spp, indent)
                                    if res and self.tokens[spp] == 'D5':  # }
                                        return True, spp + 1
        return False, spp1
    
    def statement(self, spp, indent):
        indent += ' '
        if spp < len(self.tokens) and self.tokens[spp] in ['K6']:  # if
            return self.ifStatement(spp, indent)
        # Добавить другие типы statement: while, for, присваивания и т.д.
        return False, spp

    def ifStatement(self, spp, indent):
        self.show(indent, 'ifStatement', spp)
        indent += ' '
        thistokenlist = ['K6', 'D6', 'ID', 'O24', 'N1', 'D7', 'D4']
        res, spp = self.checkTokensList(spp, thistokenlist)
        if res:
            res, spp = self.body(spp, indent)
            return res and self.tokens[spp] == 'D5', spp + 1
        return False, spp

    def classBlock(self, spp, indent):
        self.show(indent, 'classBlock', spp)
        indent += ' '
        spp1 = spp
        thistokenlist = ['K9', 'ID', 'O29', 'ID', 'D4']  # Ожидаемый список токенов для начала класса
        res, spp = self.checkTokensList(spp, thistokenlist)
        if res:
            # После успешной проверки на начало класса, проходим по телу класса
            while spp < len(self.tokens) and self.tokens[spp] != 'D5':  # Ищем конец класса (D5)
                res, spp = self.classBody(spp, indent)
                if not res:
                    return False, spp  # Если не удалось обработать тело класса, возвращаем False
            # Если мы дошли до D5, значит, класс завершен
            if self.tokens[spp] == 'D5':
                return True, spp + 1  # Пропускаем D5 и возвращаем результат
        thistokenlist = ['ID', 'ID', 'O23', 'ID', 'D6', 'N1', 'D7', 'D3']
        res, spp = self.checkTokensList(spp, thistokenlist)
        if res:
            return True, spp + 1
        print(spp)
        return False, spp1  # Если проверка не прошла, возвращаем False и оригинальный индекс

    def classBody(self, spp, indent):
        self.show(indent, 'classBody', spp)
        indent += ' '
        spp1 = spp
        if self.tokens[spp] == 'ID' and self.tokens[spp + 1] == 'D6':  # Constructor
            while self.tokens[spp] != 'D5':
                spp += 1
            return True, spp + 1
        # Проверка для обычных методов, например, сеттеров или геттеров
        if self.tokens[spp] in ['K20', 'K17'] and self.tokens[spp + 1] == 'ID':  # Метод
            while self.tokens[spp] != 'D5':spp += 1
            return True, spp + 1
        # Если переменная
        if self.tokens[spp] in ['K17', 'K18', 'K22']:  # Типы данных
            if self.tokens[spp + 1] == 'ID':  # Переменная
                while self.tokens[spp] != 'D5':
                    spp += 1
                return True, spp + 1

        return False, spp1
    
    #конец добавления
    
    def parse_declaration(self):
        '''Парсит объявление переменных'''
        token = self.current_token()
        if token.token in ['K17', 'K18', 'K22']:
            var_node = Node('VariableDeclaration')
            var_type = token.lexeme
            self.consume(token.token)
            var_node.add_child(Node('Type', var_type))
            var_node.add_child(self.parse_identifier())
            token = self.current_token()
            if token.token == 'O23':
                self.consume('O23')  # '='
                var_node.add_child(self.parse_expression())
            token = self.current_token()
            if token.token == 'D3':
                self.consume('D3')  # ';'
            else:
                raise Exception('пропущена точка с запятой')
            return var_node
        raise Exception('Unexpected token')

    def parse_cout(self):
        '''Парсит вывод'''
        if self.tokens[self.position].token == 'K24':
            self.consume('K24')
            if self.tokens[self.position].token == 'O25':
                self.consume('O25')
                token = self.tokens[self.position]
                if token.token == 'ID' or token.token == 'N1' or token.token == 'N2' or token.token == 'N3':
                    self.consume(token.token)
                    if self.tokens[self.position].token == 'D3':
                        self.consume('D3')
                        node = Node('Cout', token.lexeme)
                        return node
        raise Exception('Ошибка вывода')

    def parse_cin(self):
        '''Парсит ввод'''
        if self.tokens[self.position].token == 'K25':
            self.consume('K25')
            if self.tokens[self.position].token == 'O26':
                self.consume('O26')
                token = self.tokens[self.position]
                if token.token == 'ID':
                    self.consume(token.token)
                    if self.tokens[self.position].token == 'D3':
                        self.consume('D3')
                        node = Node('Cin')
                        node.add_child(Node('Identifirer', token.lexeme))
                        return node
        raise Exception('Ошибка ввода')

    def parse_identifier(self):
        '''Парсит идентификтор (слегка бесполезная функция,
        от нее можно отказаться)'''
        token = self.current_token()
        if token.token == 'ID':
            id_node = Node('Identifier', token.lexeme)
            self.consume('ID')
            return id_node
        raise Exception('Expected identifier')

    def parse_assignment(self):
        '''Парсит присваивание, пытаюсь запихнуть сюда
        и присваивание математических/логических выражений.
        пока что присвоить можно только значение или идентификатор'''
        node = Node('Assignment')
        node.add_child(self.parse_identifier())
        token = self.current_token()
        if token.token == 'O2':
            node.add_child(Node('++Operator', token.lexeme))
            self.consume('O2')
            if self.tokens[self.position].token == 'D3':
                self.consume('D3')
                return node

        if token.token == 'O5':
            node.add_child(Node('--Operator', token.lexeme))
            self.consume('O5')
            if self.tokens[self.position].token == 'D3':
                self.consume('D3')
                return node

        if token.token in ['O23', 'O6', 'O3', 'O8', 'O10', 'O12', 'O24']:
            if token.token == 'O24':
                node.add_child(Node('Operator', token.lexeme))
            else:
                node.add_child(Node('AssigOperator', token.lexeme))
            self.consume(token.token)
            node.add_child(self.parse_expression())
            while self.tokens[self.position].token != 'D3':
                token = self.current_token()
                if token.token in ['O1', 'O4', 'O7', 'O11', 'O9', 'O24']:
                    node.add_child(Node('Operator', token.lexeme))
                    self.consume(token.token)
                    node.add_child(self.parse_expression())
            if self.tokens[self.position].token == 'D3':
                self.consume('D3')
                return node
            else:
                raise Exception('ошибка выражения3')
        else:
            raise Exception('ошибка выражения1')

    def parse_expression(self):
        '''Парсит значение переменной (тоже слегка бесполезная функция)'''
        token = self.current_token()
        if token.token == 'N1':
            value_node = Node('Integer', token.lexeme)
            self.consume('N1')
            return value_node
        elif token.token == 'N2':
            value_node = Node('Float', token.lexeme)
            self.consume('N2')
            return value_node
        elif token.token == 'N3':
            value_node = Node('String', token.lexeme)
            self.consume('N3')
            return value_node
        elif token.token == 'K21' or token.token == 'K23':
            value_node = Node('Boolean', token.lexeme)
            self.consume(token.token)
            return value_node
        else:
            raise Exception('Expected expression')

    def parse_while(self):
        '''Парсит цикл while'''
        node = Node('While')
        token = self.current_token()

        if token.token == 'K4':
            self.consume('K4')
            condition_node = Node('Condition')
            token = self.current_token()

            if token.token == 'D6':
                self.consume('D6')
                condition_node.add_child(self.parse_expression())
                token = self.current_token()

                while token.token != 'D7':
                    if token.token in ['O1', 'O4', 'O7', 'O11', 'O9', 'O24']:
                        condition_node.add_child(Node('Operator', token.lexeme))
                        self.consume(token.token)
                        condition_node.add_child(self.parse_expression())
                    token = self.current_token()

                if token.token == 'D7':
                    self.consume('D7')
                    node.add_child(condition_node)

                    if self.current_token().token == 'D4':
                        self.consume('D4')
                        body_node = Node('Body')

                        while self.current_token().token != 'D5':
                            body_node.add_child(self.parse_code_block())

                        self.consume('D5')
                        node.add_child(body_node)
                        return node
                    else:
                        raise Exception('Expected "{" after while condition')
                else:
                    raise Exception('Expected ")" after while condition')
            else:
                raise Exception('Expected "(" after while')
        else:
            raise Exception('Expected "while" keyword')

    def print_syntax_tree(self, node, level=0):
        '''Рекурсивно выводит синтаксическое дерево.'''
        if node is None:
            return
        print("\t" * level + f"{node.node_type}: {node.value if node.value is not None else ''}")
        for child in node.children:
            self.print_syntax_tree(child, level + 1)
