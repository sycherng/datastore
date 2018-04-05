import values

class Temp:
    def __init__(self, filter_string):
        self.parsed_query = {'-f':, filter_string}

    def getAdvancedFilters(self):
        tokenized_advanced_filter = self.tokenizeAdvancedFilter()

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
        tokens_list = []
        current_index = 0
        open_paren_count = 0
        expected_tokens = ['(', 'operator']
        while current_index < length:
            for expected_token in expected_tokens:
                if expected_token == '(':
                    if filter_string[current_index] == expected_token:
                        end_index = current_index
                        last_encountered_token = expected_token
                        break
                elif expected_token == ')':
                    end_index = self.getCloseParenEndIndex(current_index, filter_string)
                    if end_index:
                        last_encountered_token = expected_token
                        break
                elif expected_token == 'operator':
                    end_index = self.getOperatorEndIndex(current_index, filter_string)
                    if end_index:
                        last_encountered_token = expected_token
                        break
                elif expected_token == 'operand':
                    end_index = self.getOperandEndIndex(current_index, filter_string)
                    if end_index:
                        last_encountered_token = expected_token
                        break
                elif expected_token == ' ':
                    if filter_string[current_index] == expected_token:
                        end_index = current_index
                        last_encountered_token = expected_token
                        break
            #if no end index and current_index < len -1 (we havent reached the end of string), raise syntax error because valid tokens not found
            if not end_index and current_index < (len - 1): #haven't reached end of string
                raise SyntaxError(f"Invalid -f syntax at {filter_string[15:]}.")
            #add token to our tokens list
            token = filter_string[current_index:end_index + 1]
            tokens_list.append(token)
            #update expected_tokens based on last_encountered_token
            expected_tokens = self.updateExpectedTokens(last_encountered_token, open_paren_count)
            open_paren_count = self.updateOpenParenCount(last_encountered_token, open_paren_count)
            #update current_index based on end_index
            current_index = end_index + 1
        #return our tokens list
        return tokens_list

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
                        
    def updateOpenParenCount(self, last_encountered_token, open_paren_count):
        if last_encountered_token == '(':
            open_paren_count += 1
        elif last_encountered_token == ')':
            open_paren_count -= 1 
            
       
    def getOperandEndIndex(self, start, string):
        """(self, int, str) -> int or None
        Starts with the suspected start index of an operand, 
        reads up to 9 valid characters and checks if it is a valid key,
        once valid key found, expects = sign,
        if = sign, reads until an operator or ) is encountered
        and returns that -1 as the end index of this operand.

        Otherwise return None."""
        key_end_index = self.getKeyEndIndex(start, string)
        if not key_end_index: #no valid keys found
            return None
        if string[key_end_index+1] != '=': #valid key not followed by =
            return None
        if string[key_end_index+2] == ')': #validkey=)
            return None

        current_index = key_end_index + 2
        while current_index < len(string):
            if string[current_index] == ')':
                return current_index - 1
            current_index += 1
        
        


    #remove when merging into queryprocessor because is duplicate function
    def getKeyEndIndex(self, start, string):
        current_index = start
        for char in string[start:]:
            if current_index - start == 10 or not char.isalpha():
                return
            elif char == '=':
                if string[start:current_index] not in values.VALID_KEYS:
                    return None
                else:
                    return current_index - 1
            current_index += 1


    def getOperatorEndIndex(self, start, string):
        """(self, int, str) -> int or None
        Starts with the suspected start index of an operator,
        reads up to 3 valid characters and checks if it is a valid key,
        if it is valid, reads until an operand or ( is encountered
        and returns that -1 as the end index of this operator.

        Otherwise returns None."""




############TESTING#############
def test(filter_string, is_valid):
    x = Temp(filter_string)
    x.getAdvancedFilters()
    print(filter_string, is_valid)
    print(x.advanced_filters)

test("TITLE=unbreakable AND TITLE=zootopia", False)
test("TITLE=unbreakable OR TITLE=zootopia", True)
#test("TITLE=despicable me AND REV=4.00 OR REV=3.00", True)
#test("TITLE=despicable me AND (TITLE=zootopia OR TITLE=unbreakable)", False)
#test("TITLE=despicable me AND REV=4.00 OR REV=3.00 AND DATE=2014-03-01 OR DATE=2014-03-01", True)
#test("((TITLE=despicable me AND REV=4.00 OR REV=3.00) AND DATE=2014-03-01) OR DATE=2014-03-01", True)
#test("TITLE=despicable me AND ((REV=4.00 OR REV=3.00 AND DATE=2014-03-01) OR DATE=2014-03-01)", True)