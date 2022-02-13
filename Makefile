MODULE := licht

pkg: readme
	@python3 setup.py sdist bdist_egg

twinetest: pkg
	@twine upload -r testpypi dist/*

twine: pkg
	@twine upload -r pypi dist/*

dev: readme
	@pipenv install --dev
	@pipenv install -e .

readme:
	@emacs --batch readme_src.org -f org-md-export-to-markdown
	@mv readme_src.md README.md

pytest:
	@pipenv run pytest -v --cov=licht --cov-report=html

clean:
	rm -rf .pytest_cache .coverage htmlcov README.md dist build
