#! /bin/bash

docker exec -it services-songs_persistence-1 /bin/bash -c "psql -U postgres -d songs"

docker exec -it services-accounts_persistence-1 /bin/bash -c "psql -U postgres -d accounts"