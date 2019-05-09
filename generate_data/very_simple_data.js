var bulk = db.foo.initializeUnorderedBulkOp();
for (var x=0;x<1000000; x++) {
     bulk.insert({myvariable : 'Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test  ' + hex_md5(x.toString()),  i : x})
     if (x%1000 == 0) {
        bulk.execute();
        var bulk = db.foo.initializeUnorderedBulkOp();
     }
}     
