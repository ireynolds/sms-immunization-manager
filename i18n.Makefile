# Define what languages to make
lang_args = -l es

# Define what directories to run makemessages and compilemessages in
lang_dirs = contextual envaya info mkdir notifications permissions \
            response stock utils dhis2 equipment messagelog moderation \
            operation_parser sim user_registration


default: compilemessages

# Run makemessages in each directory
makemessages: make_locale_dirs
	$(foreach dir,$(lang_dirs),\
		cd $(dir) &&\
		django-admin.py makemessages $(lang_args) &&\
		cd ..;\
	)

# Run compilemessages in each directory
compilemessages:
	$(foreach dir,$(lang_dirs), \
    	cd $(dir) &&\
    	django-admin.py compilemessages &&\
    	cd ..;\
	)

# Create locale directories if they do not already exist
make_locale_dirs:
	$(foreach dir,$(lang_dirs), mkdir -p $(dir)/locale;)

# Removes all locale directories. Use with caution!
clean:
	$(foreach dir,$(lang_dirs), rm -rf $(dir)/locale;)
