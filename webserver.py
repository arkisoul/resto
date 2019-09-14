from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import cgitb
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()
cgitb.enable()

class webserverHandler(BaseHTTPRequestHandler):
    """docstring for webserverHandler"""

    def do_GET(self):
        try:
            # if self.path.endswith("/hello"):
            #     self.send_response(200)
            #     self.send_header('Content-Type', 'text/html')
            #     self.end_headers()

            #     output = ""
            #     output += '<html><body>Hello!'
            #     output += '<form method="POST" enctype="multipart/form-data" action="/hello"><h2> What would you like me to say?</h2><input name="message" type="text" /><input type="submit" value="Submit" /></form>'
            #     output += '</body></html>'
            #     self.wfile.write(output.encode())
            #     print(output)
            #     return

            # if self.path.endswith("/hola"):
            #     self.send_response(200)
            #     self.send_header('Content-Type', 'text/html')
            #     self.end_headers()

            #     output = ""
            #     output += '<html><body>&#161Hola <a href="/hello">Back to Hello</a>'
            #     output += '<form method="POST" enctype="multipart/form-data" action="/hello"><h2> What would you like me to say?</h2><input name="message" type="text" /><input type="submit" value="Submit" /></form>'
            #     output += '</body></html>'
            #     self.wfile.write(output.encode())
            #     print(output)
            #     return

            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                output = ''
                output += '<!doctype html><html><head><title>Restaurants</title></head><body>'
                output += '<div><table><thead><tr><th>Sr No</th><th>Name</th><th>Action</th></tr></thead><tbody>'
                output += self.get_restaurants()
                output += '</tbody></table></div>'
                output += '<div><a href="/restaurants/new">Create New Restaurant</a></div>'
                output += '</body></html>'
                self.wfile.write(output.encode())
                # print(output)
                return

            # Create New Restaurant
            if self.path.endswith('/restaurants/new'):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                output = ''
                output += '<!doctype html><html><head><title>Add New - Restaurants</title></head><body>'
                output += '<form method="POST" enctype="multipart/form-data" action="/restaurants/new"><h2> What is the res name?</h2><label for="name"><input name="name" type="text" /></label><input name="action" type="hidden" value="add" /><input type="submit" value="Submit" /></form>'
                output += '</body></html>'
                self.wfile.write(output.encode())
                return

            # Edit a Restaurant Name
            if self.path.endswith('/edit'):
                rest_id = int(self.path.split('/')[2])
                restaurant = self.get_restaurant(rest_id)
                restaurant_name = restaurant.name
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                output = ''
                output += '<!doctype html><html><head><title>Edit - Restaurants</title></head><body>'
                output += '<form method="POST" enctype="multipart/form-data" action="/restaurant/%d/edit"><h2> What is the new name for %s?</h2><label for="name"><input name="name" type="text" placeholder="%s" /></label><input type="submit" value="Rename" /></form>' % (rest_id, restaurant_name, restaurant_name)
                output += '</body></html>'
                self.wfile.write(output.encode())
                return

            # Delete a Restaurant
            if self.path.endswith('/delete'):
                rest_id = int(self.path.split('/')[2])
                restaurant = self.get_restaurant(rest_id)
                restaurant_name = restaurant.name
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                output = ''
                output += '<!doctype html><html><head><title>Edit - Restaurants</title></head><body>'
                output += '<form method="POST" enctype="multipart/form-data" action="/restaurant/%d/delete"><h2>You are about to delete %s restaurant, are you sure?</h2><input type="submit" value="Delete" /></form>' % (rest_id, restaurant_name)
                output += '</body></html>'
                self.wfile.write(output.encode())
                return

        except IOError:
            self.send_error(404, "File not found %s" % self.path)

    def do_POST(self):
        try:
            self.send_response(301)
            self.send_header('Content-Type', 'text/html')
            ctype, pdict = cgi.parse_header(self.headers.get('Content-Type'))
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)

                if self.path.endswith('/new'):
                    restaurant = fields.get('name')
                    restaurant = restaurant[0].decode('utf-8')
                    new_restaurant = Restaurant(name = restaurant)
                    session.add(new_restaurant)
                    session.commit()
                    print('%s restaurant added successfully' % restaurant)
                    self.send_header('Location', '/restaurants')

                if self.path.endswith('/edit'):
                    new_restaurant_name = fields.get('name')
                    new_restaurant_name = new_restaurant_name[0].decode('utf-8')
                    rest_id = int(self.path.split('/')[2])
                    restaurant = self.get_restaurant(rest_id)
                    restaurant.name = new_restaurant_name
                    session.add(restaurant)
                    session.commit()
                    print('%s restaurant updated successfully' % new_restaurant_name)
                    self.send_header('Location', '/restaurants')

                if self.path.endswith('/delete'):
                    rest_id = int(self.path.split('/')[2])
                    restaurant = self.get_restaurant(rest_id)
                    restaurant_name = restaurant.name
                    session.delete(restaurant)
                    session.commit()
                    print('%s restaurant deleted successfully' % restaurant_name)
                    self.send_header('Location', '/restaurants')

            self.end_headers()

        except:
            self.send_error(404, "{}".format(sys.exc_info()[0]))
            print(sys.exc_info())

    def get_restaurants(self):
        # Get restaurants from DB
        query = session.query(Restaurant).order_by(Restaurant.id)
        restaurants = query.all()
        count = 1
        rows = ''
        for restaurant in restaurants:
            row = '<tr>'
            row += '<td>%d</td>' % count
            row += '<td>%s</td>' % restaurant.name
            row += '<td><a href="/restaurant/%d/edit">Edit</a></td>' % restaurant.id
            row += '<td><a href="/restaurant/%d/delete">Delete</a></td>' % restaurant.id
            row += '</tr>'
            count += 1
            rows += row
        return rows

    def get_restaurant(self, rest_id):
        # Get restaurant from DB
        restaurant = session.query(Restaurant).filter_by(id = rest_id).one()
        return restaurant


def main():
    try:
        port = 8000
        server = HTTPServer(('', port), webserverHandler)
        print("Web server running on port %s" % port)
        server.serve_forever()

    except KeyboardInterrupt:
        print(" ^C entered stopping web server...")
        server.socket.close()

if __name__ == '__main__':
    main()
