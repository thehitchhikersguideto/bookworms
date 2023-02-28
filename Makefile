
create-ml-env: 
	python3 -m venv .venvgymreco && source .venvgymreco/bin/activate
	pip3 install -r requirements.txt

ci-tests: 
	python3 -m pytest -v --cov=gymreco --cov-report 

run-fe:
	cd frontend/workout-reco-app && npm start

req: 
	pip3 install -r requirements.txt
	
