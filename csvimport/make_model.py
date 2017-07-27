from datetime import datetime
import keyword

MESSYMAP = {'Decimal': 'DecimalField',
            'Integer': 'IntegerField',
            'Bool': 'BooleanField',
            'String': 'CharField'
            }


class MakeModel(object):
    """ Generates a simple model from a definition of fields
    """

    def to_django(self, mtype):
        djtype = MESSYMAP.get(str(mtype), '')
        if not djtype:
            if str(mtype).startswith('Date('):
                djtype = 'DateTimeField'
        return djtype

    def table2model(self, table_name):
        """ CamelCase from a table name """
        breaks = ['_', ' ', '-']
        parts = [table_name, ]
        klass = ''
        schema = table_name.split('.')
        table_name = schema[-1]
        for breakpart in breaks:
            if table_name.find(breakpart) > -1:
                parts = table_name.split(breakpart)
                if parts:
                    break
        for part in parts:
            klass += part.title()
        return klass

    def model_from_table(self, table_name, fieldset):
        """ Generates model code and writes it to files,
            also clone code and sql if config requires it
            Note - follows the same format as
            introspection.get_table_description(cursor, table_name)
            [(column_name, messy_type, bytes, max_length, max_digits, decimal_places) , ...]
        """
        classname = self.table2model(table_name)
        filename = classname.lower()
        comment = "    ''' Autogenerated model file %s %s '''\n\n" % \
            (filename, datetime.now().ctime())
        code = "\nclass %s(models.Model):\n" % classname
        code += comment

        for i, row in enumerate(fieldset):
            column_name = row[0]
            att_name = column_name.lower()
            field_type = self.to_django(row[1])
            comment_notes = []  # Holds Field notes, to be displayed in a Python comment.
            extra_params = {}  # Holds Field parameters such as 'db_column'.

            # If the column name can't be used verbatim as a Python
            # attribute, set the "db_column" for this Field.
            if ' ' in att_name or '-' in att_name or keyword.iskeyword(att_name) or column_name != att_name:
                extra_params['db_column'] = column_name

            # Modify the field name to make it Python-compatible.
            if ' ' in att_name:
                att_name = att_name.replace(' ', '_')
                comment_notes.append('Field renamed to remove spaces.')
            if '-' in att_name:
                att_name = att_name.replace('-', '_')
                comment_notes.append('Field renamed to remove dashes.')
            # Dunder not allowed in field names
            att_name = att_name.replace('__', '_')
            if keyword.iskeyword(att_name):
                att_name += '_field'
                comment_notes.append('Field renamed because it was a Python reserved word.')
            if column_name != att_name:
                comment_notes.append('Field name made lowercase.')

            # Add max_length for all CharFields.
            if field_type == 'CharField' and row[3]:
                extra_params['max_length'] = row[3]

            if field_type == 'DecimalField':
                # Add fix for Non specified precision, scale numbers get set to NUMBER(0, 0)
                # and fail when in fact they take any number up to the limits ie. (38, 30)
                # but we will go for a less space hungry (16, 4)
                if int(row[4]) > 0:
                    extra_params['max_digits'] = row[4]
                else:
                    extra_params['decimal_places'] = 4
                    extra_params['max_digits'] = 16
                # Add fix for Oracle number introspection
                if int(row[5]) > -1:
                    extra_params['decimal_places'] = row[5]
                else:
                    if extra_params['max_digits']:
                        extra_params['decimal_places'] = 0
                    else:
                        extra_params['decimal_places'] = 0
                        extra_params['max_digits'] = 16
            field_type += '('

            # Don't output 'id = meta.AutoField(primary_key=True)', because
            # that's assumed if it doesn't exist.
            if att_name == 'id' and field_type == 'AutoField(' and extra_params == {'primary_key': True}:
                continue

            # FIXME:Just always assume first column is primary key
            if i == 0:
                extra_params['primary_key'] = True

            # Add 'null' and 'blank', if the 'null_ok' flag was present in the
            # table description.
            if row[6]:  # If it's NULL...
                extra_params['blank'] = True
                if not field_type in ('TextField(', 'CharField('):
                    extra_params['null'] = True
            if 'primary_key' in extra_params or 'unique' in extra_params:
                for key in ('null', 'blank'):
                    extra_params[key] = False
            if row[7]:
                if field_type in ('TextField(', 'CharField('):
                    extra_params['default'] = ''
                elif field_type in ('DecimalField(', 'IntegerField('):
                    extra_params['default'] = 0
                elif field_type == 'BooleanField(':
                    extra_params['default'] = False
            field_desc = '%s = models.%s' % (att_name, field_type)
            if extra_params:
                if not field_desc.endswith('('):
                    field_desc += ', '
                field_desc += ', '.join(['%s=%r' % (k, v) for k, v in extra_params.items()])
            field_desc += ")"
            if comment_notes:
                field_desc += ' # ' + ' '.join(comment_notes)
            field_desc = "    %s\n" % field_desc
            code += field_desc
        meta = "\n    class Meta:\n"
        code += meta
        code += "        managed = False\n"
        quoted = []
        for part in table_name.split('.'):
            quoted.append('"%s"' % part)
        table_name = '.'.join(quoted)
        code += """        db_table = u'%s'""" % table_name
        return code
