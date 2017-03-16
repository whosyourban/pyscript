#!/usr/bin/env python
# encoding: utf-8

import sys
# import re
import torndb


def underline_to_camel(underline_format):
    camel_format = ''
    for _s_ in underline_format.split('_'):
        camel_format += _s_.capitalize()

    return camel_format


def golint_format(field):
    formated = False
    for okey, nkey in {"Id": "ID", "Url": "URL", "Uri": "URI", "Uid": "UID"}.iteritems():
        if okey in field:
            formated = True
            field = field.replace(okey, nkey)

    # seq = field.find(check)
    # if seq > 0:
        # head = field[seq-1:seq]
        # if re.match(r"[A-Z]", head):
            # field = field.replace(check, to)
            # formated = True

    return field, formated


def add_doctip(field):
    tips = " `db:\"%s\"`" % field
    return tips


typemap = {
    "int": "int",
    "bigint": "int64",
    "varchar": "string",
    "char": "string",
    "decimal": "float64",
    "mediumint": "int",
    "tinyint": "int",
    "smallint": "int",
    "float": "float64",
    "timestamp": "time.Time",
    "datetime": "time.Time",
    "date": "time.Time",
    "bool": "bool",
    "text": "string",
}


def convert_type(dbtype):
    for k, t in typemap.iteritems():
        if dbtype.startswith(k):
            return t

    return None

schema = sys.argv[1]
tables = sys.argv[2:]

db = torndb.Connection("127.0.0.1:3306", schema, "root", "qweqwe")
for table in tables:
    columns = db.query("show columns from %s.%s" % (schema, table))
    tablecamel = underline_to_camel(table)

    table_comment = "// %s ORM mapping to %s.%s" % (tablecamel, schema, table)
    struct = "%s\ntype %s struct {" % (table_comment, tablecamel)
    for c in columns:
        field = c.get("Field")

        typ = convert_type(c.get("Type"))
        if c.get("Null") == "YES":
            typ = "sql.Null%s" % underline_to_camel(typ)
            if typ == "sql.NullInt":
                typ = "sql.NullInt64"

        gofield, formated = golint_format(underline_to_camel(field))

        # gofield = underline_to_camel(field).replace("Id", "ID").replace("Url", "URL").replace("Uri", "URI").replace("Uid", "UID")
        # gofield = golint_format(gofield, "url", "URL")
        # gofield = golint_format(gofield, "uri", "URI")

        doc = ""
        if formated:
            doc = add_doctip(field)
        elif field.lower() != field:
            doc = add_doctip(field)
        elif "_" in field:
            doc = add_doctip(field)

        struct += "\n    %s\t%s%s" % (gofield, typ, doc)

    infoschema_comment = "// TableName..."
    struct += "\n}\n\n%s\nfunc (%s) TableName() string {\n\t" % (infoschema_comment, tablecamel)
    struct += "return \"%s.%s\"\n" % (schema, table)
    struct += "}\n\n"
    print struct
