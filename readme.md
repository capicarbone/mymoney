## User creation

```bash
docker exec mymoney flask create-user <name> <email> <password>
```

## Run unit tests

```bash
sudo docker exec mymoney pytest ./tests/unit
```