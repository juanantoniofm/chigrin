REPORTS_DIR = reports
all: clean check metrics test

check:
	pychecker `find chigrin -name '*.py'`
metrics: reports
	pymetrics -S -k -z --csv=${REPORTS_DIR}/pymetrics.csv `find . -name '*.py'`
test: reports
	nosetests --with-coverage --cover-package chigrin --cover-erase --cover-html --cover-html-dir=${REPORTS_DIR}
reports:
	mkdir reports
clean:
	find . -name '*~' -exec rm {} +
	find . -name '*.pyc' -exec rm {} +
	rm -rf ${REPORTS_DIR} build dist MANIFEST
