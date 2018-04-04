import values
import entry
import sortable_row

class QueryProcessor:


    def __init__(self, query):
        self.query = query

        #parse query to individual clauses
        self.flags_to_strings = self.parseQuery() #dict<str, str> | dict of <valid flags=>parameters>

        #raise error if nothing was selected
        if not '-s' in self.flags_to_strings:
            raise SyntaxError("Nothing was selected with this query.")

        #is the filter request advanced?
        self.filter_is_advanced = self.isFilterAdvanced() #boolean | whether filter has AND, OR, (, )

        #parse each clause
        if self.filter_is_advanced == False:
            self.filter = self.parseSimpleFilter() #None or tuple(str, str) | tuple of (FILTER BY key, value specification)
        self.groups = self.parseGroups() #None or list<str> | list of <GROUP BY keys>
        self.selects = self.parseSelects() #list<tuple(str, str)> | list of tuples of (SELECT key, aggregation option)
        self.orders = self.parseOrders() #None or list<tuple(str, str)> | list of tuples of (ORDER BY key, aggregate_option)

        #raise errors if clauses fail logical checks like
            #-s keys must be in -g or have an aggregated option specified (-s key:agg)
            #-o keys must be in -g or have an aggregation option specified (-o key:agg)
        self.raiseErrorIfInvalidSelects()
        self.raiseErrorIfInvalidOrders()

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
        QueryProcessor.raiseErrorIfDuplicate(key, 'query', query_dict)
        query_dict[key] = value_stringbuilder[:-1]
        return query_dict

    def isFilterAdvanced(self):
        if '-f' not in self.flags_to_strings:
            return False
        for token in ['AND', 'OR', '(', ')']:
            if token in self.flags_to_strings['-f']:
                return True
        return False

    def parseSimpleFilter(self):
        '''
        Accounts for edge case where a key such as TITLE contains multiple spaces, commas, and equal signs.
        '''
        if not '-f' in self.flags_to_strings:
            return None
        filter_string = self.flags_to_strings["-f"]
        eq_split_strings = filter_string.split("=")
        key = eq_split_strings[0]
        QueryProcessor.raiseErrorIfInvalidKey(key, '-f')
        value = '='.join(eq_split_strings[1:])
        if value == '':
            raise SyntaxError(f"-f key {key} lacks specifications.")
        return (key, value)


    def parseGroups(self):
        if not '-g' in self.flags_to_strings:
            return None
        groups_string = self.flags_to_strings['-g']
        keys = groups_string.split(',')
        for key in keys:
            QueryProcessor.raiseErrorIfInvalidKey(key, '-g')
        return keys


    def parseSelects(self):
        if not '-s' in self.flags_to_strings:
            raise SyntaxError('Nothing is selected.')
        selects = []
        select_string = self.flags_to_strings['-s']
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
        if not '-o' in self.flags_to_strings:
            return None
        self.orders_keys = []
        orders = []
        order_string = self.flags_to_strings['-o']
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
                    raise SyntaxError("Aggregation not allowed if no -g clause.")
            else:
                if key in self.groups and aggregate_option == '':
                    continue
                elif key not in self.groups and aggregate_option != '':
                    continue
                else:
                    raise SyntaxError("-s items must be in -g or -o:aggregated.")

    @staticmethod
    def raiseErrorIfInvalidKey(key, flag):
        if key not in values.VALID_KEYS:
            raise SyntaxError(f"{key} is an invalid key for {flag}.")


    @staticmethod
    def raiseErrorIfDuplicate(key, flag, dictionary):
        if key in dictionary:
            raise SyntaxError(f"{key} can only be specified once in {flag}.")

    @staticmethod
    def raiseErrorIfInvalidAggregate(key, flag):
        if key not in values.VALID_AGGREGATE_OPTIONS:
            raise SyntaxError(f"{key} is an invalid aggregation option for {flag}.")

    def processQuery(self):
        #actually process the query
        #simple filter or complex filter to get data from datastore
        self.filtered_entries = self.getFilteredEntries() #list<Entry> | list of <Entry object from datastore satisfying FILTER BY clause>
        #group the data
        self.grouped_entries = self.getGroupedEntries() #list<list<Entry>> | outer list = list of groups, inner list = all entries belonging to same group

        #if there are groups, get aggregate values
        if self.groups != None:
            self.processed_rows = self.groupsToRows() #list<dict> | list of <rows as dicts, keys include all aggregate values requested by -s and -o clauses>
        #otherwise simply turn it to a list of rows
        else:
            self.processed_rows = self.entriesToRows() #list<dict> | list of <rows as dicts, no aggregate values>

        #order row 
        self.ordered_entries = self.orderRows() #list<dict> | list of <rows as dicts, sorted by ORDER BY keys>
        #select keys
        self.selected_rows = self.getSelectedRows() #list<str> | list of <rows as str, with SELECT BY values separated by commas>
        #print rows
        self.printRows()


    def getFilteredEntries(self):
        if self.filter_is_advanced:
            return self.getAdvancedFilteredEntries()
        else:
            return self.getSimpleFilteredEntries()

    def getAdvancedFilteredEntries(self):
        #TODO implement this using expression tree parsing -> getting valid entries from datastore.
        #Reminder: -s items must be in -g or -s:agg
        raise NotImplementedError("Advanced filtering not available.")


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
        rows_list = []
        for row in self.grouped_entries:
            row_dict = {}
            for select_key in self.selects: #List(Tuple(String key, String aggregate_option)
                key, aggregate_option = select_key
                if aggregate_option == '': #no aggregate
                    row_dict_key = key
                    row_dict_value = row[0].getAttribute(key)
                else: #aggregate option
                    row_dict_key = f'{key}:{aggregate_option}'
                    row_dict_value = self.getAggregateValue(row, key, aggregate_option)
                row_dict[row_dict_key] = row_dict_value
            rows_list.append(row_dict)
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


    def entriesToRows(self):
        rows_list = []
        for entry in self.filtered_entries:
            entry_dict = entry.toDict()
            rows_list.append(entry_dict)
        return rows_list


    def orderRows(self):
        if not self.orders:
            return self.processed_rows
        sortable_rows = []
        for row in self.processed_rows:
            sortable_rows.append(sortable_row.SortableRow(row, self.orders_keys))
        sortable_rows.sort()
        ordered_rows = list(map(lambda x: x.row, sortable_rows))
        return ordered_rows


    def getSelectedRows(self):
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
        for row in self.selected_rows:
            print(row)
