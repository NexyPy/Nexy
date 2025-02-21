
# from nexy import CustomResponse, JSONResponse


from nexy.decorators import action


class Mutable:
    value :any

    def __init__(self,init:any):
        self.value = init
@action()
async def go():
    count.value += 1
    return  count.value



@action()
async def reset():
    count.value -= 1
    return count.value



count = Mutable(1)
    
