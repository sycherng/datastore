import values

class Temp:
    def __init__(self, filter_string):
        self.parsed_query = {'-f': filter_string}


    def parseAdvancedFilter(self):
        max_paren_index, advanced_filters_tokens = self.tokenizeAdvancedFilter()
        filters_dict = self.getAdvancedFilter(advanced_filters_tokens, max_paren_index)
        return filters_dict

    def tokenizeAdvancedFilter(self):
        """(self) -> list<str>
        Goes through filter_string and tokenizes into a list of:

        name        | examples   
        ------------+------------
        operands    | REV=4.00, TITLE=oh baby,   my love == you
        operators   | AND, OR
        parentheses | (, )
        
        If invalid grammatically, raises error.
        """
        filter_string = self.parsed_query['-f']
        length = len(filter_string)
        tokens_list = []
        current_index = 0
        open_paren_count = 0
        max_paren_count = 0
        max_paren_index = 0
        expected_tokens = ['(', 'operand']
        while current_index < length:
            for expected_token in expected_tokens:
                print('ln35 expected token', expected_token, expected_token == ' ')
                end_index = None
                if expected_token == '(':
                    print(111)
                    if filter_string[current_index] == expected_token:
                        end_index = current_index
                        last_encountered_token = expected_token
                        break
                elif expected_token == ')':
                    print(222)
                    end_index = self.getCloseParenEndIndex(current_index, filter_string)
                    if end_index:
                        last_encountered_token = expected_token
                        break
                elif expected_token == 'operator':
                    print(333)
                    end_index = self.getOperatorEndIndex(current_index, filter_string)
                    if end_index:
                        last_encountered_token = expected_token
                        break
                elif expected_token == 'operand':
                    print(444)
                    end_index = self.getOperandEndIndex(current_index, filter_string)
                    print('ln58 end index for operand', end_index)
                    if end_index:
                        print(4441)
                        last_encountered_token = expected_token
                        break
                elif expected_token == ' ':
                    print(555)
                    if filter_string[current_index] == expected_token:
                        print(True)
                        end_index = current_index
                        last_encountered_token = expected_token
                        break
            #if no end index and current_index < len -1 (we havent reached the end of string), raise syntax error because valid tokens not found
            if not end_index and current_index < (length - 1): #haven't reached end of string
                raise SyntaxError(f"Invalid -f syntax at {filter_string[15:]}.")
            #add token to our tokens list
            print('ln73 end index, current index, length', end_index, current_index, length)
            print(666)
            if not end_index:
                end_index = len(filter_string)
            token = filter_string[current_index:end_index + 1]
            tokens_list.append(token)
            #update expected_tokens based on last_encountered_token
            expected_tokens = self.updateExpectedTokens(last_encountered_token, open_paren_count)
            prev_max_paren_count = max_paren_count
            max_paren_count, open_paren_count = self.updateOpenParenCount(last_encountered_token, open_paren_count, max_paren_count)
            #if max_paren_count was increased, update the index in which max_paren can be found in tokens_list
            if max_paren_count > prev_max_paren_count:
                max_paren_index = len(tokens_list) - 1
            #update current_index based on end_index
            current_index = end_index + 1

        #return our max_paren_index and tokens list
        print('ln77 tokens list', tokens_list)
        return max_paren_index, tokens_list

    def updateExpectedTokens(self, last_encountered_token, open_paren_count):
        if last_encountered_token == '(':
            expected_tokens = ['operand']
        elif last_encountered_token in [')', 'operator']:
            expected_tokens = [' ']
        elif last_encountered_token == 'operand':
            expected_tokens = [' ']
            if open_paren_count > 0:
                expected_tokens.append(')')
        elif last_encountered_token == ' ':
            expected_tokens = ['(', 'operator', 'operand']
        return expected_tokens 
                        
    def updateOpenParenCount(self, last_encountered_token, open_paren_count, max_paren_count):
        if last_encountered_token == '(':
            open_paren_count += 1
            if open_paren_count > max_paren_count:
                max_paren_count += 1
        elif last_encountered_token == ')':
            open_paren_count -= 1
        return max_paren_count, open_paren_count

    def getOperandEndIndex(self, start, string):
        """(self, int, str) -> int or None
        Starts with the suspected start index of an operand, 
        reads up to 9 valid characters and checks if it is a valid key,
        once valid key found, expects = sign,
        if = sign, reads until an operator or ) is encountered
        and returns that -1 as the end index of this operand.

        Otherwise return None."""

        print('ln117 string[start]', string[start:])
        key_end_index = self.getKeyEndIndex(start, string)
        print('ln119 key end index', key_end_index)
        if not key_end_index: #no valid keys found
            return None
        if string[key_end_index+1] != '=': #valid key not followed by =
            return None
        if string[key_end_index+2] == ')': #validkey=)
            return None

        current_index = key_end_index + 2

        print('ln135 string[currin:]', string[current_index:])
        for char in string[current_index:]:
            current_char = string[current_index]
            if current_char == ')':
                return current_index - 1
            else:
                end_index = self.getOperatorEndIndex(current_index, string)
                print('ln142 operator end ind', end_index)
                if end_index:
                    return current_index - 1
            current_index += 1
        return current_index

    #remove when merging into queryprocessor because is duplicate function
    def getKeyEndIndex(self, start, string):
        current_index = start
        for char in string[start:]:
            if current_index - start == 10:
                return
            elif char == '=':
                if string[start:current_index] not in values.VALID_KEYS:
                    return None
                else:
                    return current_index - 1
            elif not char.isalpha():
                return None
            current_index += 1


    def getOperatorEndIndex(self, start, string):
        """(self, int, str) -> int or None
        Starts with the suspected start index of an operator,
        reads up to 3 valid characters and checks if it is a valid operator,
        if it is valid, updates end index,
        checks if next token encountered is a ( or operand,
        if so, return end index.

        Otherwise returns None."""
        print('ln174 start:start3', string[start:start+3])
        if string[start:start + 3] == 'AND':
            end_index = start + 3
        elif string[start:start + 2] == 'OR':
            end_index = start + 2
        else: #no valid operator found
            return None

        next_char = string[end_index + 2]
        print('ln182')
        if next_char == '(':
            print('ln184')
            return end_index
        else:
            print('ln187')
            operand_end_index = self.getOperandEndIndex(end_index, string)
            if operand_end_index:
                print('ln190')
                return end_index


    def getAdvancedFilter(self, tokens, max_paren_index):
        filters_list = []
        self.evaluateScope(tokens, max_paren_index, filters_list)
        return filters_list

    def evaluateScope(self, tokens, start, filters_list):
        current = start
        while len(tokens) > 1 and not tokens[0].isdigit():
            operator_index = self.findOperatorIndex(tokens, current, 'AND')
            if operator_index:
                left = operator_index - 1
                right = operator_index + 1
            else:
                operator_index = self.findOperatorIndex(tokens, current, 'OR')
                left = operator_index - 1
                right = operator_index + 1
            if tokens[left] == '(':
                self.evaluateScope(tokens, left + 1, filters_list)
            elif tokens[right] == ')':
                self.evaluateScope(tokens, right - 1, filters_list)

            expression = []
            #add left operand to expression
            #if left operand isn't already a num, convert it from its operand form KEY=specification to a dict {KEY:specification}
            if not tokens[left].isdigit():
                operand = self.getOperand(tokens[left])
            expression.append(operand)

            #add operator to expression
            expression.append(tokens[operator_index])

            #if right operand isn't already a num, convert it from its operand form KEY=specification to a dict {KEY:specification}
            if not tokens[right].isdigit():
                operand = self.getOperand(tokens[right])
            expression.append(operand)

            #add our expression to our filters_list
            filters_list.append(expression)

            #replace tokens [left:right+1] with the index of the expression within filters_list
            tokens.pop(left)
            tokens.pop(right)
            tokens[operator_index] = len(filters_list)

            #if current scope is just (num), remove ( and ) from tokens
            if tokens[operator_index - 1] == '(' and tokens[operator_index + 1] == ')':
                tokens.pop(operator_index - 1)
                tokens.pop(operator_index + 1)

            current = operator_index

        print('ln218 filters list', filters_list)
        return filters_list 

    def findOperatorIndex(self, tokens, start, operator):
        current_index = start
        #search leftwards
        while current_index >= 0:
            if tokens[current_index] != operator:
                current_index -= 1
            else:
                return current_index

        current_index = start + 1
        length = len(tokens)
        while current_index < length:
            if tokens[current_index] != operator:
                current_index += 1
            else:
                return current_index

    @staticmethod
    def getOperand(token):
        split = token.split('=')
        key = split[0]
        value = '='.join(split[1:])
        return {key: value}

            


############TESTING#############
def test(filter_string, is_valid):
    print(filter_string, is_valid)
    x = Temp(filter_string)
    y = x.parseAdvancedFilter()
    return y

test("TITLE=unbreakable AND TITLE=zootopia", False)
test("TITLE=unbreakable OR TITLE=zootopia", True)
test("TITLE=despicable me AND REV=4.00 OR REV=3.00", True)
test("TITLE=despicable me AND (TITLE=zootopia OR TITLE=unbreakable)", False)
test("TITLE=despicable me AND REV=4.00 OR REV=3.00 AND DATE=2014-03-01 OR DATE=2014-03-01", True)
test("((TITLE=despicable me AND REV=4.00 OR REV=3.00) AND DATE=2014-03-01) OR DATE=2014-03-01", True)
#test("TITLE=despicable me AND ((REV=4.00 OR REV=3.00 AND DATE=2014-03-01) OR DATE=2014-03-01)", True)
