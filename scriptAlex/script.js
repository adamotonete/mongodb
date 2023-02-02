


function generateCreateIndexesCommands(options) {
  var getIndexName = function(keys) {
    var name = "";
    var keyz = Object.keys(keys);
    for (var k = 0; k < keyz.length; k++) {
      var v = keys[keyz[k]];
      if (typeof v == "function")
        continue;

      if (name.length > 0)
        name += "_";
      name += keyz[k] + "_";

      name += v;
    }

    return name.substring(0, 126);
  };
  if (options === undefined) {
    options = {}
  }
  var truncateIndexName = options["truncateIndexName"] || true;
  var ensureBackground = options["ensureBackground"] || false;

  db.getMongo().getDBNames().filter(x => !["admin", "config", "local"].includes(x)).forEach(function (d) {
    db.getSiblingDB(d).getCollectionInfos({type : "collection"}).forEach(function (c) {
      var keys = db.getSiblingDB(d).getCollection(c.name).getIndexes();
      var idPosition = -1;
      for (var i = 0; i < keys.length; i++) {
        if (keys[i].name == "_id_") {
          idPosition = i;
        } else {
          keys[i].name = (truncateIndexName) ? getIndexName(keys[i].key) : keys[i].key
          if (ensureBackground) {
            // force all indexes to be created in the background
            keys[i].background = true;
          }
        }
      }
      // remove the { _id: 1 } default index as it will exist already anyway
      keys.splice(idPosition, 1);
      if (keys.length > 0) {
        print("db.getSiblingDB('" + d + "')." + c + ".createIndexes(" + JSON.stringify(keys) + ")");
      }
    });
  })
}
