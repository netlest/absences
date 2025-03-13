#!/bin/bash
cd "$( dirname $0 )"
. venv/bin/activate

setup_database() {
flask --app app setup-db
}

run_dev() {
  while true; do
  flask --app app --debug run --host=0.0.0.0 --port=8000
    if [[ "$?" == "0" ]]; then
    break
    fi
    echo App startup failed, retrying in 5 secs...
    sleep 5
  done
}

run_prod() {
  while true; do
    gunicorn -c gunicorn_config.py "app:create_app()" --access-logfile - --error-logfile -
    if [[ "$?" == "0" ]]; then
    break
    fi
    echo App startup failed, retrying in 5 secs...
    sleep 5
  done
}

case $1 in
  prod)
    setup_database
    run_prod
    ;;
  dev)
    run_dev
    ;;
  *)
    echo $"Usage: $0 prod|dev"
    ;;
esac
