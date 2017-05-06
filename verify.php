<?php

if($argc==3 && password_verify($argv[1],$argv[2])) {
    echo("OK\n");
    exit(0);
} else {
    echo("BAD\n");
    exit(-1);
}

?>