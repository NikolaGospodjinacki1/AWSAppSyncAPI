install: requirements.txt
	pip install -r requirements.txt
	# NEED TO INSTALL YARN AS WELL sudo apt-get install yarn
	# https://snipit.io/public/snippets/18890
format:
	black ./*.py

synth:
	cdk synth
clean:
	rm -rf __pycache__
all:
	make install format synth clean