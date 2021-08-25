cov:
	coverage run --source=slots_factory -m pytest ./test/unit/ && coverage report -m

pub:
	rm -rf ./build ./dist
	python setup.py sdist
	twine upload dist/*

t:
	pytest ./test/unit/

b:
	pytest ./test/benchmarks