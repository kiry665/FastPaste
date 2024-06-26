class  UndoRedo():
    def __init__(self, back, forward):
        self.undo_stack = []
        self.redo_stack = []
        self.back = back
        self.forward = forward

    def check(self):
        print("Here")
        if self.undo_is_empty():
            self.back.setDisabled(True)
        else:
            self.back.setDisabled(False)
        if self.redo_is_empty():
            self.forward.setDisabled(True)
        else:
            self.forward.setDisabled(False)

    def undo_is_empty(self):
        return len(self.undo_stack) == 0
    def push_undo(self, item, action, clear_redo=True):
        self.undo_stack.append([item, action])
        if clear_redo:
            self.redo_stack.clear()
        self.check()
    def pop_undo(self):
        if not self.undo_is_empty():
            element = self.undo_stack.pop()
            self.push_redo(element[0], element[1])
            self.check()
            return element
    def redo_is_empty(self):
        return len(self.redo_stack) == 0
    def push_redo(self, item, action):
        self.redo_stack.append([item, action])
        self.check()
    def pop_redo(self):
        if not self.redo_is_empty():
            element = self.redo_stack.pop()
            self.push_undo(element[0], element[1], False)
            self.check()
            return element

if __name__ == '__main__':
    pass

