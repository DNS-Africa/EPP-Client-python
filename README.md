epp.py standalone EPP client utility
====================================

The dev branch supports *nix pipelining. Eg. to remove xml comments  and to pipe output into xmllint to format single line responses

   cat create_domain.xml | sed -e 's/<!--.*-->//g' -e '/<!--/,/-->/d' | epp.py ... 2>&1 | egrep 'xml version.+epp' | xmllint --format -
