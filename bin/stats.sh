set -ex

mkdir -p logs;
cat /var/log/nginx/depot.galaxyproject.org_access.log |
    egrep ' /software/[^/ ]+/[^/ ]+'  |
    awk '{print $4$5" "$7}' |
    sed 's/:/ /;s/\[//g;s/\]//g;s|/| |;s|/| |' |
    awk '{logfile="logs/"$3"-"$2"-"$1".log"; logstmt=$4" "$5; print "grep -c \""logstmt"\" "logfile"; if [[ $? != \"0\" ]]; then echo \""logstmt"\" > "logfile"; fi;"}' |
    bash;
