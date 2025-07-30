

from nexy import Component
from components.LinkCard import LinkCard
from components.Badge import Badge

@Component(
   imports=[LinkCard,Badge]
)
def View():

	return {"name": "hello world"}


@Component(
   imports=[]
)
def Layout(children):
	return {"children":children}
