# procsocksh

This is a shellscript that should be run from a system that is trusted by all machines. It logs into each machine using SSH and executes specific lsof and ps commands, redirecting output which will later be processed by procsock