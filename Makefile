dockerimage ?= simple_auth
dockerfile ?= Dockerfile
srcdir ?= $(shell pwd)
datadir ?= $(shell pwd)

install:
	@docker build -t $(dockerimage) -f $(dockerfile) .

i: install


update:
	@docker build -t $(dockerimage) -f $(dockerfile) . --pull --no-cache

u: update

run: install
	@docker run                              \
	  --rm                                   \
	  -p 5000:5000							 \
	  -it $(dockerimage)                     

r: run

test: install
	@docker run                              \
	  --rm                                   \
	  -p 5000:5000							 \
	  -dt $(dockerimage)                     
	py.test --tavern-beta-new-traceback
	@docker kill `docker ps -q -n 1`

t: test


.PHONY: install i update u notebook n
