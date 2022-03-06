from PyQt5.QtCore import QSortFilterProxyModel

'''This custom class enables the Filter_Proxy_Model to iterate through the tree structures.'''


class LeafFilterProxyModel(QSortFilterProxyModel):

    def filterAcceptsRow(self, row_num, source_parent):
            ''' Overriding the parent function '''
            # Check if the current row matches
            if self.filter_accepts_row_itself(row_num, source_parent):
                    return True
            # Traverse up all the way to root and check if any of them match
            if self.filter_accepts_any_parent(source_parent):
                    return True
            # Finally, check if any of the children match
            return self.has_accepted_children(row_num, source_parent)

    def filter_accepts_row_itself(self, row_num, parent):
            return super(LeafFilterProxyModel, self).filterAcceptsRow(row_num, parent)

    def filter_accepts_any_parent(self, parent):
            ''' Traverse to the root node and check if any of the
            ancestors match the filter
            '''
            while parent.isValid():
                    if self.filter_accepts_row_itself(parent.row(), parent.parent()):
                            return True
                    parent = parent.parent()
            return False

    def has_accepted_children(self, row_num, parent):
            ''' Starting from the current node as root, traverse all
            the descendants and test if any of the children match
            '''
            model = self.sourceModel()
            source_index = model.index(row_num, 0, parent)
            children_count =  model.rowCount(source_index)
            for i in range(children_count):
                    if self.filterAcceptsRow(i, source_index):
                            return True
            return False