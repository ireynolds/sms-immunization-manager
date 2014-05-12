# TODO: use more efficient Makefile solution
create: clean
	mkdir website
	markdown built-in-operations.md > website/built-in-operations.html
	markdown deployment.md > website/deployment.html
	markdown homepage.md > website/homepage.html
	markdown user-docs.md > website/user-docs.html
	markdown create-an-operation.md > website/create-an-operation.html
	markdown dev-docs.md > website/dev-docs.html
	markdown web-interface.md > website/web-interface.html
	markdown design-decisions.md > website/design-decisions.html
	cp styles.css website/

publish: create
	# rsync website to web server's docroot

clean:
	rm -rf website/