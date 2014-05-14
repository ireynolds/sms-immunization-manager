create: clean
	python make_website.py --input website/ --output website-deploy/

publish: create
	# rsync

clean:
	rm -rf website-deploy/