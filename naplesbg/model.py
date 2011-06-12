from google.appengine.ext import db

# TODO: Garden collections/plant collection
# TODO: add family to Accession

class Accession(db.Model):
    # list accessions name recd_dt recd_amt recd_as psource_current
    # psource_acc_num psource_acc_dt psource_misc tab c:\export.txt
    acc_num = db.StringProperty()#)required=True) # TODO: make primary key
    genus = db.StringProperty()
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

    _searchable = db.StringListProperty()

    INDEX_ONLY = ['acc_num', 'name', 'genus', 'region', 'common_name', 
                  'psource_current', '_searchable']



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

    # TODO: need full condition instead of code, e.g. Alive instead of A
    condition = db.StringProperty()
    checked_date = db.StringProperty()
    checked_note = db.TextProperty()
    checked_by = db.StringProperty()
