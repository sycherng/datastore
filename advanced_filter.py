import values

class AdvancedFilter:
    def __init__(self, parsed_query):
        self.filter_string = parsed_query['-f']


    def process(self):
        self.initial_tokens = self.tokenizeAdvancedFilter()
        self.tokens = self.initial_tokens.copy()
        self.filters_list = self.getAdvancedFilter()
        return self.filters_list

    def tokenizeAdvancedFilter(self):
        """(self) -> list<str>
        Goes through self.filter_string and tokenizes into a list of:

        name        | examples
        ------------+------------
        operands    | REV=4.00, TITLE=oh baby,   my love == you
        operators   | AND, OR
        parentheses | (, )

        If invalid grammatically, raises error.
        """
        length = len(self.filter_string)
        tokens_list = []
        open_paren_count = 0
        current_index = 0
        expected_tokens = ['(', 'operand']
        last_hit_operator_operand = None
        while current_index < length:
            end_index = None
            for expected_token in expected_tokens:
                if expected_token == '(':
                    if self.filter_string[current_index] == expected_token:
                        open_paren_count += 1
                        end_index = current_index
                        last_encountered_token = expected_token
                        break
                elif expected_token == ')':
                    if self.filter_string[current_index] == expected_token:
                        open_paren_count -=1
                        end_index = current_index
                        last_encountered_token = expected_token
                        break
                elif expected_token == ' ':
                    if self.filter_string[current_index] == expected_token:
                        end_index = current_index
                        last_encountered_token = expected_token
                        break
                elif expected_token == 'operator':
                    end_index = self.getOperatorEndIndex(current_index)
                    if end_index:
                        last_hit_operator_operand = 'operator'
                        last_encountered_token = expected_token
                        break
                elif expected_token == 'operand':
                    end_index = self.getOperandEndIndex(current_index)
                    if end_index:
                        last_hit_operator_operand = 'operand'
                        last_encountered_token = expected_token
                        break
            if end_index == None:
                raise SyntaxError(f"Invalid -f parameters at {self.filter_string[current_index:]}")

            #update what our token is
            token = self.filter_string[current_index:end_index + 1]

            #add token to our tokens list if it's not a space
            if token != ' ':
                tokens_list.append(token)

            #update expected_tokens based on last_encountered_token
            expected_tokens = AdvancedFilter.updateExpectedTokens(last_encountered_token, open_paren_count, last_hit_operator_operand)

            #update current_index based on end_index
            current_index = end_index + 1

        #return our max_paren_index and tokens list
        return tokens_list

    @staticmethod
    def updateExpectedTokens(last_encountered_token, open_paren_count, last_hit_operator_operand):
        #(
        if last_encountered_token == '(':
            expected_tokens = ['operand', '(']
        #operator
        elif last_encountered_token == 'operator':
            expected_tokens = [' ']
        #)
        elif last_encountered_token == ')':
            expected_tokens = [' ']
            if open_paren_count > 0:
                expected_tokens.append(')')
        #operand
        elif last_encountered_token == 'operand':
            expected_tokens = [' ']
            if open_paren_count > 0:
                expected_tokens.append(')')
        #space
        elif last_encountered_token == ' ':
            expected_tokens = ['(', 'operator', 'operand']

        #an operator cannot be followed by another operator
        #an operand cannot be followed by another operand
        if last_hit_operator_operand in expected_tokens:
            expected_tokens.remove(last_hit_operator_operand)

        return expected_tokens

    def getOperandEndIndex(self, start):
        """(self, int, str) -> int or None
        Starts with the suspected start index of an operand,
        tries to read all chars before the first = sign as a key,
        if it's invalid, return None.

        After this point:
        We know our operand must look like VALIDKEY=somearbitraryvalue

        our value may be any number of random characters including spaces
        we need to prove we've found the end of the operand before we can conclusively
        return our suspected end index of the operand. 

        using underscore to represent spaces to illustrate possible cases:
            KEY=randomcharsincludingspaces_AND_
            KEY=randomcharsincludingspaces)_
            KEY=randomcharsincludingspaces)

        in other words, after hitting the = sign we want to read until one of the following is found:
            SPACE + operator + SPACE
            ) + SPACE
            ) if it's the final char in the string
        
        if we find any of the above, that means what was prior to it was certainly an operand
        so return i - 1 as the end index of the operand.

        our final case is that this operand finishes our clause:
            KEY=randomcharsincludingspaces

        so we read until end of the string, and return the end index as end index of the operand.

        if none of the above cases were found, we return None.
        """
        #find VALIDKEY=
        eq_split_string = self.filter_string[start:].split('=')
        if eq_split_string[0] in values.VALID_KEYS:
            key_end_index = start + self.filter_string[start:].index('=')
        else:
            return None

        #try to find value after = sign
        current_index = key_end_index+1

        length = len(self.filter_string)
        for i in range(current_index, length):
            if self.filter_string[i] == ')':
                return i - 1
            elif i == length - 1:
                return i
            elif self.filter_string[i: i+5] == ' AND ':
                return i - 1
            elif self.filter_string[i: i+4] == ' OR ':
                return i - 1
        return None

    #@staticmethod
    def getOperatorEndIndex(self, start):
        """(self, int, str) -> int or None
        Starts with the suspected start index of an operator,
        tries to find a valid operator,
        if found returns the end index of that operator, otherwise returns None."""
        if self.filter_string[start:start + 3] == 'AND':
            return start + 2
        elif self.filter_string[start:start + 2] == 'OR':
            return start + 1
        else: #no valid operator found
            return None

    ##########above fine, debug start###########
    #Please insert the completed getAdvancedFilter function here and run all tests below.
    def getAdvancedFilter(self):
        filters_list = []
        self.evaluateScope(0, filters_list)
        return filters_list

    def evaluateScope(self, start, filters_list):
        length = len(self.tokens)
        num_encountered = False
        paren_encountered = True
        priority_operator_index = None
        while self.tokens[start] == '(':
            start += 1

        current = start
        for token in self.tokens[start:]:
            if token == ')':
                current += 1
                break
            elif token == 'OR':
                priority_operator_index = current
            elif token == 'AND':
                priority_operator_index = current
                break
            current += 1

        if priority_operator_index == None:
            left_has_paren = False
            right_has_paren = False
            #go one left of start point and set left has paren = True
            #start is 0, means no paren
            if not start == 0:
                if self.tokens[start-1] == '(':
                    left_has_paren = True
            #see if current is ), if so set right = True, if not means no paren
            if self.tokens[current-1] == ')':
                right_has_paren = True
            #if left has and right has, replace both with None
            if left_has_paren and right_has_paren:
                self.tokens[start-1] = None
                self.tokens[current-1] = None
                #go left as possible within this new scope

                #call evalscope on that leftmost index
                self.evaluateScope(self.getLeftMostOfScope(start-1), filters_list)
            #else:
                #no more parens and no more operators means current state is None None None None num None None
                #nothing else to process, return
            else:
                return

        else:
            left_operand_index = priority_operator_index - 1
            right_operand_index = priority_operator_index + 1

            while self.tokens[left_operand_index] == None and left_operand_index > 0:
                left_operand_index -= 1
            if self.tokens[left_operand_index] == ')':
                #different scope to our left, evaluate that to an expression first
                #move to leftmost of that scope and call evalScope on it
                left_operand = self.evaluateScope(getLeftMostOfScope(left_operand_index - 1), filters_list)
            while self.tokens[right_operand_index] == None and right_operand_index < length:
                right_operand_index += 1
            if self.tokens[right_operand_index] == '(':
            #different scope to our right, evaluate that to an expression first
                right_operand = self.evaluateScope(right_operand_index + 1, filters_list)

            expression = []
            operator = self.tokens[priority_operator_index]
            left_operand = self.tokens[left_operand_index]
            right_operand = self.tokens[right_operand_index]

            if type(left_operand) == type(0) and operator == None: #is int
                return
            if type(right_operand) == type(0) and operator == None:
                return

            expression.append(self.getOperandDict(left_operand))
            expression.append(operator)

            expression.append(self.getOperandDict(right_operand))

            filters_list.append(expression)

            #set self.tokens list around the operator to [filters_list_index, None, None]
            self.tokens[left_operand_index] = len(filters_list)
            self.tokens[priority_operator_index] = None
            self.tokens[right_operand_index] = None

            self.evaluateScope(self.getLeftMostOfScope(priority_operator_index), filters_list)

    def getOperandDict(self, operand):
        if type(operand) == type(0): #operand has type int
            return operand
        eq_split_string = operand.split('=')
        key = eq_split_string[0]
        value = operand[operand.index('=')+1:]
        return {key: value}

    def getLeftMostOfScope(self, start):
        while start != 0 and self.tokens[start] != '(':
            start -= 1
        return start


if __name__ == '__main__': #debugging
    def test(ss):
        pq = {'-f': ss}
        x = AdvancedFilter(pq)
        x.process()
        print('tokenized form: ', x.initial_tokens)
        index = 1
        print('filters list:')
        for e in x.filters_list:
            print(e, index)
        print('original test string was: ', pq['-f'])
        print('\n')

    test("(TITLE=meow meow meow AND REV=4.00)")
    test("TITLE=unbreakable OR TITLE=zootopia")
    test("TITLE=despicable me AND REV=4.00 OR REV=3.00")
    test("TITLE=despicable me AND (TITLE=zootopia OR TITLE=unbreakable)")
    test("TITLE=despicable me AND REV=4.00 OR REV=3.00 AND DATE=2014-03-01 OR DATE=2014-03-01")
    test("((TITLE=aaa a a AND REV=bb OR REV=c) AND DATE=dddd) OR DATE=eeeee")
    test("TITLE=x AND ((REV=y OR REV=zz AND DATE=aa) OR DATE=bb)")
    test("((TITLE=oh baby, my love == you OR TITLE=sent,from, hell== AND REV=4.00) OR DATE=x)")
