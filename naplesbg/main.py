import cgi
import datetime
import re

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import model

plant_change_form_uri = 'http://spreadsheets.google.com/viewform?formkey=dG03bFlPNDMwUnlUazZXVUdTdjdZeXc6MQ'

def capitalize(s):
    if not s:
        return s
    return s.capitalize()    

def normalize_searchables(s):
    stop_words = ['a', 'an', 'and', 'of', 'this', 'am', 'at', 'by', 'do', 'x',
                  'for', 'i', 'it', 'my', 'on', 'not', 'so', 'to', 'up', 
                  ';', ',', '.', '\'', '"', '']

    # i don't know how we could get an empty string here but it seems
    # to happen sometimes
    if not s.strip(): 
        return ['ERROR']
    
    # remove stop words and punctuation and make words lowercase
    items = [i for i in s.split(' ') if i not in stop_words]
    items = map(lambda x: re.sub('\W', '', x).lower(), items)
    
    # add right side of accession number, assume 9 digit number, e.g. 201001234
    items.append(items[0][5:])
    
    return items
    

# search_form_html = """<form action="/acc" method="get">
#     <div>
#       <input type="text" name="q" />
#       <br />
#       <input type="submit" value="Search">
#     </div>
#   </form>"""
search_form_html = ""

condition_map = {'A': 'Alive',
                 'E': 'Excellent',
                 'G': 'Good',
                 'F': 'Fair',
                 'P': 'Poor',
                 'Q': 'Questionable',
                 'I': 'Indistinguishable',
                 'D': 'Dead',
                 'R': 'Deaccessioned/Removed',
                 'U': 'Unable to locate'}


class MainPage(webapp.RequestHandler):
    def get(self):
        html = template.render('template.html',
                               {'body': search_form_html})
        self.response.out.write(html)
        

