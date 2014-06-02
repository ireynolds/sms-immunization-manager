---
title: Contributing Documentation
---

# Contributing Documentation

* toc
{:toc}

The SIM documentation is provided as the static HTML you are reading right now.
These documents are produced from [Markdown](http://daringfireball.net/projects/markdown) 
templates with a ruby tool called [nanoc](http://nanoc.ws/). To help contribute you 
need to install:
* [ruby](https://www.ruby-lang.org)
* [nanoc](http://nanoc.ws/)
* [maruku](http://maruku.rubyforge.org/maruku.html)
* [slim](http://slim-lang.com/)

## Documentation Process

The content of these documentation pages is written in Markdown, which has a limited
syntax that can be complied to HTML. Nanoc is configured to use Maruku to
convert markdown to HTML following the templates defined in the default layout
file.

## Directory Structure

The `website/` directory found in the source code repository stores the templates
and markdown files. The directory structure found in content reflects the
structure for the final HTML version that will be created by nanoc.

`nanoc.yaml`: nanoc configuration file.

`Rules`: nanoc rules used when generating the web site.

`layouts/default.slim` slim template file defines more advanced HTML features
that are applied to all pages.

## Making edits

Edits should be made to the markdown files (.md) and pushed to the master
repository when complete. Consult the markdown documentation for the supported
syntax.

## Generating HTML

To generate the HTML version of the documentation navigate to the `/website`
directory and run `nanoc`. This will create an output folder (ignored by git)
that contains the HTML version of the site. This folder can be viewed locally
or hosted on a web server.

## Publishing

To publish the documentation site, run `nanoc` to generate the static site in the `content/` directory. Then copy the contents of `content/` (not the `content/` folder itself, though) into the `docs/` folder in the Document Root (as [configured](/deploy/apache/#configure_apaches_to_host_sim) in Apache).