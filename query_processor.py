import values
import entry
import sortable_row
import advanced_filter

class QueryProcessor:
    def __init__(self, query):
        self.query = query

        #parse query to individual clauses
        self.parsed_query = self.parseQuery() #dict<str, str> | dict of <valid flags=>parameters>

        #raise error if nothing was selected
        if not '-s' in self.parsed_query:
            raise SyntaxError("Nothing was selected with this query.")

        #is the filter request advanced?
        self.filter_is_advanced = self.isFilterAdvanced() #boolean | whether filter has AND, OR, (, )

        #parse each clause
        '''
        variable     | type                          | details
        -------------+-------------------------------+----------------------------------------------------
        self.filters | dict<str, str>                | dict of <FILTER BY key => value specification>
                     | None                          | None if no -f clause or filter is advanced (includes AND, OR, (, ))
        self.groups  | list<str>                     | list of <GROUP BY keys>
                     | None                          | None if no -g clause 
        self.selects | list<tuple(str, str)>         | list of tuples of (SELECT key, aggregation option)
        self.orders  | list<tuple(str, str)>         | list of tuples of (ORDER BY key, aggregation option)
                     | None                          | None if no -o clause
        '''
        if self.filter_is_advanced == False:
            self.filters = self.parseSimpleFilters()
        self.groups = self.parseGroups()
        self.selects = self.parseSelects()
        self.orders = self.parseOrders()

        #raise errors if clauses fail logical checks like
        self.raiseErrorIfInvalidSelects()
        self.raiseErrorIfInvalidOrders()


    def parseQuery(self):
        '''(self) -> dict<str, str>
        Parses self.query,
        returns a dict of valid flag=>parameters
        '''
        if self.query.isspace():
            raise SyntaxError("No query given.")

        query_dict = {}
        if self.query == '':
            return
        words_list = self.query.split(" ")
        value_stringbuilder = ''
        prev_flag = None
        for word in words_list:
            if word in values.VALID_FLAGS:
                self.updateQueryDict(query_dict, prev_flag, value_stringbuilder)
                value_stringbuilder = ''
                prev_flag = word
            else:
                value_stringbuilder += (word + ' ')
        self.updateQueryDict(query_dict, prev_flag, value_stringbuilder)
        return query_dict


    def updateQueryDict(self, query_dict, key, value_stringbuilder):
        '''(self, dict, str, str) -> dict
        Inserts into query_dict if there is a valid key and value.'''
        if value_stringbuilder == '':
            return
        QueryProcessor.raiseErrorIfDuplicate(key, 'query', query_dict)
        query_dict[key] = value_stringbuilder[:-1] #extra space
       

    def isFilterAdvanced(self):
        '''(self) -> bool
        Returns a boolean representing whether there is an advanced filter
        requested in this query.'''
        if '-f' not in self.parsed_query:
            return False
        for token in ['AND', 'OR', '(', ')']:
            if token in self.parsed_query['-f']:
                return True
        return False


    def parseSimpleFilters(self):
        '''(self) -> dict<str,str>
        Returns a dict of filter keys to filter parameters if 
        a valid -f clause is present.

        Handles single or multiple filter parameters with:
            multiple spaces
            multiple commas
            multiple equal signs
    
        Example: -f TITLE=Oh baby,   my love == you,REV=4.00,PROVIDER=your, worst, nightmare
        '''
        if '-f' not in self.parsed_query:
            return
        filter_string = self.parsed_query['-f']
        length = len(filter_string)
        current_index = 0
        filter_dict = {}
        while current_index < length:
            end_index = self.getKeyEndIndex(current_index, filter_string)
            if not end_index:
                if current_index == 0:
                    raise SyntaxError(f"-f clause opened with invalid key {filter_string[:10]}.")
                current_index = self.readUntilComma(current_index + 1, filter_string, length)
            else: #found key
                if current_index != 0: #already have a prev_key
                    prev_value_end = current_index - 1
                    prev_value = filter_string[prev_value_current:prev_value_end]
                    filter_dict[prev_key] = prev_value
                prev_key = filter_string[current_index:end_index + 1]
                prev_value_current = end_index + 2 #for '=' then 1 char
                #raise if invalid key
                #raise if duplicate key
                current_index = self.readUntilComma(current_index + 1, filter_string, length)
        filter_dict[prev_key] = filter_string[prev_value_current:]
        if filter_dict == {}:
                pass
                #raise invalid filter request
        return filter_dict

    def getKeyEndIndex(self, start, string):
        current_index = start
        for char in string[start:]:
            if current_index - start == 10:
                return None
            elif char == '=':
                if string[start:current_index] not in values.VALID_KEYS:
                    return None
                else:
                    return current_index - 1
            elif not char.isalpha():
                    return None
            current_index += 1

    def readUntilComma(self, start, string, length):
        current_index = start
        for char in string[start:]:
            if char == ',':
                return current_index + 1
            current_index += 1
        return length


    def parseGroups(self):
        '''(self) -> list<str>
        Returns a list of group by keys if a valid -g clause is present.
        '''
        if not '-g' in self.parsed_query:
            return None
        groups_string = self.parsed_query['-g']
        keys = groups_string.split(',')
        for key in keys:
            QueryProcessor.raiseErrorIfInvalidKey(key, '-g')
        return keys


    def parseSelects(self):
        '''(self)-> list<tuple(str,str)>
        Returns a list of tuples of select key, aggregation option if
        a valid -s clause is present.

        Presence of a -s clause was confirmed on line 15.
        '''
        selects = []
        select_string = self.parsed_query['-s']
        comma_split_strings = select_string.split(',')
        for string in comma_split_strings:
            pair = string.split(':')
            key = pair[0]
            QueryProcessor.raiseErrorIfInvalidKey(key, '-s')
            value = ''
            if len(pair) == 2:
                value = pair[1]
                QueryProcessor.raiseErrorIfInvalidAggregate(value, '-s')
            selects.append((key, value))
        return selects


    def parseOrders(self):
        '''(self)-> list<tuple(str, str)>
        Returns a list of tuples of order by key, aggregation option if
        a valid -o clause is present.

        Also saves a list (self.order_keys) of order by key and aggregation pairs
        as strings of key:pair for later use by self.orderRows().
        '''
        if not '-o' in self.parsed_query:
            return None
        self.orders_keys = []
        orders = []
        order_string = self.parsed_query['-o']
        comma_split_strings = order_string.split(',')
        for string in comma_split_strings:
            pair = string.split(':')
            key = pair[0]
            QueryProcessor.raiseErrorIfInvalidKey(key, '-o')
            value = ''
            if len(pair) == 2:
                value = pair[1]
                QueryProcessor.raiseErrorIfInvalidAggregate(value, '-o')
                self.orders_keys.append(f'{key}:{value}')
            else:
                self.orders_keys.append(key)
            orders.append((key, value))
        return orders


    def raiseErrorIfInvalidSelects(self):
        '''(self) -> None
        Raises errors if select clause does not satisfy the following rule:
        -s keys must be in -g or have an aggregation option (-s key:agg)
        '''
        for select in self.selects:
            key, aggregate_option = select
            if self.groups == None:
                if aggregate_option != '':
                    raise SyntaxError("Aggregation not allowed if no -g clause.")
            else:
                if key in self.groups and aggregate_option == '':
                    continue
                elif key not in self.groups and aggregate_option != '':
                    continue
                else:
                    raise SyntaxError("-s keys must be in -g or have an aggregation option specified.")


    def raiseErrorIfInvalidOrders(self):
        '''(self) -> None
        Raises errors if select clause does not satisfy the following rule:
        -s keys must be in -g or have an aggregation option (-s key:agg)
        '''
        if not self.orders:
            return
        for order in self.orders:
            key, aggregate_option = order
            if self.groups == None:
                if aggregate_option != '':
                    raise SyntaxError("Aggregation not allowed if no -g clause.")
            else:
                if key in self.groups and aggregate_option == '':
                    continue
                elif key not in self.groups and aggregate_option != '':
                    continue
                else:
                    raise SyntaxError("-o keys must be in -g or have an aggregation optionspecified.")


    @staticmethod
    def raiseErrorIfInvalidKey(key, level):
        '''(str, str) -> None
        Raises error if an invalid key as per values.VALID_KEYS.
        Convenience function.
        '''
        if key not in values.VALID_KEYS:
            raise SyntaxError(f"\"{key}\" is an invalid key for {level}.")


    @staticmethod
    def raiseErrorIfDuplicate(key, level,  dictionary):
        '''(str, str, dict) -> None
        Raises error if key already exists in dictionary.
        Convenience function.
        '''
        if key in dictionary:
            raise SyntaxError(f"\"{key}\" can only be specified once in {level}.")


    @staticmethod
    def raiseErrorIfInvalidAggregate(key, level):
        '''(str, str) -> None
        Raises error if an invalid key as per values.VALID_AGGREGATE_OPTIONS.
        Convenience function.
        '''
        if key not in values.VALID_AGGREGATE_OPTIONS:
            raise SyntaxError(f"\"{key}\" is an invalid aggregation option for {level}.")


    def processQuery(self):
        '''
        variable              | type              | details
        ----------------------+-------------------+------------------------------------------------------------------
        self.filtered_entries | list<Entry>       | list of <Entry object from datastore satisfying FILTER BY clause>
        self.grouped_entries  | list<list<Entry>> | outer list = list of groups, inner list = all entries belonging to same group
        self.processed_rows   | list<dict>        | if groups: list of <rows as dicts, keys include all aggregate values requested by -s and -o clauses>
                              | list<dict>        | if no groups: list of <rows as dicts, no aggregate values>
        self.ordered_entries  | list<dict>        | list of <rows as dicts, sorted by ORDER BY keys>
        self.selected_rows    | list<str>         | list of <rows as str, with SELECT BY values separated by commas>
        '''
        #simple filter or complex filter to get data from datastore
        self.filtered_entries = self.getFilteredEntries()
        #group the data
        self.grouped_entries = self.getGroupedEntries()

        #if there are groups, get aggregate values
        if self.groups != None:
            self.processed_rows = self.groupsToRows()
        #otherwise simply turn it to a list of rows
        else:
            self.processed_rows = self.entriesToRows()

        #order row 
        self.ordered_entries = self.orderRows()
        #select keys
        self.selected_rows = self.getSelectedRows()
        #print rows
        self.printRows()


    def getFilteredEntries(self):
        if self.filter_is_advanced:
            return self.getAdvancedFilteredEntries()
        else:
            return self.getSimpleFilteredEntries()


    def getAdvancedFilteredEntries(self):
        self.adv_filters = advanced_filter.AdvancedFilter(self.parsed_query).process()
        adv_filtered_entries = []
        with open(values.DATASTORE_NAME) as datastore:
            line = datastore.readline()
            while line:
                e = entry.Entry.lineToEntry(line)
                if self.passedAdvancedFilter(e):
                    adv_filtered_entries.append(e)
                line = datastore.readline()
        return adv_filtered_entries


    def passedAdvancedFilter(self, entry): 
        """(self, Entry) -> bool
        Returns boolean representing whether Entry satisfies filter."""
        for requirement in self.adv_filters:
            left_operand, operator, right_operand = requirement
            if type(left_operand) == type(0): #is an int
                left_operand = True
            if type(right_operand) == type(0):
                right_operand = True
            if operator == 'AND':
                expression_result = left_operand and right_operand
            elif operator == 'OR':
                expression_result = left_operand or right_operand
            if not expression_result:
                return False
        return True

    def getSimpleFilteredEntries(self):
        """None or Tuple(String key, String specification)
        (REV, 4.00)
        """
        filtered_entries = []
        with open(values.DATASTORE_NAME) as datastore:
            line = datastore.readline()
            while line:
                e = entry.Entry.lineToEntry(line)
                if self.passedFilter(e):
                    filtered_entries.append(e)
                line = datastore.readline()
        return filtered_entries


    def passedFilter(self, entry): 
        """(self, Entry) -> bool
        Returns boolean representing whether Entry satisfies filter."""
        if not self.filters: #no filters, automatically passes
            return True
        for key, value in self.filters.items():
            if entry.getAttribute(key) == value:
                return True
            return False


    def getGroupedEntries(self):
        """(self) -> List<List<Entry>>
        List<Entry> self.filtered_entries
        """
        if self.groups == None:
            return
        grouped_entries = {}
        for entry in self.filtered_entries:
            key = entry.getAttributesString(self.groups)

            if key in grouped_entries:
                grouped_entries[key].append(entry)
            else:
                grouped_entries[key] = [entry]
        return list(grouped_entries.values())


    def groupsToRows(self):
        """(self) -> list<dict>
        Turns each group in self.grouped_entries into a dict representing one row,
        includes aggregated keys and values."""       
        rows_list = []
        for row in self.grouped_entries:
            row_dict = {}
            for select_key in self.selects:
                self.getKeysAndAggregates(select_key, row, row_dict)
            for order_key in self.orders:
                self.getKeysAndAggregates(order_key, row, row_dict)
            rows_list.append(row_dict)
        return rows_list


    def getKeysAndAggregates(self, clause_key, row, row_dict):
        """(self, str, dict, dict) -> None
        Adds all keys value pairs requested by SELECT BY or ORDER BY clause to row_dict.
        If an aggregation option is specified, uses the aggregation result as value.
        If no aggregation option is specified, uses the first entry's attribute result as value"""
        key, aggregate_option = clause_key
        if aggregate_option == '': #no aggregate
            row_dict_key = key
            row_dict_value = row[0].getAttribute(key)
        else: #aggregate option
            row_dict_key = f'{key}:{aggregate_option}'
            row_dict_value = self.getAggregateValue(row, key, aggregate_option)
        if row_dict_key not in row_dict:
            row_dict[row_dict_key] = row_dict_value


    def getAggregateValue(self, row, key, aggregate_option):
        """(self, list<Entry>, str, str) -> int or str or list<str>
        Returns aggregate value for the specified key:aggregate pair
        for a row represented by a dict.
        """
        if aggregate_option == 'min':
            return self.getMinValue(row, key)
        if aggregate_option == 'max':
            return self.getMaxValue(row, key)
        if aggregate_option == 'sum': 
            return self.getSumValue(row, key)
        if aggregate_option == 'count':
            return self.getCountValue(row, key)
        if aggregate_option == 'collect': 
            return self.getCollectValue(row, key)


    def getMinValue(self, row, key): 
        min_value = QueryProcessor.stringToNum(row[0].getAttribute(key))

        for entry in row[1:]:
            value = QueryProcessor.stringToNum(entry.getAttribute(key))
            if value < min_value:
                min_value = value
        return min_value


    def getMaxValue(self, row, key): 
        max_value = QueryProcessor.stringToNum(row[0].getAttribute(key))

        for entry in row[1:]:
            value = QueryProcessor.stringToNum(entry.getAttribute(key))
            if value > max_value:
                max_value = value
        return max_value


    def getSumValue(self, row, key):
        '''
        Current implementation will concatenate strings if :sum called on a key that has string fields.
        Can easily be changed to raise Error if that is the preferred behaviour.
        '''
        sum_value = QueryProcessor.stringToNum(row[0].getAttribute(key))

        for entry in row[1:]:
            sum_value += QueryProcessor.stringToNum(entry.getAttribute(key))
        return sum_value


    def getCountValue(self, row, key):
        return len(row)


    def getCollectValue(self, row, key):
        collect_value = []
        for entry in row:
            collect_value.append(QueryProcessor.stringToNum(entry.getAttribute(key)))
        return collect_value


    @staticmethod
    def stringToNum(string): #bad name
        """(str) -> str or float or int
        If string:
            can be converted to float, return float.
            can be converted to int, return int.
        else: return string as is.
        """
        try:
            num = int(string)
        except:
            pass
        else:
            return num

        try:
            num = float(string)
        except:
            return string
        else:
            return num


    def entriesToRows(self):
        """(self) -> list<dict>
        Turns each row in self.filtered_entries into a dict representing one row."""       
        rows_list = []
        for entry in self.filtered_entries:
            entry_dict = entry.toDict()
            rows_list.append(entry_dict)
        return rows_list


    def orderRows(self):
        """(self) -> list<dict>
        Orders self.processed_rows by an arbitrary number of ORDER BY keys with
        the help of SortableRow class,
        returns as a list of dict where each dict represents a row.
        """
        if not self.orders:
            return self.processed_rows
        sortable_rows = []
        for row in self.processed_rows:
            sortable_rows.append(sortable_row.SortableRow(row, self.orders_keys))
        sortable_rows.sort()
        ordered_rows = list(map(lambda x: x.attributes_dict, sortable_rows))
        return ordered_rows


    def getSelectedRows(self):
        """(self) -> list<str>
        Returns a list of rows as strings with SELECT BY values separated by commas.
        """
        select_processed_rows = []
        for row in self.ordered_entries:
            this_row = ''
            for select in self.selects: #List of Tuple(key, aggregate):
                key, aggregate_option = select
                if aggregate_option == '':
                    select_key = key
                else:
                    select_key = f'{key}:{aggregate_option}'
                this_row += str(row[select_key])
                this_row += ','
            this_row = this_row[:-1] #remove extra ,
            select_processed_rows.append(this_row)
        return select_processed_rows 


    def printRows(self):
        """(self) -> None
        Prints each row in self.selected_rows.
        """
        for row in self.selected_rows:
            print(row)
        print(f"({len(self.selected_rows)} qualifying entries.)")
