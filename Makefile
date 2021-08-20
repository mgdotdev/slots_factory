cov:
	coverage run --source=slots_factory -m pytest ./test/test_slots_factory.py && coverage report -m

pub:
	rm -rf ./build ./dist
	python setup.py sdist
	twine upload dist/*

t:
	pytest ./test/test_slots_factory.py

b:
	pytest ./test/test_benchmarks.py