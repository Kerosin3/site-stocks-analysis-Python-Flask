#!/bin/bash
#use -dev flag to run development site version
#docker-compose build database_application
#docker-compose up database_application
date0=$(date +'%d-%m-20%y')
echo current date is $date0
flask_app="app.py"
flask_app_folder=$PWD/application/
flask_app=$PWD/application/$flask_app
echo $flask_app
if [ -e $flask_app ]
then
  echo "file app exists"
  if (( $# == 0 )); then
    echo "you must specify at either -dev or -prod flag, aborting..."
    exit 1
fi
  while [ -n "$1" ]
  do
    case "$1" in
    -dev) echo "Running in Developer mode"
        export FLASK_ENV=development
        docker-compose up -d database_application
        docker-compose up -d database_application_TEST
        ( cd $flask_app_folder && flask db init )
        ( cd $flask_app_folder && flask db migrate )
        ( cd $flask_app_folder && flask db upgrade );;
    -prod) echo "Running in Production mode";;
    *) echo "$1 is not an option, use either dev or prod"
      export FLASK_ENV=production
      exit 1;;
esac
shift
done
  echo flask_app is $flask_app
  export FLASK_APP=$flask_app
  flask run --host='0.0.0.0'
#  flask run #--host='0.0.0.0'
else
  echo "file app does not exist, aborting"
  exit 1
fi
