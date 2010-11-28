import cgi
import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import model

capitalize = lambda s: s.capitalize()

search_form_html = """<form action="/acc" method="get">
    <div>
      <input type="text" name="q" />
      <br />
      <input type="submit" value="Search">
    </div>
  </form>"""


class MainPage(webapp.RequestHandler):
    def get(self):
        html = template.render('template.html',
                               {'body': search_form_html})
        self.response.out.write(html)
        

class AccessionPage(webapp.RequestHandler):

    def build_accession_table(self, acc):
        """
        Return an html table from the acc argument.
        """
        parts = ['<table>']
        row = '<tr><td>%s</td><td>%s</td></tr>'
        #parts.append(row % ('Name:', acc.name))
        name_ref = '<a href="/acc?name=%(name)s">%(name)s</a>'
        parts.append(row % ('Name:', name_ref%{'name': cgi.escape(acc.name)}))
        parts.append(row % ('Acc #:', acc.acc_num))
        parts.append(row % ('Common name:', acc.common_name))
        parts.append(row % ('Range:', acc.range))
        parts.append(row % ("Rec'd. Date:", acc.recd_dt))
        parts.append(row % ("Rec'd. Amt:", acc.recd_amt))
        parts.append(row % ("Rec'd. As:", 
                            name_ref%{'name': cgi.escape(acc.name)}))
        parts.append(row % ("Source:", acc.psource_current))
        parts.append(row % ("Source Acc. #:", acc.psource_acc_num))
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
        form = 'http://spreadsheets.google.com/viewform?formkey=dG03bFlPNDMwUnlUazZXVUdTdjdZeXc6MQ'
        plants_href = '<a href="%(form)s&entry_0=%(name)s&entry_1=%(date)s&entry_2=%(acc_num)s&entry_3=%(qualifier)s&entry_5=%(location)s">%(plant)s</a>'
        for plant in query:
            # TODO: need to include the name in the Plant table rather
            # than query the accession table for it
            acc_query = model.Accession.all()            
            acc_query.filter('acc_num = ', plant.acc_num)
            acc = acc_query.get()
            parts.append('<tr>')
            href = plants_href % \
                {'form': form, 'name': acc.name, 'acc_num': plant.acc_num, 
                 'qualifier': plant.qualifier, 'date': datetime.date.today(),
                 'location': plant.loc_code,
                 'plant': '%s*%s' % (acc_num, plant.qualifier)}            
            parts.append('<td>%s:</td><td>%s (%s)</td>' \
                             % (href, plant.loc_name, plant.loc_code))
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
        if acc:
            table = self.build_accession_table(acc)
            write(table)
            write('<br />')
            table = self.build_plants_table(acc.acc_num)
            write(table)
            return ''.join(body)
        else:
            return None

        # search for the string in the model's indexed properties
        #write('acc.search: %s<br/>' % acc_num)
        results = model.Accession.search(acc_num)
        if results.count(1000) < 1:
            write('<div>%s not found</div>' % acc_num)
            return ''.join(body)

        items = []
        for item in query.fetch(20):
            items.append('%s: %s<br/>' % (item.acc_num, item.name))
        return ''.join(body)


    def get_accession_list(self, name):
        """
        Return a string list of <div>s of acccession.
        """
        body = []
        write = lambda s: body.append(s)#self.response.out.write(s)
        query = model.Accession.all()
        query.filter('name =', name)

        if query.count() < 1:
            return None    

        query.order('acc_num')        
        for acc in query.fetch(100):
            write('<div><a href="/acc?acc_num=%(acc_num)s">%(acc_num)s</a> - %(name)s</div>' 
                  % {'acc_num': acc.acc_num, 'name': acc.name})
        return ''.join(body)
                          

    def get_species_list(self, genus):
        """
        Return a string list of <div>s of unique species names
        matching genus.
        """
        body = []
        write = lambda s: body.append(s)#self.response.out.write(s)
        query = model.Accession.all().filter('genus =', genus).order('name')

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

        def finish_page(page):
            write(page)
            write('<br/>')
            write(search_form_html)
            self.response.out.write(template.render('template.html', 
                                                   {'body': ''.join(body)}))

        # the 'q' parameter is used for generic search queries
        q = self.request.get('q')
        if q:
            q = q.strip()
            # generic query
            page = self.get_single_accession(q)
            if page:
                finish_page(page)
                return
            
            
            # no matching accessions so look up species names and genera
            accessions = self.get_accession_list(q)
            if accessions:
                write(accessions)
                write('<br />')

            species = self.get_species_list(q)
            if species:
                write(species)
                
            if len(body) == 0:
                write('<br />')
                write('<div>%s not found</div>' % q)

            finish_page('')
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
            page = self.get_accession_list(name.strip())
            if not page:
                write('<br />')
                write('<div>%s not found</div>' % name)
            finish_page(page)
            return

        genus = self.request.get('genus')
        if genus:
            page = self.get_species_list(genus)
            if not page:
                write('<br />')
                write('No matching names found. </br>')
            finish_page(page)
            return
            

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
                                      
