# import mysql.connector
from variables import table_schema, vector_elements_list, text_attr_list, float_attr_list
import itertools
from record_time import timeit
import string
import re
import pandas as pd
from sqlalchemy import create_engine
from logger_config import logger

class Database:
    def __init__(self, db_path):
        self.table_schema = table_schema
        # Modify the connection string to use SQLite
        self.engine = create_engine(f"sqlite:///{db_path}")

    def ask_database(self, query: str) -> pd.DataFrame:
        with self.engine.connect() as connection:
            df = pd.read_sql(sql=query, con=connection)
            return df


class SQLpostprocessor:
    def __init__(self, text_attr_list= text_attr_list, float_attr_list= float_attr_list, vector_elements_list = vector_elements_list) -> None:
        self.float_attr_list = float_attr_list
        self.text_attr_list = text_attr_list      
        self.vector_elements_list = vector_elements_list
    @staticmethod
    def strip_punctuation_except_underscore(text):
        # Create a translation table excluding underscores
        punctuation_to_remove = string.punctuation.replace('_', '')
        translator = str.maketrans('', '', punctuation_to_remove)
        return text.translate(translator)

    @timeit
    def regex_sort(self, sql: str, attributes_to_add: list):
        sql = sql.replace('"', '\'')

        # Regular expressions to identify different parts of the SQL query
        select_pattern = r'\bSELECT\b\s+(DISTINCT\s*)?(.+?)\s+FROM\b'
        from_pattern = r'\bFROM\b\s+(\S+)'
        order_pattern = r'\bORDER BY\b\s+(\S+)'
        group_by_pattern = r'\bGROUP BY\b'
        where_pattern = r'\bWHERE\b\s+(.+?)\s+(LIMIT|ORDER BY|;?$)'

        # To filter 
        delete_pattern = r'\bDELETE\b'
        insert_pattern = r'\bINSERT\b'
        update_pattern = r'\bUPDATE\b'

        if re.search(delete_pattern, sql, re.IGNORECASE) or re.search(insert_pattern, sql, re.IGNORECASE) or re.search(update_pattern,sql, re.IGNORECASE):
            return None, [], []
        
        # Check if the SQL query contains a GROUP BY clause
        if re.search(group_by_pattern, sql, re.IGNORECASE):
            return sql, [], []

        # Find SELECT clause and extract attributes
        select_match = re.search(select_pattern, sql, re.IGNORECASE)

        if not select_match:
            return sql, [], []

        select_distinct, select_attrs = select_match.groups()
        if not select_distinct:
            select_distinct = ''
        select_attrs = select_attrs.strip()
        
        # Find 'text_attr = xx' in WHERE clause
        equal_pattern = re.compile(r'(\w+) *= *(?:"([^"]*)"|\'([^\']*)\')', re.IGNORECASE)

        for match in equal_pattern.finditer(sql):
            
            attribute, _, value = match.groups()

            if attribute in self.text_attr_list:
                value = value.strip('"\'') 
                like_statement = f"{attribute} LIKE '%{value}%'"
                sql = sql.replace(match.group(), like_statement)

        # Find ORDER BY clause and its attribute
        order_match = re.search(order_pattern, sql, re.IGNORECASE)
        order_attr = None
        if order_match:
            order_attr = self.strip_punctuation_except_underscore(order_match.group(1))

            where_match = re.search(where_pattern, sql, re.IGNORECASE)
            from_match = re.search(from_pattern, sql, re.IGNORECASE)
            if not where_match:
                from_string = from_match.group(0) # type: ignore
                sql = re.sub(from_string, from_string + f' WHERE {order_attr} is not null ', sql, flags=re.IGNORECASE)
            else:
                full_where_string = where_match.group(0)
                next_clause = where_match.group(2)
                where_string = re.sub(next_clause, '', full_where_string, re.IGNORECASE)
                sql = re.sub(where_string, where_string + f' AND {order_attr} is not null ', sql, flags=re.IGNORECASE)

            if str(order_attr).lower() != 'avg_times_cited':
                return sql, [], []

        # Add missing attributes to SELECT clause if necessary
        select_attr_list = [self.strip_punctuation_except_underscore(attr) for attr in re.split(r',\s*', select_attrs)]
        
        if order_attr and order_attr not in select_attr_list:
            # Add order_attr to the SELECT clause
            select_attrs += ', ' + order_attr

        for attr_to_add in set(attributes_to_add) - set(select_attr_list):
            select_attrs += ', ' + attr_to_add

        # Reconstruct SELECT clause
        select_clause = f"SELECT {select_distinct}{select_attrs} FROM"

        attributes_to_add = list(set(attributes_to_add) | set(select_attr_list))
        # Find the FROM clause position and reconstruct the SQL query
        from_match = re.search(from_pattern, sql, re.IGNORECASE)
        if from_match:
            from_clause = from_match.group(1)
        else:
            return sql, [], []

        # Reconstruct the final SQL query
        sql = re.sub(select_pattern, select_clause, sql, flags=re.IGNORECASE)
        sql = re.sub(from_pattern, f"FROM {from_clause}", sql, flags=re.IGNORECASE)

        def remove_condition_in_where_clause(sql_query, attribute_to_remove, condition_pattern, pos_for_re):
            # Regular expression to capture the value that the attribute is equal to
            

            # Find the value using regex search
            match = re.search(condition_pattern, sql_query, flags=re.IGNORECASE)
            value = None
            and_or = None
            if match:
                value = match.group(pos_for_re[0])  # Capture the value
                and_or = match.group(pos_for_re[1])

            # Remove the condition from the WHERE clause if it exists
            sql_query_modified = re.sub(condition_pattern, f'{attribute_to_remove} is not null {and_or}', sql_query,
                                        flags=re.IGNORECASE)

            # Remove the WHERE clause entirely if it becomes empty
            sql_query_final = re.sub(r'\bWHERE\s*(AND\s*|\bOR\b\s*)?\s*ORDER BY', 'ORDER BY', sql_query_modified,
                                     flags=re.IGNORECASE)

            # Clean up any trailing commas and whitespace
            sql_query_final = re.sub(r',\s*(FROM|WHERE)', r' \1', sql_query_final)
            sql_query_final = re.sub(r'\s+ORDER BY', ' ORDER BY', sql_query_final).strip()

            return sql_query_final, value

        attrs_to_postprocess = []
        values = []
        for attr in set(attributes_to_add).intersection(self.float_attr_list):
            condition_pattern =rf'\b{attr}\b\s*=\s*([+-]?\d+)\s*(AND\s*|\bOR\b\s*)?' 
            pos_for_re = [1,2]
            attrs_to_postprocess.append(attr)
            sql, value = remove_condition_in_where_clause(sql, attr, condition_pattern, pos_for_re)
            values.append(value)

        for attr in set(attributes_to_add).intersection(self.vector_elements_list):
            condition_pattern = rf'''\b{attr}\b\s*(=|LIKE)\s*(?:'([^']*)'|[^\s]+|[+-]?\d+)\s*(AND\s*|\bOR\b\s*)'''
            pos_for_re = [2,3]
            sql, value = remove_condition_in_where_clause(sql, attr, condition_pattern, pos_for_re)

        # Find where 
        sql = sql.replace('%', '%%')
        return sql, attrs_to_postprocess, values

    def manually_sort(self, retrieved_data, attrs_to_postprocess, values):
        sorted_data = retrieved_data
        # select idx from select clause
        try:
            for i, attr in enumerate(attrs_to_postprocess):
                if values[i]:
                    value = float(values[i])
                else:
                    value = 0
                sorted_data = retrieved_data.sort_values(
                    by= attr,
                    key=lambda x: abs(x - value),
                    ascending=True
                )
        except Exception as e:
            logger.warning(f'Error {e}')
        return sorted_data

    def sql_replace_with_summary(self, sql):
        like_pattern = r'\(?(\w+)\s+LIKE'
        like_match = re.match(like_pattern, sql, re.IGNORECASE)
        if like_match:
            like_string = like_match.group(1)
            sql = re.sub(like_string, 'summary', sql, re.IGNORECASE)
        return sql

    def find_float_conditions(self, parsed_query):
        float_condition = {}

        # filter conditions and targets 
        for elem in parsed_query['conditions']:
            if elem['data_type'] == 'float':
                float_condition[elem['attribute']] = elem['value']

        return float_condition

    def relax_sql(self, sql):
        # Split the query into words
        sql_as_list = sql.split(' ')

        # Find the indices for WHERE and ORDER BY clauses
        find_where = sql_as_list.index('WHERE') if 'WHERE' in sql_as_list else sql_as_list.index('FROM') + 2
        find_order = sql_as_list.index('ORDER') if 'ORDER' in sql_as_list else -1

        # Extract conditions between WHERE and ORDER BY
        conditions = sql_as_list[find_where + 1:find_order]

        # Find indices of all 'AND's
        and_indices = [i for i, word in enumerate(conditions) if word == 'AND']

        if not and_indices:
            return []

        # Generate all combinations of 'AND' and 'OR'
        combinations = itertools.product(['AND', 'OR'], repeat=len(and_indices))
        modified_sql_list = []
        # Try each combination
        for combo in combinations:
            for idx, combo_val in zip(and_indices, combo):
                conditions[idx] = combo_val
            modified_query = ' '.join(sql_as_list[:find_where + 1] + conditions + sql_as_list[find_order:])
            modified_sql_list.append(modified_query)

        return modified_sql_list

