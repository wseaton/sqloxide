from sqloxide import parse_sql, mutate_expressions, mutate_relations

if __name__ == "__main__":
    sql = "SELECT something from somewhere where something = 1 and something_else = 2"

    def func(x):
        if "CompoundIdentifier" in x.keys():
            for y in x["CompoundIdentifier"]:
                y["value"] = y["value"].upper()
        return x

    ast = parse_sql(sql=sql, dialect="ansi")
    result = mutate_expressions(parsed_query=ast, func=func)
    print(result)

    def func(x):
        return x.replace("somewhere", "anywhere")

    result = mutate_relations(parsed_query=ast, func=func)
    print(result)
