# Record Cleaner Service
Service for checking species records against the record cleaner rules.

Browse the /docs path for a definition of the API and an interface where
you can try it out.

## Configuration
The application expects certain environment variables to be set with values
which configure the service. The easiest way to do this is to create a .env file
and place it in the application root. The following settings should be 
included.

### Configuration for authentication to this service.

Javascript web tokens are used to secure connections to the service.
Obtain a JWT key with `openssl rand -hex 32`

`JWT_KEY="{Some key}"`
`JWT_ALGORITHM="HS256"`
`JWT_EXPIRES_MINUTES="15"`

### Configuration for connection to an Indicia warehouse.

An Indicia warehouse is used for species name/tvk lookup. The warehouse 
configuration needs to be altered to create a REST user so that we can
communicate with the warehouse web services.

`INDICIA_URL="{Host URL}/index.php/services/rest/"`
`INDICIA_REST_USER="{Some user name}"`
`INDICIA_REST_PASSWORD="{Some password}"`

The ID of the UKSI species list on the warehouse.
`INDICIA_TAXON_LIST_ID="{ID}"`

### Configuration for cloning rules.

The record cleaner rules are cloned from Github. Typically they will point to 
the master branch but may be different for development purposes.

The location of the repo.
`RULES_REPO="https://github.com/BiologicalRecordsCentre/record-cleaner-rules.git"`
The branch of the repo.
`RULES_BRANCH="txt_to_csv"`
The directory of the repo.
`RULES_DIR="record-cleaner-rules"`
The sub-direcotry of the csv rules.
`RULES_SUBDIR="rules_as_csv"`

### Configuration for initial user on start up.

An initial user account with admin rights is used to establish other users,
allowing them to access the service.

`INITIAL_USER_NAME="{Some user name}"`
`INITIAL_USER_PASS="{Some password}"`

## Development

## Testing