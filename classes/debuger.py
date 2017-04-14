from classes.vals import Vals

class DebugVals(Vals):
    target = ['tests', 'vals']
    vals_list = list([])
    send_to_base = []
    def update(func):
        def wraper(self, *args, **kwargs):
            try:
                trg = func(self, *args, **kwargs)
            except:
                trg = [None,None,None]
            if trg[1]:
                DebugVals.send_to_base.append(trg[0])
            if not trg[2]:
                Vals.vals_list.append(trg[0])
            else:
                Vals.vals_list[trg[2]] = trg[0]
            return trg
        return wraper