class AccessionPage(webapp.RequestHandler):

    def make_accession_link(self, acc_num):
        """
        Return a link to an accession page for acc_num.  The link will
        be styled red if the accession has plants but they are all dead.
        """
        template ='<a %(style)s href="/acc?acc_num=%(acc_num)s">%(acc_num)s</a>'
        style = ''
        query = model.Plant.all().filter('acc_num = ', acc_num)
        if query.count(1) != 0:
            query.filter("condition !=", "D").filter("condition !=", "R").\
                filter("condition !=", "U")
            if query.count(1) == 0:
                style = 'style="color: #C00"'

        return template % {'style': style, 'acc_num': acc_num}
        
        
    def build_accession_table(self, acc):
        """
        Return an html table from the acc argument.
        """
        parts = ['<table>']
        row = '<tr><td>%s</td><td>%s</td></tr>'
        #parts.append(row % ('Name:', acc.name))
        name_href = '<a href="/acc?name=%(name)s">%(name)s</a>'
        google_href = '<span style="margin-left: 40px"><a href="http://google.com/search?q=%(name)s">google</a></span>'
        name_href = name_href + google_href
        parts.append(row % ('Name:', name_href%{'name': cgi.escape(acc.name)}))
        parts.append(row % ('Acc #:', acc.acc_num))
        parts.append(row % ('Common name:', acc.common_name))
        parts.append(row % ('Range:', acc.range))
        parts.append(row % ("Misc. Notes:", acc.misc_notes))
        parts.append('<br />')
        parts.append(row % ("Rec'd. Date:", acc.recd_dt))
        parts.append(row % ("Rec'd. Amt:",acc.recd_amt))
        parts.append(row % ("Rec'd. Size:", acc.recd_size))
        parts.append(row % ("Rec'd. As:", 
                            name_href%{'name': cgi.escape(acc.name)}))
        parts.append(row % ("Rec'd. Notes:", acc.recd_notes))

        parts.append(row % ("Source:", acc.psource_current))
        parts.append(row % ("Source Acc. #:", acc.psource_acc_num))
        parts.append(row % ("Source Acc. Date:", acc.psource_acc_dt))
        parts.append(row % ("Source Notes:", acc.psource_misc))
        parts.append('</table>')
        return ''.join(parts)


    def build_plants_table(self, acc_num):
        """
        Return an html table with the plants of acc_num.
        """
        query = model.Plant.all().order('qualifier')
        parts = ['<div>']
        parts.append('Plants:')
        parts.append('<table>')
        query.filter('acc_num =', acc_num)#.order('qualifier')    
        map_href = '<a href="http://naplesbg.appspot.com/maps/map-current.png">map</a>'
        plants_href = '<a href="%(form)s&entry_0=%(name)s&entry_1=%(date)s&entry_2=%(acc_num)s&entry_3=%(qualifier)s&entry_5=%(location)s">%(plant)s</a>'
        for plant in query:
            # TODO: need to include the name in the Plant table rather
            # than query the accession table for it
            acc_query = model.Accession.all()            
            acc_query.filter('acc_num = ', plant.acc_num)
            acc = acc_query.get()
            parts.append('<tr>')
            href = plants_href % \
                {'form': plant_change_form_uri, 'name': acc.name, 
                 'acc_num': plant.acc_num, 'qualifier': plant.qualifier, 
                 'date': datetime.date.today(), 'location': plant.loc_code,
                 'plant': '%s*%s' % (acc_num, plant.qualifier)}            
            map_span = '<span style="margin-left: 40px">%s</span>' % map_href
            parts.append('<td>%s:</td><td>%s (%s) %s</td>' \
                             % (href, plant.loc_name, plant.loc_code, map_span))
            parts.append('</tr><tr>')
            nplants = plant.loc_nplants
            if nplants in (None, ''):
                nplants = '??'
            loc_date = plant.loc_date
            if not loc_date in (None, ''):
                loc_date = '??'

            
            parts.append('<td>&nbsp;</td><td>%s plants on %s</td>' \
                             % (nplants, plant.loc_date))
            parts.append('</tr><tr>')            
            checked_date = plant.checked_date
            if not checked_date:
                checked_data = '??'
            condition = condition_map.get(plant.condition, plant.condition)
            if plant.condition in ('DRU'):
                condition = '<span style="color:red">%s</span>' % condition
            parts.append('<td>&nbsp;</td><td>Condition: %s on %s</td>' \
                             % (condition, checked_date))
            parts.append('</tr><tr>')
            parts.append('<td>&nbsp;</td><td>Checked by %s: %s</td>' \
                             % (plant.checked_by, plant.checked_note))
            parts.append('</tr>')
        parts.append('</table>')
        parts.append('</div>')
        return ''.join(parts)


    def get_single_accession(self, acc_num):
        # search for a specific accession number        
        body = []
        write = lambda s: body.append(s)#self.response.out.write(s)
        query = model.Accession.all()
        query.filter('acc_num =', acc_num)
        acc = query.get()

        # TODO: this will get the first accession but will ignore any
        # other accessions in the table, in reality there should only
        # be one Accession with acc_num        
        if acc:
            table = self.build_accession_table(acc)
            write(table)
            write('<br />')
            nplants = model.Plant.all().\
                filter('acc_num =',acc.acc_num).count(1)            
            if nplants > 0:
                table = self.build_plants_table(acc.acc_num)
                write(table)

            # append "Add a plant..." for adding more plants
            change_form_href = '<p><a href="%(form)s&entry_0=%(name)s&entry_1=%(date)s&entry_2=%(acc_num)s">Add a plant...</a></p>' % \
                {'form': plant_change_form_uri, 'name':acc.name, 
                 'date': datetime.date.today(), 'acc_num': acc.acc_num}
            write('<br />')
            write(change_form_href)                                         
            return ''.join(body)
        
        return None


    def get_accessions_by_name(self, name, order=None):
        """
        Return a string list of <div>s of acccession links.
        """
        body = []
        write = lambda s: body.append(s)#self.response.out.write(s)
        query = model.Accession.all()
        query.filter('name =', name)
        if order:
            query.order(order)
        else:
            query.order('name').order('acc_num')

        if query.count() < 1:
            return None    

        #query.order('acc_num')        
        for acc in query.fetch(100):
            link = self.make_accession_link(acc.acc_num)
            write('<div>%(link)s - %(name)s</div>' \
                      % {'link': link, 'name': acc.name})
        return ''.join(body)
                          

    def get_species_by_genus(self, genus, order=None):
        """
        Return a string list of <div>s of unique species names
        matching genus.
        """
        body = []
        write = lambda s: body.append(s)
        query = model.Accession.all().filter('genus =', capitalize(genus))
        if order:
           query.order(order)
        else:
            query.order('name').order('acc_num')

        if query.count() < 1:
            return None    

        name_set = set()
        for acc in query.fetch(100):
            if acc.name not in name_set:
                write('<div><a href="/acc?name=%s">%s</a></div>' 
                      % (acc.name, acc.name))
                name_set.add(acc.name)
        return ''.join(body)


    def get(self):
        """
        Handle the get response.
        """
        body = []
        write = lambda s: body.append(s)#self.response.out.write(s)
        debug = lambda m: write('<p>%s</p>' % m)

        def finish_page(page):
            if page:
                write(page)
            write('<br/>')
            write(search_form_html)
            self.response.out.write(template.render('template.html', 
                                                   {'body': ''.join(body)}))

        # the 'q' parameter is used for generic search queries
        q = self.request.get('q')
        order = self.request.get('order')
        if order in (None, ''):
            order = None
        page = ''        
        if q:
            has_results = False
            q = q.strip().lower()
            query = model.Accession.all()
            
            query.filter('_searchable =', q.lower())
            if order:
                query.order(order)
            else:
                query.order('name').order('acc_num')

            write('<br/>') # helps with fat thumbs
            for acc in query:
                has_results = True
                link = self.make_accession_link(acc.acc_num)
                write('<div>%(link)s - %(name)s</div>' \
                          % {'link': link, 'name': acc.name})
            
            if not has_results:
                write('<div>"%s" not found</div>' % q)

            finish_page(page)
            return

        # the acc_num and name parameters are used for specific searches
        acc_num = self.request.get('acc_num')
        if acc_num:
            page = self.get_single_accession(acc_num.strip())       
            if not page:
                write('<br />')
                write('<div>%s not found</div>' % acc_num)
            finish_page(page)
            return

        name = self.request.get('name')
        if name:            
            # create a list of all accessions which match name
            page = self.get_accessions_by_name(name.strip())
            if not page:
                write('<br />')
                write('<div>%s not found</div>' % name)
            finish_page(page)
            return

        genus = self.request.get('genus')
        if genus:
            page = self.get_species_by_genus(genus, order)
            if not page:
                write('<br />')
                write('No matching names found. </br>')
            finish_page(page)
            return

        # only called if nothing else matches
        finish_page('')
            

class AdminPage(webapp.RequestHandler):

    def get(self):
        pass

    def put(self):
        pass


application = webapp.WSGIApplication([('/', MainPage),
                                      ('/acc', AccessionPage),
                                      ('/admin', AdminPage),
                                      ], 
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
                                      
