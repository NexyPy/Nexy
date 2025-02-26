
# from nexy import CustomResponse, JSONResponse


from nexy.decorators import Action


class Mutable:
    value :any

    def __init__(self,init:any):
        self.value = init
@Action()
async def go():
    count.value += 1
    return  count.value



@Action()
async def reset():
    count.value -= 1
    return count.value



count = Mutable(1)
    
