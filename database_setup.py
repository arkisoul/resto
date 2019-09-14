import sys

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()

########## Table configuration ##########

# Restaurant Table #
class Restaurant(Base):
    """docstring for Restaurant"""

    # Table name
    __tablename__ = 'restaurant'

    # Table columns
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)

# Menu Item Table #
class MenuItem(Base):
    """docstring for MenuItem"""

    # Table name
    __tablename__ = 'menu_item'

    # Table columns
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))

    restaurant = relationship(Restaurant)

    # We added this serialize function to be able to send JSON objects in a
    # serializable format
    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'course': self.course,
        }


########## insert at end of file ##########
engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.create_all(engine)
