find $1/ -type f -name "*.saas" | rev | cut -c 6- | rev | xargs -L1 sh index.sh
