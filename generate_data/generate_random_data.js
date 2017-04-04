/* this scripts generates random data */

function generateString(slimit) {
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for( var i=0; i < slimit; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    return text;
}


function generateAge() {
	return Math.floor((Math.random() * 95) + 1);;
}

function generateDate(start, end, startHour, endHour) {
  var date = new Date(+start + Math.random() * (end - start));
  var hour = startHour + Math.random() * (endHour - startHour) | 0;
  date.setHours(hour);
  return date;
}

function generateTFalse() {
	return ((Math.floor((Math.random() * 2) + 1) % 2) == 0);
}



for (var x=1;x<100;x++) {
	name = generateString(5)
	lastname = generateString(15)
	age = generateAge()
	birthdate = generateDate(1985,2012,0,23) 
	company = generateString(10)
	self_bio = generateString(100)
	receive_sms = generateTFalse()
	likes = []
	likes = [generateName(3), generateName(3), generateName(3)]
	db.smalcollection.save({'name' : name, 'lastname' : lastname, 'birthdate' : birthdate, 'company' : company , 
	  'self_bio' :self_bio, 'receive_sms': receive_sms, 'likes' : likes  })

}



