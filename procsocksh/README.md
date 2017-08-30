## procsocksh

This is a shellscript that should be run from a system that is trusted by all target machines. It logs into each machine using SSH and executes specific lsof and ps commands, redirecting output which will later be processed by procsock. This is meant to function without interaction, make sure that the appropriate options/flags are provided in the SSH command

### Output format

For details on file naming convention, see proclib code. Do NOT rename the files or procsock will not know how to process them

## Author

copyright [at] mzpqnxow.com

## License

Copyright (C) 2017 copyright@mzpqnxow.com under the MIT license
Please see COPYRIGHT for terms