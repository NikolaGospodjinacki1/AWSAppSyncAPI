install: requirements.txt
	pip install -r requirements.txt

format:
	black ./*.py

synth:
	cdk synth
clean:
	rm -rf __pycache__
all:
	make install format synth clean