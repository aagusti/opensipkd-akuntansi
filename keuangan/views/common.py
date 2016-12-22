from sqlalchemy import (
    String, Text, 
    or_,
    )
from sqlalchemy.dialects import oracle
from datatables import DataTables as BaseDataTables, ColumnDT


class DataTables(BaseDataTables):
    def _set_global_filter_expression(self):
        # global search filter
        global_search = self.params.get('search[value]', '')
        if global_search is '':
            return

        if (self.allow_regex_searches and
                self.params.get('search[regex]') == 'true'):
            op = self._get_regex_operator()
            val = clean_regex(global_search)

            def filter_for(col):
                return col.sqla_expr.op(op)(val)
        else:
            val = '%' + global_search + '%'

            def filter_for(col):
                if isinstance(self.query.session.bind.dialect, oracle.dialect):
                    return col.sqla_expr.cast(String(255)).ilike(val)
                return col.sqla_expr.cast(Text).ilike(val)

        global_filter = [filter_for(col)
                         for col in self.columns if col.global_search]

        self.filter_expressions.append(or_(*global_filter))

