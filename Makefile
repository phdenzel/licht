MODULE := licht

pkg: readme
	@python3 setup.py sdist build

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

service:
	@sed -i 's/User=.*/User=${USER}/' licht.service

user-service: service
	@cp licht.service ~/.config/systemd/user/licht.service

system-service: service
	@cp licht.service /etc/systemd/system/
	@chown root:root /etc/systemd/system/licht.service
	@chmod 644 /etc/systemd/system/licht.service

pytest:
	@pipenv run pytest -v --cov=licht --cov-report=html

clean:
	rm -rf .pytest_cache .coverage htmlcov README.md dist build
