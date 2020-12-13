"""
Builds a dependency graph by parsing all of the queries inside a folder
of .sql files. Renders via graphviz.
"""

import argparse
import json
import os
from glob import glob
from typing import List

import sqloxide
from graphviz import Digraph

parser = argparse.ArgumentParser()
parser.add_argument("--path", "-p", type=str, help="The path to process queries for.")
parser.add_argument("--dialect", "-d", type=str, help="The dialect to use.")

def get_sql_files(path: str) -> List[str]:
    return glob(path + "/**/*.sql")


def get_key_recursive(search_dict, field):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.

    - modified from: https://stackoverflow.com/a/20254842
    """
    fields_found = []

    for key, value in search_dict.items():

        if key == field:
            fields_found.append(value)

        elif isinstance(value, dict):
            results = get_key_recursive(value, field)
            for result in results:
                fields_found.append(result)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = get_key_recursive(item, field)
                    for another_result in more_results:
                        fields_found.append(another_result)

    return fields_found


def get_tables_in_query(SQL: str, dialect: str) -> List[str]:

    res = sqloxide.parse_sql(sql=SQL, dialect=dialect)
    tables = get_key_recursive(res[0]["Query"], "Table")

    results = list()

    for table in tables:
        results.append(table["name"][0]["value"] + "." + table["name"][1]["value"])

    return results


if __name__ == "__main__":

    args = parser.parse_args()

    files = get_sql_files(args.path)
    print(f'Parsing using dialect: {args.dialect}')

    result_dict = dict()

    for _f in files:
        pretty_filename = ".".join(_f.split("/")[-2:])

        with open(_f, "r") as f:
            sql = f.read()

        try:
            tables = get_tables_in_query(SQL=sql, dialect=args.dialect)
            result_dict[pretty_filename] = list(set(tables.copy()))
        except ValueError:
            print(f"File: {_f} failed to parse.")

    dot = Digraph(engine="dot")
    dot.attr(rankdir="LR")
    dot.attr(splines="ortho")
    dot.node_attr['shape'] = 'box'

    for view, tables in result_dict.items():
        view = view[:-4]
        dot.node(view)
        for table in tables:
            dot.edge(view, table)

    dot.render("./examples/depgraph.gv", view=True)
