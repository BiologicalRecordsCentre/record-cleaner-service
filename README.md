# Record Cleaner Service
Service for checking species records against the record cleaner rules.

Browse the /docs path for a definition of the API and an interface where
you can try it out.

## Configuration
The application expects certain environment variables to be set with values
which configure the service. One way to do this is to create a .env file
and place it in the application root. The following settings should be 
included.

### Configuration for authentication to this service.

Javascript web tokens are used to secure connections to the service.
Obtain a JWT key with `openssl rand -hex 32`

*   `JWT_KEY="{Some key}"`
*   `JWT_ALGORITHM="HS256"`
*   `JWT_EXPIRES_MINUTES="15"`

### Configuration for connection to an Indicia warehouse.

An Indicia warehouse is used for species name/tvk lookup. The warehouse 
configuration needs to be altered to create a REST user so that we can
communicate with the warehouse web services.

*   `INDICIA_URL="{Host URL}/index.php/services/rest/"`
*   `INDICIA_REST_USER="{Some user name}"`
*   `INDICIA_REST_PASSWORD="{Some password}"`

The ID of the UKSI species list on the warehouse.
*   `INDICIA_TAXON_LIST_ID="{ID}"`

### Configuration for cloning rules.

The record cleaner rules are cloned from Github. Typically they will point to 
the master branch but may be different for development purposes.

The location of the repo.
*   `RULES_REPO="https://github.com/BiologicalRecordsCentre/record-cleaner-rules.git"`

The branch of the repo.
*   `RULES_BRANCH="txt_to_csv"`

The directory of the repo.
*   `RULES_DIR="record-cleaner-rules"`

The sub-direcotry of the csv rules.
*   `RULES_SUBDIR="rules_as_csv"`

### Configuration for initial user on start up.

An initial user account with admin rights is used to establish other users,
allowing them to access the service.

*   `INITIAL_USER_NAME="{Some user name}"`
*   `INITIAL_USER_PASS="{Some password}"`

### Configuration for running environment.

These settings tailor the application for its hosting environment.

The type of environment: [dev|test|prod]. Defaults to prod.
*   `ENVIRONMENT="prod"`

The location for creating a data directory. Defaults to '.'
Use . to indicate a path relative to application root.
*   `DATA_DIR="."`

The location for a backup of the data directory. Defaults to '' implying
no backups exist. If, on startup, there is no database in the DATA_DIR but
there is one in the BACKUP_DIR, then it is copied in.
*   `BACKUP_DIR="/path/to/persistent/storage"`

Log level: [debug|info|warning|error|critical]. Defaults to warning.
*   `LOG_LEVEL="info"`

### Configuration for rule tolerance.

Rule tolerance creates special messages for rules that are failed but by an 
ammount that is within the tolerance value.

The number of days tolerance given to phenology rules in days. Defaults to 3.
Set to 0 to disable.
*   `PHENOLOGY_TOLERANCE=3`
The number of 10km squares tolerance given to tenkm rules. A value of 1 tests if
any of the the 8 10km squares adjacent to the recorded 10km square are valid, 
i.e.a 30km x 30km square centred on the record. A value of 2 expands this to a
50km x 50km square centred on the record and so on. Defaults to 1.
Set to 0 to disable.
*   `TENKM_TOLERANCE=1`

## Development
Do development in a fork or branch of the repo.

All pushes or merge requests to the main branch of the repository trigger unit
testing. Running the tests locally and not submitting until all tests pass saves
embarrassment.

### VS Code
When developing with VS Code the following two configuration files can be used
to debug the code locally or in a container.

#### launch.json
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: FastAPI",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.main:app",
                "--reload",
                "--port",
                "8000"
            ],
            "jinja": true
        },
        {
            "name": "Docker: Python - Fastapi",
            "type": "docker",
            "request": "launch",
            "preLaunchTask": "docker-run: debug",
            "python": {
                "pathMappings": [
                    {
                        "localRoot": "${workspaceFolder}",
                        "remoteRoot": "/app"
                    }
                ],
                "projectType": "fastapi"
            }
        }
    ]
}
```
#### tasks.json
```json
{
	"version": "2.0.0",
	"tasks": [
		{
			"type": "docker-build",
			"label": "docker-build",
			"platform": "python",
			"dockerBuild": {
				"tag": "recordcleanerservice:latest",
				"dockerfile": "${workspaceFolder}/Dockerfile",
				"context": "${workspaceFolder}",
				"pull": true
			}
		},
		{
			"type": "docker-run",
			"label": "docker-run: debug",
			"dependsOn": [
				"docker-build"
			],
			"python": {
				"args": [
					"app.main:app",
					"--host",
					"0.0.0.0",
					"--port",
					"8000"
				],
				"module": "uvicorn"
			}
        }
	]
}
```

## Testing
If a commit is tagged `v{semver}-{type}{N} where

- {semver} is a semantic version number like 1.2.3
- {type} is a pre-release type [alpha|beta|rc]
- {N} is an integer

it will be built and deployed to the UKCEH staging server. This is not publicly
accessible.

Full releases will also be deployed to staging.

## Production
Commits tagged `v{semver} are built with the intention of deployment to 
record-cleaner.brc.ac.uk. Automation of this is not enabled at present so 
manual intervention by someone with access to the host is needed for deployment.
Currently it is hosted on the CEH production cluster in Lancaster.