import shapefile

#w = shapefile.Writer(shapeType=1)
def write_shp(track):
    w = shapefile.Writer(shapefile.POLYGON)
    w.poly(parts=[track]) 
    w.field('FIRST_FLD','C','40') 
    w.field('SECOND_FLD','C','40') 
    w.record('First','Polygon') 
    w.save('/polygon')