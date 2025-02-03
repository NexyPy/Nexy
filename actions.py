class Mutable:
    value :any
    def __init__(self,init:any):
        self.value = init
count = Mutable(1)
def go():
    count.value +=10
    return count.value

def reset():
    count.value -= 1
    return count.value
    
