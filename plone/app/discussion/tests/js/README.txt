plone.app.discussion javascript testsuite
=========================================

Note: This document was shamelessly stolen from the plone.app.deco package.

We're using QUnit_ for unit testing, the jQuery test runner.

Simply load index.html directly in the browser with a file:/// url; not via
Plone. This way our tests are truely standalone and isolated.

Coverage testing
----------------

To test code coverage, I can heartily recommend using JSCoverage_. You can 
download, compile and install it by:

  $ wget http://siliconforks.com/jscoverage/download/jscoverage-0.5.tar.bz2
  $ tar xfvj jscoverage-0.5.tar.bz2
  $ cd jscoverage-0.5
  $ ./configure
  $ make
  $ sudo make install
  
After that, issue the following command to run it from your Plone buildout:

  $ jscoverage-server -v --ip-address=0.0.0.0 --port=8080 --encoding=UTF-8 \
    --document-root=plone/app/discussion/ --no-instrument=/tests

Then point your browser to the now running `coverage server
<http://localhost:8080/jscoverage.html?/tests/javascripts/test_comments.html>`__, and
the test suite will run instrumented in an iframe. Select the Summary tab to see
the results.

The command-line options ensure that only our tests and the modules being
tested are instrumented for coverage, not the testing framework nor jQuery.

Note that JSCoverage adds instrumentation statements to the code, so don't try
to debug your tests when running via the jscoverage server.

.. _QUnit:  http://docs.jquery.com/QUnit
.. _JSCoverage: http://siliconforks.com/jscoverage/
