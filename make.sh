#!/bin/bash

if [ -z "$1" ]; then 
    echo "You entered no arguments. Use ./make help for more information."
    exit 0
fi

if ["$1" == "runserver"]; then
    python manage.py runserver
    exit 0
fi

if ["$1" == "makemigrations"]; then
    python manage.py makemigrations
    exit 0
fi

if ["$1" == "migrate"]; then
    python manage.py migrate
    exit 0
fi

if ["$1" == "dbshell"]; then
    python manage.py dbshell
    exit 0
fi

if ["$1" == "help"]; then
	echo "--------------------------------------------------------------"
	echo "          Here are the different options available:           "
	echo "--------------------------------------------------------------"
	echo "  runserver   | Launches a test server for development purpose"
	echo "makemigrations|  Create a migration file to apply to database "
	echo "   migrate    |         Applies migrations to database        "
	echo "   dbshell    |    Opens mysql shell to display the database  "
	echo "     help     |              Displays this message            "
	echo "--------------------------------------------------------------"
    exit 0
fi

