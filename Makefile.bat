@ECHO OFF

if "%1" == "runserver" (
    python manage.py runserver
    goto end
)

if "%1" == "makemigrations" (
    python manage.py makemigrations
    goto end
)

if "%1" == "migrate" (
    python manage.py migrate
    goto end
)

if "%1" == "dbshell" (
    python manage.py dbshell
    goto end
)

if "%1" == "help" (
	echo "--------------------------------------------------------------"
	echo "          Here are the different options available:           "
	echo "--------------------------------------------------------------"
	echo "  runserver   | Launches a test server for development purpose"
	echo "makemigrations|  Create a migration file to apply to database "
	echo "   migrate    |         Applies migrations to database        "
	echo "   dbshell    |    Opens mysql shell to display the database  "
	echo "     help     |              Displays this message            "
	echo "--------------------------------------------------------------"
)

:end
