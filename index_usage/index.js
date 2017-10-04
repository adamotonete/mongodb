dbcheck = 'foo'
db.getSiblingDB(dbcheck).getCollectionNames().forEach(function (col_name) {
   print ('collection ' + col_name)
   values = db.getSiblingDB(dbcheck).getCollection(col_name).aggregate( [ { $indexStats: { } } ] )._batch
   values.forEach(function (ix) { 
     print(' ' + ix.name + 'count ' + ix.accesses.ops)
    })
   print ('------')
})
