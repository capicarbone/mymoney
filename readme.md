
Backend for [Savings App](https://github.com/capicarbone/SavingsApp).

## Development

### User creation

```bash
docker exec mymoney flask create-user <name> <email> <password>
```

### Run tests

```bash
sudo docker exec mymoney pytest ./tests
```