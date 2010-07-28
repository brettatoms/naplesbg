from google.appengine.ext import db
from search import Searchable

# TODO: Garden collections/plant collection
# TODO: add family to Accession

class Accession(Searchable, db.Model):
    # list accessions name recd_dt recd_amt recd_as psource_current
    # psource_acc_num psource_acc_dt psource_misc tab c:\export.txt
    acc_num = db.StringProperty()#)required=True) # TODO: make primary key
    name = db.StringProperty()
    range = db.StringProperty()
    common_name = db.StringProperty() # delineated by semicolon
    misc_notes = db.TextProperty()

    recd_dt = db.StringProperty()
    recd_amt = db.StringProperty()
    recd_as = db.StringProperty()
    recd_size = db.StringProperty()
    recd_notes = db.TextProperty()

    psource_current = db.StringProperty()
    psource_acc_num = db.StringProperty()
    psource_acc_dt = db.StringProperty()
    psource_misc = db.TextProperty()

    INDEX_ONLY = ['acc_num', 'name', 'region', 'common_name', 
                  'psource_current']


class Plant(db.Model):
    acc_num = db.StringProperty()#required=True)
    qualifier = db.StringProperty()
    # TODO: key to accession accession 
    #accession = db.ReferenceProperty(Accession, collection_name="plants")
    sex = db.StringProperty()

    loc_name = db.StringProperty()
    loc_code = db.StringProperty()
    loc_change_type = db.StringProperty()
    loc_date = db.StringProperty()
    loc_nplants = db.StringProperty()

    condition = db.StringProperty()
    checked_date = db.StringProperty()
    checked_note = db.TextProperty()
    checked_by = db.StringProperty()


# class PlantLocation(db.Model):
#     # list plants acc_num, acc_num_qual, location_full, location
#     plant = db.ReferenceProperty(Accession, collection_name="locations")
#     location_code = db.StringProperty()
#     location_name = db.StringProperty()
#     change_type = db.StringProperty()
#     date = db.StringProperty()
#     nplants = db.IntegerProperty()


# class PlantCheck(db.Model):
#     plant = db.ReferenceProperty(Accession, collection_name="checks")
#     condition = db.StringProperty()
#     date = db.StringProperty()
#     note = db.TextProperty()
#     checked_by = db.StringProperty()
