## User creation

```bash
docker exec -it mymoney flask create-user <name> <email> <password>
```

## Run unit tests

```bash
sudo docker exec -it mymoney pytest ./tests/unit
```