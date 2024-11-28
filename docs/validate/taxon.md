# Taxon

The taxon of a record must be supplied as a name or taxon-version key (TVK).

A TVK is unambiguous and is linked to a certain name. A taxon may have many 
names but there will be a preferred name and a preferred TVK. If a TVK is
supplied then the response will contain the associated name and the preferred
TVK, assuming the input is valid.

If a taxon name is supplied then it must be spelt correctly to validate.
Assuming the name can be found in the dictionary then the corresponding TVK
and preferred TVK will be returned in the response.

The preferred TVK is how rules are identified currently. This is problematic
becuase if preferred TVKs are changed and rules are not updated then rules will
not be found. It is the intention to re-engineer Record Cleaner to use orgnaism
keys which perist through name changes now that they are considered reliable.