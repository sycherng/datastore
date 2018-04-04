import values
import entry
import sortable_row

#call QueryProcessor(query).process()
class QueryProcessor:
    def __init__(self, query):
        self.query = query
        #try to get all the flags
        self.parsed_query_dict = self.parseQuery() #dict of valid flags to string specifying details

        print(self.parsed_query_dict.keys())
        print(self.parsed_query_dict.values())
        #no point continuing if nothing selected
        if not '-s' in self.parsed_query_dict:
            raise SyntaxError("Nothing was selected with this query.")

        #is the filter request advanced? allows us to ignore advanced stuff for now
        self.filter_is_advanced = self.isFilterAdvanced() #boolean

        #try to parse the flags
        if self.filter_is_advanced == False:
            self.filter = self.parseSimpleFilter() #None or Tuple(String key, String specification)
        self.groups = self.parseGroups() #None or List(String key)
        self.selects = self.parseSelects() #List(Tuple(String key, String aggregate_option)
        self.orders = self.parseOrders() #None or List(Tuple(String key, String aggregate_option))

        #raise errors if fail logical checks like
            #-s items must be in -g or -s:agg
            #-o items must be in -g or -o:agg
        self.raiseErrorIfInvalidSelects()
        self.raiseErrorIfInvalidOrders()

    def raiseErrorIfInvalidSelects(self):
        print('self.selects, line 33', self.selects)
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
                    raise SyntaxError("-s items must be in -g or -s:aggregated.")

    def raiseErrorIfInvalidOrders(self):
        if not self.orders:
            return
        for order in self.orders:
            key, aggregate_option = order
            if self.groups == None:
                if aggregate_option != '':
                    raise SyntaxErrpor("Aggregation not allowed if no -g clause.")
            else:
                if key in self.groups and aggregate_option == '':
                    continue
                elif key not in self.groups and aggregate_option != '':
                    continue
                else:
                    raise SyntaxError("-s items must be in -g or -o:aggregated.")

    def parseOrders(self):
        if not '-o' in self.parsed_query_dict:
            return None
        self.orders_keys = []
        orders = []
        order_string = self.parsed_query_dict['-o']
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
        print('line81 self.orders', orders)
        print('line82 self.orders_keys', self.orders_keys)
        return orders


    @staticmethod
    def raiseErrorIfInvalidAggregate(key, flag):
        if key not in values.VALID_AGGREGATE_OPTIONS:
            raise SyntaxError(f"{key} is an invalid aggregation option for {flag}.")


    def parseSelects(self):
        if not '-s' in self.parsed_query_dict:
            raise SyntaxError('Nothing is selected.')
        selects = []
        select_string = self.parsed_query_dict['-s']
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

    def parseGroups(self):
        if not '-g' in self.parsed_query_dict:
            return None
        groups_string = self.parsed_query_dict['-g']
        keys = groups_string.split(',')
        for key in keys:
            QueryProcessor.raiseErrorIfInvalidKey(key, '-g')
        return keys

    def parseSimpleFilter(self):
        '''
        Accounts for edge case where a key such as TITLE contains multiple spaces, commas, and equal signs.
        '''
        if not '-f' in self.parsed_query_dict:
            return None
        filter_string = self.parsed_query_dict["-f"]
        eq_split_strings = filter_string.split("=")
        key = eq_split_strings[0]
        QueryProcessor.raiseErrorIfInvalidKey(key, '-f')
        value = '='.join(eq_split_strings[1:])
        if value == '':
            raise SyntaxError(f"-f key {key} lacks specifications.")
        return (key, value)


    def isFilterAdvanced(self):
        if '-f' not in self.parsed_query_dict:
            return False
        for token in ['AND', 'OR', '(', ')']:
            if token in self.parsed_query_dict['-f']:
                return True
        return False


    def parseQuery(self):
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
        if value_stringbuilder == '':
            return
        if key in query_dict:
            raise SyntaxError(f"Flag {flag} can only be used once per query.")
        query_dict[key] = value_stringbuilder[:-1]
        return query_dict

    @staticmethod
    def raiseErrorIfInvalidKey(key, flag):
        if key not in values.VALID_KEYS:
            raise SyntaxError(f"{key} is an invalid key for {flag}.")

    @staticmethod
    def raiseErrorIfDuplicate(key, flag, dictionary):
        if key in dictionary:
            raise SyntaxError(f"{key} can only be specified once in {flag}.")

    def process(self):
        #actually process the query
        #simple filter or complex filter to get data from datastore
        self.filtered_entries = self.getFilteredEntries() #List(Entry)
        #group the data
        self.grouped_entries = self.getGroupedEntries() #List<List<Entry>>

        #unify data structures for ORDER BY and SELECT processing 
        #turn groups to rows if -g, obtain aggregate values
        if self.groups != None:
            self.processed_rows = self.groupsToRows() #list of dict
        #if not -g, turn entries to rows
        else:
            self.processed_rows = self.entriesToRows() #list of dict

        #order row 
        self.ordered_entries = self.orderRows() #list of dict
        #select keys
        self.selected_rows = self.getSelectedRows() #list of string
        print('209 selected_rows', self.selected_rows)
        #print headers and rows
        self.printRows()

    def printRows(self):
        for row in self.selected_rows:
            print(row)

    def getSelectedRows(self):
        select_processed_rows = []
        for row in self.ordered_entries:
            print('line220 row', row)
            this_row = ''
            for select in self.selects: #List of Tuple(key, aggregate):
                key, aggregate_option = select
                if aggregate_option == '':
                    select_key = key
                else:
                    select_key = f'{key}:{aggregate_option}'
                this_row += str(row[select_key])
                this_row += ','
                print('line231 this row', this_row)
            this_row = this_row[:-1] #remove extra ,
            select_processed_rows.append(this_row)
        return select_processed_rows 


    def orderRows(self):
        if not self.orders:
            return self.processed_rows
        print('line239 self.orders', self.orders)
        sortable_rows = []
        for row in self.processed_rows:
            sortable_rows.append(sortable_row.SortableRow(row, self.orders_keys))
        sortable_rows.sort()
        ordered_rows = list(map(lambda x: x.row, sortable_rows))
        return ordered_rows

    def entriesToRows(self):
        rows_list = []
        for entry in self.filtered_entries:
            entry_dict = entry.toDict()
            rows_list.append(entry_dict)
        return rows_list

    def groupsToRows(self):
        rows_list = []
        print(f'line 250, grouped-entries {self.grouped_entries}')
        for row in self.grouped_entries:
            row_dict = {}
            for select_key in self.selects: #List(Tuple(String key, String aggregate_option)
                key, aggregate_option = select_key
                if aggregate_option == '': #no aggregate
                    row_dict_key = key
                    row_dict_value = row[0].getAttribute(key)
                else: #aggregate option
                    print('line263 key', key, 'agg', aggregate_option)
                    row_dict_key = f'{key}:{aggregate_option}'
                    print('line265 row_dict_key', row_dict_key)
                    row_dict_value = self.getAggregateValue(row, key, aggregate_option)
                row_dict[row_dict_key] = row_dict_value
            rows_list.append(row_dict)
        print('line262 rows dict', rows_list)
        return rows_list

    def getAggregateValue(self, row, key, aggregate_option):
        """(self, List<Entry>, String, String""" 
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
        """
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

    def getFilteredEntries(self):
        if self.filter_is_advanced:
            return self.getAdvancedFilteredEntries()
        else:
            return self.getSimpleFilteredEntries()

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

    def passedFilter(self, entry): #TODO single filter -> comma separated filters
        if not self.filter: #no filters, automatically passes
            return True
        key, value = self.filter
        if entry.getAttribute(key) == value:
            return True
        return False

    def getAdvancedFilteredEntries(self):
        #TODO implement this using expression tree parsing -> getting valid entries from datastore.
        #Reminder: -s items must be in -g or -s:agg
        raise NotImplementedError("Advanced filtering not available.")
